"""
Test Supabase connection and verify tables
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv('.env.supabase')

def test_connection():
    """Test Supabase connection"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("❌ Supabase credentials not found in .env.supabase")
        return False
    
    print(f"🔗 Connecting to Supabase...")
    print(f"   URL: {url}")
    
    try:
        client = create_client(url, key)
        
        # Test connection by fetching tables
        print("\n📊 Testing database connection...")
        
        # Try to query a simple table
        response = client.table('brand_attributes').select('*').limit(1).execute()
        print("✅ Successfully connected to Supabase!")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n💡 Please ensure:")
        print("   1. Tables are created in Supabase (run migrations)")
        print("   2. Credentials are correct in .env.supabase")
        print("   3. Row Level Security (RLS) is properly configured")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)