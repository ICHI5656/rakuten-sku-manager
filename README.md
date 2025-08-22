# 楽天SKU管理システム

楽天RMS対応のCSV処理システム。機種の追加・削除、SKU自動採番、バリエーション展開を自動化します。

## 機能概要

- **CSV処理**: 楽天RMS仕様のCSVファイル（Shift-JIS）を読み込み・処理
- **機種管理**: バリエーション2（機種）の追加・削除
- **SKU自動採番**: sku_a000001形式での連番管理（商品ごとに独立）
- **バリエーション展開**: 全組み合わせの自動生成（cross join）
- **制約チェック**: 楽天RMS制限（最大40選択肢/属性、400SKU/商品）の自動検証
- **複数出力形式**: 単一ファイル、商品別分割、6万行自動分割

## クイックスタート

### Dockerを使用した起動

```bash
# リポジトリに移動
cd rakuten_sku_manager

# Dockerコンテナを起動
docker-compose up -d

# ブラウザでアクセス
# http://localhost:3000
```

### 停止方法

```bash
docker-compose down
```

## システム要件

- Docker Desktop 20.10以上
- Docker Compose 2.0以上
- メモリ: 4GB以上推奨
- ディスク: 10GB以上の空き容量

## 使用方法

### 1. CSVファイルのアップロード

1. ブラウザで http://localhost:3000 にアクセス
2. 楽天RMS形式のCSVファイルをドラッグ&ドロップまたは選択
3. ファイルが自動的に解析され、機種一覧が表示されます

### 2. 機種の管理

#### 機種の削除
- 既存機種リストから削除したい機種にチェック
- チェックした機種のSKU行が削除されます

#### 機種の追加
- 新機種追加フォームに機種名を入力
- 「追加」ボタンをクリック
- 新機種は既存バリエーションとの全組み合わせで展開されます

### 3. 出力形式の選択

- **1ファイルに統合**: すべての商品を1つのCSVに出力
- **商品ごとに分割**: 各商品を個別のCSVファイルに出力
- **6万行ごとに自動分割**: 大量データを楽天RMS制限に合わせて分割

### 4. ダウンロード

- 処理完了後、生成されたCSVファイルをダウンロード
- ファイルは楽天RMSに直接アップロード可能な形式（Shift-JIS、CRLF）

## 技術仕様

### バックエンド
- **言語**: Python 3.11
- **フレームワーク**: FastAPI
- **CSV処理**: pandas / polars
- **エンコーディング**: Shift-JIS対応

### フロントエンド
- **フレームワーク**: React 18 + TypeScript
- **UI**: Material-UI
- **ビルドツール**: Vite

### データ管理
- **SKU採番**: JSON形式での永続化（`data/state/sku_counters.json`）
- **アップロードファイル**: `data/uploads/`
- **出力ファイル**: `data/outputs/`

## ディレクトリ構造

```
rakuten_sku_manager/
├── backend/               # FastAPI バックエンド
│   ├── app.py            # メインアプリケーション
│   ├── services/         # ビジネスロジック
│   │   ├── csv_processor.py
│   │   ├── sku_manager.py
│   │   ├── device_manager.py
│   │   └── validator.py
│   └── models/           # データモデル
├── frontend/             # React フロントエンド
│   ├── src/
│   │   ├── components/   # UIコンポーネント
│   │   ├── services/     # API通信
│   │   └── types/        # TypeScript型定義
│   └── Dockerfile
├── data/                 # データディレクトリ
│   ├── uploads/         # アップロードファイル
│   ├── outputs/         # 出力ファイル
│   └── state/           # 状態管理
└── docker-compose.yml   # Docker構成
```

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/api/upload` | CSVファイルのアップロード |
| POST | `/api/process` | CSV処理の実行 |
| GET | `/api/download/{filename}` | 処理済みファイルのダウンロード |
| GET | `/api/devices/{file_id}` | 機種一覧の取得 |
| GET | `/api/status` | システムステータス |
| DELETE | `/api/cleanup` | 古いファイルの削除 |

## 制約事項

- **バリエーション上限**: 各属性につき最大40選択肢
- **SKU上限**: 1商品につき最大400SKU
- **ファイルサイズ**: 最大100MB
- **文字コード**: Shift-JISのみ対応
- **改行コード**: CRLF（Windows形式）

## トラブルシューティング

### ポートが使用中の場合

```bash
# ポートを変更する場合は docker-compose.yml を編集
# frontend: 3000 → 3001
# backend: 8000 → 8001
```

### メモリ不足エラー

```bash
# Docker Desktopの設定でメモリを増やす
# Settings > Resources > Memory: 8GB以上に設定
```

### 文字化けが発生する場合

- アップロードするCSVファイルがShift-JISエンコーディングであることを確認
- Excel等で保存する際は「CSV（カンマ区切り）」形式を選択

## 開発者向け情報

### ローカル開発環境

```bash
# バックエンド
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

# フロントエンド
cd frontend
npm install
npm run dev
```

### テスト実行

```bash
# バックエンドテスト
cd backend
pytest

# フロントエンドテスト
cd frontend
npm test
```

## ライセンス

このプロジェクトは内部使用を目的としています。

## サポート

問題が発生した場合は、以下を確認してください：

1. Dockerが正常に起動しているか
2. 必要なポートが空いているか
3. CSVファイルが楽天RMS仕様に準拠しているか

---

最終更新: 2025年8月