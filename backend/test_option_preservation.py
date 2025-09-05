#!/usr/bin/env python3
import pandas as pd
import tempfile
import os
import sys
sys.path.append('/app')
from services.rakuten_processor import RakutenCSVProcessor

def create_test_csv():
    """Create test CSV with option data"""
    data = {
        '商品管理番号（商品URL）': ['test-001', 'test-001', 'test-001', 'test-001', 
                                    'test-002', 'test-002', 'test-002'],
        '商品番号': ['P001', '', '', '', 'P002', '', ''],
        '商品名': ['商品名1', '', '', '', '商品名2', '', ''],
        'PC用キャッチコピー': ['キャッチコピー1', '', '', '', 'キャッチコピー2', '', ''],
        '選択肢タイプ': ['s', '', '', '', 'i', '', ''],  # Option type data
        '商品オプション項目名': ['オプション名1', '', '', '', 'オプション名2', '', ''],  # Option name data  
        '商品オプション選択肢1': ['選択肢1-1', '', '', '', '選択肢2-1', '', ''],
        '商品オプション選択肢2': ['選択肢1-2', '', '', '', '選択肢2-2', '', ''],
        'バリエーション1選択肢定義': ['色A|色B', '', '', '', '色C|色D', '', ''],
        'バリエーション2選択肢定義': ['デバイスA|デバイスB', '', '', '', 'デバイスC|デバイスD', '', ''],
        'SKU管理番号': ['', 'sku-001', 'sku-002', 'sku-003', '', 'sku-004', 'sku-005']
    }
    
    df = pd.DataFrame(data)
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    df.to_csv(temp_file.name, index=False)
    return temp_file.name, df

def test_option_preservation():
    print("=" * 60)
    print("Testing Option Data Preservation")
    print("=" * 60)
    
    # Create test CSV
    test_file, original_df = create_test_csv()
    print("\n1. Original CSV:")
    print("-" * 40)
    print(original_df.to_string())
    
    # Count rows with option data
    option_rows = original_df[
        (original_df['選択肢タイプ'].notna() & (original_df['選択肢タイプ'] != '')) |
        (original_df['商品オプション項目名'].notna() & (original_df['商品オプション項目名'] != ''))
    ]
    print(f"\n   Option rows in original: {len(option_rows)}")
    if len(option_rows) > 0:
        print("   Option data found:")
        print(option_rows[['商品管理番号（商品URL）', '選択肢タイプ', '商品オプション項目名']].to_string())
    
    # Process with RakutenProcessor
    print("\n2. Processing with RakutenProcessor...")
    print("-" * 40)
    
    processor = RakutenCSVProcessor()
    # Read the test file into DataFrame
    test_df = pd.read_csv(test_file, encoding='utf-8')
    result_df = processor.process_csv(
        test_df,
        devices_to_add=['新デバイスA'],
        custom_device_order=None,
        add_position='end',
        after_device=None
    )
    print("\n3. Processed CSV:")
    print("-" * 40)
    print(result_df.to_string())
    
    # Check option data preservation
    result_option_rows = result_df[
        (result_df['選択肢タイプ'].notna() & (result_df['選択肢タイプ'] != '')) |
        (result_df['商品オプション項目名'].notna() & (result_df['商品オプション項目名'] != ''))
    ]
    print(f"\n   Option rows in result: {len(result_option_rows)}")
    if len(result_option_rows) > 0:
        print("   Option data preserved:")
        print(result_option_rows[['商品管理番号（商品URL）', '選択肢タイプ', '商品オプション項目名']].to_string())
    
    # Verify results
    print("\n4. Verification:")
    print("-" * 40)
    
    # Check parent rows (should have variation definitions only in parent)
    parent_rows = result_df[
        (result_df['SKU管理番号'].isna() | (result_df['SKU管理番号'] == '')) & 
        (result_df['商品名'].notna() & (result_df['商品名'] != ''))
    ]
    print(f"   Parent rows: {len(parent_rows)}")
    
    # Check variation definitions
    rows_with_var2 = result_df[
        result_df['バリエーション2選択肢定義'].notna() & 
        (result_df['バリエーション2選択肢定義'] != '')
    ]
    print(f"   Rows with variation2 definitions: {len(rows_with_var2)}")
    
    # Check if option data is preserved
    if len(result_option_rows) == len(option_rows):
        print("   ✅ Option data preserved correctly!")
    else:
        print(f"   ❌ Option data lost! Original: {len(option_rows)}, Result: {len(result_option_rows)}")
    
    # Check if variation definitions are only in parent rows
    non_parent_with_var = result_df[
        (result_df['SKU管理番号'].notna() & (result_df['SKU管理番号'] != '')) &
        (result_df['バリエーション2選択肢定義'].notna() & (result_df['バリエーション2選択肢定義'] != ''))
    ]
    if len(non_parent_with_var) == 0:
        print("   ✅ Variation definitions only in parent rows!")
    else:
        print(f"   ❌ Variation definitions found in {len(non_parent_with_var)} non-parent rows!")
    
    # Clean up
    os.unlink(test_file)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_option_preservation()