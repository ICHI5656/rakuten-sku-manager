# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**rakuten_sku_manager** is a Docker-based web application for Rakuten RMS CSV processing and product attribute database management. It handles device variation management, SKU auto-numbering, and cross-join expansion for Japanese e-commerce.

## Tech Stack
- **Backend**: FastAPI (Python 3.11), Pandas, SQLite/Supabase
- **Frontend**: React 18, TypeScript, Material-UI, Vite
- **Infrastructure**: Docker Compose, Nginx
- **Database**: Dual-mode - SQLite (local) or Supabase (cloud)

## Essential Commands

### Quick Start
```bash
# Full rebuild and start (recommended for major changes)
docker-rebuild.cmd  # Windows
docker-compose down && docker-compose build --no-cache && docker-compose up -d  # Linux/Mac

# Quick rebuild for minor changes
simple-rebuild.cmd  # Windows
docker-compose restart

# Access application
http://localhost:3000  # Frontend
http://localhost:8000/docs  # API documentation
```

### Development Commands
```bash
# Backend-only rebuild
docker-compose build --no-cache backend && docker-compose up -d backend

# Frontend-only rebuild
docker-compose build --no-cache frontend && docker-compose up -d frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute Python scripts inside container
docker exec rakuten-sku-backend python /app/script_name.py

# Database access
docker exec rakuten-sku-backend python -c "import sqlite3; conn = sqlite3.connect('/app/product_attributes_new.db'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM device_attributes'); print(cur.fetchone())"
```

### Testing & Debugging
```bash
# Test CSV processing
docker cp test.csv rakuten-sku-backend:/app/test.csv
docker exec rakuten-sku-backend python /app/test_device_position.py

# Test API endpoints
curl -X GET http://localhost:8000/api/product-attributes/brands
curl -X POST http://localhost:8000/api/upload -F "file=@test.csv"

# Container health check
docker-compose ps
docker inspect rakuten-sku-backend --format='{{.State.Health.Status}}'
```

## Architecture Overview

### Processing Pipeline
```
CSV Upload → Encoding Detection → Product Grouping → Device Management → SKU Generation → Database Update → CSV Export
```

### Core Processing Flow

1. **CSV Upload & Validation** (`backend/app.py:upload_csv`)
   - Auto-detects Shift-JIS encoding
   - Groups by product management number (商品URL)
   - Extracts devices from variation2 option definitions

2. **Device Management** (`backend/services/rakuten_processor.py:process_csv`)
   - Identifies truly new devices (not in existing SKU rows)
   - Position logic application:
     ```python
     Priority: custom_device_order > add_position > default_order
     ```
   - Maintains device order consistency across products

3. **SKU Generation** (`backend/services/sku_manager.py`)
   - Product-scoped sequential numbering: `sku_a000001`, `sku_b000001`
   - State persistence: `/app/data/state/sku_counters.json`
   - Cross-join expansion: colors × devices = total SKUs

4. **Database Integration** (`backend/product_attributes_api_v2.py`)
   - SQLite path: `/app/product_attributes_new.db`
   - Supabase mode: Controlled by `USE_SUPABASE` env variable
   - Device usage count tracking
   - Auto brand detection from device names

### Critical Business Rules

#### CSV Structure Requirements
- **Parent row**: Has product management number, no SKU number, contains variation definitions
- **SKU row**: Has both product management number and SKU number
- **Encoding**: Shift-JIS for both input and output

#### Device Positioning Algorithm
```python
# backend/services/rakuten_processor.py:_update_device_definition()
if custom_device_order:  # Complete order list from frontend
    device_list = custom_device_order
elif add_position == 'start':
    device_list = new_devices + existing_devices  
elif add_position == 'after' and after_device:
    index = existing_devices.index(after_device) + 1
    device_list = existing_devices[:index] + new_devices + existing_devices[index:]
else:
    device_list = existing_devices + new_devices  # Default: append to end
```

#### Rakuten RMS Constraints
- Max 40 variations per attribute
- Max 400 SKUs per product
- Max 100MB file upload
- Files auto-delete after 24 hours

## Frontend-Backend Contract

### Key API Endpoints
```typescript
POST /api/upload
POST /api/process
GET /api/product-attributes/devices
GET /api/database/brands
POST /api/batch/upload
GET /api/batch/status/{batch_id}
```

### Process Request Interface
```typescript
interface ProcessRequest {
  file_id: string;
  devices_to_add: string[];         // All devices (new + existing)
  custom_device_order?: string[];   // Complete order list
  add_position?: 'start' | 'end' | 'after' | 'custom';
  after_device?: string;
  device_attributes?: Array<{
    device: string;
    attribute_value: string;
    size_category?: string;
  }>;
}
```

## Database Configuration

### Dual-Mode Operation
- **SQLite Mode**: Default, uses `./backend/product_attributes_new.db`
- **Supabase Mode**: Enabled via `USE_SUPABASE=true` in `.env.supabase`

### Supabase Setup
```bash
# Configure environment
cp .env.supabase .env
# Edit .env with your Supabase credentials

# Run migrations
docker exec rakuten-sku-backend python /app/migrate_to_supabase.py

# Verify connection
curl http://localhost:8000/  # Should show "database_mode": "Supabase"
```

## Common Issues & Solutions

### Device Position Issues
```bash
# Debug: Check request payload
docker logs rakuten-sku-backend | grep custom_device_order

# Debug: Add logging
docker exec rakuten-sku-backend sed -i 's/def _update_device_definition/def _update_device_definition\n        print(f"DEBUG: custom_device_order={custom_device_order}")/' /app/services/rakuten_processor.py
```

### Database Path Issues
- Docker container: Always use `/app/` prefix
- Local development: `./backend/product_attributes_new.db`
- Docker path: `/app/product_attributes_new.db`

### Encoding Issues
```bash
# Check file encoding
docker exec rakuten-sku-backend python -c "import chardet; print(chardet.detect(open('file.csv', 'rb').read()))"

# Force Shift-JIS conversion
docker exec rakuten-sku-backend python -c "import pandas as pd; df = pd.read_csv('file.csv', encoding='shift-jis'); df.to_csv('output.csv', encoding='shift-jis', index=False)"
```

### Frontend Not Updating
```bash
# Clear browser cache
Ctrl + Shift + Delete → Clear cached images and files

# Force rebuild with new hash
docker-compose build --no-cache frontend --build-arg CACHEBUST=$(date +%s)
```

## Deployment

### NAS Deployment (192.168.24.240)
```bash
# Automated deployment
./nas-direct-deploy.bat

# Manual deployment via Portainer
1. ./export-and-deploy.bat  # Creates .tar files
2. Upload to NAS: /export/*.tar
3. Import in Portainer: Images → Import
4. Deploy stack: portainer-stack.yml
```

### Production Checklist
- [ ] Set `PYTHONUNBUFFERED=1` for real-time logging
- [ ] Set `TZ=Asia/Tokyo` for JST timestamps
- [ ] Verify health checks pass
- [ ] Confirm volume mounts for data persistence
- [ ] Configure Nginx proxy for API routes

## Development Guidelines

### When Modifying Device Logic
1. Preserve `custom_device_order` if provided
2. Distinguish between `devices_to_add` (all) and truly new devices
3. Update parent row variation definitions after changes
4. Test with multi-product CSV files

### When Adding Database Features
1. Use `/app/` prefix absolute paths in Docker
2. Handle duplicates with UPDATE not INSERT
3. Maintain `usage_count` for tracking
4. Include brand auto-detection logic

### When Updating Frontend
1. Run `npm run build` in dev environment before Docker build
2. TypeScript compile check: `npx tsc --noEmit`
3. Clear browser cache after deployment
4. Ensure API endpoint contracts match backend