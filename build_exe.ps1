# Build script for DaVinci Discord RPC
# Usage: Open PowerShell in the repository root and run:
#   .\build_exe.ps1

$ErrorActionPreference = 'Stop'

Write-Host "Checking PyInstaller..."
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller not found. Installing..."
    python -m pip install pyinstaller
}

Write-Host "Building executable..."
Set-Location $PSScriptRoot
$specPath = Join-Path $PSScriptRoot '.github\DaVinci Discord RPC.spec'
pyinstaller --clean "$specPath"

Write-Host "Build complete."
Write-Host "Executable output: dist\DaVinci Discord RPC.exe"
