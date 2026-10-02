@echo off
setlocal

echo ===================================================
echo      BILL APP - INSTALLABLE SETUP COMPILER
echo ===================================================
echo.

if not exist "dist\main.exe" (
    echo [ERROR] dist\main.exe not found!
    echo Please run build_exe.bat first.
    pause
    exit /b 1
)

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

echo Compiling installer with Inno Setup...
echo Using: "%ISCC_PATH%"
"%ISCC_PATH%" se.iss
if %errorlevel% neq 0 (
    echo [ERROR] Installer build failed!
    pause
    exit /b %errorlevel%
)

echo.
echo ===================================================
echo [SUCCESS] Installable setup created at installer\mysetup.exe
echo ===================================================
echo.
pause
