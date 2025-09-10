#!/usr/bin/env python3
"""
商品画像ALT処理サービス
楽天RMS CSVの商品画像ALTタグを商品名で自動設定
"""
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AltProcessor:
    """商品画像ALT処理クラス"""
    
    # 定数定義
    TITLE_COL = "商品名"
    ID_COL = "商品管理番号（商品URL）"
    IMG_TYPE_COLS = [f"商品画像タイプ{i}" for i in range(1, 21)]
    IMG_ALT_COLS = [f"商品画像名（ALT）{i}" for i in range(1, 21)]
    
    def process_csv(self, input_path: Path, output_path: Path, encoding: str = "cp932") -> dict:
        """
        CSVファイルのALTタグを処理
        
        Args:
            input_path: 入力CSVファイルパス
            output_path: 出力CSVファイルパス
            encoding: 文字エンコーディング（デフォルト: cp932/Shift_JIS）
            
        Returns:
            処理結果の情報を含む辞書
        """
        try:
            # CSVを読み込み
            df = pd.read_csv(input_path, encoding=encoding)
            logger.info(f"CSVファイル読み込み完了: {len(df)}行")
            
            # 必須列チェック
            missing = [c for c in [self.TITLE_COL, self.ID_COL] if c not in df.columns]
            if missing:
                raise ValueError(f"必須列が見つかりません: {missing}")
            
            # 処理可能な画像タイプ/ALT列のペアを特定（SKU画像は除外）
            usable_pairs = []
            for i in range(1, 21):
                type_col = f"商品画像タイプ{i}"
                alt_col = f"商品画像名（ALT）{i}"
                if type_col in df.columns and alt_col in df.columns:
                    usable_pairs.append((type_col, alt_col))
            
            if not usable_pairs:
                logger.warning("対応する画像タイプ/ALT列が見つかりません")
                df.to_csv(output_path, index=False, encoding=encoding)
                return {
                    "status": "warning",
                    "message": "処理可能な画像列が見つかりませんでした",
                    "processed_count": 0
                }
            
            # 親行（各商品管理番号グループの最初の行）のインデックスを取得
            parent_indices = df.groupby(self.ID_COL, sort=False).head(1).index
            
            processed_count = 0
            updated_alts = []
            
            # 親行のみ処理
            for idx in parent_indices:
                title = df.at[idx, self.TITLE_COL]
                title_str = "" if pd.isna(title) else str(title)
                product_id = df.at[idx, self.ID_COL]
                
                row_updated = False
                for type_col, alt_col in usable_pairs:
                    # SKU画像はスキップ（念のため確認）
                    if 'SKU' in type_col or 'SKU' in alt_col:
                        continue
                        
                    # 商品画像タイプに値が入っているかチェック
                    val = df.at[idx, type_col] if type_col in df.columns else None
                    has_type = (
                        val is not None and 
                        not (isinstance(val, float) and pd.isna(val)) and 
                        str(val).strip() != ""
                    )
                    
                    if has_type:
                        # ALTを商品名で強制上書き
                        df.at[idx, alt_col] = title_str
                        row_updated = True
                        updated_alts.append({
                            "product_id": product_id,
                            "column": alt_col,
                            "new_value": title_str
                        })
                
                if row_updated:
                    processed_count += 1
            
            # SKU画像のALTタグを明示的にクリア（全行）
            if 'SKU画像名（ALT）' in df.columns:
                df['SKU画像名（ALT）'] = ''
                logger.info("SKU画像名（ALT）をクリアしました")
            
            # 処理後のCSVを保存
            df.to_csv(output_path, index=False, encoding=encoding, lineterminator='\r\n')
            
            logger.info(f"ALT処理完了: {processed_count}個の親行を処理")
            
            return {
                "status": "success",
                "message": f"{processed_count}個の商品のALTタグを更新しました",
                "processed_count": processed_count,
                "total_products": len(parent_indices),
                "updated_columns": len(updated_alts)
            }
            
        except Exception as e:
            logger.error(f"ALT処理エラー: {str(e)}")
            raise