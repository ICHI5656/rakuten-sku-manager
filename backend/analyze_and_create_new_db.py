#!/usr/bin/env python3
"""
Create new SQLite database from データ.xlsx with Size-Device-Attribute structure
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
import json

def analyze_excel(file_path):
    """Analyze the Excel file structure"""
    print("=" * 60)
    print("Analyzing データ.xlsx...")
    print("=" * 60)
    
    # Read all sheets
    xl_file = pd.ExcelFile(file_path)
    print(f"Found {len(xl_file.sheet_names)} sheets: {xl_file.sheet_names}")
    
    all_data = []
    
    for sheet_name in xl_file.sheet_names:
        print(f"\n--- Sheet: {sheet_name} ---")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
        print(f"Columns: {list(df.columns)}")
        
        # Show first few rows
        if not df.empty:
            print("\nFirst 3 rows:")
            print(df.head(3).to_string())
            
        # Collect data for database
        for _, row in df.iterrows():
            all_data.append({
                'sheet': sheet_name,
                'data': row.to_dict()
            })
    
    return all_data

def create_product_attributes_database(excel_file, db_path='product_attributes_new.db'):
    """Create new SQLite database with Size-Device-Attribute structure"""
    
    print("\n" + "=" * 60)
    print("Creating New Product Attributes Database")
    print("=" * 60)
    
    # Read Excel file
    xl_file = pd.ExcelFile(excel_file)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS product_devices")
    cursor.execute("DROP TABLE IF EXISTS size_categories")
    cursor.execute("DROP TABLE IF EXISTS attribute_mappings")
    
    # Create main product_devices table
    cursor.execute("""
        CREATE TABLE product_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size_category TEXT NOT NULL,
            variation_item_choice_2 TEXT NOT NULL,  -- バリエーション項目選択肢2
            product_attribute_8 TEXT NOT NULL,       -- 商品属性（値）8
            sheet_name TEXT,
            row_index INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(size_category, variation_item_choice_2)
        )
    """)
    
    # Create size_categories table for tracking unique sizes
    cursor.execute("""
        CREATE TABLE size_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size_name TEXT UNIQUE NOT NULL,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create attribute_mappings table for device-to-attribute relationships
    cursor.execute("""
        CREATE TABLE attribute_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_name TEXT NOT NULL,
            attribute_value TEXT NOT NULL,
            size_category TEXT,
            usage_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX idx_size ON product_devices(size_category)")
    cursor.execute("CREATE INDEX idx_variation ON product_devices(variation_item_choice_2)")
    cursor.execute("CREATE INDEX idx_attribute ON product_devices(product_attribute_8)")
    cursor.execute("CREATE INDEX idx_device_name ON attribute_mappings(device_name)")
    cursor.execute("CREATE INDEX idx_size_category ON attribute_mappings(size_category)")
    
    # Process data from all sheets
    devices_inserted = 0
    sizes_set = set()
    attribute_mappings = {}
    
    for sheet_name in xl_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"\nProcessing sheet: {sheet_name}")
        
        # Find all column groups (size, variation, attribute)
        column_groups = []
        
        # Group columns - each group has サイズ, バリエーション項目選択肢2, 商品属性（値）8
        size_cols = []
        variation_cols = []
        attribute_cols = []
        
        for col in df.columns:
            if 'サイズ' in str(col):
                size_cols.append(col)
            elif 'バリエーション項目選択肢2' in str(col):
                variation_cols.append(col)
            elif '商品属性' in str(col) and '8' in str(col):
                attribute_cols.append(col)
        
        # Create column groups
        for i in range(min(len(size_cols), len(variation_cols), len(attribute_cols))):
            column_groups.append({
                'size': size_cols[i],
                'variation': variation_cols[i],
                'attribute': attribute_cols[i]
            })
        
        print(f"  Found {len(column_groups)} column groups")
        
        # Process each column group
        for group_idx, group in enumerate(column_groups):
            print(f"  Processing column group {group_idx + 1}: {group['size'][:20]}")
            
            # Process rows for this column group
            for idx, row in df.iterrows():
                size_value = row.get(group['size'])
                variation_value = row.get(group['variation'])
                attribute_value = row.get(group['attribute'])
                
                # Skip empty rows
                if pd.isna(size_value) or pd.isna(variation_value) or pd.isna(attribute_value):
                    continue
                
                size_str = str(size_value).strip()
                variation_str = str(variation_value).strip()
                attribute_str = str(attribute_value).strip()
                
                # Skip if any field is empty
                if not all([size_str, variation_str, attribute_str]):
                    continue
                
                try:
                    # Insert into product_devices
                    cursor.execute("""
                        INSERT OR REPLACE INTO product_devices 
                        (size_category, variation_item_choice_2, product_attribute_8, sheet_name, row_index)
                        VALUES (?, ?, ?, ?, ?)
                    """, (size_str, variation_str, attribute_str, f"{sheet_name}_group{group_idx}", idx))
                    devices_inserted += 1
                    
                    # Track sizes
                    sizes_set.add(size_str)
                    
                    # Track attribute mappings
                    mapping_key = f"{variation_str}|{size_str}"
                    if mapping_key not in attribute_mappings:
                        attribute_mappings[mapping_key] = {
                            'device': variation_str,
                            'attribute': attribute_str,
                            'size': size_str,
                            'count': 0
                        }
                    attribute_mappings[mapping_key]['count'] += 1
                    
                except sqlite3.IntegrityError as e:
                    print(f"    Duplicate entry skipped: {variation_str} for size {size_str}")
    
    # Insert size categories
    size_order = {
        'S': 1, 'M': 2, 'L': 3, 'LL': 4, '2L': 5, '3L': 6, '4L': 7,
        'XS': 0, 'XL': 5, 'XXL': 6, 'XXXL': 7
    }
    
    for size in sorted(sizes_set):
        order = size_order.get(size.upper(), 99)
        cursor.execute("""
            INSERT OR IGNORE INTO size_categories (size_name, display_order)
            VALUES (?, ?)
        """, (size, order))
    
    # Insert attribute mappings
    for mapping in attribute_mappings.values():
        cursor.execute("""
            INSERT INTO attribute_mappings 
            (device_name, attribute_value, size_category, usage_count)
            VALUES (?, ?, ?, ?)
        """, (mapping['device'], mapping['attribute'], mapping['size'], mapping['count']))
    
    # Commit changes
    conn.commit()
    
    # Print statistics
    print(f"\n✅ Database created: {db_path}")
    print(f"   - Total devices inserted: {devices_inserted}")
    print(f"   - Unique size categories: {len(sizes_set)}")
    print(f"   - Attribute mappings: {len(attribute_mappings)}")
    
    # Show sample data
    print("\n" + "=" * 60)
    print("Sample Data")
    print("=" * 60)
    
    # Sample size categories
    cursor.execute("""
        SELECT size_name, display_order 
        FROM size_categories 
        ORDER BY display_order
        LIMIT 10
    """)
    
    print("\nSize categories:")
    for row in cursor.fetchall():
        print(f"  {row[0]} (order: {row[1]})")
    
    # Sample devices by size
    cursor.execute("""
        SELECT size_category, COUNT(*) as device_count
        FROM product_devices
        GROUP BY size_category
        ORDER BY size_category
    """)
    
    print("\nDevices per size:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} devices")
    
    # Sample device entries
    cursor.execute("""
        SELECT size_category, variation_item_choice_2, product_attribute_8
        FROM product_devices
        LIMIT 5
    """)
    
    print("\nSample device entries:")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} -> {row[2]}")
    
    conn.close()
    
    return db_path

def create_views_and_queries(db_path):
    """Create useful views for the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a view for device by size statistics
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS devices_by_size AS
        SELECT 
            size_category,
            COUNT(DISTINCT variation_item_choice_2) as unique_devices,
            COUNT(*) as total_entries
        FROM product_devices
        GROUP BY size_category
        ORDER BY 
            CASE size_category
                WHEN 'XS' THEN 0
                WHEN 'S' THEN 1
                WHEN 'M' THEN 2
                WHEN 'L' THEN 3
                WHEN 'LL' THEN 4
                WHEN '2L' THEN 5
                WHEN '3L' THEN 6
                WHEN '4L' THEN 7
                ELSE 99
            END
    """)
    
    # Create a view for device popularity
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS device_popularity AS
        SELECT 
            variation_item_choice_2 as device_name,
            COUNT(DISTINCT size_category) as available_sizes,
            GROUP_CONCAT(DISTINCT size_category) as size_list
        FROM product_devices
        GROUP BY variation_item_choice_2
        ORDER BY available_sizes DESC
    """)
    
    # Create a view for complete device-attribute mapping
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS device_attribute_view AS
        SELECT 
            pd.size_category,
            pd.variation_item_choice_2 as device_name,
            pd.product_attribute_8 as attribute_value,
            sc.display_order as size_order
        FROM product_devices pd
        LEFT JOIN size_categories sc ON pd.size_category = sc.size_name
        ORDER BY sc.display_order, pd.variation_item_choice_2
    """)
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("Database Views Created")
    print("=" * 60)
    print("  - devices_by_size: Device count per size category")
    print("  - device_popularity: Devices ranked by size availability")
    print("  - device_attribute_view: Complete mapping with size ordering")

def main():
    """Main function"""
    excel_file = 'data.xlsx'
    
    # Try to find the file in different locations
    possible_paths = [
        excel_file,
        'data.xlsx',
        '/app/data.xlsx',
        '/mnt/wsl/docker-desktop-bind-mounts/Ubuntu/f70584b20d3b11017f9f892bc2e4ad99e1e36280fd68546c36b64c78d6f83434/データ.xlsx'
    ]
    
    found_file = None
    for path in possible_paths:
        if os.path.exists(path):
            found_file = path
            print(f"Found Excel file at: {path}")
            break
    
    if not found_file:
        print("Error: Could not find data.xlsx")
        print("Tried the following paths:")
        for path in possible_paths:
            print(f"  - {path}")
        return
    
    # Analyze Excel file
    data = analyze_excel(found_file)
    
    # Create database
    db_path = create_product_attributes_database(found_file)
    
    # Create views
    create_views_and_queries(db_path)
    
    print("\n" + "=" * 60)
    print("Database Ready!")
    print("=" * 60)
    print(f"\nDatabase file: {db_path}")
    print("\nYou can query it using:")
    print("  sqlite3 product_attributes_new.db")
    print("\nExample SQL queries:")
    print("  -- Get all devices for size L:")
    print("  SELECT * FROM product_devices WHERE size_category = 'L';")
    print("\n  -- Get device count by size:")
    print("  SELECT * FROM devices_by_size;")
    print("\n  -- Get most popular devices:")
    print("  SELECT * FROM device_popularity LIMIT 10;")
    print("\n  -- Get complete mapping:")
    print("  SELECT * FROM device_attribute_view WHERE size_category = 'M';")

if __name__ == "__main__":
    main()