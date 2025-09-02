"""
Create tables in Supabase using the Supabase client
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import time

# Load environment variables
load_dotenv('.env.supabase')

def create_tables():
    """Create all necessary tables in Supabase"""
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("❌ Supabase credentials not found")
        return False
    
    print(f"🔗 Connecting to Supabase...")
    client = create_client(url, key)
    
    # Read SQL migration file
    migration_file = '/app/001_create_tables.sql' if os.path.exists('/app/001_create_tables.sql') else '001_create_tables.sql'
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    with open(migration_file, 'r') as f:
        sql_content = f.read()
    
    print("\n📝 Creating tables in Supabase...")
    print("⚠️  Note: This script can't execute raw SQL directly.")
    print("📌 Please run the SQL migration manually in Supabase Dashboard:")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Select your project")
    print("   3. Go to SQL Editor")
    print("   4. Paste and run the following SQL:\n")
    print("=" * 80)
    print(sql_content[:500] + "..." if len(sql_content) > 500 else sql_content)
    print("=" * 80)
    print("\n✨ After running the SQL, the following tables will be created:")
    print("   - brand_attributes")
    print("   - brand_values")
    print("   - device_attributes")
    print("   - sku_counters")
    
    return True

if __name__ == "__main__":
    create_tables()