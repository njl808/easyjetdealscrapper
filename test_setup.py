#!/usr/bin/env python3
"""
Quick test script to verify the scraper setup
"""

import sys
import importlib.util

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        'requests',
        'bs4',
        'selenium',
        'pandas',
        'webdriver_manager'
    ]
    
    print("Testing module imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            if module == 'bs4':
                import bs4
            elif module == 'webdriver_manager':
                from webdriver_manager.chrome import ChromeDriverManager
            else:
                __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module} - {str(e)}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed imports: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All required modules imported successfully!")
        return True

def test_config():
    """Test if configuration loads correctly"""
    try:
        from config import DEFAULT_CONFIG, AIRPORT_CODES, CSV_HEADERS
        print("✓ Configuration loaded successfully")
        print(f"  - {len(AIRPORT_CODES)} airports configured")
        print(f"  - {len(CSV_HEADERS)} CSV columns defined")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {str(e)}")
        return False

def test_scraper_class():
    """Test if scraper class can be instantiated"""
    try:
        from easyjet_scraper import EasyJetScraper
        scraper = EasyJetScraper()
        print("✓ EasyJetScraper class instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ Scraper class error: {str(e)}")
        return False

def main():
    print("EasyJet Deal Scraper - Setup Test")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Scraper Class", test_scraper_class)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ Setup is ready! You can now run the scraper.")
        print("\nQuick start:")
        print("  python run_scraper.py --list-airports")
        print("  python run_scraper.py --airports Bristol")
    else:
        print("✗ Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
