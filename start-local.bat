@echo off
echo ======================================
echo 楽天SKU管理システム - ローカル起動
echo ======================================
echo.

REM Docker Desktopが起動しているか確認
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Docker Desktopが起動していません。
    echo Docker Desktopを起動してから再実行してください。
    pause
    exit /b 1
)

echo [1/4] Dockerコンテナを停止しています...
docker-compose down

echo.
echo [2/4] Dockerイメージをビルドしています...
docker-compose build

echo.
echo [3/4] Dockerコンテナを起動しています...
docker-compose up -d

echo.
echo [4/4] 起動を確認しています...
timeout /t 5 /nobreak >nul

REM ヘルスチェック
docker-compose ps | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo [エラー] コンテナの起動に失敗しました。
    echo ログを確認してください:
    docker-compose logs --tail 50
    pause
    exit /b 1
)

echo.
echo ======================================
echo ✅ システムが正常に起動しました！
echo ======================================
echo.
echo アクセスURL:
echo   フロントエンド: http://localhost:3000
echo   バックエンドAPI: http://localhost:8000/docs
echo.
echo 停止するには: docker-compose down
echo ログを見るには: docker-compose logs -f
echo.
pause