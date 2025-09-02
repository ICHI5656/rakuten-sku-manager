import pandas as pd
import chardet

# ファイルのエンコーディングを検出
file_path = '/app/test_file.csv'
with open(file_path, 'rb') as f:
    result = chardet.detect(f.read(10000))
    encoding = result['encoding']
    print(f"Detected encoding: {encoding}")

# CSVを読み込み
df = pd.read_csv(file_path, encoding='shift-jis')

# バリエーション関連の列を探す
print("\nバリエーション関連の列:")
for col in df.columns:
    if 'バリエーション' in col:
        print(f"  - {col}")

# バリエーション2選択肢定義を確認
if 'バリエーション2選択肢定義' in df.columns:
    print("\nバリエーション2選択肢定義の値（最初の5行）:")
    for idx, val in enumerate(df['バリエーション2選択肢定義'].head(10)):
        if pd.notna(val) and val:
            print(f"  行{idx+2}: {val}")
            
# バリエーション項目選択肢2も確認（SKU行）
if 'バリエーション項目選択肢2' in df.columns:
    print("\nバリエーション項目選択肢2の値（SKU行、最初の10個）:")
    sku_rows = df[df['SKU管理番号'].notna()].head(10)
    for idx, row in sku_rows.iterrows():
        val = row['バリエーション項目選択肢2']
        if pd.notna(val):
            print(f"  SKU行: {val}")

# 商品管理番号を確認
if '商品管理番号（商品URL）' in df.columns:
    print("\n商品管理番号:")
    products = df[df['商品管理番号（商品URL）'].notna()]['商品管理番号（商品URL）'].unique()
    for prod in products[:5]:
        print(f"  - {prod}")