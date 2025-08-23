@echo off
echo 楽天SKU管理システムを起動しています...

REM Build and start containers
docker-compose up --build -d

REM Wait for services
timeout /t 5 /nobreak > nul

REM Check status
docker-compose ps

echo.
echo システムが起動しました
echo.
echo アクセスURL:
echo   http://localhost:3000
echo.
echo 停止するには: docker-compose down
echo.
pause