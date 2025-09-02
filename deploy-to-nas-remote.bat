@echo off
REM Remote NAS deployment script

echo =====================================
echo Rakuten SKU Manager - Remote NAS Deploy
echo =====================================

set NAS_IP=192.168.24.240
set NAS_USER=admin
set CONTAINER_PATH=/volume1/docker/rakuten-sku

echo.
echo Creating remote directory on NAS...
ssh %NAS_USER%@%NAS_IP% "mkdir -p %CONTAINER_PATH%"

echo.
echo Copying files to NAS...
scp export/backend.tar %NAS_USER%@%NAS_IP%:%CONTAINER_PATH%/
scp export/frontend-fixed.tar %NAS_USER%@%NAS_IP%:%CONTAINER_PATH%/frontend.tar
scp docker-compose.nas.yml %NAS_USER%@%NAS_IP%:%CONTAINER_PATH%/docker-compose.yml

echo.
echo Loading and starting containers on NAS...
ssh %NAS_USER%@%NAS_IP% "cd %CONTAINER_PATH% && docker load -i backend.tar && docker load -i frontend.tar && docker-compose down && docker-compose up -d"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo Access URLs:
echo - Application: http://%NAS_IP%:3000
echo - API Docs: http://%NAS_IP%:8000/docs
echo.
pause