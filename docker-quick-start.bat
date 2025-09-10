@echo off
chcp 65001 >nul
title 🚀 Docker クイックスタート

echo ╔══════════════════════════════════════════════════════════════╗
echo ║            🚀 Docker クイックスタート (最速起動)             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ⚡ 最速でアプリケーションを起動します...
echo.

:: Docker確認（サイレント）
docker version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker Desktop を起動中...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 10 /nobreak >nul
)

:: ビルド＆起動（バックグラウンド）
echo 📦 ビルド＆起動中...
docker-compose up -d --build

if errorlevel 1 (
    echo.
    echo ❌ エラーが発生しました
    echo 💡 docker-build.bat を使用して詳細な設定を行ってください
    pause
    exit /b 1
)

echo.
echo ✅ 起動完了！
echo.
echo 🌐 アプリケーション: http://localhost:3000
echo 📚 API ドキュメント: http://localhost:8000/docs
echo.

:: 自動でブラウザを開く
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo 終了するには任意のキーを押してください...
pause >nul