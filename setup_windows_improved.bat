@echo off
title EasyJet Deal Scraper - Windows Setup
color 0A

echo.
echo ========================================
echo  EasyJet Deal Scraper - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo + Python found:
python --version

echo.
echo Checking pip availability...

REM Try different ways to access pip
pip --version >nul 2>&1
if not errorlevel 1 (
    echo + pip found in PATH
    set PIP_CMD=pip
    goto :install_packages
)

python -m pip --version >nul 2>&1
if not errorlevel 1 (
    echo + pip found via python -m pip
    set PIP_CMD=python -m pip
    goto :install_packages
)

py -m pip --version >nul 2>&1
if not errorlevel 1 (
    echo + pip found via py -m pip
    set PIP_CMD=py -m pip
    goto :install_packages
)

echo X pip not found! Trying to install pip...
python -m ensurepip --upgrade >nul 2>&1
if errorlevel 1 (
    echo X Failed to install pip automatically
    echo.
    echo Please install pip manually:
    echo 1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py
    echo 2. Run: python get-pip.py
    echo.
    pause
    exit /b 1
)

echo + pip installed successfully
set PIP_CMD=python -m pip

:install_packages
echo.
echo Installing required packages...
echo Using command: %PIP_CMD%
echo.

REM Upgrade pip first
echo Upgrading pip...
%PIP_CMD% install --upgrade pip
if errorlevel 1 (
    echo ! Warning: Could not upgrade pip, continuing anyway...
)

REM Install from pyproject.toml if available, otherwise requirements.txt
if exist pyproject.toml (
    echo Installing from pyproject.toml...
    %PIP_CMD% install -e .
    if errorlevel 1 (
        echo X Failed to install from pyproject.toml
        echo Trying requirements.txt instead...
        goto :install_requirements
    )
    echo + Successfully installed from pyproject.toml
    goto :install_pyinstaller
)

:install_requirements
if exist requirements.txt (
    echo Installing from requirements.txt...
    %PIP_CMD% install -r requirements.txt
    if errorlevel 1 (
        echo X Failed to install requirements
        echo.
        echo Troubleshooting tips:
        echo 1. Make sure you have internet connection
        echo 2. Try running as administrator
        echo 3. Check if antivirus is blocking the installation
        echo.
        pause
        exit /b 1
    )
    echo + Requirements installed successfully
) else (
    echo X No requirements.txt or pyproject.toml found
    pause
    exit /b 1
)

:install_pyinstaller
echo.
echo Installing PyInstaller for building executable...
%PIP_CMD% install pyinstaller
if errorlevel 1 (
    echo X Failed to install PyInstaller
    echo.
    echo You can still run the application with:
    echo   python enhanced_easyjet_scraper.py
    echo   python web_gui.py
    echo.
    pause
    exit /b 1
)

echo.
echo Building Windows executable...
echo This may take a few minutes...
echo.

REM Build executable
python build_windows.py
if errorlevel 1 (
    echo X Build failed
    echo.
    echo You can still run the application with:
    echo   python enhanced_easyjet_scraper.py  (Enhanced Scraper)
    echo   python web_gui.py                   (Web Interface)
    echo   python gui_scraper.py               (Desktop GUI)
    echo.
    pause
    exit /b 1
)

echo.
echo + Setup completed successfully!
echo.
echo Files created:
echo   - dist\EasyJet_Deal_Scraper.exe (Main application)
echo   - dist\Start_GUI.bat (Quick launcher)
echo.
echo You can now run:
echo   1. Double-click: dist\EasyJet_Deal_Scraper.exe
echo   2. Or use: dist\Start_GUI.bat
echo   3. Web interface: python web_gui.py
echo   4. Enhanced scraper: python enhanced_easyjet_scraper.py
echo.
echo Tip: You can distribute the entire 'dist' folder to other computers
echo.
pause
