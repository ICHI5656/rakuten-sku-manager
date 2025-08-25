@echo off
echo ========================================
echo 更新確認スクリプト
echo ========================================
echo.

echo [1] コンテナの状態を確認:
docker compose ps
echo.

echo [2] フロントエンドのログ（最新10行）:
docker compose logs --tail=10 frontend
echo.

echo [3] バックエンドのログ（最新10行）:
docker compose logs --tail=10 backend
echo.

echo [4] コンテナ内のファイル確認:
echo DeviceListOrganizer.tsxが存在するか確認中...
docker compose exec frontend ls -la /app/src/components/DeviceListOrganizer.tsx 2>nul
if %errorlevel% eq 0 (
    echo ✅ DeviceListOrganizer.tsxが存在します
) else (
    echo ❌ DeviceListOrganizer.tsxが見つかりません
)

echo.
echo DeviceOrderEditor.tsxが存在するか確認中...
docker compose exec frontend ls -la /app/src/components/DeviceOrderEditor.tsx 2>nul
if %errorlevel% eq 0 (
    echo ✅ DeviceOrderEditor.tsxが存在します
) else (
    echo ❌ DeviceOrderEditor.tsxが見つかりません
)

echo.
echo [5] ビルド済みファイルの確認:
docker compose exec frontend ls -la /app/dist/ 2>nul

echo.
echo ========================================
echo 確認が完了しました。
echo.
echo 次のステップ:
echo 1. http://localhost:3000 にアクセス
echo 2. Ctrl+Shift+Delete でブラウザキャッシュをクリア
echo 3. ページを再読み込み（Ctrl+F5）
echo ========================================
echo.
pause