@echo off
REM NASへの直接デプロイスクリプト（Windows版）

echo =====================================
echo 楽天SKU管理システム NAS直接デプロイ
echo =====================================

REM 設定
set NAS_IP=192.168.24.240
set NAS_USER=admin

echo.
echo ステップ1: Dockerイメージをtar形式で保存中...
docker save -o rakuten-backend.tar rakuten_sku_manager-backend:latest
docker save -o rakuten-frontend.tar rakuten_sku_manager-frontend:latest

echo.
echo ステップ2: ファイルをNASに転送中...
echo パスワードを入力してください（複数回求められます）

REM SCPでファイルを転送
scp rakuten-backend.tar %NAS_USER%@%NAS_IP%:/volume1/docker/
scp rakuten-frontend.tar %NAS_USER%@%NAS_IP%:/volume1/docker/
scp docker-compose.nas.yml %NAS_USER%@%NAS_IP%:/volume1/docker/docker-compose.yml

echo.
echo ステップ3: NASでイメージをロードしてコンテナを起動中...
ssh %NAS_USER%@%NAS_IP% "cd /volume1/docker && docker load -i rakuten-backend.tar && docker load -i rakuten-frontend.tar && docker-compose up -d"

echo.
echo ========================================
echo デプロイ完了！
echo ========================================
echo.
echo アクセスURL:
echo - アプリケーション: http://%NAS_IP%:3000
echo - API ドキュメント: http://%NAS_IP%:8000/docs
echo - Portainer: http://%NAS_IP%:9000
echo.
echo ローカルのtarファイルを削除しますか？ (Y/N)
set /p DELETE_TAR=
if /i "%DELETE_TAR%"=="Y" (
    del rakuten-backend.tar
    del rakuten-frontend.tar
    echo tarファイルを削除しました
)

pause