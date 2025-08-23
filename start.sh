#!/bin/bash

echo "楽天SKU管理システムを起動しています..."

# Build and start containers
docker-compose up --build -d

# Wait for services to be ready
echo "サービスの起動を待っています..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✓ システムが正常に起動しました"
    echo ""
    echo "アクセスURL:"
    echo "  http://localhost:3000"
    echo ""
    echo "停止するには: docker-compose down"
else
    echo "✗ 起動に失敗しました"
    echo "ログを確認してください: docker-compose logs"
    exit 1
fi