import pandas as pd

# CSVを読み込み
file_path = '/app/check_test100.csv'
df = pd.read_csv(file_path, encoding='shift-jis')

# バリエーション2選択肢定義を確認
if 'バリエーション2選択肢定義' in df.columns:
    print("バリエーション2選択肢定義の内容:")
    for idx, val in enumerate(df['バリエーション2選択肢定義'].head(5)):
        if pd.notna(val) and val:
            print(f"\n行{idx+2}: {val[:200]}...")  # 最初の200文字
            
            # test100の存在を確認
            devices = val.split('|')
            print(f"  機種数: {len(devices)}")
            
            if 'test100' in devices:
                position = devices.index('test100')
                print(f"  → 'test100'の位置: {position+1}番目")
            else:
                print("  → 'test100'が見つかりません")
            
            # 最初と最後の機種を表示
            print(f"  → 最初の5機種: {devices[:5]}")
            print(f"  → 最後の5機種: {devices[-5:]}")

# バリエーション項目選択肢2（SKU行）も確認
if 'バリエーション項目選択肢2' in df.columns:
    print("\n\nSKU行の確認:")
    sku_rows = df[df['SKU管理番号'].notna()]
    print(f"  SKU行数: {len(sku_rows)}")
    
    # test100を含む行を探す
    test100_rows = sku_rows[sku_rows['バリエーション項目選択肢2'] == 'test100']
    print(f"  'test100'を含むSKU行数: {len(test100_rows)}")
    
    # 全機種のリストを確認
    all_devices = sku_rows['バリエーション項目選択肢2'].dropna().unique()
    print(f"\n全機種リスト（{len(all_devices)}種類）:")
    for device in all_devices:
        if 'test' in str(device).lower():
            print(f"  - {device} <<<")
        else:
            print(f"  - {device}")

# 商品管理番号も確認
if '商品管理番号（商品URL）' in df.columns:
    products = df[df['商品管理番号（商品URL）'].notna()]['商品管理番号（商品URL）'].unique()
    print(f"\n商品数: {len(products)}")
    for p in products[:3]:
        print(f"  - {p}")