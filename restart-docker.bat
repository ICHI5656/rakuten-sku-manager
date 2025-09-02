@echo off
echo ========================================
echo Docker再起動スクリプト
echo ========================================

echo Docker Desktopを起動してください...
echo.
echo Docker Desktopが起動したら、Enterキーを押してください。
pause

echo.
echo Dockerが起動しているか確認中...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Docker Desktopが起動していません。
    echo Docker Desktopを起動してから再度実行してください。
    pause
    exit /b 1
)

echo.
echo [1/3] 既存のコンテナを停止中...
docker-compose down

echo.
echo [2/3] コンテナを再ビルド中...
docker-compose build --no-cache

echo.
echo [3/3] コンテナを起動中...
docker-compose up -d

echo.
echo 起動を待機中（10秒）...
timeout /t 10 /nobreak > nul

echo.
echo ========================================
echo ✅ 再起動完了！
echo ========================================
echo.
echo アクセス: http://localhost:3000
echo.
echo 修正内容:
echo - 既存デバイスの重複エラーを解決
echo - デバイスが既に存在する場合は更新処理
echo - usage_countを自動的にインクリメント
echo.
pause