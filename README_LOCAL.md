# 楽天SKU管理システム - ローカル環境セットアップガイド

## 📋 前提条件

1. **Docker Desktop** がインストールされていること
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - Mac: https://docs.docker.com/desktop/install/mac-install/

2. **メモリ要件**
   - 最低4GB以上の空きメモリ
   - Docker Desktopに2GB以上のメモリを割り当て

## 🚀 クイックスタート

### Windows の場合

1. **Docker Desktop を起動**
   - スタートメニューから「Docker Desktop」を起動
   - タスクトレイのDockerアイコンが緑色になるまで待つ

2. **システムを起動**
   ```cmd
   # プロジェクトフォルダに移動
   cd C:\rakuten_sku_manager
   
   # 起動スクリプトを実行
   start-local.bat
   ```

3. **ブラウザでアクセス**
   - http://localhost:3000 - フロントエンド
   - http://localhost:8000/docs - API ドキュメント

### Mac/Linux の場合

1. **Docker Desktop を起動**

2. **システムを起動**
   ```bash
   # プロジェクトフォルダに移動
   cd ~/rakuten_sku_manager
   
   # 起動
   docker-compose up -d
   ```

## 🛠 基本操作

### システムの起動
```cmd
# Windows
start-local.bat

# Mac/Linux
docker-compose up -d
```

### システムの停止
```cmd
# Windows
stop-local.bat

# Mac/Linux
docker-compose down
```

### ログの確認
```cmd
# すべてのログを見る
docker-compose logs -f

# バックエンドのログのみ
docker-compose logs -f backend

# フロントエンドのログのみ
docker-compose logs -f frontend
```

### 再起動
```cmd
docker-compose restart
```

## 📁 ファイル構成

```
rakuten_sku_manager/
├── frontend/              # Reactフロントエンド
│   ├── src/              # ソースコード
│   ├── package.json      # npm依存関係
│   └── Dockerfile        # フロントエンドコンテナ設定
│
├── backend/              # FastAPIバックエンド
│   ├── app.py           # メインアプリケーション
│   ├── requirements.txt  # Python依存関係
│   └── Dockerfile       # バックエンドコンテナ設定
│
├── data/                # データ永続化
│   ├── state/          # SKUカウンター状態
│   └── uploads/        # アップロードファイル
│
├── docker-compose.yml   # Docker構成
├── start-local.bat     # Windows起動スクリプト
└── stop-local.bat      # Windows停止スクリプト
```

## ⚙️ 設定変更

### ポート番号を変更したい場合

`docker-compose.yml` を編集:
```yaml
services:
  frontend:
    ports:
      - "3000:3000"  # 左側の数字を変更（例: "3001:3000"）
  
  backend:
    ports:
      - "8000:8000"  # 左側の数字を変更（例: "8001:8000"）
```

### メモリ制限を設定したい場合

`docker-compose.yml` に追加:
```yaml
services:
  backend:
    mem_limit: 1g
    memswap_limit: 1g
```

## 🔧 トラブルシューティング

### Docker Desktop が起動しない
- Windowsの場合、WSL2が有効になっているか確認
- BIOSで仮想化（Virtualization）が有効になっているか確認

### ポート使用中エラー
```
Error: bind: address already in use
```
- 別のアプリケーションがポート3000または8000を使用している
- `docker-compose.yml` でポート番号を変更

### コンテナが起動しない
```cmd
# コンテナの状態を確認
docker-compose ps

# 詳細なログを確認
docker-compose logs --tail 100
```

### ブラウザでアクセスできない
1. Docker Desktopが起動しているか確認
2. コンテナが正常に起動しているか確認: `docker-compose ps`
3. ファイアウォール設定を確認

### データをリセットしたい場合
```cmd
# 全データを削除（注意！）
docker-compose down -v
rmdir /s /q data
```

## 📊 パフォーマンス調整

### Docker Desktop の設定
1. Docker Desktop の設定を開く
2. Resources → Advanced
3. 以下を推奨値に設定:
   - CPUs: 2以上
   - Memory: 4GB以上
   - Swap: 1GB
   - Disk image size: 20GB以上

## 🔐 セキュリティ注意事項

- このシステムはローカル開発用です
- インターネットに公開しないでください
- 本番環境では適切なセキュリティ設定が必要です

## 📝 更新方法

システムを更新する場合:
```cmd
# 1. コンテナを停止
docker-compose down

# 2. 最新のコードを取得（Gitを使用している場合）
git pull

# 3. イメージを再ビルド
docker-compose build --no-cache

# 4. 起動
docker-compose up -d
```

## 💡 便利なコマンド

```cmd
# コンテナに入る
docker exec -it rakuten-sku-backend bash
docker exec -it rakuten-sku-frontend sh

# データベースを確認
docker exec rakuten-sku-backend sqlite3 /app/product_attributes_new.db

# 使用容量を確認
docker system df

# 不要なデータを削除
docker system prune -a
```

## 📧 サポート

問題が解決しない場合は、以下の情報を準備してください：
- Docker Desktop のバージョン: `docker version`
- エラーログ: `docker-compose logs --tail 100`
- OS情報（Windows/Mac/Linux、バージョン）