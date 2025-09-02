"""
Backend API with Supabase integration
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
import logging

# Import Supabase connection
from supabase_client import supabase_connection

# Import existing services
from services.csv_processor import CSVProcessor
from services.sku_manager import SKUManager
from services.device_manager import DeviceManager
from services.validator import Validator
from services.rakuten_processor import RakutenCSVProcessor
from services.batch_processor import BatchProcessor
from models.schemas import ProcessRequest, DeviceAction, ProcessingOptions

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Rakuten SKU Manager API (Supabase)", version="2.0.0")

# CORS設定
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

BASE_DIR = Path(__file__).parent
DATA_DIR = Path("/app/data")
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
STATE_DIR = DATA_DIR / "state"

for dir_path in [UPLOAD_DIR, OUTPUT_DIR, STATE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

csv_processor = CSVProcessor()
sku_manager = SKUManager(STATE_DIR / "sku_counters.json")
device_manager = DeviceManager()
validator = Validator()
rakuten_processor = RakutenCSVProcessor(STATE_DIR / "sku_counters.json")
batch_processor = BatchProcessor(STATE_DIR)

@app.get("/")
async def root():
    mode = "Supabase" if supabase_connection.is_enabled() else "SQLite"
    return {
        "message": "Rakuten SKU Manager API",
        "version": "2.0.0",
        "database_mode": mode
    }

@app.get("/api/database/mode")
async def get_database_mode():
    """Get current database mode"""
    if supabase_connection.is_enabled():
        return {
            "mode": "supabase",
            "enabled": True,
            "url": os.getenv('SUPABASE_URL')
        }
    else:
        return {
            "mode": "sqlite",
            "enabled": False
        }

# =====================================
# Supabase Database API Endpoints
# =====================================

@app.get("/api/database/brands")
async def get_brands():
    """Get all brands from database"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            brands = supabase_connection.get_brands()
            if brands is None:
                return []
            return brands
        else:
            # SQLite fallback
            import sqlite3
            db_path = '/app/brand_attributes.db'
            if not os.path.exists(db_path):
                return []
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT brand_name FROM brand_values ORDER BY brand_name")
            brands = [{"brand_name": row["brand_name"]} for row in cursor.fetchall()]
            conn.close()
            
            return brands
    except Exception as e:
        logger.error(f"Error fetching brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/database/brand-values/{brand_name}")
async def get_brand_values(brand_name: str):
    """Get brand values from database"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            values = supabase_connection.get_brand_values(brand_name)
            if values is None:
                return []
            return values
        else:
            # SQLite fallback
            import sqlite3
            db_path = '/app/brand_attributes.db'
            if not os.path.exists(db_path):
                return []
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM brand_values 
                WHERE brand_name = ? 
                ORDER BY row_index
            """, (brand_name,))
            
            values = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return values
    except Exception as e:
        logger.error(f"Error fetching brand values: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/database/brands")
async def create_brand(request: dict):
    """Create a new brand"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            result = supabase_connection.create_brand(request)
            return {"message": "Brand created successfully", "data": result}
        else:
            # SQLite fallback
            import sqlite3
            conn = sqlite3.connect('/app/brand_attributes.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO brand_attributes (brand_name, brand_category)
                VALUES (?, ?)
            """, (request['brand_name'], request.get('brand_category', 'mobile_device')))
            
            conn.commit()
            conn.close()
            
            return {"message": "Brand created successfully"}
    except Exception as e:
        logger.error(f"Error creating brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/database/brand-values")
async def create_brand_value(request: dict):
    """Create a new brand value"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            result = supabase_connection.create_brand_value(request)
            return {"message": "Brand value created successfully", "data": result}
        else:
            # SQLite fallback
            import sqlite3
            conn = sqlite3.connect('/app/brand_attributes.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO brand_values (brand_name, row_index, attribute_value)
                VALUES (?, ?, ?)
            """, (request['brand_name'], request['row_index'], request['attribute_value']))
            
            conn.commit()
            conn.close()
            
            return {"message": "Brand value created successfully"}
    except Exception as e:
        logger.error(f"Error creating brand value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/database/brand-values/{value_id}")
async def update_brand_value(value_id: int, request: dict):
    """Update a brand value"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            result = supabase_connection.update_brand_value(value_id, request)
            return {"message": "Brand value updated successfully", "data": result}
        else:
            # SQLite fallback
            import sqlite3
            conn = sqlite3.connect('/app/brand_attributes.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE brand_values 
                SET attribute_value = ?
                WHERE id = ?
            """, (request['attribute_value'], value_id))
            
            conn.commit()
            conn.close()
            
            return {"message": "Brand value updated successfully"}
    except Exception as e:
        logger.error(f"Error updating brand value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/database/brand-values/{value_id}")
async def delete_brand_value(value_id: int):
    """Delete a brand value"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            result = supabase_connection.delete_brand_value(value_id)
            return {"message": "Brand value deleted successfully", "data": result}
        else:
            # SQLite fallback
            import sqlite3
            conn = sqlite3.connect('/app/brand_attributes.db')
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM brand_values WHERE id = ?", (value_id,))
            
            conn.commit()
            conn.close()
            
            return {"message": "Brand value deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting brand value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================
# Device Attributes API
# =====================================

@app.get("/api/product-attributes/devices")
async def get_devices(brand: Optional[str] = None):
    """Get devices from database"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            devices = supabase_connection.get_devices(brand)
            if devices is None:
                return []
            return devices
        else:
            # SQLite fallback
            import sqlite3
            db_path = '/app/product_attributes_new.db'
            if not os.path.exists(db_path):
                return []
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if brand:
                cursor.execute("""
                    SELECT * FROM device_attributes 
                    WHERE brand = ? 
                    ORDER BY device_name
                """, (brand,))
            else:
                cursor.execute("""
                    SELECT * FROM device_attributes 
                    ORDER BY brand, device_name
                """)
            
            devices = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return devices
    except Exception as e:
        logger.error(f"Error fetching devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/product-attributes/devices")
async def create_device(request: dict):
    """Create a new device"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            result = supabase_connection.create_device(request)
            return {"message": "Device created successfully", "data": result}
        else:
            # SQLite fallback
            import sqlite3
            conn = sqlite3.connect('/app/product_attributes_new.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO device_attributes 
                (brand, device_name, attribute_value, size_category, usage_count)
                VALUES (?, ?, ?, ?, ?)
            """, (
                request['brand'],
                request['device_name'],
                request['attribute_value'],
                request.get('size_category', ''),
                request.get('usage_count', 0)
            ))
            
            conn.commit()
            conn.close()
            
            return {"message": "Device created successfully"}
    except Exception as e:
        logger.error(f"Error creating device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/product-attributes/devices/{device_id}")
async def update_device(device_id: int, request: dict):
    """Update a device"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            result = supabase_connection.update_device(device_id, request)
            return {"message": "Device updated successfully", "data": result}
        else:
            # SQLite fallback
            import sqlite3
            conn = sqlite3.connect('/app/product_attributes_new.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE device_attributes 
                SET attribute_value = ?, size_category = ?
                WHERE id = ?
            """, (
                request['attribute_value'],
                request.get('size_category', ''),
                device_id
            ))
            
            conn.commit()
            conn.close()
            
            return {"message": "Device updated successfully"}
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/product-attributes/devices/{device_id}")
async def delete_device(device_id: int):
    """Delete a device"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            result = supabase_connection.delete_device(device_id)
            return {"message": "Device deleted successfully", "data": result}
        else:
            # SQLite fallback
            import sqlite3
            conn = sqlite3.connect('/app/product_attributes_new.db')
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM device_attributes WHERE id = ?", (device_id,))
            
            conn.commit()
            conn.close()
            
            return {"message": "Device deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================
# SKU Counter Management
# =====================================

@app.get("/api/sku-counters/{product_id}")
async def get_sku_counter(product_id: str):
    """Get SKU counter for a product"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            counter = supabase_connection.get_sku_counter(product_id)
            return {"product_id": product_id, "counter": counter or 0}
        else:
            # File-based fallback
            state_file = STATE_DIR / "sku_counters.json"
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    counters = json.load(f)
                    return {"product_id": product_id, "counter": counters.get(product_id, 0)}
            return {"product_id": product_id, "counter": 0}
    except Exception as e:
        logger.error(f"Error fetching SKU counter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sku-counters/{product_id}")
async def update_sku_counter(product_id: str, request: dict):
    """Update SKU counter for a product"""
    try:
        counter = request.get('counter', 0)
        
        if supabase_connection.is_enabled():
            # Supabase mode
            result = supabase_connection.update_sku_counter(product_id, counter)
            return {"message": "SKU counter updated successfully", "data": result}
        else:
            # File-based fallback
            state_file = STATE_DIR / "sku_counters.json"
            counters = {}
            
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    counters = json.load(f)
            
            counters[product_id] = counter
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(counters, f, ensure_ascii=False, indent=2)
            
            return {"message": "SKU counter updated successfully"}
    except Exception as e:
        logger.error(f"Error updating SKU counter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================
# Database Statistics
# =====================================

@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        if supabase_connection.is_enabled():
            # Supabase mode
            stats = supabase_connection.get_stats()
            return stats
        else:
            # SQLite fallback
            stats = {
                'total_brands': 0,
                'total_devices': 0,
                'total_values': 0,
                'database_mode': 'sqlite'
            }
            
            # Count brand values
            brand_db = '/app/brand_attributes.db'
            if os.path.exists(brand_db):
                import sqlite3
                conn = sqlite3.connect(brand_db)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(DISTINCT brand_name) FROM brand_values")
                stats['total_brands'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM brand_values")
                stats['total_values'] = cursor.fetchone()[0]
                
                conn.close()
            
            # Count devices
            device_db = '/app/product_attributes_new.db'
            if os.path.exists(device_db):
                import sqlite3
                conn = sqlite3.connect(device_db)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM device_attributes")
                stats['total_devices'] = cursor.fetchone()[0]
                
                conn.close()
            
            return stats
    except Exception as e:
        logger.error(f"Error fetching database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include all other endpoints from original app.py
# (upload_csv, process_csv, download_file, batch operations, etc.)
# These remain the same but will use Supabase for device/brand lookups when enabled

# Copy all remaining endpoints from app.py...
# [The rest of the endpoints would be copied here with minor modifications
# to use supabase_connection when checking for device attributes and brand values]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)