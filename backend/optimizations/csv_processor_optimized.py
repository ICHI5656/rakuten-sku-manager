"""
最適化されたCSV処理モジュール
- Polarsを使用した高速処理
- チャンク処理によるメモリ効率化
- 並列処理の実装
"""

import pandas as pd
import polars as pl
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
from functools import lru_cache

logging.basicConfig(level=logging.WARNING)  # DEBUGからWARNINGに変更
logger = logging.getLogger(__name__)

class OptimizedCSVProcessor:
    """最適化されたCSV処理クラス"""
    
    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size
        self._device_cache = {}
        
    def process_csv_fast(self, file_path: str) -> pd.DataFrame:
        """Polarsを使用した高速CSV読み込み"""
        try:
            # Polarsで読み込み（より高速）
            df_pl = pl.read_csv(
                file_path,
                encoding='shift-jis',
                try_parse_dates=False,
                low_memory=False
            )
            
            # Pandasに変換（必要な場合）
            return df_pl.to_pandas()
        except:
            # フォールバック: 従来のPandas読み込み
            return pd.read_csv(
                file_path,
                encoding='shift-jis',
                low_memory=False,
                na_values=['', 'nan', 'NaN', 'null'],
                keep_default_na=True
            )
    
    def process_in_chunks(self, df: pd.DataFrame, 
                         process_func: callable) -> pd.DataFrame:
        """大規模データをチャンク単位で処理"""
        if len(df) <= self.chunk_size:
            return process_func(df)
        
        chunks = []
        for start in range(0, len(df), self.chunk_size):
            end = min(start + self.chunk_size, len(df))
            chunk = df.iloc[start:end]
            processed = process_func(chunk)
            chunks.append(processed)
            
            # メモリ解放
            del chunk
            if start % (self.chunk_size * 5) == 0:
                gc.collect()
        
        result = pd.concat(chunks, ignore_index=True)
        del chunks
        gc.collect()
        
        return result
    
    def vectorized_device_processing(self, df: pd.DataFrame, 
                                    device_col: str,
                                    devices_to_remove: List[str] = None,
                                    devices_to_add: List[str] = None) -> pd.DataFrame:
        """ベクトル化された機種処理"""
        if devices_to_remove:
            # isinを使用した高速フィルタリング
            mask = ~df[device_col].isin(devices_to_remove)
            df = df[mask].copy()
        
        if devices_to_add:
            # 一括追加処理
            new_rows = self._create_bulk_device_rows(df, device_col, devices_to_add)
            if new_rows:
                df = pd.concat([df] + new_rows, ignore_index=True)
        
        return df
    
    def _create_bulk_device_rows(self, df: pd.DataFrame, 
                                 device_col: str,
                                 devices: List[str]) -> List[pd.DataFrame]:
        """デバイス行を一括作成"""
        new_dfs = []
        template_row = df.iloc[0] if not df.empty else None
        
        if template_row is not None:
            for device in devices:
                new_row = template_row.copy()
                new_row[device_col] = device
                new_dfs.append(pd.DataFrame([new_row]))
        
        return new_dfs
    
    @lru_cache(maxsize=128)
    def cached_device_lookup(self, brand: str, size: str) -> Optional[str]:
        """キャッシュ付きデバイス属性検索"""
        cache_key = f"{brand}_{size}"
        if cache_key in self._device_cache:
            return self._device_cache[cache_key]
        
        # データベースから取得（実際の実装は省略）
        result = self._fetch_from_database(brand, size)
        self._device_cache[cache_key] = result
        return result
    
    def _fetch_from_database(self, brand: str, size: str) -> Optional[str]:
        """データベースから属性を取得（プレースホルダー）"""
        # 実際の実装では最適化されたクエリを使用
        return None
    
    def parallel_product_processing(self, products: List[Dict], 
                                   process_func: callable,
                                   max_workers: int = 4) -> List[pd.DataFrame]:
        """商品を並列処理"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_func, product): product 
                for product in products
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing product: {e}")
        
        return results
    
    def optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrameのメモリ使用量を最適化"""
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type != 'object':
                if col_type == 'float64':
                    df[col] = pd.to_numeric(df[col], downcast='float')
                elif col_type == 'int64':
                    df[col] = pd.to_numeric(df[col], downcast='integer')
            else:
                # カテゴリ型に変換可能な列を変換
                num_unique_values = len(df[col].unique())
                num_total_values = len(df[col])
                if num_unique_values / num_total_values < 0.5:
                    df[col] = df[col].astype('category')
        
        return df
    
    def batch_database_operations(self, operations: List[Tuple[str, Any]]) -> None:
        """データベース操作をバッチ処理"""
        # トランザクションで一括処理
        import sqlite3
        
        conn = sqlite3.connect('/app/product_attributes_new.db')
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('BEGIN TRANSACTION')
        
        try:
            cursor = conn.cursor()
            for query, params in operations:
                cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


class FastSKUGenerator:
    """高速SKU生成クラス"""
    
    def __init__(self):
        self.counter_cache = {}
        
    def generate_skus_vectorized(self, 
                                 num_skus: int,
                                 prefix: str = 'sku_a') -> np.ndarray:
        """ベクトル化されたSKU生成"""
        # NumPyを使用した高速生成
        counter_start = self.counter_cache.get(prefix, 1)
        sku_numbers = np.arange(counter_start, counter_start + num_skus)
        
        # ベクトル化された文字列生成
        skus = np.char.add(prefix, 
                          np.char.zfill(sku_numbers.astype(str), 6))
        
        self.counter_cache[prefix] = counter_start + num_skus
        return skus
    
    def bulk_assign_skus(self, df: pd.DataFrame, 
                         sku_col: str = 'SKU管理番号') -> pd.DataFrame:
        """DataFrameに一括でSKUを割り当て"""
        mask = df[sku_col].isna() | (df[sku_col] == '')
        num_needed = mask.sum()
        
        if num_needed > 0:
            new_skus = self.generate_skus_vectorized(num_needed)
            df.loc[mask, sku_col] = new_skus
        
        return df


def optimize_variation_definitions(df: pd.DataFrame) -> pd.DataFrame:
    """バリエーション定義のクリア処理を最適化"""
    variation_cols = ['バリエーション1選択肢定義', 'バリエーション2選択肢定義']
    
    # 親行マスクを作成
    parent_mask = (df['商品管理番号（商品URL）'].notna() & 
                  (df['SKU管理番号'].isna() | (df['SKU管理番号'] == '')))
    
    # ベクトル化された一括更新
    for col in variation_cols:
        if col in df.columns:
            df.loc[~parent_mask, col] = ''
    
    return df


if __name__ == "__main__":
    # テスト用コード
    processor = OptimizedCSVProcessor()
    sku_gen = FastSKUGenerator()
    
    print("Optimized CSV Processor initialized")
    print("Fast SKU Generator initialized")