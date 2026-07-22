@echo off
echo Starting AI News Aggregator...
cd /d "%~dp0"
start "News Aggregator Server" cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3
start http://localhost:8000
