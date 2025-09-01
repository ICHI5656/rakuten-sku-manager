import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import json
import logging
import random
import re

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
                   devices_to_remove: List[str] = None, add_position: str = 'start',
                   after_device: str = None, custom_device_order: List[str] = None,
                   insert_index: int = None, brand_attributes: List[str] = None,
                   device_attributes: List[Dict] = None, apply_db_attributes_to_existing: bool = True) -> pd.DataFrame:
        """CSVを処理して機種を追加/削除（複数商品対応）"""
        
        # デバッグログ
        print(f"[DEBUG] process_csv called with:")
        print(f"  devices_to_add: {devices_to_add}")
        print(f"  devices_to_remove: {devices_to_remove}")
        print(f"  add_position: {add_position}")
        print(f"  custom_device_order: {custom_device_order}")
        
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
                print(f"[DEBUG] Processing product: {product_id}")
                
                # 機種削除
                if devices_to_remove:
                    print(f"[DEBUG] Removing devices: {devices_to_remove}")
                    sku_rows = self._remove_devices(sku_rows, devices_to_remove, device_col)
                
                # 既存のSKU行にデータベースの属性値を適用
                if apply_db_attributes_to_existing and device_attributes:
                    sku_rows = self._apply_db_attributes_to_existing(sku_rows, device_col, device_attributes)
                
                # 機種追加（実際に新規の機種のみ）
                really_new_devices = []  # 追加前に初期化
                if devices_to_add:
                    # 既存のSKU行にある機種を除外（追加前の状態で判定）
                    existing_devices_before_add = set(sku_rows[device_col].dropna().unique()) if device_col in sku_rows.columns else set()
                    really_new_devices = [d for d in devices_to_add if d not in existing_devices_before_add]
                    
                    if really_new_devices:
                        print(f"[DEBUG] Adding NEW devices: {really_new_devices}")
                        new_sku_rows = self._add_devices(
                            parent_rows, sku_rows, really_new_devices, 
                            product_id, product_col, device_col, color_col, sku_col,
                            brand_attributes, device_attributes
                        )
                        print(f"[DEBUG] Created {len(new_sku_rows)} new SKU rows")
                        sku_rows = pd.concat([new_sku_rows, sku_rows], ignore_index=True)
                    else:
                        print(f"[DEBUG] No really new devices to add (all already exist)")
                
                # バリエーション2選択肢定義を更新（親行）- 位置指定に対応
                if device_def_col in parent_rows.columns and not sku_rows.empty:
                    # devices_to_addではなくcustom_device_orderを優先的に使用
                    # custom_device_orderは完全な機種リスト（正しい順序）
                    if custom_device_order:
                        print(f"[DEBUG] Using custom_device_order for definition update")
                        parent_rows = self._update_device_definition(
                            parent_rows, sku_rows, device_col, device_def_col, 
                            devices_to_add,  # 元のリストを渡す（フィルタリングしない）
                            add_position, after_device, custom_device_order, insert_index
                        )
                    elif devices_to_add:
                        # custom_device_orderがない場合は、本当に新しい機種のみを渡す
                        print(f"[DEBUG] Using really_new_devices for definition update: {really_new_devices}")
                        parent_rows = self._update_device_definition(
                            parent_rows, sku_rows, device_col, device_def_col, 
                            really_new_devices,  # 事前に計算した本当に新しい機種
                            add_position, after_device, custom_device_order, insert_index
                        )
                    else:
                        # devices_to_addがない場合（既存の機種のみの更新）
                        parent_rows = self._update_device_definition(
                            parent_rows, sku_rows, device_col, device_def_col, 
                            [], add_position, after_device, custom_device_order, insert_index
                        )
                
                # 全てのSKU番号を新規採番（sku_aプレフィックス）
                sku_rows = self._regenerate_all_skus(sku_rows, sku_col)
                
                # システム連携用SKU番号を生成（device_attributesからsize_categoryを使用）
                sku_rows = self._generate_system_sku_numbers(sku_rows, product_id, device_col, color_col, device_attributes)
                
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
    
    def _apply_db_attributes_to_existing(self, sku_rows: pd.DataFrame, device_col: str, 
                                         device_attributes: List[Dict]) -> pd.DataFrame:
        """既存のSKU行にデータベースから取得した属性値を適用（商品属性8のみ）"""
        if sku_rows.empty or not device_attributes:
            return sku_rows
        
        # 商品属性列の列名を定義
        product_attr8_col = '商品属性（値）8'
        # 商品属性2と4は変更しない
        # product_attr2_col = '商品属性（値）2'
        # product_attr4_col = '商品属性（値）4'
        
        # device_attributesを辞書形式に変換
        device_attr_map = {}
        for attr in device_attributes:
            if isinstance(attr, dict) and 'device' in attr:
                device_attr_map[attr['device']] = attr
        
        # 各SKU行に対して商品属性8のみ適用
        if device_col in sku_rows.columns and product_attr8_col in sku_rows.columns:
            for idx, row in sku_rows.iterrows():
                device_name = row[device_col]
                if pd.notna(device_name):
                    # デバイス名を文字列に変換（99999999999などの数値も処理）
                    device_name_str = str(device_name)
                    if device_name_str in device_attr_map:
                        attr_value = device_attr_map[device_name_str].get('attribute_value')
                        if attr_value:
                            sku_rows.at[idx, product_attr8_col] = attr_value
                            print(f"[DB Apply] Updated {device_name_str} product_attr8 with: {attr_value}")
                    
                    # 商品属性2と4は変更しない（元の値を保持）
                    # if product_attr2_col in sku_rows.columns:
                    #     既存の値を保持
                    # if product_attr4_col in sku_rows.columns:
                    #     既存の値を保持（空白のまま）
        
        return sku_rows
    
    def _add_devices(self, parent_rows: pd.DataFrame, sku_rows: pd.DataFrame, 
                    devices_to_add: List[str], product_id: str,
                    product_col: str, device_col: str, color_col: str, sku_col: str,
                    brand_attributes: List[str] = None, device_attributes: List[Dict] = None) -> pd.DataFrame:
        """新しい機種のSKU行を追加"""
        
        # 商品属性列の列名を定義
        product_attr1_col = '商品属性（値）1'
        product_attr8_col = '商品属性（値）8'
        product_attr2_col = '商品属性（値）2'  # attribute_value用
        product_attr3_col = '商品属性（値）3'  # size用
        product_attr4_col = '商品属性（値）4'  # size_category用
        
        # device_attributesを辞書形式に変換
        device_attr_map = {}
        if device_attributes:
            for attr in device_attributes:
                if isinstance(attr, dict) and 'device' in attr:
                    device_attr_map[attr['device']] = attr
        
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
                    
                    # デバイス固有の属性を設定（商品属性2と4は変更しない）
                    if device in device_attr_map:
                        device_info = device_attr_map[device]
                        
                        # 商品属性（値）2は変更しない（元の値を保持）
                        # if product_attr2_col in new_row.index and device_info.get('attribute_value'):
                        #     new_row[product_attr2_col] = device_info['attribute_value']
                        #     print(f"[DEBUG] Set product_attr2 for {device}: {device_info['attribute_value']}")
                        
                        # sizeを商品属性（値）3に設定（これは残す）
                        if product_attr3_col in new_row.index and device_info.get('size'):
                            new_row[product_attr3_col] = device_info['size']
                            print(f"[DEBUG] Set product_attr3 for {device}: {device_info['size']}")
                        
                        # 商品属性（値）4は変更しない（空白のまま）
                        # if product_attr4_col in new_row.index and device_info.get('size_category'):
                        #     new_row[product_attr4_col] = device_info['size_category']
                        #     print(f"[DEBUG] Set product_attr4 for {device}: {device_info['size_category']}")
                    
                    # 商品属性（値）1にランダムな属性値を設定
                    if product_attr1_col in new_row.index and brand_attributes:
                        # brand_attributesからランダムに1つ選択
                        random_attribute = random.choice(brand_attributes)
                        new_row[product_attr1_col] = random_attribute
                        print(f"[DEBUG] Set product_attr1 for {device}: {random_attribute}")
                    
                    # 商品属性（値）8にattribute_valueを設定（device_attributesから取得）
                    if product_attr8_col in new_row.index:
                        # device_attributesから対応するattribute_valueを取得
                        if device in device_attr_map and device_attr_map[device].get('attribute_value'):
                            attribute_value = device_attr_map[device]['attribute_value']
                            new_row[product_attr8_col] = attribute_value
                            print(f"[DEBUG] Set product_attr8 (attribute_value) for {device}: {attribute_value}")
                        else:
                            # device_attributesがない場合はdevice名をそのまま設定
                            new_row[product_attr8_col] = device
                            print(f"[DEBUG] Set product_attr8 (fallback to device_name) for {device}: {device}")
                    
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
    
    def _generate_system_sku_numbers(self, sku_rows: pd.DataFrame, product_id: str, 
                                    device_col: str, color_col: str, 
                                    device_attributes: List[Dict] = None) -> pd.DataFrame:
        """システム連携用SKU番号を生成（size_categoryを使用）"""
        system_sku_col = 'システム連携用SKU番号'
        
        # システム連携用SKU番号列が存在しない場合は作成
        if system_sku_col not in sku_rows.columns:
            sku_rows[system_sku_col] = ''
        
        # device_attributesを辞書形式に変換
        device_size_map = {}
        if device_attributes:
            for attr in device_attributes:
                if isinstance(attr, dict) and 'device' in attr:
                    device_name = attr['device']
                    size_category = attr.get('size_category', '')
                    if size_category:
                        device_size_map[device_name] = size_category
        
        # 各SKU行に対してシステム連携用SKU番号を生成
        for idx, row in sku_rows.iterrows():
            # 商品ID、デバイス、カラーを取得
            device = row.get(device_col, '')
            color = row.get(color_col, '')
            
            if pd.notna(device) and pd.notna(color):
                # デバイスのサイズカテゴリを取得（なければ空文字）
                size_category = device_size_map.get(device, '')
                
                # カラーから不要な部分を除去（A.ベージュ/グリーン → ベージュ/グリーン）
                # "A."や"B."などのプレフィックスを削除
                clean_color = re.sub(r'^[A-Z]\.\s*', '', str(color))
                
                # システム連携用SKU番号を構築
                # 形式: kaiser_huawei_色_LL（固定）
                system_sku = f"{product_id}_{clean_color}_LL"
                
                sku_rows.at[idx, system_sku_col] = system_sku
                print(f"[DEBUG] Generated system SKU: {system_sku}")
        
        return sku_rows
    
    def _update_device_definition(self, parent_rows: pd.DataFrame, sku_rows: pd.DataFrame,
                                 device_col: str, device_def_col: str, 
                                 devices_to_add: List[str] = None, add_position: str = 'start',
                                 after_device: str = None, custom_device_order: List[str] = None,
                                 insert_index: int = None) -> pd.DataFrame:
        """バリエーション2選択肢定義を更新（全機種リスト）"""
        print(f"[DEBUG] _update_device_definition called with:")
        print(f"  add_position: {add_position}")
        print(f"  after_device: {after_device}")
        print(f"  custom_device_order: {custom_device_order}")
        print(f"  devices_to_add: {devices_to_add}")
        
        if device_col not in sku_rows.columns:
            return parent_rows
        
        # SKU行から全機種を取得（順序を保持）
        all_sku_devices = []
        seen_devices = set()
        for device in sku_rows[device_col].dropna():
            device_str = str(device)
            if device_str not in seen_devices:
                all_sku_devices.append(device_str)
                seen_devices.add(device_str)
        
        print(f"[DEBUG] All devices in current SKU rows (order preserved): {all_sku_devices}")
        
        # 親行から元の機種リストを取得（処理前の状態、順序を保持）
        original_devices_from_parent = []
        if device_def_col in parent_rows.columns:
            for _, row in parent_rows.iterrows():
                var_def = row.get(device_def_col)
                if pd.notna(var_def) and var_def:
                    original_devices_from_parent = [d.strip() for d in str(var_def).split('|') if d.strip()]
                    break
        
        print(f"[DEBUG] Original devices from parent (order preserved): {original_devices_from_parent}")
        
        # 元の親行定義がある場合はそれを基準とし、ない場合はSKU行の順序を使用
        if original_devices_from_parent:
            base_device_order = original_devices_from_parent
        else:
            base_device_order = all_sku_devices
        
        # devices_to_addが指定されている場合の処理
        if devices_to_add:
            print(f"[DEBUG] devices_to_add: {devices_to_add}")
            
            # 新規機種の判定：devices_to_addの中で、基準リストに存在しない機種
            base_device_set = set(base_device_order)
            new_devices = [d for d in devices_to_add if d not in base_device_set]
            
        else:
            new_devices = []
        
        print(f"[DEBUG] New devices identified: {new_devices}")
        print(f"[DEBUG] Base device order: {base_device_order}")
        
        # 位置指定に基づいて機種リストを組み立て
        # custom_device_orderが存在する場合、それが最終的な機種順序
        if custom_device_order:
            # custom_device_orderは完全な順序付きリスト（新規機種も正しい位置に含まれている）
            print(f"[DEBUG] Using custom_device_order directly: {custom_device_order}")
            device_list = list(custom_device_order)
        elif not new_devices:
            # 新規機種がない場合は元の順序を維持
            device_list = base_device_order
        elif add_position == 'start':
            # リストの先頭に追加
            device_list = new_devices + base_device_order
        elif add_position == 'end':
            # リストの末尾に追加
            device_list = base_device_order + new_devices
        elif add_position == 'after' and after_device:
            # 特定機種の後に追加
            print(f"[DEBUG] Looking for after_device: '{after_device}' in base_device_order")
            print(f"[DEBUG] base_device_order: {base_device_order}")
            print(f"[DEBUG] new_devices to insert: {new_devices}")
            
            device_list = []
            found_position = False
            
            # 基準デバイスを順番に処理
            for device in base_device_order:
                device_list.append(device)
                print(f"[DEBUG] Checking device: '{device}' == '{after_device}' ? {device == after_device}")
                if device == after_device:
                    print(f"[DEBUG] Found after_device! Inserting new devices: {new_devices}")
                    device_list.extend(new_devices)
                    found_position = True
            
            # after_deviceが見つからない場合は末尾に追加
            if not found_position:
                print(f"[DEBUG] after_device '{after_device}' not found in base_device_order, adding at end")
                device_list.extend(new_devices)
        else:
            # デフォルトは元の順序を維持して先頭に新機種を追加
            device_list = new_devices + base_device_order
        
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