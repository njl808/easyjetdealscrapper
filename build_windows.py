#!/usr/bin/env python3
"""
Build script for creating Windows executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔨 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    icon_path = "icon.ico"
    if not os.path.exists(icon_path):
        print("📝 Creating default icon...")
        # Create a simple text-based icon placeholder
        # In a real scenario, you'd want to provide a proper .ico file
        with open("icon_placeholder.txt", "w") as f:
            f.write("Icon placeholder - replace with actual .ico file for better appearance")
        print("ℹ️  No icon.ico found - executable will use default icon")

def build_executable():
    """Build the Windows executable"""
    print("🚀 Starting Windows executable build process...")
    
    # Check if we have all required files
    required_files = [
        "gui_scraper.py",
        "easyjet_scraper.py", 
        "config.py",
        "web_gui.py",
        "requirements.txt"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Create icon placeholder
    create_icon()
    
    # Clean previous builds
    if os.path.exists("dist"):
        print("🧹 Cleaning previous build...")
        shutil.rmtree("dist")
    
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Build with PyInstaller
    build_cmd = "pyinstaller --clean --noconfirm easyjet_scraper.spec"
    
    if not run_command(build_cmd, "Building executable with PyInstaller"):
        return False
    
    # Check if executable was created
    exe_path = os.path.join("dist", "EasyJet_Deal_Scraper.exe")
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
        print(f"✅ Executable created successfully!")
        print(f"📁 Location: {os.path.abspath(exe_path)}")
        print(f"📏 Size: {file_size:.1f} MB")
        return True
    else:
        print("❌ Executable not found after build")
        return False

def create_installer_script():
    """Create an NSIS installer script"""
    nsis_script = """
; EasyJet Deal Scraper Installer
; Created with NSIS

!define APPNAME "EasyJet Deal Scraper"
!define COMPANYNAME "EasyJet Deal Scraper"
!define DESCRIPTION "Find the lowest price EasyJet holiday deals"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/njl808/easyjetdealscrapper"
!define UPDATEURL "https://github.com/njl808/easyjetdealscrapper"
!define ABOUTURL "https://github.com/njl808/easyjetdealscrapper"
!define INSTALLSIZE 50000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"
Name "${APPNAME}"
Icon "icon.ico"
outFile "EasyJet_Deal_Scraper_Installer.exe"

!include LogicLib.nsh

page components
page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    setOutPath $INSTDIR
    file "dist\\EasyJet_Deal_Scraper.exe"
    file "README.md"
    file "LICENSE"
    
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    createDirectory "$SMPROGRAMS\\${COMPANYNAME}"
    createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\EasyJet_Deal_Scraper.exe"
    createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\EasyJet_Deal_Scraper.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "uninstall"
    delete "$INSTDIR\\EasyJet_Deal_Scraper.exe"
    delete "$INSTDIR\\README.md"
    delete "$INSTDIR\\LICENSE"
    delete "$INSTDIR\\uninstall.exe"
    
    delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
    delete "$DESKTOP\\${APPNAME}.lnk"
    rmDir "$SMPROGRAMS\\${COMPANYNAME}"
    rmDir "$INSTDIR"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
sectionEnd
"""
    
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    print("📦 NSIS installer script created: installer.nsi")
    print("ℹ️  To create installer, install NSIS and run: makensis installer.nsi")

def create_batch_files():
    """Create convenient batch files for Windows users"""
    
    # Batch file to run the GUI
    gui_batch = """@echo off
title EasyJet Deal Scraper
echo Starting EasyJet Deal Scraper GUI...
echo.
"EasyJet_Deal_Scraper.exe"
if errorlevel 1 (
    echo.
    echo Error: Failed to start the application
    echo Please make sure all files are present and try again.
    pause
)
"""
    
    # Batch file to run web interface
    web_batch = """@echo off
title EasyJet Deal Scraper - Web Interface
echo Starting EasyJet Deal Scraper Web Interface...
echo.
echo The web interface will open in your browser at:
echo http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
python web_gui.py
pause
"""
    
    with open("dist/Start_GUI.bat", "w") as f:
        f.write(gui_batch)
    
    with open("dist/Start_Web_Interface.bat", "w") as f:
        f.write(web_batch)
    
    print("📝 Created batch files:")
    print("   - Start_GUI.bat (Desktop GUI)")
    print("   - Start_Web_Interface.bat (Web Interface)")

def main():
    """Main build process"""
    print("🏗️  EasyJet Deal Scraper - Windows Build Tool")
    print("=" * 50)
    
    if build_executable():
        create_batch_files()
        create_installer_script()
        
        print("\n🎉 Build completed successfully!")
        print("\n📁 Files created:")
        print(f"   - dist/EasyJet_Deal_Scraper.exe (Main executable)")
        print(f"   - dist/Start_GUI.bat (Quick launcher)")
        print(f"   - dist/Start_Web_Interface.bat (Web interface launcher)")
        print(f"   - installer.nsi (NSIS installer script)")
        
        print("\n🚀 Next steps:")
        print("1. Test the executable: dist/EasyJet_Deal_Scraper.exe")
        print("2. Optional: Install NSIS and run 'makensis installer.nsi' to create installer")
        print("3. Distribute the dist/ folder or the installer to users")
        
        return True
    else:
        print("\n❌ Build failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
