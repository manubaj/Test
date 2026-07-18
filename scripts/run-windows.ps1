# SignalForge — Windows one-shot launcher (Docker Desktop required)
# Usage (PowerShell):
#   .\scripts\run-windows.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Error "Docker is not installed or not on PATH. Install Docker Desktop first."
}

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example"
}

Write-Host "Starting SignalForge stack..."
docker compose up --build -d

Write-Host ""
Write-Host "Frontend:  http://localhost:3000"
Write-Host "API docs:  http://localhost:8000/docs"
Write-Host "Login:     admin@example.com / Admin123!"
Write-Host ""
Write-Host "Logs: docker compose logs -f"
