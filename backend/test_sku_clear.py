#!/usr/bin/env python3
"""Test script to verify SKU row clearing functionality"""

import pandas as pd
import sys
import os

# テスト用CSVを作成（親行とSKU行を含む）
test_data = {
    '商品管理番号（商品URL）': ['TEST001', 'TEST001', 'TEST001', 'TEST001', 'TEST002', 'TEST002', 'TEST002'],
    'SKU管理番号': ['', 'sku_test_001', 'sku_test_002', 'sku_test_003', '', 'sku_test_004', 'sku_test_005'],
    'バリエーション項目選択肢1': ['', 'ブラック', 'ホワイト', 'レッド', '', 'ブルー', 'グリーン'],
    'バリエーション項目選択肢2': ['', 'iPhone15', 'iPhone15', 'iPhone16', '', 'iPhone14', 'iPhone14'],
    'バリエーション2選択肢定義': ['iPhone14|iPhone15', 'この行はSKU行なので空になるべき', 'この行もSKU行なので空になるべき', 'この行もSKU行なので空になるべき', 'iPhone14', 'SKU行なので空', 'SKU行なので空']
}

print("=== Test Data Creation ===")
df = pd.DataFrame(test_data)
print(f"Created test data with {len(df)} rows")

# CSVファイルとして保存
test_file = '/app/test_input.csv'
df.to_csv(test_file, index=False, encoding='shift-jis')
print(f"Saved to {test_file}")

print("\n=== Before Processing ===")
print("バリエーション2選択肢定義 column values:")
for idx, row in df.iterrows():
    sku = row.get('SKU管理番号', '')
    var2_def = row.get('バリエーション2選択肢定義', '')
    is_sku = 'SKU行' if sku else '親行'
    print(f"  Row {idx+1} ({is_sku}): SKU=[{sku}], バリエーション2選択肢定義=[{var2_def}]")

# 処理用モジュールをインポート
sys.path.insert(0, '/app')
from services.rakuten_processor import RakutenCSVProcessor
from services.csv_processor import CSVProcessor
from pathlib import Path

print("\n=== Processing ===")
# CSVファイルを読み込み
csv_processor = CSVProcessor()
loaded_df = csv_processor.read_csv(test_file)

# 楽天処理を実行
sku_state_file = Path('/app/data/state/sku_counters.json')
processor = RakutenCSVProcessor(sku_state_file=sku_state_file)
processed_df = processor.process_csv(
    loaded_df,
    devices_to_add=['iPhone16 Pro'],
    add_position='end'
)

# 結果を保存
output_file = '/app/test_output.csv'
csv_processor.save_csv(processed_df, output_file)
print(f"Saved processed result to {output_file}")

# 結果を確認
print("\n=== After Processing ===")
print("バリエーション2選択肢定義 column values:")
for idx, row in processed_df.iterrows():
    sku = row.get('SKU管理番号', '')
    var2_def = row.get('バリエーション2選択肢定義', '')
    is_sku = 'SKU行' if sku else '親行'
    print(f"  Row {idx+1} ({is_sku}): SKU=[{sku}], バリエーション2選択肢定義=[{var2_def}]")

# 検証
print("\n=== Validation ===")
sku_rows = processed_df[processed_df['SKU管理番号'].notna() & (processed_df['SKU管理番号'] != '')]
parent_rows = processed_df[~(processed_df['SKU管理番号'].notna() & (processed_df['SKU管理番号'] != ''))]

print(f"Total parent rows: {len(parent_rows)}")
print(f"Total SKU rows: {len(sku_rows)}")

# SKU行のバリエーション2選択肢定義が空であることを確認
if 'バリエーション2選択肢定義' in sku_rows.columns:
    non_empty_sku_rows = sku_rows[sku_rows['バリエーション2選択肢定義'].notna() & (sku_rows['バリエーション2選択肢定義'] != '')]
    if len(non_empty_sku_rows) > 0:
        print(f"❌ ERROR: {len(non_empty_sku_rows)} SKU rows still have non-empty バリエーション2選択肢定義")
        for idx, row in non_empty_sku_rows.iterrows():
            print(f"  - Row {idx+1}: SKU={row['SKU管理番号']}, Value={row['バリエーション2選択肢定義']}")
    else:
        print("✅ SUCCESS: All SKU rows have empty バリエーション2選択肢定義")

# 親行のバリエーション2選択肢定義が正しく更新されていることを確認
if 'バリエーション2選択肢定義' in parent_rows.columns:
    for idx, row in parent_rows.iterrows():
        var2_def = row.get('バリエーション2選択肢定義', '')
        if var2_def:
            devices = var2_def.split('|')
            print(f"Parent row devices: {devices}")