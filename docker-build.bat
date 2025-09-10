@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔══════════════════════════════════════════════════════════════╗
echo ║          🐳 Docker ビルド＆起動 (ワンクリック)              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Docker Desktop起動確認
echo [1/5] Docker Desktop の確認中...
docker version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  Docker Desktop が起動していません
    echo 💡 Docker Desktop を起動しています...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo.
    echo ⏳ Docker Desktop の起動を待っています（最大60秒）...
    
    set /a count=0
    :wait_docker
    timeout /t 2 /nobreak >nul
    set /a count+=2
    docker version >nul 2>&1
    if errorlevel 1 (
        if !count! lss 60 (
            echo    待機中... !count!秒
            goto wait_docker
        ) else (
            echo.
            echo ❌ Docker Desktop の起動に失敗しました
            echo 💡 手動で Docker Desktop を起動してから再実行してください
            pause
            exit /b 1
        )
    )
)
echo ✅ Docker Desktop が起動しています
echo.

:: 既存コンテナの確認
echo [2/5] 既存のコンテナを確認中...
docker-compose ps >nul 2>&1
if not errorlevel 1 (
    echo 📦 既存のコンテナが見つかりました
    echo.
    choice /C YN /M "既存のコンテナを停止してから再ビルドしますか？"
    if !errorlevel!==1 (
        echo.
        echo 🛑 既存のコンテナを停止中...
        docker-compose down
        echo ✅ 停止完了
    )
)
echo.

:: ビルドモードの選択
echo [3/5] ビルドモードを選択してください:
echo.
echo   1. 通常ビルド（キャッシュ使用・高速）
echo   2. クリーンビルド（キャッシュ削除・完全再構築）
echo   3. 特定サービスのみビルド
echo.
choice /C 123 /M "選択"
set BUILD_MODE=!errorlevel!

echo.
if !BUILD_MODE!==1 (
    echo 📦 通常ビルドを開始します...
    echo.
    docker-compose build
) else if !BUILD_MODE!==2 (
    echo 🧹 クリーンビルドを開始します...
    echo.
    docker-compose build --no-cache
) else (
    echo 利用可能なサービス:
    echo   1. backend（バックエンド）
    echo   2. frontend（フロントエンド）
    echo   3. nginx（Webサーバー）
    echo.
    choice /C 123 /M "ビルドするサービスを選択"
    
    if !errorlevel!==1 set SERVICE=backend
    if !errorlevel!==2 set SERVICE=frontend
    if !errorlevel!==3 set SERVICE=nginx
    
    echo.
    echo 📦 !SERVICE! のビルドを開始します...
    docker-compose build !SERVICE!
)

if errorlevel 1 (
    echo.
    echo ❌ ビルドに失敗しました
    echo 💡 エラーメッセージを確認してください
    pause
    exit /b 1
)

echo.
echo ✅ ビルド完了！
echo.

:: コンテナ起動
echo [4/5] コンテナを起動しますか？
choice /C YN /M "起動する？"
if !errorlevel!==1 (
    echo.
    echo 🚀 コンテナを起動中...
    docker-compose up -d
    
    if errorlevel 1 (
        echo.
        echo ❌ 起動に失敗しました
        pause
        exit /b 1
    )
    
    echo.
    echo ✅ 起動完了！
    echo.
    
    :: ヘルスチェック
    echo [5/5] サービスの起動を確認中...
    timeout /t 5 /nobreak >nul
    
    :: Backend確認
    curl -s http://localhost:8000/health >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Backend: 起動中... (http://localhost:8000)
    ) else (
        echo ✅ Backend: 正常稼働中 (http://localhost:8000)
    )
    
    :: Frontend確認
    curl -s http://localhost:3000 >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Frontend: 起動中... (http://localhost:3000)
    ) else (
        echo ✅ Frontend: 正常稼働中 (http://localhost:3000)
    )
    
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                    🎉 セットアップ完了！                     ║
    echo ╠══════════════════════════════════════════════════════════════╣
    echo ║  アプリケーション: http://localhost:3000                     ║
    echo ║  API ドキュメント: http://localhost:8000/docs               ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    
    :: ブラウザで開く
    choice /C YN /T 5 /D N /M "ブラウザで開きますか？"
    if !errorlevel!==1 (
        start http://localhost:3000
    )
)

echo.
echo 🔧 その他の操作:
echo   - ログ確認: docker-compose logs -f
echo   - 停止: docker-compose down
echo   - 再起動: docker-compose restart
echo.
pause