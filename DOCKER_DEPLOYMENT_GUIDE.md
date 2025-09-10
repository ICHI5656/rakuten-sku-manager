# 別のパソコンでDockerを使って起動する手順

## 前提条件
- Docker Desktop または Docker Engine がインストール済み
- Git がインストール済み（またはZIPファイルでダウンロード可能）

## 方法1: Gitを使う場合

### 1. リポジトリをクローン
```bash
git clone https://github.com/ICHI5656/rakuten-sku-manager.git
cd rakuten-sku-manager
```

### 2. 環境変数ファイルを作成
`backend/.env` ファイルを作成し、必要な環境変数を設定：
```env
# Supabase設定（必要に応じて）
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# その他の設定
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 3. Dockerコンテナを起動
```bash
docker compose up -d
```

### 4. アプリケーションにアクセス
ブラウザで以下のURLを開く：
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## 方法2: ZIPファイルを使う場合

### 1. GitHubからZIPをダウンロード
1. https://github.com/ICHI5656/rakuten-sku-manager にアクセス
2. 緑色の「Code」ボタンをクリック
3. 「Download ZIP」を選択
4. ダウンロードしたZIPファイルを解凍

### 2. コマンドプロンプトまたはターミナルを開く
```bash
# 解凍したフォルダに移動
cd path/to/rakuten-sku-manager

# Dockerコンテナを起動
docker compose up -d
```

## 方法3: 既存のDockerイメージを使う場合（ネットワーク経由）

現在のPCでDockerイメージをエクスポート：
```bash
# イメージをファイルに保存
docker save -o rakuten-sku-frontend.tar rakuten-sku-manager-frontend
docker save -o rakuten-sku-backend.tar rakuten-sku-manager-backend
```

別のPCでイメージをインポート：
```bash
# イメージを読み込み
docker load -i rakuten-sku-frontend.tar
docker load -i rakuten-sku-backend.tar

# docker-compose.ymlファイルがある場所で起動
docker compose up -d
```

## トラブルシューティング

### ポートが使用中の場合
`docker-compose.yml`を編集してポートを変更：
```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # 3000の代わりに3001を使用
  backend:
    ports:
      - "8001:8000"  # 8000の代わりに8001を使用
```

### コンテナの状態確認
```bash
# コンテナの状態を確認
docker compose ps

# ログを確認
docker compose logs -f

# 特定のサービスのログを確認
docker compose logs -f backend
docker compose logs -f frontend
```

### コンテナの再起動
```bash
# 全サービスを再起動
docker compose restart

# 特定のサービスを再起動
docker compose restart backend
docker compose restart frontend
```

### 完全にリセットする場合
```bash
# コンテナを停止して削除
docker compose down

# ボリュームも含めて削除
docker compose down -v

# イメージも含めて削除
docker compose down --rmi all

# 再度ビルドして起動
docker compose up -d --build
```

## ネットワーク設定（同一ネットワーク内の別PCからアクセス）

### 現在のPCのIPアドレスを確認
Windows:
```cmd
ipconfig
```

Mac/Linux:
```bash
ifconfig
# または
ip addr
```

### 別のPCからアクセス
IPアドレスが `192.168.1.100` の場合：
- フロントエンド: http://192.168.1.100:3000
- バックエンドAPI: http://192.168.1.100:8000

### ファイアウォールの設定
Windowsの場合、ファイアウォールでポート3000と8000を許可する必要があります：
1. Windows Defenderファイアウォールを開く
2. 「詳細設定」をクリック
3. 「受信の規則」→「新しい規則」
4. ポート3000と8000を許可

## Docker Desktopの設定（Windows）

### WSL2統合を有効にする
1. Docker Desktop設定を開く
2. 「Resources」→「WSL Integration」
3. 使用するLinuxディストリビューションを有効化

### リソース制限の調整
1. Docker Desktop設定を開く
2. 「Resources」→「Advanced」
3. 必要に応じてCPU、メモリを調整

## 必要なディスク容量
- Dockerイメージ: 約1.5GB
- アプリケーションファイル: 約50MB
- 合計: 約2GB以上の空き容量を推奨

## システム要件
- RAM: 4GB以上（8GB推奨）
- CPU: 2コア以上
- OS: Windows 10/11, macOS 10.15+, Linux（Docker対応）