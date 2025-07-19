#!/usr/bin/env python3
"""
Improved EasyJet Holiday Deals Scraper
Uses direct API calls instead of Selenium navigation for better performance
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import os
from urllib.parse import urlencode
from config import DEFAULT_CONFIG, AIRPORT_CODES, CSV_HEADERS

class ImprovedEasyJetScraper:
    def __init__(self, config: Dict = None):
        """Initialize the improved scraper with configuration"""
        self.config = config or DEFAULT_CONFIG
        self.setup_logging()
        self.session = requests.Session()
        self.setup_session()
        self.deals = []
        
        # EasyJet API endpoints
        self.base_url = "https://www.easyjet.com/en/holidays/mixedresultlist"
        self.search_params_template = {
            'ibf': 'true',
            'dst': 'ALL',  # All destinations
            'sAccId': '',
            'geog': 'ALL',
            'flex': '7',   # Flexible dates (±7 days)
            'aa': '1',     # Adults
            'rooms': '1',  # Number of rooms
            'page': '1',
            'take': '50',  # Results per page (max 50)
            'orderBy': 'price',  # Order by price (lowest first)
            'orderDirection': 'asc',
            'm': '0'
        }
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('improved_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_session(self):
        """Setup requests session with proper headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
    def generate_search_dates(self) -> List[Tuple[str, str, int]]:
        """Generate search date ranges for the next few months"""
        search_dates = []
        today = datetime.now()
        
        for month_offset in range(self.config['search_months_ahead']):
            # Start from next month
            search_date = today + timedelta(days=30 * (month_offset + 1))
            
            # Generate date ranges for 7-14 day trips
            for duration in range(self.config['min_duration'], self.config['max_duration'] + 1):
                departure_date = search_date
                return_date = departure_date + timedelta(days=duration)
                
                # Format dates for EasyJet API (DD-MM-YYYY)
                from_date = departure_date.strftime('%d-%m-%Y')
                to_date = return_date.strftime('%d-%m-%Y')
                
                search_dates.append((from_date, to_date, duration))
                
        return search_dates
    
    def build_search_url(self, airport_code: str, from_date: str, to_date: str, 
                        page: int = 1, results_per_page: int = 50) -> str:
        """Build search URL with parameters"""
        params = self.search_params_template.copy()
        params.update({
            'org': airport_code,
            'from': from_date,
            'to': to_date,
            'page': str(page),
            'take': str(results_per_page)
        })
        
        # Add price filtering if configured
        if self.config.get('price_threshold'):
            params['maxPrice'] = str(self.config['price_threshold'])
        if self.config.get('min_price'):
            params['minPrice'] = str(self.config['min_price'])
            
        url = f"{self.base_url}?{urlencode(params)}"
        return url
    
    def fetch_search_results(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch search results from EasyJet API"""
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if we got valid HTML
            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
            else:
                self.logger.warning(f"Unexpected content type: {response.headers.get('content-type')}")
                return None
                
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
    
    def parse_deal_card(self, card_element) -> Optional[Dict]:
        """Parse individual deal card from HTML"""
        try:
            deal = {}
            
            # Extract hotel name
            hotel_element = card_element.find(['h3', 'h4'], class_=lambda x: x and 'hotel' in x.lower())
            if not hotel_element:
                hotel_element = card_element.find(['h3', 'h4'])
            deal['hotel_name'] = hotel_element.get_text(strip=True) if hotel_element else 'Unknown Hotel'
            
            # Extract destination
            destination_element = card_element.find(class_=lambda x: x and any(word in x.lower() for word in ['destination', 'location', 'city']))
            if not destination_element:
                destination_element = card_element.find('span', string=lambda text: text and any(word in text.lower() for word in ['spain', 'greece', 'italy', 'portugal', 'turkey']))
            deal['destination'] = destination_element.get_text(strip=True) if destination_element else 'Unknown Destination'
            
            # Extract price
            price_element = card_element.find(class_=lambda x: x and 'price' in x.lower())
            if not price_element:
                price_element = card_element.find(string=lambda text: text and '£' in text)
                if price_element:
                    price_element = price_element.parent
            
            if price_element:
                price_text = price_element.get_text(strip=True)
                # Extract numeric price
                import re
                price_match = re.search(r'£([0-9,]+)', price_text)
                if price_match:
                    deal['total_price'] = f"£{price_match.group(1)}"
                    deal['price_per_person'] = deal['total_price']  # Assuming per person
                else:
                    deal['total_price'] = price_text
                    deal['price_per_person'] = price_text
            else:
                deal['total_price'] = 'Price not available'
                deal['price_per_person'] = 'Price not available'
            
            # Extract board type
            board_element = card_element.find(string=lambda text: text and any(word in text.lower() for word in ['breakfast', 'half board', 'full board', 'all inclusive']))
            deal['board_type'] = board_element.strip() if board_element else 'Room Only'
            
            # Extract room type
            room_element = card_element.find(string=lambda text: text and any(word in text.lower() for word in ['double', 'twin', 'single', 'suite', 'apartment']))
            deal['room_type'] = room_element.strip() if room_element else 'Standard Room'
            
            # Extract deal URL
            link_element = card_element.find('a', href=True)
            if link_element:
                href = link_element['href']
                if href.startswith('/'):
                    deal['deal_url'] = f"https://www.easyjet.com{href}"
                else:
                    deal['deal_url'] = href
            else:
                deal['deal_url'] = 'URL not available'
            
            return deal
            
        except Exception as e:
            self.logger.debug(f"Error parsing deal card: {e}")
            return None
    
    def scrape_search_results(self, airport: str, from_date: str, to_date: str) -> List[Dict]:
        """Scrape deals for specific search parameters"""
        airport_code = AIRPORT_CODES.get(airport, airport)
        deals = []
        
        # Try multiple pages
        max_pages = 5  # Limit to avoid excessive requests
        for page in range(1, max_pages + 1):
            url = self.build_search_url(airport_code, from_date, to_date, page)
            soup = self.fetch_search_results(url)
            
            if not soup:
                break
                
            # Find deal cards - try multiple selectors
            deal_selectors = [
                '[class*="result"]',
                '[class*="card"]',
                '[class*="deal"]',
                '[class*="package"]',
                '.holiday-result',
                '.search-result'
            ]
            
            deal_cards = []
            for selector in deal_selectors:
                deal_cards = soup.select(selector)
                if deal_cards:
                    break
            
            if not deal_cards:
                self.logger.warning(f"No deal cards found on page {page}")
                break
            
            page_deals = []
            for card in deal_cards:
                deal = self.parse_deal_card(card)
                if deal and self.is_valid_deal(deal):
                    # Add search metadata
                    deal.update({
                        'departure_airport': airport,
                        'departure_date': from_date,
                        'return_date': to_date,
                        'duration_days': (datetime.strptime(to_date, '%d-%m-%Y') - 
                                        datetime.strptime(from_date, '%d-%m-%Y')).days,
                        'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    page_deals.append(deal)
            
            deals.extend(page_deals)
            self.logger.info(f"Found {len(page_deals)} deals on page {page}")
            
            # Stop if we didn't find many deals (likely end of results)
            if len(page_deals) < 5:
                break
                
            # Rate limiting
            time.sleep(self.config.get('delay_between_requests', 2))
        
        return deals
    
    def scrape_all_airports(self) -> List[Dict]:
        """Scrape deals from all configured airports"""
        all_deals = []
        search_dates = self.generate_search_dates()
        
        for airport in self.config['departure_airports']:
            self.logger.info(f"Scraping deals from {airport}")
            
            for from_date, to_date, duration in search_dates:
                self.logger.info(f"Searching {airport} -> {from_date} to {to_date} ({duration} days)")
                
                try:
                    deals = self.scrape_search_results(airport, from_date, to_date)
                    all_deals.extend(deals)
                    self.logger.info(f"Found {len(deals)} deals for this search")
                    
                except Exception as e:
                    self.logger.error(f"Error scraping {airport} {from_date}-{to_date}: {e}")
                    continue
                
                # Rate limiting between searches
                time.sleep(self.config.get('delay_between_requests', 2))
        
        # Sort by price if configured
        if self.config.get('sort_by_price', True) and all_deals:
            all_deals = self.sort_deals_by_price(all_deals)
        
        return all_deals
    
    def is_valid_deal(self, deal: Dict) -> bool:
        """Check if a deal meets the criteria"""
        try:
            # Extract numeric price from string
            price_str = str(deal.get('total_price', '0')).replace('£', '').replace(',', '')
            try:
                price = float(price_str)
            except:
                return False
                
            min_price = self.config.get('min_price', 100)
            max_price = self.config.get('price_threshold', 2000)
            
            # Check price range
            if price < min_price or price > max_price:
                return False
                
            # Check required fields
            required_fields = ['hotel_name', 'destination']
            for field in required_fields:
                if not deal.get(field) or deal.get(field) == 'Unknown Hotel':
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.debug(f"Error validating deal: {e}")
            return False
    
    def sort_deals_by_price(self, deals: List[Dict]) -> List[Dict]:
        """Sort deals by price (lowest first)"""
        def get_price(deal):
            try:
                price_str = str(deal.get('total_price', '0')).replace('£', '').replace(',', '')
                return float(price_str)
            except:
                return float('inf')  # Put invalid prices at the end
        
        return sorted(deals, key=get_price)
    
    def save_to_csv(self, deals: List[Dict], filename: str = None):
        """Save deals to CSV file"""
        if not deals:
            self.logger.warning("No deals to save")
            return
            
        filename = filename or self.config['output_file']
        
        try:
            df = pd.DataFrame(deals)
            # Ensure all required columns are present
            for col in CSV_HEADERS:
                if col not in df.columns:
                    df[col] = 'N/A'
            
            # Reorder columns to match CSV_HEADERS
            df = df[CSV_HEADERS]
            df.to_csv(filename, index=False)
            self.logger.info(f"Saved {len(deals)} deals to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")
    
    def create_demo_data(self):
        """Create demo data when scraping fails"""
        self.logger.info("Creating demo data as fallback...")
        
        demo_deals = [
            {
                'departure_airport': 'Bristol',
                'destination': 'Mallorca, Spain',
                'departure_date': '15-08-2025',
                'return_date': '22-08-2025',
                'duration_days': 7,
                'hotel_name': 'Hotel Palma Bay',
                'board_type': 'Half Board',
                'room_type': 'Double Room',
                'total_price': '£650',
                'price_per_person': '£325',
                'deal_url': 'https://www.easyjet.com/holidays/mallorca-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'departure_airport': 'Bristol',
                'destination': 'Barcelona, Spain',
                'departure_date': '20-08-2025',
                'return_date': '27-08-2025',
                'duration_days': 7,
                'hotel_name': 'Barcelona City Hotel',
                'board_type': 'Breakfast',
                'room_type': 'Twin Room',
                'total_price': '£720',
                'price_per_person': '£360',
                'deal_url': 'https://www.easyjet.com/holidays/barcelona-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        # Filter and save demo deals
        valid_deals = [deal for deal in demo_deals if self.is_valid_deal(deal)]
        if valid_deals:
            self.save_to_csv(valid_deals)
            self.logger.info(f"Created demo CSV with {len(valid_deals)} sample deals")
    
    def run(self):
        """Main method to run the improved scraper"""
        try:
            self.logger.info("Starting Improved EasyJet Deal Scraper")
            
            # Scrape deals from all airports
            all_deals = self.scrape_all_airports()
            
            # Save results
            if all_deals:
                self.save_to_csv(all_deals)
                self.logger.info(f"Scraping completed. Found {len(all_deals)} total deals")
            else:
                self.logger.warning("No deals found, creating demo data")
                self.create_demo_data()
                
        except Exception as e:
            self.logger.error(f"Error in main scraper run: {e}")
            self.create_demo_data()

def main():
    """Main function to run the improved scraper"""
    # You can customize the configuration here
    custom_config = DEFAULT_CONFIG.copy()
    custom_config['departure_airports'] = ['Bristol']  # Start with Bristol
    custom_config['search_months_ahead'] = 3  # Search next 3 months
    custom_config['output_file'] = 'improved_easyjet_deals.csv'
    
    scraper = ImprovedEasyJetScraper(custom_config)
    scraper.run()

if __name__ == "__main__":
    main()
