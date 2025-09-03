@echo off
echo ======================================
echo Windowsファイアウォール設定削除
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

echo ファイアウォールルールを削除しています...

REM フロントエンド用のルールを削除
netsh advfirewall firewall delete rule name="Rakuten SKU Manager Frontend"
if %errorlevel% equ 0 (
    echo ✅ フロントエンド(3000)のルールを削除しました
) else (
    echo ⚠️ フロントエンド(3000)のルールが見つかりません
)

REM バックエンドAPI用のルールを削除
netsh advfirewall firewall delete rule name="Rakuten SKU Manager Backend"
if %errorlevel% equ 0 (
    echo ✅ バックエンドAPI(8000)のルールを削除しました
) else (
    echo ⚠️ バックエンドAPI(8000)のルールが見つかりません
)

echo.
echo ======================================
echo ファイアウォールルールの削除完了
echo ======================================
echo.
pause