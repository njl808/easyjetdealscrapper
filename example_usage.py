#!/usr/bin/env python3
"""
Example usage of the EasyJet Deal Scraper
"""

from easyjet_scraper import EasyJetScraper
from config import DEFAULT_CONFIG
import json

def example_basic_usage():
    """Example: Basic usage with default settings"""
    print("Example 1: Basic usage (Bristol airport, 7-14 days)")
    
    config = DEFAULT_CONFIG.copy()
    config['departure_airports'] = ['Bristol']
    config['search_months_ahead'] = 2  # Limit for demo
    
    scraper = EasyJetScraper(config)
    scraper.run()

def example_custom_config():
    """Example: Custom configuration"""
    print("Example 2: Custom configuration")
    
    custom_config = {
        'departure_airports': ['Bristol', 'Birmingham'],
        'min_duration': 10,
        'max_duration': 14,
        'search_months_ahead': 3,
        'output_file': 'custom_deals.csv',
        'delay_between_requests': 3,
        'max_retries': 2
    }
    
    print("Configuration:")
    print(json.dumps(custom_config, indent=2))
    
    scraper = EasyJetScraper(custom_config)
    scraper.run()

def example_multiple_airports():
    """Example: Search from multiple airports"""
    print("Example 3: Multiple airports search")
    
    config = DEFAULT_CONFIG.copy()
    config['departure_airports'] = ['Bristol', 'Manchester', 'Birmingham']
    config['output_file'] = 'multi_airport_deals.csv'
    
    scraper = EasyJetScraper(config)
    scraper.run()

if __name__ == "__main__":
    print("EasyJet Deal Scraper - Usage Examples")
    print("=" * 50)
    
    # Uncomment the example you want to run:
    
    # example_basic_usage()
    # example_custom_config()
    # example_multiple_airports()
    
    print("\nTo run an example, uncomment one of the function calls above.")
    print("\nOr use the command line interface:")
    print("  python run_scraper.py --airports Bristol --min-duration 7 --max-duration 14")
