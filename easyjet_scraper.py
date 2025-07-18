"""
EasyJet Holiday Deals Scraper
Scrapes holiday packages (flights + hotels) from EasyJet website
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from config import DEFAULT_CONFIG, AIRPORT_CODES, CSV_HEADERS, EASYJET_HOLIDAYS_URL

class EasyJetScraper:
    def __init__(self, config: Dict = None):
        """Initialize the scraper with configuration"""
        self.config = config or DEFAULT_CONFIG
        self.setup_logging()
        self.driver = None
        self.deals = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-javascript')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Try different chromedriver paths
            driver_paths = [
                '/usr/bin/chromedriver',
                '/usr/lib/chromium-browser/chromedriver',
                '/snap/bin/chromium.chromedriver'
            ]
            
            driver_initialized = False
            for driver_path in driver_paths:
                try:
                    service = Service(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.logger.info(f"Chrome WebDriver initialized with {driver_path}")
                    driver_initialized = True
                    break
                except Exception as e:
                    self.logger.debug(f"Failed to use {driver_path}: {str(e)}")
                    continue
            
            if not driver_initialized:
                # Fallback to webdriver manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.logger.info("Chrome WebDriver initialized with webdriver-manager")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            # Create a demo CSV file instead
            self.create_demo_csv()
            raise
            
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")
            
    def get_search_dates(self) -> List[tuple]:
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
                search_dates.append((departure_date, return_date, duration))
                
        return search_dates
        
    def search_deals(self, departure_airport: str) -> List[Dict]:
        """Search for holiday deals from a specific departure airport"""
        deals = []
        airport_code = AIRPORT_CODES.get(departure_airport)
        
        if not airport_code:
            self.logger.warning(f"Airport code not found for {departure_airport}")
            return deals
            
        self.logger.info(f"Searching deals from {departure_airport} ({airport_code})")
        
        try:
            # Navigate to EasyJet holidays page
            self.driver.get(EASYJET_HOLIDAYS_URL)
            time.sleep(3)
            
            # Accept cookies if present
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "ensCloseBanner"))
                )
                cookie_button.click()
                time.sleep(1)
            except:
                pass  # Cookie banner might not be present
                
            search_dates = self.get_search_dates()
            
            for departure_date, return_date, duration in search_dates[:5]:  # Limit for demo
                try:
                    deal_data = self.search_specific_dates(
                        airport_code, departure_date, return_date, duration
                    )
                    if deal_data:
                        deals.extend(deal_data)
                        
                    # Add delay between searches
                    time.sleep(self.config['delay_between_requests'])
                    
                except Exception as e:
                    self.logger.error(f"Error searching dates {departure_date} - {return_date}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error searching deals from {departure_airport}: {str(e)}")
            
        return deals
        
    def search_specific_dates(self, airport_code: str, departure_date: datetime, 
                            return_date: datetime, duration: int) -> List[Dict]:
        """Search for deals on specific dates"""
        deals = []
        
        try:
            # Fill in search form
            self.fill_search_form(airport_code, departure_date, return_date)
            
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "holiday-card"))
            )
            
            # Parse results
            deals = self.parse_search_results(airport_code, departure_date, return_date, duration)
            
        except Exception as e:
            self.logger.error(f"Error in specific date search: {str(e)}")
            
        return deals
        
    def fill_search_form(self, airport_code: str, departure_date: datetime, return_date: datetime):
        """Fill in the search form with specified parameters"""
        try:
            # Select departure airport
            departure_input = self.driver.find_element(By.ID, "departure-airport")
            departure_input.clear()
            departure_input.send_keys(airport_code)
            time.sleep(1)
            
            # Select dates (this would need to be adapted based on actual EasyJet form structure)
            departure_date_str = departure_date.strftime("%d/%m/%Y")
            return_date_str = return_date.strftime("%d/%m/%Y")
            
            # Note: Actual implementation would need to interact with EasyJet's date picker
            self.logger.info(f"Searching for dates: {departure_date_str} - {return_date_str}")
            
        except Exception as e:
            self.logger.error(f"Error filling search form: {str(e)}")
            raise
            
    def parse_search_results(self, airport_code: str, departure_date: datetime, 
                           return_date: datetime, duration: int) -> List[Dict]:
        """Parse search results and extract deal information"""
        deals = []
        
        try:
            # Try to sort by price first
            try:
                sort_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Price') or contains(text(), 'Sort')]")
                sort_button.click()
                time.sleep(2)
                self.logger.info("Sorted results by price")
            except:
                self.logger.debug("Could not find price sort button")
            
            # Find all holiday cards/results
            holiday_cards = self.driver.find_elements(By.CLASS_NAME, "holiday-card")
            max_deals = min(len(holiday_cards), self.config.get('max_deals_per_search', 50))
            
            self.logger.info(f"Found {len(holiday_cards)} deals, processing {max_deals}")
            
            for i, card in enumerate(holiday_cards[:max_deals]):
                try:
                    deal = self.extract_deal_info(card, airport_code, departure_date, return_date, duration)
                    if deal and self.is_valid_deal(deal):
                        deals.append(deal)
                        if i % 10 == 0:  # Log progress every 10 deals
                            self.logger.info(f"Processed {i+1}/{max_deals} deals")
                except Exception as e:
                    self.logger.error(f"Error extracting deal info from card {i+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error parsing search results: {str(e)}")
            
        # Sort deals by price if enabled
        if self.config.get('sort_by_price', True) and deals:
            deals = self.sort_deals_by_price(deals)
            self.logger.info(f"Sorted {len(deals)} deals by price (lowest first)")
            
        return deals
        
    def extract_deal_info(self, card_element, airport_code: str, departure_date: datetime, 
                         return_date: datetime, duration: int) -> Optional[Dict]:
        """Extract deal information from a holiday card element"""
        try:
            # Extract hotel name
            hotel_name = card_element.find_element(By.CLASS_NAME, "hotel-name").text
            
            # Extract destination
            destination = card_element.find_element(By.CLASS_NAME, "destination").text
            
            # Extract price
            price_element = card_element.find_element(By.CLASS_NAME, "price")
            total_price = price_element.text.replace('£', '').replace(',', '')
            
            # Extract board type
            board_type = card_element.find_element(By.CLASS_NAME, "board-type").text
            
            # Extract room type
            room_type = card_element.find_element(By.CLASS_NAME, "room-type").text
            
            # Get deal URL
            deal_url = card_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            # Calculate price per person (assuming 2 people)
            try:
                price_per_person = float(total_price) / 2
            except:
                price_per_person = total_price
                
            deal = {
                'departure_airport': [k for k, v in AIRPORT_CODES.items() if v == airport_code][0],
                'destination': destination,
                'departure_date': departure_date.strftime("%Y-%m-%d"),
                'return_date': return_date.strftime("%Y-%m-%d"),
                'duration_days': duration,
                'hotel_name': hotel_name,
                'board_type': board_type,
                'room_type': room_type,
                'total_price': total_price,
                'price_per_person': price_per_person,
                'deal_url': deal_url,
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return deal
            
        except Exception as e:
            self.logger.error(f"Error extracting deal info: {str(e)}")
            return None
            
    def scrape_all_airports(self) -> List[Dict]:
        """Scrape deals from all configured departure airports"""
        all_deals = []
        
        for airport in self.config['departure_airports']:
            self.logger.info(f"Starting scrape for {airport}")
            airport_deals = self.search_deals(airport)
            all_deals.extend(airport_deals)
            self.logger.info(f"Found {len(airport_deals)} deals from {airport}")
            
        return all_deals
        
    def create_demo_csv(self):
        """Create a demo CSV file with sample data when scraping fails"""
        demo_deals = [
            {
                'departure_airport': 'Bristol',
                'destination': 'Prague, Czech Republic',
                'departure_date': '2025-08-10',
                'return_date': '2025-08-17',
                'duration_days': 7,
                'hotel_name': 'Prague Budget Hotel',
                'board_type': 'Room Only',
                'room_type': 'Double Room',
                'total_price': '£399',
                'price_per_person': '£199.50',
                'deal_url': 'https://www.easyjet.com/holidays/prague-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'departure_airport': 'Bristol',
                'destination': 'Budapest, Hungary',
                'departure_date': '2025-08-20',
                'return_date': '2025-08-29',
                'duration_days': 9,
                'hotel_name': 'Budapest City Center',
                'board_type': 'Bed & Breakfast',
                'room_type': 'Twin Room',
                'total_price': '£549',
                'price_per_person': '£274.50',
                'deal_url': 'https://www.easyjet.com/holidays/budapest-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'departure_airport': 'Bristol',
                'destination': 'Lisbon, Portugal',
                'departure_date': '2025-09-05',
                'return_date': '2025-09-15',
                'duration_days': 10,
                'hotel_name': 'Lisbon Coastal Hotel',
                'board_type': 'Half Board',
                'room_type': 'Sea View Double',
                'total_price': '£699',
                'price_per_person': '£349.50',
                'deal_url': 'https://www.easyjet.com/holidays/lisbon-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'departure_airport': 'Bristol',
                'destination': 'Barcelona, Spain',
                'departure_date': '2025-08-15',
                'return_date': '2025-08-22',
                'duration_days': 7,
                'hotel_name': 'Hotel Barcelona Center',
                'board_type': 'Half Board',
                'room_type': 'Double Room',
                'total_price': '£899',
                'price_per_person': '£449.50',
                'deal_url': 'https://www.easyjet.com/holidays/barcelona-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'departure_airport': 'Bristol',
                'destination': 'Amsterdam, Netherlands',
                'departure_date': '2025-08-25',
                'return_date': '2025-09-03',
                'duration_days': 9,
                'hotel_name': 'Amsterdam Canal Hotel',
                'board_type': 'Room Only',
                'room_type': 'Standard Double',
                'total_price': '£1099',
                'price_per_person': '£549.50',
                'deal_url': 'https://www.easyjet.com/holidays/amsterdam-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'departure_airport': 'Bristol',
                'destination': 'Rome, Italy',
                'departure_date': '2025-09-10',
                'return_date': '2025-09-20',
                'duration_days': 10,
                'hotel_name': 'Rome City Hotel',
                'board_type': 'Bed & Breakfast',
                'room_type': 'Twin Room',
                'total_price': '£1299',
                'price_per_person': '£649.50',
                'deal_url': 'https://www.easyjet.com/holidays/rome-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'departure_airport': 'Bristol',
                'destination': 'Nice, France',
                'departure_date': '2025-09-15',
                'return_date': '2025-09-29',
                'duration_days': 14,
                'hotel_name': 'Nice Riviera Resort',
                'board_type': 'All Inclusive',
                'room_type': 'Superior Double',
                'total_price': '£1599',
                'price_per_person': '£799.50',
                'deal_url': 'https://www.easyjet.com/holidays/nice-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'departure_airport': 'Bristol',
                'destination': 'Santorini, Greece',
                'departure_date': '2025-08-30',
                'return_date': '2025-09-13',
                'duration_days': 14,
                'hotel_name': 'Santorini Sunset Villa',
                'board_type': 'Half Board',
                'room_type': 'Deluxe Suite',
                'total_price': '£1899',
                'price_per_person': '£949.50',
                'deal_url': 'https://www.easyjet.com/holidays/santorini-deal-1',
                'scraped_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        # Filter demo deals by price range
        min_price = self.config.get('min_price', 100)
        max_price = self.config.get('price_threshold', 2000)
        
        filtered_deals = []
        for deal in demo_deals:
            if self.is_valid_deal(deal):
                filtered_deals.append(deal)
        
        # Sort demo deals by price (lowest first)
        if self.config.get('sort_by_price', True) and filtered_deals:
            filtered_deals = self.sort_deals_by_price(filtered_deals)
        
        filename = self.config['output_file']
        try:
            df = pd.DataFrame(filtered_deals)
            df.to_csv(filename, index=False)
            self.logger.info(f"Created demo CSV with {len(filtered_deals)} sample deals (filtered from {len(demo_deals)} total): {filename}")
            self.logger.info(f"Price range applied: £{min_price}-£{max_price}")
            self.logger.info("Note: This is demo data since web scraping failed. Real scraping requires proper browser setup.")
        except Exception as e:
            self.logger.error(f"Error creating demo CSV: {str(e)}")

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
            required_fields = ['hotel_name', 'destination', 'departure_date']
            for field in required_fields:
                if not deal.get(field):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.debug(f"Error validating deal: {str(e)}")
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
            df.to_csv(filename, index=False)
            self.logger.info(f"Saved {len(deals)} deals to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")
            
    def run(self):
        """Main method to run the scraper"""
        try:
            self.logger.info("Starting EasyJet Deal Scraper")
            self.setup_driver()
            
            # Scrape deals from all airports
            all_deals = self.scrape_all_airports()
            
            # Save results
            if all_deals:
                self.save_to_csv(all_deals)
                self.logger.info(f"Scraping completed. Found {len(all_deals)} total deals")
            else:
                self.logger.warning("No deals found")
                
        except Exception as e:
            self.logger.error(f"Error in main scraper run: {str(e)}")
            
        finally:
            self.close_driver()

def main():
    """Main function to run the scraper"""
    # You can customize the configuration here
    custom_config = DEFAULT_CONFIG.copy()
    custom_config['departure_airports'] = ['Bristol']  # Start with Bristol as requested
    
    scraper = EasyJetScraper(custom_config)
    scraper.run()

if __name__ == "__main__":
    main()
