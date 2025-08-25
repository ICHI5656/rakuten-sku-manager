@echo off
echo Checking frontend files...
echo.

cd /d C:\Users\info\Desktop\sin\rakuten_sku_manager

echo [Local files]:
dir frontend\src\components\Device*.tsx /b
echo.

echo [Container files]:
docker exec rakuten-sku-frontend ls /app/src/components/ | findstr Device
echo.

echo [Container build status]:
docker exec rakuten-sku-frontend ls -la /app/dist/assets/*.js
echo.

echo [Frontend logs]:
docker compose logs --tail=10 frontend
echo.

pause