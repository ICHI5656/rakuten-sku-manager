@echo off
echo ======================================
echo 大容量CSV対応版 - システム再起動
echo （5万行以上のCSVファイル対応）
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

echo [1/5] 既存のコンテナを停止しています...
docker-compose down

echo.
echo [2/5] Dockerイメージを再ビルドしています...
docker-compose build --no-cache

echo.
echo [3/5] 最適化設定でコンテナを起動しています...
docker-compose up -d

echo.
echo [4/5] システムの起動を待っています...
timeout /t 10 /nobreak >nul

echo.
echo [5/5] ヘルスチェック中...
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
echo 🚀 大容量CSV対応設定:
echo   - 最大入力ファイルサイズ: 1GB
echo   - 最大入力行数: 200,000行対応
echo   - 出力分割: 親製品単位で60,000行ごと
echo   - メモリ割り当て: 最大6GB
echo   - 並列処理: 有効
echo.
echo アクセスURL:
echo   フロントエンド: http://localhost:3000
echo   バックエンドAPI: http://localhost:8000/docs
echo.
echo ログ確認: docker-compose logs -f
echo 停止: docker-compose down
echo.
pause