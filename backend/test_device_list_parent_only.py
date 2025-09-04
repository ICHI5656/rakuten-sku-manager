#!/usr/bin/env python3
"""
Test script to verify that device list (バリエーション2選択肢定義) 
is only present in parent rows, not in SKU rows
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.rakuten_processor import RakutenCSVProcessor

def create_test_data():
    """Create test CSV data with multiple products and SKUs"""
    data = {
        '商品管理番号（商品URL）': ['PROD001', '', '', 'PROD001', 'PROD001', 
                              'PROD002', '', 'PROD002', 'PROD002'],
        'SKU管理番号': ['', 'sku_a000001', 'sku_a000002', 'sku_a000003', 'sku_a000004',
                      '', 'sku_a000005', 'sku_a000006', 'sku_a000007'],
        'バリエーション項目選択肢1': ['', 'ブラック', 'ホワイト', 'レッド', 'ブルー',
                               '', 'グリーン', 'イエロー', 'パープル'],
        'バリエーション項目選択肢2': ['', 'iPhone14', 'iPhone14', 'iPhone15', 'iPhone15',
                               '', 'iPhone14', 'iPhone15', 'iPhone16'],
        'バリエーション2選択肢定義': ['iPhone14｜iPhone15', 'iPhone14｜iPhone15', 'iPhone14｜iPhone15', 
                                'iPhone14｜iPhone15', 'iPhone14｜iPhone15',
                                'iPhone14｜iPhone15｜iPhone16', 'iPhone14｜iPhone15｜iPhone16',
                                'iPhone14｜iPhone15｜iPhone16', 'iPhone14｜iPhone15｜iPhone16'],
    }
    
    df = pd.DataFrame(data)
    return df

def test_device_list_parent_only():
    """Test that device list is only in parent rows"""
    print("=" * 60)
    print("Testing: Device list should only be in parent rows")
    print("=" * 60)
    
    # Create test data
    df = create_test_data()
    print("\n1. Original data:")
    print(df[['商品管理番号（商品URL）', 'SKU管理番号', 'バリエーション2選択肢定義']].to_string())
    
    # Initialize processor
    processor = RakutenCSVProcessor(Path('./test_sku_state.json'))
    
    # Process with device addition
    devices_to_add = ['iPhone16 Pro', 'iPhone16 Pro Max']
    print(f"\n2. Adding devices: {devices_to_add}")
    
    result_df = processor.process_csv(
        df,
        devices_to_add=devices_to_add,
        add_position='end'
    )
    
    print("\n3. Processed data:")
    print(result_df[['商品管理番号（商品URL）', 'SKU管理番号', 'バリエーション2選択肢定義']].head(20).to_string())
    
    # Verify that SKU rows have empty device list
    print("\n4. Verification:")
    
    # Check each product
    for product_id in result_df['商品管理番号（商品URL）'].dropna().unique():
        product_rows = result_df[result_df['商品管理番号（商品URL）'] == product_id]
        
        # Parent row (no SKU)
        parent_rows = product_rows[product_rows['SKU管理番号'].isna() | (product_rows['SKU管理番号'] == '')]
        
        # SKU rows
        sku_rows = product_rows[product_rows['SKU管理番号'].notna() & (product_rows['SKU管理番号'] != '')]
        
        print(f"\n  Product: {product_id}")
        
        # Check parent row
        if not parent_rows.empty:
            device_list = parent_rows.iloc[0]['バリエーション2選択肢定義']
            print(f"    Parent row device list: '{device_list}'")
            
            if pd.isna(device_list) or device_list == '':
                print("    ⚠️  WARNING: Parent row has empty device list!")
            else:
                print("    ✅ Parent row has device list")
        
        # Check SKU rows
        if not sku_rows.empty:
            sku_device_lists = sku_rows['バリエーション2選択肢定義'].unique()
            print(f"    SKU rows device lists: {sku_device_lists}")
            
            # All SKU rows should have empty device list
            non_empty_sku_device_lists = [d for d in sku_device_lists if pd.notna(d) and d != '']
            
            if non_empty_sku_device_lists:
                print(f"    ❌ ERROR: SKU rows have non-empty device lists: {non_empty_sku_device_lists}")
            else:
                print(f"    ✅ All {len(sku_rows)} SKU rows have empty device lists")
    
    # Save result for inspection
    output_file = Path('./test_device_list_result.csv')
    result_df.to_csv(output_file, encoding='shift_jis', index=False)
    print(f"\n5. Result saved to: {output_file}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_device_list_parent_only()