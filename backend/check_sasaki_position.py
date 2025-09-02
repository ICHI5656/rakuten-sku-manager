import pandas as pd

# CSVを読み込み
file_path = '/app/check_sasaki.csv'
df = pd.read_csv(file_path, encoding='shift-jis')

print("="*60)
print("SASAKI位置問題の調査")
print("="*60)

# バリエーション2選択肢定義を確認
if 'バリエーション2選択肢定義' in df.columns:
    print("\n■ バリエーション2選択肢定義の内容:")
    for idx, val in enumerate(df['バリエーション2選択肢定義'].head(5)):
        if pd.notna(val) and val:
            print(f"\n行{idx+2}: ")
            
            # sasakiの位置を確認
            devices = val.split('|')
            print(f"  機種数: {len(devices)}")
            
            if 'sasaki' in devices:
                position = devices.index('sasaki')
                print(f"  → 'sasaki'の位置: {position+1}番目")
                print(f"\n  → 機種リスト:")
                for i, d in enumerate(devices):
                    if d == 'sasaki':
                        print(f"     [{i+1}] >>> {d} <<< ★新機種")
                    else:
                        print(f"     [{i+1}] {d}")
            else:
                print("  → 'sasaki'が見つかりません")
                print(f"\n  → 機種リスト:")
                for i, d in enumerate(devices[:10]):
                    print(f"     [{i+1}] {d}")

# バリエーション項目選択肢2（SKU行）も確認
if 'バリエーション項目選択肢2' in df.columns:
    print("\n\n■ SKU行での機種の出現:")
    sku_rows = df[df['SKU管理番号'].notna()]
    
    # sasakiを含む行を探す
    sasaki_rows = sku_rows[sku_rows['バリエーション項目選択肢2'] == 'sasaki']
    print(f"  'sasaki'を含むSKU行数: {len(sasaki_rows)}")
    
    # 全機種のリストを確認
    all_devices = sku_rows['バリエーション項目選択肢2'].dropna().unique()
    print(f"\n  全機種リスト（{len(all_devices)}種類）:")
    for i, device in enumerate(all_devices):
        if device == 'sasaki':
            print(f"  [{i+1}] >>> {device} <<< ★新機種")
        else:
            print(f"  [{i+1}] {device}")

print("\n" + "="*60)
print("調査完了")
print("="*60)