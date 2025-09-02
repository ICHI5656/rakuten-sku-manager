#!/usr/bin/env python3
"""
Create SQLite database from brand attributes Excel file
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime

def create_brand_database(excel_file, db_path='brand_attributes.db'):
    """Create SQLite database from brand attributes Excel"""
    
    print("=" * 50)
    print("Creating Brand Attributes Database")
    print("=" * 50)
    
    # Read Excel file
    df = pd.read_excel(excel_file)
    print(f"Excel shape: {df.shape[0]} rows x {df.shape[1]} columns")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS brand_attributes")
    cursor.execute("DROP TABLE IF EXISTS brand_values")
    
    # Create brand_attributes table
    cursor.execute("""
        CREATE TABLE brand_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL,
            brand_category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create brand_values table
    cursor.execute("""
        CREATE TABLE brand_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL,
            row_index INTEGER,
            attribute_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_brand_name ON brand_attributes(brand_name)")
    cursor.execute("CREATE INDEX idx_brand_values_name ON brand_values(brand_name)")
    
    # Process data
    brands_inserted = set()
    values_count = 0
    
    for col in df.columns:
        # Extract brand name from column (e.g., "ブランド名(iphone)" -> "iphone")
        if 'ブランド名' in col:
            brand_name = col.replace('ブランド名(', '').replace(')', '')
            
            # Insert brand if not exists
            if brand_name not in brands_inserted:
                cursor.execute("""
                    INSERT INTO brand_attributes (brand_name, brand_category)
                    VALUES (?, ?)
                """, (brand_name, 'mobile_device'))
                brands_inserted.add(brand_name)
            
            # Insert all values for this brand
            for idx, value in enumerate(df[col]):
                if pd.notna(value) and str(value).strip():
                    cursor.execute("""
                        INSERT INTO brand_values (brand_name, row_index, attribute_value)
                        VALUES (?, ?, ?)
                    """, (brand_name, idx, str(value)))
                    values_count += 1
    
    # Commit changes
    conn.commit()
    
    # Print statistics
    print(f"\n✅ Database created: {db_path}")
    print(f"   - Brands inserted: {len(brands_inserted)}")
    print(f"   - Total values: {values_count}")
    
    # Show sample data
    print("\n" + "=" * 50)
    print("Sample Data")
    print("=" * 50)
    
    cursor.execute("""
        SELECT brand_name, COUNT(*) as value_count
        FROM brand_values
        GROUP BY brand_name
        LIMIT 5
    """)
    
    print("\nValues per brand (first 5):")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} values")
    
    cursor.execute("""
        SELECT brand_name, attribute_value
        FROM brand_values
        WHERE row_index = 1
        LIMIT 5
    """)
    
    print("\nSample attribute values (row 1):")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    conn.close()
    
    return db_path

def query_examples(db_path):
    """Show example queries"""
    print("\n" + "=" * 50)
    print("Example Queries")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Example 1: Get all brands
    print("\n1. All brands:")
    cursor.execute("SELECT brand_name FROM brand_attributes ORDER BY brand_name")
    brands = [row[0] for row in cursor.fetchall()]
    print("   " + ", ".join(brands))
    
    # Example 2: Get values for a specific brand
    print("\n2. Values for 'iphone' brand:")
    cursor.execute("""
        SELECT row_index, attribute_value 
        FROM brand_values 
        WHERE brand_name = 'iphone' 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   Row {row[0]}: {row[1]}")
    
    conn.close()

def main():
    """Main function"""
    excel_file = 'product_attributes.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"Error: File '{excel_file}' not found")
        return
    
    # Create database
    db_path = create_brand_database(excel_file)
    
    # Show example queries
    query_examples(db_path)
    
    print("\n" + "=" * 50)
    print("Database Ready!")
    print("=" * 50)
    print(f"\nDatabase file: {db_path}")
    print("\nYou can query it using:")
    print("  sqlite3 brand_attributes.db")
    print("\nExample SQL commands:")
    print("  .tables")
    print("  SELECT * FROM brand_attributes;")
    print("  SELECT * FROM brand_values WHERE brand_name = 'iphone';")

if __name__ == "__main__":
    main()