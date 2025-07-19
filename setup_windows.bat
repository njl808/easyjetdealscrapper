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
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found:
python --version

echo.
echo 📦 Installing required packages...
echo.

REM Try different pip commands
echo Trying pip...
pip install -r requirements.txt >nul 2>&1
if not errorlevel 1 (
    echo ✅ Requirements installed with pip
    goto :install_pyinstaller
)

echo Trying python -m pip...
python -m pip install -r requirements.txt >nul 2>&1
if not errorlevel 1 (
    echo ✅ Requirements installed with python -m pip
    set PIP_CMD=python -m pip
    goto :install_pyinstaller
)

echo Trying py -m pip...
py -m pip install -r requirements.txt >nul 2>&1
if not errorlevel 1 (
    echo ✅ Requirements installed with py -m pip
    set PIP_CMD=py -m pip
    goto :install_pyinstaller
)

echo ❌ Failed to install requirements with any pip method
echo.
echo Troubleshooting tips:
echo 1. Try running: python -m pip install -r requirements.txt
echo 2. Run this script as Administrator
echo 3. Check WINDOWS_TROUBLESHOOTING.md for more help
echo.
pause
exit /b 1

:install_pyinstaller
echo.
echo 🔨 Installing PyInstaller for building executable...
if defined PIP_CMD (
    %PIP_CMD% install pyinstaller
) else (
    pip install pyinstaller
)
if errorlevel 1 (
    echo ❌ Failed to install PyInstaller
    echo You can still run the application manually
    pause
    exit /b 1
)

echo.
echo 🏗️ Building Windows executable...
echo This may take a few minutes...
echo.

REM Build executable
python build_windows.py
if errorlevel 1 (
    echo ❌ Build failed
    echo.
    echo You can still run the application with:
    echo   python gui_scraper.py  (Desktop GUI)
    echo   python web_gui.py      (Web Interface)
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📁 Files created:
echo   - dist\EasyJet_Deal_Scraper.exe (Main application)
echo   - dist\Start_GUI.bat (Quick launcher)
echo.
echo 🚀 You can now run:
echo   1. Double-click: dist\EasyJet_Deal_Scraper.exe
echo   2. Or use: dist\Start_GUI.bat
echo   3. Web interface: python web_gui.py
echo.
echo 💡 Tip: You can distribute the entire 'dist' folder to other computers
echo.
pause
