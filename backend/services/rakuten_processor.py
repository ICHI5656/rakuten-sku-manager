import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import json
import logging

logger = logging.getLogger(__name__)

class RakutenCSVProcessor:
    """楽天RMS CSV処理クラス - 正しい親子構造を維持"""
    
    def __init__(self, sku_state_file: Path = None):
        self.sku_state_file = sku_state_file
        self.global_sku_counter = self._load_global_counter()
        self.used_sku_numbers = self._load_used_skus()
        
    def _load_global_counter(self) -> int:
        """グローバルSKUカウンターを読み込み"""
        if self.sku_state_file and self.sku_state_file.exists():
            with open(self.sku_state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('global_counter', 0)
        return 0
    
    def _load_used_skus(self) -> set:
        """使用済みSKU番号を読み込み"""
        if self.sku_state_file and self.sku_state_file.exists():
            with open(self.sku_state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('used_skus', []))
        return set()
    
    def _save_sku_state(self):
        """SKU採番状態を保存"""
        if self.sku_state_file:
            self.sku_state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.sku_state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'global_counter': self.global_sku_counter,
                    'used_skus': list(self.used_sku_numbers)
                }, f, ensure_ascii=False, indent=2)
    
    def process_csv(self, df: pd.DataFrame, devices_to_add: List[str] = None, 
                   devices_to_remove: List[str] = None) -> pd.DataFrame:
        """CSVを処理して機種を追加/削除（複数商品対応）"""
        
        # 商品管理番号の列を特定
        product_col = '商品管理番号（商品URL）'
        sku_col = 'SKU管理番号'
        device_col = 'バリエーション項目選択肢2'
        color_col = 'バリエーション項目選択肢1'
        device_def_col = 'バリエーション2選択肢定義'  # 機種定義列
        
        # 複数商品を分割して処理
        products = self._split_products(df, product_col, sku_col)
        
        result_dfs = []
        
        for product_data in products:
            parent_rows = product_data['parent_rows']
            sku_rows = product_data['sku_rows']
            
            if not parent_rows.empty:
                product_id = parent_rows.iloc[0][product_col]
                
                # 機種削除
                if devices_to_remove:
                    sku_rows = self._remove_devices(sku_rows, devices_to_remove, device_col)
                
                # 機種追加
                if devices_to_add:
                    new_sku_rows = self._add_devices(
                        parent_rows, sku_rows, devices_to_add, 
                        product_id, product_col, device_col, color_col, sku_col
                    )
                    sku_rows = pd.concat([new_sku_rows, sku_rows], ignore_index=True)
                
                # バリエーション2選択肢定義を更新（親行）- 新機種を先頭に配置
                if device_def_col in parent_rows.columns and not sku_rows.empty:
                    parent_rows = self._update_device_definition(
                        parent_rows, sku_rows, device_col, device_def_col, devices_to_add
                    )
                
                # 全てのSKU番号を新規採番（sku_aプレフィックス）
                sku_rows = self._regenerate_all_skus(sku_rows, sku_col)
                
                # 親行とSKU行を結合
                product_result = pd.concat([parent_rows, sku_rows], ignore_index=True)
                result_dfs.append(product_result)
        
        # 全商品を結合
        if result_dfs:
            result = pd.concat(result_dfs, ignore_index=True)
            # SKU状態を保存
            self._save_sku_state()
            return result
        
        return df
    
    def _split_products(self, df: pd.DataFrame, product_col: str, sku_col: str) -> List[Dict]:
        """複数商品を分割（同じ商品IDは同じ商品、異なるIDは別商品）"""
        # 商品IDごとにグループ化
        products_dict = {}
        
        for idx, row in df.iterrows():
            has_product = pd.notna(row.get(product_col, None)) and row.get(product_col, '') != ''
            has_sku = pd.notna(row.get(sku_col, None)) and row.get(sku_col, '') != ''
            
            if has_product:
                product_id = row[product_col]
                
                # この商品IDが初めての場合、初期化
                if product_id not in products_dict:
                    products_dict[product_id] = {
                        'parent_rows': [],
                        'sku_rows': [],
                        'product_id': product_id
                    }
                
                if not has_sku:
                    # 親行
                    products_dict[product_id]['parent_rows'].append(row)
                else:
                    # SKU行
                    products_dict[product_id]['sku_rows'].append(row)
            elif has_sku and products_dict:
                # 商品IDがないがSKUがある行（前の商品のSKU行）
                # 最後に処理した商品のSKU行として追加
                last_product_id = list(products_dict.keys())[-1]
                products_dict[last_product_id]['sku_rows'].append(row)
        
        # 辞書からリストに変換
        products = []
        for product_id, product_data in products_dict.items():
            products.append({
                'parent_rows': pd.DataFrame(product_data['parent_rows']),
                'sku_rows': pd.DataFrame(product_data['sku_rows']) if product_data['sku_rows'] else pd.DataFrame(),
                'product_id': product_id
            })
        
        print(f"Found {len(products)} unique products (by 商品管理番号)")
        for i, product in enumerate(products):
            product_id = product.get('product_id', 'Unknown')
            print(f"  Product {i+1} ({product_id}): {len(product['parent_rows'])} parent rows, {len(product['sku_rows'])} SKU rows")
        
        return products
    
    def _split_parent_sku_rows(self, df: pd.DataFrame, product_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """親行（商品情報）とSKU行を分離"""
        # 親行: 商品管理番号があり、かつSKU管理番号が空の最初の連続行
        parent_mask = pd.Series([False] * len(df))
        sku_start_idx = -1
        
        for i, row in df.iterrows():
            # SKU管理番号が入っている最初の行を見つける
            if pd.notna(row.get('SKU管理番号', None)) and row.get('SKU管理番号', '') != '':
                sku_start_idx = i
                break
        
        if sku_start_idx > 0:
            parent_mask[:sku_start_idx] = True
            parent_rows = df[parent_mask].copy()
            sku_rows = df[~parent_mask].copy()
        else:
            # SKU行がない場合は、商品管理番号がある最初の行だけを親行とする
            parent_rows = df.iloc[:1].copy()
            sku_rows = df.iloc[1:].copy() if len(df) > 1 else pd.DataFrame()
        
        return parent_rows, sku_rows
    
    def _remove_devices(self, sku_rows: pd.DataFrame, devices_to_remove: List[str], 
                       device_col: str) -> pd.DataFrame:
        """指定された機種のSKU行を削除"""
        if device_col not in sku_rows.columns:
            return sku_rows
        
        mask = ~sku_rows[device_col].isin(devices_to_remove)
        return sku_rows[mask].copy()
    
    def _add_devices(self, parent_rows: pd.DataFrame, sku_rows: pd.DataFrame, 
                    devices_to_add: List[str], product_id: str,
                    product_col: str, device_col: str, color_col: str, sku_col: str) -> pd.DataFrame:
        """新しい機種のSKU行を追加"""
        
        # 商品属性（値）8の列名を定義
        product_attr8_col = '商品属性（値）8'
        
        # 既存のカラーバリエーションと対応するSKU行を取得
        color_sku_map = {}
        if color_col in sku_rows.columns:
            # 各カラーの最初のSKU行を取得（テンプレートとして使用）
            for color in sku_rows[color_col].dropna().unique():
                color_rows = sku_rows[sku_rows[color_col] == color]
                if not color_rows.empty:
                    color_sku_map[color] = color_rows.iloc[0].copy()
        
        if not color_sku_map:
            # カラーバリエーションがない場合
            if not sku_rows.empty:
                base_row = sku_rows.iloc[0].copy()
                color_sku_map[''] = base_row
            else:
                base_row = parent_rows.iloc[0].copy()
                color_sku_map[''] = base_row
        
        new_rows = []
        for device in devices_to_add:
            # 既存の機種をチェック
            if device_col in sku_rows.columns:
                if device in sku_rows[device_col].values:
                    continue  # すでに存在する機種はスキップ
            
            # 各カラーごとに新しいSKU行を作成
            # カラーの順序を保持（元データの順序）
            sorted_colors = []
            if color_col in sku_rows.columns:
                # 元データでの出現順を維持
                for _, row in sku_rows.iterrows():
                    color = row[color_col]
                    if pd.notna(color) and color not in sorted_colors:
                        sorted_colors.append(color)
            else:
                sorted_colors = list(color_sku_map.keys())
            
            for i, color in enumerate(sorted_colors):
                if color in color_sku_map:
                    new_row = color_sku_map[color].copy()
                    
                    # 商品管理番号を設定
                    new_row[product_col] = product_id
                    
                    # デバイスを設定
                    if device_col in new_row.index:
                        new_row[device_col] = device
                    
                    # 商品属性（値）8に機種名を設定（例: HUAWEI Mate 20 Pro）
                    if product_attr8_col in new_row.index:
                        # デバイス名から "HUAWEI" プレフィックスを追加（まだない場合）
                        device_display_name = device
                        if 'Mate' in device or 'nova' in device or 'P30' in device or 'P20' in device:
                            if not device.startswith('HUAWEI'):
                                device_display_name = f"HUAWEI {device.replace('(', '').replace(')', '')}"
                                # 括弧内の型番は残す
                                if '(' in device:
                                    device_display_name = f"HUAWEI {device.split('(')[0].strip()}"
                        new_row[product_attr8_col] = device_display_name
                    
                    # SKU番号は後で全体的に再採番するので、一時的に空にする
                    new_row[sku_col] = ""
                    
                    new_rows.append(new_row)
        
        if new_rows:
            return pd.DataFrame(new_rows)
        
        return pd.DataFrame()
    
    def _regenerate_all_skus(self, sku_rows: pd.DataFrame, sku_col: str) -> pd.DataFrame:
        """全てのSKU番号を新規採番（sku_aプレフィックス、重複なし）"""
        if sku_col not in sku_rows.columns or sku_rows.empty:
            return sku_rows
        
        # 全ての行に新しいSKU番号を割り当て
        for idx in sku_rows.index:
            # 次の未使用番号を見つける
            while True:
                self.global_sku_counter += 1
                new_sku = f"sku_a{self.global_sku_counter:06d}"
                
                # この番号が未使用であることを確認
                if new_sku not in self.used_sku_numbers:
                    sku_rows.at[idx, sku_col] = new_sku
                    self.used_sku_numbers.add(new_sku)
                    break
        
        return sku_rows
    
    def _update_device_definition(self, parent_rows: pd.DataFrame, sku_rows: pd.DataFrame,
                                 device_col: str, device_def_col: str, 
                                 devices_to_add: List[str] = None) -> pd.DataFrame:
        """バリエーション2選択肢定義を更新（全機種リスト）"""
        if device_col not in sku_rows.columns:
            return parent_rows
        
        # SKU行から全機種を取得
        all_devices = sku_rows[device_col].dropna().unique()
        print(f"All devices found: {all_devices}")
        print(f"Number of parent rows to update: {len(parent_rows)}")
        
        # 新機種を先頭に配置
        device_list = []
        new_devices = []
        existing_devices = []
        
        # 追加した機種リストを取得
        devices_to_add_set = set(devices_to_add) if devices_to_add else set()
        
        for device in all_devices:
            device_str = str(device)
            # 新規追加機種を先頭に
            if device_str in devices_to_add_set:
                new_devices.append(device_str)
            else:
                existing_devices.append(device_str)
        
        # 新機種を先頭、その後既存機種
        device_list = new_devices + existing_devices
        
        # パイプ区切りで結合（楽天RMS仕様）
        device_definition = '|'.join(device_list)
        print(f"Device definition string: {device_definition}")
        
        # すべての親行のバリエーション2選択肢定義を確実に更新
        updated_count = 0
        for idx in parent_rows.index:
            if device_def_col in parent_rows.columns:
                parent_rows.loc[idx, device_def_col] = device_definition
                updated_count += 1
                print(f"Updated parent row at index {idx}")
        
        print(f"Total parent rows updated: {updated_count}")
        
        # 確認のため、更新後の値をチェック
        if device_def_col in parent_rows.columns:
            unique_defs = parent_rows[device_def_col].unique()
            print(f"Unique device definitions after update: {len(unique_defs)}")
            for def_val in unique_defs[:2]:  # 最初の2つを表示
                print(f"  - {str(def_val)[:100]}...")
        
        return parent_rows