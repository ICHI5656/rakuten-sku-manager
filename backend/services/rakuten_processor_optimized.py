"""
最適化版 Rakuten CSV Processor
パフォーマンス改善点:
- ロギングレベルの最適化
- ベクトル化処理
- 不要な重複コードの削除
- メモリ効率の改善
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
import json
import logging
from pathlib import Path
import gc
from functools import lru_cache

# ロギングレベルを本番向けに調整
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class RakutenCSVProcessorOptimized:
    """最適化版Rakuten CSV処理クラス"""
    
    def __init__(self, sku_state_file: str = '/app/data/state/sku_counters.json'):
        self.sku_state_file = Path(sku_state_file)
        self.global_sku_counter = self._load_global_counter()
        self.used_sku_numbers = self._load_used_skus()
        
        # キャッシュ設定
        self._device_cache = {}
        self._attribute_cache = {}
        
        # カラム名定数（繰り返しアクセスを高速化）
        self.PRODUCT_COL = '商品管理番号（商品URL）'
        self.SKU_COL = 'SKU管理番号'
        self.DEVICE_COL = 'バリエーション項目選択肢2'
        self.COLOR_COL = 'バリエーション項目選択肢1'
        self.DEVICE_DEF_COL = 'バリエーション2選択肢定義'
        self.COLOR_DEF_COL = 'バリエーション1選択肢定義'
    
    def _load_global_counter(self) -> int:
        """グローバルSKUカウンターを読み込み"""
        if self.sku_state_file.exists():
            with open(self.sku_state_file, 'r') as f:
                data = json.load(f)
                return data.get('global_counter', 1)
        return 1
    
    def _load_used_skus(self) -> set:
        """使用済みSKU番号を読み込み"""
        if self.sku_state_file.exists():
            with open(self.sku_state_file, 'r') as f:
                data = json.load(f)
                return set(data.get('used_skus', []))
        return set()
    
    def _save_sku_state(self):
        """SKU状態を保存"""
        self.sku_state_file.parent.mkdir(parents=True, exist_ok=True)
        state = {
            'global_counter': self.global_sku_counter,
            'used_skus': list(self.used_sku_numbers)
        }
        with open(self.sku_state_file, 'w') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def process_csv(self, df: pd.DataFrame, 
                   devices_to_add: List[str] = None,
                   devices_to_remove: List[str] = None,
                   add_position: str = 'start',
                   after_device: str = None,
                   custom_device_order: List[str] = None,
                   insert_index: int = None,
                   brand_attributes: List[str] = None,
                   device_attributes: List[Dict] = None,
                   apply_db_attributes_to_existing: bool = True,
                   reset_all_devices: bool = False) -> pd.DataFrame:
        """CSV処理メイン関数（最適化版）"""
        
        # メモリ最適化: データ型を最適化
        df = self._optimize_dtypes(df)
        
        # 商品を分割して処理
        products = self._split_products_fast(df)
        
        # 並列処理可能な商品を処理
        result_dfs = self._process_products_vectorized(
            products, devices_to_add, devices_to_remove,
            add_position, after_device, custom_device_order,
            device_attributes, apply_db_attributes_to_existing,
            reset_all_devices
        )
        
        if result_dfs:
            result = pd.concat(result_dfs, ignore_index=True)
            self._save_sku_state()
            
            # メモリ解放
            del result_dfs
            gc.collect()
            
            return result
        
        return df
    
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrameのデータ型を最適化してメモリ使用量を削減"""
        for col in df.columns:
            if col in [self.PRODUCT_COL, self.SKU_COL, self.DEVICE_COL, self.COLOR_COL]:
                # 重要な列はそのまま
                continue
            
            col_type = df[col].dtype
            if col_type == 'object':
                # カテゴリ型に変換可能な場合は変換
                unique_ratio = len(df[col].unique()) / len(df[col])
                if unique_ratio < 0.5:
                    df[col] = df[col].astype('category')
        
        return df
    
    def _split_products_fast(self, df: pd.DataFrame) -> List[Dict]:
        """商品を高速分割"""
        products = []
        
        # 親行、オプション行、SKU行を一括で識別
        parent_mask = (df[self.PRODUCT_COL].notna() & 
                      (df[self.SKU_COL].isna() | (df[self.SKU_COL] == '')))
        
        option_mask = ((df['選択肢タイプ'].notna()) | 
                      (df['商品オプション項目名'].notna())) if '選択肢タイプ' in df.columns else pd.Series([False] * len(df))
        
        sku_mask = (df[self.PRODUCT_COL].notna() & 
                   df[self.SKU_COL].notna() & 
                   (df[self.SKU_COL] != ''))
        
        # グループ化して処理
        for product_id, group_df in df.groupby(self.PRODUCT_COL, dropna=True):
            product_data = {
                'product_id': product_id,
                'parent_rows': group_df[parent_mask & (group_df[self.PRODUCT_COL] == product_id)].copy(),
                'option_rows': group_df[option_mask & (group_df[self.PRODUCT_COL] == product_id)].copy(),
                'sku_rows': group_df[sku_mask & (group_df[self.PRODUCT_COL] == product_id)].copy()
            }
            products.append(product_data)
        
        return products
    
    def _process_products_vectorized(self, products: List[Dict],
                                    devices_to_add: List[str],
                                    devices_to_remove: List[str],
                                    add_position: str,
                                    after_device: str,
                                    custom_device_order: List[str],
                                    device_attributes: List[Dict],
                                    apply_db_attributes_to_existing: bool,
                                    reset_all_devices: bool) -> List[pd.DataFrame]:
        """商品をベクトル化処理"""
        result_dfs = []
        
        for product_data in products:
            parent_rows = product_data['parent_rows']
            sku_rows = product_data['sku_rows']
            option_rows = product_data['option_rows']
            
            if parent_rows.empty:
                continue
            
            # バリエーション定義を一括クリア
            sku_rows = self._clear_variation_definitions_vectorized(sku_rows)
            
            # デバイス処理
            if reset_all_devices:
                sku_rows = self._reset_all_devices_fast(
                    parent_rows, custom_device_order or devices_to_add or []
                )
            else:
                # デバイス削除（ベクトル化）
                if devices_to_remove and not sku_rows.empty:
                    sku_rows = sku_rows[~sku_rows[self.DEVICE_COL].isin(devices_to_remove)]
                
                # デバイス追加
                if devices_to_add:
                    new_rows = self._add_devices_vectorized(
                        parent_rows, sku_rows, devices_to_add,
                        device_attributes
                    )
                    if not new_rows.empty:
                        sku_rows = pd.concat([new_rows, sku_rows], ignore_index=True)
            
            # デバイス定義更新
            if not sku_rows.empty:
                parent_rows = self._update_device_definition_fast(
                    parent_rows, sku_rows, custom_device_order,
                    add_position, after_device
                )
                
                # SKU採番（ベクトル化）
                sku_rows = self._generate_skus_vectorized(sku_rows)
            
            # 結果を結合
            result_parts = [parent_rows]
            if not option_rows.empty:
                result_parts.append(option_rows)
            if not sku_rows.empty:
                result_parts.append(sku_rows)
            
            result_dfs.append(pd.concat(result_parts, ignore_index=True))
        
        return result_dfs
    
    def _clear_variation_definitions_vectorized(self, df: pd.DataFrame) -> pd.DataFrame:
        """バリエーション定義を一括クリア"""
        if df.empty:
            return df
        
        variation_cols = [self.DEVICE_DEF_COL, self.COLOR_DEF_COL]
        for col in variation_cols:
            if col in df.columns:
                df[col] = ''
        
        return df
    
    def _reset_all_devices_fast(self, parent_rows: pd.DataFrame, 
                               devices: List[str]) -> pd.DataFrame:
        """全デバイスリセット（高速版）"""
        if not devices or parent_rows.empty:
            return pd.DataFrame()
        
        # テンプレート行から必要な情報を取得
        template = parent_rows.iloc[0].copy()
        
        # 色のバリエーションを取得（存在する場合）
        colors = [None]  # デフォルト
        
        # クロスジョインでSKU行を生成
        rows = []
        for device in devices:
            for color in colors:
                row = template.copy()
                row[self.DEVICE_COL] = device
                if color:
                    row[self.COLOR_COL] = color
                row[self.SKU_COL] = ''
                row[self.DEVICE_DEF_COL] = ''
                row[self.COLOR_DEF_COL] = ''
                rows.append(row)
        
        return pd.DataFrame(rows)
    
    def _add_devices_vectorized(self, parent_rows: pd.DataFrame,
                               sku_rows: pd.DataFrame,
                               devices: List[str],
                               device_attributes: List[Dict]) -> pd.DataFrame:
        """デバイス追加（ベクトル化版）"""
        if parent_rows.empty or not devices:
            return pd.DataFrame()
        
        # 既存デバイスを取得
        existing_devices = set()
        if not sku_rows.empty and self.DEVICE_COL in sku_rows.columns:
            existing_devices = set(sku_rows[self.DEVICE_COL].dropna().unique())
        
        # 追加が必要なデバイスのみフィルタ
        devices_to_add = [d for d in devices if d not in existing_devices]
        
        if not devices_to_add:
            return pd.DataFrame()
        
        # 色のバリエーションを取得
        colors = self._get_colors_from_skus(sku_rows)
        
        # バッチでSKU行を作成
        template = parent_rows.iloc[0].copy()
        rows = []
        
        for device in devices_to_add:
            # デバイス属性を取得
            attribute = self._get_device_attribute(device, device_attributes)
            
            for color in colors:
                row = template.copy()
                row[self.DEVICE_COL] = device
                if color:
                    row[self.COLOR_COL] = color
                row[self.SKU_COL] = ''
                row['商品属性（値）8'] = attribute if attribute else ''
                rows.append(row)
        
        return pd.DataFrame(rows)
    
    def _get_device_attribute(self, device: str, 
                             attributes: List[Dict]) -> Optional[str]:
        """デバイス属性を取得"""
        if not attributes:
            return None
        
        for attr in attributes:
            if isinstance(attr, dict) and attr.get('device') == device:
                return attr.get('attribute_value')
        return None
    
    def _get_colors_from_skus(self, sku_rows: pd.DataFrame) -> List[Optional[str]]:
        """SKU行から色のリストを取得"""
        if sku_rows.empty or self.COLOR_COL not in sku_rows.columns:
            return [None]
        
        colors = sku_rows[self.COLOR_COL].dropna().unique()
        return list(colors) if len(colors) > 0 else [None]
    
    def _update_device_definition_fast(self, parent_rows: pd.DataFrame,
                                      sku_rows: pd.DataFrame,
                                      custom_order: List[str],
                                      add_position: str,
                                      after_device: str) -> pd.DataFrame:
        """デバイス定義を高速更新"""
        if sku_rows.empty or self.DEVICE_COL not in sku_rows.columns:
            return parent_rows
        
        # 現在のデバイスリストを取得
        current_devices = sku_rows[self.DEVICE_COL].dropna().unique().tolist()
        
        # カスタムオーダーがある場合はそれを使用
        if custom_order:
            device_list = custom_order
        else:
            device_list = current_devices
        
        # デバイス定義文字列を作成
        device_def = '##'.join(device_list) if device_list else ''
        
        # 親行のデバイス定義を更新
        if self.DEVICE_DEF_COL in parent_rows.columns:
            parent_rows[self.DEVICE_DEF_COL] = device_def
        
        return parent_rows
    
    def _generate_skus_vectorized(self, sku_rows: pd.DataFrame) -> pd.DataFrame:
        """SKUを一括生成（ベクトル化）"""
        if sku_rows.empty:
            return sku_rows
        
        # 空のSKUをマスク
        empty_mask = (sku_rows[self.SKU_COL].isna()) | (sku_rows[self.SKU_COL] == '')
        num_needed = empty_mask.sum()
        
        if num_needed > 0:
            # NumPyで高速生成
            start = self.global_sku_counter
            sku_numbers = np.arange(start, start + num_needed)
            new_skus = np.char.add('sku_a', np.char.zfill(sku_numbers.astype(str), 6))
            
            # 一括割り当て
            sku_rows.loc[empty_mask, self.SKU_COL] = new_skus
            
            # カウンター更新
            self.global_sku_counter = start + num_needed
            self.used_sku_numbers.update(new_skus.tolist())
        
        return sku_rows


def migrate_to_optimized():
    """既存のプロセッサーを最適化版に移行"""
    print("Migrating to optimized Rakuten CSV Processor...")
    return RakutenCSVProcessorOptimized()