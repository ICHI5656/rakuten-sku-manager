#!/bin/bash
# NASへの自動デプロイスクリプト

# 設定
NAS_IP="192.168.24.240"
NAS_USER="admin"
PROJECT_NAME="rakuten-sku-manager"
NAS_DEPLOY_PATH="/volume1/docker/$PROJECT_NAME"

echo "==================================="
echo "楽天SKU管理システム NASデプロイ"
echo "==================================="

# 1. 必要なファイルをNASに転送
echo ""
echo "1. 設定ファイルをNASに転送中..."
ssh $NAS_USER@$NAS_IP "mkdir -p $NAS_DEPLOY_PATH"

# docker-compose.ymlを転送
scp docker-compose.nas.yml $NAS_USER@$NAS_IP:$NAS_DEPLOY_PATH/docker-compose.yml

# 2. NASでGitHubからコードを取得してビルド
echo ""
echo "2. NASでDockerイメージをビルド中..."
ssh $NAS_USER@$NAS_IP << 'ENDSSH'
cd /volume1/docker/rakuten-sku-manager

# GitHubからクローン（既存の場合はpull）
if [ ! -d ".git" ]; then
    git clone https://github.com/your-username/rakuten-sku-manager.git .
else
    git pull origin main
fi

# Dockerイメージをビルド
docker-compose build

# 古いコンテナを停止
docker-compose down

# 新しいコンテナを起動
docker-compose up -d

echo ""
echo "デプロイ完了！"
echo "アクセスURL:"
echo "- フロントエンド: http://192.168.24.240:3000"
echo "- バックエンドAPI: http://192.168.24.240:8000/docs"
ENDSSH