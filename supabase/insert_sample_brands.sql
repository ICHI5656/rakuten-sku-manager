-- Supabaseにサンプルブランドデータを挿入

-- ブランドを追加
INSERT INTO brand_attributes (brand_name, brand_category) VALUES
('iPhone', 'mobile_device'),
('Galaxy', 'mobile_device'),
('Xperia', 'mobile_device'),
('AQUOS', 'mobile_device'),
('Pixel', 'mobile_device'),
('Huawei', 'mobile_device')
ON CONFLICT (brand_name) DO NOTHING;

-- iPhoneのブランド属性値を追加
INSERT INTO brand_values (brand_name, row_index, attribute_value) VALUES
('iPhone', 1, 'amicoco|アップル|iPhone'),
('iPhone', 2, 'amicoco|アップル|Pro'),
('iPhone', 3, 'amicoco|アップル|Plus'),
('iPhone', 4, 'amicoco|アップル|ProMax'),
('iPhone', 5, 'amicoco|アップル|mini')
ON CONFLICT (brand_name, row_index) DO NOTHING;

-- Galaxyのブランド属性値を追加
INSERT INTO brand_values (brand_name, row_index, attribute_value) VALUES
('Galaxy', 1, 'amicoco|サムスン|Galaxy'),
('Galaxy', 2, 'amicoco|サムスン|Note'),
('Galaxy', 3, 'amicoco|サムスン|Ultra'),
('Galaxy', 4, 'amicoco|サムスン|Plus')
ON CONFLICT (brand_name, row_index) DO NOTHING;

-- Xperiaのブランド属性値を追加
INSERT INTO brand_values (brand_name, row_index, attribute_value) VALUES
('Xperia', 1, 'amicoco|ソニー|Xperia'),
('Xperia', 2, 'amicoco|ソニー|1'),
('Xperia', 3, 'amicoco|ソニー|5'),
('Xperia', 4, 'amicoco|ソニー|10'),
('Xperia', 5, 'amicoco|ソニー|Ace')
ON CONFLICT (brand_name, row_index) DO NOTHING;

-- AQUOSのブランド属性値を追加
INSERT INTO brand_values (brand_name, row_index, attribute_value) VALUES
('AQUOS', 1, 'amicoco|シャープ|AQUOS'),
('AQUOS', 2, 'amicoco|シャープ|sense'),
('AQUOS', 3, 'amicoco|シャープ|wish'),
('AQUOS', 4, 'amicoco|シャープ|R')
ON CONFLICT (brand_name, row_index) DO NOTHING;

-- Pixelのブランド属性値を追加
INSERT INTO brand_values (brand_name, row_index, attribute_value) VALUES
('Pixel', 1, 'amicoco|グーグル|Pixel'),
('Pixel', 2, 'amicoco|グーグル|Pro'),
('Pixel', 3, 'amicoco|グーグル|a')
ON CONFLICT (brand_name, row_index) DO NOTHING;

-- Huaweiのブランド属性値を追加
INSERT INTO brand_values (brand_name, row_index, attribute_value) VALUES
('Huawei', 1, 'amicoco|ファーウェイ|アップル'),
('Huawei', 2, 'amicoco|ファーウェイ|グーグル'),
('Huawei', 3, 'amicoco|ファーウェイ|ソニー'),
('Huawei', 4, 'amicoco|ファーウェイ|原セラ'),
('Huawei', 5, 'amicoco|ファーウェイ|ASUS'),
('Huawei', 6, 'amicoco|ファーウェイ|シャープ'),
('Huawei', 7, 'amicoco|ファーウェイ|富士通'),
('Huawei', 8, 'amicoco|ファーウェイ|FCNT'),
('Huawei', 9, 'amicoco|ファーウェイ|楽天モバイル'),
('Huawei', 10, 'amicoco|ファーウェイ|サムスン'),
('Huawei', 11, 'amicoco|ファーウェイ|シャオミ'),
('Huawei', 12, 'amicoco|ファーウェイ|オッポ')
ON CONFLICT (brand_name, row_index) DO NOTHING;

-- 確認クエリ
SELECT 
    ba.brand_name,
    COUNT(bv.id) as value_count
FROM brand_attributes ba
LEFT JOIN brand_values bv ON ba.brand_name = bv.brand_name
GROUP BY ba.brand_name
ORDER BY ba.brand_name;