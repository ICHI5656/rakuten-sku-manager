from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import json
from enum import Enum

router = APIRouter(prefix="/api/multi-database", tags=["multi-database"])

class DatabaseType(str, Enum):
    BRAND_ATTRIBUTES = "brand_attributes"
    PRODUCT_ATTRIBUTES_8 = "product_attributes_8"

DB_PATHS = {
    DatabaseType.BRAND_ATTRIBUTES: "brand_attributes.db",
    DatabaseType.PRODUCT_ATTRIBUTES_8: "product_attributes_new.db"
}

class AttributeCreate(BaseModel):
    name: str
    category: Optional[str] = None
    value: Optional[str] = None

class AttributeUpdate(BaseModel):
    value: str

class QueryRequest(BaseModel):
    query: str
    params: Optional[List[Any]] = None

def get_db_connection(db_type: DatabaseType):
    """Get database connection for specified database type"""
    db_path = DB_PATHS.get(db_type)
    if not db_path or not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail=f"Database {db_type} not found")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/databases")
async def list_databases():
    """List all available databases"""
    databases = []
    for db_type, db_path in DB_PATHS.items():
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            databases.append({
                "type": db_type,
                "path": db_path,
                "size": size,
                "exists": True
            })
        else:
            databases.append({
                "type": db_type,
                "path": db_path,
                "exists": False
            })
    return databases

@router.get("/{db_type}/stats")
async def get_database_stats(db_type: DatabaseType):
    """Get database statistics for specified database"""
    try:
        conn = get_db_connection(db_type)
        cursor = conn.cursor()
        
        stats = {}
        
        if db_type == DatabaseType.BRAND_ATTRIBUTES:
            # Brand database stats
            cursor.execute("SELECT COUNT(*) FROM brand_attributes")
            stats["total_brands"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM brand_values")
            stats["total_values"] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT brand_name, COUNT(*) as value_count
                FROM brand_values
                GROUP BY brand_name
                ORDER BY value_count DESC
                LIMIT 5
            """)
            stats["top_brands"] = [{"brand": row[0], "count": row[1]} for row in cursor.fetchall()]
            
        elif db_type == DatabaseType.PRODUCT_ATTRIBUTES_8:
            # Product attributes 8 database stats (new structure)
            cursor.execute("SELECT COUNT(DISTINCT size_category) FROM product_devices")
            stats["total_sizes"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM product_devices")
            stats["total_devices"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM attribute_mappings")
            stats["total_mappings"] = cursor.fetchone()[0]
            
            # Devices per size
            cursor.execute("""
                SELECT size_category, COUNT(*) as device_count
                FROM product_devices
                GROUP BY size_category
                ORDER BY device_count DESC
                LIMIT 10
            """)
            stats["devices_by_size"] = [{"size": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Most popular devices (available in multiple sizes)
            cursor.execute("""
                SELECT variation_item_choice_2, COUNT(DISTINCT size_category) as size_count
                FROM product_devices
                GROUP BY variation_item_choice_2
                ORDER BY size_count DESC
                LIMIT 5
            """)
            stats["popular_devices"] = [{"device": row[0], "sizes": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{db_type}/data")
async def get_data(
    db_type: DatabaseType,
    table: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Get data from specified database and table"""
    try:
        conn = get_db_connection(db_type)
        cursor = conn.cursor()
        
        # Get available tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not table:
            # Return table list if no table specified
            conn.close()
            return {"tables": tables}
        
        if table not in tables:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Table {table} not found")
        
        # Get data from specified table
        cursor.execute(f"SELECT * FROM {table} LIMIT ?", (limit,))
        columns = [description[0] for description in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "table": table,
            "columns": columns,
            "data": data,
            "total_count": total_count,
            "returned_count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{db_type}/devices-by-size/{size}")
async def get_devices_by_size(db_type: DatabaseType, size: str):
    """Get devices for a specific size"""
    if db_type != DatabaseType.PRODUCT_ATTRIBUTES_8:
        raise HTTPException(status_code=400, detail="This endpoint is only for product_attributes_8 database")
    
    try:
        conn = get_db_connection(db_type)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, size_category, variation_item_choice_2, product_attribute_8, sheet_name
            FROM product_devices
            WHERE size_category = ?
            ORDER BY variation_item_choice_2
        """, (size,))
        
        values = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{db_type}/device-mappings")
async def get_device_mappings(db_type: DatabaseType):
    """Get all device mappings"""
    if db_type != DatabaseType.PRODUCT_ATTRIBUTES_8:
        raise HTTPException(status_code=400, detail="This endpoint is only for product_attributes_8 database")
    
    try:
        conn = get_db_connection(db_type)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM attribute_mappings
            ORDER BY device_name, size_category
        """)
        
        mappings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return mappings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{db_type}/add-device")
async def add_device(db_type: DatabaseType, device: Dict[str, Any]):
    """Add a new device to the database"""
    if db_type != DatabaseType.PRODUCT_ATTRIBUTES_8:
        raise HTTPException(status_code=400, detail="This endpoint is only for product_attributes_8 database")
    
    try:
        conn = get_db_connection(db_type)
        cursor = conn.cursor()
        
        # Insert into product_devices table
        cursor.execute("""
            INSERT OR REPLACE INTO product_devices 
            (size_category, variation_item_choice_2, product_attribute_8, sheet_name, row_index)
            VALUES (?, ?, ?, 'manual_entry', 0)
        """, (
            device.get('size_category', '[L]'),
            device.get('variation_item_choice_2', ''),
            device.get('product_attribute_8', '')
        ))
        
        # Also insert into attribute_mappings
        cursor.execute("""
            INSERT OR REPLACE INTO attribute_mappings
            (device_name, attribute_value, size_category, usage_count)
            VALUES (?, ?, ?, 1)
        """, (
            device.get('variation_item_choice_2', ''),
            device.get('product_attribute_8', ''),
            device.get('size_category', '[L]')
        ))
        
        conn.commit()
        device_id = cursor.lastrowid
        conn.close()
        
        return {"success": True, "id": device_id, "message": "Device added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{db_type}/devices-by-brand")
async def get_devices_by_brand(
    db_type: DatabaseType,
    brand: str = Query(...),
    limit: int = Query(25, le=100),
    offset: int = Query(0, ge=0)
):
    """Get devices filtered by brand"""
    if db_type != DatabaseType.PRODUCT_ATTRIBUTES_8:
        raise HTTPException(status_code=400, detail="This endpoint is only for product_attributes_8 database")
    
    try:
        conn = get_db_connection(db_type)
        cursor = conn.cursor()
        
        # Build WHERE clause based on brand
        where_clause = ""
        params = []
        
        if brand == "iphone":
            where_clause = "WHERE (device_name LIKE ? OR attribute_value LIKE ?)"
            params = ["%iphone%", "%iPhone%"]
        elif brand == "xperia":
            where_clause = "WHERE (device_name LIKE ? OR device_name LIKE ? OR attribute_value LIKE ?)"
            params = ["%xperia%", "%SO-%", "%Xperia%"]
        elif brand == "aquos":
            where_clause = "WHERE (device_name LIKE ? OR device_name LIKE ? OR attribute_value LIKE ?)"
            params = ["%aquos%", "%SH-%", "%AQUOS%"]
        elif brand == "galaxy":
            where_clause = "WHERE (device_name LIKE ? OR device_name LIKE ? OR attribute_value LIKE ?)"
            params = ["%galaxy%", "%SC-%", "%Galaxy%"]
        elif brand == "pixel":
            where_clause = "WHERE (device_name LIKE ? OR attribute_value LIKE ?)"
            params = ["%pixel%", "%Pixel%"]
        elif brand == "huawei":
            where_clause = "WHERE (device_name LIKE ? OR device_name LIKE ? OR attribute_value LIKE ?)"
            params = ["%huawei%", "%mate%", "%HUAWEI%"]
        elif brand == "arrows":
            where_clause = "WHERE (device_name LIKE ? OR device_name LIKE ? OR attribute_value LIKE ?)"
            params = ["%arrows%", "%M0%", "%arrows%"]
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM attribute_mappings {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated data
        data_query = f"""
            SELECT 
                id,
                device_name,
                attribute_value,
                size_category,
                usage_count,
                created_at
            FROM attribute_mappings
            {where_clause}
            ORDER BY device_name
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        cursor.execute(data_query, params)
        
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "devices": devices,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{db_type}/query")
async def execute_query(db_type: DatabaseType, request: QueryRequest):
    """Execute a SQL query on specified database (read-only)"""
    try:
        # Only allow SELECT queries
        if not request.query.strip().upper().startswith('SELECT'):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
        
        conn = get_db_connection(db_type)
        cursor = conn.cursor()
        
        if request.params:
            cursor.execute(request.query, request.params)
        else:
            cursor.execute(request.query)
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "database": db_type,
            "columns": columns,
            "data": results,
            "row_count": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{db_type}/search")
async def search_in_database(
    db_type: DatabaseType,
    search_term: str = Query(..., min_length=1),
    limit: int = Query(50, le=500)
):
    """Search for a term across all text columns in the database"""
    try:
        conn = get_db_connection(db_type)
        cursor = conn.cursor()
        
        results = []
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Build search query for text columns
            text_columns = [col[1] for col in columns if col[2] in ('TEXT', 'VARCHAR')]
            
            if text_columns:
                where_clauses = [f"{col} LIKE ?" for col in text_columns]
                query = f"SELECT * FROM {table} WHERE {' OR '.join(where_clauses)} LIMIT ?"
                params = [f"%{search_term}%"] * len(text_columns) + [limit]
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                if rows:
                    column_names = [col[0] for col in cursor.description]
                    for row in rows:
                        results.append({
                            "table": table,
                            "data": dict(zip(column_names, row))
                        })
        
        conn.close()
        
        return {
            "search_term": search_term,
            "results": results[:limit],
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{db_type}/export")
async def export_database(db_type: DatabaseType):
    """Export the specified database file"""
    db_path = DB_PATHS.get(db_type)
    if not db_path or not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail=f"Database {db_type} not found")
    
    return FileResponse(
        db_path,
        media_type='application/x-sqlite3',
        filename=f'{db_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite'
    )