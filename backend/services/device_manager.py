import pandas as pd
from typing import List, Dict, Set

class DeviceManager:
    def __init__(self):
        # Try multiple possible column names for compatibility
        self.device_columns = [
            'バリエーション2:選択肢',
            'バリエーション項目選択肢2',
            'バリエーション2選択肢定義'
        ]
        self.device_column = None  # Will be set dynamically
        self.device_attribute_column = '商品属性（値）8'  # Device attribute column
        self.color_attribute_column = '商品属性（値）3'  # Color attribute column
    
    def extract_devices(self, df: pd.DataFrame) -> List[str]:
        """Extract unique device names from DataFrame"""
        devices = set()
        
        print(f"[DEBUG] Extracting devices from DataFrame with {len(df)} rows")
        
        # Try to extract from variation definition column (parent rows)
        var_def_col = 'バリエーション2選択肢定義'
        if var_def_col in df.columns:
            print(f"[DEBUG] Found {var_def_col} column")
            for value in df[var_def_col].dropna().unique():
                if value and str(value).strip():
                    # Split pipe-delimited list
                    device_list = [d.strip() for d in str(value).split('|') if d.strip()]
                    print(f"[DEBUG] Extracted from variation def: {device_list}")
                    devices.update(device_list)
        
        # Also extract from SKU rows
        sku_device_col = 'バリエーション項目選択肢2'
        if sku_device_col in df.columns:
            print(f"[DEBUG] Found {sku_device_col} column")
            device_values = df[sku_device_col].dropna().unique()
            device_values = [str(d).strip() for d in device_values if d and str(d).strip()]
            print(f"[DEBUG] Extracted from SKU rows: {device_values}")
            devices.update(device_values)
        
        # Fallback to old method if neither column exists
        if not devices:
            print(f"[DEBUG] No devices found, trying fallback method")
            self.device_column = None
            for col_name in self.device_columns:
                if col_name in df.columns:
                    self.device_column = col_name
                    break
            
            if self.device_column and self.device_column in df.columns:
                device_values = df[self.device_column].dropna().unique()
                device_values = [d for d in device_values if d and str(d).strip()]
                devices.update(device_values)
        
        # Sort and return as list
        result = sorted(list(devices))
        print(f"[DEBUG] Final extracted devices: {result}")
        return result
    
    def add_devices(self, df: pd.DataFrame, devices_to_add: List[str]) -> pd.DataFrame:
        """Add new devices to DataFrame"""
        if not devices_to_add:
            return df
        
        # Ensure device_column is set
        if not self.device_column:
            for col_name in self.device_columns:
                if col_name in df.columns:
                    self.device_column = col_name
                    break
        
        result_dfs = []
        
        if '商品管理番号（商品URL）' in df.columns:
            grouped = df.groupby('商品管理番号（商品URL）')
            
            for product_id, group in grouped:
                # Get existing devices
                existing_devices = set()
                if self.device_column and self.device_column in group.columns:
                    existing_devices = set(group[self.device_column].dropna().unique())
                
                # Add new devices that don't exist
                new_devices = [d for d in devices_to_add if d not in existing_devices]
                
                if new_devices:
                    # Get base row for copying attributes
                    base_row = group.iloc[0].copy()
                    
                    # Get other variations (not device)
                    other_variations = self._get_other_variations(group)
                    
                    # Create new rows for each new device
                    new_rows = []
                    for device in new_devices:
                        if other_variations:
                            # Create combination with other variations
                            for var_combo in other_variations:
                                new_row = base_row.copy()
                                new_row[self.device_column] = device
                                
                                # Set other variations
                                for var_num, var_value in var_combo.items():
                                    if var_num != 2:  # Skip device variation
                                        new_row[f'バリエーション{var_num}:選択肢'] = var_value
                                
                                # Update device attribute
                                if self.device_attribute_column in new_row.index:
                                    new_row[self.device_attribute_column] = device
                                
                                # Clear SKU for new row
                                if 'SKU管理番号' in new_row.index:
                                    new_row['SKU管理番号'] = None
                                
                                new_rows.append(new_row)
                        else:
                            # No other variations, just add device
                            new_row = base_row.copy()
                            new_row[self.device_column] = device
                            
                            # Update device attribute
                            if self.device_attribute_column in new_row.index:
                                new_row[self.device_attribute_column] = device
                            
                            # Clear SKU for new row
                            if 'SKU管理番号' in new_row.index:
                                new_row['SKU管理番号'] = None
                            
                            new_rows.append(new_row)
                    
                    # Combine existing and new rows
                    if new_rows:
                        new_df = pd.DataFrame(new_rows)
                        # Put new devices at the beginning
                        group = pd.concat([new_df, group], ignore_index=True)
                
                result_dfs.append(group)
        
        if result_dfs:
            return pd.concat(result_dfs, ignore_index=True)
        
        return df
    
    def remove_devices(self, df: pd.DataFrame, devices_to_remove: List[str]) -> pd.DataFrame:
        """Remove specified devices from DataFrame"""
        if not devices_to_remove:
            return df
        
        # Ensure device_column is set
        if not self.device_column:
            for col_name in self.device_columns:
                if col_name in df.columns:
                    self.device_column = col_name
                    break
        
        if not self.device_column or self.device_column not in df.columns:
            return df
        
        # Create mask for rows to keep
        mask = ~df[self.device_column].isin(devices_to_remove)
        
        # Filter DataFrame
        filtered_df = df[mask].copy()
        
        # Reset index
        filtered_df.reset_index(drop=True, inplace=True)
        
        return filtered_df
    
    def _get_other_variations(self, group: pd.DataFrame) -> List[Dict[int, str]]:
        """Get all variation combinations except device (variation 2)"""
        variations = {}
        
        # Collect variations 1, 3-6 (skip 2 which is device)
        for i in [1, 3, 4, 5, 6]:
            col_name = f'バリエーション{i}:選択肢'
            if col_name in group.columns:
                unique_values = group[col_name].dropna().unique()
                if len(unique_values) > 0:
                    variations[i] = unique_values.tolist()
        
        if not variations:
            return []
        
        # Generate all combinations
        import itertools
        keys = sorted(variations.keys())
        values = [variations[k] for k in keys]
        
        combinations = []
        for combo in itertools.product(*values):
            combo_dict = {}
            for idx, key in enumerate(keys):
                combo_dict[key] = combo[idx]
            combinations.append(combo_dict)
        
        return combinations
    
    def update_device_attributes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Update device-related attributes in DataFrame"""
        # Ensure device_column is set
        if not self.device_column:
            for col_name in self.device_columns:
                if col_name in df.columns:
                    self.device_column = col_name
                    break
        
        if self.device_column and self.device_column in df.columns and self.device_attribute_column in df.columns:
            # Sync device attribute with device variation
            df[self.device_attribute_column] = df[self.device_column]
        
        return df
    
    def validate_device_count(self, df: pd.DataFrame) -> Dict[str, int]:
        """Validate device count per product"""
        device_counts = {}
        
        # Ensure device_column is set
        if not self.device_column:
            for col_name in self.device_columns:
                if col_name in df.columns:
                    self.device_column = col_name
                    break
        
        if '商品管理番号（商品URL）' in df.columns and self.device_column and self.device_column in df.columns:
            grouped = df.groupby('商品管理番号（商品URL）')
            
            for product_id, group in grouped:
                unique_devices = group[self.device_column].dropna().nunique()
                device_counts[product_id] = unique_devices
        
        return device_counts