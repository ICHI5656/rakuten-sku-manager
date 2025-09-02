#!/usr/bin/env python3
"""全機種削除・再定義および並び替え機能のテスト"""

import pandas as pd
from pathlib import Path
from services.rakuten_processor import RakutenCSVProcessor

def test_reset_and_reorder():
    # テストデータ作成
    data = {
        '商品管理番号（商品URL）': ['product_X', 'product_X', 'product_X', 'product_X'],
        'SKU管理番号': ['', 'sku_x000001', 'sku_x000002', 'sku_x000003'],
        'バリエーション2選択肢定義': ['iPhone13|Galaxy S22|Xperia 1IV', '', '', ''],
        'バリエーション項目選択肢2': ['', 'iPhone13', 'Galaxy S22', 'Xperia 1IV'],
        '在庫タイプ': ['通常在庫'] * 4,
        '商品名': ['Product X'] * 4
    }
    
    df = pd.DataFrame(data)
    processor = RakutenCSVProcessor(Path('/app/data/state/sku_counters.json'))
    
    # テスト1: 機種並び替え（削除なし）
    print("\n=== テスト1: 機種の並び替え ===")
    print("元の順序: iPhone13|Galaxy S22|Xperia 1IV")
    
    new_order = ['Xperia 1IV', 'iPhone13', 'Galaxy S22']
    result = processor.process_csv(
        df.copy(),
        custom_device_order=new_order
    )
    
    parent = result[result['SKU管理番号'] == '']
    if not parent.empty:
        devices = parent.iloc[0]['バリエーション2選択肢定義'].split('|')
        print(f"新しい順序: {devices}")
        if devices == new_order:
            print("✅ 並び替え成功")
        else:
            print(f"❌ 期待と違う順序 (期待: {new_order})")
    
    # テスト2: 全機種削除して新機種で再定義
    print("\n=== テスト2: 全機種削除して再定義 ===")
    print("元の機種: iPhone13|Galaxy S22|Xperia 1IV")
    
    new_devices = ['iPhone15 Pro', 'Pixel 8 Pro', 'Galaxy S24 Ultra']
    result2 = processor.process_csv(
        df.copy(),
        devices_to_add=new_devices,
        reset_all_devices=True
    )
    
    parent = result2[result2['SKU管理番号'] == '']
    if not parent.empty:
        devices = parent.iloc[0]['バリエーション2選択肢定義'].split('|')
        print(f"新しい機種: {devices}")
        if set(devices) == set(new_devices):
            print("✅ 全機種削除・再定義成功")
        else:
            print(f"❌ 期待と違う機種 (期待: {new_devices})")
    
    # SKU行も正しく作られているか確認
    sku_rows = result2[result2['SKU管理番号'] != '']
    print(f"SKU行数: {len(sku_rows)}")
    if len(sku_rows) == len(new_devices):
        print("✅ SKU行数が正しい")
    else:
        print(f"❌ SKU行数が違う (期待: {len(new_devices)})")
    
    # テスト3: 全機種削除して順序指定で再定義
    print("\n=== テスト3: 全機種削除して順序指定で再定義 ===")
    
    ordered_devices = ['Galaxy S24', 'iPhone15', 'Xperia 5V', 'Pixel 8']
    result3 = processor.process_csv(
        df.copy(),
        custom_device_order=ordered_devices,
        reset_all_devices=True
    )
    
    parent = result3[result3['SKU管理番号'] == '']
    if not parent.empty:
        devices = parent.iloc[0]['バリエーション2選択肢定義'].split('|')
        print(f"新しい機種と順序: {devices}")
        if devices == ordered_devices:
            print("✅ 全機種削除・順序指定再定義成功")
        else:
            print(f"❌ 期待と違う (期待: {ordered_devices})")

if __name__ == "__main__":
    test_reset_and_reorder()