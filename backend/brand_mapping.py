"""
ブランド名マッピング定義
ブランドDB（brand_attributes.db）と商品属性8DB（product_attributes_new.db）の
ブランド名を統一するためのマッピング
"""

# ブランドDBの名前 -> 商品属性8DBの名前
BRAND_MAPPING = {
    # ブランドDB -> 商品属性8DB
    'iphone': 'iPhone',
    'Xperia': 'Xperia',
    'galaxy': 'Galaxy',
    'Google Pixel': 'Google Pixel',
    'aquos': 'AQUOS',
    'huawei': 'HUAWEI',
    'arrows': 'arrows',
    'OPPO': 'OPPO',
    'その他': 'その他',
    
    # 逆マッピング（商品属性8DB -> ブランドDB）も含む
    'iPhone': 'iPhone',
    'XPERIA': 'Xperia',
    'Galaxy': 'Galaxy',
    'AQUOS': 'AQUOS',
    'HUAWEI': 'HUAWEI',
    
    # 追加の正規化パターン
    'IPHONE': 'iPhone',
    'xperia': 'Xperia',
    'GALAXY': 'Galaxy',
    'Aquos': 'AQUOS',
    'Huawei': 'HUAWEI',
    'Arrows': 'arrows',
    'oppo': 'OPPO',
}

def normalize_brand_name(brand_name: str) -> str:
    """
    ブランド名を正規化して統一形式に変換
    
    Args:
        brand_name: 入力ブランド名
        
    Returns:
        正規化されたブランド名
    """
    if not brand_name:
        return brand_name
    
    # まず完全一致でマッピングを確認
    if brand_name in BRAND_MAPPING:
        return BRAND_MAPPING[brand_name]
    
    # 大文字小文字を無視してマッピングを確認
    for key, value in BRAND_MAPPING.items():
        if key.lower() == brand_name.lower():
            return value
    
    # マッピングにない場合はそのまま返す
    return brand_name

def get_brand_db_name(product_attr_brand: str) -> str:
    """
    商品属性8DBのブランド名からブランドDBの名前を取得
    
    Args:
        product_attr_brand: 商品属性8DBのブランド名
        
    Returns:
        ブランドDBのブランド名
    """
    # 逆マッピング辞書を作成
    reverse_mapping = {
        'iPhone': 'iphone',
        'Xperia': 'Xperia',
        'Galaxy': 'galaxy',
        'Google Pixel': 'Google Pixel',
        'AQUOS': 'aquos',
        'HUAWEI': 'huawei',
        'arrows': 'arrows',
        'OPPO': 'OPPO',
        'その他': 'その他',
    }
    
    return reverse_mapping.get(product_attr_brand, product_attr_brand)

def detect_brand_from_device_name(device_name: str) -> str:
    """
    デバイス名からブランドを自動検出
    
    Args:
        device_name: デバイス名
        
    Returns:
        検出されたブランド名（正規化済み）
    """
    if not device_name:
        return 'その他'
    
    device_lower = device_name.lower()
    
    # ブランド検出パターン
    patterns = {
        'iPhone': ['iphone', 'pro max', 'pro', 'plus', 'mini', 'se'],
        'Xperia': ['xperia', 'so-', 'sov', 'sol'],
        'Galaxy': ['galaxy', 'sc-', 'scv', 'sm-'],
        'AQUOS': ['aquos', 'sh-', 'shv', 'sense', 'wish', 'zero'],
        'Google Pixel': ['pixel', 'google'],
        'HUAWEI': ['huawei', 'mate', 'nova', 'p30', 'p40', 'hw-'],
        'arrows': ['arrows', 'f-', 'fcv', 'nx'],
        'OPPO': ['oppo', 'reno', 'find', 'a-series'],
    }
    
    for brand, keywords in patterns.items():
        for keyword in keywords:
            if keyword in device_lower:
                return brand
    
    return 'その他'