#!/usr/bin/env python3
"""
Create SQLite database from 商品属性.xlsx (Product Attributes Excel file)
"""

import pandas as pd
import sqlite3
import json
from datetime import datetime
import os

def analyze_excel(file_path):
    """Analyze Excel file structure"""
    print("=" * 50)
    print("Analyzing Excel file...")
    print("=" * 50)
    
    df = pd.read_excel(file_path)
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    
    # Find key columns
    key_columns = {}
    for col in df.columns:
        if '商品管理番号' in col:
            key_columns['product_id'] = col
        elif 'SKU管理番号' in col:
            key_columns['sku_id'] = col
        elif '商品名' in col:
            key_columns['product_name'] = col
        elif 'バリエーション項目選択肢1' in col:
            key_columns['variation1_choice'] = col
        elif 'バリエーション項目選択肢2' in col:
            key_columns['variation2_choice'] = col
        elif 'バリエーション1選択肢定義' in col:
            key_columns['variation1_def'] = col
        elif 'バリエーション2選択肢定義' in col:
            key_columns['variation2_def'] = col
        elif '販売価格' in col and 'SKU' not in col:
            key_columns['price'] = col
        elif '在庫数' in col:
            key_columns['stock'] = col
        elif '商品属性（値）8' in col:
            key_columns['attribute8'] = col
    
    print("\nKey columns found:")
    for key, col_name in key_columns.items():
        print(f"  {key}: {col_name}")
    
    return df, key_columns

def create_database(df, key_columns, db_path='rakuten_products.db'):
    """Create SQLite database from DataFrame"""
    print("\n" + "=" * 50)
    print(f"Creating database: {db_path}")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS skus")
    cursor.execute("DROP TABLE IF EXISTS variations")
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            variation1_definition TEXT,
            variation2_definition TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create SKUs table
    cursor.execute("""
        CREATE TABLE skus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            sku_id TEXT UNIQUE,
            variation1_choice TEXT,
            variation2_choice TEXT,
            price REAL,
            stock INTEGER,
            attribute8 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    
    # Create variations table (for tracking device lists)
    cursor.execute("""
        CREATE TABLE variations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            variation_type TEXT,  -- 'variation1' or 'variation2'
            variation_value TEXT,
            position INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_skus_product_id ON skus(product_id)")
    cursor.execute("CREATE INDEX idx_variations_product_id ON variations(product_id)")
    
    # Process data
    product_col = key_columns.get('product_id')
    sku_col = key_columns.get('sku_id')
    
    if not product_col or not sku_col:
        print("Error: Required columns not found")
        return
    
    # Group by product
    products_data = []
    skus_data = []
    variations_data = []
    
    current_product = None
    for idx, row in df.iterrows():
        product_id = row.get(product_col)
        sku_id = row.get(sku_col)
        
        # Check if this is a parent row (product without SKU)
        if pd.notna(product_id) and pd.isna(sku_id):
            # This is a product parent row
            current_product = product_id
            product_data = {
                'product_id': product_id,
                'product_name': row.get(key_columns.get('product_name', ''), ''),
                'variation1_definition': row.get(key_columns.get('variation1_def', ''), ''),
                'variation2_definition': row.get(key_columns.get('variation2_def', ''), '')
            }
            products_data.append(product_data)
            
            # Parse variation definitions
            var2_def = row.get(key_columns.get('variation2_def', ''), '')
            if pd.notna(var2_def) and var2_def:
                devices = str(var2_def).split('|')
                for pos, device in enumerate(devices):
                    if device.strip():
                        variations_data.append({
                            'product_id': product_id,
                            'variation_type': 'variation2',
                            'variation_value': device.strip(),
                            'position': pos
                        })
        
        # Check if this is a SKU row
        elif pd.notna(sku_id) and current_product:
            sku_data = {
                'product_id': current_product,
                'sku_id': sku_id,
                'variation1_choice': row.get(key_columns.get('variation1_choice', ''), ''),
                'variation2_choice': row.get(key_columns.get('variation2_choice', ''), ''),
                'price': row.get(key_columns.get('price', ''), None),
                'stock': row.get(key_columns.get('stock', ''), None),
                'attribute8': row.get(key_columns.get('attribute8', ''), '')
            }
            skus_data.append(sku_data)
    
    # Insert data into database
    print(f"\nInserting {len(products_data)} products...")
    for product in products_data:
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (product_id, product_name, variation1_definition, variation2_definition)
            VALUES (?, ?, ?, ?)
        """, (
            product['product_id'],
            product['product_name'],
            product['variation1_definition'],
            product['variation2_definition']
        ))
    
    print(f"Inserting {len(skus_data)} SKUs...")
    for sku in skus_data:
        cursor.execute("""
            INSERT OR REPLACE INTO skus 
            (product_id, sku_id, variation1_choice, variation2_choice, price, stock, attribute8)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            sku['product_id'],
            sku['sku_id'],
            sku['variation1_choice'],
            sku['variation2_choice'],
            sku['price'],
            sku['stock'],
            sku['attribute8']
        ))
    
    print(f"Inserting {len(variations_data)} variation values...")
    for var in variations_data:
        cursor.execute("""
            INSERT INTO variations 
            (product_id, variation_type, variation_value, position)
            VALUES (?, ?, ?, ?)
        """, (
            var['product_id'],
            var['variation_type'],
            var['variation_value'],
            var['position']
        ))
    
    # Commit and close
    conn.commit()
    
    # Print statistics
    print("\n" + "=" * 50)
    print("Database created successfully!")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM products")
    print(f"Total products: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM skus")
    print(f"Total SKUs: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM variations")
    print(f"Total variation values: {cursor.fetchone()[0]}")
    
    # Sample query
    print("\n" + "=" * 50)
    print("Sample query - First 3 products with device counts:")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            COUNT(DISTINCT s.sku_id) as sku_count,
            COUNT(DISTINCT v.variation_value) as device_count
        FROM products p
        LEFT JOIN skus s ON p.product_id = s.product_id
        LEFT JOIN variations v ON p.product_id = v.product_id AND v.variation_type = 'variation2'
        GROUP BY p.product_id
        LIMIT 3
    """)
    
    for row in cursor.fetchall():
        print(f"Product: {row[0]}")
        print(f"  Name: {row[1]}")
        print(f"  SKUs: {row[2]}")
        print(f"  Devices: {row[3]}")
        print()
    
    conn.close()
    print("Database connection closed.")
    return db_path

def main():
    """Main function"""
    excel_file = 'product_attributes.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"Error: File '{excel_file}' not found")
        print("Please ensure the Excel file is in the current directory")
        return
    
    # Analyze Excel file
    df, key_columns = analyze_excel(excel_file)
    
    # Create database
    db_path = create_database(df, key_columns)
    
    if db_path:
        print(f"\n✅ Database created: {db_path}")
        print("\nYou can now query the database using SQLite commands or any SQLite client.")
        print("\nExample queries:")
        print("  - SELECT * FROM products LIMIT 5;")
        print("  - SELECT * FROM skus WHERE product_id = 'kaiser_huawei';")
        print("  - SELECT * FROM variations WHERE variation_type = 'variation2';")

if __name__ == "__main__":
    main()