import json
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import threading
import logging

logger = logging.getLogger(__name__)

class SKUManager:
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.counters = self._load_state()
        self.lock = threading.Lock()
    
    def _load_state(self) -> Dict[str, int]:
        """Load SKU counters from state file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse SKU state file: {e}")
                return {}
            except IOError as e:
                logger.error(f"Failed to read SKU state file: {e}")
                return {}
        return {}
    
    def save_state(self):
        """Save SKU counters to state file"""
        with self.lock:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.counters, f, ensure_ascii=False, indent=2)
    
    def get_next_sku(self, product_id: str) -> str:
        """Get next SKU number for a product"""
        with self.lock:
            if product_id not in self.counters:
                self.counters[product_id] = 0
            
            self.counters[product_id] += 1
            sku_number = self.counters[product_id]
            
            # Format: sku_r000001
            return f"sku_r{sku_number:06d}"
    
    def generate_skus(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate SKUs for all rows in DataFrame"""
        # Ensure SKU管理番号 column exists
        if 'SKU管理番号' not in df.columns:
            df['SKU管理番号'] = None
        
        # Process by product
        if '商品管理番号（商品URL）' in df.columns:
            for idx, row in df.iterrows():
                product_id = row['商品管理番号（商品URL）']
                
                # Only generate SKU if not already present
                if pd.isna(row['SKU管理番号']) or row['SKU管理番号'] == '':
                    df.at[idx, 'SKU管理番号'] = self.get_next_sku(product_id)
        
        return df
    
    def renumber_all_skus(self, df: pd.DataFrame, start_from: int = 1) -> pd.DataFrame:
        """Renumber all SKUs from scratch"""
        # Reset counters for affected products
        if '商品管理番号（商品URL）' in df.columns:
            product_ids = df['商品管理番号（商品URL）'].unique()
            
            for product_id in product_ids:
                self.counters[product_id] = start_from - 1
            
            # Generate new SKUs
            df = self.generate_skus(df)
        
        return df
    
    def get_product_sku_count(self, product_id: str) -> int:
        """Get current SKU count for a product"""
        return self.counters.get(product_id, 0)
    
    def reset_product_counter(self, product_id: str):
        """Reset SKU counter for a specific product"""
        with self.lock:
            if product_id in self.counters:
                self.counters[product_id] = 0
    
    def get_all_counters(self) -> Dict[str, int]:
        """Get all SKU counters"""
        return self.counters.copy()
    
    def import_counters(self, counters: Dict[str, int]):
        """Import SKU counters from external source"""
        with self.lock:
            self.counters.update(counters)
            self.save_state()