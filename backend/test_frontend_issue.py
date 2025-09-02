#!/usr/bin/env python3
"""フロントエンドの複数機種追加問題を調査"""

def test_split_logic():
    """カンマ区切りのロジックをテスト"""
    
    test_cases = [
        "test1, test2, test3",
        "test1,test2,test3",  # スペースなし
        "test1，test2，test3",  # 全角カンマ
        "test1　，　test2　，　test3",  # 全角スペース
        "iPhone 15 Pro, Galaxy S24, Pixel 8",
    ]
    
    for test_input in test_cases:
        print(f"\n入力: '{test_input}'")
        
        # 正規化
        normalized = test_input.replace('，', ',').replace('　', ' ')
        print(f"正規化後: '{normalized}'")
        
        # 分割
        devices = [d.strip() for d in normalized.split(',') if d.strip()]
        print(f"機種リスト: {devices}")
        print(f"機種数: {len(devices)}")
        
        if len(devices) == 1:
            print("  → 単一機種 (データベース登録ダイアログを表示)")
        else:
            print("  → 複数機種 (直接追加)")

if __name__ == "__main__":
    test_split_logic()