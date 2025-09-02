#!/bin/bash
# GitHub Container Registryへのプッシュスクリプト

# 設定
GITHUB_USERNAME="your-github-username"
GITHUB_TOKEN="your-github-token"  # https://github.com/settings/tokens で作成

echo "GitHub Container Registryへのプッシュ"
echo "====================================="

# GitHub Container Registryにログイン
echo ""
echo "GitHub Container Registryにログイン中..."
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# イメージのタグ付け
echo ""
echo "イメージをタグ付け中..."
docker tag rakuten_sku_manager-backend:latest ghcr.io/$GITHUB_USERNAME/rakuten-sku-backend:latest
docker tag rakuten_sku_manager-frontend:latest ghcr.io/$GITHUB_USERNAME/rakuten-sku-frontend:latest

# イメージのプッシュ
echo ""
echo "バックエンドイメージをプッシュ中..."
docker push ghcr.io/$GITHUB_USERNAME/rakuten-sku-backend:latest

echo ""
echo "フロントエンドイメージをプッシュ中..."
docker push ghcr.io/$GITHUB_USERNAME/rakuten-sku-frontend:latest

echo ""
echo "完了！"
echo ""
echo "Portainerで使用するイメージ名："
echo "- ghcr.io/$GITHUB_USERNAME/rakuten-sku-backend:latest"
echo "- ghcr.io/$GITHUB_USERNAME/rakuten-sku-frontend:latest"