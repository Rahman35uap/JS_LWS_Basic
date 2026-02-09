"""
Enhanced JLPT N5 Kanji Scraper
Scrapes all 80 N5 kanji from jlptsensei.com with comprehensive data extraction
"""

import requests
from bs4 import BeautifulSoup
import json
import base64
from io import BytesIO
from PIL import Image
import time
import re
from urllib.parse import urljoin, urlparse

class EnhancedKanjiScraper:
    def __init__(self):
        self.base_url = "https://jlptsensei.com/jlpt-n5-kanji-list/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.kanji_data = []
        self.scraped_count = 0
    
    def scrape_all(self):
        """Main scraping orchestrator"""
        print("🚀 Starting enhanced scraping...")
        
        # 1. Get all kanji list pages
        all_urls = self.get_paginated_urls()
        print(f"📄 Found {len(all_urls)} pages")
        
        # 2. Extract kanji from each page
        for idx, url in enumerate(all_urls, 1):
            print(f"📥 Scraping page {idx}/{len(all_urls)}: {url}")
            self.scrape_kanji_from_page(url)
            time.sleep(2)  # Rate limiting
        
        # 3. Enhance with supplementary data
        print("🔍 Enhancing with stroke count and radical data...")
        self.enhance_with_metadata()
        
        # 4. Validate all data
        print("✅ Validating data...")
        self.validate_all_kanji()
        
        # 5. Export
        print("💾 Exporting to JSON...")
        self.export_json()
        
        print(f"🎉 Complete! Scraped {len(self.kanji_data)} kanji")
    
    def get_paginated_urls(self):
        """Extract all page URLs from pagination"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            urls = [self.base_url]
            
            # Find pagination links
            pagination = soup.find('div', class_='pagination')
            if pagination:
                for link in pagination.find_all('a', href=True):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in urls and 'jlpt-n5-kanji-list' in full_url:
                            urls.append(full_url)
            
            # Also check for numbered pages
            for i in range(2, 10):  # Check up to page 10
                test_url = f"{self.base_url}page/{i}/"
                try:
                    test_resp = self.session.head(test_url, timeout=5)
                    if test_resp.status_code == 200:
                        if test_url not in urls:
                            urls.append(test_url)
                except:
                    break
            
            return urls
        except Exception as e:
            print(f"⚠️ Error getting paginated URLs: {e}")
            return [self.base_url]
    
    def scrape_kanji_from_page(self, url):
        """Scrape all kanji from a single page"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find kanji entries - try multiple selectors
            kanji_entries = (
                soup.find_all('div', class_='kanji-entry') or
                soup.find_all('article', class_='kanji') or
                soup.find_all('div', class_='kanji-item') or
                soup.find_all('tr')  # Sometimes in tables
            )
            
            if not kanji_entries:
                # Try finding links to individual kanji pages
                kanji_links = soup.find_all('a', href=re.compile(r'/jlpt-n5-kanji/'))
                for link in kanji_links:
                    kanji_url = urljoin(self.base_url, link.get('href'))
                    kanji_data = self.scrape_individual_kanji(kanji_url)
                    if kanji_data:
                        self.kanji_data.append(kanji_data)
                        self.scraped_count += 1
            else:
                for entry in kanji_entries:
                    kanji_data = self.extract_kanji_data(entry)
                    if kanji_data:
                        self.kanji_data.append(kanji_data)
                        self.scraped_count += 1
        except Exception as e:
            print(f"❌ Error scraping page {url}: {e}")
    
    def scrape_individual_kanji(self, kanji_url):
        """Scrape a single kanji from its individual page"""
        try:
            response = self.session.get(kanji_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract kanji character from title or main content
            character = None
            title = soup.find('h1')
            if title:
                # Extract kanji from title like "日 - JLPT N5 Kanji"
                match = re.search(r'^([一-龯])', title.text.strip())
                if match:
                    character = match.group(1)
            
            if not character:
                # Try finding in main content
                main_char = soup.find('span', class_=re.compile('kanji|character'))
                if main_char:
                    character = main_char.text.strip()
            
            if not character:
                return None
            
            # Check if already scraped
            if any(k['character'] == character for k in self.kanji_data):
                return None
            
            # Extract all data
            kanji_data = {
                'id': len(self.kanji_data) + 1,
                'character': character,
                'svg': self.extract_svg(soup),
                'flashcard_base64': self.extract_flashcard(soup),
                'mnemonic': self.extract_mnemonic(soup),
                'readings': self.extract_readings(soup),
                'examples': self.extract_examples(soup),
                'stroke_count': None,
                'radical': None,
                'radical_meaning': None,
                'jlpt_level': 'N5',
                'frequency_rank': None,
                'user_data': {
                    'mastery_level': 0,
                    'last_reviewed': None,
                    'next_review': None,
                    'times_correct': 0,
                    'times_wrong': 0,
                    'bookmarked': False,
                    'notes': ''
                }
            }
            
            return kanji_data
        except Exception as e:
            print(f"❌ Error scraping individual kanji {kanji_url}: {e}")
            return None
    
    def extract_kanji_data(self, entry):
        """Extract all data for a single kanji from entry element"""
        try:
            # Extract character
            character = None
            char_elem = (
                entry.find('span', class_=re.compile('kanji|character')) or
                entry.find('td') or
                entry.find('a', href=re.compile('kanji'))
            )
            
            if char_elem:
                text = char_elem.text.strip()
                # Extract first kanji character
                match = re.search(r'([一-龯])', text)
                if match:
                    character = match.group(1)
            
            if not character:
                return None
            
            # Check if already scraped
            if any(k['character'] == character for k in self.kanji_data):
                return None
            
            # Extract SVG
            svg_element = entry.find('svg', class_=re.compile('stroke|diagram'))
            svg_str = str(svg_element) if svg_element else None
            
            # Extract flashcard
            flashcard_base64 = self.extract_flashcard_from_entry(entry)
            
            # Extract readings
            readings = self.extract_readings_from_entry(entry)
            
            # Extract examples
            examples = self.extract_examples_from_entry(entry)
            
            # Extract mnemonic
            mnemonic = self.extract_mnemonic_from_entry(entry)
            
            return {
                'id': len(self.kanji_data) + 1,
                'character': character,
                'svg': svg_str,
                'flashcard_base64': flashcard_base64,
                'mnemonic': mnemonic,
                'readings': readings,
                'examples': examples,
                'stroke_count': None,
                'radical': None,
                'radical_meaning': None,
                'jlpt_level': 'N5',
                'frequency_rank': None,
                'user_data': {
                    'mastery_level': 0,
                    'last_reviewed': None,
                    'next_review': None,
                    'times_correct': 0,
                    'times_wrong': 0,
                    'bookmarked': False,
                    'notes': ''
                }
            }
        except Exception as e:
            print(f"❌ Error extracting kanji: {e}")
            return None
    
    def extract_svg(self, soup):
        """Extract SVG stroke diagram"""
        svg_element = soup.find('svg', class_=re.compile('stroke|diagram'))
        if svg_element:
            return str(svg_element)
        return None
    
    def extract_flashcard(self, soup):
        """Extract flashcard image from soup"""
        flashcard_img = (
            soup.find('img', class_=re.compile('flashcard|img-responsive')) or
            soup.find('img', alt=re.compile('kanji|flashcard', re.I))
        )
        if flashcard_img:
            img_url = flashcard_img.get('src') or flashcard_img.get('data-src')
            if img_url:
                return self.download_and_encode_image(img_url)
        return None
    
    def extract_flashcard_from_entry(self, entry):
        """Extract flashcard from entry element"""
        flashcard_img = entry.find('img', class_=re.compile('img-responsive|flashcard'))
        if flashcard_img:
            img_url = flashcard_img.get('src') or flashcard_img.get('data-src')
            if img_url:
                return self.download_and_encode_image(img_url)
        return None
    
    def extract_readings(self, soup):
        """Extract readings from full page"""
        readings = {'onyomi': [], 'kunyomi': [], 'special': []}
        
        # Find readings section
        readings_section = (
            soup.find('div', id='related-words') or
            soup.find('div', class_=re.compile('readings|pronunciation'))
        )
        
        if not readings_section:
            return readings
        
        text = readings_section.get_text()
        
        # Extract onyomi
        onyomi_match = re.search(r'Onyomi[:\s]+(.+?)(?=Kunyomi|Special|$)', text, re.IGNORECASE | re.DOTALL)
        if onyomi_match:
            onyomi_text = onyomi_match.group(1)
            readings['onyomi'] = self.parse_readings(onyomi_text)
        
        # Extract kunyomi
        kunyomi_match = re.search(r'Kunyomi[:\s]+(.+?)(?=Special|$)', text, re.IGNORECASE | re.DOTALL)
        if kunyomi_match:
            kunyomi_text = kunyomi_match.group(1)
            readings['kunyomi'] = self.parse_readings(kunyomi_text)
        
        # Extract special
        special_match = re.search(r'Special[:\s]+(.+?)$', text, re.IGNORECASE | re.DOTALL)
        if special_match:
            special_text = special_match.group(1)
            readings['special'] = self.parse_readings(special_text)
        
        return readings
    
    def extract_readings_from_entry(self, entry):
        """Extract readings from entry element"""
        readings = {'onyomi': [], 'kunyomi': [], 'special': []}
        
        related_words = entry.find('div', id='related-words')
        if not related_words:
            return readings
        
        text = related_words.get_text()
        
        # Parse readings (format varies)
        sections = {
            'onyomi': r'Onyomi[:\s]+(.+?)(?=Kunyomi|Special|$)',
            'kunyomi': r'Kunyomi[:\s]+(.+?)(?=Special|$)',
            'special': r'Special[:\s]+(.+?)$'
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                readings[key] = self.parse_readings(match.group(1))
        
        return readings
    
    def parse_readings(self, text):
        """Parse reading text into structured format"""
        readings = []
        
        # Try multiple formats
        # Format 1: "word【reading】meaning"
        pattern1 = r'([^【]+)【([^】]+)】([^【]+?)(?=[^【]*【|$)'
        matches1 = re.findall(pattern1, text)
        for word, reading, meaning in matches1:
            readings.append({
                'word': word.strip(),
                'reading': reading.strip(),
                'meaning': meaning.strip()
            })
        
        # Format 2: "reading (word) - meaning"
        if not readings:
            pattern2 = r'([^\s(]+)\s*\(([^)]+)\)\s*[-–]\s*([^\n]+)'
            matches2 = re.findall(pattern2, text)
            for reading, word, meaning in matches2:
                readings.append({
                    'word': word.strip(),
                    'reading': reading.strip(),
                    'meaning': meaning.strip()
                })
        
        # Format 3: Simple list "reading1, reading2"
        if not readings:
            readings_list = [r.strip() for r in text.split(',') if r.strip()]
            for reading in readings_list:
                readings.append({
                    'word': '',
                    'reading': reading,
                    'meaning': ''
                })
        
        return readings
    
    def extract_examples(self, soup):
        """Extract example sentences from full page"""
        examples = []
        
        example_divs = soup.find_all('div', class_=re.compile('example|sentence'))
        
        for ex_div in example_divs[:5]:  # Limit to 5 examples
            try:
                # Main sentence (preserve HTML)
                main = ex_div.find('p') or ex_div.find('div', class_=re.compile('main|japanese'))
                if main:
                    japanese_html = self.clean_html(str(main))
                else:
                    continue
                
                # Furigana
                furigana = ''
                furigana_elem = ex_div.find('div', id=re.compile('_ja|furigana'))
                if furigana_elem:
                    furigana = furigana_elem.text.strip()
                
                # Romaji
                romaji = ''
                romaji_elem = ex_div.find('div', id=re.compile('_romaji|romaji'))
                if romaji_elem:
                    romaji = romaji_elem.text.strip()
                
                # English
                english = ''
                english_elem = ex_div.find('div', id=re.compile('_en|english'))
                if english_elem:
                    english = english_elem.text.strip()
                
                if japanese_html:
                    examples.append({
                        'japanese_html': japanese_html,
                        'furigana': furigana,
                        'romaji': romaji,
                        'english': english
                    })
            except Exception as e:
                print(f"⚠️ Error parsing example: {e}")
        
        return examples
    
    def extract_examples_from_entry(self, entry):
        """Extract examples from entry element"""
        examples = []
        
        example_divs = entry.find_all('div', class_=re.compile('example'))
        
        for ex_div in example_divs[:5]:
            try:
                main = ex_div.find('div', class_='example-main') or ex_div.find('p')
                if main:
                    japanese_html = self.clean_html(str(main))
                else:
                    continue
                
                furigana = ''
                furigana_div = ex_div.find('div', id=re.compile('_ja$'))
                if furigana_div:
                    furigana = furigana_div.text.strip()
                
                romaji = ''
                romaji_div = ex_div.find('div', id=re.compile('_romaji$'))
                if romaji_div:
                    romaji = romaji_div.text.strip()
                
                english = ''
                english_div = ex_div.find('div', id=re.compile('_en$'))
                if english_div:
                    english = english_div.text.strip()
                
                if japanese_html:
                    examples.append({
                        'japanese_html': japanese_html,
                        'furigana': furigana,
                        'romaji': romaji,
                        'english': english
                    })
            except Exception as e:
                print(f"⚠️ Error parsing example: {e}")
        
        return examples
    
    def extract_mnemonic(self, soup):
        """Extract mnemonic story"""
        mnemonic_div = (
            soup.find('div', class_=re.compile('mnemonic')) or
            soup.find('p', class_=re.compile('mnemonic|story'))
        )
        if mnemonic_div:
            return mnemonic_div.text.strip()
        return None
    
    def extract_mnemonic_from_entry(self, entry):
        """Extract mnemonic from entry"""
        mnemonic_div = entry.find('div', class_='mnemonic')
        if mnemonic_div:
            return mnemonic_div.text.strip()
        return None
    
    def clean_html(self, html_str):
        """Remove ads but preserve formatting"""
        if not html_str:
            return ''
        
        soup = BeautifulSoup(html_str, 'html.parser')
        
        # Remove ad elements
        for ad in soup.find_all(['iframe', 'ins', 'script', 'style']):
            ad.decompose()
        
        # Remove ezoic and ad classes
        for ez in soup.find_all(class_=re.compile('ezoic|adsbygoogle|advertisement')):
            ez.decompose()
        
        return str(soup)
    
    def download_and_encode_image(self, url):
        """Download image and convert to base64"""
        try:
            if not url or not url.startswith('http'):
                if url and url.startswith('/'):
                    url = 'https://jlptsensei.com' + url
                else:
                    return None
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Convert to WebP for smaller size
            img = Image.open(BytesIO(response.content))
            
            # Resize if too large (max 800px width)
            if img.width > 800:
                ratio = 800 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((800, new_height), Image.Resampling.LANCZOS)
            
            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=85)
            
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/webp;base64,{base64_str}"
        except Exception as e:
            print(f"⚠️ Failed to download image {url}: {e}")
            return None
    
    def enhance_with_metadata(self):
        """Add stroke count and radical info"""
        # Basic N5 kanji metadata (subset - you'd need to complete all 80)
        metadata_lookup = {
            '日': {'stroke_count': 4, 'radical': '日', 'radical_meaning': 'sun, day'},
            '月': {'stroke_count': 4, 'radical': '月', 'radical_meaning': 'moon, month'},
            '火': {'stroke_count': 4, 'radical': '火', 'radical_meaning': 'fire'},
            '水': {'stroke_count': 4, 'radical': '水', 'radical_meaning': 'water'},
            '木': {'stroke_count': 4, 'radical': '木', 'radical_meaning': 'tree'},
            '金': {'stroke_count': 8, 'radical': '金', 'radical_meaning': 'gold, metal'},
            '土': {'stroke_count': 3, 'radical': '土', 'radical_meaning': 'earth'},
            '一': {'stroke_count': 1, 'radical': '一', 'radical_meaning': 'one'},
            '二': {'stroke_count': 2, 'radical': '二', 'radical_meaning': 'two'},
            '三': {'stroke_count': 3, 'radical': '一', 'radical_meaning': 'one'},
            # Add more as needed - this is a sample
        }
        
        for kanji in self.kanji_data:
            char = kanji['character']
            if char in metadata_lookup:
                kanji.update(metadata_lookup[char])
            else:
                # Try to infer from SVG if available
                if kanji.get('svg'):
                    # Count path elements as stroke estimate
                    svg_soup = BeautifulSoup(kanji['svg'], 'html.parser')
                    paths = svg_soup.find_all('path')
                    if paths:
                        kanji['stroke_count'] = len(paths)
    
    def validate_all_kanji(self):
        """Validate each kanji has required data"""
        errors = []
        warnings = []
        
        for kanji in self.kanji_data:
            char = kanji['character']
            
            # Required fields
            if not kanji.get('character'):
                errors.append(f"Missing character for kanji {kanji.get('id')}")
            
            if not kanji.get('svg'):
                warnings.append(f"Missing SVG for {char}")
            
            if not kanji.get('examples') or len(kanji['examples']) == 0:
                warnings.append(f"No examples for {char}")
            
            # Warnings
            if not kanji.get('flashcard_base64'):
                warnings.append(f"Missing flashcard for {char}")
            
            if not kanji.get('stroke_count'):
                warnings.append(f"Missing stroke count for {char}")
        
        if errors:
            print(f"❌ ERRORS: {len(errors)}")
            for err in errors[:5]:
                print(f"  - {err}")
        
        if warnings:
            print(f"⚠️ WARNINGS: {len(warnings)}")
            for warn in warnings[:10]:
                print(f"  - {warn}")
    
    def export_json(self, filename='kanji_data_enhanced.json'):
        """Export to JSON"""
        output = {
            'metadata': {
                'scrape_date': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'total_kanji': len(self.kanji_data),
                'version': '2.0',
                'source': 'jlptsensei.com',
                'features': ['svg', 'flashcards', 'srs', 'analytics']
            },
            'kanji': self.kanji_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Exported to {filename} ({len(self.kanji_data)} kanji)")

# Run
if __name__ == '__main__':
    scraper = EnhancedKanjiScraper()
    scraper.scrape_all()
