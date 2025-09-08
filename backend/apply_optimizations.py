#!/usr/bin/env python3
"""
最適化適用スクリプト
すべての最適化を既存システムに適用
"""

import sys
import os
import shutil
from pathlib import Path
import logging

# パスを追加
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/optimizations')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def apply_database_optimizations():
    """データベース最適化を適用"""
    logger.info("Applying database optimizations...")
    
    try:
        from optimizations.database_optimizer import DatabaseOptimizer
        
        # 本番データベースに最適化を適用
        db_path = '/app/product_attributes_new.db'
        if os.path.exists(db_path):
            optimizer = DatabaseOptimizer(db_path)
            stats = optimizer.optimize_all()
            logger.info(f"Database optimization complete: {stats}")
        else:
            logger.warning(f"Database not found: {db_path}")
        
        # brand_attributes.dbにも適用
        brand_db = '/app/brand_attributes.db'
        if os.path.exists(brand_db):
            optimizer = DatabaseOptimizer(brand_db)
            optimizer.create_indexes()
            logger.info("Brand database indexes created")
            
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return False
    
    return True

def integrate_optimized_processor():
    """最適化されたプロセッサーを統合"""
    logger.info("Integrating optimized processor...")
    
    try:
        # バックアップ作成
        original = Path('/app/services/rakuten_processor.py')
        backup = Path('/app/services/rakuten_processor_backup.py')
        
        if original.exists() and not backup.exists():
            shutil.copy2(original, backup)
            logger.info(f"Backup created: {backup}")
        
        # 最適化版を適用するためのラッパーを作成
        wrapper_content = '''"""
Rakuten CSV Processor - 最適化版への移行ラッパー
"""

import os
import logging

# 環境変数で最適化版の使用を制御
USE_OPTIMIZED = os.getenv('USE_OPTIMIZED_PROCESSOR', 'true').lower() == 'true'

if USE_OPTIMIZED:
    try:
        from .rakuten_processor_optimized import RakutenCSVProcessorOptimized as RakutenCSVProcessor
        logging.info("Using optimized Rakuten CSV Processor")
    except ImportError:
        # フォールバック: 元のプロセッサーを使用
        from .rakuten_processor_backup import RakutenCSVProcessor
        logging.warning("Optimized processor not found, using original")
else:
    from .rakuten_processor_backup import RakutenCSVProcessor
    logging.info("Using original Rakuten CSV Processor")

__all__ = ['RakutenCSVProcessor']
'''
        
        # ラッパーを保存
        with open('/app/services/rakuten_processor.py', 'w', encoding='utf-8') as f:
            f.write(wrapper_content)
        
        logger.info("Processor integration complete")
        
    except Exception as e:
        logger.error(f"Processor integration failed: {e}")
        return False
    
    return True

def update_app_configuration():
    """アプリケーション設定を更新"""
    logger.info("Updating application configuration...")
    
    try:
        # app.pyの最適化設定を追加
        app_path = Path('/app/app.py')
        if app_path.exists():
            content = app_path.read_text(encoding='utf-8')
            
            # ロギングレベルの変更を追加
            if 'logging.basicConfig' not in content:
                optimization_config = '''
# Performance optimizations
import os
import logging

# Set logging level based on environment
LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable optimizations
os.environ['USE_OPTIMIZED_PROCESSOR'] = 'true'
os.environ['ENABLE_QUERY_CACHE'] = 'true'
os.environ['MAX_WORKERS'] = '4'

'''
                # ファイルの先頭付近に挿入
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(('import', 'from')):
                        import_end = i
                        break
                
                lines.insert(import_end, optimization_config)
                content = '\n'.join(lines)
                
                app_path.write_text(content, encoding='utf-8')
                logger.info("App configuration updated")
        
    except Exception as e:
        logger.error(f"Configuration update failed: {e}")
        return False
    
    return True

def create_performance_monitoring():
    """パフォーマンスモニタリングスクリプトを作成"""
    logger.info("Creating performance monitoring...")
    
    monitor_script = '''#!/usr/bin/env python3
"""
パフォーマンスモニタリングスクリプト
"""

import time
import psutil
import sqlite3
import json
from datetime import datetime

def monitor_performance():
    """システムパフォーマンスをモニタリング"""
    stats = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': {
            'percent': psutil.virtual_memory().percent,
            'used_gb': psutil.virtual_memory().used / (1024**3),
            'available_gb': psutil.virtual_memory().available / (1024**3)
        },
        'disk': {
            'percent': psutil.disk_usage('/').percent,
            'free_gb': psutil.disk_usage('/').free / (1024**3)
        }
    }
    
    # データベース統計
    try:
        conn = sqlite3.connect('/app/product_attributes_new.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM device_attributes")
        stats['db_device_count'] = cursor.fetchone()[0]
        conn.close()
    except:
        stats['db_device_count'] = -1
    
    return stats

if __name__ == "__main__":
    while True:
        stats = monitor_performance()
        print(json.dumps(stats, indent=2))
        
        # 高負荷時の警告
        if stats['cpu_percent'] > 80:
            print("WARNING: High CPU usage detected!")
        if stats['memory']['percent'] > 85:
            print("WARNING: High memory usage detected!")
        
        time.sleep(30)  # 30秒ごとにモニタリング
'''
    
    try:
        monitor_path = Path('/app/monitor_performance.py')
        monitor_path.write_text(monitor_script, encoding='utf-8')
        monitor_path.chmod(0o755)
        logger.info("Performance monitor created")
        
    except Exception as e:
        logger.error(f"Monitor creation failed: {e}")
        return False
    
    return True

def verify_optimizations():
    """最適化が正しく適用されたか検証"""
    logger.info("Verifying optimizations...")
    
    checks = {
        'database_indexes': False,
        'optimized_processor': False,
        'configuration': False,
        'monitoring': False
    }
    
    # データベースインデックスの確認
    try:
        import sqlite3
        conn = sqlite3.connect('/app/product_attributes_new.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = cursor.fetchall()
        checks['database_indexes'] = len(indexes) > 0
        conn.close()
    except:
        pass
    
    # 最適化プロセッサーの確認
    checks['optimized_processor'] = os.path.exists('/app/services/rakuten_processor_optimized.py')
    
    # 設定の確認
    checks['configuration'] = os.getenv('USE_OPTIMIZED_PROCESSOR', '').lower() == 'true'
    
    # モニタリングの確認
    checks['monitoring'] = os.path.exists('/app/monitor_performance.py')
    
    # 結果表示
    logger.info("Optimization verification results:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        logger.info(f"  {status} {check}")
    
    return all(checks.values())

def main():
    """メイン実行関数"""
    logger.info("="*50)
    logger.info("Starting optimization application")
    logger.info("="*50)
    
    success = True
    
    # 1. データベース最適化
    if not apply_database_optimizations():
        logger.error("Database optimization failed")
        success = False
    
    # 2. プロセッサー統合
    if not integrate_optimized_processor():
        logger.error("Processor integration failed")
        success = False
    
    # 3. 設定更新
    if not update_app_configuration():
        logger.error("Configuration update failed")
        success = False
    
    # 4. モニタリング作成
    if not create_performance_monitoring():
        logger.error("Monitor creation failed")
        success = False
    
    # 5. 検証
    if verify_optimizations():
        logger.info("✅ All optimizations successfully applied!")
    else:
        logger.warning("⚠️ Some optimizations may not be fully applied")
        success = False
    
    logger.info("="*50)
    
    if success:
        logger.info("🚀 System optimization complete!")
        logger.info("Restart the application to apply all changes")
    else:
        logger.error("❌ Optimization had some issues")
        logger.info("Check the logs for details")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())