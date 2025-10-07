import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
import dateparser
import pandas as pd
import time
from urllib.parse import urljoin, urlparse

class MultiSourceScraper:
    """
    Multi-source scraper for third-nation removals data from various websites
    """

    def __init__(self):
        self.sources = {
            'hard_g_history': {
                'url': 'https://hardghistory.ghost.io/tracking-all-of-trumps-third-country-removals-that-we-know-of/',
                'scraper': self.scrape_hard_g_history,
                'enabled': True
            },
            'amnesty_usa': {
                'url': 'https://www.amnestyusa.org/blog/third-country-deportations-another-cruel-piece-of-president-trumps-anti-immigrant-agenda/',
                'scraper': self.scrape_amnesty_usa,
                'enabled': True
            },
            'deportation_data': {
                'url': 'https://deportationdata.org/data/ice.html',
                'scraper': self.scrape_deportation_data,
                'enabled': True
            },
            'dhs_ohss': {
                'url': 'https://ohss.dhs.gov/topics/immigration/immigration-enforcement/monthly-tables',
                'scraper': self.scrape_dhs_ohss,
                'enabled': True
            },
            'ice_statistics': {
                'url': 'https://www.ice.gov/statistics',
                'scraper': self.scrape_ice_statistics,
                'enabled': True
            }
        }

    def parse_date_range(self, date_text):
        """
        Parse complex date ranges like 'Sept. 5-6, 2025' or 'Sept. 30-Oct. 1, 2025'
        Returns list of ISO dates
        """
        if not date_text:
            return [datetime.now().strftime('%Y-%m-%d')]

        # Remove "Date(s):" prefix if present
        date_text = re.sub(r'^Date$[^:]*:', '', date_text).strip()

        # Handle ranges with hyphens
        if '-' in date_text and ',' in date_text:
            # Split on comma to get year
            parts = date_text.split(',')
            if len(parts) >= 2:
                year = parts[-1].strip()
                date_part = ','.join(parts[:-1])

                # Check if it's a cross-month range (contains two month names)
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                month_count = sum(1 for month in month_names if month in date_part)

                if month_count >= 2:
                    # Cross-month range like "Sept. 30-Oct. 1, 2025"
                    date_ranges = date_part.split('-')
                    if len(date_ranges) == 2:
                        start_date = f"{date_ranges[0].strip()}, {year}"
                        end_date = f"{date_ranges[1].strip()}, {year}"

                        start_parsed = dateparser.parse(start_date)
                        end_parsed = dateparser.parse(end_date)

                        if start_parsed and end_parsed:
                            dates = []
                            current = start_parsed
                            while current <= end_parsed:
                                dates.append(current.strftime('%Y-%m-%d'))
                                current += timedelta(days=1)
                            return dates
                else:
                    # Same-month range like "Sept. 5-6, 2025"
                    date_match = re.search(r'([A-Za-z]+\.?)\s*(\d+)\s*-\s*(\d+)', date_part)
                    if date_match:
                        month_str, start_day, end_day = date_match.groups()
                        start_date = f"{month_str} {start_day}, {year}"
                        end_date = f"{month_str} {end_day}, {year}"

                        start_parsed = dateparser.parse(start_date)
                        end_parsed = dateparser.parse(end_date)

                        if start_parsed and end_parsed:
                            dates = []
                            current = start_parsed
                            while current <= end_parsed:
                                dates.append(current.strftime('%Y-%m-%d'))
                                current += timedelta(days=1)
                            return dates

        # Handle single dates
        parsed = dateparser.parse(date_text)
        if parsed:
            return [parsed.strftime('%Y-%m-%d')]

        return [datetime.now().strftime('%Y-%m-%d')]

    def scrape_hard_g_history(self):
        """
        Scrape the Hard G History webpage for third-nation removal data
        """
        url = "https://hardghistory.ghost.io/tracking-all-of-trumps-third-country-removals-that-we-know-of/"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find country sections (h2 tags followed by details)
            country_sections = soup.find_all('h2')
            removals_data = []

            for section in country_sections:
                country_name = section.get_text().strip()
                if not country_name:
                    continue

                # Get all paragraphs until next h2
                current = section.next_sibling
                details = []
                while current and (current.name != 'h2'):
                    if current.name == 'p':
                        details.append(current.get_text().strip())
                    current = current.next_sibling

                # Parse details
                date_info = None
                who_info = None
                more_info = []

                for detail in details:
                    if detail.startswith('Date(s):'):
                        date_info = detail
                    elif detail.startswith('Who:'):
                        who_info = detail
                    elif detail.startswith('More:'):
                        # Extract URLs from "More:" section
                        urls = re.findall(r'https?://[^\s)]+', detail)
                        more_info.extend(urls)

                # Extract number of people
                number_removed = None
                if who_info:
                    num_match = re.search(r'(\d+)', who_info)
                    if num_match:
                        number_removed = int(num_match.group(1))

                # Extract origin nationalities
                origin_nationalities = []
                if who_info:
                    # This is a simplified approach - you might want more sophisticated parsing
                    nationality_keywords = ['Iranians', 'Russians', 'Venezuelans', 'Cubans', 'Afghans']
                    for keyword in nationality_keywords:
                        if keyword[:-1].lower() in who_info.lower():
                            origin_nationalities.append(keyword[:-1])

                # Parse dates
                iso_dates = self.parse_date_range(date_info)

                # Create entry
                entry = {
                    "destination_country": country_name,
                    "date": iso_dates[0] if iso_dates else None,
                    "date_range_end": iso_dates[-1] if len(iso_dates) > 1 else None,
                    "number_removed": number_removed,
                    "origin_nationalities": origin_nationalities or ["Various"],
                    "source_urls": more_info,
                    "notes": who_info or "",
                    "data_source": "Hard G History",
                    "source_url": url,
                    "scraped_at": datetime.now().isoformat()
                }

                removals_data.append(entry)

            return removals_data

        except Exception as e:
            print(f"Error scraping Hard G History: {e}")
            return []

    def scrape_amnesty_usa(self):
        """
        Scrape Amnesty USA blog post about third-country deportations
        """
        url = "https://www.amnestyusa.org/blog/third-country-deportations-another-cruel-piece-of-president-trumps-anti-immigrant-agenda/"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract article content
            article_content = soup.find('article') or soup.find('div', class_='entry-content')
            if not article_content:
                return []

            # Look for mentions of countries and numbers
            text_content = article_content.get_text()

            # Extract potential removal data from text
            removals_data = []

            # Look for country mentions with numbers
            country_patterns = [
                r'(\d+)\s+(?:people|migrants|individuals)\s+(?:to|sent to)\s+([A-Z][a-z]+)',
                r'([A-Z][a-z]+).*?(\d+)\s+(?:people|migrants|individuals)',
                r'sent\s+(\d+)\s+(?:people|migrants|individuals).*?to\s+([A-Z][a-z]+)'
            ]

            for pattern in country_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        number, country = match
                        try:
                            number_removed = int(number)
                            entry = {
                                "destination_country": country.upper(),
                                "date": None,
                                "date_range_end": None,
                                "number_removed": number_removed,
                                "origin_nationalities": ["Various"],
                                "source_urls": [url],
                                "notes": f"Extracted from Amnesty USA article",
                                "data_source": "Amnesty USA",
                                "source_url": url,
                                "scraped_at": datetime.now().isoformat()
                            }
                            removals_data.append(entry)
                        except ValueError:
                            continue

            return removals_data

        except Exception as e:
            print(f"Error scraping Amnesty USA: {e}")
            return []

    def scrape_deportation_data(self):
        """
        Scrape deportation data from deportationdata.org
        """
        url = "https://deportationdata.org/data/ice.html"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            removals_data = []

            # Look for tables with deportation data
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # Try to extract country and numbers
                        cell_texts = [cell.get_text().strip() for cell in cells]

                        # Look for patterns like "Country Name: 123"
                        for i, text in enumerate(cell_texts):
                            if ':' in text and any(char.isdigit() for char in text):
                                parts = text.split(':')
                                if len(parts) == 2:
                                    country = parts[0].strip()
                                    number_part = parts[1].strip()
                                    try:
                                        number = int(re.search(r'\d+', number_part).group())
                                        entry = {
                                            "destination_country": country.upper(),
                                            "date": None,
                                            "date_range_end": None,
                                            "number_removed": number,
                                            "origin_nationalities": ["Various"],
                                            "source_urls": [url],
                                            "notes": f"Extracted from deportation data table",
                                            "data_source": "Deportation Data Project",
                                            "source_url": url,
                                            "scraped_at": datetime.now().isoformat()
                                        }
                                        removals_data.append(entry)
                                    except (ValueError, AttributeError):
                                        continue

            return removals_data

        except Exception as e:
            print(f"Error scraping Deportation Data: {e}")
            return []

    def scrape_dhs_ohss(self):
        """
        Scrape DHS OHSS monthly tables for immigration enforcement data
        """
        url = "https://ohss.dhs.gov/topics/immigration/immigration-enforcement/monthly-tables"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            removals_data = []

            # Look for links to monthly reports
            links = soup.find_all('a', href=True)
            report_links = []

            for link in links:
                href = link['href']
                if 'monthly' in href.lower() or 'table' in href.lower():
                    full_url = urljoin(url, href)
                    report_links.append(full_url)

            # For now, just return metadata about available reports
            # In a full implementation, you'd scrape each report
            if report_links:
                entry = {
                    "destination_country": "MULTIPLE",
                    "date": None,
                    "date_range_end": None,
                    "number_removed": None,
                    "origin_nationalities": ["Various"],
                    "source_urls": report_links[:5],  # Limit to first 5
                    "notes": f"DHS OHSS monthly reports available: {len(report_links)} reports found",
                    "data_source": "DHS OHSS",
                    "source_url": url,
                    "scraped_at": datetime.now().isoformat()
                }
                removals_data.append(entry)

            return removals_data

        except Exception as e:
            print(f"Error scraping DHS OHSS: {e}")
            return []

    def scrape_ice_statistics(self):
        """
        Scrape ICE statistics page
        """
        url = "https://www.ice.gov/statistics"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            removals_data = []

            # Look for statistics and data
            stats_content = soup.find_all(['div', 'section'], class_=re.compile(r'(stat|data|number)'))

            for content in stats_content:
                text = content.get_text()

                # Look for deportation/removal statistics
                if any(keyword in text.lower() for keyword in ['deport', 'remov', 'third.country']):
                    # Extract numbers and context
                    numbers = re.findall(r'\d+(?:,\d+)*', text)

                    for number_str in numbers:
                        try:
                            number = int(number_str.replace(',', ''))
                            if number > 10:  # Filter out small numbers that might not be deportation counts
                                entry = {
                                    "destination_country": "MULTIPLE",
                                    "date": None,
                                    "date_range_end": None,
                                    "number_removed": number,
                                    "origin_nationalities": ["Various"],
                                    "source_urls": [url],
                                    "notes": f"ICE statistics: {text[:200]}...",
                                    "data_source": "ICE Statistics",
                                    "source_url": url,
                                    "scraped_at": datetime.now().isoformat()
                                }
                                removals_data.append(entry)
                        except ValueError:
                            continue

            return removals_data

        except Exception as e:
            print(f"Error scraping ICE Statistics: {e}")
            return []

    def scrape_all_sources(self):
        """
        Scrape all enabled sources and combine the data
        """
        all_data = []

        for source_name, source_config in self.sources.items():
            if source_config['enabled']:
                print(f"Scraping {source_name}...")
                try:
                    data = source_config['scraper']()
                    all_data.extend(data)
                    print(f"  Found {len(data)} records from {source_name}")
                except Exception as e:
                    print(f"  Error scraping {source_name}: {e}")

                # Be respectful to servers
                time.sleep(1)

        return all_data

    def add_custom_source(self, name, url, scraper_function=None, enabled=True):
        """
        Add a custom data source
        """
        if scraper_function is None:
            # Create a basic scraper that extracts numbers and countries from text
            def basic_scraper():
                try:
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text_content = soup.get_text()

                    removals_data = []

                    # Look for country mentions with numbers
                    country_patterns = [
                        r'(\d+)\s+(?:people|migrants|individuals)\s+(?:to|sent to)\s+([A-Z][a-z]+)',
                        r'([A-Z][a-z]+).*?(\d+)\s+(?:people|migrants|individuals)',
                        r'sent\s+(\d+)\s+(?:people|migrants|individuals).*?to\s+([A-Z][a-z]+)'
                    ]

                    for pattern in country_patterns:
                        matches = re.findall(pattern, text_content, re.IGNORECASE)
                        for match in matches:
                            if len(match) == 2:
                                number, country = match
                                try:
                                    number_removed = int(number)
                                    entry = {
                                        "destination_country": country.upper(),
                                        "date": None,
                                        "date_range_end": None,
                                        "number_removed": number_removed,
                                        "origin_nationalities": ["Various"],
                                        "source_urls": [url],
                                        "notes": f"Extracted from {name}",
                                        "data_source": name,
                                        "source_url": url,
                                        "scraped_at": datetime.now().isoformat()
                                    }
                                    removals_data.append(entry)
                                except ValueError:
                                    continue

                    return removals_data

                except Exception as e:
                    print(f"Error scraping {name}: {e}")
                    return []

            scraper_function = basic_scraper

        self.sources[name] = {
            'url': url,
            'scraper': scraper_function,
            'enabled': enabled
        }

    def update_removals_data(self):
        """
        Update the removals.json file with fresh data from all sources
        """
        new_data = self.scrape_all_sources()

        # Load existing data if it exists
        try:
            with open('data/removals.json', 'r') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Merge data (avoid duplicates based on destination country, date, and source)
        existing_keys = {(item.get('destination_country'), item.get('date'), item.get('data_source')) for item in existing_data}
        merged_data = existing_data.copy()

        for new_entry in new_data:
            key = (new_entry.get('destination_country'), new_entry.get('date'), new_entry.get('data_source'))
            if key not in existing_keys:
                merged_data.append(new_entry)
                existing_keys.add(key)

        # Save updated data
        with open('data/removals.json', 'w') as f:
            json.dump(merged_data, f, indent=2)

        print(f"Updated data with {len(new_data)} new entries from {len([s for s in self.sources.values() if s['enabled']])} sources")

if __name__ == "__main__":
    scraper = MultiSourceScraper()
    scraper.update_removals_data()