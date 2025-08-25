@echo off
echo ========================================
echo 完全クリーン再ビルド - 楽天SKU管理システム
echo ========================================
echo.
echo このスクリプトは完全にクリーンな状態から再ビルドします。
echo.

REM Dockerが起動しているか確認
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Docker Desktopが起動していません。
    echo Docker Desktopを起動してから再度実行してください。
    pause
    exit /b 1
)

echo [1/7] 既存のコンテナを停止中...
docker compose down
timeout /t 2 /nobreak > nul

echo.
echo [2/7] コンテナ、イメージ、ボリュームを完全削除中...
docker compose down --rmi all --volumes --remove-orphans
timeout /t 2 /nobreak > nul

echo.
echo [3/7] Dockerのキャッシュをクリア中...
docker system prune -f
timeout /t 2 /nobreak > nul

echo.
echo [4/7] node_modulesを削除中（クリーンビルドのため）...
if exist frontend\node_modules (
    echo フロントエンドのnode_modulesを削除中...
    rmdir /s /q frontend\node_modules 2>nul
)
if exist backend\node_modules (
    echo バックエンドのnode_modulesを削除中...
    rmdir /s /q backend\node_modules 2>nul
)

echo.
echo [5/7] distフォルダを削除中...
if exist frontend\dist (
    rmdir /s /q frontend\dist 2>nul
)

echo.
echo [6/7] 完全に新しくイメージをビルド中...
echo これには5-10分かかる場合があります...
docker compose build --no-cache --progress=plain
if %errorlevel% neq 0 (
    echo [エラー] ビルドに失敗しました。
    echo 以下を確認してください：
    echo 1. Docker Desktopが正常に動作しているか
    echo 2. インターネット接続が安定しているか
    echo 3. C:ドライブに十分な空き容量があるか
    pause
    exit /b 1
)

echo.
echo [7/7] コンテナを起動中...
docker compose up -d
if %errorlevel% neq 0 (
    echo [エラー] コンテナの起動に失敗しました。
    pause
    exit /b 1
)

echo.
echo 起動を待機中...
timeout /t 10 /nobreak > nul

echo.
echo コンテナの状態:
docker compose ps

echo.
echo ログを確認中（最後の20行）:
docker compose logs --tail=20

echo.
echo ========================================
echo ✅ 完全クリーン再ビルドが完了しました！
echo ========================================
echo.
echo 🌐 アクセス方法:
echo    1. ブラウザで http://localhost:3000 を開く
echo    2. Ctrl+F5 でハード更新（重要！）
echo    3. CSVファイルをアップロード
echo    4. 新機種を入力（例: test1, test2, test3）
echo    5. 緑色の「完全カスタマイズ」ボタンが表示されます
echo.
echo 📌 新機能の確認:
echo    - 緑色の「完全カスタマイズ」ボタン
echo    - 各新機種を個別に配置可能
echo    - ドラッグ&ドロップで自由な並び替え
echo.
echo ⚠️  もし変更が反映されない場合:
echo    1. ブラウザのキャッシュを完全にクリア
echo    2. プライベートウィンドウで開く
echo    3. 別のブラウザで試す
echo.
echo 🔧 トラブルシューティング:
echo    ログ確認: docker compose logs -f frontend
echo    再起動: docker compose restart
echo    停止: docker compose down
echo ========================================
echo.
pause