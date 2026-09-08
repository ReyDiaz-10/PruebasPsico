$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creando entorno virtual..."
    py -m venv .venv
}

$Python = ".venv\Scripts\python.exe"

Write-Host "Instalando y verificando dependencias..."
& $Python -m pip install -r requirements.txt

$env:DATABASE_URL = "sqlite:///./voting.db"

Write-Host ""
Write-Host "PruebasPsico iniciado correctamente"
Write-Host "API:     http://127.0.0.1:8000"
Write-Host "Swagger: http://127.0.0.1:8000/docs"
Write-Host ""

& $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-use-colors

