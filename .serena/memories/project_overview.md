# 楽天SKUマネージャー プロジェクト概要

## プロジェクトの目的
Rakuten RMS CSV処理のためのDockerベースWebアプリケーション。機種バリエーション管理、SKU自動生成、クロスジョイン展開を行う。

## 技術スタック
- **Backend**: Python (FastAPI), pandas, SQLite
- **Frontend**: React, TypeScript, Material-UI, Vite
- **Infrastructure**: Docker, Docker Compose
- **Database**: SQLite (product_attributes_new.db)

## コーディング規約
- Python: snake_case、型ヒントなし、日本語コメント
- TypeScript/React: camelCase、型定義必須、関数コンポーネント
- ファイルエンコーディング: Shift-JIS (入出力CSV)、UTF-8 (ソースコード)

## プロジェクト構造
```
rakuten_sku_manager/
├── backend/
│   ├── app.py                    # FastAPI メインアプリケーション
│   ├── services/
│   │   ├── rakuten_processor.py  # CSV処理、機種管理
│   │   ├── csv_processor.py      # エンコーディング処理
│   │   └── sku_manager.py        # SKU採番管理
│   └── product_attributes_api_v2.py # データベース操作
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DeviceManager.tsx      # 機種管理UI
│   │   │   ├── DeviceOrderEditor.tsx  # 機種順序編集
│   │   │   └── FileUpload.tsx         # CSVアップロード
│   │   └── services/api.ts            # API通信
└── docker-compose.yml
```

## 重要なビジネスルール
1. 親行（商品管理番号あり、SKU管理番号なし）にバリエーション定義
2. SKU行（両方あり）は色×機種の全組み合わせ
3. 機種位置制御の優先順位：
   - custom_device_order（完全な順序リスト）
   - add_position（start/end/after）
   - デフォルト（既存順序維持）