# Third-Nation Removals - Distribution Report

## Current Distribution Status

### ✅ Project Successfully Compiled and Deployed

Your third-nation-removals project has been successfully compiled and deployed to GitHub at https://github.com/j---f/third-nation-removals

### 📁 File Compilation Locations

1. **Primary Data Location**: `data/removals.json`
   - Contains scraped data from Hard G History
   - Currently has 17 removal records
   - Last updated: October 7, 2025

2. **API Server**: Running on http://127.0.0.1:5000
   - Provides REST API endpoints for data access
   - Serves JSON data with metadata

3. **GitHub Repository**: https://github.com/j---f/third-nation-removals
   - All source code and configuration files
   - Automated daily updates via GitHub Actions

### 🔧 Project Structure

```
third-nation-removals/
├── data/
│   └── removals.json          # Primary data file
├── scripts/
│   ├── scraper_framework.py   # Web scraper
│   ├── validate.py           # Data validation
│   ├── api.py                # Flask API server
│   └── export_data.py        # Export functionality
├── .github/
│   └── workflows/
│       └── auto-update.yml   # GitHub Actions
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation
└── .gitignore               # Git ignore rules
```

## Export Options

The project now supports exporting data in multiple formats:

### 1. JSON Format
- **File Location**: `exports/third_nation_remoals_YYYYMMDD_HHMMSS.json`
- **Description**: Complete data in JSON format with full structure
- **Usage**: Best for programmatic access and data interchange

### 2. CSV Format
- **File Location**: `exports/third_nation_removals_YYYYMMDD_HHMMSS.csv`
- **Description**: Flattened data in CSV format for spreadsheet applications
- **Usage**: Best for data analysis in Excel, Google Sheets, or pandas

### 3. Markdown Format
- **File Location**: `exports/third_nation_removals_YYYYMMDD_HHMMSS.md`
- **Description**: Formatted report with summary statistics and tables
- **Usage**: Best for documentation and GitHub README files

### 4. Plain Text Format
- **File Location**: `exports/third_nation_removals_YYYYMMDD_HHMMSS.txt`
- **Description**: Simple text report with structured data
- **Usage**: Best for printing or simple text readers

### 5. PDF Format
- **File Location**: `exports/third_nation_removals_YYYYMMDD_HHMMSS.pdf`
- **Description**: Professional report with tables and formatting
- **Usage**: Best for sharing, printing, and formal presentations

### 6. Word Document Format
- **File Location**: `exports/third_nation_removals_YYYYMMDD_HHMMSS.docx`
- **Description**: Word document with formatted tables and text
- **Usage**: Best for editing and collaboration in Microsoft Word

## How to Export Data

### Command Line
```bash
cd third-nation-removals
python3 scripts/export_data.py
```

This will export the data in all available formats to the `exports/` directory.

### API Access
You can also access the data via the API endpoints:

1. **Get All Data**: `GET http://127.0.0.1:5000/api/v1/removals`
2. **Get Summary**: `GET http://127.0.0.1:5000/api/v1/removals/summary`
3. **Get by Country**: `GET http://127.0.0.1:5000/api/v1/removals/country/<country>`

## Current Data Summary

- **Total Removal Events**: 17
- **Total People Removed**: 1,202+
- **Destination Countries**: 15
- **Data Sources**: Hard G History

### Top Destination Countries by People Removed

1. **PANAMA**: 300 people
2. **EL SALVADOR**: 252 people
3. **UZBEKISTAN**: 131 people
4. **QATAR**: 120 people
5. **COSTA RICA**: 200 people

## Automation

The project includes automated daily updates via GitHub Actions:

1. **Scrapes new data** from Hard G History
2. **Validates data structure** for quality assurance
3. **Commits and pushes** any changes to GitHub

## Dependencies

The project requires the following Python packages:

- requests (for web scraping)
- beautifulsoup4 (for HTML parsing)
- flask (for API server)
- dateparser (for date parsing)
- pandas (for data manipulation)
- reportlab (for PDF export)
- python-docx (for Word document export)

## Installation

```bash
cd third-nation-removals
pip3 install -r requirements.txt
```

## Testing the Distribution

1. **Test the scraper**:
   ```bash
   python3 scripts/scraper_framework.py
   ```

2. **Test the API server**:
   ```bash
   python3 scripts/api.py
   ```
   Then visit http://127.0.0.1:5000/api/v1/removals

3. **Test data validation**:
   ```bash
   python3 scripts/validate.py data/removals.json
   ```

4. **Test export functionality**:
   ```bash
   python3 scripts/export_data.py
   ```

## Future Enhancements

1. **Additional export formats**: XML, YAML, Excel
2. **Data visualization**: Charts and graphs
3. **Advanced filtering**: By date range, nationality, etc.
4. **Email notifications**: For data updates
5. **Database integration**: For larger datasets