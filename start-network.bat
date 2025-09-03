@echo off
setlocal enabledelayedexpansion

echo ======================================
echo 楽天SKU管理システム - ネットワーク共有起動
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

REM ホストPCのIPアドレスを取得
echo [1/5] ネットワーク設定を確認しています...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set IP_ADDRESS=%%b
        REM ローカルホストとDockerの内部IPは除外
        if not "!IP_ADDRESS!"=="127.0.0.1" (
            if not "!IP_ADDRESS:~0,3!"=="172" (
                goto :found_ip
            )
        )
    )
)

:found_ip
if "!IP_ADDRESS!"=="" (
    echo [エラー] IPアドレスを取得できませんでした。
    echo 手動でIPアドレスを入力してください。
    set /p IP_ADDRESS="IPアドレス: "
)

echo.
echo ========================================
echo ホストPCのIPアドレス: %IP_ADDRESS%
echo ========================================
echo.
echo 他のPCからは以下のURLでアクセスできます:
echo   フロントエンド: http://%IP_ADDRESS%:3000
echo   バックエンドAPI: http://%IP_ADDRESS%:8000/docs
echo.

REM 既存のコンテナを停止
echo [2/5] 既存のコンテナを停止しています...
docker-compose down

REM docker-compose.network.ymlをコピーしてIPアドレスを置換
echo [3/5] ネットワーク設定を適用しています...
powershell -Command "(Get-Content docker-compose.network.yml) -replace 'HOST_IP', '%IP_ADDRESS%' | Set-Content docker-compose.temp.yml"

echo.
echo [4/5] Dockerイメージをビルドしています...
docker-compose -f docker-compose.temp.yml build

echo.
echo [5/5] Dockerコンテナを起動しています...
docker-compose -f docker-compose.temp.yml up -d

REM 一時ファイルを削除
del docker-compose.temp.yml

echo.
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
echo ✅ ネットワーク共有モードで起動完了！
echo ======================================
echo.
echo 【このPC】
echo   フロントエンド: http://localhost:3000
echo   バックエンドAPI: http://localhost:8000/docs
echo.
echo 【同じネットワーク内の他のPC】
echo   フロントエンド: http://%IP_ADDRESS%:3000
echo   バックエンドAPI: http://%IP_ADDRESS%:8000/docs
echo.
echo ※ Windowsファイアウォールの設定が必要な場合があります
echo ※ 停止するには: docker-compose down
echo.
pause