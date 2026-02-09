"""
TEST SCRAPER - Scrape a single kanji for testing
"""

import requests
from bs4 import BeautifulSoup
import json

def scrape_single_kanji(url):
    """Scrape a single kanji page for testing"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Test Scraper)'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract data
    data = {
        'url': url,
        'title': soup.title.string if soup.title else None,
        'has_svg': bool(soup.find('svg', class_='stroke_order_diagram')),
        'has_readings': bool(soup.find('div', id='related-words')),
        'has_examples': bool(soup.find('div', class_='example-cont')),
        'page_size_kb': len(response.content) / 1024
    }
    
    # Try to find kanji character
    kanji_char = None
    for elem in soup.find_all(['span', 'h1', 'h2']):
        text = elem.get_text(strip=True)
        if len(text) == 1 and '\u4e00' <= text <= '\u9fff':
            kanji_char = text
            break
    
    data['character'] = kanji_char
    
    return data

if __name__ == '__main__':
    # Test URLs
    test_urls = [
        'https://jlptsensei.com/learn-japanese-kanji/%e6%97%a5-nichi-jitsu-day-sun/',
        'https://jlptsensei.com/learn-japanese-kanji/%e4%b8%80-ichi-one/',
        'https://jlptsensei.com/learn-japanese-kanji/%e5%9b%bd-koku-country/'
    ]
    
    print("🧪 Testing scraper on 3 kanji pages...\n")
    
    for url in test_urls:
        result = scrape_single_kanji(url)
        print(f"URL: {url}")
        print(f"  Character: {result['character']}")
        print(f"  Has SVG: {result['has_svg']}")
        print(f"  Has readings: {result['has_readings']}")
        print(f"  Has examples: {result['has_examples']}")
        print(f"  Page size: {result['page_size_kb']:.1f} KB")
        print()