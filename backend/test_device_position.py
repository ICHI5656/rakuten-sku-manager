#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
機種位置制御機能のテストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from services.rakuten_processor import RakutenCSVProcessor
from services.csv_processor import CSVProcessor

def test_custom_device_order():
    """custom_device_orderのテスト"""
    print("=" * 60)
    print("TEST: custom_device_order（完全な機種順序指定）")
    print("=" * 60)
    
    # テストデータ作成
    test_data = {
        '商品管理番号（商品URL）': ['TEST001', 'TEST001', 'TEST001'],
        'SKU管理番号': ['', 'sku_a000001', 'sku_a000002'],
        'バリエーション項目選択肢1': ['', 'ブラック', 'ホワイト'],
        'バリエーション項目選択肢2': ['', 'iPhone15', 'iPhone15'],
        'バリエーション2選択肢定義': ['iPhone15|iPhone14', '', '']
    }
    
    df = pd.DataFrame(test_data)
    
    processor = RakutenCSVProcessor()
    
    # custom_device_orderで完全な順序を指定
    custom_order = ['iPhone14', 'Galaxy S24', 'iPhone15', 'Xperia 1V']
    
    result = processor.process_csv(
        df,
        devices_to_add=['Galaxy S24', 'Xperia 1V'],  # 新規追加機種
        custom_device_order=custom_order  # 完全な順序指定
    )
    
    # 結果確認
    parent_row = result[result['SKU管理番号'] == '']
    if not parent_row.empty:
        device_def = parent_row.iloc[0]['バリエーション2選択肢定義']
        print(f"結果の機種定義: {device_def}")
        print(f"期待値: {'|'.join(custom_order)}")
        
        if device_def == '|'.join(custom_order):
            print("✅ テスト成功: custom_device_orderが正しく適用されました")
        else:
            print("❌ テスト失敗: 機種順序が期待と異なります")
    
    print()
    return result

def test_position_start():
    """先頭追加のテスト"""
    print("=" * 60)
    print("TEST: add_position='start'（先頭に追加）")
    print("=" * 60)
    
    test_data = {
        '商品管理番号（商品URL）': ['TEST002', 'TEST002', 'TEST002'],
        'SKU管理番号': ['', 'sku_a000001', 'sku_a000002'],
        'バリエーション項目選択肢1': ['', 'ブラック', 'ホワイト'],
        'バリエーション項目選択肢2': ['', 'iPhone15', 'iPhone15'],
        'バリエーション2選択肢定義': ['iPhone15|iPhone14', '', '']
    }
    
    df = pd.DataFrame(test_data)
    processor = RakutenCSVProcessor()
    
    result = processor.process_csv(
        df,
        devices_to_add=['Galaxy S24'],
        add_position='start'
    )
    
    parent_row = result[result['SKU管理番号'] == '']
    if not parent_row.empty:
        device_def = parent_row.iloc[0]['バリエーション2選択肢定義']
        print(f"結果の機種定義: {device_def}")
        
        if device_def.startswith('Galaxy S24'):
            print("✅ テスト成功: 新機種が先頭に追加されました")
        else:
            print("❌ テスト失敗: 新機種が先頭にありません")
    
    print()
    return result

def test_position_after():
    """特定機種の後に追加のテスト"""
    print("=" * 60)
    print("TEST: add_position='after'（特定機種の後に追加）")
    print("=" * 60)
    
    test_data = {
        '商品管理番号（商品URL）': ['TEST003', 'TEST003', 'TEST003', 'TEST003'],
        'SKU管理番号': ['', 'sku_a000001', 'sku_a000002', 'sku_a000003'],
        'バリエーション項目選択肢1': ['', 'ブラック', 'ホワイト', 'ブラック'],
        'バリエーション項目選択肢2': ['', 'iPhone15', 'iPhone15', 'iPhone14'],
        'バリエーション2選択肢定義': ['iPhone15|iPhone14|iPhone13', '', '', '']
    }
    
    df = pd.DataFrame(test_data)
    processor = RakutenCSVProcessor()
    
    result = processor.process_csv(
        df,
        devices_to_add=['Galaxy S24'],
        add_position='after',
        after_device='iPhone14'
    )
    
    parent_row = result[result['SKU管理番号'] == '']
    if not parent_row.empty:
        device_def = parent_row.iloc[0]['バリエーション2選択肢定義']
        print(f"結果の機種定義: {device_def}")
        
        devices = device_def.split('|')
        if 'iPhone14' in devices and 'Galaxy S24' in devices:
            iphone14_idx = devices.index('iPhone14')
            galaxy_idx = devices.index('Galaxy S24')
            if galaxy_idx == iphone14_idx + 1:
                print("✅ テスト成功: Galaxy S24がiPhone14の直後に追加されました")
            else:
                print("❌ テスト失敗: Galaxy S24の位置が正しくありません")
        else:
            print("❌ テスト失敗: 必要な機種が見つかりません")
    
    print()
    return result

def test_existing_device_no_duplicate():
    """既存機種を追加しても重複しないテスト"""
    print("=" * 60)
    print("TEST: 既存機種の重複防止")
    print("=" * 60)
    
    test_data = {
        '商品管理番号（商品URL）': ['TEST004', 'TEST004', 'TEST004'],
        'SKU管理番号': ['', 'sku_a000001', 'sku_a000002'],
        'バリエーション項目選択肢1': ['', 'ブラック', 'ホワイト'],
        'バリエーション項目選択肢2': ['', 'iPhone15', 'iPhone15'],
        'バリエーション2選択肢定義': ['iPhone15|iPhone14', '', '']
    }
    
    df = pd.DataFrame(test_data)
    processor = RakutenCSVProcessor()
    
    # 既に存在するiPhone15を追加しようとする
    result = processor.process_csv(
        df,
        devices_to_add=['iPhone15', 'Galaxy S24'],  # iPhone15は既存
        add_position='end'
    )
    
    parent_row = result[result['SKU管理番号'] == '']
    if not parent_row.empty:
        device_def = parent_row.iloc[0]['バリエーション2選択肢定義']
        print(f"結果の機種定義: {device_def}")
        
        devices = device_def.split('|')
        iphone15_count = devices.count('iPhone15')
        
        if iphone15_count == 1:
            print("✅ テスト成功: iPhone15の重複が防止されました")
        else:
            print(f"❌ テスト失敗: iPhone15が{iphone15_count}回出現しています")
    
    # SKU行の数も確認
    sku_rows = result[result['SKU管理番号'] != '']
    print(f"SKU行数: {len(sku_rows)}")
    
    print()
    return result

def main():
    """メインテスト実行"""
    print("\n機種位置制御機能テスト開始\n")
    
    # 各テストを実行
    test_custom_device_order()
    test_position_start()
    test_position_after()
    test_existing_device_no_duplicate()
    
    print("\n全テスト完了\n")

if __name__ == "__main__":
    main()