from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import json
import io
import openpyxl

router = APIRouter(prefix="/api/database", tags=["database"])

DB_PATH = "brand_attributes.db"

class BrandCreate(BaseModel):
    brand_name: str
    brand_category: str = "mobile_device"

class BrandValueCreate(BaseModel):
    brand_name: str
    row_index: int
    attribute_value: str

class BrandValueUpdate(BaseModel):
    brand_name: Optional[str] = None
    row_index: Optional[int] = None
    attribute_value: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    params: Optional[List[Any]] = None

def get_db_connection():
    """Get database connection"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="Database not found")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/brands")
async def get_brands():
    """Get all brands"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, brand_name, brand_category, created_at
            FROM brand_attributes
            ORDER BY brand_name
        """)
        brands = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return brands
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand-values/{brand_name}")
async def get_brand_values(brand_name: str):
    """Get values for a specific brand"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, brand_name, row_index, attribute_value, created_at
            FROM brand_values
            WHERE brand_name = ?
            ORDER BY row_index
        """, (brand_name,))
        values = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brands")
async def create_brand(brand: BrandCreate):
    """Create a new brand"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if brand already exists
        cursor.execute("SELECT id FROM brand_attributes WHERE brand_name = ?", (brand.brand_name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Brand already exists")
        
        # Insert new brand
        cursor.execute("""
            INSERT INTO brand_attributes (brand_name, brand_category)
            VALUES (?, ?)
        """, (brand.brand_name, brand.brand_category))
        
        conn.commit()
        brand_id = cursor.lastrowid
        conn.close()
        
        return {"id": brand_id, "message": "Brand created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/brands/{brand_name}")
async def delete_brand(brand_name: str):
    """Delete a brand and its values"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete brand values first
        cursor.execute("DELETE FROM brand_values WHERE brand_name = ?", (brand_name,))
        
        # Delete brand
        cursor.execute("DELETE FROM brand_attributes WHERE brand_name = ?", (brand_name,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        conn.commit()
        conn.close()
        
        return {"message": "Brand deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brand-values")
async def create_brand_value(value: BrandValueCreate):
    """Create a new brand value"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if brand exists
        cursor.execute("SELECT id FROM brand_attributes WHERE brand_name = ?", (value.brand_name,))
        if not cursor.fetchone():
            # Create brand if it doesn't exist
            cursor.execute("""
                INSERT INTO brand_attributes (brand_name, brand_category)
                VALUES (?, 'mobile_device')
            """, (value.brand_name,))
        
        # Insert brand value
        cursor.execute("""
            INSERT INTO brand_values (brand_name, row_index, attribute_value)
            VALUES (?, ?, ?)
        """, (value.brand_name, value.row_index, value.attribute_value))
        
        conn.commit()
        value_id = cursor.lastrowid
        conn.close()
        
        return {"id": value_id, "message": "Brand value created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/brand-values/{value_id}")
async def update_brand_value(value_id: int, update: BrandValueUpdate):
    """Update a brand value"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if update.brand_name is not None:
            update_fields.append("brand_name = ?")
            params.append(update.brand_name)
        if update.row_index is not None:
            update_fields.append("row_index = ?")
            params.append(update.row_index)
        if update.attribute_value is not None:
            update_fields.append("attribute_value = ?")
            params.append(update.attribute_value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(value_id)
        query = f"UPDATE brand_values SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Value not found")
        
        conn.commit()
        conn.close()
        
        return {"message": "Value updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/brand-values/{value_id}")
async def delete_brand_value(value_id: int):
    """Delete a brand value"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM brand_values WHERE id = ?", (value_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Value not found")
        
        conn.commit()
        conn.close()
        
        return {"message": "Brand value deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total brands
        cursor.execute("SELECT COUNT(*) FROM brand_attributes")
        total_brands = cursor.fetchone()[0]
        
        # Get total values
        cursor.execute("SELECT COUNT(*) FROM brand_values")
        total_values = cursor.fetchone()[0]
        
        # Get last update time (most recent created_at)
        cursor.execute("""
            SELECT MAX(created_at) as last_updated
            FROM (
                SELECT created_at FROM brand_attributes
                UNION ALL
                SELECT created_at FROM brand_values
            )
        """)
        last_updated = cursor.fetchone()[0] or datetime.now().isoformat()
        
        conn.close()
        
        return {
            "total_brands": total_brands,
            "total_values": total_values,
            "last_updated": last_updated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_database():
    """Export brand database as Excel file"""
    try:
        conn = get_db_connection()
        
        # Get all brands and their values
        query = """
            SELECT DISTINCT brand_name 
            FROM brand_values 
            ORDER BY brand_name
        """
        brands_df = pd.read_sql_query(query, conn)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Create a sheet with all brand values
            all_data = []
            
            for brand in brands_df['brand_name']:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT row_index, attribute_value
                    FROM brand_values
                    WHERE brand_name = ?
                    ORDER BY row_index
                """, (brand,))
                
                values = cursor.fetchall()
                
                # Create column data
                col_data = {f'ブランド名({brand})': []}
                for row_idx, attr_value in values:
                    # Ensure list is long enough
                    while len(col_data[f'ブランド名({brand})']) <= row_idx:
                        col_data[f'ブランド名({brand})'].append('')
                    col_data[f'ブランド名({brand})'][row_idx] = attr_value
                
                # Add to all_data
                if not all_data:
                    all_data = col_data
                else:
                    # Merge with existing data
                    for key, values in col_data.items():
                        all_data[key] = values
            
            # Convert to DataFrame and write
            if all_data:
                df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in all_data.items()]))
                df.to_excel(writer, sheet_name='Brand Attributes', index=False)
        
        conn.close()
        
        # Return Excel file
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                "Content-Disposition": f"attachment; filename=brand_attributes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_data(file: UploadFile = File(...)):
    """Import data from Excel/CSV file"""
    try:
        # Save uploaded file
        contents = await file.read()
        temp_path = f"temp_{file.filename}"
        
        with open(temp_path, 'wb') as f:
            f.write(contents)
        
        # Read file based on extension
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(temp_path)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(temp_path, encoding='utf-8-sig')
        else:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Process and insert data
        conn = get_db_connection()
        cursor = conn.cursor()
        
        rows_imported = 0
        for col in df.columns:
            if 'ブランド名' in col:
                brand_name = col.replace('ブランド名(', '').replace(')', '')
                
                # Insert brand if not exists
                cursor.execute("""
                    INSERT OR IGNORE INTO brand_attributes (brand_name, brand_category)
                    VALUES (?, 'imported')
                """, (brand_name,))
                
                # Insert values
                for idx, value in enumerate(df[col]):
                    if pd.notna(value) and str(value).strip():
                        cursor.execute("""
                            INSERT INTO brand_values (brand_name, row_index, attribute_value)
                            VALUES (?, ?, ?)
                        """, (brand_name, idx, str(value)))
                        rows_imported += 1
        
        conn.commit()
        conn.close()
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {
            "message": "Data imported successfully",
            "rows_imported": rows_imported
        }
    except HTTPException:
        raise
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def execute_query(request: QueryRequest):
    """Execute a SQL query (read-only)"""
    try:
        # Only allow SELECT queries
        if not request.query.strip().upper().startswith('SELECT'):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.params:
            cursor.execute(request.query, request.params)
        else:
            cursor.execute(request.query)
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Get results
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        
        return {
            "columns": columns,
            "data": results,
            "row_count": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))