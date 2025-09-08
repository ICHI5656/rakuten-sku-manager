#!/usr/bin/env python3
"""
ブランド名の統一化とデータベース更新スクリプト
商品属性（値）8のブランド名を正規化して統一管理
"""

import sqlite3
import json
from pathlib import Path

def normalize_brand_name(device_name: str) -> str:
    """デバイス名から正規化されたブランド名を取得"""
    
    device_lower = device_name.lower()
    
    # iPhone系
    if 'iphone' in device_lower or 'ipad' in device_lower:
        return 'IPHONE'
    
    # Xperia系
    elif 'xperia' in device_lower:
        return 'XPERIA'
    
    # AQUOS系
    elif 'aquos' in device_lower:
        return 'AQUOS'
    
    # Galaxy系
    elif 'galaxy' in device_lower:
        return 'GALAXY'
    
    # Google Pixel系
    elif 'pixel' in device_lower or 'google' in device_lower:
        return 'GOOGLE PIXEL'
    
    # Huawei系
    elif 'huawei' in device_lower or 'nova' in device_lower or 'mate' in device_lower or 'p30' in device_lower or 'p40' in device_lower:
        return 'HUAWEI'
    
    # ARROWS系
    elif 'arrows' in device_lower or 'f-' in device_lower:
        return 'ARROWS'
    
    # OPPO系
    elif 'oppo' in device_lower or 'reno' in device_lower or 'find' in device_lower:
        return 'OPPO'
    
    # Xiaomi系
    elif 'xiaomi' in device_lower or 'redmi' in device_lower or 'mi ' in device_lower:
        return 'XIAOMI'
    
    # OnePlus系
    elif 'oneplus' in device_lower or '1+' in device_lower:
        return 'ONEPLUS'
    
    # ASUS系
    elif 'zenfone' in device_lower or 'asus' in device_lower:
        return 'ASUS'
    
    # Sony系（Xperia以外）
    elif 'sony' in device_lower:
        return 'SONY'
    
    # Samsung系（Galaxy以外）
    elif 'samsung' in device_lower:
        return 'SAMSUNG'
    
    # その他のケース
    else:
        # らくらくフォン、キッズケータイなど
        if 'らくらく' in device_name or 'キッズ' in device_name or 'basio' in device_lower:
            return 'その他'
        
        # デフォルト
        return 'その他'


def update_device_attributes_brands():
    """device_attributesテーブルのブランド名を更新"""
    
    db_path = '/app/product_attributes_new.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 現在のデバイスを取得
        cursor.execute("""
            SELECT id, device_name, brand 
            FROM device_attributes
        """)
        
        devices = cursor.fetchall()
        print(f"Found {len(devices)} devices to update")
        
        # ブランド別の集計
        brand_counts = {}
        updates = []
        
        for device_id, device_name, current_brand in devices:
            normalized_brand = normalize_brand_name(device_name)
            
            if normalized_brand != current_brand:
                updates.append((normalized_brand, device_id))
            
            if normalized_brand not in brand_counts:
                brand_counts[normalized_brand] = 0
            brand_counts[normalized_brand] += 1
        
        # 更新を実行
        if updates:
            print(f"\nUpdating {len(updates)} devices...")
            cursor.executemany("""
                UPDATE device_attributes 
                SET brand = ?, 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, updates)
            conn.commit()
            print(f"Successfully updated {len(updates)} devices")
        else:
            print("No updates needed - all brands are already normalized")
        
        # 統計情報を表示
        print("\n=== Brand Distribution ===")
        for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{brand}: {count}")
        
        # brand_valuesテーブルも確認・作成
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='brand_values'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("\nCreating brand_values table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brand_values (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand_name TEXT NOT NULL,
                    row_index INTEGER NOT NULL,
                    attribute_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("brand_values table created")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_brand_mapping():
    """ブランドマッピング用のJSONファイルを作成"""
    
    brand_mapping = {
        "IPHONE": {
            "variations": ["iPhone", "iPad", "iPod"],
            "attribute_pattern": "amicoco|アップル|",
            "display_name": "iPhone"
        },
        "XPERIA": {
            "variations": ["Xperia"],
            "attribute_pattern": "amicoco|ソニー|",
            "display_name": "Xperia"
        },
        "AQUOS": {
            "variations": ["AQUOS", "sense", "wish", "zero"],
            "attribute_pattern": "amicoco|シャープ|",
            "display_name": "AQUOS"
        },
        "GALAXY": {
            "variations": ["Galaxy", "Note", "Fold", "Flip"],
            "attribute_pattern": "amicoco|サムスン|",
            "display_name": "Galaxy"
        },
        "GOOGLE PIXEL": {
            "variations": ["Pixel", "Nexus"],
            "attribute_pattern": "amicoco|グーグル|",
            "display_name": "Google Pixel"
        },
        "HUAWEI": {
            "variations": ["HUAWEI", "nova", "Mate", "P30", "P40"],
            "attribute_pattern": "amicoco|ファーウェイ|",
            "display_name": "HUAWEI"
        },
        "ARROWS": {
            "variations": ["arrows", "F-41", "F-51", "F-52"],
            "attribute_pattern": "amicoco|富士通|",
            "display_name": "arrows"
        },
        "OPPO": {
            "variations": ["OPPO", "Reno", "Find", "A"],
            "attribute_pattern": "amicoco|オッポ|",
            "display_name": "OPPO"
        },
        "XIAOMI": {
            "variations": ["Xiaomi", "Redmi", "Mi", "POCO"],
            "attribute_pattern": "amicoco|シャオミ|",
            "display_name": "Xiaomi"
        },
        "その他": {
            "variations": ["らくらくフォン", "キッズケータイ", "BASIO", "かんたんスマホ"],
            "attribute_pattern": "amicoco|その他|",
            "display_name": "その他"
        }
    }
    
    # JSONファイルとして保存
    output_path = Path('/app/brand_mapping.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(brand_mapping, f, ensure_ascii=False, indent=2)
    
    print(f"\nBrand mapping saved to {output_path}")
    return brand_mapping


def verify_updates():
    """更新後の確認"""
    
    db_path = '/app/product_attributes_new.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ブランド別の統計
        cursor.execute("""
            SELECT brand, COUNT(*) as count
            FROM device_attributes
            GROUP BY brand
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        
        print("\n=== Final Brand Statistics ===")
        total = 0
        for brand, count in results:
            print(f"{brand}: {count} devices")
            total += count
        
        print(f"\nTotal devices: {total}")
        
        # サンプル表示
        print("\n=== Sample Devices by Brand ===")
        for brand, _ in results[:5]:  # Top 5 brands
            cursor.execute("""
                SELECT device_name, attribute_value
                FROM device_attributes
                WHERE brand = ?
                LIMIT 3
            """, (brand,))
            
            print(f"\n{brand}:")
            for device_name, attr in cursor.fetchall():
                print(f"  - {device_name}: {attr}")
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("="*50)
    print("Brand Normalization and Database Update")
    print("="*50)
    
    # 1. デバイス属性のブランド名を更新
    update_device_attributes_brands()
    
    # 2. ブランドマッピングファイルを作成
    create_brand_mapping()
    
    # 3. 更新結果を確認
    verify_updates()
    
    print("\n✅ Brand update completed successfully!")
    print("="*50)