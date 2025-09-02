@echo off
echo =====================================
echo Rakuten SKU Manager - Diagnostics
echo =====================================
echo.

echo [1] Container Status:
docker ps -a | findstr rakuten
echo.

echo [2] Port Bindings:
netstat -an | findstr :3000
netstat -an | findstr :8000
echo.

echo [3] Backend Health:
curl -s http://localhost:8000/health || echo Backend not responding
echo.

echo [4] Frontend Health:
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:3000
echo.

echo [5] Container Logs (Backend - last 10 lines):
docker logs --tail 10 rakuten-sku-backend
echo.

echo [6] Container Logs (Frontend - last 10 lines):
docker logs --tail 10 rakuten-sku-frontend
echo.

echo [7] Network Test:
docker exec rakuten-sku-frontend ping -c 1 backend || echo Cannot reach backend
echo.

echo [8] API Test:
curl -s http://localhost:8000/api/product-attributes/brands || echo API not responding
echo.

pause