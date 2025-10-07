#!/usr/bin/env python3
"""
Example script showing how to add custom data sources to the multi-source scraper
"""

from multi_source_scraper import MultiSourceScraper

def example_custom_scraper():
    """
    Example of how to add custom data sources
    """
    scraper = MultiSourceScraper()

    # Example 1: Add a basic source that automatically extracts numbers and countries
    scraper.add_custom_source(
        name="Example News Source",
        url="https://example-news.com/deportation-article",
        enabled=True
    )

    # Example 2: Add a source with a custom scraper function
    def custom_news_scraper():
        """
        Custom scraper for a specific news website
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            url = "https://example-news.com/deportation-article"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Custom parsing logic for this specific site
            articles = soup.find_all('article', class_='deportation-news')

            removals_data = []

            for article in articles:
                headline = article.find('h2').get_text() if article.find('h2') else ""
                content = article.find('div', class_='content').get_text() if article.find('div', class_='content') else ""

                # Extract deportation numbers and countries from content
                import re
                numbers = re.findall(r'\d+', content)
                countries = re.findall(r'\b[A-Z][a-z]+\b', content)

                if numbers and countries:
                    for number in numbers:
                        if int(number) > 10:  # Filter small numbers
                            entry = {
                                "destination_country": countries[0] if countries else "UNKNOWN",
                                "date": None,
                                "date_range_end": None,
                                "number_removed": int(number),
                                "origin_nationalities": ["Various"],
                                "source_urls": [url],
                                "notes": f"From article: {headline[:100]}...",
                                "data_source": "Example News Source",
                                "source_url": url,
                                "scraped_at": "2025-10-07T15:48:50.581Z"  # Would use datetime.now().isoformat() in real implementation
                            }
                            removals_data.append(entry)
                            break  # Only add one entry per article

            return removals_data

        except Exception as e:
            print(f"Error scraping custom news source: {e}")
            return []

    scraper.add_custom_source(
        name="Custom News Scraper",
        url="https://example-news.com",
        scraper_function=custom_news_scraper,
        enabled=True
    )

    # Example 3: Add government or NGO sources
    scraper.add_custom_source(
        name="Human Rights Watch",
        url="https://www.hrw.org/topic/immigration/us-immigration",
        enabled=True
    )

    scraper.add_custom_source(
        name="ACLU Immigration",
        url="https://www.aclu.org/issues/immigrants-rights",
        enabled=True
    )

    # Show current sources
    print("Current data sources:")
    for name, config in scraper.sources.items():
        status = "ENABLED" if config['enabled'] else "DISABLED"
        print(f"  - {name}: {config['url']} [{status}]")

    # Test scraping (optional - comment out for production)
    print("\nTesting custom sources...")
    # scraper.update_removals_data()  # Uncomment to actually run the scrapers

    print("Custom sources added successfully!")
    print("Run 'python scripts/multi_source_scraper.py' to scrape all sources including the new ones.")

if __name__ == "__main__":
    example_custom_scraper()