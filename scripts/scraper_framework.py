import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
import dateparser

def parse_date_range(date_text):
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

def scrape_hard_g_history():
    """
    Scrape the Hard G History webpage for third-nation removal data
    """
    url = "https://hardghistory.ghost.io/tracking-all-of-trumps-third-country-removals-that-we-know-of/"

    try:
        response = requests.get(url)
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
            iso_dates = parse_date_range(date_info)

            # Create entry
            entry = {
                "destination_country": country_name,
                "date": iso_dates[0] if iso_dates else None,
                "date_range_end": iso_dates[-1] if len(iso_dates) > 1 else None,
                "number_removed": number_removed,
                "origin_nationalities": origin_nationalities or ["Various"],
                "source_urls": more_info,
                "notes": who_info or ""
            }

            removals_data.append(entry)

        return removals_data

    except Exception as e:
        print(f"Error scraping data: {e}")
        return []

def update_removals_data():
    """
    Update the removals.json file with fresh data
    """
    new_data = scrape_hard_g_history()

    # Load existing data if it exists
    try:
        with open('data/removals.json', 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    # Merge data (avoid duplicates based on destination country and date)
    existing_keys = {(item.get('destination_country'), item.get('date')) for item in existing_data}
    merged_data = existing_data.copy()

    for new_entry in new_data:
        key = (new_entry.get('destination_country'), new_entry.get('date'))
        if key not in existing_keys:
            merged_data.append(new_entry)
            existing_keys.add(key)

    # Save updated data
    with open('data/removals.json', 'w') as f:
        json.dump(merged_data, f, indent=2)

    print(f"Updated data with {len(new_data)} new entries")

if __name__ == "__main__":
    update_removals_data()