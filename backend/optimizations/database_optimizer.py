"""
データベースパフォーマンス最適化スクリプト
- インデックスの作成
- クエリの最適化
- 接続プールの実装
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """データベース最適化クラス"""
    
    def __init__(self, db_path: str = '/app/product_attributes_new.db'):
        self.db_path = db_path
        
    @contextmanager
    def get_connection(self):
        """データベース接続のコンテキストマネージャー"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # WALモード有効化（書き込み性能向上）
        conn.execute('PRAGMA journal_mode=WAL')
        # キャッシュサイズ増加
        conn.execute('PRAGMA cache_size=10000')
        # 同期モードを通常に（パフォーマンス向上）
        conn.execute('PRAGMA synchronous=NORMAL')
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_indexes(self):
        """パフォーマンス向上のためのインデックス作成"""
        indexes = [
            # device_attributes テーブル用
            "CREATE INDEX IF NOT EXISTS idx_device_brand ON device_attributes(brand)",
            "CREATE INDEX IF NOT EXISTS idx_device_name ON device_attributes(device_name)",
            "CREATE INDEX IF NOT EXISTS idx_device_size ON device_attributes(size_category)",
            "CREATE INDEX IF NOT EXISTS idx_device_brand_device ON device_attributes(brand, device_name)",
            "CREATE INDEX IF NOT EXISTS idx_device_brand_size ON device_attributes(brand, size_category)",
            "CREATE INDEX IF NOT EXISTS idx_device_usage ON device_attributes(usage_count DESC)",
            
            # product_devices テーブル用（レガシー互換性）
            "CREATE INDEX IF NOT EXISTS idx_pd_size ON product_devices(size_category)",
            "CREATE INDEX IF NOT EXISTS idx_pd_variation ON product_devices(variation_item_choice_2)",
            "CREATE INDEX IF NOT EXISTS idx_pd_attribute ON product_devices(product_attribute_8)",
            "CREATE INDEX IF NOT EXISTS idx_pd_composite ON product_devices(size_category, variation_item_choice_2)",
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for index_sql in indexes:
                try:
                    start_time = time.time()
                    cursor.execute(index_sql)
                    elapsed = time.time() - start_time
                    logger.info(f"Index created: {index_sql.split('INDEX')[1].split('ON')[0].strip()} ({elapsed:.2f}s)")
                except Exception as e:
                    logger.error(f"Failed to create index: {e}")
    
    def analyze_tables(self):
        """テーブル統計情報を更新（クエリプランナー最適化）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            tables = ['device_attributes', 'product_devices', 'attribute_mappings']
            for table in tables:
                try:
                    cursor.execute(f"ANALYZE {table}")
                    logger.info(f"Analyzed table: {table}")
                except Exception as e:
                    logger.warning(f"Could not analyze {table}: {e}")
    
    def vacuum_database(self):
        """データベースの最適化（断片化解消）"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("VACUUM")
            conn.close()
            logger.info("Database vacuumed successfully")
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """パフォーマンス統計を取得"""
        stats = {}
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # テーブルサイズ
            cursor.execute("""
                SELECT name, 
                       SUM("pgsize") as size_bytes
                FROM dbstat
                GROUP BY name
                ORDER BY size_bytes DESC
            """)
            stats['table_sizes'] = cursor.fetchall()
            
            # インデックス情報
            cursor.execute("""
                SELECT name, tbl_name 
                FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            stats['indexes'] = cursor.fetchall()
            
            # テーブル行数
            for table in ['device_attributes', 'product_devices']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
        
        return stats
    
    def optimize_all(self):
        """すべての最適化を実行"""
        logger.info("Starting database optimization...")
        
        # 1. インデックス作成
        self.create_indexes()
        
        # 2. テーブル分析
        self.analyze_tables()
        
        # 3. VACUUM実行
        self.vacuum_database()
        
        # 4. 統計情報表示
        stats = self.get_performance_stats()
        logger.info(f"Optimization complete. Stats: {stats}")
        
        return stats


class QueryCache:
    """クエリ結果のキャッシュ"""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # seconds
        
    def get(self, key: str) -> Optional[Any]:
        """キャッシュから取得"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """キャッシュに保存"""
        if len(self.cache) >= self.max_size:
            # LRU: 最も古いエントリを削除
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """キャッシュをクリア"""
        self.cache.clear()


if __name__ == "__main__":
    # スタンドアロン実行時
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else '/app/product_attributes_new.db'
    
    optimizer = DatabaseOptimizer(db_path)
    optimizer.optimize_all()
    
    print("\nDatabase optimization completed successfully!")