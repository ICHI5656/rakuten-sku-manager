"""
Supabase client configuration for Rakuten SKU Manager
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.supabase')

# Only import supabase if it's going to be used
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

class SupabaseConnection:
    """Manage Supabase connection and operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.use_supabase = os.getenv('USE_SUPABASE', 'false').lower() == 'true'
        
        if self.use_supabase:
            if not SUPABASE_AVAILABLE:
                print("Warning: USE_SUPABASE is true but supabase package is not available. Falling back to SQLite.")
                self.use_supabase = False
            else:
                url = os.getenv('SUPABASE_URL')
                key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
                
                if not url or not key:
                    print("Warning: Supabase URL and key not provided. Falling back to SQLite.")
                    self.use_supabase = False
                else:
                    try:
                        self.client = create_client(url, key)
                    except Exception as e:
                        print(f"Warning: Failed to create Supabase client: {e}. Falling back to SQLite.")
                        self.use_supabase = False
                        self.client = None
    
    def is_enabled(self) -> bool:
        """Check if Supabase mode is enabled"""
        return self.use_supabase
    
    def get_client(self) -> Optional[Client]:
        """Get Supabase client instance"""
        return self.client
    
    # Brand Attributes Operations
    def get_brands(self):
        """Get all brands from Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('brand_attributes').select('*').order('brand_name').execute()
        return response.data
    
    def get_brand_values(self, brand_name: str):
        """Get brand values from Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('brand_values').select('*').eq('brand_name', brand_name).order('row_index').execute()
        return response.data
    
    def create_brand(self, brand_data: dict):
        """Create a new brand in Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('brand_attributes').insert(brand_data).execute()
        return response.data
    
    def create_brand_value(self, value_data: dict):
        """Create a new brand value in Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('brand_values').insert(value_data).execute()
        return response.data
    
    def update_brand_value(self, value_id: int, update_data: dict):
        """Update a brand value in Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('brand_values').update(update_data).eq('id', value_id).execute()
        return response.data
    
    def delete_brand_value(self, value_id: int):
        """Delete a brand value from Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('brand_values').delete().eq('id', value_id).execute()
        return response.data
    
    # Device Attributes Operations
    def get_devices(self, brand: Optional[str] = None):
        """Get devices from Supabase"""
        if not self.client:
            return None
        
        query = self.client.table('device_attributes').select('*')
        
        if brand:
            query = query.eq('brand', brand)
        
        response = query.order('brand').order('device_name').execute()
        return response.data
    
    def create_device(self, device_data: dict):
        """Create a new device in Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('device_attributes').insert(device_data).execute()
        return response.data
    
    def update_device(self, device_id: int, update_data: dict):
        """Update a device in Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('device_attributes').update(update_data).eq('id', device_id).execute()
        return response.data
    
    def delete_device(self, device_id: int):
        """Delete a device from Supabase"""
        if not self.client:
            return None
        
        response = self.client.table('device_attributes').delete().eq('id', device_id).execute()
        return response.data
    
    def upsert_device(self, device_data: dict):
        """Upsert a device (insert or update based on unique constraint)"""
        if not self.client:
            return None
        
        response = self.client.table('device_attributes').upsert(
            device_data,
            on_conflict='brand,device_name'
        ).execute()
        return response.data
    
    # SKU Counter Operations
    def get_sku_counter(self, product_id: str):
        """Get SKU counter for a product"""
        if not self.client:
            return None
        
        response = self.client.table('sku_counters').select('counter').eq('product_id', product_id).execute()
        
        if response.data:
            return response.data[0]['counter']
        return 0
    
    def update_sku_counter(self, product_id: str, counter: int):
        """Update SKU counter for a product"""
        if not self.client:
            return None
        
        response = self.client.table('sku_counters').upsert({
            'product_id': product_id,
            'counter': counter
        }).execute()
        return response.data
    
    # Database Statistics
    def get_stats(self):
        """Get database statistics"""
        if not self.client:
            return None
        
        # Get brand count
        brand_response = self.client.table('brand_attributes').select('id', count='exact').execute()
        brand_count = brand_response.count or 0
        
        # Get device count
        device_response = self.client.table('device_attributes').select('id', count='exact').execute()
        device_count = device_response.count or 0
        
        # Get brand values count
        values_response = self.client.table('brand_values').select('id', count='exact').execute()
        values_count = values_response.count or 0
        
        return {
            'total_brands': brand_count,
            'total_devices': device_count,
            'total_values': values_count
        }

# Create a singleton instance
supabase_connection = SupabaseConnection()