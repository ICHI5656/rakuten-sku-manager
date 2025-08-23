"""SKUマネージャーのテスト"""
import pytest
import json
from pathlib import Path
from services.sku_manager import SKUManager


class TestSKUManager:
    """SKUManagerクラスのテスト"""
    
    def test_initialization(self, test_state_file):
        """初期化のテスト"""
        manager = SKUManager(test_state_file)
        assert manager.state_file == test_state_file
        assert manager.counters == {}
    
    def test_get_next_sku(self, test_state_file):
        """SKU生成のテスト"""
        manager = SKUManager(test_state_file)
        
        # 最初のSKU
        sku1 = manager.get_next_sku("product001")
        assert sku1 == "sku_a000001"
        
        # 同じ商品の次のSKU
        sku2 = manager.get_next_sku("product001")
        assert sku2 == "sku_a000002"
        
        # 別の商品の最初のSKU
        sku3 = manager.get_next_sku("product002")
        assert sku3 == "sku_a000001"
    
    def test_save_and_load_state(self, test_state_file):
        """状態の保存と読み込みのテスト"""
        # 最初のマネージャーで状態を作成
        manager1 = SKUManager(test_state_file)
        manager1.get_next_sku("product001")
        manager1.get_next_sku("product001")
        manager1.save_state()
        
        # 新しいマネージャーで状態を読み込み
        manager2 = SKUManager(test_state_file)
        assert manager2.counters["product001"] == 2
        
        # 続きから番号を生成
        sku = manager2.get_next_sku("product001")
        assert sku == "sku_a000003"
    
    def test_thread_safety(self, test_state_file):
        """スレッドセーフティのテスト"""
        import threading
        
        manager = SKUManager(test_state_file)
        results = []
        
        def generate_sku():
            sku = manager.get_next_sku("product001")
            results.append(sku)
        
        threads = []
        for _ in range(10):
            t = threading.Thread(target=generate_sku)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # SKUが重複していないことを確認
        assert len(results) == len(set(results))
        assert len(results) == 10