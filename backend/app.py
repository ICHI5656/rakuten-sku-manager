from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

from services.csv_processor import CSVProcessor
from services.sku_manager import SKUManager
from services.device_manager import DeviceManager
from services.validator import Validator
from services.rakuten_processor import RakutenCSVProcessor
from models.schemas import ProcessRequest, DeviceAction, ProcessingOptions

app = FastAPI(title="Rakuten SKU Manager API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/")
async def root():
    return {"message": "Rakuten SKU Manager API", "version": "1.0.0"}

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file for processing"""
    print(f"Uploading file: {file.filename}")
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
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
        
        # Get products with their devices
        product_devices = {}
        if product_col in df.columns and sku_col in df.columns and device_col in df.columns:
            # Group by product
            current_product = None
            for _, row in df.iterrows():
                if pd.notna(row[product_col]) and pd.isna(row[sku_col]):
                    # Parent row - new product
                    current_product = row[product_col]
                    if current_product not in product_devices:
                        product_devices[current_product] = set()
                elif pd.notna(row[sku_col]) and current_product:
                    # SKU row
                    if pd.notna(row[device_col]):
                        product_devices[current_product].add(row[device_col])
        
        # Convert sets to lists for JSON
        product_devices = {k: sorted(list(v)) for k, v in product_devices.items()}
        
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
    file_path = UPLOAD_DIR / request.file_id
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    print(f"Processing file: {file_path}")
    print(f"Devices to add: {request.devices_to_add}")
    print(f"Devices to remove: {request.devices_to_remove}")
    
    try:
        
        # Read CSV
        df = csv_processor.read_csv(file_path)
        
        # Use new Rakuten processor for proper parent-child structure
        df = rakuten_processor.process_csv(
            df, 
            devices_to_add=request.devices_to_add,
            devices_to_remove=request.devices_to_remove
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
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
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
    
    return {
        "uploads": upload_count,
        "outputs": output_count,
        "products_tracked": len(sku_state),
        "total_skus_generated": sum(sku_state.values())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)