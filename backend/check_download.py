#!/usr/bin/env python3
"""Check downloaded CSV file from API"""

import requests
import pandas as pd
import json
import os

# 最新の処理済みファイルIDを取得
response = requests.get('http://localhost:8000/api/files')
if response.status_code == 200:
    files = response.json()
    if files:
        latest_file = files[0]
        file_id = latest_file['file_id']
        print(f"Latest file: {file_id}")
        
        # ファイルをダウンロード
        download_url = f'http://localhost:8000/api/download/{file_id}'
        download_response = requests.get(download_url)
        
        if download_response.status_code == 200:
            # ファイルを保存
            output_path = f'downloaded_{file_id}.csv'
            with open(output_path, 'wb') as f:
                f.write(download_response.content)
            
            print(f"Downloaded to: {output_path}")
            
            # CSVファイルを読み込んで確認
            df = pd.read_csv(output_path, encoding='shift-jis', low_memory=False)
            
            print(f"\n=== ファイル分析 ===")
            print(f"Total rows: {len(df)}")
            
            # 親行とSKU行を識別
            if 'SKU管理番号' in df.columns:
                sku_mask = df['SKU管理番号'].notna() & (df['SKU管理番号'] != '')
                parent_rows = df[~sku_mask]
                sku_rows = df[sku_mask]
                
                print(f"Parent rows: {len(parent_rows)}")
                print(f"SKU rows: {len(sku_rows)}")
                
                # バリエーション2選択肢定義を確認
                if 'バリエーション2選択肢定義' in df.columns:
                    # SKU行で値がある行を確認
                    non_empty_sku = sku_rows[
                        sku_rows['バリエーション2選択肢定義'].notna() & 
                        (sku_rows['バリエーション2選択肢定義'] != '')
                    ]
                    
                    print(f"\nSKU行でバリエーション2選択肢定義が空でない行数: {len(non_empty_sku)}")
                    
                    if len(non_empty_sku) > 0:
                        print("\n❌ 問題: SKU行にバリエーション2選択肢定義が残っています")
                        print("\n最初の5行:")
                        for idx, row in non_empty_sku.head(5).iterrows():
                            sku = row['SKU管理番号']
                            value = row['バリエーション2選択肢定義']
                            print(f"  Row {idx+1}: SKU={sku}, Value={value[:50] if len(value) > 50 else value}")
                    else:
                        print("✅ OK: すべてのSKU行でバリエーション2選択肢定義が空です")
                    
                    # 親行の確認
                    non_empty_parent = parent_rows[
                        parent_rows['バリエーション2選択肢定義'].notna() & 
                        (parent_rows['バリエーション2選択肢定義'] != '')
                    ]
                    print(f"\n親行でバリエーション2選択肢定義がある行数: {len(non_empty_parent)}")
        else:
            print(f"Download failed: {download_response.status_code}")
    else:
        print("No files found")
else:
    print(f"Failed to get file list: {response.status_code}")