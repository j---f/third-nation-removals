# Third-Nation Removals Tracking

Dataset tracking third-nation deportation removals under the Trump administration.

## Features

- **Multi-source data collection** from various websites and organizations
- **Automated scraping** from Hard G History, Amnesty USA, Deportation Data Project, DHS OHSS, and ICE Statistics
- **Date range parsing** for complex date formats
- **API endpoints** for easy integration
- **Data validation** to ensure quality
- **GitHub Actions automation** for daily updates
- **Extensible framework** for adding new data sources

## Data Sources

The project aggregates data from multiple sources:

1. **Hard G History** - Primary source for detailed third-country removal tracking
2. **Amnesty USA** - Human rights perspective on deportation policies
3. **Deportation Data Project** - Academic research on deportation statistics
4. **DHS OHSS** - Official government monthly enforcement reports
5. **ICE Statistics** - Immigration and Customs Enforcement official statistics

## Usage

### Update data manually
```bash
python scripts/multi_source_scraper.py
```

### Validate data
```bash
python scripts/validate.py data/removals.json
```

### Start API server
```bash
python scripts/api.py
```

### API Endpoints

- `GET /api/v1/removals` - Get all removal data with metadata
- `GET /api/v1/removals/summary` - Get summary statistics
- `GET /api/v1/removals/country/<country>` - Get removals by destination country

## Adding New Data Sources

You can easily add new data sources:

```python
from scripts.multi_source_scraper import MultiSourceScraper

scraper = MultiSourceScraper()

# Add a custom source with automatic scraping
scraper.add_custom_source(
    name="Custom Source",
    url="https://example.com/deportation-data",
    enabled=True
)

# Or add a custom scraper function
def my_custom_scraper():
    # Your custom scraping logic here
    return []

scraper.add_custom_source(
    name="My Custom Source",
    url="https://example.com",
    scraper_function=my_custom_scraper,
    enabled=True
)
```

## Data Structure

Each removal entry contains:
- `destination_country`: Country where people were sent
- `date`: Date of removal (ISO format)
- `date_range_end`: End date if multi-day removal
- `number_removed`: Number of people removed
- `origin_nationalities`: Nationalities of those removed
- `source_urls`: Source URLs for verification
- `notes`: Additional information
- `data_source`: Which source provided this data
- `source_url`: URL of the data source
- `scraped_at`: When this data was collected

## Automation

This repository uses GitHub Actions to automatically:
1. Scrape new data from all sources daily at 2 AM UTC
2. Validate the data structure
3. Commit and push any changes

## Configuration

You can enable/disable data sources by modifying the `sources` dictionary in `multi_source_scraper.py`:

```python
self.sources = {
    'hard_g_history': {
        'url': '...',
        'scraper': self.scrape_hard_g_history,
        'enabled': True  # Set to False to disable
    },
    # ... other sources
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add new data sources or improve existing scrapers
4. Ensure all validation passes
5. Submit a pull request

## License

MIT License
