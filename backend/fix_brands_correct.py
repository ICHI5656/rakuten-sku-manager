#!/usr/bin/env python3
"""
ブランド名統一化スクリプト（修正版）
UIのブランド表示と完全に一致させる
"""
import sqlite3
import json
from pathlib import Path

def normalize_brand_name(device_name):
    """デバイス名からブランド名を正規化
    UIと完全に一致させる: IPHONE, XPERIA, AQUOS, GALAXY, GOOGLE PIXEL, HUAWEI, ARROWS, その他
    """
    if not device_name:
        return 'その他'
    
    device_lower = device_name.lower()
    
    # ブランド判定（UIの表示と一致）
    if 'iphone' in device_lower:
        return 'IPHONE'
    elif 'xperia' in device_lower:
        return 'XPERIA'
    elif 'aquos' in device_lower:
        return 'AQUOS'
    elif 'galaxy' in device_lower:
        return 'GALAXY'
    elif 'pixel' in device_lower:
        return 'GOOGLE PIXEL'
    elif 'huawei' in device_lower or 'mate' in device_lower or 'nova' in device_lower or 'p30' in device_lower or 'p40' in device_lower:
        return 'HUAWEI'
    elif 'arrows' in device_lower:
        return 'ARROWS'
    elif 'oppo' in device_lower or 'reno' in device_lower or 'find' in device_lower:
        return 'OPPO'
    else:
        # 個別のデバイス名チェック
        device_name_clean = device_name.replace(' ', '').replace('-', '').lower()
        
        # Xperiaの追加パターン
        if any(x in device_name_clean for x in ['1vi', '1v', '1iv', '1iii', '1ii', '10v', '10iv', '10iii', '5v', '5iv']):
            if 'xperia' not in device_lower:  # "1 VI(SO-51E)" のようなケース
                return 'XPERIA'
        
        # AQUOSの追加パターン
        elif any(x in device_name_clean for x in ['sense', 'wish', 'r9', 'r8', 'r7', 'r6', 'zero']):
            if 'aquos' not in device_lower:
                return 'AQUOS'
        
        # Galaxyの追加パターン
        elif any(x in device_name_clean for x in ['s24', 's23', 's22', 's21', 'a55', 'a54', 'a53', 'z fold', 'z flip']):
            if 'galaxy' not in device_lower:
                return 'GALAXY'
        
        return 'その他'

def main():
    db_path = '/app/product_attributes_new.db'
    
    print("=" * 50)
    print("ブランド名統一化処理（修正版）")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 現在のデータを取得
        print("\n1. 現在のデバイスデータを取得中...")
        cursor.execute('''
            SELECT device_name, brand, size_category, attribute_value, id
            FROM device_attributes
            ORDER BY device_name
        ''')
        devices = cursor.fetchall()
        print(f"  → {len(devices)} 件のデバイスを取得しました")
        
        # ブランド名を正規化
        print("\n2. ブランド名を正規化中...")
        update_count = 0
        brand_stats = {}
        
        for device_name, current_brand, size_category, attribute_value, device_id in devices:
            if device_name:
                normalized_brand = normalize_brand_name(device_name)
                
                # 統計を記録
                if normalized_brand not in brand_stats:
                    brand_stats[normalized_brand] = []
                brand_stats[normalized_brand].append(device_name)
                
                # 更新が必要な場合
                if current_brand != normalized_brand:
                    cursor.execute('''
                        UPDATE device_attributes 
                        SET brand = ?
                        WHERE id = ?
                    ''', (normalized_brand, device_id))
                    update_count += 1
                    print(f"  更新: {device_name}: {current_brand} → {normalized_brand}")
        
        print(f"\n  → {update_count} 件のブランド名を更新しました")
        
        # コミット
        conn.commit()
        
        # 最終統計を表示
        print("\n3. 最終的なブランド統計:")
        print("-" * 40)
        
        # UIの順番で表示
        ui_order = ['IPHONE', 'XPERIA', 'AQUOS', 'GALAXY', 'GOOGLE PIXEL', 'HUAWEI', 'ARROWS', 'その他', 'OPPO']
        
        for brand in ui_order:
            if brand in brand_stats:
                count = len(brand_stats[brand])
                print(f"  {brand}: {count} devices")
                # 最初の3つのデバイスを表示
                for i, device in enumerate(brand_stats[brand][:3]):
                    print(f"    - {device}")
                if count > 3:
                    print(f"    ... 他 {count - 3} devices")
        
        # データベースからも確認
        print("\n4. データベースの最終確認:")
        cursor.execute('''
            SELECT brand, COUNT(*) as count 
            FROM device_attributes 
            GROUP BY brand 
            ORDER BY 
                CASE brand
                    WHEN 'IPHONE' THEN 1
                    WHEN 'XPERIA' THEN 2
                    WHEN 'AQUOS' THEN 3
                    WHEN 'GALAXY' THEN 4
                    WHEN 'GOOGLE PIXEL' THEN 5
                    WHEN 'HUAWEI' THEN 6
                    WHEN 'ARROWS' THEN 7
                    WHEN 'その他' THEN 8
                    ELSE 9
                END
        ''')
        
        for brand, count in cursor.fetchall():
            print(f"  {brand}: {count} devices")
        
        print("\n✅ ブランド名の統一化が完了しました！")
        print("  UIの表示と完全に一致するようになりました。")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()