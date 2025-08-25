@echo off
chcp 65001 >nul
echo ========================================
echo Complete Clean Rebuild - Rakuten SKU Manager
echo ========================================
echo.
echo This script will completely rebuild from clean state.
echo.

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/7] Stopping existing containers...
docker compose down
timeout /t 2 /nobreak > nul

echo.
echo [2/7] Removing all containers, images, volumes...
docker compose down --rmi all --volumes --remove-orphans
timeout /t 2 /nobreak > nul

echo.
echo [3/7] Clearing Docker cache...
docker system prune -f
timeout /t 2 /nobreak > nul

echo.
echo [4/7] Removing node_modules...
if exist frontend\node_modules (
    echo Removing frontend node_modules...
    rmdir /s /q frontend\node_modules 2>nul
)
if exist backend\node_modules (
    echo Removing backend node_modules...
    rmdir /s /q backend\node_modules 2>nul
)

echo.
echo [5/7] Removing dist folder...
if exist frontend\dist (
    rmdir /s /q frontend\dist 2>nul
)

echo.
echo [6/7] Building new images from scratch...
echo This may take 5-10 minutes...
docker compose build --no-cache --progress=plain
if %errorlevel% neq 0 (
    echo [ERROR] Build failed.
    echo Please check:
    echo 1. Docker Desktop is running properly
    echo 2. Internet connection is stable
    echo 3. Enough free space on C: drive
    pause
    exit /b 1
)

echo.
echo [7/7] Starting containers...
docker compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start containers.
    pause
    exit /b 1
)

echo.
echo Waiting for startup...
timeout /t 10 /nobreak > nul

echo.
echo Container status:
docker compose ps

echo.
echo ========================================
echo OK - Complete rebuild finished!
echo ========================================
echo.
echo Access URL:
echo    http://localhost:3000
echo.
echo Instructions:
echo    1. Open browser to http://localhost:3000
echo    2. Press Ctrl+F5 for hard refresh
echo    3. Upload CSV file
echo    4. Add new devices (e.g., test1, test2, test3)
echo    5. Look for green [Complete Customize] button
echo.
echo New Features:
echo    - Green [Complete Customize] button
echo    - Individual device positioning
echo    - Drag and drop reordering
echo.
echo If changes not visible:
echo    1. Clear browser cache completely
echo    2. Use private/incognito window
echo    3. Try different browser
echo.
echo Commands:
echo    View logs: docker compose logs -f frontend
echo    Restart: docker compose restart
echo    Stop: docker compose down
echo ========================================
echo.
pause