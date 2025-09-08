from fastapi import APIRouter, HTTPException, File, UploadFile, Query, Form
from fastapi.responses import FileResponse, JSONResponse
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

router = APIRouter(prefix="/api/product-attributes", tags=["product-attributes"])

DB_PATH = "product_attributes_new.db"

class DeviceCreate(BaseModel):
    brand: str
    device_name: str
    attribute_value: str
    size_category: str
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
        # Create database if it doesn't exist
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
    
    # 旧テーブル（互換性のため）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_devices (
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
        )
    """)
    
    # インデックス
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_brand ON device_attributes(brand)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_device ON device_attributes(device_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_size ON device_attributes(size_category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_brand_device ON device_attributes(brand, device_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_variation ON product_devices(variation_item_choice_2)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attribute ON product_devices(product_attribute_8)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_name ON attribute_mappings(device_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_size_category ON attribute_mappings(size_category)")
    
    conn.commit()
    conn.close()

@router.get("/brands")
async def get_brands():
    """Get list of brands with device counts for database management UI"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Define main brands
        main_brands = [
            {"id": "iPhone", "name": "iPhone", "name_jp": "iPhone", "db_name": "IPHONE"},
            {"id": "Xperia", "name": "Xperia", "name_jp": "Xperia", "db_name": "XPERIA"},
            {"id": "AQUOS", "name": "AQUOS", "name_jp": "AQUOS", "db_name": "AQUOS"},
            {"id": "Galaxy", "name": "Galaxy", "name_jp": "Galaxy", "db_name": "GALAXY"},
            {"id": "Pixel", "name": "Google Pixel", "name_jp": "Google Pixel", "db_name": "GOOGLE PIXEL"},
            {"id": "Huawei", "name": "HUAWEI", "name_jp": "HUAWEI", "db_name": "HUAWEI"},
            {"id": "arrows", "name": "arrows", "name_jp": "arrows", "db_name": "ARROWS"},
            {"id": "Other", "name": "その他", "name_jp": "その他", "db_name": "その他"}
        ]
        
        # Get device counts from device_attributes table if exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='device_attributes'
        """)
        has_device_attributes = cursor.fetchone() is not None
        
        brands = []
        for idx, brand_info in enumerate(main_brands):
            device_count = 0
            
            if has_device_attributes:
                cursor.execute("""
                    SELECT COUNT(*) FROM device_attributes WHERE brand = ?
                """, (brand_info["db_name"],))
                device_count = cursor.fetchone()[0]
            
            brands.append({
                "id": brand_info["id"],
                "name": brand_info["name"],
                "name_jp": brand_info["name_jp"],
                "display_order": idx,
                "device_count": device_count
            })
        
        conn.close()
        
        return {
            "brands": brands,
            "total": len(brands)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-brands")
async def get_available_brands()
    """Get list of available brands from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ブランド定義
        brands = [
            {"id": "iPhone", "label": "iPhone", "icon": "📱"},
            {"id": "Galaxy", "label": "Galaxy", "icon": "🌌"},
            {"id": "Xperia", "label": "Xperia", "icon": "📲"},
            {"id": "AQUOS", "label": "AQUOS", "icon": "💧"},
            {"id": "Pixel", "label": "Pixel", "icon": "🔷"},
            {"id": "Huawei", "label": "Huawei", "icon": "🌸"},
            {"id": "Xiaomi", "label": "Xiaomi", "icon": "🦊"},
            {"id": "OPPO", "label": "OPPO", "icon": "🟢"},
            {"id": "OnePlus", "label": "OnePlus", "icon": "➕"},
            {"id": "iPad", "label": "iPad", "icon": "📋"},
            {"id": "Surface", "label": "Surface", "icon": "🖥️"},
            {"id": "Other", "label": "その他", "icon": "📱"}
        ]
        
        # 各ブランドのデバイス数を取得
        for brand in brands:
            brand_id = brand["id"]
            if brand_id == "Other":
                cursor.execute("""
                    SELECT COUNT(DISTINCT variation_item_choice_2)
                    FROM product_devices
                """)
            else:
                # ブランドパターンの定義
                patterns = {
                    'iPhone': ['iphone', 'iPhone'],
                    'Galaxy': ['galaxy', 'Galaxy'],
                    'Xperia': ['xperia', 'Xperia', 'SO-'],
                    'AQUOS': ['aquos', 'AQUOS', 'SH-'],
                    'Pixel': ['pixel', 'Pixel'],
                    'Huawei': ['huawei', 'Huawei', 'P30', 'P40', 'Mate', 'nova'],
                    'Xiaomi': ['xiaomi', 'Xiaomi', 'Mi ', 'Redmi'],
                    'OPPO': ['oppo', 'OPPO', 'Reno', 'Find'],
                    'OnePlus': ['oneplus', 'OnePlus'],
                    'iPad': ['ipad', 'iPad'],
                    'Surface': ['surface', 'Surface']
                }
                
                brand_patterns = patterns.get(brand_id, [brand_id.lower()])
                query_parts = []
                for pattern in brand_patterns:
                    query_parts.append(f"variation_item_choice_2 LIKE '%{pattern}%'")
                
                query = f"""
                    SELECT COUNT(DISTINCT variation_item_choice_2)
                    FROM product_devices
                    WHERE {' OR '.join(query_parts)}
                """
                cursor.execute(query)
            
            count = cursor.fetchone()[0]
            brand["deviceCount"] = count
        
        conn.close()
        
        return {
            "brands": brands,
            "total": len(brands)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand-attributes/{brand}")
async def get_brand_attributes(brand: str):
    """Get random attributes for a specific brand"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ブランドに基づいてデバイス名パターンを定義
        brand_patterns = {
            'iPhone': ['iphone', 'iPhone'],
            'Galaxy': ['galaxy', 'Galaxy'],
            'Xperia': ['xperia', 'Xperia', 'SO-'],
            'AQUOS': ['aquos', 'AQUOS', 'SH-'],
            'Pixel': ['pixel', 'Pixel'],
            'Huawei': ['huawei', 'Huawei', 'P30', 'P40'],
            'Xiaomi': ['xiaomi', 'Xiaomi', 'Mi ', 'Redmi'],
            'OPPO': ['oppo', 'OPPO', 'Reno', 'Find'],
            'OnePlus': ['oneplus', 'OnePlus'],
            'iPad': ['ipad', 'iPad'],
            'Surface': ['surface', 'Surface']
        }
        
        # ブランドに対応するパターンを取得
        patterns = brand_patterns.get(brand, [brand.lower(), brand])
        
        # パターンに基づいてデバイスを検索
        query_parts = []
        for pattern in patterns:
            query_parts.append(f"variation_item_choice_2 LIKE '%{pattern}%'")
        
        query = f"""
            SELECT DISTINCT product_attribute_8, COUNT(*) as count
            FROM product_devices
            WHERE {' OR '.join(query_parts)}
            GROUP BY product_attribute_8
            ORDER BY count DESC
            LIMIT 100
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        attributes = [row[0] for row in results]
        
        # もし該当するブランドの属性が見つからない場合、汎用的な属性を返す
        if not attributes:
            cursor.execute("""
                SELECT DISTINCT product_attribute_8, COUNT(*) as count
                FROM product_devices
                GROUP BY product_attribute_8
                ORDER BY count DESC
                LIMIT 50
            """)
            results = cursor.fetchall()
            attributes = [row[0] for row in results]
        
        conn.close()
        
        return {
            "brand": brand,
            "attributes": attributes,
            "count": len(attributes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total devices
        cursor.execute("SELECT COUNT(*) FROM product_devices")
        total_devices = cursor.fetchone()[0]
        
        # Total sizes
        cursor.execute("SELECT COUNT(DISTINCT size_category) FROM product_devices")
        total_sizes = cursor.fetchone()[0]
        
        # Devices by size
        cursor.execute("""
            SELECT size_category, COUNT(*) as count
            FROM product_devices
            GROUP BY size_category
            ORDER BY count DESC
        """)
        devices_by_size = [{"size": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Devices by brand (inferred from device names)
        brands = {
            'iPhone': ['iphone', 'iPhone'],
            'Xperia': ['xperia', 'SO-', 'Xperia'],
            'AQUOS': ['aquos', 'SH-', 'AQUOS', 'wish', 'sense'],
            'Galaxy': ['galaxy', 'SC-', 'Galaxy'],
            'Pixel': ['pixel', 'Pixel'],
            'HUAWEI': ['huawei', 'mate', 'HUAWEI'],
            'arrows': ['arrows', 'M0'],
        }
        
        brand_counts = {}
        for brand, patterns in brands.items():
            query = " OR ".join([f"variation_item_choice_2 LIKE '%{p}%'" for p in patterns])
            cursor.execute(f"SELECT COUNT(*) FROM product_devices WHERE {query}")
            brand_counts[brand] = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_devices": total_devices,
            "total_sizes": total_sizes,
            "devices_by_size": devices_by_size,
            "devices_by_brand": brand_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices")
async def get_devices(
    brand: Optional[str] = None,
    size: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(25, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get devices with filtering options"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_clauses = []
        params = []
        
        if brand:
            brand_patterns = {
                'iphone': ['%iphone%', '%iPhone%'],
                'xperia': ['%xperia%', '%SO-%', '%Xperia%'],
                'aquos': ['%aquos%', '%SH-%', '%AQUOS%', '%wish%', '%sense%'],
                'galaxy': ['%galaxy%', '%SC-%', '%Galaxy%'],
                'pixel': ['%pixel%', '%Pixel%'],
                'huawei': ['%huawei%', '%mate%', '%HUAWEI%'],
                'arrows': ['%arrows%', '%M0%'],
            }
            
            if brand.lower() in brand_patterns:
                patterns = brand_patterns[brand.lower()]
                brand_clause = " OR ".join(["(variation_item_choice_2 LIKE ? OR product_attribute_8 LIKE ?)" for _ in patterns])
                where_clauses.append(f"({brand_clause})")
                for p in patterns:
                    params.extend([p, p])
        
        if size:
            where_clauses.append("size_category = ?")
            params.append(size)
        
        if search:
            where_clauses.append("(variation_item_choice_2 LIKE ? OR product_attribute_8 LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM product_devices WHERE {where_sql}", params)
        total = cursor.fetchone()[0]
        
        # Get paginated data - using both product_devices and attribute_mappings
        query = f"""
            SELECT 
                pd.id,
                pd.variation_item_choice_2 as device_name,
                pd.product_attribute_8 as attribute_value,
                pd.size_category,
                COALESCE(am.usage_count, 1) as usage_count,
                pd.created_at
            FROM product_devices pd
            LEFT JOIN attribute_mappings am 
                ON pd.variation_item_choice_2 = am.device_name 
                AND pd.size_category = am.size_category
            WHERE {where_sql}
            ORDER BY pd.id DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        cursor.execute(query, params)
        
        devices = []
        for row in cursor.fetchall():
            devices.append({
                "id": row[0],
                "device_name": row[1],
                "attribute_value": row[2],
                "size_category": row[3],
                "usage_count": row[4],
                "created_at": row[5]
            })
        
        conn.close()
        
        return {
            "devices": devices,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/devices")
async def create_device(device: DeviceCreate):
    """Create a new device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert into product_devices
        cursor.execute("""
            INSERT OR REPLACE INTO product_devices 
            (size_category, variation_item_choice_2, product_attribute_8, brand, sheet_name)
            VALUES (?, ?, ?, ?, 'manual')
        """, (device.size_category, device.variation_item_choice_2, device.product_attribute_8, device.brand))
        
        device_id = cursor.lastrowid
        
        # Also update attribute_mappings
        cursor.execute("""
            INSERT OR REPLACE INTO attribute_mappings
            (device_name, attribute_value, size_category, usage_count)
            VALUES (?, ?, ?, 1)
        """, (device.variation_item_choice_2, device.product_attribute_8, device.size_category))
        
        conn.commit()
        conn.close()
        
        return {"id": device_id, "message": "Device created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Device already exists for this size")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/devices/{device_id}")
async def update_device(device_id: int, device: DeviceUpdate):
    """Update a device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query
        updates = []
        params = []
        
        if device.size_category is not None:
            updates.append("size_category = ?")
            params.append(device.size_category)
        
        if device.variation_item_choice_2 is not None:
            updates.append("variation_item_choice_2 = ?")
            params.append(device.variation_item_choice_2)
        
        if device.product_attribute_8 is not None:
            updates.append("product_attribute_8 = ?")
            params.append(device.product_attribute_8)
        
        if device.brand is not None:
            updates.append("brand = ?")
            params.append(device.brand)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(device_id)
        
        cursor.execute(f"""
            UPDATE product_devices 
            SET {', '.join(updates)}
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
        
        cursor.execute("DELETE FROM product_devices WHERE id = ?", (device_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        
        conn.commit()
        conn.close()
        
        return {"message": "Device deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...)):
    """Import devices from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            content = await file.read()
            
            # Detect encoding
            detected = chardet.detect(content)
            encoding = detected.get('encoding', 'utf-8')
            
            # Handle Shift-JIS encoding
            if 'shift' in encoding.lower() or 'sjis' in encoding.lower():
                encoding = 'shift_jis'
            
            tmp.write(content)
            tmp_path = tmp.name
        
        # Read CSV with detected encoding
        try:
            df = pd.read_csv(tmp_path, encoding=encoding)
        except:
            # Fallback to UTF-8
            df = pd.read_csv(tmp_path, encoding='utf-8-sig')
        
        # Process CSV data
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        # Identify columns
        size_cols = [col for col in df.columns if 'サイズ' in str(col) or 'size' in str(col).lower()]
        var_cols = [col for col in df.columns if 'バリエーション項目選択肢2' in str(col)]
        attr_cols = [col for col in df.columns if '商品属性' in str(col) and '8' in str(col)]
        
        # Process each set of columns
        for i in range(min(len(size_cols), len(var_cols), len(attr_cols))):
            size_col = size_cols[i] if i < len(size_cols) else None
            var_col = var_cols[i] if i < len(var_cols) else None
            attr_col = attr_cols[i] if i < len(attr_cols) else None
            
            if not all([size_col, var_col, attr_col]):
                continue
            
            for idx, row in df.iterrows():
                size_val = row.get(size_col)
                var_val = row.get(var_col)
                attr_val = row.get(attr_col)
                
                if pd.isna(size_val) or pd.isna(var_val) or pd.isna(attr_val):
                    continue
                
                size_str = str(size_val).strip()
                var_str = str(var_val).strip()
                attr_str = str(attr_val).strip()
                
                if not all([size_str, var_str, attr_str]):
                    continue
                
                try:
                    # Insert into product_devices
                    cursor.execute("""
                        INSERT OR REPLACE INTO product_devices 
                        (size_category, variation_item_choice_2, product_attribute_8, sheet_name, row_index)
                        VALUES (?, ?, ?, ?, ?)
                    """, (size_str, var_str, attr_str, f"import_{i}", idx))
                    
                    # Update attribute_mappings
                    cursor.execute("""
                        INSERT OR REPLACE INTO attribute_mappings
                        (device_name, attribute_value, size_category, usage_count)
                        VALUES (?, ?, ?, 1)
                    """, (var_str, attr_str, size_str))
                    
                    imported_count += 1
                except sqlite3.IntegrityError:
                    skipped_count += 1
                except Exception as e:
                    errors.append(f"Row {idx}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": errors[:10] if errors else [],
            "message": f"インポート完了: {imported_count}件追加, {skipped_count}件スキップ"
        }
    
    except Exception as e:
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-csv")
async def export_csv():
    """Export parent devices only to CSV (exclude child/sub devices)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # まず、親デバイスを特定する
        # 親デバイス = 各サイズカテゴリで最初に登録されたデバイス、またはキッズ/シニア向けでない通常のデバイス
        
        # キッズ・シニア向けデバイスのパターン
        kids_senior_patterns = [
            'キッズケータイ', 'mamorino', 'あんしんファミリースマホ', 'あんしんスマホ',
            'らくらくフォン', 'らくらくホン', 'BASIO', 'シンプルスマホ', 'かんたんスマホ',
            'ジュニアスマホ', 'キッズ向け', 'シニア向け'
        ]
        
        # WHERE句を構築 - キッズ・シニア向けデバイスを除外
        where_conditions = []
        for pattern in kids_senior_patterns:
            where_conditions.append(f"variation_item_choice_2 NOT LIKE '%{pattern}%'")
            where_conditions.append(f"product_attribute_8 NOT LIKE '%{pattern}%'")
        
        where_clause = " AND ".join(where_conditions)
        
        # 親デバイスのみを取得
        # グループごとの最初のデバイスを親と見なす
        query = f"""
            WITH ranked_devices AS (
                SELECT 
                    size_category,
                    variation_item_choice_2,
                    product_attribute_8,
                    ROW_NUMBER() OVER (
                        PARTITION BY size_category, 
                        SUBSTR(variation_item_choice_2, 1, 
                            CASE 
                                WHEN INSTR(variation_item_choice_2, ' ') > 0 
                                THEN INSTR(variation_item_choice_2, ' ') - 1
                                ELSE LENGTH(variation_item_choice_2)
                            END
                        )
                        ORDER BY id
                    ) as rn
                FROM product_devices
                WHERE {where_clause}
            )
            SELECT 
                size_category as 'サイズ',
                variation_item_choice_2 as 'バリエーション項目選択肢2',
                product_attribute_8 as '商品属性（値）8'
            FROM ranked_devices
            WHERE rn = 1
            ORDER BY 
                CASE size_category
                    WHEN '[SS]' THEN 0
                    WHEN '[S]' THEN 1
                    WHEN '[M]' THEN 2
                    WHEN '[L]' THEN 3
                    WHEN '[LL]' THEN 4
                    WHEN '[2L]' THEN 5
                    WHEN '[3L]' THEN 6
                    WHEN '[4L]' THEN 7
                    WHEN '[i6]' THEN 8
                    ELSE 99
                END,
                variation_item_choice_2
        """
        
        df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        # CSVファイルを作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"product_attributes_parent_only_{timestamp}.csv"
        tmp_path = f"/tmp/{filename}"
        
        # Shift-JISエンコーディングで保存
        df.to_csv(tmp_path, index=False, encoding='shift_jis')
        
        print(f"Exported {len(df)} parent devices to CSV")
        
        return FileResponse(
            tmp_path,
            media_type='text/csv',
            filename=filename,
            headers={
                "Content-Type": "text/csv; charset=shift_jis"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/template-csv")
async def download_template():
    """Download CSV template for import"""
    try:
        # Create template data
        template_data = {
            'サイズ': ['[L]', '[LL]', '[2L]', '[3L]', '[M]', '[S]'],
            'バリエーション項目選択肢2': [
                'iPhone16 ProMax',
                'iPhone16 Plus', 
                'Xperia 10 VI',
                'AQUOS sense9',
                'Galaxy S25 Ultra',
                'Pixel 10 Pro'
            ],
            '商品属性（値）8': [
                'iPhone 16 Pro Max',
                'iPhone 16 Plus',
                'Xperia 10 VI',
                'AQUOS sense9',
                'Galaxy S25 Ultra',
                'Google Pixel 10 Pro'
            ]
        }
        
        df = pd.DataFrame(template_data)
        
        # Save to temporary file with Shift-JIS encoding
        filename = "product_attributes_template.csv"
        tmp_path = f"/tmp/{filename}"
        
        df.to_csv(tmp_path, index=False, encoding='shift_jis')
        
        return FileResponse(
            tmp_path,
            media_type='text/csv',
            filename=filename,
            headers={
                "Content-Type": "text/csv; charset=shift_jis",
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sizes")
async def get_sizes():
    """Get all size categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT size_category, COUNT(*) as count
            FROM product_devices
            GROUP BY size_category
            ORDER BY 
                CASE size_category
                    WHEN '[SS]' THEN 0
                    WHEN '[S]' THEN 1
                    WHEN '[M]' THEN 2
                    WHEN '[L]' THEN 3
                    WHEN '[LL]' THEN 4
                    WHEN '[2L]' THEN 5
                    WHEN '[3L]' THEN 6
                    WHEN '[4L]' THEN 7
                    WHEN '[i6]' THEN 8
                    ELSE 99
                END
        """)
        
        sizes = [{"size": row[0], "count": row[1]} for row in cursor.fetchall()]
        conn.close()
        
        return {"sizes": sizes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear-all")
async def clear_all_data():
    """Clear all data from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM product_devices")
        cursor.execute("DELETE FROM attribute_mappings")
        cursor.execute("DELETE FROM size_categories")
        
        conn.commit()
        conn.close()
        
        return {"message": "All data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))