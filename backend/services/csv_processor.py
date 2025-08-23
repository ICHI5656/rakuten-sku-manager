import pandas as pd
import polars as pl
import chardet
from pathlib import Path
from typing import List, Dict, Optional, Union
import codecs

class CSVProcessor:
    def __init__(self):
        self.original_columns = None
        self.encoding = 'shift_jis'
    
    def detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding"""
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            return result['encoding'] or 'shift_jis'
    
    def read_csv(self, file_path: Path, use_polars: bool = False) -> Union[pd.DataFrame, pl.DataFrame]:
        """Read CSV file with proper encoding"""
        # Detect encoding
        encoding = self.detect_encoding(file_path)
        
        if use_polars:
            # Use polars for large files
            df = pl.read_csv(
                file_path,
                encoding=encoding,
                truncate_ragged_lines=True
            )
        else:
            # Use pandas for standard processing
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                dtype=str,
                keep_default_na=False,
                on_bad_lines='skip'
            )
            
            # Store original columns for later
            self.original_columns = df.columns.tolist()
        
        return df
    
    def save_csv(self, df: pd.DataFrame, file_path: Path):
        """Save DataFrame to CSV with Shift-JIS encoding"""
        # Ensure column order matches original
        if self.original_columns and set(df.columns) == set(self.original_columns):
            df = df[self.original_columns]
        
        # Save with Shift-JIS encoding and CRLF line endings
        df.to_csv(
            file_path,
            index=False,
            encoding='shift_jis',
            errors='replace',
            lineterminator='\r\n'
        )
    
    def get_product_info(self, df: pd.DataFrame) -> List[Dict]:
        """Extract product information from DataFrame"""
        products = []
        
        if '商品管理番号（商品URL）' in df.columns:
            grouped = df.groupby('商品管理番号（商品URL）')
            
            for product_id, group in grouped:
                product_info = {
                    "product_id": product_id,
                    "product_name": group['商品名'].iloc[0] if '商品名' in group.columns else "",
                    "variation_count": self._count_variations(group),
                    "sku_count": len(group[group['SKU管理番号'].notna()]) if 'SKU管理番号' in group.columns else 0
                }
                products.append(product_info)
        
        return products
    
    def _count_variations(self, df: pd.DataFrame) -> int:
        """Count total variations in a product"""
        variation_count = 1
        
        # Check variation columns (バリエーション1-6)
        for i in range(1, 7):
            col_name = f'バリエーション{i}:選択肢'
            if col_name in df.columns:
                unique_values = df[col_name].dropna().unique()
                if len(unique_values) > 0:
                    variation_count *= len(unique_values)
        
        return variation_count
    
    def process_cross_join(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate all variation combinations using cross join"""
        result_dfs = []
        
        if '商品管理番号（商品URL）' in df.columns:
            grouped = df.groupby('商品管理番号（商品URL）')
            
            for product_id, group in grouped:
                # Extract variations
                variations = {}
                for i in range(1, 7):
                    col_name = f'バリエーション{i}:選択肢'
                    if col_name in group.columns:
                        unique_values = group[col_name].dropna().unique()
                        if len(unique_values) > 0:
                            variations[i] = unique_values.tolist()
                
                if variations:
                    # Create cross join of all variations
                    import itertools
                    variation_combinations = list(itertools.product(*variations.values()))
                    
                    # Create new rows for each combination
                    base_row = group.iloc[0].copy()
                    new_rows = []
                    
                    for combo in variation_combinations:
                        new_row = base_row.copy()
                        for idx, (var_num, value) in enumerate(zip(variations.keys(), combo)):
                            new_row[f'バリエーション{var_num}:選択肢'] = value
                        new_rows.append(new_row)
                    
                    if new_rows:
                        result_dfs.append(pd.DataFrame(new_rows))
                else:
                    result_dfs.append(group)
        
        if result_dfs:
            return pd.concat(result_dfs, ignore_index=True)
        
        return df
    
    def split_by_size(self, df: pd.DataFrame, max_rows: int = 60000) -> List[pd.DataFrame]:
        """Split DataFrame into chunks of max_rows"""
        chunks = []
        for i in range(0, len(df), max_rows):
            chunks.append(df.iloc[i:i+max_rows])
        return chunks