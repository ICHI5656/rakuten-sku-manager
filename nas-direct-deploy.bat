@echo off
REM NAS Direct Deployment Script

echo =====================================
echo Rakuten SKU Manager - NAS Deploy
echo =====================================

set NAS_IP=192.168.24.240
set NAS_USER=quest
set NAS_PATH=/home/quest/rakuten-sku

echo.
echo Step 1: Testing SSH connection...
ssh %NAS_USER%@%NAS_IP% "echo 'SSH connection successful'"

echo.
echo Step 2: Creating directory on NAS...
ssh %NAS_USER%@%NAS_IP% "mkdir -p %NAS_PATH%"

echo.
echo Step 3: Copying files to NAS...
scp export/backend.tar %NAS_USER%@%NAS_IP%:%NAS_PATH%/
scp export/frontend-fixed.tar %NAS_USER%@%NAS_IP%:%NAS_PATH%/frontend.tar
scp docker-compose-nas-simple.yml %NAS_USER%@%NAS_IP%:%NAS_PATH%/docker-compose.yml

echo.
echo Step 4: Loading images and starting containers on NAS...
ssh %NAS_USER%@%NAS_IP% "cd %NAS_PATH% && sudo docker load -i backend.tar && sudo docker load -i frontend.tar && sudo docker-compose down && sudo docker-compose up -d"

echo.
echo Step 5: Checking deployment status...
ssh %NAS_USER%@%NAS_IP% "sudo docker ps | grep rakuten"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo Access URLs:
echo - Application: http://%NAS_IP%:3000
echo - API Docs: http://%NAS_IP%:8000/docs
echo.
pause