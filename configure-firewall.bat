@echo off
echo ======================================
echo Windowsファイアウォール設定
echo ======================================
echo.
echo 管理者権限が必要です。
echo.

REM 管理者権限の確認
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] このスクリプトは管理者権限で実行してください。
    echo 右クリック → 「管理者として実行」を選択してください。
    pause
    exit /b 1
)

echo Dockerポートのファイアウォールルールを追加しています...

REM フロントエンド用のルール（ポート3000）
netsh advfirewall firewall add rule name="Rakuten SKU Manager Frontend" dir=in action=allow protocol=TCP localport=3000
if %errorlevel% equ 0 (
    echo ✅ フロントエンド(3000)のルールを追加しました
) else (
    echo ⚠️ フロントエンド(3000)のルールは既に存在します
)

REM バックエンドAPI用のルール（ポート8000）
netsh advfirewall firewall add rule name="Rakuten SKU Manager Backend" dir=in action=allow protocol=TCP localport=8000
if %errorlevel% equ 0 (
    echo ✅ バックエンドAPI(8000)のルールを追加しました
) else (
    echo ⚠️ バックエンドAPI(8000)のルールは既に存在します
)

echo.
echo ======================================
echo ファイアウォール設定完了
echo ======================================
echo.
echo 追加されたルール:
netsh advfirewall firewall show rule name="Rakuten SKU Manager Frontend"
netsh advfirewall firewall show rule name="Rakuten SKU Manager Backend"
echo.
echo ルールを削除する場合は remove-firewall.bat を実行してください。
echo.
pause