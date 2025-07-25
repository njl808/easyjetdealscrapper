#!/usr/bin/env python3
"""
Simple script to run the EasyJet scraper with custom settings
"""

import argparse
import json
from easyjet_scraper import EasyJetScraper
from config import DEFAULT_CONFIG, AIRPORT_CODES

def main():
    parser = argparse.ArgumentParser(description='EasyJet Holiday Deal Scraper')
    parser.add_argument('--airports', nargs='+', default=['Bristol'], 
                       help='Departure airports to search from')
    parser.add_argument('--min-duration', type=int, default=7,
                       help='Minimum trip duration in days')
    parser.add_argument('--max-duration', type=int, default=14,
                       help='Maximum trip duration in days')
    parser.add_argument('--output', default='easyjet_deals.csv',
                       help='Output CSV filename')
    parser.add_argument('--months-ahead', type=int, default=6,
                       help='Number of months ahead to search')
    parser.add_argument('--max-deals', type=int, default=50,
                       help='Maximum number of deals to collect per search')
    parser.add_argument('--max-price', type=int, default=2000,
                       help='Maximum price threshold in GBP')
    parser.add_argument('--min-price', type=int, default=100,
                       help='Minimum price threshold in GBP')
    parser.add_argument('--sort-by-price', action='store_true', default=True,
                       help='Sort deals by lowest price first (default: True)')
    parser.add_argument('--list-airports', action='store_true',
                       help='List available airports and exit')
    
    args = parser.parse_args()
    
    if args.list_airports:
        print("Available airports:")
        for name, code in AIRPORT_CODES.items():
            print(f"  {name} ({code})")
        return
    
    # Validate airports
    invalid_airports = [airport for airport in args.airports if airport not in AIRPORT_CODES]
    if invalid_airports:
        print(f"Error: Invalid airports: {', '.join(invalid_airports)}")
        print("Use --list-airports to see available options")
        return
    
    # Create custom configuration
    config = DEFAULT_CONFIG.copy()
    config.update({
        'departure_airports': args.airports,
        'min_duration': args.min_duration,
        'max_duration': args.max_duration,
        'output_file': args.output,
        'search_months_ahead': args.months_ahead,
        'max_deals_per_search': args.max_deals,
        'price_threshold': args.max_price,
        'min_price': args.min_price,
        'sort_by_price': args.sort_by_price
    })
    
    print(f"Starting scraper with configuration:")
    print(f"  Airports: {', '.join(args.airports)}")
    print(f"  Duration: {args.min_duration}-{args.max_duration} days")
    print(f"  Price range: £{args.min_price}-£{args.max_price}")
    print(f"  Max deals per search: {args.max_deals}")
    print(f"  Sort by price: {args.sort_by_price}")
    print(f"  Output: {args.output}")
    print(f"  Search period: {args.months_ahead} months ahead")
    print()
    
    # Run scraper
    scraper = EasyJetScraper(config)
    scraper.run()

if __name__ == "__main__":
    main()
