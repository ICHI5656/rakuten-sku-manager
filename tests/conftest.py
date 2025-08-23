"""pytest設定ファイル"""
import pytest
import sys
import os
from pathlib import Path

# バックエンドのパスを追加
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

@pytest.fixture
def sample_csv_data():
    """テスト用のサンプルCSVデータを提供"""
    import pandas as pd
    
    data = {
        '商品管理番号（商品URL）': ['product001', 'product001', 'product001', 'product002', 'product002'],
        'SKU管理番号': [None, 'sku_a000001', 'sku_a000002', None, 'sku_a000003'],
        'バリエーション項目選択肢1': ['', 'ブラック', 'ホワイト', '', 'レッド'],
        'バリエーション項目選択肢2': ['', 'iPhone 14', 'iPhone 14', '', 'iPhone 15'],
        'バリエーション2選択肢定義': ['iPhone 14|iPhone 15', '', '', 'iPhone 15|iPhone 14 Pro', '']
    }
    
    return pd.DataFrame(data)

@pytest.fixture
def test_state_file(tmp_path):
    """一時的な状態ファイルのパスを提供"""
    return tmp_path / "test_sku_state.json"

@pytest.fixture
def mock_upload_file():
    """アップロードファイルのモックを提供"""
    from fastapi import UploadFile
    from io import BytesIO
    
    class MockUploadFile:
        def __init__(self, filename: str, content: bytes):
            self.filename = filename
            self.file = BytesIO(content)
        
        async def read(self):
            return self.file.read()
        
        async def seek(self, offset):
            self.file.seek(offset)
    
    return MockUploadFile