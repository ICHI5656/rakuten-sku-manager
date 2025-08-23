"""パフォーマンス最適化ユーティリティ"""
import pandas as pd
from typing import Dict, Any, Iterator
import logging

logger = logging.getLogger(__name__)


def dataframe_to_dict_iterator(df: pd.DataFrame) -> Iterator[Dict[str, Any]]:
    """
    DataFrameを効率的に辞書のイテレータに変換
    iterrows()よりも高速なitertuples()を使用
    """
    for row in df.itertuples(index=True):
        row_dict = {
            '_index': row.Index,
            **{col: getattr(row, _sanitize_column_name(col), None) 
               for col in df.columns}
        }
        yield row_dict


def _sanitize_column_name(col_name: str) -> str:
    """
    列名をitertuples()で使用可能な形式に変換
    日本語や特殊文字を含む列名に対応
    """
    # 括弧や特殊文字をアンダースコアに置換
    replacements = {
        ' ': '_',
        '（': '_',
        '）': '_',
        '(': '_',
        ')': '_',
        '/': '_',
        '\\': '_',
        '.': '_',
        '-': '_',
        '!': '_',
        '?': '_',
        '！': '_',
        '？': '_',
    }
    
    sanitized = col_name
    for old, new in replacements.items():
        sanitized = sanitized.replace(old, new)
    
    # 先頭が数字の場合は'_'を追加
    if sanitized and sanitized[0].isdigit():
        sanitized = f'_{sanitized}'
    
    return sanitized


def process_dataframe_in_chunks(df: pd.DataFrame, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
    """
    大規模DataFrameをチャンクに分割して処理
    メモリ効率を改善
    """
    total_rows = len(df)
    for start in range(0, total_rows, chunk_size):
        end = min(start + chunk_size, total_rows)
        logger.debug(f"Processing chunk: rows {start} to {end}")
        yield df.iloc[start:end]


def optimize_dataframe_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrameのデータ型を最適化してメモリ使用量を削減
    """
    optimized_df = df.copy()
    
    for col in optimized_df.columns:
        col_type = optimized_df[col].dtype
        
        # 整数型の最適化
        if col_type != 'object':
            c_min = optimized_df[col].min()
            c_max = optimized_df[col].max()
            
            if str(col_type)[:3] == 'int':
                if c_min > pd.np.iinfo(pd.np.int8).min and c_max < pd.np.iinfo(pd.np.int8).max:
                    optimized_df[col] = optimized_df[col].astype(pd.np.int8)
                elif c_min > pd.np.iinfo(pd.np.int16).min and c_max < pd.np.iinfo(pd.np.int16).max:
                    optimized_df[col] = optimized_df[col].astype(pd.np.int16)
                elif c_min > pd.np.iinfo(pd.np.int32).min and c_max < pd.np.iinfo(pd.np.int32).max:
                    optimized_df[col] = optimized_df[col].astype(pd.np.int32)
            
            # 浮動小数点型の最適化
            elif str(col_type)[:5] == 'float':
                if c_min > pd.np.finfo(pd.np.float16).min and c_max < pd.np.finfo(pd.np.float16).max:
                    optimized_df[col] = optimized_df[col].astype(pd.np.float16)
                elif c_min > pd.np.finfo(pd.np.float32).min and c_max < pd.np.finfo(pd.np.float32).max:
                    optimized_df[col] = optimized_df[col].astype(pd.np.float32)
    
    return optimized_df