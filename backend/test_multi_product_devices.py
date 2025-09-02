#!/usr/bin/env python3
"""異なる機種セットを持つ複数製品への新機種追加テスト"""

import pandas as pd
from pathlib import Path
from services.rakuten_processor import RakutenCSVProcessor

def test_multi_product_device_addition():
    # テストデータ作成
    data = {
        '商品管理番号（商品URL）': ['product_A', 'product_A', 'product_A', 'product_B', 'product_B'],
        'SKU管理番号': ['', 'sku_a000001', 'sku_a000002', '', 'sku_b000001'],
        'バリエーション2選択肢定義': ['iPhone13|iPhone14', '', '', 'Galaxy S22', ''],
        'バリエーション項目選択肢2': ['', 'iPhone13', 'iPhone14', '', 'Galaxy S22'],
        '在庫タイプ': ['通常在庫'] * 5,
        '商品名': ['Product A'] * 3 + ['Product B'] * 2
    }
    
    df = pd.DataFrame(data)
    
    # プロセッサ初期化
    processor = RakutenCSVProcessor(Path('/app/data/state/sku_counters.json'))
    
    # テスト1: 両製品に新機種追加
    print("\n=== テスト1: iPhone15を全製品に追加 ===")
    result = processor.process_csv(
        df.copy(),
        devices_to_add=['iPhone15'],
        add_position='end'
    )
    
    # 結果確認
    print("\n結果:")
    for product_id in ['product_A', 'product_B']:
        product_rows = result[result['商品管理番号（商品URL）'] == product_id]
        parent = product_rows[product_rows['SKU管理番号'] == '']
        if not parent.empty:
            devices = parent.iloc[0]['バリエーション2選択肢定義'].split('|')
            print(f"{product_id}: {devices}")
            if 'iPhone15' in devices:
                print(f"  ✅ iPhone15が追加された")
            else:
                print(f"  ❌ iPhone15が追加されていない")
    
    # テスト2: custom_device_orderで全製品の順序統一
    print("\n=== テスト2: custom_device_orderで統一 ===")
    custom_order = ['iPhone14', 'iPhone15', 'Galaxy S22', 'iPhone13']
    result2 = processor.process_csv(
        df.copy(),
        devices_to_add=['iPhone15'],
        custom_device_order=custom_order
    )
    
    print("\n結果:")
    for product_id in ['product_A', 'product_B']:
        product_rows = result2[result2['商品管理番号（商品URL）'] == product_id]
        parent = product_rows[product_rows['SKU管理番号'] == '']
        if not parent.empty:
            devices = parent.iloc[0]['バリエーション2選択肢定義'].split('|')
            print(f"{product_id}: {devices}")
            # 期待される順序と比較
            expected = [d for d in custom_order if d in devices or d == 'iPhone15']
            if devices == expected:
                print(f"  ✅ 順序が正しい")
            else:
                print(f"  ❌ 順序が違う (期待: {expected})")

if __name__ == "__main__":
    test_multi_product_device_addition()