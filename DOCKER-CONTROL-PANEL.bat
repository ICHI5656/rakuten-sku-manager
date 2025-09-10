@echo off
chcp 65001 >nul
title 🎛️ Docker コントロールパネル
setlocal enabledelayedexpansion

:MENU
cls
echo ╔══════════════════════════════════════════════════════════════╗
echo ║           🎛️  Docker コントロールパネル                      ║
echo ║                                                              ║
echo ║         楽天SKUマネージャー Docker管理ツール                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: ステータス確認
echo 📊 現在のステータス:
docker-compose ps >nul 2>&1
if errorlevel 1 (
    echo    🔴 Docker コンテナ: 停止中
) else (
    docker-compose ps | findstr "Up" >nul 2>&1
    if errorlevel 1 (
        echo    🔴 Docker コンテナ: 停止中
    ) else (
        echo    🟢 Docker コンテナ: 稼働中
    )
)

:: Docker Desktop確認
docker version >nul 2>&1
if errorlevel 1 (
    echo    🔴 Docker Desktop: 未起動
) else (
    echo    🟢 Docker Desktop: 起動中
)
echo.

echo ════════════════════════════════════════════════════════════════
echo.
echo 🚀 クイック操作:
echo.
echo   [1] ⚡ クイックスタート（最速起動）
echo   [2] 🏗️  通常ビルド＆起動
echo   [3] 🧹 クリーン再ビルド（完全リセット）
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo 📦 コンテナ管理:
echo.
echo   [4] ▶️  コンテナ起動
echo   [5] ⏸️  コンテナ停止
echo   [6] 🔄 コンテナ再起動
echo   [7] 📋 ログ表示
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo 🔧 メンテナンス:
echo.
echo   [8] 🗑️  未使用リソースの削除
echo   [9] 📊 Docker情報表示
echo   [A] 🌐 ブラウザでアプリを開く
echo   [B] 📚 APIドキュメントを開く
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo   [0] 終了
echo.

choice /C 1234567890AB /M "操作を選択してください"
set CHOICE=%errorlevel%

echo.
if %CHOICE%==1 goto QUICK_START
if %CHOICE%==2 goto NORMAL_BUILD
if %CHOICE%==3 goto CLEAN_BUILD
if %CHOICE%==4 goto START_CONTAINERS
if %CHOICE%==5 goto STOP_CONTAINERS
if %CHOICE%==6 goto RESTART_CONTAINERS
if %CHOICE%==7 goto SHOW_LOGS
if %CHOICE%==8 goto CLEANUP
if %CHOICE%==9 goto SHOW_INFO
if %CHOICE%==10 goto EXIT
if %CHOICE%==11 goto OPEN_APP
if %CHOICE%==12 goto OPEN_API

:QUICK_START
echo ⚡ クイックスタートを実行中...
docker-compose up -d --build
if errorlevel 1 (
    echo ❌ エラーが発生しました
    pause
) else (
    echo ✅ 起動完了！
    timeout /t 2 /nobreak >nul
    start http://localhost:3000
)
goto MENU

:NORMAL_BUILD
echo 🏗️  通常ビルドを実行中...
docker-compose build
if errorlevel 1 (
    echo ❌ ビルドに失敗しました
    pause
    goto MENU
)
echo ✅ ビルド完了！
choice /C YN /M "起動しますか？"
if %errorlevel%==1 (
    docker-compose up -d
    echo ✅ 起動完了！
)
pause
goto MENU

:CLEAN_BUILD
echo 🧹 クリーン再ビルドを実行します
echo ⚠️  すべてのキャッシュが削除されます
choice /C YN /M "続行しますか？"
if %errorlevel%==2 goto MENU
docker-compose down -v
docker-compose build --no-cache --pull
if errorlevel 1 (
    echo ❌ ビルドに失敗しました
    pause
    goto MENU
)
echo ✅ クリーンビルド完了！
choice /C YN /M "起動しますか？"
if %errorlevel%==1 (
    docker-compose up -d
    echo ✅ 起動完了！
)
pause
goto MENU

:START_CONTAINERS
echo ▶️  コンテナを起動中...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 起動に失敗しました
) else (
    echo ✅ 起動完了！
)
pause
goto MENU

:STOP_CONTAINERS
echo ⏸️  コンテナを停止中...
docker-compose down
echo ✅ 停止完了！
pause
goto MENU

:RESTART_CONTAINERS
echo 🔄 再起動するサービスを選択:
echo.
echo   1. すべて
echo   2. Backend
echo   3. Frontend
echo   4. Nginx
echo.
choice /C 1234 /M "選択"
if %errorlevel%==1 docker-compose restart
if %errorlevel%==2 docker-compose restart backend
if %errorlevel%==3 docker-compose restart frontend
if %errorlevel%==4 docker-compose restart nginx
echo ✅ 再起動完了！
pause
goto MENU

:SHOW_LOGS
echo 📋 ログ表示オプション:
echo.
echo   1. すべてのログ（リアルタイム）
echo   2. Backend ログ
echo   3. Frontend ログ
echo   4. 最新100行のみ
echo   5. メニューに戻る
echo.
choice /C 12345 /M "選択"
if %errorlevel%==1 docker-compose logs -f
if %errorlevel%==2 docker-compose logs -f backend
if %errorlevel%==3 docker-compose logs -f frontend
if %errorlevel%==4 (
    docker-compose logs --tail=100
    pause
)
goto MENU

:CLEANUP
echo 🗑️  クリーンアップを実行します
echo.
echo 削除対象:
echo   - 停止中のコンテナ
echo   - 未使用のイメージ
echo   - 未使用のボリューム
echo   - 未使用のネットワーク
echo.
choice /C YN /M "続行しますか？"
if %errorlevel%==2 goto MENU
docker system prune -a --volumes -f
echo ✅ クリーンアップ完了！
pause
goto MENU

:SHOW_INFO
echo 📊 Docker 情報:
echo.
echo ─── コンテナ状態 ───
docker-compose ps
echo.
echo ─── イメージ一覧 ───
docker images | findstr rakuten
echo.
echo ─── ボリューム一覧 ───
docker volume ls | findstr rakuten
echo.
echo ─── ディスク使用量 ───
docker system df
echo.
pause
goto MENU

:OPEN_APP
start http://localhost:3000
goto MENU

:OPEN_API
start http://localhost:8000/docs
goto MENU

:EXIT
echo.
echo 👋 Docker コントロールパネルを終了します
timeout /t 2 /nobreak >nul
exit /b 0