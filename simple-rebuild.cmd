@echo off
echo Rebuilding Docker containers...
echo.

docker compose down
docker compose build --no-cache
docker compose up -d

echo.
echo Done! Access: http://localhost:3000
echo Clear browser cache: Ctrl+F5
pause