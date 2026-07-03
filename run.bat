@echo off
title Smart Video Downloader
echo Starting Smart Video Downloader...
echo.

:: Open default browser to the app URL after a small delay
start "" http://localhost:5050

:: Start the Python backend using the virtual environment
venv\Scripts\python.exe -m app.app

if %ERRORLEVEL% neq 0 (
    echo.
    echo Server stopped with error or virtual environment is missing.
    echo Please make sure you have python installed and 'venv' folder present.
    pause
)
