@echo off
echo Docker Hubへのプッシュスクリプト
echo ================================

set DOCKERHUB_USERNAME=your-dockerhub-username

echo.
echo Docker Hubにログイン...
docker login

echo.
echo イメージのタグ付け...
docker tag rakuten_sku_manager-backend:latest %DOCKERHUB_USERNAME%/rakuten-sku-backend:latest
docker tag rakuten_sku_manager-frontend:latest %DOCKERHUB_USERNAME%/rakuten-sku-frontend:latest

echo.
echo イメージのプッシュ...
docker push %DOCKERHUB_USERNAME%/rakuten-sku-backend:latest
docker push %DOCKERHUB_USERNAME%/rakuten-sku-frontend:latest

echo.
echo 完了！
echo Portainerで以下のイメージ名を使用してください：
echo - %DOCKERHUB_USERNAME%/rakuten-sku-backend:latest
echo - %DOCKERHUB_USERNAME%/rakuten-sku-frontend:latest
pause