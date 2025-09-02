-- Supabase Migration: 既存のオブジェクトを考慮した安全な移行スクリプト

-- 1. 既存のテーブルとインデックスを確認（情報収集のみ）
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- 2. テーブルが存在しない場合のみ作成
CREATE TABLE IF NOT EXISTS brand_attributes (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) UNIQUE NOT NULL,
    brand_category VARCHAR(255) DEFAULT 'mobile_device',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS brand_values (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    row_index INTEGER NOT NULL,
    attribute_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_name) REFERENCES brand_attributes(brand_name) ON DELETE CASCADE,
    UNIQUE(brand_name, row_index)
);

CREATE TABLE IF NOT EXISTS device_attributes (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    device_name VARCHAR(255) NOT NULL,
    attribute_value TEXT NOT NULL,
    size_category VARCHAR(50),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(brand, device_name)
);

CREATE TABLE IF NOT EXISTS sku_counters (
    product_id VARCHAR(255) PRIMARY KEY,
    counter INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. インデックスを安全に作成（DROP & CREATE方式）
DROP INDEX IF EXISTS idx_brand_values_brand;
CREATE INDEX idx_brand_values_brand ON brand_values(brand_name);

DROP INDEX IF EXISTS idx_device_attributes_brand;
CREATE INDEX idx_device_attributes_brand ON device_attributes(brand);

DROP INDEX IF EXISTS idx_device_attributes_device;
CREATE INDEX idx_device_attributes_device ON device_attributes(device_name);

-- 4. トリガー関数を作成または置換
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. トリガーを安全に作成（DROP & CREATE方式）
DROP TRIGGER IF EXISTS update_brand_attributes_updated_at ON brand_attributes;
CREATE TRIGGER update_brand_attributes_updated_at 
    BEFORE UPDATE ON brand_attributes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_brand_values_updated_at ON brand_values;
CREATE TRIGGER update_brand_values_updated_at 
    BEFORE UPDATE ON brand_values
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_device_attributes_updated_at ON device_attributes;
CREATE TRIGGER update_device_attributes_updated_at 
    BEFORE UPDATE ON device_attributes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sku_counters_updated_at ON sku_counters;
CREATE TRIGGER update_sku_counters_updated_at 
    BEFORE UPDATE ON sku_counters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 6. 作成結果を確認
SELECT 
    'Tables created successfully' as status,
    COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('brand_attributes', 'brand_values', 'device_attributes', 'sku_counters');