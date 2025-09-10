@echo off
chcp 65001 >nul
title 📊 Docker ステータス

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 📊 Docker ステータス確認                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Docker Desktop確認
echo 🐳 Docker Desktop:
docker version >nul 2>&1
if errorlevel 1 (
    echo    ❌ 未起動
    echo.
    choice /C YN /M "Docker Desktop を起動しますか？"
    if %errorlevel%==1 (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        echo    起動中... 10秒後に再確認します
        timeout /t 10 /nobreak >nul
        docker version >nul 2>&1
        if errorlevel 1 (
            echo    ❌ まだ起動していません
        ) else (
            echo    ✅ 起動完了
        )
    )
) else (
    echo    ✅ 起動中
    docker version | findstr Version | head -1
)
echo.

:: コンテナ状態
echo 📦 コンテナ状態:
docker-compose ps 2>nul
if errorlevel 1 (
    echo    コンテナが定義されていません
) 
echo.

:: リソース使用状況
echo 💾 リソース使用状況:
docker system df 2>nul
echo.

:: ポート使用状況
echo 🔌 ポート使用状況:
netstat -an | findstr ":3000" >nul 2>&1
if errorlevel 1 (
    echo    ポート 3000: 🟢 利用可能
) else (
    echo    ポート 3000: 🔴 使用中
)

netstat -an | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo    ポート 8000: 🟢 利用可能
) else (
    echo    ポート 8000: 🔴 使用中
)
echo.

:: サービス確認
echo 🌐 サービス確認:
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo    Frontend: ⭕ 未起動
) else (
    echo    Frontend: ✅ http://localhost:3000
)

curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo    Backend:  ⭕ 未起動
) else (
    echo    Backend:  ✅ http://localhost:8000
)
echo.

pause