@echo off
chcp 65001 >nul
title 🧹 Docker クリーン再ビルド

echo ╔══════════════════════════════════════════════════════════════╗
echo ║          🧹 Docker 完全クリーン再ビルド                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ⚠️  警告: すべてのDockerキャッシュとイメージを削除して再構築します
echo.

choice /C YN /M "続行しますか？"
if errorlevel 2 (
    echo.
    echo 🚫 キャンセルしました
    pause
    exit /b 0
)

echo.
echo [1/6] 🛑 既存のコンテナを停止中...
docker-compose down -v

echo.
echo [2/6] 🗑️  未使用のコンテナを削除中...
docker container prune -f

echo.
echo [3/6] 🗑️  未使用のイメージを削除中...
docker image prune -a -f

echo.
echo [4/6] 🗑️  未使用のボリュームを削除中...
docker volume prune -f

echo.
echo [5/6] 🗑️  未使用のネットワークを削除中...
docker network prune -f

echo.
echo [6/6] 🏗️  クリーンビルドを開始...
docker-compose build --no-cache --pull

if errorlevel 1 (
    echo.
    echo ❌ ビルドに失敗しました
    pause
    exit /b 1
)

echo.
echo ✅ クリーンビルド完了！
echo.

choice /C YN /M "コンテナを起動しますか？"
if errorlevel 2 (
    echo.
    echo 📝 起動コマンド: docker-compose up -d
    pause
    exit /b 0
)

echo.
echo 🚀 コンテナを起動中...
docker-compose up -d

echo.
echo ✅ すべて完了！
echo.
echo 🌐 アプリケーション: http://localhost:3000
echo 📚 API ドキュメント: http://localhost:8000/docs
echo.

timeout /t 3 /nobreak >nul
start http://localhost:3000

pause