#!/usr/bin/env python3
"""
ブランド名統一化スクリプト（安全版）
データベース管理UIと一致させる
"""
import sqlite3
import json
from pathlib import Path

def normalize_brand_name(device_name):
    """デバイス名からブランド名を正規化"""
    if not device_name:
        return 'その他'
    
    device_lower = device_name.lower()
    
    # UIに表示されているブランドと一致させる
    if 'iphone' in device_lower:
        return 'IPHONE'  # 大文字で統一
    elif 'xperia' in device_lower:
        return 'XPERIA'  # 大文字で統一
    elif 'aquos' in device_lower:
        return 'AQUOS'
    elif 'galaxy' in device_lower:
        return 'GALAXY'  # 大文字で統一
    elif 'pixel' in device_lower:
        return 'GOOGLE PIXEL'  # 大文字で統一
    elif 'huawei' in device_lower:
        return 'HUAWEI'
    elif 'arrows' in device_lower:
        return 'ARROWS'
    elif 'oppo' in device_lower:
        return 'OPPO'
    elif 'moto' in device_lower or 'razr' in device_lower:
        return 'その他'
    elif 'zenfone' in device_lower or 'rog phone' in device_lower:
        return 'その他'
    elif 'redmi' in device_lower or 'mi ' in device_lower or 'xiaomi' in device_lower:
        return 'その他'
    else:
        return 'その他'

def main():
    db_path = '/app/product_attributes_new.db'
    
    print("=" * 50)
    print("ブランド名統一化処理")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # まず重複データを削除
        print("\n1. 重複データを削除中...")
        cursor.execute('''
            DELETE FROM device_attributes 
            WHERE rowid NOT IN (
                SELECT MIN(rowid) 
                FROM device_attributes 
                GROUP BY device_name, size_category
            )
        ''')
        deleted_count = cursor.rowcount
        print(f"  → {deleted_count} 件の重複を削除しました")
        
        # 現在のデータを取得
        print("\n2. デバイスデータを取得中...")
        cursor.execute('''
            SELECT DISTINCT device_name, brand, size_category, attribute_value
            FROM device_attributes
        ''')
        devices = cursor.fetchall()
        print(f"  → {len(devices)} 件のデバイスを取得しました")
        
        # ブランド名を正規化して更新
        print("\n3. ブランド名を正規化中...")
        update_count = 0
        brand_mapping = {}
        
        for device_name, current_brand, size_category, attribute_value in devices:
            if device_name:
                normalized_brand = normalize_brand_name(device_name)
                
                if current_brand != normalized_brand:
                    # 既存のレコードを削除
                    cursor.execute('''
                        DELETE FROM device_attributes 
                        WHERE device_name = ? AND size_category = ?
                    ''', (device_name, size_category))
                    
                    # 新しいブランド名で挿入
                    cursor.execute('''
                        INSERT INTO device_attributes 
                        (brand, device_name, attribute_value, size_category)
                        VALUES (?, ?, ?, ?)
                    ''', (normalized_brand, device_name, attribute_value or '', size_category))
                    
                    update_count += 1
                    brand_mapping[device_name] = {
                        'old': current_brand,
                        'new': normalized_brand
                    }
        
        print(f"  → {update_count} 件のブランド名を更新しました")
        
        # コミット
        conn.commit()
        
        # 統計を表示
        print("\n4. 最終的なブランド統計:")
        cursor.execute('''
            SELECT brand, COUNT(*) as count 
            FROM device_attributes 
            GROUP BY brand 
            ORDER BY count DESC
        ''')
        
        for brand, count in cursor.fetchall():
            print(f"  • {brand}: {count} devices")
        
        # マッピング情報を保存
        if brand_mapping:
            mapping_file = Path('/app/brand_normalization.json')
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(brand_mapping, f, ensure_ascii=False, indent=2)
            print(f"\n5. ブランドマッピングを保存: {mapping_file}")
        
        print("\n✅ ブランド名の統一化が完了しました！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()