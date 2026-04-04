@echo off
REM Build script for DaVinci Discord RPC using PyInstaller.
REM Run this from the repository root.
cd /d %~dp0

python -m pip install pyinstaller
pyinstaller --clean ".github\DaVinci Discord RPC.spec"
if %ERRORLEVEL% neq 0 (
    echo PyInstaller failed. Check the error messages above.
    pause
    exit /b %ERRORLEVEL%
)
echo.
echo Build complete.
echo Executable output: dist\DaVinci Discord RPC.exe
pause
