@echo off
echo ======================================================================
echo Starting Honey Chain Traceability AI Sequence Discovery System
echo Smart India Hackathon 2026 - PS ID: SIH26021 (Ministry of MSME)
echo Web Dashboard URL: http://localhost:8000
echo ======================================================================
set PYTHONPATH=c:\Projects\unsupervised\backend
.\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause

