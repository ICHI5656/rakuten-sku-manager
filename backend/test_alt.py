#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('/app')
from services.rakuten_processor import RakutenCSVProcessor
import pandas as pd

# テストCSVを読み込み
df = pd.read_csv('/app/test_with_images.csv', dtype=str, keep_default_na=False)

print('=== 処理前のデータ ===')
print(f'商品名: {df.iloc[0]["商品名"]}')
print(f'商品画像URL1: {df.iloc[0]["商品画像URL1"]}')
print(f'商品画像ALT1: {df.iloc[0]["商品画像名（ALT）1"]}')
print(f'商品画像URL2: {df.iloc[0]["商品画像URL2"]}')
print(f'商品画像ALT2: {df.iloc[0]["商品画像名（ALT）2"]}')
print(f'商品画像URL10: {df.iloc[0]["商品画像URL10"]}')
print(f'商品画像ALT10: {df.iloc[0]["商品画像名（ALT）10"]}')

# ALTテキスト自動設定を有効にして処理
processor = RakutenCSVProcessor()
result_df = processor.process_csv(df, auto_fill_alt_text=True)

print('\n=== 処理後のデータ ===')
print(f'商品名: {result_df.iloc[0]["商品名"]}')
print(f'商品画像ALT1: {result_df.iloc[0]["商品画像名（ALT）1"]} (上書きされたか確認)')
print(f'商品画像ALT2: {result_df.iloc[0]["商品画像名（ALT）2"]} (新規設定されたか確認)')
print(f'商品画像ALT3: {result_df.iloc[0]["商品画像名（ALT）3"]}')
print(f'商品画像ALT10: {result_df.iloc[0]["商品画像名（ALT）10"]}')

# CSVファイルとして保存
result_df.to_csv('/app/test_result.csv', index=False, encoding='shift_jis')
print('\n結果をtest_result.csvに保存しました')