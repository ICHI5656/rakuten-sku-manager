# CLAUDE.md - Rakuten SKU Manager

This file provides guidance to Claude Code (claude.ai/code) when working with the Rakuten SKU Manager project.

## Project Overview

**rakuten_sku_manager** is a Docker-based web application for processing Rakuten RMS CSV files with device variation management, SKU auto-generation, and CSV output processing.

- **Location**: `/rakuten_sku_manager`
- **Stack**: FastAPI (Python) backend + React/TypeScript frontend + Docker
- **Purpose**: Automated Rakuten marketplace CSV processing with device management and SKU generation

## Quick Start

### Development Commands

```bash
# Start the application
docker-compose up -d

# Rebuild after code changes (force rebuild)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Architecture

### Backend (FastAPI)
- **Main App**: `backend/app.py` - FastAPI application with CORS middleware
- **Core Services**:
  - `services/rakuten_processor.py` - Main Rakuten CSV processing logic
  - `services/csv_processor.py` - Generic CSV reading/writing with encoding detection
  - `services/sku_manager.py` - SKU auto-numbering (sku_a000001 format)
  - `services/device_manager.py` - Device extraction and management
  - `services/validator.py` - Data validation and constraint checking
- **Models**: `models/schemas.py` - Pydantic data models
- **Port**: 8000

### Frontend (React + TypeScript)
- **Framework**: React 18 + TypeScript + Material-UI
- **Build Tool**: Vite
- **Main Component**: `src/components/DeviceManager.tsx` - Device management interface
- **Services**: `src/services/api.ts` - Backend API communication
- **Types**: `src/types/index.ts` - TypeScript interfaces
- **Port**: 3000

### Data Management
- **Upload Directory**: `data/uploads/` - Temporary CSV files
- **Output Directory**: `data/outputs/` - Processed CSV files
- **State Directory**: `data/state/` - SKU counters and persistent state
- **SKU State File**: `data/state/sku_counters.json` - Product-specific SKU counters

## Key Features

### CSV Processing
- **Input Format**: Rakuten RMS CSV with Shift-JIS encoding
- **Output Format**: Shift-JIS encoded CSV with CRLF line endings
- **Encoding Detection**: Automatic detection and conversion between Shift-JIS and UTF-8
- **Parent-Child Structure**: Handles Rakuten's parent row (商品) and child row (SKU) relationships

### Device Management
- **Device Addition**: Support for adding multiple devices (comma-separated input)
- **Device Removal**: Checkbox-based device removal from existing variations
- **Device Prioritization**: New devices are placed at the beginning of variation definitions
- **Product-Specific Devices**: Display different device sets per product in separate modal windows

### SKU Auto-Generation
- **Format**: `sku_a000001` with auto-incrementing numbers
- **Scope**: Product-specific counters (each product maintains independent SKU sequence)
- **Persistence**: SKU counters saved to JSON file for session continuity
- **Capacity**: Supports large SKU volumes with automatic counter management

### Variation Processing
- **Column Mapping**:
  - `商品管理番号（商品URL）` - Product ID
  - `SKU管理番号` - SKU ID
  - `バリエーション項目選択肢2` - Device variation field
  - `バリエーション2選択肢定義` - Device definition field (pipe-separated)
- **Cross Join**: Automatic generation of all device combinations with existing variations
- **Parent Row Updates**: Automatic updating of variation definitions in parent rows

## API Endpoints

| Method | Endpoint | Description | Key Parameters |
|--------|----------|-------------|----------------|
| POST | `/api/upload` | Upload CSV file for processing | `file: UploadFile` |
| POST | `/api/process` | Process CSV with device changes | `ProcessRequest` with `devices_to_add`, `devices_to_remove` |
| GET | `/api/download/{filename}` | Download processed CSV | `filename: str` |
| GET | `/api/devices/{file_id}` | Get device list from uploaded CSV | `file_id: str` |
| GET | `/api/status` | System status and statistics | - |
| DELETE | `/api/cleanup` | Clean up old files (24h+) | - |

## Data Models

### ProcessRequest
```typescript
interface ProcessRequest {
  file_id: string;
  devices_to_add: string[];
  devices_to_remove: string[];
  output_format: "single" | "per_product" | "split_60k";
}
```

### UploadResponse
```typescript
interface UploadResponse {
  file_id: string;
  devices: string[];
  products: ProductInfo[];
  product_devices?: Record<string, string[]>;  // Key feature for product grouping
  row_count: number;
  column_count: number;
}
```

## Important Processing Logic

### Device Definition Updates (`rakuten_processor.py:_update_device_definition`)
```python
# New devices are prioritized at the beginning
new_devices = []
existing_devices = []
devices_to_add_set = set(devices_to_add) if devices_to_add else set()

for device in all_devices:
    device_str = str(device)
    if device_str in devices_to_add_set:
        new_devices.append(device_str)
    else:
        existing_devices.append(device_str)

device_list = new_devices + existing_devices
```

### Product Device Extraction (`app.py`)
```python
# Extract product-specific device lists from variation definitions
if product_col in df.columns and sku_col in df.columns and var_def_col in df.columns:
    for idx, row in df.iterrows():
        has_product = pd.notna(row.get(product_col))
        sku_value = row.get(sku_col)
        is_sku_empty = pd.isna(sku_value) or sku_value == ''
        
        if has_product and is_sku_empty:  # Parent row
            product_id = row[product_col]
            var_def_value = row.get(var_def_col, None)
            if pd.notna(var_def_value) and var_def_value and str(var_def_value).strip():
                device_list = [d.strip() for d in str(var_def_value).split('|') if d.strip()]
                if device_list:
                    product_devices[product_id] = device_list
```

## Development Workflow

### Making Code Changes
1. Modify source code in `backend/` or `frontend/`
2. Rebuild containers: `docker-compose build --no-cache`
3. Restart services: `docker-compose up -d`
4. Clear browser cache if frontend changes not appearing
5. Check logs: `docker-compose logs -f backend` or `docker-compose logs -f frontend`

### Testing
- **Backend Tests**: No dedicated test framework configured - manual testing via API endpoints
- **Frontend Tests**: No test scripts configured - manual browser testing
- **CSV Testing**: Use sample Rakuten RMS CSV files with proper Shift-JIS encoding

### Debugging
- **API Debugging**: Check `docker-compose logs -f backend` for Python errors
- **Frontend Debugging**: Browser developer tools + `docker-compose logs -f frontend`
- **Data Flow**: DeviceManager includes extensive console.log debugging for productDevices flow

## Constraints and Limitations

### Rakuten RMS Constraints
- **Variation Limit**: Maximum 40 choices per variation attribute
- **SKU Limit**: Maximum 400 SKUs per product
- **File Size**: Recommended maximum 100MB
- **Encoding**: Must be Shift-JIS for Rakuten compatibility

### System Constraints
- **File Retention**: Automatic cleanup after 24 hours
- **Memory Usage**: Depends on CSV file size and number of variations
- **Concurrent Processing**: Single-threaded CSV processing

## File Naming Conventions

### Input Files
- Pattern: `upload_{timestamp}_{original_filename}`
- Location: `data/uploads/`

### Output Files
- **Single File**: `item_{timestamp}.csv`
- **Per Product**: `item_{timestamp}_{index}.csv`
- **Split Files**: `item_{timestamp}_{chunk_number}.csv`
- Location: `data/outputs/`

## Troubleshooting

### Common Issues
1. **Port Conflicts**: Change ports in `docker-compose.yml` if 3000/8000 are in use
2. **Character Encoding**: Ensure input CSV files are Shift-JIS encoded
3. **Frontend Not Updating**: Clear browser cache and rebuild with `--no-cache`
4. **Device Grouping Not Showing**: Check `productDevices` in browser console and backend logs

### Debug Commands
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 backend
docker-compose logs --tail=100 frontend

# Restart single service
docker-compose restart backend

# Force complete rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Important Notes
- This system handles Japanese text data with proper Shift-JIS encoding support
- The application prioritizes newly added devices at the beginning of variation lists
- Product-specific device grouping enables handling multiple products with different device sets
- SKU generation is product-scoped to avoid conflicts between different products
- Docker is required for proper development and deployment - no native Python/Node.js setup documented

## Recent Enhancements
- **Multi-device Addition**: Support for comma-separated device input (`test1, test2, test3`)
- **Device Prioritization**: New devices automatically placed at beginning of variation definitions
- **Product Grouping**: Modal dialog system for viewing product-specific device lists
- **Enhanced Debugging**: Extensive logging and visual debugging elements in DeviceManager component