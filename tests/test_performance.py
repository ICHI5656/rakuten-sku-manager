"""パフォーマンス最適化のテスト"""
import pytest
import pandas as pd
import numpy as np
from backend.utils.performance import (
    dataframe_to_dict_iterator,
    process_dataframe_in_chunks,
    optimize_dataframe_dtypes,
    _sanitize_column_name
)


class TestPerformanceUtils:
    """パフォーマンスユーティリティのテスト"""
    
    def test_sanitize_column_name(self):
        """列名のサニタイズテスト"""
        assert _sanitize_column_name("商品管理番号（商品URL）") == "商品管理番号_商品URL_"
        assert _sanitize_column_name("SKU管理番号") == "SKU管理番号"
        assert _sanitize_column_name("バリエーション項目選択肢1") == "バリエーション項目選択肢1"
        assert _sanitize_column_name("1stColumn") == "_1stColumn"
    
    def test_dataframe_to_dict_iterator(self, sample_csv_data):
        """DataFrameから辞書イテレータへの変換テスト"""
        results = list(dataframe_to_dict_iterator(sample_csv_data))
        
        assert len(results) == 5
        assert '_index' in results[0]
        assert '商品管理番号（商品URL）' in results[0]
        assert results[0]['商品管理番号（商品URL）'] == 'product001'
    
    def test_process_dataframe_in_chunks(self):
        """チャンク処理のテスト"""
        # 大規模データフレームを作成
        df = pd.DataFrame({
            'col1': range(10000),
            'col2': range(10000),
        })
        
        chunks = list(process_dataframe_in_chunks(df, chunk_size=1000))
        
        assert len(chunks) == 10
        assert len(chunks[0]) == 1000
        assert len(chunks[-1]) == 1000
    
    def test_optimize_dataframe_dtypes(self):
        """データ型最適化のテスト"""
        # 様々なデータ型を含むDataFrameを作成
        df = pd.DataFrame({
            'small_int': np.array([1, 2, 3, 4, 5], dtype=np.int64),
            'large_int': np.array([1000000, 2000000, 3000000, 4000000, 5000000], dtype=np.int64),
            'float_col': np.array([1.1, 2.2, 3.3, 4.4, 5.5], dtype=np.float64),
            'text_col': ['a', 'b', 'c', 'd', 'e']
        })
        
        optimized_df = optimize_dataframe_dtypes(df)
        
        # small_intはint8に最適化されるべき
        assert optimized_df['small_int'].dtype == np.int8
        # large_intはint32に最適化されるべき
        assert optimized_df['large_int'].dtype == np.int32
        # float_colはfloat32に最適化されるべき
        assert optimized_df['float_col'].dtype == np.float32
        # text_colは変更されない
        assert optimized_df['text_col'].dtype == 'object'