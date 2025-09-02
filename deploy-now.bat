@echo off
echo Starting NAS deployment...
echo.
echo Please enter password "Ichio_22520113" when prompted (3 times for file transfer)
echo.

echo Transferring backend.tar...
scp export\backend.tar quest@192.168.24.240:/home/quest/rakuten-sku/

echo Transferring frontend.tar...
scp export\frontend-fixed.tar quest@192.168.24.240:/home/quest/rakuten-sku/frontend.tar

echo Transferring docker-compose.yml...
scp docker-compose-nas-simple.yml quest@192.168.24.240:/home/quest/rakuten-sku/docker-compose.yml

echo.
echo Files transferred. Now connect via SSH to complete deployment:
echo.
echo ssh quest@192.168.24.240
echo Password: Ichio_22520113
echo.
echo Then run these commands:
echo   cd /home/quest/rakuten-sku
echo   sudo docker load -i backend.tar
echo   sudo docker load -i frontend.tar
echo   sudo docker-compose up -d
echo   sudo docker ps
echo.
pause