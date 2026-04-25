@echo off
title NewsDebate Fetcher - Hourly
color 0A

echo ========================================
echo    NewsDebate News Fetcher
echo    Fetches 50 articles every hour
echo    Press Ctrl+C to stop
echo ========================================
echo.

:loop
echo [%date% %time%] Fetching 50 articles...

C:\Users\User\OneDrive\Desktop\NewsDebate\venv\Scripts\python.exe C:\Users\User\OneDrive\Desktop\NewsDebate\manage.py fetch_news --count 50

echo [%date% %time%] Done. Waiting 1 hour...
echo.

timeout /t 3600 /nobreak >nul
goto loop