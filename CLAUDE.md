# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**rakuten_sku_manager** is a Docker-based web application for Rakuten RMS CSV processing and product attribute database management. It handles device variation management, SKU auto-numbering, cross-join expansion for Japanese e-commerce, and automatic ALT text generation for product images.

## Tech Stack
- **Backend**: FastAPI (Python 3.11), Pandas, SQLite/Supabase
- **Frontend**: React 18, TypeScript 5.9.2, Material-UI, Vite, Node.js 20
- **Infrastructure**: Docker Compose, Nginx
- **Database**: Dual-mode - SQLite (local) or Supabase (cloud)

## Essential Commands

### Quick Start
```bash
# Windows quick start
start-local.bat               # Basic local deployment
start-network.bat             # Network-enabled deployment

# Docker commands
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose restart        # Restart services

# Full rebuild (when major changes)
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# Access points
http://localhost:3000         # Frontend
http://localhost:8000/docs    # API documentation
```

### Development Commands
```bash
# Backend operations
docker-compose build --no-cache backend && docker-compose up -d backend
docker-compose logs -f backend
docker exec rakuten-sku-backend python /app/script_name.py

# Frontend operations  
docker-compose build --no-cache frontend && docker-compose up -d frontend
docker-compose logs -f frontend

# Local frontend development (without Docker)
cd frontend
npm install        # Install dependencies
npm run dev        # Start dev server (port 5173)
npm run build      # Build for production
npx tsc --noEmit   # TypeScript type checking
```

### Testing & Debugging
```bash
# Test CSV processing
docker cp test.csv rakuten-sku-backend:/app/test.csv
docker exec rakuten-sku-backend python /app/test_device_position.py

# Test ALT text auto-fill feature
docker exec rakuten-sku-backend python test_alt_text.py

# Test batch processing
curl -X POST http://localhost:8000/api/batch-upload -F "files=@file1.csv" -F "files=@file2.csv"
curl -X GET http://localhost:8000/api/batch-status/{batch_id}

# Database queries
docker exec rakuten-sku-backend sqlite3 /app/product_attributes_new.db "SELECT * FROM device_attributes LIMIT 10"

# Container restart optimization
restart-optimized.bat         # Windows optimized restart script
```

## Architecture Overview

### Processing Pipeline
```
CSV Upload → Encoding Detection → Product Grouping → Device Management → SKU Generation → Database Update → CSV Export
```

### Core Processing Flow

1. **CSV Upload & Validation** (`backend/app.py:upload_csv`)
   - Auto-detects Shift-JIS encoding
   - Groups by product management number (商品管理番号)
   - Extracts devices from variation2 definitions
   - File size limit increased to 1GB (configured in nginx.conf)

2. **Batch Processing** (`backend/services/batch_processor.py`)
   - Supports multiple CSV files simultaneously
   - Auto-detects different device patterns across files
   - `process_mode`: 'auto' | 'same_devices' | 'different_devices'
   - Handles device positioning per file when patterns differ

3. **Device Management** (`backend/services/rakuten_processor.py`)
   - Position priority: `custom_device_order` > `add_position` > default
   - Maintains consistency across products
   - Database integration for brand-based selection
   - **Important**: バリエーション2選択肢定義 appears ONLY in parent rows
   - **ALT Text Auto-Fill**: Automatically sets 商品画像名（ALT）1-10 to product name when 商品画像URL exists

4. **SKU Generation** (`backend/services/sku_manager.py`)
   - Format: `sku_a000001`, `sku_b000001` (global numbering)
   - State persistence: `/app/data/state/sku_counters.json`
   - Cross-join: colors × devices = total SKUs

5. **CSV Splitting** (`backend/services/csv_splitter.py`)
   - Auto-splits files >60k rows while maintaining parent product integrity
   - Ensures parent products and their SKUs stay together

6. **CSV Export** (`backend/product_attributes_api.py:export_csv`)
   - Parent device filtering for バリエーション2選択肢定義
   - Excludes child devices (キッズケータイ, らくらくフォン, BASIO, etc.)
   - Uses ROW_NUMBER() OVER PARTITION to identify parent devices

### Critical Business Rules

#### CSV Structure
- **Parent row**: Has product ID (商品管理番号), no SKU (SKU管理番号 is empty), contains variation definitions
- **SKU row**: Has both product ID and SKU number
- **Encoding**: Shift-JIS for input/output
- **バリエーション2選択肢定義**: Must be empty for ALL non-parent rows (SKU rows and others)

#### Device Positioning Algorithm
```python
# backend/services/rakuten_processor.py
if custom_device_order:
    device_list = custom_device_order
elif add_position == 'start':
    device_list = new_devices + existing_devices  
elif add_position == 'after' and after_device:
    index = existing_devices.index(after_device) + 1
    device_list = existing_devices[:index] + new_devices + existing_devices[index:]
else:
    device_list = existing_devices + new_devices
```

#### Parent Device Export Logic
```python
# backend/product_attributes_api.py:export_csv
# Filters out child/sub devices:
kids_senior_patterns = [
    'キッズケータイ', 'mamorino', 'あんしんファミリースマホ', 
    'あんしんスマホ', 'らくらくフォン', 'らくらくホン', 
    'BASIO', 'シンプルスマホ', 'かんたんスマホ'
]
# Uses ROW_NUMBER() to select first device in each group as parent
```

#### Rakuten RMS Constraints
- Max 40 variations per attribute
- Max 400 SKUs per product  
- Max 1GB file upload (configured in nginx)
- Files auto-delete after 24 hours
- CSV must be Shift-JIS encoded with CRLF line endings

## Frontend-Backend Contract

### Key API Endpoints
```typescript
POST /api/upload                    // Single file upload (max 1GB)
POST /api/process                   // Process single file
POST /api/batch-upload              // Multiple files upload
POST /api/batch-process             // Process batch with process_mode
GET /api/batch-status/{batch_id}    // Check batch status
GET /api/batch-download/{batch_id}  // Download batch results as ZIP
GET /api/download/{filename}        // Download processed file (with ?split=true for >60k rows)
GET /api/product-attributes/brands  // Get all brands with devices
GET /api/product-attributes/devices // Get devices by brand
GET /api/product-attributes/export-csv // Export parent devices only
```

### Process Request Interface
```typescript
interface ProcessRequest {
  file_id: string;
  devices_to_add: string[];
  custom_device_order?: string[];
  add_position?: 'start' | 'end' | 'after' | 'custom';
  after_device?: string;
  device_brand?: string;              // For brand-based selection
  process_mode?: 'auto' | 'same_devices' | 'different_devices';  // Batch processing mode
  reset_all_devices?: boolean;        // Clear all existing devices and replace
  output_format?: 'single' | 'per_product' | 'split_60k';
  auto_fill_alt_text?: boolean;       // Auto-fill ALT text for product images (default: true)
  device_attributes?: Array<{
    device: string;
    attribute_value: string;
    size_category?: string;
  }>;
}
```

## Database Configuration

### Dual-Mode Operation
- **SQLite Mode** (default): `/app/product_attributes_new.db`
- **Supabase Mode**: Enable with `USE_SUPABASE=true` in `.env`

### Database Schema
```sql
-- product_devices table (legacy/compatibility)
CREATE TABLE product_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    size_category TEXT NOT NULL,
    variation_item_choice_2 TEXT NOT NULL,
    product_attribute_8 TEXT NOT NULL,
    brand TEXT,
    sheet_name TEXT DEFAULT 'manual',
    row_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(size_category, variation_item_choice_2)
);

-- device_attributes table (new structure)
CREATE TABLE device_attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    device_name TEXT NOT NULL,
    attribute_value TEXT NOT NULL,
    size_category TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(brand, device_name, size_category)
);

-- Indexes for performance
CREATE INDEX idx_brand ON device_attributes(brand);
CREATE INDEX idx_device ON device_attributes(device_name);
CREATE INDEX idx_size ON device_attributes(size_category);
CREATE INDEX idx_variation ON product_devices(variation_item_choice_2);
CREATE INDEX idx_attribute ON product_devices(product_attribute_8);
```

## Deployment Scripts

### Windows Batch Files
- `start-local.bat` - Local deployment (localhost only)
- `start-network.bat` - Network-enabled deployment (LAN access)
- `configure-firewall.bat` - Setup Windows firewall for network access
- `clean-rebuild.bat` - Complete cleanup and rebuild
- `restart-optimized.bat` - Optimized container restart preserving data

### Network Deployment
```bash
# Enable network access
start-network.bat              # Uses docker-compose.network.yml
configure-firewall.bat          # Opens ports 3000, 8000

# Access from other machines
http://<host-ip>:3000           # Replace <host-ip> with actual IP
```

## Common Issues & Solutions

### Large File Processing (300MB+)
- Nginx and backend configured for 1GB max file size
- Use `split_60k` output format for automatic splitting
- Monitor Docker memory usage (6GB allocated)

### バリエーション2選択肢定義 Issues
- Must appear ONLY in parent rows (商品管理番号 present, SKU管理番号 empty)
- Automatically cleared from all other rows during processing
- Parent device export filters out child devices (キッズケータイ, etc.)
- Verified at multiple points: processing, saving, and download

### ALT Text Auto-Fill Not Working
- Verify 商品画像URL1-10 columns have actual URLs
- Check `auto_fill_alt_text=true` is passed in request
- Ensure processing parent rows (not SKU rows)
- ALT text only sets when corresponding image URL exists
- Feature processes 商品画像名（ALT）1 through 商品画像名（ALT）10

### Docker Build Cache Issues
```bash
# Force complete rebuild
docker-compose down
docker system prune -a --volumes
docker-compose build --no-cache
docker-compose up -d
```

### Frontend TypeScript Errors
```bash
cd frontend
npm install typescript --save-dev
npx tsc --version  # Should show 5.9.2+
```

### Database Path Issues
- Docker: Always use `/app/` prefix
- Local: `./backend/product_attributes_new.db`
- Never use relative paths in Docker context

### Encoding Problems
```python
# Force Shift-JIS for Rakuten CSV
df.to_csv(output_path, encoding='shift-jis', index=False, line_terminator='\r\n')
```

## Development Guidelines

### When Modifying Device Logic
1. Check `custom_device_order` preservation in `rakuten_processor.py`
2. Ensure バリエーション2選択肢定義 only in parent rows
3. Test batch processing with different device patterns
4. Verify brand dropdown updates correctly
5. Check parent device filtering in export_csv

### When Adding Database Features
1. Use absolute paths with `/app/` prefix in Docker
2. Handle duplicates with UPDATE not INSERT
3. Update both SQLite and Supabase handlers
4. Test brand aggregation queries
5. Maintain compatibility between product_devices and device_attributes tables

### When Updating Frontend
1. Build locally first: `npm run build`
2. Check types: `npx tsc --noEmit`
3. Clear browser cache after deployment
4. Ensure FormData correctly passes all parameters

### Git Workflow
```bash
git status                      # Always check status first
git checkout -b feature/name    # Create feature branch
git add -A                      # Stage changes
git commit -m "feat: description"
git push origin feature/name    # Push to GitHub
# Create PR to master branch (not main)
```

## Performance Optimization

- Batch processing uses ThreadPoolExecutor (max_workers=3)
- CSV processing optimized for large files (>100k rows, up to 200k)
- Database queries use indexes on device_name, brand_name
- Frontend uses React.memo for large device lists
- Docker containers allocated 6GB memory for large file processing
- File splitting maintains parent product integrity
- Parent device filtering uses SQL window functions for efficiency

## Security Considerations

- CORS configured for specific origins only
- File size limited to 1GB (configurable in nginx.conf)
- Uploaded files auto-delete after 24 hours
- No sensitive data in Git repository
- Supabase credentials in `.env` file only
- Docker health checks prevent failed container issues