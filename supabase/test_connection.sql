-- Supabaseの接続テスト用SQL
-- このクエリを実行して、データベースが正常に動作しているか確認します

-- 1. 現在のテーブルを確認
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- 2. 各テーブルのレコード数を確認
SELECT 
    'brand_attributes' as table_name, 
    COUNT(*) as count 
FROM brand_attributes
UNION ALL
SELECT 
    'brand_values' as table_name, 
    COUNT(*) as count 
FROM brand_values
UNION ALL
SELECT 
    'device_attributes' as table_name, 
    COUNT(*) as count 
FROM device_attributes
UNION ALL
SELECT 
    'sku_counters' as table_name, 
    COUNT(*) as count 
FROM sku_counters;