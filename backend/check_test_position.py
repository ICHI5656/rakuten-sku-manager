import pandas as pd

# CSVを読み込み
file_path = '/app/check_thik.csv'
df = pd.read_csv(file_path, encoding='shift-jis')

# バリエーション2選択肢定義を確認
if 'バリエーション2選択肢定義' in df.columns:
    print("バリエーション2選択肢定義の内容:")
    for idx, val in enumerate(df['バリエーション2選択肢定義'].head(5)):
        if pd.notna(val) and val:
            print(f"\n行{idx+2}: {val}")
            
            # testの位置を確認
            devices = val.split('|')
            if 'test' in devices:
                position = devices.index('test')
                print(f"  → 'test'の位置: {position+1}番目")
                print(f"  → 機種リスト:")
                for i, d in enumerate(devices[:10]):  # 最初の10個を表示
                    if d == 'test':
                        print(f"     [{i+1}] >>> {d} <<<")
                    else:
                        print(f"     [{i+1}] {d}")
            else:
                print("  → 'test'が見つかりません")

# バリエーション項目選択肢2（SKU行）も確認
if 'バリエーション項目選択肢2' in df.columns:
    print("\n\nSKU行での'test'の出現:")
    sku_rows = df[df['SKU管理番号'].notna()]
    test_rows = sku_rows[sku_rows['バリエーション項目選択肢2'] == 'test']
    print(f"  'test'を含むSKU行数: {len(test_rows)}")
    
    # 全機種のリストを確認
    all_devices = sku_rows['バリエーション項目選択肢2'].dropna().unique()
    print(f"\n全機種リスト（{len(all_devices)}種類）:")
    for i, device in enumerate(all_devices):
        if device == 'test':
            print(f"  [{i+1}] >>> {device} <<<")
        else:
            print(f"  [{i+1}] {device}")