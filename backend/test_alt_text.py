#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
商品画像ALTテキスト自動設定機能のテストスクリプト
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.rakuten_processor import RakutenCSVProcessor

def create_test_data():
    """テスト用CSVデータを作成"""
    
    # 楽天CSV形式のテストデータ
    data = {
        '商品管理番号（商品URL）': ['product001', 'product001', 'product001', 'product002', 'product002'],
        'SKU管理番号': ['', 'sku_a000001', 'sku_a000002', '', 'sku_b000001'],
        '商品名': ['テスト商品1', '', '', 'テスト商品2', ''],
        'バリエーション項目選択肢1': ['', 'ブラック', 'ホワイト', '', 'レッド'],
        'バリエーション項目選択肢2': ['', 'iPhone 13', 'iPhone 13', '', 'iPhone 14'],
        'バリエーション1選択肢定義': ['ブラック|ホワイト', '', '', 'レッド|ブルー', ''],
        'バリエーション2選択肢定義': ['iPhone 13|iPhone 14', '', '', 'iPhone 14|iPhone 15', ''],
    }
    
    # 商品画像URLとALTテキストのカラムを追加（1～10まで）
    for i in range(1, 11):
        # 画像URLカラム
        url_col = f'商品画像URL{i}'
        alt_col = f'商品画像名（ALT）{i}'
        
        if i <= 3:
            # 1～3は画像URLあり
            data[url_col] = [
                f'https://example.com/product001_{i}.jpg',  # 親行1: URLあり
                '',  # SKU行
                '',  # SKU行
                f'https://example.com/product002_{i}.jpg',  # 親行2: URLあり
                ''   # SKU行
            ]
            
            if i == 1:
                # ALT1は既存値あり（上書きテスト）
                data[alt_col] = ['既存のALTテキスト', '', '', '', '']
            else:
                # ALT2, 3は空（新規設定テスト）
                data[alt_col] = ['', '', '', '', '']
        else:
            # 4～10は画像URLなし
            data[url_col] = ['', '', '', '', '']
            data[alt_col] = ['', '', '', '', '']
    
    return pd.DataFrame(data)

def test_alt_text_processing():
    """ALTテキスト自動設定機能のテスト"""
    
    print("=" * 60)
    print("商品画像ALTテキスト自動設定機能のテスト")
    print("=" * 60)
    
    # テストデータ作成
    df = create_test_data()
    
    print("\n■ 処理前のデータ:")
    print("-" * 40)
    print("親行1（product001）:")
    print(f"  商品名: {df.iloc[0]['商品名']}")
    print(f"  商品画像URL1: {df.iloc[0]['商品画像URL1']}")
    print(f"  商品画像名（ALT）1: {df.iloc[0]['商品画像名（ALT）1']}")
    print(f"  商品画像URL2: {df.iloc[0]['商品画像URL2']}")
    print(f"  商品画像名（ALT）2: {df.iloc[0]['商品画像名（ALT）2']}")
    print(f"  商品画像URL3: {df.iloc[0]['商品画像URL3']}")
    print(f"  商品画像名（ALT）3: {df.iloc[0]['商品画像名（ALT）3']}")
    
    print("\n親行2（product002）:")
    print(f"  商品名: {df.iloc[3]['商品名']}")
    print(f"  商品画像URL1: {df.iloc[3]['商品画像URL1']}")
    print(f"  商品画像名（ALT）1: {df.iloc[3]['商品画像名（ALT）1']}")
    
    # RakutenCSVProcessorで処理
    processor = RakutenCSVProcessor()
    
    # ALTテキスト自動設定を有効にして処理
    result_df = processor.process_csv(
        df,
        devices_to_add=None,
        devices_to_remove=None,
        auto_fill_alt_text=True  # ALTテキスト自動設定を有効化
    )
    
    print("\n■ 処理後のデータ:")
    print("-" * 40)
    print("親行1（product001）:")
    print(f"  商品名: {result_df.iloc[0]['商品名']}")
    print(f"  商品画像URL1: {result_df.iloc[0]['商品画像URL1']}")
    print(f"  商品画像名（ALT）1: {result_df.iloc[0]['商品画像名（ALT）1']} ← 商品名で上書きされた")
    print(f"  商品画像URL2: {result_df.iloc[0]['商品画像URL2']}")
    print(f"  商品画像名（ALT）2: {result_df.iloc[0]['商品画像名（ALT）2']} ← 商品名が設定された")
    print(f"  商品画像URL3: {result_df.iloc[0]['商品画像URL3']}")
    print(f"  商品画像名（ALT）3: {result_df.iloc[0]['商品画像名（ALT）3']} ← 商品名が設定された")
    print(f"  商品画像URL4: {result_df.iloc[0]['商品画像URL4']}")
    print(f"  商品画像名（ALT）4: {result_df.iloc[0]['商品画像名（ALT）4']} ← URLがないので空のまま")
    
    print("\n親行2（product002）:")
    print(f"  商品名: {result_df.iloc[3]['商品名']}")
    print(f"  商品画像URL1: {result_df.iloc[3]['商品画像URL1']}")
    print(f"  商品画像名（ALT）1: {result_df.iloc[3]['商品画像名（ALT）1']} ← 商品名が設定された")
    
    # SKU行のチェック（変更されていないことを確認）
    print("\nSKU行（変更されていないことを確認）:")
    print(f"  SKU行1のALT1: {result_df.iloc[1]['商品画像名（ALT）1']} ← 空のまま")
    print(f"  SKU行2のALT1: {result_df.iloc[2]['商品画像名（ALT）1']} ← 空のまま")
    
    # テスト結果の検証
    print("\n■ テスト結果:")
    print("-" * 40)
    
    tests_passed = 0
    tests_total = 0
    
    # テスト1: 既存ALTの上書き
    tests_total += 1
    if result_df.iloc[0]['商品画像名（ALT）1'] == 'テスト商品1':
        print("✅ テスト1 成功: 既存のALTテキストが商品名で上書きされました")
        tests_passed += 1
    else:
        print("❌ テスト1 失敗: 既存のALTテキストが上書きされませんでした")
    
    # テスト2: 空のALTに商品名設定
    tests_total += 1
    if result_df.iloc[0]['商品画像名（ALT）2'] == 'テスト商品1':
        print("✅ テスト2 成功: 空のALTテキストに商品名が設定されました")
        tests_passed += 1
    else:
        print("❌ テスト2 失敗: 空のALTテキストに商品名が設定されませんでした")
    
    # テスト3: URLがない場合はALTを変更しない
    tests_total += 1
    if result_df.iloc[0]['商品画像名（ALT）4'] == '':
        print("✅ テスト3 成功: URLがない場合はALTを変更しませんでした")
        tests_passed += 1
    else:
        print("❌ テスト3 失敗: URLがない場合でもALTが変更されました")
    
    # テスト4: SKU行は処理対象外
    tests_total += 1
    if result_df.iloc[1]['商品画像名（ALT）1'] == '':
        print("✅ テスト4 成功: SKU行のALTは変更されませんでした")
        tests_passed += 1
    else:
        print("❌ テスト4 失敗: SKU行のALTが変更されました")
    
    # テスト5: 複数商品の処理
    tests_total += 1
    if result_df.iloc[3]['商品画像名（ALT）1'] == 'テスト商品2':
        print("✅ テスト5 成功: 複数商品が正しく処理されました")
        tests_passed += 1
    else:
        print("❌ テスト5 失敗: 複数商品の処理に問題があります")
    
    # テスト6: ALTテキスト無効化のテスト
    print("\n■ ALTテキスト自動設定を無効化した場合のテスト:")
    df2 = create_test_data()
    result_df2 = processor.process_csv(
        df2,
        devices_to_add=None,
        devices_to_remove=None,
        auto_fill_alt_text=False  # ALTテキスト自動設定を無効化
    )
    
    tests_total += 1
    if result_df2.iloc[0]['商品画像名（ALT）1'] == '既存のALTテキスト':
        print("✅ テスト6 成功: 無効化時はALTテキストが変更されませんでした")
        tests_passed += 1
    else:
        print("❌ テスト6 失敗: 無効化時でもALTテキストが変更されました")
    
    # 総合結果
    print("\n" + "=" * 60)
    print(f"テスト結果: {tests_passed}/{tests_total} 成功")
    if tests_passed == tests_total:
        print("🎉 すべてのテストが成功しました！")
    else:
        print(f"⚠️ {tests_total - tests_passed}個のテストが失敗しました")
    print("=" * 60)
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = test_alt_text_processing()
    sys.exit(0 if success else 1)