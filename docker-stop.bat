@echo off
chcp 65001 >nul
title 🛑 Docker 停止

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 🛑 Docker コンテナ停止                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📋 現在実行中のコンテナ:
docker-compose ps
echo.

choice /C YN /M "コンテナを停止しますか？"
if errorlevel 2 (
    echo.
    echo 🚫 キャンセルしました
    pause
    exit /b 0
)

echo.
echo 🛑 コンテナを停止中...
docker-compose down

echo.
echo ✅ 停止完了！
echo.

choice /C YN /M "ボリューム（データ）も削除しますか？"
if errorlevel 2 (
    echo.
    echo 📝 データは保持されます
) else (
    echo.
    echo 🗑️  ボリュームを削除中...
    docker-compose down -v
    echo ✅ ボリューム削除完了
)

echo.
pause