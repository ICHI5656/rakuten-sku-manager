# NASへのデプロイ手順

## 1. 必要なファイル
- `rakuten-sku-backend.tar` - バックエンドのDockerイメージ
- `rakuten-sku-frontend.tar` - フロントエンドのDockerイメージ
- `docker-compose.nas.yml` - Docker Compose設定ファイル
- `data/` フォルダ - データファイル用ディレクトリ

## 2. NASでの実行手順

### 2.1 Dockerイメージのロード

NASにSSH接続して、以下のコマンドを実行：

```bash
# イメージファイルをNASに転送後、以下を実行
docker load -i rakuten-sku-backend.tar
docker load -i rakuten-sku-frontend.tar
```

### 2.2 アプリケーションの起動

```bash
# docker-compose.nas.ymlがあるディレクトリで実行
docker-compose -f docker-compose.nas.yml up -d
```

### 2.3 アプリケーションへのアクセス

- **フロントエンド**: http://192.168.24.240:3000
- **バックエンドAPI**: http://192.168.24.240:8000
- **APIドキュメント**: http://192.168.24.240:8000/docs

## 3. Portainer経由でのデプロイ

Portainerを使用する場合：

1. Portainerにアクセス: http://192.168.24.240:9000
2. 「Stacks」→「Add stack」を選択
3. `docker-compose.nas.yml`の内容をコピー＆ペースト
4. 「Deploy the stack」をクリック

## 4. データのバックアップ

重要なデータは以下のディレクトリに保存されます：
- `/app/data/uploads/` - アップロードされたCSVファイル
- `/app/data/outputs/` - 処理済みCSVファイル
- `/app/data/state/` - SKU番号の管理状態
- `/app/product_attributes_new.db` - Product Attributes 8データベース

## 5. トラブルシューティング

### ログの確認
```bash
docker-compose -f docker-compose.nas.yml logs -f backend
docker-compose -f docker-compose.nas.yml logs -f frontend
```

### 再起動
```bash
docker-compose -f docker-compose.nas.yml restart
```

### 停止と削除
```bash
docker-compose -f docker-compose.nas.yml down
```

## 6. アップデート手順

1. 新しいイメージをビルド
2. tarファイルとして保存
3. NASに転送
4. 既存のコンテナを停止
5. 新しいイメージをロード
6. コンテナを再起動

## 7. セキュリティ注意事項

- このシステムは内部ネットワークでの使用を想定しています
- 外部からアクセスする場合は、適切なファイアウォール設定とHTTPS化を行ってください
- データベースファイルは定期的にバックアップしてください