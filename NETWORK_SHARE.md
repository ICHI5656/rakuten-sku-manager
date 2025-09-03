# 🌐 ネットワーク共有セットアップガイド

同じLAN内の他のPCからシステムにアクセスできるようにする設定です。

## 📋 前提条件

- ホストPCでDockerが動作している
- すべてのPCが同じネットワーク（LAN）に接続されている
- Windowsファイアウォールまたはセキュリティソフトが通信を許可している

## 🚀 ホストPC（サーバー側）の設定

### Step 1: ファイアウォール設定

**管理者権限**でコマンドプロンプトを開いて実行：

```cmd
# 管理者権限で実行
configure-firewall.bat
```

または手動で設定：
1. Windows Defender ファイアウォール → 詳細設定
2. 受信の規則 → 新しい規則
3. ポート → TCP → 特定のローカルポート「3000, 8000」
4. 接続を許可する
5. プライベートネットワークにチェック
6. 名前「Rakuten SKU Manager」

### Step 2: システムを起動

```cmd
# ネットワーク共有モードで起動
start-network.bat
```

このスクリプトは自動的に：
- ホストPCのIPアドレスを検出
- ネットワーク用の設定でDockerコンテナを起動
- アクセスURLを表示

### Step 3: IPアドレスの確認

起動時に表示される、または以下のコマンドで確認：

```cmd
ipconfig
```

例：`192.168.1.100`

## 💻 クライアントPC（アクセスする側）の設定

### ブラウザでアクセス

ホストPCのIPアドレスを使ってアクセス：

- **フロントエンド**: `http://192.168.1.100:3000`
- **API**: `http://192.168.1.100:8000/docs`

※ `192.168.1.100` は実際のホストPCのIPアドレスに置き換えてください

## 🔧 詳細設定

### 固定IPアドレスの設定（推奨）

ホストPCに固定IPを設定すると、毎回同じアドレスでアクセスできます：

1. コントロールパネル → ネットワークと共有センター
2. アダプター設定の変更 → イーサネットを右クリック → プロパティ
3. インターネットプロトコル バージョン4 (TCP/IPv4) → プロパティ
4. 「次のIPアドレスを使う」を選択：
   - IPアドレス: `192.168.1.100`（例）
   - サブネットマスク: `255.255.255.0`
   - デフォルトゲートウェイ: `192.168.1.1`（ルーターのIP）

### ポート番号の変更

`docker-compose.network.yml` を編集：

```yaml
services:
  frontend:
    ports:
      - "0.0.0.0:3001:3000"  # 3001に変更
  backend:
    ports:
      - "0.0.0.0:8001:8000"  # 8001に変更
```

## 🔒 セキュリティ設定

### アクセス制限（推奨）

特定のIPアドレスからのみアクセスを許可する場合：

1. **nginx設定** (`frontend/nginx.conf`)に追加：
```nginx
location / {
    # 特定のIPからのみ許可
    allow 192.168.1.0/24;  # ローカルネットワーク
    deny all;
    
    root /usr/share/nginx/html;
    try_files $uri /index.html;
}
```

2. **バックエンドCORS設定** (`backend/app.py`)：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.1.100:3000", "http://localhost:3000"],  # 特定のオリジンのみ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### HTTPS設定（オプション）

本格的に運用する場合は、SSL証明書を設定してHTTPS化を推奨。

## 🖥️ 同時アクセス数

- 推奨: 5-10台程度
- 最大: 20-30台（ホストPCのスペック次第）

多数のアクセスが予想される場合は、専用サーバーの利用を検討してください。

## ❗ トラブルシューティング

### アクセスできない場合

1. **pingテスト**
```cmd
# クライアントPCから
ping 192.168.1.100
```

2. **ファイアウォール確認**
```cmd
# ホストPCで
netsh advfirewall firewall show rule name="Rakuten SKU Manager Frontend"
```

3. **Dockerポート確認**
```cmd
# ホストPCで
netstat -an | findstr "3000"
netstat -an | findstr "8000"
```

4. **セキュリティソフトの確認**
- Windows Defender
- ウイルス対策ソフト
- 企業のセキュリティポリシー

### 遅い・重い場合

1. **ホストPCのリソース確認**
```cmd
# タスクマネージャーで確認
# CPU、メモリ、ネットワーク使用率
```

2. **Docker設定調整**
```yaml
# docker-compose.network.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

3. **同時アクセス数を制限**

## 📊 パフォーマンス監視

### アクセスログ確認
```bash
# フロントエンドのアクセスログ
docker logs -f rakuten-sku-frontend

# バックエンドのアクセスログ
docker logs -f rakuten-sku-backend
```

### リソース使用状況
```bash
docker stats
```

## 🔄 更新方法

ネットワーク共有中にシステムを更新：

1. 接続中のユーザーに通知
2. システム停止
```cmd
docker-compose down
```
3. 更新を取得
```cmd
git pull origin master
```
4. 再起動
```cmd
start-network.bat
```

## 📱 モバイルデバイスからのアクセス

同じWi-Fiネットワークに接続していれば、スマートフォンやタブレットからもアクセス可能：

1. Wi-Fi設定で同じネットワークに接続
2. ブラウザで `http://192.168.1.100:3000` にアクセス

※ レスポンシブデザインではないため、PCブラウザでの利用を推奨

## 🚨 注意事項

- **社内ネットワーク**: IT部門の許可を得てから使用してください
- **セキュリティ**: 機密データを扱う場合は適切なセキュリティ対策を実施
- **ライセンス**: 商用利用の場合はライセンスを確認
- **負荷**: 多数の同時アクセスはホストPCに負荷がかかります

## 📞 サポート

問題が発生した場合の確認事項：
- ホストPCのIPアドレス
- ファイアウォールの状態
- Dockerコンテナの状態: `docker-compose ps`
- エラーログ: `docker-compose logs --tail 100`