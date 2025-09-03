@echo off
echo ======================================
echo 楽天SKU管理システム - 停止
echo ======================================
echo.

echo Dockerコンテナを停止しています...
docker-compose down

echo.
echo ✅ システムを停止しました。
echo.
pause