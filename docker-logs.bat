@echo off
chcp 65001 >nul
title 📋 Docker ログビューア

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 📋 Docker ログビューア                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo ログを表示するサービスを選択してください:
echo.
echo   1. すべてのサービス
echo   2. Backend（バックエンド）
echo   3. Frontend（フロントエンド）  
echo   4. Nginx（Webサーバー）
echo   5. 最新100行のみ表示（全サービス）
echo.

choice /C 12345 /M "選択"
set LOG_MODE=%errorlevel%

echo.
if %LOG_MODE%==1 (
    echo 📋 すべてのサービスのログを表示します...
    echo    終了: Ctrl+C
    echo.
    docker-compose logs -f
) else if %LOG_MODE%==2 (
    echo 📋 Backend のログを表示します...
    echo    終了: Ctrl+C
    echo.
    docker-compose logs -f backend
) else if %LOG_MODE%==3 (
    echo 📋 Frontend のログを表示します...
    echo    終了: Ctrl+C
    echo.
    docker-compose logs -f frontend
) else if %LOG_MODE%==4 (
    echo 📋 Nginx のログを表示します...
    echo    終了: Ctrl+C
    echo.
    docker-compose logs -f nginx
) else (
    echo 📋 最新100行のログを表示します...
    echo.
    docker-compose logs --tail=100
    echo.
    pause
)