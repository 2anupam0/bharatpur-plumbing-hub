@echo off
title Bharatpur Plumbing Hub - Server
echo.
echo  ============================================
echo   Bharatpur Plumbing Hub - Starting Server...
echo  ============================================
echo.

cd /d "%~dp0"

echo  Opening website in your browser...
start http://127.0.0.1:8000/

echo  Starting Django server on http://127.0.0.1:8000
echo.
echo  Dashboard:  http://127.0.0.1:8000/dashboard/
echo  Login:      admin / admin123
echo.
echo  Press Ctrl+C to stop the server.
echo.

.\venv\Scripts\python.exe manage.py runserver

pause
