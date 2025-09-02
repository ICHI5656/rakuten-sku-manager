@echo off
REM Docker images export and NAS deployment script

echo =====================================
echo Rakuten SKU Manager - NAS Deployment
echo =====================================

REM Configuration
set NAS_IP=192.168.24.240
set EXPORT_DIR=export

echo.
echo Step 1: Creating export directory...
if not exist %EXPORT_DIR% mkdir %EXPORT_DIR%

echo.
echo Step 2: Exporting Docker images to tar files...
docker save -o %EXPORT_DIR%\backend.tar rakuten_sku_manager-backend:latest
docker save -o %EXPORT_DIR%\frontend.tar rakuten_sku_manager-frontend:latest

echo.
echo Step 3: Creating deployment configuration...
copy docker-compose.nas.yml %EXPORT_DIR%\docker-compose.yml

echo.
echo ========================================
echo Export Complete!
echo ========================================
echo.
echo Files created in %EXPORT_DIR% directory:
echo - backend.tar (Backend Docker image)
echo - frontend.tar (Frontend Docker image)  
echo - docker-compose.yml (Deployment configuration)
echo.
echo Next steps:
echo 1. Copy the %EXPORT_DIR% folder to your NAS
echo 2. SSH into NAS: ssh admin@%NAS_IP%
echo 3. Navigate to the copied folder
echo 4. Load images:
echo    docker load -i backend.tar
echo    docker load -i frontend.tar
echo 5. Start services:
echo    docker-compose up -d
echo.
echo Or use Portainer at http://%NAS_IP%:9000
echo.
pause