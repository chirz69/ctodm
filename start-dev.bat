@echo off
cd /d "%~dp0\backend"
start "comment2dm-backend" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000"
cd /d "%~dp0\frontend\frontend"
start "comment2dm-frontend" cmd /k "npm start"
