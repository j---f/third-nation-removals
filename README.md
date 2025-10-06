# Third-Nation Removals Tracking

Dataset tracking third-nation deportation removals under the Trump administration.

## Features

- **Automated scraping** of Hard G History data
- **Date range parsing** for complex date formats
- **API endpoints** for easy integration
- **Data validation** to ensure quality
- **GitHub Actions automation** for daily updates

## Usage

### Update data manually
```bash
python scripts/scraper_framework.py
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

## Data Structure

Each removal entry contains:
- `destination_country`: Country where people were sent
- `date`: Date of removal (ISO format)
- `date_range_end`: End date if multi-day removal
- `number_removed`: Number of people removed
- `origin_nationalities`: Nationalities of those removed
- `source_urls`: Source URLs for verification
- `notes`: Additional information

## Automation

This repository uses GitHub Actions to automatically:
1. Scrape new data daily at 2 AM UTC
2. Validate the data structure
3. Commit and push any changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all validation passes
5. Submit a pull request

## License

MIT License
