@echo off
cd /d "%~dp0"
docker compose up -d --build --remove-orphans %*
if errorlevel 1 exit /b %errorlevel%
timeout /t 1 /nobreak >nul
echo.
docker compose logs ready --no-log-prefix
echo.
