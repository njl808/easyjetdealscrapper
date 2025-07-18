# EasyJet Holiday Deal Scraper

A Python web scraper that searches for EasyJet holiday deals (flights + hotels) from configurable departure airports. The scraper searches for 7-14 day holiday packages and exports the results to CSV format.

## Features

- 🛫 **Configurable Departure Airports**: Search from Bristol, London Gatwick, Manchester, and more
- 📅 **Flexible Date Ranges**: Search for trips lasting 7-14 days across multiple months
- 🏨 **Comprehensive Data**: Extracts hotel name, board type, room type, prices, and dates
- 📊 **CSV Export**: Results saved in easy-to-analyze CSV format
- 🔧 **Customizable**: Easy to configure search parameters
- 📝 **Logging**: Detailed logging for monitoring scraper progress

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/easyjetdealscraper.git
cd easyjetdealscraper
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. The scraper will automatically download and manage Chrome WebDriver.

## Usage

### Basic Usage

Run the scraper with default settings (searches from Bristol):
```bash
python run_scraper.py
```

### Custom Airport Search

Search from specific airports:
```bash
python run_scraper.py --airports "Bristol" "Manchester" "London Gatwick"
```

### Custom Duration

Search for trips of specific duration:
```bash
python run_scraper.py --min-duration 10 --max-duration 14
```

### Custom Output File

Specify output filename:
```bash
python run_scraper.py --output my_deals.csv
```

### List Available Airports

See all supported departure airports:
```bash
python run_scraper.py --list-airports
```

### Full Example

```bash
python run_scraper.py --airports "Bristol" "Birmingham" --min-duration 7 --max-duration 10 --output bristol_deals.csv --months-ahead 3
```

## Available Airports

- Bristol (BRS)
- London Gatwick (LGW)
- London Luton (LTN)
- London Stansted (STN)
- Manchester (MAN)
- Birmingham (BHX)
- Liverpool (LPL)
- Newcastle (NCL)
- Edinburgh (EDI)
- Glasgow (GLA)
- Belfast (BFS)

## Output Format

The scraper generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| departure_airport | Departure airport name |
| destination | Holiday destination |
| departure_date | Outbound flight date |
| return_date | Return flight date |
| duration_days | Trip duration in days |
| hotel_name | Name of the hotel |
| board_type | Meal plan (e.g., Half Board, All Inclusive) |
| room_type | Type of room |
| total_price | Total package price |
| price_per_person | Price per person (total/2) |
| deal_url | Direct link to the deal |
| scraped_date | When the data was scraped |

## Configuration

You can modify the default settings in `config.py`:

```python
DEFAULT_CONFIG = {
    'departure_airports': ['Bristol', 'London Gatwick', 'Manchester'],
    'min_duration': 7,
    'max_duration': 14,
    'search_months_ahead': 6,
    'output_file': 'easyjet_deals.csv',
    'delay_between_requests': 2,  # seconds
    'max_retries': 3
}
```

## Advanced Usage

### Direct Python Usage

```python
from easyjet_scraper import EasyJetScraper
from config import DEFAULT_CONFIG

# Custom configuration
config = DEFAULT_CONFIG.copy()
config['departure_airports'] = ['Bristol']
config['min_duration'] = 10

# Run scraper
scraper = EasyJetScraper(config)
scraper.run()
```

## Logging

The scraper creates detailed logs in `scraper.log` and displays progress in the console. Log levels include:
- INFO: General progress updates
- WARNING: Non-critical issues
- ERROR: Problems that prevent scraping specific deals

## Important Notes

⚠️ **Responsible Scraping**: This tool is for personal use only. Please respect EasyJet's terms of service and don't overload their servers.

⚠️ **Rate Limiting**: The scraper includes delays between requests to be respectful to the website.

⚠️ **Website Changes**: Web scrapers can break when websites update their structure. You may need to update the selectors in the code.

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**: The scraper automatically downloads ChromeDriver, but you may need to update Chrome browser.

2. **No Results Found**: 
   - Check if the website structure has changed
   - Verify your search parameters are reasonable
   - Check the logs for specific error messages

3. **Slow Performance**: 
   - Reduce the number of months to search ahead
   - Increase delays between requests
   - Limit the number of departure airports

### Getting Help

Check the `scraper.log` file for detailed error messages. Common solutions:
- Update Chrome browser to the latest version
- Check your internet connection
- Verify the website is accessible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use only. Users are responsible for complying with EasyJet's terms of service and applicable laws. The authors are not responsible for any misuse of this software.

---

**Happy deal hunting! ✈️🏖️**
