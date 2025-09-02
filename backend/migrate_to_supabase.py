"""
Migrate existing SQLite data to Supabase
"""
import os
import sqlite3
import json
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

# Load environment variables
load_dotenv('.env.supabase')

def migrate_data():
    """Migrate data from SQLite to Supabase"""
    
    # Connect to Supabase
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("❌ Supabase credentials not found")
        return False
    
    print("🔗 Connecting to Supabase...")
    supabase = create_client(url, key)
    
    # Connect to SQLite
    sqlite_path = '/app/product_attributes_new.db' if os.path.exists('/app/product_attributes_new.db') else 'backend/product_attributes_new.db'
    
    if not os.path.exists(sqlite_path):
        print(f"⚠️ SQLite database not found at {sqlite_path}")
        print("📌 No data to migrate - starting with empty Supabase database")
        return True
    
    print(f"📂 Reading from SQLite: {sqlite_path}")
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Migrate brand_attributes
    print("\n📦 Migrating brand_attributes...")
    try:
        cur.execute("SELECT * FROM brand_attributes")
        brands = cur.fetchall()
        
        for brand in brands:
            brand_data = {
                'brand_name': brand['brand_name'],
                'brand_category': brand['brand_category'] if 'brand_category' in brand.keys() else 'mobile_device'
            }
            try:
                supabase.table('brand_attributes').insert(brand_data).execute()
                print(f"  ✅ {brand['brand_name']}")
            except Exception as e:
                if 'duplicate' in str(e).lower():
                    print(f"  ⏭️ {brand['brand_name']} (already exists)")
                else:
                    print(f"  ❌ {brand['brand_name']}: {e}")
        
        print(f"  📊 Migrated {len(brands)} brands")
    except sqlite3.OperationalError as e:
        print(f"  ⚠️ Table not found in SQLite: {e}")
    
    # Migrate brand_values
    print("\n📦 Migrating brand_values...")
    try:
        cur.execute("SELECT * FROM brand_values")
        values = cur.fetchall()
        
        for value in values:
            value_data = {
                'brand_name': value['brand_name'],
                'row_index': value['row_index'],
                'attribute_value': value['attribute_value']
            }
            try:
                supabase.table('brand_values').insert(value_data).execute()
            except Exception as e:
                if 'duplicate' not in str(e).lower():
                    print(f"  ❌ Error: {e}")
        
        print(f"  📊 Migrated {len(values)} brand values")
    except sqlite3.OperationalError as e:
        print(f"  ⚠️ Table not found in SQLite: {e}")
    
    # Migrate device_attributes
    print("\n📦 Migrating device_attributes...")
    try:
        cur.execute("SELECT * FROM device_attributes")
        devices = cur.fetchall()
        
        for device in devices:
            device_data = {
                'brand': device['brand'],
                'device_name': device['device_name'],
                'attribute_value': device['attribute_value'],
                'size_category': device['size_category'] if 'size_category' in device.keys() else None,
                'usage_count': device['usage_count'] if 'usage_count' in device.keys() else 0
            }
            try:
                supabase.table('device_attributes').insert(device_data).execute()
                print(f"  ✅ {device['device_name']}")
            except Exception as e:
                if 'duplicate' in str(e).lower():
                    print(f"  ⏭️ {device['device_name']} (already exists)")
                else:
                    print(f"  ❌ {device['device_name']}: {e}")
        
        print(f"  📊 Migrated {len(devices)} devices")
    except sqlite3.OperationalError as e:
        print(f"  ⚠️ Table not found in SQLite: {e}")
    
    # Migrate SKU counters from JSON file
    print("\n📦 Migrating SKU counters...")
    sku_file = '/app/data/state/sku_counters.json' if os.path.exists('/app/data/state/sku_counters.json') else 'backend/data/state/sku_counters.json'
    
    if os.path.exists(sku_file):
        with open(sku_file, 'r') as f:
            counters = json.load(f)
        
        for product_id, counter in counters.items():
            counter_data = {
                'product_id': product_id,
                'counter': counter
            }
            try:
                supabase.table('sku_counters').upsert(counter_data).execute()
                print(f"  ✅ {product_id}: {counter}")
            except Exception as e:
                print(f"  ❌ {product_id}: {e}")
        
        print(f"  📊 Migrated {len(counters)} SKU counters")
    else:
        print(f"  ⚠️ SKU counters file not found")
    
    conn.close()
    
    # Get statistics
    print("\n📊 Supabase Database Statistics:")
    try:
        brands_count = supabase.table('brand_attributes').select('id', count='exact').execute()
        devices_count = supabase.table('device_attributes').select('id', count='exact').execute()
        values_count = supabase.table('brand_values').select('id', count='exact').execute()
        counters_count = supabase.table('sku_counters').select('product_id', count='exact').execute()
        
        print(f"  • Brands: {brands_count.count}")
        print(f"  • Devices: {devices_count.count}")
        print(f"  • Brand Values: {values_count.count}")
        print(f"  • SKU Counters: {counters_count.count}")
    except Exception as e:
        print(f"  ❌ Could not get statistics: {e}")
    
    print("\n✅ Migration completed successfully!")
    return True

if __name__ == "__main__":
    migrate_data()