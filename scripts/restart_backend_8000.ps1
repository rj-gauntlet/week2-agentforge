# Kill whatever is listening on port 8000, then start the FastAPI backend.
$port = 8000
$pids = (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Where-Object State -eq Listen).OwningProcess | Sort-Object -Unique
if ($pids) {
    foreach ($p in $pids) {
        Write-Host "Stopping process $p on port $port..."
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}
Set-Location $PSScriptRoot\..
Write-Host "Starting backend on http://127.0.0.1:$port ..."
& .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port $port
