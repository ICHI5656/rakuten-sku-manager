#!/usr/bin/env python3
"""
Create SQLite database from 商品属性(値)8.xlsx
This creates a separate database for product attribute 8 data
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime

def analyze_excel(file_path):
    """Analyze the Excel file structure"""
    print("=" * 50)
    print("Analyzing 商品属性(値)8.xlsx...")
    print("=" * 50)
    
    df = pd.read_excel(file_path)
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    
    # Show column names
    print("\nColumns found:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
        # Show sample data from each column
        non_null = df[col].notna().sum()
        if non_null > 0:
            sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A"
            print(f"     Sample: {str(sample)[:50]}...")
    
    return df

def create_product_attributes_8_database(excel_file, db_path='product_attributes_8.db'):
    """Create SQLite database for product attributes 8"""
    
    print("\n" + "=" * 50)
    print("Creating Product Attributes 8 Database")
    print("=" * 50)
    
    # Read Excel file
    df = pd.read_excel(excel_file)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS product_attributes")
    cursor.execute("DROP TABLE IF EXISTS attribute_values")
    cursor.execute("DROP TABLE IF EXISTS device_mappings")
    
    # Create main product_attributes table
    cursor.execute("""
        CREATE TABLE product_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_type TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create attribute_values table for storing actual values
    cursor.execute("""
        CREATE TABLE attribute_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_type TEXT NOT NULL,
            row_index INTEGER,
            attribute_value TEXT,
            device_name TEXT,
            model_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create device_mappings table for device relationships
    cursor.execute("""
        CREATE TABLE device_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_type TEXT NOT NULL,
            device_name TEXT,
            full_name TEXT,
            model_variants TEXT,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_product_type ON attribute_values(product_type)")
    cursor.execute("CREATE INDEX idx_device_name ON attribute_values(device_name)")
    cursor.execute("CREATE INDEX idx_device_mappings_type ON device_mappings(product_type)")
    
    # Process data
    products_inserted = set()
    values_count = 0
    device_mappings = {}
    
    for col in df.columns:
        # Each column represents a product type (e.g., iphone, galaxy, etc.)
        product_type = col
        
        # Insert product type if not exists
        if product_type not in products_inserted:
            # Determine category based on product name
            category = 'smartphone'
            if 'iphone' in product_type.lower():
                category = 'ios'
            elif 'android' in product_type.lower() or 'galaxy' in product_type.lower():
                category = 'android'
            elif 'huawei' in product_type.lower():
                category = 'huawei'
                
            cursor.execute("""
                INSERT INTO product_attributes (product_type, category)
                VALUES (?, ?)
            """, (product_type, category))
            products_inserted.add(product_type)
        
        # Process each row value for this product type
        for idx, value in enumerate(df[col]):
            if pd.notna(value) and str(value).strip():
                value_str = str(value).strip()
                
                # Try to parse device information from the value
                device_name = None
                model_number = None
                
                # Common patterns in device names
                if '(' in value_str and ')' in value_str:
                    # Extract model number from parentheses
                    parts = value_str.split('(')
                    device_name = parts[0].strip()
                    model_number = parts[1].replace(')', '').strip()
                else:
                    device_name = value_str
                
                # Insert attribute value
                cursor.execute("""
                    INSERT INTO attribute_values 
                    (product_type, row_index, attribute_value, device_name, model_number)
                    VALUES (?, ?, ?, ?, ?)
                """, (product_type, idx, value_str, device_name, model_number))
                values_count += 1
                
                # Track device mappings
                if device_name and device_name not in device_mappings:
                    device_mappings[device_name] = {
                        'product_type': product_type,
                        'full_name': value_str,
                        'model_variants': model_number or ''
                    }
    
    # Insert device mappings
    for device_name, mapping in device_mappings.items():
        cursor.execute("""
            INSERT INTO device_mappings 
            (product_type, device_name, full_name, model_variants)
            VALUES (?, ?, ?, ?)
        """, (
            mapping['product_type'],
            device_name,
            mapping['full_name'],
            mapping['model_variants']
        ))
    
    # Commit changes
    conn.commit()
    
    # Print statistics
    print(f"\n✅ Database created: {db_path}")
    print(f"   - Product types: {len(products_inserted)}")
    print(f"   - Total values: {values_count}")
    print(f"   - Device mappings: {len(device_mappings)}")
    
    # Show sample data
    print("\n" + "=" * 50)
    print("Sample Data")
    print("=" * 50)
    
    # Sample product types
    cursor.execute("""
        SELECT product_type, COUNT(*) as value_count
        FROM attribute_values
        GROUP BY product_type
        LIMIT 5
    """)
    
    print("\nProduct types and their value counts:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} values")
    
    # Sample attribute values
    cursor.execute("""
        SELECT product_type, attribute_value, device_name, model_number
        FROM attribute_values
        WHERE device_name IS NOT NULL
        LIMIT 5
    """)
    
    print("\nSample device entries:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
        if row[3]:  # If model_number exists
            print(f"    Device: {row[2]} | Model: {row[3]}")
    
    # Sample device mappings
    cursor.execute("""
        SELECT device_name, full_name, model_variants
        FROM device_mappings
        LIMIT 5
    """)
    
    print("\nDevice mappings:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
        if row[2]:
            print(f"    Variants: {row[2]}")
    
    conn.close()
    
    return db_path

def create_views_and_queries(db_path):
    """Create useful views for the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a view for device statistics
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS device_statistics AS
        SELECT 
            product_type,
            COUNT(DISTINCT device_name) as unique_devices,
            COUNT(*) as total_entries
        FROM attribute_values
        WHERE device_name IS NOT NULL
        GROUP BY product_type
    """)
    
    # Create a view for popular devices
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS popular_devices AS
        SELECT 
            device_name,
            COUNT(*) as usage_count,
            GROUP_CONCAT(DISTINCT product_type) as used_in_products
        FROM attribute_values
        WHERE device_name IS NOT NULL
        GROUP BY device_name
        ORDER BY usage_count DESC
    """)
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("Database Views Created")
    print("=" * 50)
    print("  - device_statistics: Statistics per product type")
    print("  - popular_devices: Most commonly used devices")

def main():
    """Main function"""
    excel_file = 'product_attributes_8.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"Error: File '{excel_file}' not found")
        print("Please ensure the Excel file is in the current directory")
        return
    
    # Analyze Excel file
    df = analyze_excel(excel_file)
    
    # Create database
    db_path = create_product_attributes_8_database(excel_file)
    
    # Create views
    create_views_and_queries(db_path)
    
    print("\n" + "=" * 50)
    print("Database Ready!")
    print("=" * 50)
    print(f"\nDatabase file: {db_path}")
    print("\nYou can query it using:")
    print("  sqlite3 product_attributes_8.db")
    print("\nExample SQL queries:")
    print("  SELECT * FROM product_attributes;")
    print("  SELECT * FROM attribute_values WHERE product_type = 'iPhone 15 Pro';")
    print("  SELECT * FROM device_mappings;")
    print("  SELECT * FROM device_statistics;")
    print("  SELECT * FROM popular_devices LIMIT 10;")

if __name__ == "__main__":
    main()