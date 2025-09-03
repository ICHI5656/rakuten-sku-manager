#!/bin/bash

echo "======================================"
echo "楽天SKU管理システム - ローカル起動"
echo "======================================"
echo ""

# Docker が起動しているか確認
if ! docker version > /dev/null 2>&1; then
    echo "[エラー] Docker が起動していません。"
    echo "Docker Desktop を起動してから再実行してください。"
    exit 1
fi

echo "[1/4] Dockerコンテナを停止しています..."
docker-compose down

echo ""
echo "[2/4] Dockerイメージをビルドしています..."
docker-compose build

echo ""
echo "[3/4] Dockerコンテナを起動しています..."
docker-compose up -d

echo ""
echo "[4/4] 起動を確認しています..."
sleep 5

# ヘルスチェック
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "======================================"
    echo "✅ システムが正常に起動しました！"
    echo "======================================"
    echo ""
    echo "アクセスURL:"
    echo "  フロントエンド: http://localhost:3000"
    echo "  バックエンドAPI: http://localhost:8000/docs"
    echo ""
    echo "停止するには: docker-compose down"
    echo "ログを見るには: docker-compose logs -f"
else
    echo ""
    echo "[エラー] コンテナの起動に失敗しました。"
    echo "ログを確認してください:"
    docker-compose logs --tail 50
    exit 1
fi