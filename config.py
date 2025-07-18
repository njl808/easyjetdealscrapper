"""
Configuration file for EasyJet Deal Scraper
"""

# Default configuration
DEFAULT_CONFIG = {
    'departure_airports': ['Bristol', 'London Gatwick', 'Manchester'],
    'min_duration': 7,
    'max_duration': 14,
    'search_months_ahead': 6,
    'output_file': 'easyjet_deals.csv',
    'delay_between_requests': 2,  # seconds
    'max_retries': 3
}

# EasyJet URLs and selectors
EASYJET_BASE_URL = "https://www.easyjet.com"
EASYJET_HOLIDAYS_URL = "https://www.easyjet.com/en/holidays"

# Airport codes mapping
AIRPORT_CODES = {
    'Bristol': 'BRS',
    'London Gatwick': 'LGW',
    'London Luton': 'LTN',
    'London Stansted': 'STN',
    'Manchester': 'MAN',
    'Birmingham': 'BHX',
    'Liverpool': 'LPL',
    'Newcastle': 'NCL',
    'Edinburgh': 'EDI',
    'Glasgow': 'GLA',
    'Belfast': 'BFS'
}

# CSV column headers
CSV_HEADERS = [
    'departure_airport',
    'destination',
    'departure_date',
    'return_date',
    'duration_days',
    'hotel_name',
    'board_type',
    'room_type',
    'total_price',
    'price_per_person',
    'deal_url',
    'scraped_date'
]
