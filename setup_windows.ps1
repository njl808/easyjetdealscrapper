# EasyJet Deal Scraper - PowerShell Setup Script
# This script handles pip PATH issues and provides better error handling

param(
    [switch]$SkipBuild = $false
)

# Set console encoding for proper Unicode display
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " EasyJet Deal Scraper - PowerShell Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Function to test command availability
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction SilentlyContinue) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Function to run pip command with fallbacks
function Invoke-PipCommand {
    param($Arguments)
    
    $pipCommands = @("pip", "python -m pip", "py -m pip")
    
    foreach ($cmd in $pipCommands) {
        try {
            Write-Host "Trying: $cmd $Arguments" -ForegroundColor Yellow
            $result = Invoke-Expression "$cmd $Arguments"
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Success with: $cmd" -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Host "❌ Failed with: $cmd" -ForegroundColor Red
            continue
        }
    }
    
    return $false
}

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Cyan

try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8+ from: https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check pip availability
Write-Host ""
Write-Host "🔍 Checking pip availability..." -ForegroundColor Cyan

$pipFound = $false
$pipCommands = @(
    @{cmd="pip"; desc="pip in PATH"},
    @{cmd="python -m pip"; desc="pip via python module"},
    @{cmd="py -m pip"; desc="pip via py launcher"}
)

foreach ($pipCmd in $pipCommands) {
    try {
        $result = Invoke-Expression "$($pipCmd.cmd) --version" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Found: $($pipCmd.desc)" -ForegroundColor Green
            $global:PipCommand = $pipCmd.cmd
            $pipFound = $true
            break
        }
    } catch {
        continue
    }
}

if (-not $pipFound) {
    Write-Host "❌ pip not found! Attempting to install..." -ForegroundColor Red
    try {
        python -m ensurepip --upgrade
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ pip installed successfully" -ForegroundColor Green
            $global:PipCommand = "python -m pip"
            $pipFound = $true
        }
    } catch {
        Write-Host "❌ Failed to install pip automatically" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install pip manually:" -ForegroundColor Yellow
        Write-Host "1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py" -ForegroundColor Yellow
        Write-Host "2. Run: python get-pip.py" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Upgrade pip
Write-Host ""
Write-Host "🔄 Upgrading pip..." -ForegroundColor Cyan
try {
    Invoke-Expression "$global:PipCommand install --upgrade pip" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip upgraded successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Warning: Could not upgrade pip, continuing anyway..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Warning: Could not upgrade pip, continuing anyway..." -ForegroundColor Yellow
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan

$installSuccess = $false

# Try pyproject.toml first (modern approach)
if (Test-Path "pyproject.toml") {
    Write-Host "Installing from pyproject.toml..." -ForegroundColor Yellow
    try {
        Invoke-Expression "$global:PipCommand install -e ."
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully installed from pyproject.toml" -ForegroundColor Green
            $installSuccess = $true
        }
    } catch {
        Write-Host "❌ Failed to install from pyproject.toml, trying requirements.txt..." -ForegroundColor Red
    }
}

# Fallback to requirements.txt
if (-not $installSuccess -and (Test-Path "requirements.txt")) {
    Write-Host "Installing from requirements.txt..." -ForegroundColor Yellow
    try {
        Invoke-Expression "$global:PipCommand install -r requirements.txt"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully installed from requirements.txt" -ForegroundColor Green
            $installSuccess = $true
        }
    } catch {
        Write-Host "❌ Failed to install from requirements.txt" -ForegroundColor Red
    }
}

if (-not $installSuccess) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Make sure you have internet connection" -ForegroundColor Yellow
    Write-Host "2. Try running PowerShell as administrator" -ForegroundColor Yellow
    Write-Host "3. Check if antivirus is blocking the installation" -ForegroundColor Yellow
    Write-Host "4. Try: pip install --user -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Install PyInstaller for building executable
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "🔨 Installing PyInstaller..." -ForegroundColor Cyan
    try {
        Invoke-Expression "$global:PipCommand install pyinstaller"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PyInstaller installed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install PyInstaller" -ForegroundColor Red
            $SkipBuild = $true
        }
    } catch {
        Write-Host "❌ Failed to install PyInstaller" -ForegroundColor Red
        $SkipBuild = $true
    }
}

# Build executable
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "🏗️ Building Windows executable..." -ForegroundColor Cyan
    Write-Host "This may take a few minutes..." -ForegroundColor Yellow
    
    try {
        python build_windows.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Build failed" -ForegroundColor Red
            $SkipBuild = $true
        }
    } catch {
        Write-Host "❌ Build failed" -ForegroundColor Red
        $SkipBuild = $true
    }
}

# Final status
Write-Host ""
Write-Host "🎉 Setup completed!" -ForegroundColor Green
Write-Host ""

if (-not $SkipBuild -and (Test-Path "dist\EasyJet_Deal_Scraper.exe")) {
    Write-Host "📁 Files created:" -ForegroundColor Cyan
    Write-Host "   - dist\EasyJet_Deal_Scraper.exe (Main application)" -ForegroundColor White
    Write-Host "   - dist\Start_GUI.bat (Quick launcher)" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 You can now run:" -ForegroundColor Cyan
    Write-Host "   1. Double-click: dist\EasyJet_Deal_Scraper.exe" -ForegroundColor White
    Write-Host "   2. Or use: dist\Start_GUI.bat" -ForegroundColor White
} else {
    Write-Host "⚠️ Executable build was skipped or failed" -ForegroundColor Yellow
}

Write-Host "   3. Web interface: python web_gui.py" -ForegroundColor White
Write-Host "   4. Enhanced scraper: python enhanced_easyjet_scraper.py" -ForegroundColor White
Write-Host "   5. Test setup: python test_setup.py" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tip: You can distribute the entire 'dist' folder to other computers" -ForegroundColor Cyan
Write-Host ""

# Test the installation
Write-Host "🧪 Testing installation..." -ForegroundColor Cyan
try {
    python -c "import requests, bs4, pandas, flask; print('✅ All core dependencies imported successfully')"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Installation test passed!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Installation test failed - some dependencies might be missing" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
