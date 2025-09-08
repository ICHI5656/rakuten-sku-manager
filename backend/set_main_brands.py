#!/usr/bin/env python3
"""
主要ブランドのみを表示するよう設定
データベース管理ページで表示するブランドを固定
"""
import sqlite3
import json

# UIに表示する主要ブランド（固定）
MAIN_BRANDS = [
    'IPHONE',
    'XPERIA', 
    'AQUOS',
    'GALAXY',
    'GOOGLE PIXEL',
    'HUAWEI',
    'ARROWS',
    'その他'
]

def setup_main_brands():
    """主要ブランドのセットアップ"""
    db_path = '/app/product_attributes_new.db'
    
    print("=" * 50)
    print("主要ブランド設定")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # brands_configテーブルを作成（存在しない場合）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brands_config (
                id INTEGER PRIMARY KEY,
                brand_name TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                display_order INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 既存のブランド設定をクリア
        cursor.execute('DELETE FROM brands_config')
        
        # 主要ブランドを挿入
        for i, brand in enumerate(MAIN_BRANDS):
            cursor.execute('''
                INSERT INTO brands_config (brand_name, display_name, display_order)
                VALUES (?, ?, ?)
            ''', (brand, brand, i + 1))
        
        print(f"✅ {len(MAIN_BRANDS)}個の主要ブランドを設定しました")
        
        # 現在のデバイスを主要ブランドに合わせて整理
        print("\n現在のデバイス分布を確認中...")
        
        # その他以外のブランドを確認
        cursor.execute('''
            SELECT DISTINCT brand 
            FROM device_attributes 
            WHERE brand NOT IN ({})
        '''.format(','.join('?' * len(MAIN_BRANDS))), MAIN_BRANDS)
        
        other_brands = cursor.fetchall()
        
        if other_brands:
            print(f"\n以下のブランドを「その他」に統合します:")
            for (brand,) in other_brands:
                print(f"  - {brand}")
                
            # 「その他」に統合
            cursor.execute('''
                UPDATE device_attributes 
                SET brand = 'その他'
                WHERE brand NOT IN ({})
            '''.format(','.join('?' * len(MAIN_BRANDS))), MAIN_BRANDS)
            
            updated = cursor.rowcount
            print(f"  → {updated}件のデバイスを「その他」に統合しました")
        
        # コミット
        conn.commit()
        
        # 最終統計
        print("\n最終的なブランド分布:")
        print("-" * 40)
        
        cursor.execute('''
            SELECT brand, COUNT(*) as count 
            FROM device_attributes 
            WHERE brand IN ({})
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
        '''.format(','.join('?' * len(MAIN_BRANDS))), MAIN_BRANDS)
        
        total = 0
        for brand, count in cursor.fetchall():
            print(f"  {brand}: {count} devices")
            total += count
        
        print(f"\n合計: {total} devices")
        print("=" * 50)
        
        # 設定ファイルも作成
        config = {
            "main_brands": MAIN_BRANDS,
            "display_settings": {
                "show_only_main": True,
                "allow_custom": False
            }
        }
        
        with open('/app/brand_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("\n✅ ブランド設定が完了しました")
        print("  データベース管理ページには主要ブランドのみが表示されます")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    setup_main_brands()