#!/usr/bin/env python3
import pandas as pd
import tempfile
import os
import sys
sys.path.append('/app')
from services.rakuten_processor import RakutenCSVProcessor

def create_realistic_test_csv():
    """楽天の実際の形式に近いCSVを作成（親行とオプション行が別々）"""
    data = {
        '商品管理番号（商品URL）': [
            'test-001',  # 親行（商品情報あり）
            'test-001',  # オプション行（選択肢タイプあり）
            'test-001',  # SKU行
            'test-001',  # SKU行
            'test-002',  # 親行（商品情報あり）
            'test-002',  # オプション行（選択肢タイプあり）
            'test-002',  # SKU行
            'test-002',  # SKU行
        ],
        '商品番号': ['P001', '', '', '', 'P002', '', '', ''],
        '商品名': ['商品名1', '', '', '', '商品名2', '', '', ''],
        'PC用キャッチコピー': ['キャッチコピー1', '', '', '', 'キャッチコピー2', '', '', ''],
        '選択肢タイプ': ['', 's', '', '', '', 'i', '', ''],  # 2行目と6行目がオプション行
        '商品オプション項目名': ['', 'オプション名1', '', '', '', 'オプション名2', '', ''],
        '商品オプション選択肢1': ['', '選択肢1-1', '', '', '', '選択肢2-1', '', ''],
        '商品オプション選択肢2': ['', '選択肢1-2', '', '', '', '選択肢2-2', '', ''],
        'バリエーション1選択肢定義': ['色A|色B', '', '', '', '色C|色D', '', '', ''],
        'バリエーション2選択肢定義': ['デバイスA|デバイスB', '', '', '', 'デバイスC|デバイスD', '', '', ''],
        'SKU管理番号': ['', '', 'sku-001', 'sku-002', '', '', 'sku-003', 'sku-004']
    }
    
    df = pd.DataFrame(data)
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    df.to_csv(temp_file.name, index=False)
    return temp_file.name, df

def test_realistic_format():
    print("=" * 70)
    print("Testing Realistic Rakuten CSV Format")
    print("=" * 70)
    
    # Create test CSV
    test_file, original_df = create_realistic_test_csv()
    print("\n1. Original CSV (楽天の実際の形式):")
    print("-" * 50)
    print(original_df.to_string())
    
    # Count different row types
    parent_rows = original_df[
        (original_df['SKU管理番号'].isna() | (original_df['SKU管理番号'] == '')) & 
        (original_df['商品名'].notna() & (original_df['商品名'] != ''))
    ]
    option_rows = original_df[
        (original_df['選択肢タイプ'].notna() & (original_df['選択肢タイプ'] != ''))
    ]
    sku_rows = original_df[
        (original_df['SKU管理番号'].notna() & (original_df['SKU管理番号'] != ''))
    ]
    
    print(f"\n   Row types in original:")
    print(f"   - Parent rows (商品名あり): {len(parent_rows)}")
    print(f"   - Option rows (選択肢タイプあり): {len(option_rows)}")
    print(f"   - SKU rows (SKU番号あり): {len(sku_rows)}")
    
    # Process with RakutenProcessor
    print("\n2. Processing with RakutenCSVProcessor...")
    print("-" * 50)
    
    processor = RakutenCSVProcessor()
    # Read the test file into DataFrame
    test_df = pd.read_csv(test_file, encoding='utf-8')
    result_df = processor.process_csv(
        test_df,
        devices_to_add=['新デバイスX', '新デバイスY'],
        custom_device_order=None,
        add_position='end',
        after_device=None
    )
    
    print("\n3. Processed CSV:")
    print("-" * 50)
    # Show first 10 rows only to avoid clutter
    print(result_df.head(10).to_string())
    print(f"... (Total rows: {len(result_df)})")
    
    # Check different row types in result
    result_parent_rows = result_df[
        (result_df['SKU管理番号'].isna() | (result_df['SKU管理番号'] == '')) & 
        (result_df['商品名'].notna() & (result_df['商品名'] != ''))
    ]
    result_option_rows = result_df[
        (result_df['選択肢タイプ'].notna() & (result_df['選択肢タイプ'] != ''))
    ]
    result_sku_rows = result_df[
        (result_df['SKU管理番号'].notna() & (result_df['SKU管理番号'] != ''))
    ]
    
    print(f"\n   Row types in result:")
    print(f"   - Parent rows (商品名あり): {len(result_parent_rows)}")
    print(f"   - Option rows (選択肢タイプあり): {len(result_option_rows)}")
    print(f"   - SKU rows (SKU番号あり): {len(result_sku_rows)}")
    
    # Detailed verification
    print("\n4. Verification:")
    print("-" * 50)
    
    # Check variation definitions
    rows_with_var2 = result_df[
        result_df['バリエーション2選択肢定義'].notna() & 
        (result_df['バリエーション2選択肢定義'] != '')
    ]
    print(f"   Rows with バリエーション2選択肢定義: {len(rows_with_var2)}")
    
    # Check if option rows are preserved with their data
    if len(result_option_rows) == len(option_rows):
        print("   ✅ Option rows preserved!")
        # Check if option data is intact
        for idx in result_option_rows.index[:2]:  # Check first 2 option rows
            opt_type = result_df.loc[idx, '選択肢タイプ']
            opt_name = result_df.loc[idx, '商品オプション項目名']
            print(f"      - Row {idx}: Type={opt_type}, Name={opt_name}")
    else:
        print(f"   ❌ Option rows changed! Original: {len(option_rows)}, Result: {len(result_option_rows)}")
    
    # Check if parent rows didn't increase
    if len(result_parent_rows) == len(parent_rows):
        print("   ✅ Parent rows count maintained!")
    else:
        print(f"   ❌ Parent rows changed! Original: {len(parent_rows)}, Result: {len(result_parent_rows)}")
    
    # Check if variation definitions are ONLY in parent rows
    non_parent_with_var = result_df[
        ~((result_df['SKU管理番号'].isna() | (result_df['SKU管理番号'] == '')) & 
          (result_df['商品名'].notna() & (result_df['商品名'] != ''))) &
        (result_df['バリエーション2選択肢定義'].notna() & (result_df['バリエーション2選択肢定義'] != ''))
    ]
    if len(non_parent_with_var) == 0:
        print("   ✅ Variation definitions ONLY in parent rows!")
    else:
        print(f"   ❌ Variation definitions found in {len(non_parent_with_var)} non-parent rows!")
        print("      Details of problematic rows:")
        for idx in non_parent_with_var.index[:3]:  # Show first 3 problematic rows
            sku = result_df.loc[idx, 'SKU管理番号']
            var2 = result_df.loc[idx, 'バリエーション2選択肢定義']
            print(f"      - Row {idx}: SKU={sku}, Var2={var2[:30]}...")
    
    # Clean up
    os.unlink(test_file)
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_realistic_format()