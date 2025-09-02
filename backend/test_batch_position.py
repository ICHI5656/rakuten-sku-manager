#!/usr/bin/env python3
"""
バッチ処理の機種位置指定機能テストスクリプト
"""

import os
import json
import shutil
import pandas as pd
from pathlib import Path
from services.batch_processor import BatchProcessor

def create_test_csv(filename, product_id, devices):
    """テスト用CSVファイルを作成"""
    data = {
        '商品管理番号（商品URL）': [product_id],
        '商品番号': [''],
        '全商品ディレクトリID': [''],
        '在庫タイプ': ['通常在庫'],
        'SKU管理番号': [''],
        'システム連携用SKU番号': [''],
        'バリエーション2選択肢定義': [','.join(devices)],
        '商品名': [f'Test Product {product_id}'],
        'PC用販売説明文': ['Test description'],
        'スマートフォン用商品説明文': ['Test mobile description']
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='shift-jis')
    print(f"テストファイル作成: {filename}")
    return filename

def test_batch_position_control():
    """バッチ処理の位置指定機能をテスト"""
    
    print("\n=== バッチ処理の位置指定機能テスト開始 ===\n")
    
    # テスト用ディレクトリを作成
    test_dir = Path('/app/data/test_batch')
    test_dir.mkdir(exist_ok=True)
    
    # バッチプロセッサを初期化
    processor = BatchProcessor(state_dir=Path('/app/data/state'))
    
    # テスト用CSVファイルを作成
    test_files = []
    test_files.append(create_test_csv(
        test_dir / 'test1.csv',
        'product_001',
        ['iPhone13', 'iPhone14', 'iPhone15']
    ))
    test_files.append(create_test_csv(
        test_dir / 'test2.csv',
        'product_002',
        ['Galaxy S22', 'Galaxy S23']
    ))
    test_files.append(create_test_csv(
        test_dir / 'test3.csv',
        'product_003',
        ['Xperia 1IV', 'Xperia 5IV']
    ))
    
    # ケース1: custom_device_orderで指定
    print("\n--- ケース1: custom_device_orderで指定 ---")
    custom_order = ['iPhone14', 'Galaxy S24', 'iPhone13', 'Xperia 1V', 'iPhone15']
    
    import asyncio
    async def run_test1():
        result = await processor.process_batch_files(
            file_paths=test_files,
            devices_to_add=['Galaxy S24', 'Xperia 1V'],
            custom_device_order=custom_order,
            output_format='single',
            apply_to_all=True
        )
        return result
    
    result1 = asyncio.run(run_test1())
    
    # 結果を確認
    for file_result in result1['results']:
        print(f"\n{file_result['filename']}:")
        print(f"  ステータス: {file_result['status']}")
        if file_result['status'] == 'success':
            # 結果CSVを読み込んで機種順を確認
            output_path = Path(file_result['output_path'])
            if output_path.exists():
                df = pd.read_csv(output_path, encoding='shift-jis')
                parent_rows = df[df['SKU管理番号'].isna()]
                if not parent_rows.empty:
                    device_def = parent_rows.iloc[0]['バリエーション2選択肢定義']
                    if pd.notna(device_def):
                        devices = device_def.split(',')
                        print(f"  機種順序: {devices}")
                        # 期待される順序と比較
                        expected = ['iPhone14', 'Galaxy S24', 'iPhone13', 'Xperia 1V', 'iPhone15']
                        if devices == expected:
                            print("  ✅ 順序が正しい")
                        else:
                            print(f"  ❌ 順序が違う")
                            print(f"     期待: {expected}")
    
    # ケース2: add_position='start'で指定
    print("\n--- ケース2: add_position='start'で指定 ---")
    
    async def run_test2():
        result = await processor.process_batch_files(
            file_paths=test_files,
            devices_to_add=['NewDevice1', 'NewDevice2'],
            add_position='start',
            output_format='single',
            apply_to_all=True
        )
        return result
    
    result2 = asyncio.run(run_test2())
    
    for file_result in result2['results']:
        print(f"\n{file_result['filename']}:")
        print(f"  ステータス: {file_result['status']}")
        if file_result['status'] == 'success':
            output_path = Path(file_result['output_path'])
            if output_path.exists():
                df = pd.read_csv(output_path, encoding='shift-jis')
                parent_rows = df[df['SKU管理番号'].isna()]
                if not parent_rows.empty:
                    device_def = parent_rows.iloc[0]['バリエーション2選択肢定義']
                    if pd.notna(device_def):
                        devices = device_def.split(',')
                        print(f"  機種順序: {devices}")
                        # 新機種が最初に来ているか確認
                        if devices[:2] == ['NewDevice1', 'NewDevice2']:
                            print("  ✅ 新機種が最初に追加された")
                        else:
                            print("  ❌ 新機種の位置が違う")
    
    # ケース3: add_position='after'で指定
    print("\n--- ケース3: add_position='after'で指定 ---")
    
    async def run_test3():
        result = await processor.process_batch_files(
            file_paths=[test_files[0]],  # iPhone13, iPhone14, iPhone15を含むファイル
            devices_to_add=['AfterDevice1', 'AfterDevice2'],
            add_position='after',
            after_device='iPhone14',
            output_format='single',
            apply_to_all=True
        )
        return result
    
    result3 = asyncio.run(run_test3())
    
    for file_result in result3['results']:
        print(f"\n{file_result['filename']}:")
        print(f"  ステータス: {file_result['status']}")
        if file_result['status'] == 'success':
            output_path = Path(file_result['output_path'])
            if output_path.exists():
                df = pd.read_csv(output_path, encoding='shift-jis')
                parent_rows = df[df['SKU管理番号'].isna()]
                if not parent_rows.empty:
                    device_def = parent_rows.iloc[0]['バリエーション2選択肢定義']
                    if pd.notna(device_def):
                        devices = device_def.split(',')
                        print(f"  機種順序: {devices}")
                        # iPhone14の後に新機種が来ているか確認
                        try:
                            iphone14_index = devices.index('iPhone14')
                            if devices[iphone14_index+1:iphone14_index+3] == ['AfterDevice1', 'AfterDevice2']:
                                print("  ✅ 新機種がiPhone14の後に追加された")
                            else:
                                print("  ❌ 新機種の位置が違う")
                        except ValueError:
                            print("  ❌ iPhone14が見つからない")
    
    # テストディレクトリをクリーンアップ
    shutil.rmtree(test_dir, ignore_errors=True)
    
    print("\n=== テスト完了 ===\n")

if __name__ == "__main__":
    test_batch_position_control()