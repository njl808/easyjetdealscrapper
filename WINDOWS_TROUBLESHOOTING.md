# 🔧 Windows Setup Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "pip is not recognized as an internal or external command"

**Cause:** pip is not in the Windows PATH environment variable.

**Solutions:**
1. **Use the improved setup scripts:**
   - Run `setup_windows_improved.bat` instead of `setup_windows.bat`
   - Or run `setup_windows.ps1` in PowerShell

2. **Manual fix:**
   ```cmd
   python -m pip install -r requirements.txt
   ```

3. **Add pip to PATH:**
   - Find your Python installation (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python3X\`)
   - Add `Scripts` folder to PATH: `C:\Users\YourName\AppData\Local\Programs\Python\Python3X\Scripts\`

### Issue 2: Python 3.14.0b4 (Beta Version) Issues

**Cause:** You're using a beta version of Python which may have compatibility issues.

**Solutions:**
1. **Install stable Python:**
   - Download Python 3.11 or 3.12 from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Use py launcher:**
   ```cmd
   py -m pip install -r requirements.txt
   ```

### Issue 3: Permission Denied Errors

**Solutions:**
1. **Run as Administrator:**
   - Right-click Command Prompt or PowerShell
   - Select "Run as administrator"

2. **Use user installation:**
   ```cmd
   python -m pip install --user -r requirements.txt
   ```

### Issue 4: Antivirus Blocking Installation

**Solutions:**
1. **Temporarily disable antivirus** during installation
2. **Add Python folder to antivirus exclusions**
3. **Use offline installation:**
   ```cmd
   python -m pip install --no-index --find-links . -r requirements.txt
   ```

## Quick Setup Commands

### Option 1: PowerShell (Recommended)
```powershell
# Run in PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_windows.ps1
```

### Option 2: Improved Batch File
```cmd
setup_windows_improved.bat
```

### Option 3: Manual Installation
```cmd
# Check Python
python --version

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Test installation
python test_setup.py

# Run the scraper
python enhanced_easyjet_scraper.py
```

## Alternative: Use Modern Python Packaging

If you have Python 3.8+, you can use the modern approach:

```cmd
# Install from pyproject.toml
python -m pip install -e .

# This installs all dependencies automatically
```

## Verification Commands

Test if everything is working:

```cmd
# Test Python
python --version

# Test pip
python -m pip --version

# Test dependencies
python -c "import requests, bs4, pandas, flask; print('All dependencies OK')"

# Run test script
python test_setup.py

# Run the scraper
python enhanced_easyjet_scraper.py
```

## Still Having Issues?

1. **Check Python installation:**
   - Make sure Python 3.8+ is installed
   - Verify "Add to PATH" was checked during installation

2. **Reinstall Python:**
   - Uninstall current Python
   - Download from https://python.org
   - Install with "Add to PATH" checked

3. **Use virtual environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   python -m pip install -r requirements.txt
   ```

4. **Contact support:**
   - Create an issue on GitHub with your error message
   - Include your Python version and Windows version
