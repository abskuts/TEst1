@echo off
:: ============================================================
:: build_windows_app.bat
:: Builds WRAFCT_v1_4.exe as a standalone Windows application.
:: Output: dist\WRAFCT_v1_4.exe
::
:: Requirements: Python 3.9+ must be on the PATH.
:: Run this script from the repository root.
:: ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo  WRAFCT Windows Application Builder
echo ============================================================
echo.

:: Verify Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python was not found on PATH.
    echo        Please install Python 3.9+ and ensure it is on PATH.
    pause
    exit /b 1
)

echo [1/5] Creating clean virtual environment in .venv ...
if exist .venv (
    rmdir /s /q .venv
)
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment ...
call .venv\Scripts\activate.bat

echo [3/5] Installing runtime dependencies ...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements.txt dependencies.
    pause
    exit /b 1
)

echo [4/5] Installing PyInstaller ...
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [5/5] Building executable with PyInstaller ...
pyinstaller WRAFCT_v1_4.spec --noconfirm
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller build failed. See output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Build complete!
echo  Executable: dist\WRAFCT_v1_4.exe
echo ============================================================
echo.

pause
