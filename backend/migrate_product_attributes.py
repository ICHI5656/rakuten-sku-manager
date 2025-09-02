#!/usr/bin/env python3
"""
商品属性8データベース移行スクリプト
新しいスキーマ: 機種ブランド別管理
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os
import shutil
import chardet

# データベースパス
OLD_DB_PATH = "product_attributes_new.db"
NEW_DB_PATH = "product_attributes_v2.db"
BACKUP_PATH = f"product_attributes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def detect_encoding(file_path):
    """ファイルのエンコーディングを検出"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def create_new_schema(conn):
    """新しいデータベーススキーマを作成"""
    cursor = conn.cursor()
    
    # 新しいテーブル構造
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,           -- ブランド名 (iPhone, Xperia, AQUOS, Galaxy, Google Pixel, HUAWEI, arrows, その他)
            device_name TEXT NOT NULL,      -- デバイス名 (variation_item_choice_2)
            attribute_value TEXT NOT NULL,  -- 属性値 (product_attribute_8)
            size_category TEXT NOT NULL,    -- サイズカテゴリ
            usage_count INTEGER DEFAULT 0,  -- 使用回数
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(brand, device_name, size_category)
        )
    """)
    
    # ブランドマスターテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT UNIQUE NOT NULL,
            brand_name_jp TEXT,             -- 日本語ブランド名
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # インデックスの作成
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_brand ON device_attributes(brand)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_device ON device_attributes(device_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_size ON device_attributes(size_category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_brand_device ON device_attributes(brand, device_name)")
    
    conn.commit()

def determine_brand(device_name, attribute_value):
    """デバイス名と属性値からブランドを判定"""
    device_lower = device_name.lower() if device_name else ""
    attr_lower = attribute_value.lower() if attribute_value else ""
    
    # ブランド判定ロジック
    if 'iphone' in device_lower or 'iphone' in attr_lower:
        return 'iPhone'
    elif 'xperia' in device_lower or 'xperia' in attr_lower or device_lower.startswith('so-'):
        return 'Xperia'
    elif 'aquos' in device_lower or 'aquos' in attr_lower or device_lower.startswith('sh-'):
        return 'AQUOS'
    elif 'galaxy' in device_lower or 'galaxy' in attr_lower or device_lower.startswith('sc-') or device_lower.startswith('scg'):
        return 'Galaxy'
    elif 'pixel' in device_lower or 'pixel' in attr_lower:
        return 'Google Pixel'
    elif 'huawei' in device_lower or 'huawei' in attr_lower or 'mate' in device_lower or 'nova' in device_lower:
        return 'HUAWEI'
    elif 'arrows' in device_lower or 'arrows' in attr_lower or device_lower.startswith('f-'):
        return 'arrows'
    else:
        return 'その他'

def insert_default_brands(conn):
    """デフォルトのブランドデータを挿入"""
    cursor = conn.cursor()
    
    brands = [
        ('iPhone', 'iPhone', 1),
        ('Xperia', 'Xperia', 2),
        ('AQUOS', 'AQUOS', 3),
        ('Galaxy', 'Galaxy', 4),
        ('Google Pixel', 'Google Pixel', 5),
        ('HUAWEI', 'HUAWEI', 6),
        ('arrows', 'arrows', 7),
        ('その他', 'その他', 99)
    ]
    
    for brand_name, brand_name_jp, order in brands:
        cursor.execute("""
            INSERT OR IGNORE INTO brands (brand_name, brand_name_jp, display_order) 
            VALUES (?, ?, ?)
        """, (brand_name, brand_name_jp, order))
    
    conn.commit()

def migrate_from_old_db(old_conn, new_conn):
    """旧データベースから新データベースへ移行"""
    cursor_old = old_conn.cursor()
    cursor_new = new_conn.cursor()
    
    # 既存のproduct_devicesテーブルからデータを取得
    cursor_old.execute("""
        SELECT size_category, variation_item_choice_2, product_attribute_8 
        FROM product_devices
    """)
    
    devices = cursor_old.fetchall()
    
    for size, device_name, attribute in devices:
        if device_name and attribute:
            brand = determine_brand(device_name, attribute)
            
            cursor_new.execute("""
                INSERT OR REPLACE INTO device_attributes 
                (brand, device_name, attribute_value, size_category, usage_count)
                VALUES (?, ?, ?, ?, 0)
            """, (brand, device_name, attribute, size or ''))
    
    # attribute_mappingsテーブルからも移行（もし存在すれば）
    try:
        cursor_old.execute("""
            SELECT device_name, attribute_value, size_category, usage_count 
            FROM attribute_mappings
        """)
        
        mappings = cursor_old.fetchall()
        
        for device_name, attribute, size, usage in mappings:
            if device_name and attribute:
                brand = determine_brand(device_name, attribute)
                
                cursor_new.execute("""
                    UPDATE device_attributes 
                    SET usage_count = ?
                    WHERE brand = ? AND device_name = ? AND size_category = ?
                """, (usage or 0, brand, device_name, size or ''))
    except:
        pass
    
    new_conn.commit()

def import_csv_data(csv_path, conn):
    """CSVファイルからデータをインポート"""
    # エンコーディングを検出
    encoding = detect_encoding(csv_path)
    if encoding is None:
        encoding = 'shift-jis'
    
    # CSVを読み込み（複雑な構造に対応）
    df = pd.read_csv(csv_path, encoding=encoding, header=None)
    
    cursor = conn.cursor()
    
    # CSVの構造を解析（ブランドごとのカラムグループ）
    brand_columns = {
        'iPhone': (0, 1, 2),
        'Xperia': (5, 6, 7),
        'AQUOS': (10, 11, 12),
        'Galaxy': (15, 16, 17),
        'Google Pixel': (19, 20, 21),
        'HUAWEI': (23, 24, 25),
        'arrows': (27, 28, 29)
    }
    
    for brand, (size_col, device_col, attr_col) in brand_columns.items():
        # ヘッダー行をスキップ（最初の2行）
        for idx in range(2, len(df)):
            try:
                size_category = df.iloc[idx, size_col] if pd.notna(df.iloc[idx, size_col]) else ''
                device_name = df.iloc[idx, device_col] if pd.notna(df.iloc[idx, device_col]) else ''
                attribute_value = df.iloc[idx, attr_col] if pd.notna(df.iloc[idx, attr_col]) else ''
                
                if device_name and attribute_value:
                    # サイズカテゴリのクリーニング
                    if isinstance(size_category, str):
                        size_category = size_category.strip('[]')
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO device_attributes 
                        (brand, device_name, attribute_value, size_category, usage_count)
                        VALUES (?, ?, ?, ?, 0)
                    """, (brand, device_name.strip(), attribute_value.strip(), size_category))
            except:
                continue
    
    conn.commit()
    print(f"CSVデータをインポートしました: {csv_path}")

def main():
    """メイン処理"""
    print("商品属性8データベース移行を開始します...")
    
    # バックアップを作成
    if os.path.exists(OLD_DB_PATH):
        shutil.copy2(OLD_DB_PATH, BACKUP_PATH)
        print(f"バックアップを作成しました: {BACKUP_PATH}")
    
    # 新しいデータベースを作成
    new_conn = sqlite3.connect(NEW_DB_PATH)
    create_new_schema(new_conn)
    insert_default_brands(new_conn)
    
    # 旧データベースからデータを移行（存在する場合）
    if os.path.exists(OLD_DB_PATH):
        old_conn = sqlite3.connect(OLD_DB_PATH)
        migrate_from_old_db(old_conn, new_conn)
        old_conn.close()
        print("既存データベースからデータを移行しました")
    
    # CSVファイルからデータをインポート（存在する場合）
    csv_path = "/app/商品属性8.csv"
    if os.path.exists(csv_path):
        import_csv_data(csv_path, new_conn)
    
    # 統計情報を表示
    cursor = new_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM device_attributes")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT brand, COUNT(*) FROM device_attributes GROUP BY brand ORDER BY COUNT(*) DESC")
    brand_stats = cursor.fetchall()
    
    print(f"\n移行完了:")
    print(f"総デバイス数: {total}")
    print("\nブランド別統計:")
    for brand, count in brand_stats:
        print(f"  {brand}: {count}")
    
    new_conn.close()
    print(f"\n新しいデータベースを作成しました: {NEW_DB_PATH}")
    
    # 新しいDBを本番用にコピー
    shutil.copy2(NEW_DB_PATH, "product_attributes_new.db")
    print("product_attributes_new.dbを更新しました")

if __name__ == "__main__":
    main()