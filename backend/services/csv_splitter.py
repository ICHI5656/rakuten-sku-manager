"""
CSV Splitter for large files
Splits processed CSV files into 60k row chunks while keeping parent products intact
"""
import pandas as pd
import logging
from pathlib import Path
from typing import List, Tuple, Dict
import math

logger = logging.getLogger(__name__)

class CSVSplitter:
    """Split large CSV files into manageable chunks"""
    
    def __init__(self, max_rows_per_file: int = 60000):
        """
        Initialize CSV splitter
        Args:
            max_rows_per_file: Maximum rows per output file (default: 60000)
        """
        self.max_rows_per_file = max_rows_per_file
    
    def split_by_parent_products(self, df: pd.DataFrame, output_dir: Path, base_filename: str) -> List[Path]:
        """
        Split DataFrame into multiple files based on parent products
        Ensures each parent product and its SKUs stay together
        
        Args:
            df: DataFrame to split
            output_dir: Directory to save split files
            base_filename: Base name for output files
            
        Returns:
            List of paths to created files
        """
        output_files = []
        
        # 商品管理番号でグループ化
        product_id_column = '商品管理番号（商品URL）'
        if product_id_column not in df.columns:
            # Try alternative column name
            product_id_column = '商品管理番号'
            if product_id_column not in df.columns:
                logger.error(f"Product ID column not found in DataFrame")
                return []
        
        # 親製品ごとにグループ化してカウント
        product_groups = []
        for product_id, group in df.groupby(product_id_column, sort=False):
            product_groups.append({
                'product_id': product_id,
                'rows': len(group),
                'data': group
            })
        
        logger.info(f"Found {len(product_groups)} parent products with total {len(df)} rows")
        
        # 分割ロジック: 親製品単位で6万行を超えない範囲でグループ化
        current_chunk = []
        current_rows = 0
        chunk_number = 1
        
        for product_group in product_groups:
            # 単一の親製品が最大行数を超える場合の警告
            if product_group['rows'] > self.max_rows_per_file:
                logger.warning(
                    f"Parent product {product_group['product_id']} has {product_group['rows']} rows, "
                    f"exceeding max limit of {self.max_rows_per_file}. It will be in its own file."
                )
                # この製品だけで1ファイル作成
                if current_chunk:
                    # 現在のチャンクを保存
                    output_file = self._save_chunk(
                        current_chunk, output_dir, base_filename, chunk_number
                    )
                    output_files.append(output_file)
                    chunk_number += 1
                    current_chunk = []
                    current_rows = 0
                
                # 大きな製品を単独で保存
                output_file = self._save_chunk(
                    [product_group], output_dir, base_filename, chunk_number
                )
                output_files.append(output_file)
                chunk_number += 1
                continue
            
            # 現在のチャンクに追加すると制限を超える場合
            if current_rows + product_group['rows'] > self.max_rows_per_file:
                # 現在のチャンクを保存
                if current_chunk:
                    output_file = self._save_chunk(
                        current_chunk, output_dir, base_filename, chunk_number
                    )
                    output_files.append(output_file)
                    chunk_number += 1
                
                # 新しいチャンクを開始
                current_chunk = [product_group]
                current_rows = product_group['rows']
            else:
                # 現在のチャンクに追加
                current_chunk.append(product_group)
                current_rows += product_group['rows']
        
        # 最後のチャンクを保存
        if current_chunk:
            output_file = self._save_chunk(
                current_chunk, output_dir, base_filename, chunk_number
            )
            output_files.append(output_file)
        
        logger.info(f"Split into {len(output_files)} files")
        return output_files
    
    def _save_chunk(self, chunk: List[Dict], output_dir: Path, base_filename: str, chunk_number: int) -> Path:
        """
        Save a chunk of product groups to a CSV file
        
        Args:
            chunk: List of product groups
            output_dir: Output directory
            base_filename: Base filename
            chunk_number: Chunk number for filename
            
        Returns:
            Path to saved file
        """
        # Combine all DataFrames in the chunk
        chunk_df = pd.concat([group['data'] for group in chunk], ignore_index=True)
        
        # Generate filename
        filename = f"{base_filename}_part{chunk_number:03d}.csv"
        output_path = output_dir / filename
        
        # Clear バリエーション2選択肢定義 for SKU rows before saving
        if 'バリエーション2選択肢定義' in chunk_df.columns and 'SKU管理番号' in chunk_df.columns:
            sku_mask = chunk_df['SKU管理番号'].notna() & (chunk_df['SKU管理番号'] != '')
            chunk_df.loc[sku_mask, 'バリエーション2選択肢定義'] = ''
        
        # Save with Shift-JIS encoding for Rakuten
        chunk_df.to_csv(
            output_path,
            index=False,
            encoding='shift_jis',
            line_terminator='\r\n'
        )
        
        total_products = len(chunk)
        total_rows = len(chunk_df)
        logger.info(
            f"Saved {filename}: {total_products} products, {total_rows} rows"
        )
        
        return output_path
    
    def estimate_splits(self, total_rows: int, avg_rows_per_product: float) -> Dict:
        """
        Estimate number of split files needed
        
        Args:
            total_rows: Total number of rows
            avg_rows_per_product: Average rows per parent product
            
        Returns:
            Dictionary with estimation details
        """
        estimated_files = math.ceil(total_rows / self.max_rows_per_file)
        products_per_file = self.max_rows_per_file / avg_rows_per_product
        
        return {
            'total_rows': total_rows,
            'max_rows_per_file': self.max_rows_per_file,
            'estimated_files': estimated_files,
            'avg_rows_per_product': avg_rows_per_product,
            'avg_products_per_file': products_per_file,
            'note': 'Actual file count may vary to keep parent products intact'
        }