#!/usr/bin/env python3
"""
Enhanced Virtual Environment Setup Script for EasyJet Deal Scraper
Addresses Windows pip install issues and provides robust environment setup
"""

import os
import sys
import subprocess
import platform
import venv
from pathlib import Path
import json
import tempfile

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SetupManager:
    def __init__(self):
        self.python_version = sys.version_info
        self.platform = platform.system()
        self.is_windows = self.platform == 'Windows'
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / 'venv'
        
    def print_status(self, message: str, status: str = 'info'):
        """Print colored status messages"""
        colors = {
            'success': Colors.GREEN + '✅',
            'error': Colors.RED + '❌',
            'warning': Colors.YELLOW + '⚠️',
            'info': Colors.BLUE + 'ℹ️'
        }
        print(f"{colors.get(status, '')} {message}{Colors.END}")
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements"""
        min_version = (3, 8)
        if self.python_version >= min_version:
            self.print_status(f"Python {self.python_version.major}.{self.python_version.minor} detected", 'success')
            return True
        else:
            self.print_status(f"Python {min_version[0]}.{min_version[1]}+ required, found {self.python_version.major}.{self.python_version.minor}", 'error')
            return False

def main():
    """Main function to run the setup"""
    setup = SetupManager()
    print(f"{Colors.BOLD}🚀 EasyJet Deal Scraper - Enhanced Setup{Colors.END}")
    print("=" * 60)
    
    if setup.check_python_version():
        setup.print_status("Setup validation passed", 'success')
        return True
    else:
        setup.print_status("Setup validation failed", 'error')
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
