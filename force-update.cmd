@echo off
echo ========================================
echo Force Update - Rakuten SKU Manager
echo ========================================
echo.

cd /d C:\Users\info\Desktop\sin\rakuten_sku_manager

echo [1] Stopping containers...
docker compose stop
timeout /t 2 /nobreak > nul

echo.
echo [2] Removing frontend container...
docker compose rm -f frontend
timeout /t 2 /nobreak > nul

echo.
echo [3] Removing frontend image...
docker rmi rakuten_sku_manager-frontend 2>nul
timeout /t 2 /nobreak > nul

echo.
echo [4] Rebuilding frontend only...
docker compose build frontend --no-cache
if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo [5] Starting containers...
docker compose up -d
timeout /t 5 /nobreak > nul

echo.
echo [6] Checking files in container...
docker exec rakuten-sku-frontend ls -la /app/src/components/ | findstr Device

echo.
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo IMPORTANT STEPS:
echo 1. Open Chrome/Edge
echo 2. Press F12 (Developer Tools)
echo 3. Go to Application tab
echo 4. Click "Clear site data"
echo 5. Close browser completely
echo 6. Open NEW browser window
echo 7. Go to: http://localhost:3000
echo.
echo Or use Incognito: Ctrl+Shift+N
echo ========================================
pause