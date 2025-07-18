# 🪟 Windows Deployment Guide for EasyJet Deal Scraper

This guide explains how to create a Windows executable (.exe) for the EasyJet Deal Scraper.

## 📋 Prerequisites

### On Windows Machine:
1. **Python 3.8+** installed from [python.org](https://python.org)
2. **Git** installed (optional, for cloning)
3. **Chrome Browser** installed (required for live scraping)

## 🚀 Quick Setup Instructions

### Step 1: Get the Code
```bash
# Option A: Clone from GitHub
git clone https://github.com/njl808/easyjetdealscrapper.git
cd easyjetdealscrapper

# Option B: Download ZIP and extract
# Download from: https://github.com/njl808/easyjetdealscrapper/archive/main.zip
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Install PyInstaller for building executable
pip install pyinstaller
```

### Step 3: Build Windows Executable
```bash
# Run the build script
python build_windows.py
```

This will create:
- `dist/EasyJet_Deal_Scraper.exe` - Main executable
- `dist/Start_GUI.bat` - Quick launcher
- `installer.nsi` - NSIS installer script (optional)

## 📦 Alternative: Manual PyInstaller Build

If the build script doesn't work, try manual PyInstaller:

```bash
# Simple one-file executable
pyinstaller --onefile --windowed --name "EasyJet_Deal_Scraper" gui_scraper.py

# Advanced build with all dependencies
pyinstaller --clean --noconfirm easyjet_scraper.spec
```

## 🎯 Running the Application

### Desktop GUI (Recommended)
```bash
# Double-click the executable or run:
EasyJet_Deal_Scraper.exe
```

### Web Interface
```bash
# Run the web version:
python web_gui.py
# Then open: http://localhost:8000
```

### Command Line
```bash
# Direct command line usage:
python run_scraper.py --airports "Bristol" --max-price 800
```

## 🛠️ Troubleshooting

### Common Issues:

1. **"Chrome not found" errors**
   - Install Google Chrome browser
   - The scraper will automatically handle ChromeDriver

2. **"Module not found" errors**
   - Run: `pip install -r requirements.txt`
   - Make sure you're using the correct Python environment

3. **Executable won't start**
   - Try running from command prompt to see error messages
   - Check Windows Defender/antivirus isn't blocking it

4. **No deals found**
   - Check internet connection
   - The scraper includes demo data as fallback

## 📁 Distribution Package

For easy distribution, create a folder with:
```
EasyJet_Deal_Scraper/
├── EasyJet_Deal_Scraper.exe    # Main application
├── Start_GUI.bat               # Quick launcher
├── README.md                   # Instructions
├── LICENSE                     # License file
└── requirements.txt            # Dependencies (for reference)
```

## 🔧 Advanced: NSIS Installer

To create a professional Windows installer:

1. **Install NSIS** from [nsis.sourceforge.io](https://nsis.sourceforge.io)
2. **Run the installer script**:
   ```bash
   makensis installer.nsi
   ```
3. **Distribute** the generated `EasyJet_Deal_Scraper_Installer.exe`

## 🎨 Customization

### Adding an Icon
1. Create or download an `.ico` file
2. Name it `icon.ico` in the project folder
3. Rebuild with PyInstaller

### Modifying the GUI
- Edit `gui_scraper.py` for desktop interface
- Edit `web_gui.py` and `templates/` for web interface
- Rebuild after changes

## 📊 Features Included

✅ **Desktop GUI** - Full tkinter interface
✅ **Web GUI** - Modern Bootstrap interface  
✅ **Price Filtering** - Lowest prices first
✅ **Multiple Airports** - All UK departure airports
✅ **CSV Export** - Professional data export
✅ **Real-time Logging** - Progress tracking
✅ **Error Handling** - Graceful fallbacks

## 🔗 Support

- **GitHub**: https://github.com/njl808/easyjetdealscrapper
- **Issues**: Report bugs on GitHub Issues
- **License**: GPL-3.0 (Open Source)

---

**Happy deal hunting! ✈️🏖️**
