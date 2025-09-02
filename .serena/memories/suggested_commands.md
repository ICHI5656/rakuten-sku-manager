# 開発用コマンド一覧

## Docker操作
```bash
# システム起動（必須）
docker-compose up -d

# バックエンド再ビルド
docker-compose down && docker-compose build --no-cache backend && docker-compose up -d

# フロントエンド再ビルド
docker-compose down && docker-compose build --no-cache frontend && docker-compose up -d

# 完全再ビルド
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# ログ確認
docker logs --tail 50 rakuten-sku-backend
docker logs --tail 50 rakuten-sku-frontend
docker logs -f rakuten-sku-backend | grep DEBUG
```

## デバッグ
```bash
# Pythonスクリプト実行
docker exec rakuten-sku-backend python /app/script_name.py

# ファイルコピー
docker cp local_file.csv rakuten-sku-backend:/app/test.csv

# API確認
curl http://localhost:8000/docs
curl -X GET http://localhost:8000/api/product-attributes/brands
```

## データベース操作
```bash
# DB内容確認
docker exec rakuten-sku-backend sqlite3 /app/product_attributes_new.db "SELECT * FROM device_attributes LIMIT 10;"

# SKUカウンタリセット
docker exec rakuten-sku-backend rm /app/data/state/sku_counters.json
```

## Git操作
```bash
git status
git branch
git checkout -b feature/device-position-control
```

## テスト（タスク完了時）
```bash
# フロントエンドビルドテスト
docker exec rakuten-sku-frontend npm run build

# APIエンドポイントテスト
curl -X POST http://localhost:8000/api/process -F "file=@test.csv"
```