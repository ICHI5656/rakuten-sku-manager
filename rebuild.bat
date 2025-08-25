@echo off
echo 楽天SKU管理システムを再ビルドします...
echo.

REM 既存のコンテナを停止
echo [1/3] 既存コンテナを停止中...
docker compose down

REM キャッシュを使わずに再ビルド
echo.
echo [2/3] 最新のコードでビルド中...
docker compose build --no-cache

REM コンテナを起動
echo.
echo [3/3] コンテナを起動中...
docker compose up -d

REM 状態確認
echo.
docker compose ps

echo.
echo ========================================
echo 再ビルドが完了しました！
echo.
echo アクセスURL: http://localhost:3000
echo.
echo ブラウザのキャッシュもクリアしてください：
echo   Chrome: Ctrl+Shift+R
echo   Firefox: Ctrl+Shift+R
echo ========================================
echo.
pause