@echo off
chcp 65001 >nul
title 🔄 Docker 再起動

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 🔄 Docker コンテナ再起動                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 再起動方法を選択してください:
echo.
echo   1. すべてのサービスを再起動
echo   2. Backend のみ再起動
echo   3. Frontend のみ再起動
echo   4. Nginx のみ再起動
echo.

choice /C 1234 /M "選択"
set RESTART_MODE=%errorlevel%

echo.
if %RESTART_MODE%==1 (
    echo 🔄 すべてのサービスを再起動中...
    docker-compose restart
) else if %RESTART_MODE%==2 (
    echo 🔄 Backend を再起動中...
    docker-compose restart backend
) else if %RESTART_MODE%==3 (
    echo 🔄 Frontend を再起動中...
    docker-compose restart frontend
) else (
    echo 🔄 Nginx を再起動中...
    docker-compose restart nginx
)

if errorlevel 1 (
    echo.
    echo ❌ 再起動に失敗しました
    pause
    exit /b 1
)

echo.
echo ✅ 再起動完了！
echo.

:: ヘルスチェック
echo 📋 サービス状態を確認中...
timeout /t 3 /nobreak >nul
docker-compose ps

echo.
echo 🌐 アプリケーション: http://localhost:3000
echo 📚 API ドキュメント: http://localhost:8000/docs
echo.

pause