"""
JLPT VOCABULARY SELENIUM PERFECT SCRAPER - 100% ACCURACY MODE
- Pure Selenium (no Requests fallback)
- Robust waits for ALL content to load
- Extracts vocabulary table data + rich text examples
- Time is not an issue - focuses on accuracy
- Works for all JLPT levels (N1-N5)
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import json
import time
import re
import random
import os
from datetime import datetime
from urllib.parse import urljoin
import sys


class JLPTVocabSeleniumPerfectScraper:
    """Pure Selenium scraper for JLPT vocabulary with 100% data accuracy"""
    
    def __init__(self, level='n5', headless=False):
        """
        Initialize the vocabulary scraper
        
        Args:
            level (str): JLPT level (n1, n2, n3, n4, n5)
            headless (bool): Run browser in background
        """
        self.level = level.lower()
        self.base_url = f"https://jlptsensei.com/jlpt-{self.level}-vocabulary-list/"
        self.headless = headless
        
        # Data storage
        self.vocab_data = []
        self.errors = []
        self.skipped_urls = []
        self.scraped_urls = set()
        
        # Setup Selenium
        self.driver = None
        self.setup_selenium()
        
        # Create output file names
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.checkpoint_file = f'jlpt_{self.level}_vocab_checkpoint_{timestamp}.json'
        self.final_file = f'jlpt_{self.level}_vocab_perfect_{timestamp}.json'
        
        print(f"🎯 JLPT {self.level.upper()} Vocabulary Perfect Scraper Initialized")
        print(f"⏱️  Time is not an issue - focusing on 100% accuracy")
        print(f"📁 Checkpoint: {self.checkpoint_file}")
        print(f"📁 Final Output: {self.final_file}")
        
    def setup_selenium(self):
        """Setup Selenium WebDriver with maximum stability"""
        print("⚙️ Setting up Selenium WebDriver...")
        
        chrome_options = Options()
        
        # Anti-detection settings
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Performance and stability
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # Set large window size
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Headless mode if specified
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Apply stealth techniques
            stealth(self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(60)
            
            print("✅ Selenium WebDriver setup complete")
            
        except Exception as e:
            print(f"❌ Failed to setup Selenium: {e}")
            raise
            
    def human_delay(self, min_sec=3, max_sec=7):
        """Human-like delay with random variation"""
        delay = random.uniform(min_sec, max_sec)
        if random.random() < 0.2:
            delay += random.uniform(2, 5)
        time.sleep(delay)
        
    def comprehensive_scroll(self):
        """Comprehensive scrolling to trigger ALL lazy-loaded content"""
        try:
            print("      🔄 Scrolling to load all content...")
            
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            current_position = 0
            scroll_pause = 1.5
            
            # Scroll down in chunks
            while current_position < total_height:
                scroll_amount = random.randint(300, 600)
                current_position += scroll_amount
                
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(scroll_pause)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height > total_height:
                    total_height = new_height
                    
                if random.random() < 0.15:
                    scroll_back = random.randint(100, 200)
                    self.driver.execute_script(f"window.scrollBy(0, -{scroll_back});")
                    time.sleep(0.5)
            
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            print("      ✅ Scrolling complete")
            
        except Exception as e:
            print(f"      ⚠️ Scroll error (non-critical): {e}")
            
    def wait_for_element(self, by, value, timeout=20, description="element"):
        """Wait for element with descriptive error handling"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            print(f"      ✅ Found {description}")
            return element
        except TimeoutException:
            print(f"      ⚠️ Timeout waiting for {description}")
            return None
            
    def wait_for_any_element(self, selectors, timeout=20, description="any element"):
        """Wait for any of multiple selectors"""
        for by, value in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                print(f"      ✅ Found {description}: {value}")
                return element
            except TimeoutException:
                continue
        print(f"      ⚠️ None of the {description} selectors found")
        return None
        
    def get_all_vocab_urls(self):
        """Get all vocabulary detail URLs from list pages with table data"""
        print(f"🔍 Fetching vocabulary list for JLPT {self.level.upper()}...")
        all_vocab = []
        current_page_url = self.base_url
        page_num = 1
        
        while current_page_url:
            print(f"   📑 Scanning Page {page_num}...")
            
            try:
                # Load page
                self.driver.get(current_page_url)
                
                # Wait for table
                self.wait_for_element(By.TAG_NAME, "table", timeout=15, description="vocabulary table")
                
                # Wait a bit for dynamic content
                time.sleep(3)
                
                # Scroll to load all content
                self.comprehensive_scroll()
                
                # Get page source and parse
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Extract vocabulary from table
                page_vocab = self._extract_vocab_from_table(soup)
                
                all_vocab.extend(page_vocab)
                print(f"      ✅ Found {len(page_vocab)} vocabulary entries on this page")
                
                # Check for next page
                next_btn = soup.select_one('a.next.page-numbers')
                if next_btn and next_btn.get('href'):
                    current_page_url = next_btn['href']
                    page_num += 1
                    self.human_delay(2, 4)
                else:
                    current_page_url = None
                    
            except Exception as e:
                print(f"   ❌ Error scanning page {page_num}: {e}")
                break
        
        print(f"✅ Found TOTAL {len(all_vocab)} unique vocabulary entries")
        return all_vocab
        
    def _extract_vocab_from_table(self, soup):
        """Extract vocabulary data from table"""
        vocab_list = []
        
        # Find the main table
        table = soup.find('table')
        if not table:
            print("      ⚠️ No table found on page")
            return vocab_list
        
        # Get table headers to understand structure
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        
        # If no thead, try first tr
        if not headers:
            first_row = table.find('tr')
            if first_row:
                headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
        
        print(f"      🔍 Table headers: {headers}")
        
        # Process table rows
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            
            # Skip header rows
            if not cells or len(cells) < 3:
                continue
            
            # Skip if first cell is a header
            if cells[0].name == 'th':
                continue
            
            try:
                # Extract data based on table structure
                # Expected: #, ごい (Japanese), Vocabulary (English?), Type, Meaning
                
                vocab_entry = {}
                
                # Number/ID (column 0)
                vocab_entry['number'] = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                
                # Japanese vocabulary (column 1 - ごい)
                if len(cells) > 1:
                    jp_cell = cells[1]
                    # Try to find link
                    link = jp_cell.find('a', href=True)
                    if link:
                        vocab_entry['vocabulary_japanese'] = link.get_text(strip=True)
                        vocab_entry['detail_url'] = urljoin(self.base_url, link['href'])
                    else:
                        vocab_entry['vocabulary_japanese'] = jp_cell.get_text(strip=True)
                        vocab_entry['detail_url'] = None
                
                # English vocabulary (column 2 - Vocabulary)
                vocab_entry['vocabulary_english'] = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                
                # Type (column 3)
                vocab_entry['type'] = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                
                # Meaning (column 4)
                vocab_entry['meaning'] = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                
                # Only add if we have essential data
                if vocab_entry.get('vocabulary_japanese') and vocab_entry.get('detail_url'):
                    vocab_list.append(vocab_entry)
                    
            except Exception as e:
                print(f"      ⚠️ Error extracting row: {e}")
                continue
        
        return vocab_list
        
    def scrape_vocab_detail(self, vocab_entry):
        """
        Scrape vocabulary detail page for rich text examples
        """
        url = vocab_entry.get('detail_url')
        if not url:
            print(f"  ⚠️ No detail URL for {vocab_entry.get('vocabulary_japanese')}")
            return vocab_entry
        
        print(f"  📥 Processing: {vocab_entry.get('vocabulary_japanese')} ({url})")
        
        # Check if already scraped
        for vocab in self.vocab_data:
            if vocab.get('detail_url') == url:
                print("    ✅ Already scraped, skipping...")
                return vocab
        
        try:
            # Load page
            print("      🌐 Loading page with Selenium...")
            self.driver.get(url)
            
            # PHASE 1: Wait for basic structure
            print("      ⏳ Phase 1: Waiting for basic page structure...")
            self.wait_for_element(By.TAG_NAME, "h1", timeout=20, description="page title")
            self.wait_for_element(By.TAG_NAME, "article", timeout=20, description="main article")
            
            # PHASE 2: Wait for examples section
            print("      ⏳ Phase 2: Waiting for examples section...")
            time.sleep(3)
            
            examples_selectors = [
                (By.ID, "examples"),
                (By.CLASS_NAME, "example-cont"),
                (By.CLASS_NAME, "vocab-examples"),
                (By.XPATH, "//*[contains(@class, 'example')]"),
            ]
            self.wait_for_any_element(examples_selectors, timeout=15, description="examples section")
            
            # PHASE 3: Comprehensive scrolling
            print("      ⏳ Phase 3: Loading all lazy content...")
            self.comprehensive_scroll()
            
            # PHASE 4: Final wait
            print("      ⏳ Phase 4: Final content stabilization...")
            time.sleep(4)
            
            # Get final page source
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            print("      ✅ Page fully loaded, extracting examples...")
            
            # Extract examples
            examples = self._extract_rich_examples(soup, vocab_entry.get('vocabulary_japanese'))
            
            # Add examples to vocab entry
            vocab_entry['examples'] = examples
            vocab_entry['scraped_at'] = datetime.now().isoformat()
            vocab_entry['jlpt_level'] = self.level.upper()
            vocab_entry['has_examples'] = len(examples) > 0
            vocab_entry['data_quality'] = self._calculate_data_quality(vocab_entry)
            
            # Print summary
            print(f"    ✅ {vocab_entry.get('vocabulary_japanese')} - {vocab_entry.get('meaning')}")
            print(f"      🎨 Examples: {len(examples)}")
            print(f"      📊 Data Quality: {vocab_entry['data_quality']}/100")
            
            return vocab_entry
            
        except Exception as e:
            print(f"    ❌ Error extracting data from {url}: {e}")
            import traceback
            traceback.print_exc()
            self.errors.append(f"Extraction error ({url}): {e}")
            self.skipped_urls.append(url)
            return vocab_entry
    
    def _extract_rich_examples(self, soup, vocab_word):
        """Extract example sentences with rich HTML formatting"""
        examples = []
        
        # Find examples section
        examples_section = soup.find('div', id='examples')
        if not examples_section:
            examples_section = soup.find('div', class_=re.compile(r'example|vocab-example'))
        
        if not examples_section:
            print("      ⚠️ No examples section found")
            return examples
        
        # Find all example containers
        example_containers = examples_section.find_all('div', class_='example-cont')
        
        for container in example_containers:
            try:
                # Get example ID
                example_id = container.get('id', f'example_{len(examples)+1}')
                
                # Extract Japanese text with HTML styling
                jp_elem = container.select_one('.example-main p.jp')
                if not jp_elem:
                    jp_elem = container.select_one('p.jp')
                if not jp_elem:
                    jp_elem = container.find('p', class_=re.compile(r'jp|japanese'))
                
                if not jp_elem:
                    continue
                
                # Get Japanese text and HTML
                jp_text = jp_elem.get_text(strip=True)
                jp_html = str(jp_elem)
                
                # Extract furigana (Japanese kana)
                furigana_elem = container.find('div', id=re.compile(r'.*_ja$'))
                if not furigana_elem:
                    furigana_elem = container.select_one('.alert-success')
                furigana = furigana_elem.get_text(strip=True) if furigana_elem else ""
                
                # Extract romaji
                romaji_elem = container.find('div', id=re.compile(r'.*_romaji$'))
                if not romaji_elem:
                    romaji_elem = container.select_one('.alert-info')
                romaji = romaji_elem.get_text(strip=True) if romaji_elem else ""
                
                # Extract English translation
                en_elem = container.find('div', id=re.compile(r'.*_en$'))
                if not en_elem:
                    en_elem = container.select_one('.alert-primary')
                english = en_elem.get_text(strip=True) if en_elem else ""
                
                # Check if contains vocab word
                has_vocab = vocab_word in jp_text if vocab_word else False
                
                # Check if has HTML styling
                has_html_styling = bool(jp_elem.find(['span', 'strong', 'em', 'b', 'i']))
                
                example_data = {
                    'id': example_id,
                    'japanese_text': jp_text,
                    'japanese_html': jp_html,
                    'furigana': furigana,
                    'romaji': romaji,
                    'english': english,
                    'has_vocab_word': has_vocab,
                    'has_html_styling': has_html_styling
                }
                
                examples.append(example_data)
                
            except Exception as e:
                print(f"      ⚠️ Error extracting example: {e}")
                continue
        
        return examples
    
    def _calculate_data_quality(self, vocab_entry):
        """Calculate data quality score (0-100)"""
        score = 0
        
        # Japanese vocabulary (20 points)
        if vocab_entry.get('vocabulary_japanese'):
            score += 20
        
        # Meaning (20 points)
        if vocab_entry.get('meaning'):
            score += 20
        
        # Type (10 points)
        if vocab_entry.get('type'):
            score += 10
        
        # Detail URL (10 points)
        if vocab_entry.get('detail_url'):
            score += 10
        
        # Examples (40 points)
        examples = vocab_entry.get('examples', [])
        if len(examples) > 0:
            score += 20
        if len(examples) >= 3:
            score += 10
        if any(ex.get('has_html_styling') for ex in examples):
            score += 10
        
        return min(score, 100)

    def _extract_rich_examples(self, soup, vocab_word):
        """
        Extract example sentences with high-fidelity styling
        Targets 'example-main' and handles collapse divs
        """
        examples = []
        
        # Find examples section
        examples_section = soup.find('div', id='examples')
        if not examples_section:
            examples_section = soup.find('div', class_=re.compile(r'example|vocab-example|example-container'))
        
        if not examples_section:
            return examples

        # Find all example containers
        example_containers = examples_section.select('.example-main, .example-cont, div[class*="example-cont"]')
        
        for container in example_containers:
            try:
                # 1. Get Japanese HTML (Preserving styles)
                jp_elem = container.select_one('.example-ja, p.jp, .japanese-text')
                if not jp_elem:
                    jp_elem = container.find('p')
                
                if not jp_elem: continue

                # Clean the HTML but keep essential tags
                raw_html = str(jp_elem)
                clean_soup = BeautifulSoup(raw_html, 'html.parser')
                
                # Remove unwanted tags
                for tag in clean_soup.find_all(['script', 'style', 'ins', 'iframe', 'button', 'a']):
                    tag.decompose()
                
                # Preserve only color/style classes (Blueprint requirement)
                for tag in clean_soup.find_all(True):
                    classes = tag.get('class', [])
                    if isinstance(classes, str): classes = [classes]
                    
                    # Keep style-related attributes like "color", "bold", etc.
                    keep_classes = [c for c in classes if any(s in c.lower() for s in ['color', 'bold', 'underline', 'red', 'blue'])]
                    if keep_classes:
                        tag['class'] = keep_classes
                    else:
                        del tag['class']
                
                japanese_html = str(clean_soup)
                japanese_text = clean_soup.get_text(strip=True)
                
                # 2. Extract English Translation
                en_elem = container.select_one('.example-en, p.en, .english-text, [id$="_en"], [id*="-en"]')
                english = en_elem.get_text(strip=True) if en_elem else ""

                # 3. Extract Furigana/Reading
                furigana = ""
                ruby_tags = clean_soup.find_all('ruby')
                if ruby_tags:
                    furigana = "".join([rt.get_text() for rt in clean_soup.find_all('rt')])
                else:
                    reading_elem = container.select_one('.reading, .furigana, [id$="_ja"], [id*="-ja"]')
                    if reading_elem:
                        furigana = reading_elem.get_text(strip=True)

                # 4. Romaji
                romaji_elem = container.select_one('.romaji, [id$="_romaji"]')
                romaji = romaji_elem.get_text(strip=True) if romaji_elem else ""

                if any(ex['japanese_text'] == japanese_text for ex in examples):
                    continue

                examples.append({
                    'id': f"ex_{len(examples)+1}",
                    'japanese_html': japanese_html,
                    'japanese_text': japanese_text,
                    'english': english,
                    'furigana': furigana,
                    'romaji': romaji,
                    'has_html_styling': '<span' in japanese_html or 'class=' in japanese_html,
                    'has_vocab_word': vocab_word in japanese_text if vocab_word else False
                })
                
            except Exception as e:
                print(f"      ⚠️ Error parsing example: {e}")
                continue
                
        return examples

    def perform_integrity_check(self):
        """
        Verify that every vocabulary entry has its required data.
        Automatic Testing Requirement.
        """
        print(f"\n🔍 PERFORMING INTEGRITY CHECK...")
        missing_examples = []
        low_quality = []
        total = len(self.vocab_data)
        
        for v in self.vocab_data:
            if not v.get('examples') or len(v.get('examples')) == 0:
                missing_examples.append(v['vocabulary_japanese'])
            if v.get('data_quality', 0) < 70:
                low_quality.append(v['vocabulary_japanese'])
                
        print(f"   ✅ Total Vocabulary: {total}")
        print(f"   ⚠️  Missing Examples: {len(missing_examples)} ({', '.join(missing_examples[:10])}{'...' if len(missing_examples) > 10 else ''})")
        print(f"   ⚠️  Low Quality (<70): {len(low_quality)} ({', '.join(low_quality[:10])}{'...' if len(low_quality) > 10 else ''})")
        
        return {
            'total': total,
            'missing_examples': missing_examples,
            'low_quality': low_quality,
            'passed': len(missing_examples) == 0
        }

    def save_final_results(self):
        """Save final results to Master JSON and Web App"""
        if not self.vocab_data:
            print("❌ No data to save!")
            return
            
        final_data = {
            'metadata': {
                'jlpt_level': self.level.upper(),
                'total_vocabulary': len(self.vocab_data),
                'scraped_at': datetime.now().isoformat(),
                'version': '3.0-selenium-perfect-master',
                'source': 'jlptsensei.com',
                'features': ['vocabulary', 'readings', 'meanings', 'types', 'rich_examples', 'furigana', 'romaji']
            },
            'vocabulary': self.vocab_data,
            'scraping_info': {
                'errors': self.errors,
                'total_scraped': len(self.scraped_urls)
            }
        }
        
        # Save to scrapers directory
        with open(self.final_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Final results saved to: {self.final_file}")
        
        # Save to web_app directory (Mandatory for the app)
        web_app_file = os.path.join(os.path.dirname(__file__), '..', 'web_app', 'jlpt_n5_complete.json')
        try:
            with open(web_app_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)
            print(f"� Successfully deployed data to: {web_app_file}")
        except Exception as e:
            print(f"❌ Error deploying to web_app: {e}")

    def run(self, max_vocab=None, resume=True):
        """Main execution loop"""
        start_time = time.time()
        
        if resume: self.load_checkpoint()
        
        # 1. Discovery
        all_vocab = self.get_all_vocab_urls()
        if not all_vocab: return False
        
        # 2. Filter
        remaining = [v for v in all_vocab if v.get('detail_url') not in self.scraped_urls]
        if max_vocab: remaining = remaining[:max_vocab]
        
        print(f"\n📥 Starting to scrape {len(remaining)} vocabulary details...\n")
        
        # 3. Scrape Details
        for idx, entry in enumerate(remaining, 1):
            data = self.scrape_vocab_detail(entry)
            if data:
                self.vocab_data.append(data)
                self.scraped_urls.add(data['detail_url'])
                
            if idx % 5 == 0: self.save_checkpoint()
            
            # Delay to avoid blocking
            if idx < len(remaining):
                self.human_delay(3, 6)
                
        # 4. Finalize
        self.perform_integrity_check()
        self.save_final_results()
        self.cleanup()
        
        print(f"\n✨ Scraper execution finished in {time.time() - start_time:.1f}s")
        return True

    def cleanup(self):
        """Quit driver and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Selenium closed")
            except: pass
        if os.path.exists(self.checkpoint_file): os.remove(self.checkpoint_file)

    def save_checkpoint(self):
        """Save progress to JSON"""
        data = {'vocab_data': self.vocab_data, 'scraped_urls': list(self.scraped_urls)}
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_checkpoint(self):
        """Load progress from JSON"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.vocab_data = data.get('vocab_data', [])
                    self.scraped_urls = set(data.get('scraped_urls', []))
                    print(f"📂 Resuming from checkpoint: {len(self.vocab_data)} items")
            except: pass

if __name__ == '__main__':
    # Simple CLI
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', default='n5')
    parser.add_argument('--max', type=int, default=None)
    parser.add_argument('--headless', action='store_true', default=True)
    args = parser.parse_args()
    
    scraper = JLPTVocabSeleniumPerfectScraper(level=args.level, headless=args.headless)
    scraper.run(max_vocab=args.max)
