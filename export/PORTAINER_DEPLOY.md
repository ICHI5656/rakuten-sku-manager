# Portainerでのデプロイ手順

## 方法1: イメージのアップロードとスタック作成

### ステップ1: Portainerにアクセス
1. ブラウザで http://192.168.24.240:9000 にアクセス
2. ログイン

### ステップ2: Dockerイメージのインポート
1. 左メニューから「Images」をクリック
2. 「Import」ボタンをクリック
3. 「Upload」タブを選択
4. 以下のファイルをアップロード：
   - `backend.tar` → イメージ名: `rakuten-sku-backend:latest`
   - `frontend-fixed.tar` → イメージ名: `rakuten-sku-frontend:latest`

### ステップ3: スタックの作成
1. 左メニューから「Stacks」をクリック
2. 「Add stack」ボタンをクリック
3. Stack名: `rakuten-sku`
4. 「Web editor」に以下のYAMLを貼り付け：

```yaml
version: '3.8'

services:
  backend:
    image: rakuten-sku-backend:latest
    container_name: rakuten-sku-backend
    ports:
      - "8000:8000"
    volumes:
      - /var/rakuten_data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped

  frontend:
    image: rakuten-sku-frontend:latest
    container_name: rakuten-sku-frontend
    ports:
      - "3000:80"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

5. 「Deploy the stack」ボタンをクリック

## 方法2: コマンドラインでイメージをロード後、Portainerで管理

### ステップ1: SSHでNASに接続
```bash
ssh quest@192.168.24.240
# パスワード: Ichio_22520113
```

### ステップ2: イメージをロード
```bash
cd /home/quest/rakuten-sku
sudo docker load -i backend.tar
sudo docker load -i frontend.tar
```

### ステップ3: Portainerでスタック作成
1. Portainerにアクセス
2. 「Stacks」→「Add stack」
3. 上記のYAMLを使用してデプロイ

## アクセス確認
- アプリケーション: http://192.168.24.240:3000
- API ドキュメント: http://192.168.24.240:8000/docs

## トラブルシューティング

### ポートが使用中の場合
Portainerで既存のコンテナを停止・削除してから再デプロイ

### イメージが見つからない場合
Imagesページでイメージ名を確認：
- `rakuten-sku-backend:latest`
- `rakuten-sku-frontend:latest`

### ログの確認
Containers → コンテナ名をクリック → Logs