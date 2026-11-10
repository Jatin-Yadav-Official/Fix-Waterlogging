@echo off
title Fix Waterlogging
cd /d "%~dp0"
echo ===============================================================
echo Starting Fix Waterlogging Server...
echo Open your browser at: http://127.0.0.1:8000
echo ===============================================================
python server.py
pause
