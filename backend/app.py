from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Supabase connection
from supabase_client import supabase_connection
from typing import List, Optional, Dict
import pandas as pd
import polars as pl
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import asyncio
import tempfile
import logging

from services.csv_processor import CSVProcessor
from services.sku_manager import SKUManager
from services.device_manager import DeviceManager
from services.validator import Validator
from services.rakuten_processor import RakutenCSVProcessor
from services.batch_processor import BatchProcessor
from database_api import router as database_router
from product_attributes_api_v2 import router as product_attributes_router
from models.schemas import ProcessRequest, DeviceAction, ProcessingOptions

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Rakuten SKU Manager API", version="1.0.0")

# CORS設定を環境変数から取得
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 一時的にすべてのオリジンを許可
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# Include database routers
app.include_router(database_router)
app.include_router(product_attributes_router)

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
        "version": "1.0.0",
        "database_mode": mode
    }

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file for processing"""
    logger.info(f"Uploading file: {file.filename}")
    
    # ファイル形式チェック
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # ファイルサイズチェック（最大100MB）
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File size {file_size / 1024 / 1024:.2f}MB exceeds maximum allowed size of 100MB"
        )
    
    # ファイルを元の位置に戻す
    await file.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"upload_{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    try:
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Detect encoding and read CSV
        df = csv_processor.read_csv(file_path)
        
        # Extract devices and products with device info
        product_col = '商品管理番号（商品URL）'
        sku_col = 'SKU管理番号'
        device_col = 'バリエーション項目選択肢2'
        
        # Get products with their devices from variation definition
        product_devices = {}
        var_def_col = 'バリエーション2選択肢定義'
        
        if product_col in df.columns and sku_col in df.columns and var_def_col in df.columns:
            # 親行から機種リストを取得
            for idx, row in df.iterrows():
                has_product = pd.notna(row.get(product_col))
                sku_value = row.get(sku_col)
                is_sku_empty = pd.isna(sku_value) or sku_value == ''
                
                if has_product and is_sku_empty:
                    # Parent row
                    product_id = row[product_col]
                    var_def_value = row.get(var_def_col, None)
                    
                    if pd.notna(var_def_value) and var_def_value and str(var_def_value).strip():
                        # パイプ区切りの機種リストを解析
                        device_list = [d.strip() for d in str(var_def_value).split('|') if d.strip()]
                        if device_list:
                            product_devices[product_id] = device_list
        
        # フォールバック: SKU行から取得
        if not product_devices and device_col in df.columns:
            current_product = None
            for _, row in df.iterrows():
                if pd.notna(row[product_col]) and pd.isna(row[sku_col]):
                    current_product = row[product_col]
                    if current_product not in product_devices:
                        product_devices[current_product] = []
                elif pd.notna(row.get(sku_col, '')) and current_product:
                    if pd.notna(row.get(device_col, '')):
                        if row[device_col] not in product_devices[current_product]:
                            product_devices[current_product].append(row[device_col])
        
        # Get overall device list
        devices = device_manager.extract_devices(df)
        
        # Get product info
        products = csv_processor.get_product_info(df)
        
        return {
            "file_id": filename,
            "devices": devices,
            "products": products,
            "product_devices": product_devices,  # 商品ごとの機種リスト
            "row_count": len(df),
            "column_count": len(df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process")
async def process_csv(request: ProcessRequest):
    """Process CSV with device changes"""
    print(f"[DEBUG] === PROCESS REQUEST RECEIVED ===")
    print(f"[DEBUG] Request.devices_to_add: {request.devices_to_add} (type: {type(request.devices_to_add)})")
    print(f"[DEBUG] Request.device_brand: '{request.device_brand}' (type: {type(request.device_brand)})")
    print(f"[DEBUG] Request.device_attributes: {request.device_attributes}")
    
    file_path = UPLOAD_DIR / request.file_id
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    print(f"Processing file: {file_path}")
    print(f"Devices to add: {request.devices_to_add}")
    print(f"Devices to remove: {request.devices_to_remove}")
    if request.device_brand:
        print(f"Device brand: {request.device_brand}")
    
    try:
        # Product Attributes 8データベースから各デバイスの属性値を取得
        device_db_attributes = {}
        # 新規追加デバイスと既存デバイスの両方を対象にする
        all_devices_to_check = request.devices_to_add if request.devices_to_add else []
        
        # CSVファイルから既存デバイスを取得して追加
        try:
            df = csv_processor.read_csv(file_path)
            existing_devices = device_manager.extract_devices(df)
            if existing_devices:
                all_devices_to_check.extend(existing_devices)
                # 重複を削除
                all_devices_to_check = list(set(all_devices_to_check))
        except Exception as e:
            print(f"Error reading existing devices: {e}")
        
        if all_devices_to_check:
            try:
                import sqlite3
                
                # デバイス属性を取得（Supabase優先、SQLiteフォールバック）
                if supabase_connection.is_enabled():
                    # Supabase mode
                    for device_name in all_devices_to_check:
                        device_name_str = str(device_name)
                        devices_data = supabase_connection.get_devices()
                        
                        if devices_data:
                            for device in devices_data:
                                if device['device_name'] == device_name_str:
                                    device_db_attributes[device_name_str] = {
                                        'attribute_value': device['attribute_value'],
                                        'size_category': device.get('size_category', ''),
                                        'brand': device.get('brand', '')
                                    }
                                    print(f"[DB] Found attributes for {device_name_str}: {device['attribute_value']}")
                                    break
                else:
                    # SQLite fallback
                    db_path = '/app/product_attributes_new.db'
                    
                    if os.path.exists(db_path):
                        conn = sqlite3.connect(db_path)
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()
                    
                    # すべてのデバイスの属性値を取得（新規追加＋既存）
                    for device_name in all_devices_to_check:
                        # デバイス名を文字列に変換（数値も処理）
                        device_name_str = str(device_name)
                        # デバイス名で検索
                        cursor.execute("""
                            SELECT device_name, attribute_value, size_category, brand
                            FROM device_attributes 
                            WHERE device_name = ?
                            ORDER BY usage_count DESC, updated_at DESC
                            LIMIT 1
                        """, (device_name_str,))
                        
                        device_row = cursor.fetchone()
                        
                        if device_row:
                            # キーも文字列に統一
                            device_db_attributes[device_name_str] = {
                                'attribute_value': device_row['attribute_value'],
                                'size_category': device_row['size_category'],
                                'brand': device_row['brand']
                            }
                            print(f"[DB] Found attributes for {device_name_str}: {device_row['attribute_value']}")
                        else:
                            # 部分一致で再検索
                            cursor.execute("""
                                SELECT device_name, attribute_value, size_category, brand
                                FROM device_attributes 
                                WHERE device_name LIKE ?
                                ORDER BY usage_count DESC, updated_at DESC
                                LIMIT 1
                            """, (f"%{device_name_str}%",))
                            
                            device_row = cursor.fetchone()
                            if device_row:
                                device_db_attributes[device_name_str] = {
                                    'attribute_value': device_row['attribute_value'],
                                    'size_category': device_row['size_category'],
                                    'brand': device_row['brand']
                                }
                                print(f"[DB] Found partial match for {device_name_str}: {device_row['attribute_value']}")
                            else:
                                print(f"[DB] No attributes found for {device_name_str}")
                    
                    conn.close()
                
            except Exception as e:
                print(f"Error fetching device attributes from database: {e}")
        
        # device_attributesをマージ（UIからの入力を優先、DBの値をフォールバック）
        final_device_attributes = []
        if request.device_attributes:
            # UIから送信された属性情報を使用
            for attr in request.device_attributes:
                # DeviceAttributeInfoオブジェクトからプロパティにアクセス
                device_name = attr.device
                final_attr = {
                    'device': device_name,
                    'attribute_value': attr.attribute_value or '',
                    'size_category': attr.size_category or ''
                }
                
                # UIで未設定の場合はDBの値を使用
                if device_name in device_db_attributes:
                    db_attr = device_db_attributes[device_name]
                    if not final_attr['attribute_value']:
                        final_attr['attribute_value'] = db_attr['attribute_value']
                    if not final_attr['size_category']:
                        final_attr['size_category'] = db_attr['size_category']
                
                final_device_attributes.append(final_attr)
        else:
            # UIからの入力がない場合、DBの値を使用
            if request.devices_to_add:
                for device_name in request.devices_to_add:
                    if device_name in device_db_attributes:
                        db_attr = device_db_attributes[device_name]
                        final_device_attributes.append({
                            'device': device_name,
                            'attribute_value': db_attr['attribute_value'],
                            'size_category': db_attr['size_category']
                        })
                    else:
                        # DBにもない場合はデバイス名をそのまま使用
                        final_device_attributes.append({
                            'device': device_name,
                            'attribute_value': device_name,  # フォールバック
                            'size_category': ''
                        })
        
        # 既存デバイスの属性値もfinal_device_attributesに追加（新規追加以外のデバイス）
        added_devices = set([str(attr['device']) for attr in final_device_attributes])
        for device_name, db_attr in device_db_attributes.items():
            if device_name not in added_devices:
                final_device_attributes.append({
                    'device': device_name,  # 文字列として保存
                    'attribute_value': db_attr['attribute_value'],
                    'size_category': db_attr['size_category']
                })
        
        print(f"[DEBUG] Final device attributes: {final_device_attributes}")
        
        # ブランドに基づいて属性値を取得
        brand_attributes = []
        print(f"[DEBUG] Checking brand attributes fetch conditions:")
        print(f"[DEBUG]   request.device_brand: '{request.device_brand}' (type: {type(request.device_brand)})")
        print(f"[DEBUG]   request.devices_to_add: {request.devices_to_add} (type: {type(request.devices_to_add)})")
        print(f"[DEBUG]   bool(request.device_brand): {bool(request.device_brand)}")
        print(f"[DEBUG]   bool(request.devices_to_add): {bool(request.devices_to_add)}")
        print(f"[DEBUG]   condition result: {bool(request.device_brand and request.devices_to_add)}")
        
        if request.device_brand and request.devices_to_add:
            try:
                # ブランド属性を取得（Supabase優先、SQLiteフォールバック）
                if supabase_connection.is_enabled():
                    # Supabase mode
                    brand_names_to_try = [
                        request.device_brand,
                        request.device_brand.lower(),
                        request.device_brand.upper(),
                        request.device_brand.capitalize()
                    ]
                    
                    if 'huawei' in request.device_brand.lower():
                        brand_names_to_try.extend(['huawei', 'HUAWEI', 'Huawei'])
                    
                    for brand_name in brand_names_to_try:
                        values = supabase_connection.get_brand_values(brand_name)
                        if values:
                            brand_attributes = [v['attribute_value'] for v in values if v.get('row_index', 0) > 0]
                            if brand_attributes:
                                print(f"[DEBUG] Found brand attributes from Supabase for '{brand_name}': {len(brand_attributes)} attributes")
                                break
                else:
                    # SQLite fallback
                    brand_db_path = '/app/brand_attributes.db'
                    if os.path.exists(brand_db_path):
                        import sqlite3
                        conn_brand = sqlite3.connect(brand_db_path)
                        cursor_brand = conn_brand.cursor()
                    
                    # ブランド名を正規化（大文字小文字の違いを吸収）
                    brand_names_to_try = [
                        request.device_brand,
                        request.device_brand.lower(),
                        request.device_brand.upper(),
                        request.device_brand.capitalize()
                    ]
                    
                    # HUAWEIの特別処理
                    if 'huawei' in request.device_brand.lower():
                        brand_names_to_try.extend(['huawei', 'HUAWEI', 'Huawei'])
                    
                    print(f"[DEBUG] Searching brand_attributes.db for brand: {request.device_brand}")
                    print(f"[DEBUG] Will try these brand names: {brand_names_to_try}")
                    
                    for brand_name in brand_names_to_try:
                        print(f"[DEBUG] Trying brand name: '{brand_name}'")
                        cursor_brand.execute('''
                            SELECT attribute_value 
                            FROM brand_values 
                            WHERE brand_name = ? AND row_index > 0
                            ORDER BY row_index
                        ''', (brand_name,))
                        
                        results = cursor_brand.fetchall()
                        print(f"[DEBUG] Query result for '{brand_name}': {len(results)} rows found")
                        if results:
                            brand_attributes = [row[0] for row in results]
                            print(f"[DEBUG] SUCCESS! Found brand attributes from DB for '{brand_name}': {len(brand_attributes)} attributes")
                            print(f"[DEBUG] First 3 attributes: {brand_attributes[:3]}")
                            break
                        else:
                            print(f"[DEBUG] No results for brand name: '{brand_name}'")
                    
                    conn_brand.close()
                
                # データベースから取得できなかった場合は、ハードコーディングされた属性値を使用（フォールバック）
                if not brand_attributes:
                    # ブランドごとに適切な属性値を設定
                    brand_attribute_mapping = {
                        'Huawei': [
                            'amicoco|ファーウェイ|アップル',
                            'amicoco|ファーウェイ|グーグル',
                            'amicoco|ファーウェイ|ソニー',
                            'amicoco|ファーウェイ|原セラ',
                            'amicoco|ファーウェイ|ASUS',
                            'amicoco|ファーウェイ|シャープ',
                            'amicoco|ファーウェイ|富士通',
                            'amicoco|ファーウェイ|FCNT',
                            'amicoco|ファーウェイ|楽天モバイル',
                            'amicoco|ファーウェイ|サムスン',
                            'amicoco|ファーウェイ|シャオミ',
                            'amicoco|ファーウェイ|オッポ'
                        ],
                        'huawei': [
                            'amicoco|ファーウェイ|アップル',
                            'amicoco|ファーウェイ|グーグル',
                            'amicoco|ファーウェイ|ソニー',
                            'amicoco|ファーウェイ|原セラ',
                            'amicoco|ファーウェイ|ASUS',
                            'amicoco|ファーウェイ|シャープ',
                            'amicoco|ファーウェイ|富士通',
                            'amicoco|ファーウェイ|FCNT',
                            'amicoco|ファーウェイ|楽天モバイル',
                            'amicoco|ファーウェイ|サムスン',
                            'amicoco|ファーウェイ|シャオミ',
                            'amicoco|ファーウェイ|オッポ'
                        ],
                        'iPhone': [
                            'amicoco|アップル|iPhone',
                            'amicoco|アップル|Pro',
                            'amicoco|アップル|Plus',
                            'amicoco|アップル|ProMax',
                            'amicoco|アップル|mini'
                        ],
                        'Galaxy': [
                            'amicoco|サムスン|Galaxy',
                            'amicoco|サムスン|Note',
                            'amicoco|サムスン|Ultra',
                            'amicoco|サムスン|Plus'
                        ],
                        'Xperia': [
                            'amicoco|ソニー|Xperia',
                            'amicoco|ソニー|1',
                            'amicoco|ソニー|5',
                            'amicoco|ソニー|10',
                            'amicoco|ソニー|Ace'
                        ],
                        'AQUOS': [
                            'amicoco|シャープ|AQUOS',
                            'amicoco|シャープ|sense',
                            'amicoco|シャープ|wish',
                            'amicoco|シャープ|R'
                        ],
                        'Pixel': [
                            'amicoco|グーグル|Pixel',
                            'amicoco|グーグル|Pro',
                            'amicoco|グーグル|a'
                        ],
                        'Xiaomi': [
                            'amicoco|シャオミ|Xiaomi',
                            'amicoco|シャオミ|Redmi',
                            'amicoco|シャオミ|Mi',
                            'amicoco|シャオミ|Note'
                        ],
                        'OPPO': [
                            'amicoco|オッポ|OPPO',
                            'amicoco|オッポ|Reno',
                            'amicoco|オッポ|Find',
                            'amicoco|オッポ|A'
                        ],
                        'OnePlus': [
                            'amicoco|ワンプラス|OnePlus',
                            'amicoco|ワンプラス|Pro',
                            'amicoco|ワンプラス|Nord'
                        ],
                        'iPad': [
                            'amicoco|アップル|iPad',
                            'amicoco|アップル|iPadPro',
                            'amicoco|アップル|iPadAir',
                            'amicoco|アップル|iPadmini'
                        ],
                        'Surface': [
                            'amicoco|マイクロソフト|Surface',
                            'amicoco|マイクロソフト|Pro',
                            'amicoco|マイクロソフト|Go',
                            'amicoco|マイクロソフト|Laptop'
                        ]
                    }
                    
                    # ブランドに対応する属性値を取得
                    if request.device_brand in brand_attribute_mapping:
                        brand_attributes = brand_attribute_mapping[request.device_brand]
                    else:
                        # デフォルトの属性値
                        brand_attributes = [
                            'amicoco|その他|スマートフォン',
                            'amicoco|その他|タブレット',
                            'amicoco|その他|デバイス'
                        ]
                    
                    print(f"[DEBUG] Using fallback attributes for brand {request.device_brand}: {len(brand_attributes)} attributes")
                    print(f"[DEBUG] First 3 fallback attributes: {brand_attributes[:3]}")
                    
            except Exception as e:
                print(f"[ERROR] Error fetching brand attributes: {e}")
                # エラーの場合はデフォルト属性値を使用
                brand_attributes = []
        
        # 最終的に使用される brand_attributes をログ出力
        print(f"[DEBUG] Final brand_attributes to be used: {len(brand_attributes)} attributes")
        if brand_attributes:
            print(f"[DEBUG] Final brand_attributes first 3: {brand_attributes[:3]}")
        
        # Read CSV
        df = csv_processor.read_csv(file_path)
        
        # Use new Rakuten processor for proper parent-child structure
        df = rakuten_processor.process_csv(
            df, 
            devices_to_add=request.devices_to_add,
            devices_to_remove=request.devices_to_remove,
            add_position=request.add_position,
            after_device=request.after_device,
            custom_device_order=request.custom_device_order,
            insert_index=request.insert_index,
            brand_attributes=brand_attributes,
            device_attributes=final_device_attributes,
            reset_all_devices=request.reset_all_devices
        )
        
        # Validate constraints
        validation_result = validator.validate_dataframe(df)
        if not validation_result["valid"]:
            return JSONResponse(
                status_code=400,
                content={"error": "Validation failed", "details": validation_result["errors"]}
            )
        
        # Process and save output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = []
        
        if request.output_format == "single":
            output_file = OUTPUT_DIR / f"item_{timestamp}.csv"
            print(f"Saving to: {output_file}")
            csv_processor.save_csv(df, output_file)
            output_files.append(str(output_file.name))
            print(f"Saved file: {output_file.name}")
        
        elif request.output_format == "per_product":
            products = df.groupby('商品管理番号（商品URL）')
            for i, (product_id, product_df) in enumerate(products):
                output_file = OUTPUT_DIR / f"item_{timestamp}_{i+1}.csv"
                csv_processor.save_csv(product_df, output_file)
                output_files.append(str(output_file.name))
        
        elif request.output_format == "split_60k":
            chunk_size = 60000
            for i in range(0, len(df), chunk_size):
                chunk_df = df.iloc[i:i+chunk_size]
                output_file = OUTPUT_DIR / f"item_{timestamp}_{i//chunk_size + 1}.csv"
                csv_processor.save_csv(chunk_df, output_file)
                output_files.append(str(output_file.name))
        
        # Save SKU state
        sku_manager.save_state()
        
        # Count SKUs safely
        sku_count = 0
        if 'SKU管理番号' in df.columns:
            sku_count = len(df[df['SKU管理番号'].notna()])
        
        return {
            "success": True,
            "output_files": output_files,
            "total_rows": len(df),
            "sku_count": sku_count
        }
    
    except Exception as e:
        import traceback
        print(f"Error in process_csv: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download processed CSV file"""
    # まず通常の出力ディレクトリを確認
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            media_type='text/csv',
            filename=filename,
            headers={
                "Content-Type": "text/csv; charset=shift_jis"
            }
        )
    
    # バッチディレクトリも確認（バッチ処理されたファイル用）
    # ファイル名にバッチIDが含まれている場合、該当するバッチディレクトリを検索
    for batch_dir in UPLOAD_DIR.glob("*_batch"):
        batch_file_path = batch_dir / filename
        if batch_file_path.exists():
            return FileResponse(
                path=batch_file_path,
                media_type='text/csv',
                filename=filename,
                headers={
                    "Content-Type": "text/csv; charset=shift_jis"
                }
            )
    
    raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type='text/csv',
        filename=filename,
        headers={
            "Content-Type": "text/csv; charset=shift_jis"
        }
    )

@app.get("/api/devices/{file_id}")
async def get_devices(file_id: str):
    """Get list of devices from uploaded CSV"""
    try:
        file_path = UPLOAD_DIR / file_id
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        df = csv_processor.read_csv(file_path)
        devices = device_manager.extract_devices(df)
        
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cleanup")
async def cleanup_old_files():
    """Clean up old files (older than 24 hours)"""
    import time
    current_time = time.time()
    deleted_files = []
    
    for directory in [UPLOAD_DIR, OUTPUT_DIR]:
        for file_path in directory.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > 86400:  # 24 hours
                    file_path.unlink()
                    deleted_files.append(str(file_path.name))
    
    return {"deleted_files": deleted_files}

@app.post("/api/batch-upload")
async def batch_upload_csv(files: List[UploadFile] = File(...)):
    """Upload multiple CSV files for batch processing"""
    logger.info(f"Batch uploading {len(files)} files")
    
    uploaded_files = []
    errors = []
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S_batch")
    batch_dir = UPLOAD_DIR / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        if not file.filename.endswith('.csv'):
            errors.append({
                'file': file.filename,
                'error': 'Only CSV files are allowed'
            })
            continue
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Remove directory path from filename (for folder uploads)
            clean_filename = Path(file.filename).name
            filename = f"{timestamp}_{clean_filename}"
            file_path = batch_dir / filename
            
            logger.info(f"Saving file to: {file_path}")
            contents = await file.read()
            with open(file_path, 'wb') as f:
                f.write(contents)
            
            # Verify file was saved
            if not file_path.exists():
                logger.error(f"File not saved: {file_path}")
                raise Exception(f"Failed to save file: {filename}")
            
            logger.info(f"File saved successfully: {file_path} (size: {file_path.stat().st_size} bytes)")
            
            # Quick analysis
            df = csv_processor.read_csv(file_path)
            devices = device_manager.extract_devices(df)
            
            # Get product-specific device information (same as single file upload)
            product_col = '商品管理番号（商品URL）'
            sku_col = 'SKU管理番号'
            var_def_col = 'バリエーション2選択肢定義'
            device_col = 'バリエーション項目選択肢2'
            
            product_devices = {}
            
            if product_col in df.columns and sku_col in df.columns and var_def_col in df.columns:
                # 親行から機種リストを取得
                for idx, row in df.iterrows():
                    has_product = pd.notna(row.get(product_col))
                    sku_value = row.get(sku_col)
                    is_sku_empty = pd.isna(sku_value) or sku_value == ''
                    
                    if has_product and is_sku_empty:
                        # Parent row
                        product_id = row[product_col]
                        var_def_value = row.get(var_def_col, None)
                        
                        if pd.notna(var_def_value) and var_def_value and str(var_def_value).strip():
                            # パイプ区切りの機種リストを解析
                            device_list = [d.strip() for d in str(var_def_value).split('|') if d.strip()]
                            if device_list:
                                product_devices[product_id] = device_list
            
            # フォールバック: SKU行から取得
            if not product_devices and device_col in df.columns:
                current_product = None
                for _, row in df.iterrows():
                    if pd.notna(row.get(product_col)) and pd.isna(row.get(sku_col, '')):
                        current_product = row[product_col]
                        if current_product not in product_devices:
                            product_devices[current_product] = []
                    elif pd.notna(row.get(sku_col, '')) and current_product:
                        if pd.notna(row.get(device_col, '')):
                            device_value = row[device_col]
                            if device_value not in product_devices[current_product]:
                                product_devices[current_product].append(device_value)
            
            uploaded_files.append({
                'filename': filename,
                'original_name': file.filename,
                'path': str(file_path),
                'devices': devices,
                'product_devices': product_devices,  # 商品ごとの機種リスト
                'row_count': len(df),
                'column_count': len(df.columns)
            })
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
            errors.append({
                'file': file.filename,
                'error': str(e)
            })
    
    # Collect all unique devices while maintaining order
    # First, collect all product devices from all files
    all_product_devices = {}  # Aggregate product devices from all files
    file_device_lists = []  # Store device lists from each file
    
    for file_info in uploaded_files:
        # Store device list from this file
        if 'devices' in file_info:
            file_device_lists.append(file_info['devices'])
        
        # Merge product devices from each file
        if 'product_devices' in file_info:
            for product_id, devices in file_info['product_devices'].items():
                if product_id not in all_product_devices:
                    all_product_devices[product_id] = devices
                else:
                    # Merge device lists if same product appears in multiple files
                    existing = set(all_product_devices[product_id])
                    for device in devices:
                        if device not in existing:
                            all_product_devices[product_id].append(device)
    
    # Find the most common device list order pattern as reference
    # Count how many products use each device list order pattern
    device_order_patterns = {}
    
    # Collect from products to find common order patterns
    for product_id, devices in all_product_devices.items():
        if devices:
            # Create a hashable key from the device list order
            order_key = tuple(devices)
            if order_key not in device_order_patterns:
                device_order_patterns[order_key] = {
                    'devices': devices,
                    'count': 0,
                    'products': []
                }
            device_order_patterns[order_key]['count'] += 1
            device_order_patterns[order_key]['products'].append(product_id)
            logger.info(f"Product {product_id}: {len(devices)} devices - First 3: {devices[:3] if devices else []}")
    
    # Select the most common device order pattern as reference
    reference_list = []
    if device_order_patterns:
        # Find the order pattern used by most products
        most_common_pattern = max(device_order_patterns.values(), key=lambda x: x['count'])
        reference_list = most_common_pattern['devices']
        logger.info(f"Selected reference order from pattern used by {most_common_pattern['count']} products")
        logger.info(f"Reference list order (first 5): {reference_list[:5] if len(reference_list) >= 5 else reference_list}")
    else:
        # Fallback to first file's device list if no product patterns found
        if file_device_lists and file_device_lists[0]:
            reference_list = file_device_lists[0]
            logger.info(f"Using first file's device order as reference: {reference_list[:5] if len(reference_list) >= 5 else reference_list}")
    
    # Build the final all_devices list based on reference order
    all_devices = []
    seen_devices = set()
    
    # First add devices in reference order
    for device in reference_list:
        if device not in seen_devices:
            all_devices.append(device)
            seen_devices.add(device)
    
    # Then add any remaining devices from all files (preserving their order)
    for file_devices in file_device_lists:
        for device in file_devices:
            if device not in seen_devices:
                all_devices.append(device)
                seen_devices.add(device)
    
    logger.info(f"Collected all devices from batch (order preserved): {all_devices}")
    logger.info(f"Total unique devices: {len(all_devices)}")
    logger.info(f"Product-specific devices: {len(all_product_devices)} products")
    
    result = {
        'batch_id': batch_id,
        'uploaded_files': uploaded_files,
        'errors': errors,
        'total_files': len(uploaded_files),
        'all_devices': all_devices,  # Already a list with order preserved
        'all_product_devices': all_product_devices  # Aggregated product devices
    }
    
    logger.info(f"Batch upload result: batch_id={batch_id}, total_files={len(uploaded_files)}, unique_devices={len(all_devices)}")
    
    return result

@app.post("/api/batch-process")
async def batch_process_csv(
    batch_id: str = Form(...),
    devices_to_add: Optional[str] = Form(None),
    devices_to_remove: Optional[str] = Form(None),
    output_format: str = Form('single'),
    apply_to_all: bool = Form(True),
    add_position: Optional[str] = Form(None),
    after_device: Optional[str] = Form(None),
    custom_device_order: Optional[str] = Form(None),
    process_mode: Optional[str] = Form('auto')  # 'auto', 'same_devices', 'different_devices'
):
    """Process multiple CSV files in batch"""
    logger.info(f"Batch processing: {batch_id}")
    logger.info(f"UPLOAD_DIR: {UPLOAD_DIR}")
    logger.info(f"Looking for batch_dir: {UPLOAD_DIR / batch_id}")
    
    # Parse device lists
    devices_add = json.loads(devices_to_add) if devices_to_add else None
    devices_remove = json.loads(devices_to_remove) if devices_to_remove else None
    custom_order = json.loads(custom_device_order) if custom_device_order else None
    
    # Find batch files
    batch_dir = UPLOAD_DIR / batch_id
    
    # List all directories in UPLOAD_DIR for debugging
    logger.info(f"Contents of UPLOAD_DIR: {list(UPLOAD_DIR.iterdir())}")
    
    if not batch_dir.exists():
        logger.error(f"Batch directory not found: {batch_dir}")
        # Create empty result for missing batch
        return {
            'status': 'error',
            'message': f'Batch not found: {batch_id}',
            'batch_id': batch_id,
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'results': []
        }
    
    csv_files = list(batch_dir.glob("*.csv"))
    if not csv_files:
        logger.warning(f"No CSV files found in batch: {batch_id}")
        # Return empty result instead of error
        return {
            'status': 'completed',
            'message': 'No files to process',
            'batch_id': batch_id,
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'results': []
        }
    
    # Get device attributes from database if devices are being added
    device_attributes = None
    if devices_add:
        try:
            # Get attributes from database for each device
            device_attributes = []
            import httpx
            async with httpx.AsyncClient() as client:
                for device in devices_add:
                    # Query the product attributes database using the existing API endpoint
                    try:
                        resp = await client.get(f"http://localhost:8000/api/product-attributes/device/{device}")
                        if resp.status_code == 200:
                            data = resp.json()
                        else:
                            data = None
                    except:
                        data = None
                    
                    if data and 'attribute_value' in data:
                        device_attributes.append({
                            'device': device,
                            'attribute_value': data['attribute_value'],
                            'size_category': data.get('size_category')
                        })
                    else:
                        # Fallback: use device name as attribute_value
                        device_attributes.append({
                            'device': device,
                            'attribute_value': device,
                            'size_category': None
                        })
        except Exception as e:
            logger.warning(f"Could not fetch device attributes: {e}")
            device_attributes = None
    
    # Process batch
    result = await batch_processor.process_batch_files(
        file_paths=csv_files,
        devices_to_add=devices_add,
        devices_to_remove=devices_remove,
        output_format=output_format,
        apply_to_all=apply_to_all,
        device_attributes=device_attributes,
        add_position=add_position,
        after_device=after_device,
        custom_device_order=custom_order,
        process_mode=process_mode  # Pass process_mode to batch processor
    )
    
    return result

@app.get("/api/batch-download/{batch_id}")
async def download_batch_results(batch_id: str):
    """Download all processed files from a batch as a zip"""
    import zipfile
    import io
    from fastapi.responses import StreamingResponse
    
    logger.info(f"Download request for batch: {batch_id}")
    
    status = batch_processor.get_batch_status(batch_id)
    logger.info(f"Batch status: {status}")
    
    if status['status'] == 'not_found':
        # Try to find files directly in the batch directory as fallback
        batch_dir = UPLOAD_DIR / batch_id
        if batch_dir.exists():
            logger.info(f"Batch directory found: {batch_dir}")
            # Find all processed files in the directory
            processed_files = list(batch_dir.glob("*_processed_*.csv"))
            if processed_files:
                logger.info(f"Found {len(processed_files)} processed files")
                
                # ZIPファイルをバッチディレクトリ内に作成
                zip_file_path = batch_dir / f"batch_{batch_id}_results.zip"
                
                with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in processed_files:
                        zip_file.write(file_path, file_path.name)
                
                logger.info(f"Created ZIP file: {zip_file_path}")
                
                # ZIPファイルを返す
                return FileResponse(
                    path=zip_file_path,
                    media_type='application/zip',
                    filename=f"batch_{batch_id}_results.zip"
                )
        
        raise HTTPException(status_code=404, detail="Batch ID not found")
    
    if status['status'] != 'completed':
        logger.warning(f"Batch not completed: {status['status']}")
        # Continue anyway if we have results
        if 'results' not in status or not status['results']:
            raise HTTPException(status_code=400, detail="Batch processing not completed")
    
    # Collect all output files
    output_files = []
    for result in status.get('results', []):
        if result['status'] == 'success' and 'output_path' in result:
            output_path = Path(result['output_path'])
            if output_path.exists():
                output_files.append(output_path)
    
    if not output_files:
        raise HTTPException(status_code=404, detail="No output files found")
    
    # ZIPファイルをバッチディレクトリに作成
    batch_dir = UPLOAD_DIR / batch_id
    if not batch_dir.exists():
        batch_dir.mkdir(parents=True, exist_ok=True)
    
    zip_file_path = batch_dir / f"batch_{batch_id}_results.zip"
    
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in output_files:
            zip_file.write(file_path, file_path.name)
    
    logger.info(f"Created ZIP file: {zip_file_path}")
    
    return FileResponse(
        path=zip_file_path,
        media_type='application/zip',
        filename=f"batch_{batch_id}_results.zip"
    )

@app.get("/api/batch-status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get batch processing status"""
    status = batch_processor.get_batch_status(batch_id)
    if status['status'] == 'not_found':
        raise HTTPException(status_code=404, detail="Batch ID not found")
    return status

@app.get("/api/status")
async def get_status():
    """Get system status"""
    upload_count = len(list(UPLOAD_DIR.glob("*.csv")))
    output_count = len(list(OUTPUT_DIR.glob("*.csv")))
    
    sku_state = {}
    state_file = STATE_DIR / "sku_counters.json"
    if state_file.exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            sku_state = json.load(f)
    
    # Calculate total SKUs - handle both old format (int) and new format (list)
    total_skus = 0
    for value in sku_state.values():
        if isinstance(value, int):
            total_skus += value
        elif isinstance(value, list):
            total_skus += len(value)
    
    return {
        "uploads": upload_count,
        "outputs": output_count,
        "products_tracked": len(sku_state),
        "total_skus_generated": total_skus
    }

# =====================================
# データベース統合管理API
# =====================================

@app.post("/api/database/brand-values")
async def add_brand_value(request: dict):
    """ブランド属性値を追加"""
    try:
        conn = sqlite3.connect('/app/brand_attributes.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO brand_values (brand_name, row_index, attribute_value)
            VALUES (?, ?, ?)
        ''', (request['brand_name'], request['row_index'], request['attribute_value']))
        
        conn.commit()
        conn.close()
        
        return {"message": "Brand value added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/database/brand-values/{id}")
async def update_brand_value(id: int, request: dict):
    """ブランド属性値を更新"""
    try:
        conn = sqlite3.connect('/app/brand_attributes.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE brand_values 
            SET attribute_value = ?
            WHERE id = ?
        ''', (request['attribute_value'], id))
        
        conn.commit()
        conn.close()
        
        return {"message": "Brand value updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/database/brand-values/{id}")
async def delete_brand_value(id: int):
    """ブランド属性値を削除"""
    try:
        conn = sqlite3.connect('/app/brand_attributes.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM brand_values WHERE id = ?', (id,))
        
        conn.commit()
        conn.close()
        
        return {"message": "Brand value deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/database/export")
async def export_brand_database():
    """ブランドデータベースをExcelファイルとしてエクスポート"""
    try:
        import pandas as pd
        from fastapi.responses import StreamingResponse
        import io
        
        conn = sqlite3.connect('/app/brand_attributes.db')
        
        # すべてのブランドデータを取得
        query = '''
            SELECT brand_name, row_index, attribute_value 
            FROM brand_values 
            ORDER BY brand_name, row_index
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Excelファイルとして出力
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Brand Attributes', index=False)
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename=brand_attributes_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/database/import")
async def import_brand_database(file: UploadFile):
    """Excelファイルからブランドデータベースをインポート"""
    try:
        import pandas as pd
        
        # ファイルを読み込み
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 必要なカラムが存在するか確認
        required_columns = ['brand_name', 'row_index', 'attribute_value']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"Required columns: {required_columns}")
        
        conn = sqlite3.connect('/app/brand_attributes.db')
        cursor = conn.cursor()
        
        # 既存データをクリア（オプション）
        # cursor.execute('DELETE FROM brand_values')
        
        # データを挿入
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO brand_values (brand_name, row_index, attribute_value)
                VALUES (?, ?, ?)
            ''', (row['brand_name'], row['row_index'], row['attribute_value']))
        
        conn.commit()
        conn.close()
        
        return {"message": f"Successfully imported {len(df)} records"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/product-attributes/export")
async def export_device_attributes():
    """デバイス属性データベースをExcelファイルとしてエクスポート"""
    try:
        import pandas as pd
        from fastapi.responses import StreamingResponse
        import io
        
        conn = sqlite3.connect('/app/product_attributes_new.db')
        
        # すべてのデバイスデータを取得
        query = '''
            SELECT brand, device_name, attribute_value, size_category, usage_count 
            FROM device_attributes 
            ORDER BY brand, device_name
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Excelファイルとして出力
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Device Attributes', index=False)
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename=device_attributes_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/product-attributes/import")
async def import_device_attributes(file: UploadFile):
    """Excelファイルからデバイス属性データベースをインポート"""
    try:
        import pandas as pd
        
        # ファイルを読み込み
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 必要なカラムが存在するか確認
        required_columns = ['brand', 'device_name', 'attribute_value']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"Required columns: {required_columns}")
        
        conn = sqlite3.connect('/app/product_attributes_new.db')
        cursor = conn.cursor()
        
        # データを挿入または更新
        for _, row in df.iterrows():
            size_category = row.get('size_category', '')
            usage_count = row.get('usage_count', 0)
            
            cursor.execute('''
                INSERT OR REPLACE INTO device_attributes 
                (brand, device_name, attribute_value, size_category, usage_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['brand'], row['device_name'], row['attribute_value'], size_category, usage_count))
        
        conn.commit()
        conn.close()
        
        return {"message": f"Successfully imported {len(df)} records"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/product-attributes/devices")
async def add_device(request: dict):
    """デバイスを追加"""
    try:
        conn = sqlite3.connect('/app/product_attributes_new.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO device_attributes (brand, device_name, attribute_value, size_category, usage_count)
            VALUES (?, ?, ?, ?, 0)
        ''', (request['brand'], request['device_name'], request['attribute_value'], request.get('size_category', '')))
        
        conn.commit()
        conn.close()
        
        return {"message": "Device added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)