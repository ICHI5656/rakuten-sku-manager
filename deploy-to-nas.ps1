# PowerShell NAS Deployment Script

$NAS_IP = "192.168.24.240"
$NAS_USER = "quest"
$NAS_PASS = "Ichio_22520113"
$NAS_PATH = "/home/quest/rakuten-sku"
$EXPORT_DIR = "export"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Rakuten SKU Manager - NAS Deployment" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if files exist
Write-Host "Checking files..." -ForegroundColor Yellow
if (-not (Test-Path "$EXPORT_DIR\backend.tar")) {
    Write-Host "Error: backend.tar not found in export directory" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "$EXPORT_DIR\frontend-fixed.tar")) {
    Write-Host "Error: frontend-fixed.tar not found in export directory" -ForegroundColor Red
    exit 1
}

Write-Host "Files found. Starting deployment..." -ForegroundColor Green
Write-Host ""

# Use plink for SSH commands (PuTTY suite)
Write-Host "Step 1: Creating directory on NAS..." -ForegroundColor Yellow
echo y | plink -pw $NAS_PASS $NAS_USER@$NAS_IP "mkdir -p $NAS_PATH"

Write-Host "Step 2: Copying files to NAS..." -ForegroundColor Yellow
pscp -pw $NAS_PASS $EXPORT_DIR\backend.tar ${NAS_USER}@${NAS_IP}:${NAS_PATH}/
pscp -pw $NAS_PASS $EXPORT_DIR\frontend-fixed.tar ${NAS_USER}@${NAS_IP}:${NAS_PATH}/frontend.tar
pscp -pw $NAS_PASS docker-compose-nas-simple.yml ${NAS_USER}@${NAS_IP}:${NAS_PATH}/docker-compose.yml

Write-Host "Step 3: Loading Docker images..." -ForegroundColor Yellow
plink -pw $NAS_PASS $NAS_USER@$NAS_IP "cd $NAS_PATH && sudo docker load -i backend.tar"
plink -pw $NAS_PASS $NAS_USER@$NAS_IP "cd $NAS_PATH && sudo docker load -i frontend.tar"

Write-Host "Step 4: Starting containers..." -ForegroundColor Yellow
plink -pw $NAS_PASS $NAS_USER@$NAS_IP "cd $NAS_PATH && sudo docker-compose down"
plink -pw $NAS_PASS $NAS_USER@$NAS_IP "cd $NAS_PATH && sudo docker-compose up -d"

Write-Host "Step 5: Checking status..." -ForegroundColor Yellow
plink -pw $NAS_PASS $NAS_USER@$NAS_IP "sudo docker ps | grep rakuten"

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "- Application: http://$NAS_IP`:3000" -ForegroundColor White
Write-Host "- API Docs: http://$NAS_IP`:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")