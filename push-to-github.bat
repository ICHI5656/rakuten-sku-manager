@echo off
REM GitHub Container Registryへのプッシュスクリプト

REM ===== 設定 =====
set GITHUB_USERNAME=info
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
REM GitHubトークンは https://github.com/settings/tokens/new で作成
REM 必要な権限: write:packages, read:packages, delete:packages

echo GitHub Container Registryへのプッシュ
echo =====================================

REM GitHub Container Registryにログイン
echo.
echo GitHub Container Registryにログイン中...
echo %GITHUB_TOKEN% | docker login ghcr.io -u %GITHUB_USERNAME% --password-stdin

REM イメージのタグ付け
echo.
echo イメージをタグ付け中...
docker tag rakuten_sku_manager-backend:latest ghcr.io/%GITHUB_USERNAME%/rakuten-sku-backend:latest
docker tag rakuten_sku_manager-frontend:latest ghcr.io/%GITHUB_USERNAME%/rakuten-sku-frontend:latest

REM イメージのプッシュ
echo.
echo バックエンドイメージをプッシュ中...
docker push ghcr.io/%GITHUB_USERNAME%/rakuten-sku-backend:latest

echo.
echo フロントエンドイメージをプッシュ中...
docker push ghcr.io/%GITHUB_USERNAME%/rakuten-sku-frontend:latest

echo.
echo 完了！
echo.
echo Portainerで使用するイメージ名：
echo - ghcr.io/%GITHUB_USERNAME%/rakuten-sku-backend:latest
echo - ghcr.io/%GITHUB_USERNAME%/rakuten-sku-frontend:latest
echo.
pause