@echo off
echo ========================================
echo Docker更新スクリプト - 楽天SKU管理システム
echo ========================================
echo.

REM カレントディレクトリを確認
echo 現在のディレクトリ: %CD%
echo.

REM Dockerが起動しているか確認
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Docker Desktopが起動していません。
    echo Docker Desktopを起動してから再度実行してください。
    pause
    exit /b 1
)

echo [1/4] 既存のコンテナを停止中...
docker compose down
if %errorlevel% neq 0 (
    echo [警告] コンテナの停止でエラーが発生しましたが、続行します...
)

echo.
echo [2/4] コンテナとボリュームを削除中...
docker compose down -v
timeout /t 2 /nobreak > nul

echo.
echo [3/4] 最新のコードでイメージを再ビルド中...
echo これには数分かかる場合があります...
docker compose build --no-cache
if %errorlevel% neq 0 (
    echo [エラー] ビルドに失敗しました。
    pause
    exit /b 1
)

echo.
echo [4/4] コンテナを起動中...
docker compose up -d
if %errorlevel% neq 0 (
    echo [エラー] コンテナの起動に失敗しました。
    pause
    exit /b 1
)

echo.
echo コンテナの状態を確認中...
timeout /t 5 /nobreak > nul
docker compose ps

echo.
echo ========================================
echo ✅ Docker更新が完了しました！
echo ========================================
echo.
echo 🌐 アクセスURL:
echo    http://localhost:3000
echo.
echo 📌 新機能:
echo    - 完全カスタマイズボタン（緑色）で機種を個別配置
echo    - ドラッグ&ドロップで自由に並び替え
echo    - 新機種を任意の位置に配置可能
echo.
echo ⚠️  ブラウザのキャッシュをクリアしてください:
echo    Chrome/Edge: Ctrl+Shift+R または F12→Network→Disable cache
echo.
echo 停止する場合: docker compose down
echo ログ確認: docker compose logs -f
echo ========================================
echo.
pause