$env:PYTHONPATH = "c:\Projects\unsupervised\backend"
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Starting Honey Chain Traceability AI Sequence Discovery System" -ForegroundColor Yellow
Write-Host "Smart India Hackathon 2026 - PS ID: SIH26021 (Ministry of MSME)" -ForegroundColor Green
Write-Host "Web Dashboard URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
.\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

