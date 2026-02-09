"""
JLPT n4 COMPLETE SCRAPER - FINAL WORKING VERSION
Extracts ALL readings AND rich text examples with HTML styling
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import sys
from datetime import datetime
from urllib.parse import urljoin
from tqdm import tqdm

class JLPTn4CompleteScraper:
    def __init__(self, rate_limit=1.5):
        self.base_url = "https://jlptsensei.com/jlpt-n4-kanji-list/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.rate_limit = rate_limit
        self.kanji_data = []
        self.errors = []
        
    def get_all_kanji_urls(self):
        """Get all kanji detail URLs"""
        print("🔍 Fetching main kanji list page...")
        
        try:
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            urls = []
            
            # Method 1: Look for kanji in tables
            tables = soup.find_all('table')
            for table in tables:
                links = table.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/learn-japanese-kanji/' in href and not href.endswith('/feed/'):
                        full_url = urljoin(self.base_url, href)
                        if full_url not in urls:
                            urls.append(full_url)
            
            # Method 2: Look for all kanji links
            if not urls:
                kanji_links = soup.select('a[href*="/learn-japanese-kanji/"]')
                for link in kanji_links:
                    href = link['href']
                    if not href.endswith('/feed/'):
                        full_url = urljoin(self.base_url, href)
                        if full_url not in urls:
                            urls.append(full_url)
            
            urls = list(dict.fromkeys(urls))
            print(f"✅ Found {len(urls)} kanji detail URLs")
            return urls
            
        except Exception as e:
            self.errors.append(f"Error getting kanji URLs: {str(e)}")
            return []
    
    def scrape_kanji_detail(self, url):
        """Scrape complete kanji data from detail page"""
        try:
            print(f"  📥 Fetching: {url}")
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Extract kanji character
            kanji_char = self._extract_kanji_char(soup, url)
            if not kanji_char:
                return None
            
            # 2. Extract meaning
            meaning = self._extract_meaning(soup)
            
            # 3. Extract ALL readings (FIXED VERSION)
            readings = self._extract_all_readings_fixed(soup)
            
            # 4. Extract stroke count
            stroke_count = self._extract_stroke_count(soup)
            
            # 5. Extract stroke diagram
            svg_data = self._extract_stroke_diagram(soup)
            
            # 6. Extract rich text examples
            examples = self._extract_rich_examples(soup, kanji_char)
            
            # 7. Extract JLPT level
            jlpt_level = "n4"
            
            kanji_data = {
                'character': kanji_char,
                'meaning': meaning,
                'readings': readings,
                'stroke_count': stroke_count,
                'stroke_diagram': svg_data.get('svg'),
                'stroke_image': svg_data.get('image_url'),
                'examples': examples,
                'jlpt_level': jlpt_level,
                'page_url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Print summary
            print(f"    ✅ {kanji_char} - {meaning}")
            print(f"      📖 Readings: {len(readings['onyomi'])} Onyomi, "
                  f"{len(readings['kunyomi'])} Kunyomi, "
                  f"{len(readings['special'])} Special")
            print(f"      📝 Examples: {len(examples)}")
            
            return kanji_data
            
        except Exception as e:
            error_msg = f"Error scraping {url}: {str(e)}"
            print(f"    ❌ {error_msg}")
            self.errors.append(error_msg)
            return None
    
    def _extract_kanji_char(self, soup, url):
        """Extract kanji character"""
        # Try multiple selectors
        selectors = [
            'span.kanji-character',
            '.kanji-large',
            '.kanji-main',
            'h1.kanji',
            '.entry-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                match = re.search(r'[\u4e00-\u9fff]', text)
                if match:
                    return match.group(0)
        
        # From title
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            match = re.search(r'([\u4e00-\u9fff])\s*-', title_text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_meaning(self, soup):
        """Extract kanji meaning"""
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            match = re.search(r'Meaning:\s*(.+?)(?:\s*-|$)', title_text)
            if match:
                return match.group(1).strip()
        
        return "Meaning not found"
    
    def _extract_all_readings_fixed(self, soup):
        """Extract ALL readings - PROPERLY FIXED VERSION"""
        readings = {
            'onyomi': [],
            'kunyomi': [],
            'special': []
        }
        
        # Find the vocabulary section
        vocab_div = soup.find('div', id='related-words')
        if not vocab_div:
            return readings
        
        # Get all <p> tags in the vocabulary section
        paragraphs = vocab_div.find_all('p')
        
        for p in paragraphs:
            # Get all text lines from this paragraph
            lines = []
            for content in p.contents:
                if isinstance(content, str):
                    lines.append(content.strip())
                elif content.name == 'br':
                    lines.append('\n')
            
            # Combine and split by newline
            text_content = ''.join(lines)
            
            # Determine reading type
            reading_type = None
            if 'Onyomi Readings' in text_content:
                reading_type = 'onyomi'
                # Remove the header
                text_content = text_content.replace('Onyomi Readings', '').strip()
            elif 'Kunyomi Readings' in text_content:
                reading_type = 'kunyomi'
                text_content = text_content.replace('Kunyomi Readings', '').strip()
            elif 'Special Readings' in text_content:
                reading_type = 'special'
                text_content = text_content.replace('Special Readings', '').strip()
            else:
                continue
            
            # Split into individual examples
            examples = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            # Parse each example
            for example in examples:
                if '【' in example and '】' in example:
                    # Find positions of 【 and 】
                    start = example.find('【')
                    end = example.find('】')
                    
                    if start != -1 and end != -1 and start < end:
                        word = example[:start].strip()
                        reading = example[start+1:end].strip()
                        meaning = example[end+1:].strip()
                        
                        # Clean up meaning
                        meaning = meaning.replace('】', '').strip()
                        
                        readings[reading_type].append({
                            'word': word,
                            'reading': reading,
                            'meaning': meaning
                        })
        
        # If no readings found with paragraph method, try regex method
        if not any(len(readings[rt]) > 0 for rt in ['onyomi', 'kunyomi', 'special']):
            all_text = vocab_div.get_text()
            
            # Extract Onyomi section
            onyomi_pattern = r'Onyomi Readings(.*?)(?:Kunyomi Readings|Special Readings|$)'
            onyomi_match = re.search(onyomi_pattern, all_text, re.DOTALL | re.IGNORECASE)
            if onyomi_match:
                onyomi_text = onyomi_match.group(1).strip()
                self._parse_readings_from_text(onyomi_text, readings, 'onyomi')
            
            # Extract Kunyomi section
            kunyomi_pattern = r'Kunyomi Readings(.*?)(?:Special Readings|$)'
            kunyomi_match = re.search(kunyomi_pattern, all_text, re.DOTALL | re.IGNORECASE)
            if kunyomi_match:
                kunyomi_text = kunyomi_match.group(1).strip()
                self._parse_readings_from_text(kunyomi_text, readings, 'kunyomi')
            
            # Extract Special section
            special_pattern = r'Special Readings(.*?)$'
            special_match = re.search(special_pattern, all_text, re.DOTALL | re.IGNORECASE)
            if special_match:
                special_text = special_match.group(1).strip()
                self._parse_readings_from_text(special_text, readings, 'special')
        
        return readings
    
    def _parse_readings_from_text(self, text, readings_dict, reading_type):
        """Parse readings from text content"""
        # Split into lines
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or '【' not in line or '】' not in line:
                continue
            
            # Find 【 and 】
            start = line.find('【')
            end = line.find('】')
            
            if start != -1 and end != -1 and start < end:
                word = line[:start].strip()
                reading = line[start+1:end].strip()
                meaning = line[end+1:].strip()
                
                # Clean up
                meaning = meaning.replace('】', '').strip()
                
                readings_dict[reading_type].append({
                    'word': word,
                    'reading': reading,
                    'meaning': meaning
                })
    
    def _extract_stroke_count(self, soup):
        """Extract stroke count"""
        patterns = [
            r'Stroke Count:\s*(\d+)',
            r'Strokes:\s*(\d+)',
            r'(\d+)\s*strokes',
            r'画数:\s*(\d+)'
        ]
        
        all_text = soup.get_text()
        
        for pattern in patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        
        return None
    
    def _extract_stroke_diagram(self, soup):
        """Extract stroke order diagram"""
        # Look for SVG
        svg = soup.find('svg')
        if svg:
            return {'svg': str(svg), 'image_url': None}
        
        # Look for image
        img = soup.find('img', src=re.compile(r'stroke|order|diagram', re.I))
        if img and img.get('src'):
            return {'svg': None, 'image_url': img['src']}
        
        return {'svg': None, 'image_url': None}
    
    def _extract_rich_examples(self, soup, kanji_char):
        """Extract rich text examples with HTML styling"""
        examples = []
        
        # Find all example containers
        example_containers = soup.find_all('div', class_='example-cont')
        
        for container in example_containers:
            try:
                example_id = container.get('id', '')
                
                # Get Japanese text with HTML styling
                jp_div = container.find('div', class_='example-main')
                if not jp_div:
                    continue
                    
                jp_paragraph = jp_div.find('p', class_='jp')
                if jp_paragraph:
                    # Preserve the HTML exactly as it is
                    japanese_html = str(jp_paragraph)
                    
                    # Clean unwanted tags but preserve styling
                    html_soup = BeautifulSoup(japanese_html, 'html.parser')
                    
                    # Remove ads, scripts, iframes
                    for tag in html_soup.find_all(['script', 'iframe', 'ins', 'style', 'noscript']):
                        tag.decompose()
                    
                    # Remove ezoic classes but keep color class
                    for tag in html_soup.find_all(class_=lambda x: x and 'ezoic' in x):
                        tag.decompose()
                    
                    # Convert color class to highlight
                    for span in html_soup.find_all('span', class_='color'):
                        span['class'] = 'kanji-highlight'
                    
                    japanese_html = str(html_soup)
                else:
                    # Fallback to plain text
                    japanese_html = jp_div.get_text(strip=True)
                
                # Extract example number from ID
                example_num = example_id.replace('example_', '')
                
                # Get furigana
                furigana_div = container.find('div', id=f'example_{example_num}_ja')
                furigana = furigana_div.get_text(strip=True) if furigana_div else ""
                
                # Get romaji
                romaji_div = container.find('div', id=f'example_{example_num}_romaji')
                romaji = romaji_div.get_text(strip=True) if romaji_div else ""
                
                # Get English translation
                english_div = container.find('div', id=f'example_{example_num}_en')
                english = english_div.get_text(strip=True) if english_div else ""
                
                # Extract plain Japanese text
                japanese_text = jp_paragraph.get_text(strip=True) if jp_paragraph else ""
                
                example_data = {
                    'id': example_id,
                    'japanese_html': japanese_html,
                    'japanese_text': japanese_text,
                    'furigana': furigana,
                    'romaji': romaji,
                    'english': english,
                    'has_highlight': 'class="kanji-highlight"' in japanese_html or 'class="color"' in japanese_html
                }
                
                examples.append(example_data)
                
            except Exception as e:
                self.errors.append(f"Error parsing example: {str(e)}")
                continue
        
        return examples
    
    def scrape_all_kanji(self, max_kanji=500):
        """Main scraping function"""
        print("=" * 70)
        print("🚀 JLPT n4 COMPLETE SCRAPER - WORKING VERSION")
        print("=" * 70)
        
        start_time = time.time()
        
        try:
            # 1. Get all kanji URLs
            kanji_urls = self.get_all_kanji_urls()
            
            if not kanji_urls:
                print("❌ No kanji URLs found!")
                return False
            
            # Limit if needed
            if max_kanji and len(kanji_urls) > max_kanji:
                kanji_urls = kanji_urls[:max_kanji]
            
            print(f"\n📥 Scraping {len(kanji_urls)} kanji pages...")
            
            # 2. Scrape each kanji
            for idx, url in enumerate(kanji_urls, 1):
                print(f"\n[{idx}/{len(kanji_urls)}] Processing...")
                
                kanji_data = self.scrape_kanji_detail(url)
                if kanji_data:
                    kanji_data['id'] = idx
                    self.kanji_data.append(kanji_data)
                    
                    # Save progress every 5 kanji
                    if idx % 5 == 0:
                        self._save_progress()
                else:
                    print(f"    ⚠️ Could not scrape this page")
                
                # Rate limiting
                time.sleep(self.rate_limit)
            
            # 3. Save final results
            if self.kanji_data:
                self._save_final_results()
            else:
                print("\n❌ No data was scraped!")
                return False
            
            elapsed_time = time.time() - start_time
            
            # Calculate statistics
            total_kanji = len(self.kanji_data)
            total_onyomi = sum(len(k['readings']['onyomi']) for k in self.kanji_data)
            total_kunyomi = sum(len(k['readings']['kunyomi']) for k in self.kanji_data)
            total_special = sum(len(k['readings']['special']) for k in self.kanji_data)
            total_examples = sum(len(k['examples']) for k in self.kanji_data)
            rich_examples = sum(1 for k in self.kanji_data for ex in k['examples'] if ex.get('has_highlight'))
            
            print(f"\n🎉 SCRAPING COMPLETE!")
            print(f"⏱️  Time taken: {elapsed_time:.2f} seconds")
            print(f"📊 STATISTICS:")
            print(f"   • Kanji scraped: {total_kanji}")
            print(f"   • Onyomi readings: {total_onyomi}")
            print(f"   • Kunyomi readings: {total_kunyomi}")
            print(f"   • Special readings: {total_special}")
            print(f"   • Example sentences: {total_examples}")
            print(f"   • Rich text examples: {rich_examples}")
            
            # Show sample data from first kanji
            if self.kanji_data:
                first = self.kanji_data[0]
                print(f"\n📄 SAMPLE DATA for '{first['character']}':")
                print(f"   Meaning: {first['meaning']}")
                print(f"   Onyomi examples: {len(first['readings']['onyomi'])}")
                print(f"   Kunyomi examples: {len(first['readings']['kunyomi'])}")
                print(f"   Special examples: {len(first['readings']['special'])}")
                
                if first['readings']['onyomi']:
                    print(f"\n   First Onyomi example:")
                    print(f"      Word: {first['readings']['onyomi'][0]['word']}")
                    print(f"      Reading: {first['readings']['onyomi'][0]['reading']}")
                    print(f"      Meaning: {first['readings']['onyomi'][0]['meaning']}")
            
            if self.errors:
                print(f"\n⚠️  Errors encountered: {len(self.errors)}")
                with open('scraping_errors.log', 'w', encoding='utf-8') as f:
                    for error in self.errors:
                        f.write(f"{error}\n")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Scraping interrupted by user")
            self._save_progress()
            return False
            
        except Exception as e:
            print(f"\n❌ Critical error: {e}")
            import traceback
            traceback.print_exc()
            self._save_progress()
            return False
    
    def _save_progress(self):
        """Save progress to file"""
        if self.kanji_data:
            data = {
                'metadata': {
                    'scraped_at': datetime.now().isoformat(),
                    'progress': f"{len(self.kanji_data)} kanji",
                    'version': '1.0'
                },
                'kanji': self.kanji_data,
                'errors': self.errors[:10]
            }
            
            try:
                with open('scraping_progress.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("   💾 Progress saved")
            except Exception:
                pass
    
    def _save_final_results(self):
        """Save final results to JSON files"""
        # Create metadata
        metadata = {
            'scraped_at': datetime.now().isoformat(),
            'total_kanji': len(self.kanji_data),
            'version': 'final-2.0',
            'source': 'jlptsensei.com',
            'jlpt_level': 'n4',
            'features': [
                'kanji_characters',
                'meanings',
                'all_readings_extracted',
                'stroke_counts',
                'rich_text_examples',
                'html_styling',
                'furigana',
                'romaji',
                'english_translations'
            ]
        }
        
        # Prepare output
        output = {
            'metadata': metadata,
            'kanji': self.kanji_data
        }
        
        # 1. Save with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'jlpt_n4_complete_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Saved complete data to: {filename}")
        
        # 2. Save minified version
        with open('jlpt_n4_kanji.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, separators=(',', ':'))
        
        print(f"✅ Saved minified data to: jlpt_n4_kanji.json")
        
        # 3. Save statistics
        stats = {
            'total_kanji': len(self.kanji_data),
            'total_onyomi_readings': sum(len(k['readings']['onyomi']) for k in self.kanji_data),
            'total_kunyomi_readings': sum(len(k['readings']['kunyomi']) for k in self.kanji_data),
            'total_special_readings': sum(len(k['readings']['special']) for k in self.kanji_data),
            'total_examples': sum(len(k['examples']) for k in self.kanji_data),
            'kanji_with_stroke_count': sum(1 for k in self.kanji_data if k.get('stroke_count')),
            'kanji_with_stroke_diagram': sum(1 for k in self.kanji_data if k.get('stroke_diagram') or k.get('stroke_image')),
            'scraping_errors': len(self.errors)
        }
        
        with open('scraping_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   • Kanji: {stats['total_kanji']}")
        print(f"   • Onyomi readings: {stats['total_onyomi_readings']}")
        print(f"   • Kunyomi readings: {stats['total_kunyomi_readings']}")
        print(f"   • Special readings: {stats['total_special_readings']}")
        print(f"   • Example sentences: {stats['total_examples']}")
        
        # 4. Save CSS for styling
        self._save_css_file()

    def _save_css_file(self):
        """Save CSS file for styling"""
        css_content = """/* JLPT n4 Kanji Styling */
.kanji-highlight {
    color: #e74c3c;
    font-weight: bold;
    background-color: #fff3cd;
    padding: 2px 4px;
    border-radius: 3px;
}

.jp {
    font-family: "Hiragino Kaku Gothic Pro", "Meiryo", "MS PGothic", sans-serif;
    font-size: 1.2em;
    line-height: 1.6;
    margin: 10px 0;
}

.romaji {
    font-style: italic;
    color: #666;
    font-size: 0.9em;
}

.english {
    color: #2c3e50;
    font-size: 1em;
    margin-top: 5px;
}

.example-container {
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
    margin: 15px 0;
    background: linear-gradient(to right, #f8f9fa, #ffffff);
}

.reading-item {
    padding: 8px 12px;
    margin: 5px 0;
    border-left: 3px solid #3498db;
    background-color: #f8f9fa;
}

.word {
    font-weight: bold;
    color: #2c3e50;
}

.reading {
    color: #e74c3c;
    margin: 0 10px;
}

.meaning {
    color: #7f8c8d;
}
"""
        
        with open('kanji_styles.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ Saved CSS styles to: kanji_styles.css")

# Command line interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape JLPT n4 kanji with ALL readings and rich text')
    parser.add_argument('--rate-limit', type=float, default=1.5, help='Delay between requests (seconds)')
    parser.add_argument('--max-kanji', type=int, default=500, help='Maximum number of kanji to scrape')
    parser.add_argument('--test', action='store_true', help='Test mode (scrape only first 3 kanji)')
    
    args = parser.parse_args()
    
    if args.test:
        args.max_kanji = 3
        print("🧪 TEST MODE: Scraping first 3 kanji only")
    
    scraper = JLPTn4CompleteScraper(rate_limit=args.rate_limit)
    success = scraper.scrape_all_kanji(max_kanji=args.max_kanji)
    
    if success:
        print("\n✨ ALL DONE! Files created:")
        print("   1. jlpt_n4_complete_*.json - Complete data with timestamp")
        print("   2. jlpt_n4_kanji.json - Minified version")
        print("   3. kanji_styles.css - CSS for styling")
        print("   4. scraping_stats.json - Statistics")
        
        if scraper.kanji_data:
            # Verify readings are extracted
            print("\n✅ VERIFICATION:")
            for i, kanji in enumerate(scraper.kanji_data[:3], 1):
                print(f"   Kanji {i}: {kanji['character']}")
                print(f"      Onyomi: {len(kanji['readings']['onyomi'])} examples")
                print(f"      Kunyomi: {len(kanji['readings']['kunyomi'])} examples")
                print(f"      Special: {len(kanji['readings']['special'])} examples")
    
    sys.exit(0 if success else 1)