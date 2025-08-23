import pandas as pd
from typing import Dict, List

class Validator:
    def __init__(self):
        self.max_variations_per_attribute = 40
        self.max_skus_per_product = 400
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict:
        """Validate DataFrame against Rakuten RMS constraints"""
        errors = []
        warnings = []
        
        # Check if required columns exist
        required_columns = ['商品管理番号（商品URL）']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate by product
        if '商品管理番号（商品URL）' in df.columns:
            grouped = df.groupby('商品管理番号（商品URL）')
            
            for product_id, group in grouped:
                # Check variation limits
                for i in range(1, 7):
                    col_name = f'バリエーション{i}:選択肢'
                    if col_name in group.columns:
                        unique_count = group[col_name].dropna().nunique()
                        if unique_count > self.max_variations_per_attribute:
                            errors.append(
                                f"Product {product_id}: Variation {i} has {unique_count} options "
                                f"(max: {self.max_variations_per_attribute})"
                            )
                
                # Check total SKU count
                sku_count = len(group)
                if sku_count > self.max_skus_per_product:
                    errors.append(
                        f"Product {product_id}: Has {sku_count} SKUs "
                        f"(max: {self.max_skus_per_product})"
                    )
                elif sku_count > self.max_skus_per_product * 0.9:
                    warnings.append(
                        f"Product {product_id}: Has {sku_count} SKUs "
                        f"(approaching limit of {self.max_skus_per_product})"
                    )
        
        # Check for duplicate SKUs
        if 'SKU管理番号' in df.columns:
            # Filter out empty SKUs and check for duplicates
            non_empty_skus = df[df['SKU管理番号'].notna() & (df['SKU管理番号'] != '')]
            if len(non_empty_skus) > 0:
                sku_duplicates = non_empty_skus['SKU管理番号'].duplicated()
                if sku_duplicates.any():
                    duplicate_skus = non_empty_skus[sku_duplicates]['SKU管理番号'].unique()
                    errors.append(f"Duplicate SKUs found: {', '.join(duplicate_skus[:5])}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_encoding(self, text: str) -> bool:
        """Check if text can be encoded in Shift-JIS"""
        try:
            text.encode('shift_jis')
            return True
        except UnicodeEncodeError:
            return False
    
    def clean_for_shiftjis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame for Shift-JIS encoding"""
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: self._clean_text(x) if pd.notna(x) else x)
        return df
    
    def _clean_text(self, text: str) -> str:
        """Clean text to be Shift-JIS compatible"""
        if not isinstance(text, str):
            return str(text)
        
        # Try to encode as Shift-JIS, replace problematic characters
        try:
            text.encode('shift_jis')
            return text
        except UnicodeEncodeError:
            # Replace problematic characters
            cleaned = []
            for char in text:
                try:
                    char.encode('shift_jis')
                    cleaned.append(char)
                except UnicodeEncodeError:
                    # Replace with placeholder or skip
                    cleaned.append('?')
            return ''.join(cleaned)
    
    def check_data_integrity(self, df: pd.DataFrame) -> Dict:
        """Check overall data integrity"""
        issues = []
        
        # Check for empty DataFrame
        if df.empty:
            issues.append("DataFrame is empty")
        
        # Check for required variation structure
        has_variations = False
        for i in range(1, 7):
            if f'バリエーション{i}:選択肢' in df.columns:
                has_variations = True
                break
        
        if not has_variations:
            issues.append("No variation columns found")
        
        # Check for mixed encoding issues
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = df[col].dropna().head(100)
                for value in sample:
                    if not self.validate_encoding(str(value)):
                        issues.append(f"Column '{col}' contains non-Shift-JIS characters")
                        break
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues
        }