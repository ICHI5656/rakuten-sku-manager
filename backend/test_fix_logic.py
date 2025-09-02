import pandas as pd

# テストデータ
print("="*60)
print("新機種位置指定ロジックのテスト")
print("="*60)

# 元の機種リスト（親行から取得した想定）
original_devices = [
    'Mate 20 Pro(LAY-L09)',
    'Mate 9(MHA-L29)',
    'nova 5T(YAL-L21)',
    'nova lite 3(POT-LX2J)',
    'nova lite 3+(POT-LX2J)',
    'P30 lite(HWV33/MAR-LX2)',
    'P30 Pro(HW-02L/VOG-L29)'
]

# devices_to_addが来た場合（フロントエンドから）
devices_to_add = [
    'sasaki',  # 新機種
    'Mate 20 Pro(LAY-L09)',
    'Mate 9(MHA-L29)',
    'nova 5T(YAL-L21)',
    'nova lite 3(POT-LX2J)',
    'nova lite 3+(POT-LX2J)',
    'P30 lite(HWV33/MAR-LX2)',
    'P30 Pro(HW-02L/VOG-L29)'
]

# custom_device_orderも含まれている場合（正しい順序）
custom_device_order = [
    'Mate 20 Pro(LAY-L09)',
    'Mate 9(MHA-L29)',
    'nova 5T(YAL-L21)',
    'nova lite 3(POT-LX2J)',
    'nova lite 3+(POT-LX2J)',
    'sasaki',  # P30 liteの前に追加したい
    'P30 lite(HWV33/MAR-LX2)',
    'P30 Pro(HW-02L/VOG-L29)'
]

print("\n■ 元の機種リスト（親行から）:")
for i, d in enumerate(original_devices):
    print(f"  [{i+1}] {d}")

print("\n■ devices_to_add（フロントエンドから）:")
for i, d in enumerate(devices_to_add):
    if d == 'sasaki':
        print(f"  [{i+1}] {d} ★新機種")
    else:
        print(f"  [{i+1}] {d}")

print("\n■ custom_device_order（正しい順序）:")
for i, d in enumerate(custom_device_order):
    if d == 'sasaki':
        print(f"  [{i+1}] {d} ★新機種（P30 liteの前）")
    else:
        print(f"  [{i+1}] {d}")

# 新機種の識別
original_set = set(original_devices)
really_new_devices = [d for d in devices_to_add if d not in original_set]

print("\n■ 本当に新しい機種（really_new_devices）:")
print(f"  {really_new_devices}")

# custom_device_orderが存在する場合の処理
if custom_device_order:
    print("\n■ 最終的な機種リスト（custom_device_orderを使用）:")
    final_device_list = custom_device_order
    for i, d in enumerate(final_device_list):
        if d == 'sasaki':
            print(f"  [{i+1}] {d} ★正しい位置に配置！")
        else:
            print(f"  [{i+1}] {d}")
    
    # パイプ区切りで定義文字列を作成
    device_definition = '|'.join(final_device_list)
    print(f"\n■ バリエーション2選択肢定義:")
    print(f"  {device_definition}")

print("\n" + "="*60)
print("テスト完了 - custom_device_orderが正しく使われれば成功")
print("="*60)