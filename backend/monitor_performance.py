#!/usr/bin/env python3
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
