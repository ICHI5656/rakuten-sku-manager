-- Supabase Migration: Create tables for Rakuten SKU Manager

-- Create brand_attributes table
CREATE TABLE IF NOT EXISTS brand_attributes (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) UNIQUE NOT NULL,
    brand_category VARCHAR(255) DEFAULT 'mobile_device',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create brand_values table
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

-- Create device_attributes table
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

-- Create SKU state table for counter persistence
CREATE TABLE IF NOT EXISTS sku_counters (
    product_id VARCHAR(255) PRIMARY KEY,
    counter INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_brand_values_brand ON brand_values(brand_name);
CREATE INDEX idx_device_attributes_brand ON device_attributes(brand);
CREATE INDEX idx_device_attributes_device ON device_attributes(device_name);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_brand_attributes_updated_at BEFORE UPDATE ON brand_attributes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_brand_values_updated_at BEFORE UPDATE ON brand_values
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_device_attributes_updated_at BEFORE UPDATE ON device_attributes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sku_counters_updated_at BEFORE UPDATE ON sku_counters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();