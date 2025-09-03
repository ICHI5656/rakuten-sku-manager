# 🚀 ローカルPC環境セットアップ手順

## 📋 必要なソフトウェア

1. **Git** - プロジェクトをダウンロード
   - https://git-scm.com/downloads

2. **Docker Desktop** - コンテナ実行環境
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - Mac: https://docs.docker.com/desktop/install/mac-install/

## 📦 セットアップ手順

### Step 1: GitHubからクローン

```bash
# コマンドプロンプトまたはPowerShellで実行
# 任意の場所にプロジェクトをクローン
git clone https://github.com/ICHI5656/rakuten-sku-manager.git

# プロジェクトフォルダに移動
cd rakuten-sku-manager
```

### Step 2: Docker Desktopを起動

1. Docker Desktopアプリケーションを起動
2. タスクトレイのDockerアイコンが緑色になるまで待つ
3. 設定でメモリを最低2GB以上に設定（推奨4GB）

### Step 3: システムを起動

#### Windows の場合
```cmd
# プロジェクトフォルダで実行
start-local.bat
```

#### Mac/Linux の場合
```bash
# 実行権限を付与
chmod +x start-local.sh

# 起動
./start-local.sh
```

または直接Dockerコマンドで：
```bash
docker-compose up -d
```

### Step 4: ブラウザでアクセス

起動完了後、以下のURLにアクセス：
- **フロントエンド**: http://localhost:3000
- **API ドキュメント**: http://localhost:8000/docs

## 🔄 更新方法

最新版を取得する場合：

```bash
# 1. 現在のコンテナを停止
docker-compose down

# 2. 最新のコードを取得
git pull origin master

# 3. Dockerイメージを再ビルド
docker-compose build --no-cache

# 4. 起動
docker-compose up -d
```

## 🛠 よく使うコマンド

### 起動・停止
```bash
# 起動
docker-compose up -d

# 停止
docker-compose down

# 再起動
docker-compose restart

# ログ確認
docker-compose logs -f
```

### トラブルシューティング
```bash
# コンテナ状態確認
docker-compose ps

# ログ確認（最新50行）
docker-compose logs --tail 50

# コンテナに入る
docker exec -it rakuten-sku-backend bash

# 全削除してやり直し
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## ⚙️ 環境変数設定（オプション）

Supabaseを使用する場合は `.env` ファイルを作成：

```env
# .env ファイル
USE_SUPABASE=false
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 📱 動作確認チェックリスト

- [ ] Docker Desktop が起動している
- [ ] `docker-compose ps` で両方のコンテナが "Up" 状態
- [ ] http://localhost:3000 でフロントエンドが表示される
- [ ] CSVファイルのアップロードができる
- [ ] 機種選択でブランドドロップダウンが表示される

## ❗ トラブルシューティング

### ポートが使用中のエラー
他のアプリがポート3000または8000を使用している場合、`docker-compose.yml`で変更：
```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # 3001に変更
  backend:
    ports:
      - "8001:8000"  # 8001に変更
```

### Dockerメモリ不足エラー
Docker Desktop の設定：
- Settings → Resources → Advanced
- Memory: 4GB以上に設定

### ブラウザでアクセスできない
1. ファイアウォールの設定確認
2. `docker-compose logs` でエラー確認
3. ブラウザのキャッシュクリア（Ctrl+F5）

## 📝 注意事項

- 初回起動時はDockerイメージのダウンロードで時間がかかります（約5-10分）
- データは `./data` フォルダに保存されます
- 本番環境では適切なセキュリティ設定を行ってください

## 🆘 サポート

問題が発生した場合：
1. `docker-compose logs --tail 100` でエラーログ確認
2. GitHubのIssuesに報告: https://github.com/ICHI5656/rakuten-sku-manager/issues