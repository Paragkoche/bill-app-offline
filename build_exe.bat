@echo off
echo ===================================================
echo      BILL APP - PYTHON TO EXE COMPILER
echo ===================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment (.venv) not found!
    pause
    exit /b 1
)

echo Building CSS and JS assets...
call npm run build

echo Compiling Python to dist\main.exe...
call .venv\Scripts\pyinstaller.exe --noconfirm --onefile --name "main" --clean --collect-all uvicorn --collect-all fastapi --collect-all pydantic --collect-all jinja2 main.py
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller compilation failed!
    pause
    exit /b %errorlevel%
)

echo.
echo [SUCCESS] Standalone EXE created at dist\main.exe
echo.
pause
