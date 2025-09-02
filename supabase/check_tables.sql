-- テーブルとデータの状態を確認するクエリ

-- 1. 既存のテーブルを確認
SELECT 
    table_name,
    'exists' as status
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. 各テーブルのレコード数を確認
SELECT 
    'device_attributes' as table_name,
    COUNT(*) as record_count
FROM device_attributes
UNION ALL
SELECT 
    'brand_attributes' as table_name,
    COUNT(*) as record_count
FROM brand_attributes
UNION ALL
SELECT 
    'brand_values' as table_name,
    COUNT(*) as record_count
FROM brand_values
UNION ALL
SELECT 
    'sku_counters' as table_name,
    COUNT(*) as record_count
FROM sku_counters
ORDER BY table_name;

-- 3. デバイスデータのサンプルを確認（最初の5件）
SELECT * FROM device_attributes LIMIT 5;