@echo off
setlocal

echo ===================================================
echo      BILL APP - COMPLETE BUILD PROCESS
echo ===================================================
echo.

:: 1. Check for Virtual Environment
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv not found!
    echo Please create it first using: uv venv --python 3.12
    pause
    exit /b 1
)

:: 2. Build CSS and JS assets
echo [1/3] Building CSS and JS assets...
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build frontend assets!
    pause
    exit /b %errorlevel%
)
echo [1/3] CSS and JS assets built successfully.
echo.

:: 3. Build Python to standalone main.exe with PyInstaller
echo [2/3] Compiling Python to EXE with PyInstaller...
call .venv\Scripts\pyinstaller.exe --noconfirm --onefile --name "main" --clean --collect-all uvicorn --collect-all fastapi --collect-all pydantic --collect-all jinja2 main.py
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller compilation failed!
    pause
    exit /b %errorlevel%
)
echo [2/3] dist\main.exe created successfully.
echo.

:: 4. Locate Inno Setup Compiler ISCC.exe
echo [3/3] Building installable setup executable with Inno Setup...
set "ISCC_PATH="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC_PATH if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC_PATH if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC_PATH for /f "delims=" %%I in ('where iscc 2^>nul') do set "ISCC_PATH=%%I"

if not defined ISCC_PATH (
    echo [ERROR] Inno Setup Compiler ISCC.exe not found!
    echo Please install Inno Setup: winget install --id JRSoftware.InnoSetup -e
    pause
    exit /b 1
)

echo Using Inno Setup compiler: "%ISCC_PATH%"
"%ISCC_PATH%" se.iss
if %errorlevel% neq 0 (
    echo [ERROR] Inno Setup compilation failed!
    pause
    exit /b %errorlevel%
)

echo.
echo ===================================================
echo [SUCCESS] Build process completed successfully!
echo.
echo   Standalone EXE : dist\main.exe
echo   Installable EXE: installer\mysetup.exe
echo ===================================================
echo.
pause
