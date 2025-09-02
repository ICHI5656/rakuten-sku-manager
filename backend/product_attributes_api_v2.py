from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import json
import tempfile
import chardet
from pathlib import Path
import io
import openpyxl

router = APIRouter(prefix="/api/product-attributes", tags=["product-attributes"])

DB_PATH = "/app/product_attributes_new.db"

class DeviceCreate(BaseModel):
    brand: str
    device_name: str
    attribute_value: str
    size_category: Optional[str] = ""  # サイズカテゴリを任意に
    usage_count: Optional[int] = 0

class DeviceUpdate(BaseModel):
    brand: Optional[str] = None
    device_name: Optional[str] = None
    attribute_value: Optional[str] = None
    size_category: Optional[str] = None
    usage_count: Optional[int] = None

def get_db_connection():
    """Get database connection"""
    if not os.path.exists(DB_PATH):
        create_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    """Create the database structure"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 新しいテーブル構造
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            device_name TEXT NOT NULL,
            attribute_value TEXT NOT NULL,
            size_category TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(brand, device_name, size_category)
        )
    """)
    
    # ブランドマスターテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT UNIQUE NOT NULL,
            brand_name_jp TEXT,
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # インデックス
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_brand ON device_attributes(brand)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_device ON device_attributes(device_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_size ON device_attributes(size_category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_brand_device ON device_attributes(brand, device_name)")
    
    # デフォルトブランドを挿入
    default_brands = [
        ('iPhone', 'iPhone', 1),
        ('Xperia', 'Xperia', 2),
        ('AQUOS', 'AQUOS', 3),
        ('Galaxy', 'Galaxy', 4),
        ('Google Pixel', 'Google Pixel', 5),
        ('HUAWEI', 'HUAWEI', 6),
        ('arrows', 'arrows', 7),
        ('その他', 'その他', 99)
    ]
    
    for brand_name, brand_name_jp, order in default_brands:
        cursor.execute("""
            INSERT OR IGNORE INTO brands (brand_name, brand_name_jp, display_order) 
            VALUES (?, ?, ?)
        """, (brand_name, brand_name_jp, order))
    
    conn.commit()
    conn.close()

@router.get("/brands")
async def get_brands():
    """Get list of all brands with device counts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                b.brand_name,
                b.brand_name_jp,
                b.display_order,
                COUNT(DISTINCT d.id) as device_count
            FROM brands b
            LEFT JOIN device_attributes d ON b.brand_name = d.brand
            WHERE b.is_active = 1
            GROUP BY b.brand_name, b.brand_name_jp, b.display_order
            ORDER BY b.display_order
        """)
        
        brands = []
        for row in cursor.fetchall():
            brands.append({
                "id": row[0],
                "name": row[0],
                "name_jp": row[1],
                "display_order": row[2],
                "device_count": row[3]
            })
        
        conn.close()
        return {"brands": brands, "total": len(brands)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices")
async def get_devices(
    brand: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    size_category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(1000, ge=1, le=1000)
):
    """Get all devices (returns array for frontend compatibility)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        where_clauses = []
        params = []
        
        if brand:
            where_clauses.append("brand = ?")
            params.append(brand)
        
        if search:
            where_clauses.append("(device_name LIKE ? OR attribute_value LIKE ?)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        if size_category:
            where_clauses.append("size_category = ?")
            params.append(size_category)
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Get all data (limited to 1000 for safety)
        data_query = f"""
            SELECT id, brand, device_name, attribute_value, size_category, usage_count, created_at, updated_at
            FROM device_attributes
            {where_sql}
            ORDER BY usage_count DESC, brand, device_name
            LIMIT 1000
        """
        cursor.execute(data_query, params)
        
        devices = []
        for row in cursor.fetchall():
            devices.append({
                "id": row[0],
                "brand": row[1],
                "device_name": row[2],
                "attribute_value": row[3],
                "size_category": row[4],
                "usage_count": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            })
        
        conn.close()
        
        # Return array directly for frontend
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/devices")
async def create_device(device: DeviceCreate):
    """Create a new device or update if exists"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if device already exists
        cursor.execute("""
            SELECT id, usage_count FROM device_attributes 
            WHERE brand = ? AND device_name = ? AND size_category = ?
        """, (device.brand, device.device_name, device.size_category or ''))
        
        existing = cursor.fetchone()
        
        if existing:
            # Device exists - update it
            device_id = existing[0]
            new_usage_count = existing[1] + 1
            
            cursor.execute("""
                UPDATE device_attributes 
                SET attribute_value = ?, usage_count = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (device.attribute_value, new_usage_count, device_id))
        else:
            # Create new device
            cursor.execute("""
                INSERT INTO device_attributes 
                (brand, device_name, attribute_value, size_category, usage_count)
                VALUES (?, ?, ?, ?, ?)
            """, (device.brand, device.device_name, device.attribute_value, 
                  device.size_category or '', device.usage_count))
            
            device_id = cursor.lastrowid
        
        conn.commit()
        
        # Get the device (created or updated)
        cursor.execute("""
            SELECT * FROM device_attributes WHERE id = ?
        """, (device_id,))
        
        row = cursor.fetchone()
        result_device = {
            "id": row[0],
            "brand": row[1],
            "device_name": row[2],
            "attribute_value": row[3],
            "size_category": row[4],
            "usage_count": row[5],
            "created_at": row[6],
            "updated_at": row[7]
        }
        
        conn.close()
        return result_device
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/devices/{device_id}")
async def update_device(device_id: int, device: DeviceUpdate):
    """Update a device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query
        update_fields = []
        params = []
        
        if device.brand is not None:
            update_fields.append("brand = ?")
            params.append(device.brand)
        if device.device_name is not None:
            update_fields.append("device_name = ?")
            params.append(device.device_name)
        if device.attribute_value is not None:
            update_fields.append("attribute_value = ?")
            params.append(device.attribute_value)
        if device.size_category is not None:
            update_fields.append("size_category = ?")
            params.append(device.size_category)
        if device.usage_count is not None:
            update_fields.append("usage_count = ?")
            params.append(device.usage_count)
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(device_id)
        
        cursor.execute(f"""
            UPDATE device_attributes
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, params)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        
        conn.commit()
        conn.close()
        
        return {"message": "Device updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/devices/{device_id}")
async def delete_device(device_id: int):
    """Delete a device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM device_attributes WHERE id = ?", (device_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        
        conn.commit()
        conn.close()
        
        return {"message": "Device deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total devices
        cursor.execute("SELECT COUNT(*) FROM device_attributes")
        total_devices = cursor.fetchone()[0]
        
        # Devices by brand
        cursor.execute("""
            SELECT brand, COUNT(*) as count
            FROM device_attributes
            GROUP BY brand
            ORDER BY count DESC
        """)
        
        brands_data = []
        for row in cursor.fetchall():
            brands_data.append({
                "brand": row[0],
                "count": row[1]
            })
        
        # Devices by size
        cursor.execute("""
            SELECT size_category, COUNT(*) as count
            FROM device_attributes
            GROUP BY size_category
            ORDER BY count DESC
        """)
        
        sizes_data = []
        for row in cursor.fetchall():
            sizes_data.append({
                "size": row[0],
                "count": row[1]
            })
        
        # Most used devices
        cursor.execute("""
            SELECT device_name, attribute_value, usage_count
            FROM device_attributes
            ORDER BY usage_count DESC
            LIMIT 10
        """)
        
        popular_devices = []
        for row in cursor.fetchall():
            popular_devices.append({
                "device_name": row[0],
                "attribute_value": row[1],
                "usage_count": row[2]
            })
        
        conn.close()
        
        return {
            "total_devices": total_devices,
            "by_brand": brands_data,
            "by_size": sizes_data,
            "popular_devices": popular_devices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...)):
    """Import devices from CSV file"""
    try:
        contents = await file.read()
        
        # Detect encoding
        detected = chardet.detect(contents)
        encoding = detected['encoding'] or 'shift-jis'
        
        # Read CSV
        df = pd.read_csv(io.StringIO(contents.decode(encoding)))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imported = 0
        skipped = 0
        
        # Expected columns: brand, device_name, attribute_value, size_category
        required_columns = ['brand', 'device_name', 'attribute_value', 'size_category']
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing_columns}")
        
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO device_attributes 
                    (brand, device_name, attribute_value, size_category, usage_count)
                    VALUES (?, ?, ?, ?, 0)
                """, (row['brand'], row['device_name'], row['attribute_value'], row['size_category']))
                
                if cursor.rowcount > 0:
                    imported += 1
                else:
                    skipped += 1
            except:
                skipped += 1
        
        conn.commit()
        conn.close()
        
        return {
            "message": "CSV imported successfully",
            "imported": imported,
            "skipped": skipped
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-csv")
async def export_csv(brand: Optional[str] = None):
    """Export devices to CSV file"""
    try:
        conn = get_db_connection()
        
        query = """
            SELECT brand, device_name, attribute_value, size_category, usage_count
            FROM device_attributes
        """
        params = []
        
        if brand:
            query += " WHERE brand = ?"
            params.append(brand)
        
        query += " ORDER BY brand, device_name"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='shift-jis') as f:
            df.to_csv(f, index=False, encoding='shift-jis')
            temp_path = f.name
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"product_attributes_{brand if brand else 'all'}_{timestamp}.csv"
        
        return FileResponse(
            path=temp_path,
            filename=filename,
            media_type="text/csv; charset=shift-jis",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_excel():
    """Export device attributes as Excel file"""
    try:
        conn = get_db_connection()
        
        # Get all device attributes
        query = """
            SELECT id, brand, device_name, attribute_value, size_category, usage_count
            FROM device_attributes
            ORDER BY brand, device_name
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Device Attributes', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Device Attributes']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Return Excel file
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                "Content-Disposition": f"attachment; filename=device_attributes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_excel(file: UploadFile = File(...)):
    """Import device attributes from Excel file"""
    try:
        # Save uploaded file temporarily
        contents = await file.read()
        
        # Read Excel file
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['brand', 'device_name', 'attribute_value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imported = 0
        updated = 0
        
        for _, row in df.iterrows():
            brand = str(row['brand']) if pd.notna(row['brand']) else ''
            device_name = str(row['device_name']) if pd.notna(row['device_name']) else ''
            attribute_value = str(row['attribute_value']) if pd.notna(row['attribute_value']) else ''
            size_category = str(row['size_category']) if 'size_category' in row and pd.notna(row['size_category']) else ''
            
            if not brand or not device_name:
                continue
            
            # Check if device exists
            cursor.execute("""
                SELECT id FROM device_attributes
                WHERE brand = ? AND device_name = ?
            """, (brand, device_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing device
                cursor.execute("""
                    UPDATE device_attributes
                    SET attribute_value = ?, size_category = ?
                    WHERE id = ?
                """, (attribute_value, size_category, existing[0]))
                updated += 1
            else:
                # Insert new device
                cursor.execute("""
                    INSERT INTO device_attributes (brand, device_name, attribute_value, size_category, usage_count)
                    VALUES (?, ?, ?, ?, 0)
                """, (brand, device_name, attribute_value, size_category))
                imported += 1
        
        conn.commit()
        conn.close()
        
        return {
            "message": "Excel import completed successfully",
            "imported": imported,
            "updated": updated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/template-csv")
async def get_template_csv():
    """Get CSV template for import"""
    try:
        # Create template DataFrame
        template_data = {
            'brand': ['iPhone', 'Xperia', 'AQUOS', 'Galaxy', 'Google Pixel'],
            'device_name': ['iPhone16 ProMax', '10 VI(SO-52E)', 'wish4(SH-52E)', 'S25 Ultra (SC-52F)', 'Pixel 10 Pro'],
            'attribute_value': ['iPhone 16 Pro Max', 'Xperia 10 VI', 'AQUOS wish4', 'Galaxy S25 Ultra', 'Google Pixel 10 Pro'],
            'size_category': ['2L', 'LL', '3L', '3L', '2L']
        }
        
        df = pd.DataFrame(template_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='shift-jis') as f:
            df.to_csv(f, index=False, encoding='shift-jis')
            temp_path = f.name
        
        return FileResponse(
            path=temp_path,
            filename="product_attributes_template.csv",
            media_type="text/csv; charset=shift-jis",
            headers={
                "Content-Disposition": "attachment; filename*=UTF-8''product_attributes_template.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sizes")
async def get_sizes():
    """Get all unique size categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT size_category, COUNT(*) as count
            FROM device_attributes
            WHERE size_category IS NOT NULL AND size_category != ''
            GROUP BY size_category
            ORDER BY size_category
        """)
        
        sizes = []
        for row in cursor.fetchall():
            sizes.append({
                "size": row[0],
                "count": row[1]
            })
        
        conn.close()
        
        return {"sizes": sizes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear-all")
async def clear_all_devices():
    """Clear all devices from database (use with caution)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM device_attributes")
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return {
            "message": f"Deleted {deleted} devices",
            "deleted": deleted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))