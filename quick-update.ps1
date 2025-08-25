# PowerShell版の更新スクリプト（管理者権限不要）
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker更新 - 楽天SKU管理システム" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Dockerの確認
try {
    docker --version | Out-Null
} catch {
    Write-Host "[エラー] Docker Desktopが起動していません。" -ForegroundColor Red
    Write-Host "Docker Desktopを起動してから再度実行してください。" -ForegroundColor Red
    Read-Host "Enterキーを押して終了"
    exit 1
}

# 現在のディレクトリを表示
Write-Host "現在のディレクトリ: $PWD" -ForegroundColor Gray
Write-Host ""

# 1. コンテナ停止
Write-Host "[1/4] 既存のコンテナを停止中..." -ForegroundColor Green
docker compose down 2>$null

# 2. ボリューム削除
Write-Host ""
Write-Host "[2/4] コンテナとボリュームを削除中..." -ForegroundColor Green
docker compose down -v 2>$null
Start-Sleep -Seconds 2

# 3. 再ビルド
Write-Host ""
Write-Host "[3/4] 最新のコードでイメージを再ビルド中..." -ForegroundColor Green
Write-Host "      これには数分かかる場合があります..." -ForegroundColor Gray
docker compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "[エラー] ビルドに失敗しました。" -ForegroundColor Red
    Read-Host "Enterキーを押して終了"
    exit 1
}

# 4. コンテナ起動
Write-Host ""
Write-Host "[4/4] コンテナを起動中..." -ForegroundColor Green
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "[エラー] コンテナの起動に失敗しました。" -ForegroundColor Red
    Read-Host "Enterキーを押して終了"
    exit 1
}

# 状態確認
Write-Host ""
Write-Host "コンテナの状態を確認中..." -ForegroundColor Gray
Start-Sleep -Seconds 5
docker compose ps

# 完了メッセージ
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Docker更新が完了しました！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 アクセスURL:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "📌 新機能:" -ForegroundColor Yellow
Write-Host "   - 完全カスタマイズボタン（緑色）で機種を個別配置" -ForegroundColor White
Write-Host "   - ドラッグ&ドロップで自由に並び替え" -ForegroundColor White
Write-Host "   - 新機種を任意の位置に配置可能" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  ブラウザのキャッシュをクリアしてください:" -ForegroundColor Yellow
Write-Host "   Chrome/Edge: Ctrl+Shift+R" -ForegroundColor White
Write-Host ""
Write-Host "停止: docker compose down" -ForegroundColor Gray
Write-Host "ログ: docker compose logs -f" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Enterキーを押して終了"