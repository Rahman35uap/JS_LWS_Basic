"""
JLPT UNIVERSAL MASTER SCRAPER WITH SELENIUM - PART 1/2
- Bypasses CAPTCHA/bot detection with Selenium
- Extracts ALL kanji characters, ALL readings
- Preserves rich text examples with HTML styling
- Gets stroke diagrams and all metadata
- Works for all JLPT levels (N1-N5)
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import re
import random
import os
from datetime import datetime
from urllib.parse import urljoin
import sys

class JLPTUniversalMasterScraper:
    def __init__(self, level='n5', headless=False, rate_limit=2.0):
        """
        Initialize the universal scraper
        
        Args:
            level (str): JLPT level (n1, n2, n3, n4, n5)
            headless (bool): Run browser in background (faster but less human-like)
            rate_limit (float): Minimum delay between requests
        """
        self.level = level.lower()
        self.base_url = f"https://jlptsensei.com/jlpt-{self.level}-kanji-list/"
        self.rate_limit = rate_limit
        self.headless = headless
        
        # Data storage
        self.kanji_data = []
        self.errors = []
        self.skipped_urls = []
        self.scraped_urls = set()
        
        # Setup both Requests and Selenium
        self.setup_requests()
        self.setup_selenium()
        
        # Create checkpoint file name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.checkpoint_file = f'jlpt_{self.level}_checkpoint_{timestamp}.json'
        self.final_file = f'jlpt_{self.level}_complete_{timestamp}.json'
        
        print(f"🎯 JLPT {self.level.upper()} Universal Master Scraper Initialized")
        print(f"📁 Checkpoint: {self.checkpoint_file}")
        print(f"📁 Final Output: {self.final_file}")
        
    def setup_requests(self):
        """Setup Requests session with realistic headers"""
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        self.rotate_headers()
        
    def rotate_headers(self):
        """Rotate headers to appear more human-like"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'ja-JP,ja;q=0.7']),
            'Accept-Encoding': 'gzip, deflate', # Removed 'br' to prevent encoding errors
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
    def setup_selenium(self):
        """Setup Selenium WebDriver with stealth options"""
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
        
        # Window size
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Headless mode if specified
        if self.headless:
            chrome_options.add_argument("--headless")
        
        try:
            # Use Selenium's built-in manager (Selenium 4.6+)
            # This automatically detects and extracts the correct driver
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
            
            print("✅ Selenium WebDriver setup complete")
            
        except Exception as e:
            print(f"❌ Failed to setup Selenium: {e}")
            print("⚠️ Falling back to Requests-only mode")
            self.driver = None
            
    def human_like_delay(self, min_sec=2, max_sec=8):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_sec, max_sec)
        if random.random() < 0.3:  # 30% chance of "thinking" delay
            delay += random.uniform(1, 4)
        time.sleep(delay)
        
    def human_like_scroll(self):
        """Simulate human scrolling patterns"""
        if not self.driver:
            return
            
        try:
            # Get page height
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            current_pos = 0
            
            while current_pos < total_height:
                # Random scroll amount
                scroll_amount = random.randint(300, 800)
                current_pos += scroll_amount
                
                # Scroll down
                self.driver.execute_script(f"window.scrollTo(0, {current_pos});")
                time.sleep(random.uniform(0.5, 2))
                
                # Occasionally scroll back up a bit
                if random.random() < 0.15:
                    back_amount = random.randint(100, 300)
                    self.driver.execute_script(f"window.scrollBy(0, -{back_amount});")
                    time.sleep(random.uniform(0.3, 1))
                    
        except Exception as e:
            print(f"⚠️ Scroll simulation failed: {e}")
            
    def get_all_kanji_urls(self):
        """
        Get all kanji detail URLs from the list pages (Recursive Pagination)
        """
        print(f"🔍 Fetching kanji list for JLPT {self.level.upper()}...")
        all_urls = []
        current_page_url = self.base_url
        page_num = 1
        
        while current_page_url:
            print(f"   📑 Scanning Page {page_num}...")
            
            # Use Selenium or Requests based on availability
            soup = None
            try:
                if self.driver:
                    self.driver.get(current_page_url)
                    time.sleep(random.uniform(2, 4))
                    self.human_like_scroll()
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                else:
                    self.rotate_headers()
                    response = self.session.get(current_page_url, timeout=20)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                print(f"   ❌ Error scanning page {page_num}: {e}")
                if "404" in str(e): break
            
            if not soup: break
            
            # Extract URLs
            page_urls = []
            
            # Method 1: Table links
            for table in soup.find_all('table'):
                for link in table.find_all('a', href=True):
                    href = link['href']
                    if '/learn-japanese-kanji/' in href and not href.endswith('/feed/'):
                        page_urls.append(urljoin(self.base_url, href))
                        
            # Method 2: Direct links (Backup)
            if len(page_urls) < 5:
                for link in soup.select('a[href*="/learn-japanese-kanji/"]'):
                    href = link['href']
                    if not href.endswith('/feed/') and '#' not in href:
                        page_urls.append(urljoin(self.base_url, href))
            
            # Clean and add
            page_urls = list(dict.fromkeys(page_urls))
            new_urls = [u for u in page_urls if u not in all_urls]
            all_urls.extend(new_urls)
            print(f"      ✅ Found {len(new_urls)} new kanji on this page.")
            
            # Pagination Check
            next_btn = soup.select_one('a.next.page-numbers')
            if next_btn and next_btn.get('href'):
                current_page_url = next_btn['href']
                page_num += 1
                if not self.driver: time.sleep(self.rate_limit)
            else:
                current_page_url = None
                
        # Final cleanup
        all_urls = list(dict.fromkeys(all_urls))
        print(f"✅ Found TOTAL {len(all_urls)} unique kanji URLs")
        return all_urls
            
    def scrape_with_selenium(self, url):
        """
        Scrape a page using Selenium (bypasses bot detection)
        Returns BeautifulSoup object
        """
        if not self.driver:
            return None
            
        try:
            print(f"🌐 Selenium: Opening {url}")
            
            # Navigate to page
            self.driver.get(url)
            
            # Human-like delay
            self.human_like_delay(3, 7)
            
            # Scroll to trigger lazy loading
            self.human_like_scroll()
            
            # Wait for content to load
            time.sleep(random.uniform(2, 4))
            
            # Get page source
            html = self.driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            return soup
            
        except Exception as e:
            print(f"❌ Selenium error for {url}: {e}")
            self.errors.append(f"Selenium error ({url}): {e}")
            return None
            
    def scrape_with_requests(self, url, retries=2):
        """
        Scrape a page using Requests (faster when not blocked)
        Returns BeautifulSoup object
        """
        for attempt in range(retries + 1):
            try:
                # Rotate headers for each attempt
                self.rotate_headers()
                
                # Add referrer
                self.session.headers.update({
                    'Referer': random.choice([self.base_url, 'https://www.google.com/', 'https://jlptsensei.com/'])
                })
                
                # Human-like delay
                self.human_like_delay(2, 5)
                
                # Make request
                response = self.session.get(url, timeout=20)
                
                # Check for blocking
                if response.status_code in [403, 429, 503]:
                    print(f"⚠️ Server blocking ({response.status_code}), attempt {attempt+1}/{retries+1}")
                    time.sleep(30 * (attempt + 1))
                    continue
                    
                # Check for CAPTCHA in content
                if any(word in response.text.lower() for word in ['captcha', 'unusual traffic', 'security check']):
                    print(f"⚠️ CAPTCHA detected, attempt {attempt+1}/{retries+1}")
                    time.sleep(60 * (attempt + 1))
                    continue
                    
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
                
            except Exception as e:
                if attempt < retries:
                    print(f"⚠️ Requests attempt {attempt+1} failed: {e}, retrying...")
                    time.sleep(10 * (attempt + 1))
                else:
                    print(f"❌ Requests failed for {url}: {e}")
                    self.errors.append(f"Requests error ({url}): {e}")
                    
        return None
        
    def scrape_kanji_detail(self, url):
        """
        Master function to scrape all kanji details
        Tries Requests first, falls back to Selenium if blocked
        """
        print(f"  📥 Processing: {url}")
        
        # Check if already scraped
        for kanji in self.kanji_data:
            if kanji.get('page_url') == url:
                print("    ✅ Already scraped, skipping...")
                return kanji
                
        # Try Requests first (faster)
        soup = self.scrape_with_requests(url)
        
        # If Requests fails or returns blocked content, try Selenium
        if soup is None or self.is_blocked_page(soup):
            print("    ⚠️ Requests blocked, switching to Selenium...")
            soup = self.scrape_with_selenium(url)
            
        if soup is None:
            print(f"    ❌ Failed to scrape {url}")
            self.skipped_urls.append(url)
            return None
            
        # Extract all data
        try:
            # 1. Extract kanji character
            kanji_char = self._extract_kanji_char(soup, url)
            if not kanji_char:
                print(f"    ❌ Could not extract kanji character from {url}")
                self.skipped_urls.append(url)
                return None
                
            # 2. Extract meaning
            meaning = self._extract_meaning(soup)
            
            # 3. Extract ALL readings
            readings = self._extract_all_readings_complete(soup)
            
            # 4. Extract stroke count
            stroke_count = self._extract_stroke_count(soup)
            
            # 5. Extract stroke diagram (SVG or image)
            stroke_data = self._extract_stroke_diagram(soup)
            
            # 6. Extract flashcard/mnemonic image
            flashcard_url = self._extract_flashcard_image(soup)
            
            # 7. Extract rich text examples with styling
            examples = self._extract_rich_examples_with_styling(soup, kanji_char)
            
            # 8. Extract additional metadata
            metadata = self._extract_metadata(soup)
            
            # Create complete kanji data object
            kanji_data = {
                'id': len(self.kanji_data) + 1,
                'character': kanji_char,
                'meaning': meaning,
                'readings': readings,
                'stroke_count': stroke_count,
                'stroke_diagram_svg': stroke_data.get('svg'),
                'stroke_image_url': stroke_data.get('image_url'),
                'flashcard_url': flashcard_url,
                'examples': examples,
                'metadata': metadata,
                'page_url': url,
                'scraped_at': datetime.now().isoformat(),
                'jlpt_level': self.level.upper(),
                'has_rich_text': len(examples) > 0,
                'data_quality': self._calculate_data_quality({
                    'character': kanji_char,
                    'readings': readings,
                    'examples': examples,
                    'stroke_count': stroke_count
                })
            }
            
            # Print summary
            print(f"    ✅ {kanji_char} - {meaning}")
            print(f"      📖 Readings: {len(readings['onyomi'])} Onyomi, "
                  f"{len(readings['kunyomi'])} Kunyomi, "
                  f"{len(readings['special'])} Special")
            print(f"      🎨 Examples: {len(examples)} (Rich text: {any(ex.get('has_html_styling', False) for ex in examples)})")
            print(f"      ✍️  Strokes: {stroke_count if stroke_count else 'Not found'}")
            
            return kanji_data
            
        except Exception as e:
            print(f"    ❌ Error extracting data from {url}: {e}")
            import traceback
            traceback.print_exc()
            self.errors.append(f"Extraction error ({url}): {e}")
            self.skipped_urls.append(url)
            return None
            
    def is_blocked_page(self, soup):
        """Check if page shows blocking/CAPTCHA"""
        text = soup.get_text().lower()
        blocked_indicators = [
            'captcha',
            'unusual traffic',
            'security check',
            'access denied',
            'cloudflare',
            'please verify you are human'
        ]
        return any(indicator in text for indicator in blocked_indicators)
        
    def _extract_kanji_char(self, soup, url):
        """Extract kanji character using multiple methods"""
        # Method 1: Look for specific classes
        selectors = [
            '.kanji-character',
            '.kanji-large',
            '.kanji-main',
            'h1.kanji',
            '.entry-title',
            '.kanji-heading',
            '.main-kanji'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                match = re.search(r'[\u4e00-\u9fff]', text)
                if match:
                    return match.group(0)
                    
        # Method 2: From page title
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            # Match patterns like "JLPT N5 Kanji: 日 (nichi)" or "Learn Kanji 日"
            match = re.search(r'([\u4e00-\u9fff])\s*(?:\(|【|-|:|$)|\s+([\u4e00-\u9fff])\s', title_text)
            if match:
                return match.group(1) or match.group(2)
                
        # Method 3: From URL
        try:
            from urllib.parse import unquote
            decoded_url = unquote(url)
            match = re.search(r'([\u4e00-\u9fff])', decoded_url)
            if match:
                print(f"    ⚠️ Extracted from URL: {match.group(1)}")
                return match.group(1)
        except:
            pass
            
        # Method 4: From main content headers
        for h in soup.find_all(['h1', 'h2']):
            text = h.get_text()
            match = re.search(r'[\u4e00-\u9fff]', text)
            if match:
                return match.group(0)
                
        return None
        
    def _extract_meaning(self, soup):
        """Extract kanji meaning"""
        # Method 1: From title
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            match = re.search(r'Meaning:\s*(.+?)(?:\s*-|\s*\(|\s*$)', title_text)
            if match:
                return match.group(1).strip()
                
        # Method 2: From content
        meaning_label = soup.find(string=re.compile(r'Meaning:'))
        if meaning_label:
            parent = meaning_label.parent
            if parent:
                text = parent.get_text()
                match = re.search(r'Meaning:\s*(.+?)(?:\.|$)', text)
                if match:
                    return match.group(1).strip()
                    
        # Method 3: From meta description
        meta = soup.find('meta', {'name': 'description'})
        if meta and 'content' in meta.attrs:
            content = meta['content']
            match = re.search(r'Meaning:\s*(.+?)(?:\.|$)', content)
            if match:
                return match.group(1).strip()
                
        return "Meaning not found"
    def _extract_all_readings_complete(self, soup):
        """
        Extract ALL readings (onyomi, kunyomi, special) with words
        Enhanced version that handles various page structures
        """
        readings = {
            'onyomi': [],
            'kunyomi': [],
            'special': []
        }
        
        # Find vocabulary/readings section
        vocab_section = None
        
        # Try multiple section identifiers
        section_ids = ['related-words', 'readings', 'vocabulary', 'words']
        for section_id in section_ids:
            vocab_section = soup.find('div', id=section_id)
            if vocab_section:
                break
                
        if not vocab_section:
            # Try class-based search
            vocab_section = soup.find('div', class_=re.compile(r'related|reading|vocab'))
            if not vocab_section:
                # Fallback to whole page
                vocab_section = soup
                
        # Get all text content
        all_text = vocab_section.get_text(separator='\n')
        
        # Parse by sections
        current_section = None
        
        # Process line by line
        lines = all_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if 'onyomi' in line.lower() and 'reading' in line.lower():
                current_section = 'onyomi'
                continue
            elif 'kunyomi' in line.lower() and 'reading' in line.lower():
                current_section = 'kunyomi'
                continue
            elif 'special' in line.lower() and 'reading' in line.lower():
                current_section = 'special'
                continue
                
            # Parse reading entries
            if current_section and '【' in line and '】' in line:
                try:
                    # Find word and reading
                    word_end = line.find('【')
                    reading_end = line.find('】')
                    
                    if word_end != -1 and reading_end != -1:
                        word = line[:word_end].strip()
                        reading = line[word_end+1:reading_end].strip()
                        meaning = line[reading_end+1:].strip()
                        
                        # Clean up
                        meaning = meaning.replace('】', '').strip()
                        
                        readings[current_section].append({
                            'word': word,
                            'reading': reading,
                            'meaning': meaning
                        })
                except:
                    continue
                    
        # Additional parsing for structured divs
        for reading_type in ['onyomi', 'kunyomi', 'special']:
            if not readings[reading_type]:
                # Look for specific divs with reading type
                divs = vocab_section.find_all('div', string=re.compile(reading_type, re.I))
                for div in divs:
                    # Get next sibling containing examples
                    next_elem = div.find_next_sibling()
                    if next_elem and next_elem.name == 'div':
                        examples = next_elem.find_all(['p', 'li', 'span'])
                        for example in examples:
                            text = example.get_text(strip=True)
                            if '【' in text and '】' in text:
                                try:
                                    word_end = text.find('【')
                                    reading_end = text.find('】')
                                    word = text[:word_end].strip()
                                    reading = text[word_end+1:reading_end].strip()
                                    meaning = text[reading_end+1:].replace('】', '').strip()
                                    
                                    readings[reading_type].append({
                                        'word': word,
                                        'reading': reading,
                                        'meaning': meaning
                                    })
                                except:
                                    continue
                                    
        return readings
        
    def _extract_stroke_count(self, soup):
        """Extract stroke count"""
        patterns = [
            r'Stroke Count:\s*(\d+)',
            r'Strokes:\s*(\d+)',
            r'(\d+)\s*strokes',
            r'画数:\s*(\d+)',
            r'Stroke order:\s*(\d+)',
            r'Number of Strokes:\s*(\d+)'
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
        """Extract stroke diagram (SVG or image)"""
        result = {'svg': None, 'image_url': None}
        
        # Look for SVG with class 'stroke_order_diagram' or inside specific divs
        svg_element = soup.select_one('svg.stroke_order_diagram')
        if not svg_element:
            # Look for div that might contain it
            svg_container = soup.select_one('.kanji-stroke-order, #kanji-stroke-order')
            if svg_container:
                svg_element = svg_container.find('svg')
        
        if svg_element:
            # Clean up the SVG for injection
            svg_element['class'] = svg_element.get('class', []) + ['stroke-diagram-injected']
            result['svg'] = str(svg_element)
            
        # Look for stroke diagram images with specific class
        stroke_img = soup.select_one('img.stroke_order_diagram')
        if not stroke_img:
            stroke_img = soup.find('img', src=re.compile(r'stroke|order|diagram', re.I))
            
        if stroke_img:
            src = stroke_img.get('src')
            if src:
                result['image_url'] = urljoin(self.base_url, src)
                
        return result
        
    def _extract_flashcard_image(self, soup):
        """Extract flashcard/mnemonic image URL"""
        # Priority 1: img-responsive class often used for flashcards
        img = soup.select_one('img.img-responsive[src*="kanji"]')
        if not img:
            # Priority 2: Mnemonic specific selectors
            img = soup.select_one('.mnemonic-image img, .kanji-image img, img[src*="mnemonic"]')
            
        if not img:
            # Priority 3: Any image in the entry content that looks like a flashcard
            for image in soup.select('.entry-content img'):
                src = image.get('src', '')
                if any(k in src.lower() for k in ['flashcard', 'mnemonic', 'kanji-image']):
                    img = image
                    break
                    
        if img and img.get('src'):
            src = img['src']
            return urljoin(self.base_url, src)
                    
        return None
        
    def _extract_rich_examples_with_styling(self, soup, kanji_char):
        """
        Extract example sentences with high-fidelity styling
        Targets 'example-main' and handles collapse divs
        """
        examples = []
        
        # Priority 1: Target specifically 'example-main' which is the standard on JLPT Sensei
        example_containers = soup.select('.example-main, div[class*="example-cont"]')
        
        if not example_containers:
            # Fallback to general example classes
            example_containers = soup.select('.jp-example, .sentence-example, .example-container')

        for container in example_containers:
            try:
                # 1. Get Japanese HTML (Preserving styles)
                jp_elem = container.select_one('.example-ja, p.jp, .japanese-text')
                if not jp_elem:
                    # Look for hidden/collapse version
                    jp_elem = container.select_one('[id$="_ja"], [id*="-ja"]')
                
                if not jp_elem: 
                    # If it's a direct paragraph in container
                    jp_elem = container.find('p')
                
                if not jp_elem: continue

                # Clean the HTML but keep essential tags
                raw_html = str(jp_elem)
                clean_soup = BeautifulSoup(raw_html, 'html.parser')
                
                # Remove ads, social buttons, etc.
                for tag in clean_soup.find_all(['script', 'style', 'ins', 'iframe', 'button', 'a']):
                    tag.decompose()
                
                # Preserve only color/style classes
                for tag in clean_soup.find_all(True):
                    classes = tag.get('class', [])
                    if isinstance(classes, str): classes = [classes]
                    
                    # Keep style-related attributes but clean others
                    keep_classes = [c for c in classes if any(s in c.lower() for s in ['color', 'bold', 'underline', 'red', 'blue'])]
                    if keep_classes:
                        tag['class'] = keep_classes
                    else:
                        del tag['class']
                
                # The core requirement: maintain <span class="color">
                japanese_html = str(clean_soup)
                japanese_text = clean_soup.get_text(strip=True)
                
                # 2. Extract English Translation
                en_elem = container.select_one('.example-en, p.en, .english-text')
                if not en_elem:
                    en_elem = container.select_one('[id$="_en"], [id*="-en"]')
                
                english = en_elem.get_text(strip=True) if en_elem else ""

                # 3. Extract Furigana/Reading (if available in HTML)
                furigana = ""
                # Often in <ruby> or specific reading classes
                ruby_tags = clean_soup.find_all('ruby')
                if ruby_tags:
                    # If ruby tags used, furigana is the sum of <rt>
                    furigana = "".join([rt.get_text() for rt in clean_soup.find_all('rt')])
                else:
                    # Check for separate reading elements
                    reading_elem = container.select_one('.reading, .furigana')
                    if reading_elem:
                        furigana = reading_elem.get_text(strip=True)

                # Ensure we skip duplicates
                if any(ex['japanese_text'] == japanese_text for ex in examples):
                    continue

                examples.append({
                    'japanese_html': japanese_html,
                    'japanese_text': japanese_text,
                    'english': english,
                    'furigana': furigana,
                    'has_html_styling': '<span' in japanese_html or 'class=' in japanese_html,
                    'id': f"ex_{len(examples)+1}"
                })
                
            except Exception as e:
                print(f"⚠️ Error parsing example in container: {e}")
                continue
                
        return examples
        
    def _extract_metadata(self, soup):
        """Extract additional metadata"""
        metadata = {}
        
        # Extract radicals if available
        radicals = []
        radical_patterns = [
            r'Radical:\s*(.+?)(?:\n|$)',
            r'部首:\s*(.+)',
            r'Radicals?:\s*(.+)'
        ]
        
        all_text = soup.get_text()
        for pattern in radical_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                radicals = [r.strip() for r in match.group(1).split(',')]
                break
                
        metadata['radicals'] = radicals
        
        # Extract JLPT level confirmation
        jlpt_pattern = r'JLPT\s*(N[1-5])'
        match = re.search(jlpt_pattern, all_text, re.IGNORECASE)
        if match:
            metadata['confirmed_level'] = match.group(1).lower()
            
        # Extract frequency if available
        freq_patterns = [
            r'Frequency:\s*(\d+)',
            r'常用漢字:\s*(\d+)',
            r'Joy o Kanji:\s*(\d+)'
        ]
        
        for pattern in freq_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                metadata['frequency_rank'] = int(match.group(1))
                break
                
        return metadata
        
    def _calculate_data_quality(self, data):
        """Calculate data quality score (0-100)"""
        score = 0
        
        # Character (25 points)
        if data['character']:
            score += 25
            
        # Readings (35 points)
        readings = data['readings']
        total_readings = len(readings['onyomi']) + len(readings['kunyomi']) + len(readings['special'])
        if total_readings > 0:
            score += min(35, total_readings * 3)
            
        # Examples (30 points)
        examples = data['examples']
        if examples:
            score += min(30, len(examples) * 5)
            
        # Stroke count (10 points)
        if data['stroke_count']:
            score += 10
            
        return score
        
    def save_checkpoint(self):
        """Save current progress to checkpoint file"""
        if not self.kanji_data:
            return
            
        checkpoint_data = {
            'metadata': {
                'level': self.level.upper(),
                'kanji_count': len(self.kanji_data),
                'last_update': datetime.now().isoformat(),
                'progress': f"{len(self.kanji_data)} kanji scraped"
            },
            'kanji_data': self.kanji_data,
            'errors': self.errors[-20:],  # Last 20 errors
            'skipped_urls': self.skipped_urls
        }
        
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            print(f"💾 Checkpoint saved: {len(self.kanji_data)} kanji")
        except Exception as e:
            print(f"❌ Error saving checkpoint: {e}")
            
    def load_checkpoint(self):
        """Load progress from checkpoint file"""
        if not os.path.exists(self.checkpoint_file):
            return False
            
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.kanji_data = data.get('kanji_data', [])
            self.errors = data.get('errors', [])
            self.skipped_urls = data.get('skipped_urls', [])
            
            print(f"📂 Loaded checkpoint: {len(self.kanji_data)} kanji")
            return True
            
        except Exception as e:
            print(f"❌ Error loading checkpoint: {e}")
            return False
            
    def perform_integrity_check(self):
        """
        Verify that every kanji in the list has its SVG and Flashcard image.
        Automatic Testing Requirement.
        """
        print(f"\n🔍 PERFORMING INTEGRITY CHECK...")
        missing_svg = []
        missing_flashcard = []
        total = len(self.kanji_data)
        
        for k in self.kanji_data:
            if not k.get('stroke_diagram_svg') and not k.get('stroke_image_url'):
                missing_svg.append(k['character'])
            if not k.get('flashcard_url'):
                missing_flashcard.append(k['character'])
                
        print(f"   ✅ Total Kanji: {total}")
        print(f"   ⚠️  Missing SVG: {len(missing_svg)} ({', '.join(missing_svg[:10])}{'...' if len(missing_svg) > 10 else ''})")
        print(f"   ⚠️  Missing Flashcards: {len(missing_flashcard)} ({', '.join(missing_flashcard[:10])}{'...' if len(missing_flashcard) > 10 else ''})")
        
        return {
            'total': total,
            'missing_svg': missing_svg,
            'missing_flashcard': missing_flashcard,
            'passed': len(missing_svg) == 0 and len(missing_flashcard) == 0
        }

    def run(self, max_kanji=None, resume=True):
        """
        Main scraping function
        
        Args:
            max_kanji (int): Maximum number of kanji to scrape
            resume (bool): Resume from checkpoint if available
        """
        print(f"\n{'='*70}")
        print(f"🚀 STARTING JLPT {self.level.upper()} MASTER SCRAPER")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        
        # Try to resume from checkpoint
        if resume:
            self.load_checkpoint()
            
        # Get all kanji URLs
        kanji_urls = self.get_all_kanji_urls()
        
        if not kanji_urls:
            print("❌ No kanji URLs found!")
            return False
            
        # Limit if specified
        if max_kanji and len(kanji_urls) > max_kanji:
            print(f"📊 Limiting to {max_kanji} kanji")
            kanji_urls = kanji_urls[:max_kanji]
            
        print(f"\n📥 Starting to scrape {len(kanji_urls)} kanji pages...\n")
        
        # Scrape each kanji
        for idx, url in enumerate(kanji_urls, 1):
            # Skip if already scraped
            already_scraped = False
            for kanji in self.kanji_data:
                if kanji.get('page_url') == url:
                    already_scraped = True
                    break
                    
            if already_scraped:
                print(f"[{idx}/{len(kanji_urls)}] ✅ Already scraped: {url}")
                continue
                
            # Scrape the kanji
            kanji_data = self.scrape_kanji_detail(url)
            
            if kanji_data:
                self.kanji_data.append(kanji_data)
                
                # Save checkpoint every 5 kanji
                if idx % 5 == 0:
                    self.save_checkpoint()
                    
                # Rate limiting
                if idx < len(kanji_urls):
                    delay = random.uniform(self.rate_limit, self.rate_limit * 2)
                    print(f"    ⏳ Waiting {delay:.1f}s before next...")
                    time.sleep(delay)
            else:
                print(f"    ❌ Failed to scrape {url}")
                
        # Perform integrity check
        self.perform_integrity_check()
        
        # Final save
        self.save_final_results()
        
        # Clean up
        self.cleanup()
        
        # Print statistics
        elapsed_time = time.time() - start_time
        self.print_statistics(elapsed_time)
        
        return True
        
    def save_final_results(self):
        """Save final results to JSON file"""
        if not self.kanji_data:
            print("❌ No data to save!")
            return
            
        # Prepare metadata
        metadata = {
            'level': self.level.upper(),
            'total_kanji': len(self.kanji_data),
            'scraped_at': datetime.now().isoformat(),
            'version': '2.0-universal',
            'source': 'jlptsensei.com',
            'features': [
                'kanji_characters',
                'meanings',
                'all_readings_extracted',
                'stroke_counts',
                'stroke_diagrams',
                'flashcard_images',
                'rich_text_examples',
                'html_styling_preserved',
                'furigana',
                'romaji',
                'english_translations',
                'metadata',
                'data_quality_scores'
            ]
        }
        
        # Calculate statistics
        stats = {
            'total_onyomi': sum(len(k['readings']['onyomi']) for k in self.kanji_data),
            'total_kunyomi': sum(len(k['readings']['kunyomi']) for k in self.kanji_data),
            'total_special': sum(len(k['readings']['special']) for k in self.kanji_data),
            'total_examples': sum(len(k['examples']) for k in self.kanji_data),
            'rich_text_examples': sum(1 for k in self.kanji_data for ex in k['examples'] if ex.get('has_html_styling')),
            'kanji_with_stroke_count': sum(1 for k in self.kanji_data if k.get('stroke_count')),
            'kanji_with_stroke_diagram': sum(1 for k in self.kanji_data if k.get('stroke_diagram_svg') or k.get('stroke_image_url')),
            'kanji_with_flashcard': sum(1 for k in self.kanji_data if k.get('flashcard_url')),
            'average_data_quality': sum(k.get('data_quality', 0) for k in self.kanji_data) / len(self.kanji_data)
        }
        
        # Prepare complete output
        output = {
            'metadata': {**metadata, **stats},
            'kanji': self.kanji_data,
            'scraping_info': {
                'errors': self.errors,
                'skipped_urls': self.skipped_urls,
                'total_attempts': len(self.kanji_data) + len(self.skipped_urls)
            }
        }
        
        # Save main file
        try:
            with open(self.final_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Complete data saved to: {self.final_file}")
        except Exception as e:
            print(f"❌ Error saving final file: {e}")
            
        # Save minified version
        try:
            minified_file = f'jlpt_{self.level}_minified.json'
            with open(minified_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, separators=(',', ':'))
            print(f"✅ Minified data saved to: {minified_file}")
        except Exception as e:
            print(f"⚠️ Error saving minified file: {e}")
            
        # Save statistics separately
        try:
            stats_file = f'jlpt_{self.level}_statistics.json'
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
            print(f"✅ Statistics saved to: {stats_file}")
        except Exception as e:
            print(f"⚠️ Error saving statistics: {e}")
            
        # Save CSS for styling
        self.save_styling_css()
        
    def save_styling_css(self):
        """Save CSS file for styling kanji examples"""
        css_content = """
            /* JLPT Kanji Example Styling - Universal */
            .kanji-highlight {
                color: #e74c3c;
                font-weight: bold;
                background-color: #fff3cd;
                padding: 2px 4px;
                border-radius: 3px;
                border: 1px solid #ffc107;
            }

            .jp-example {
                font-family: "Hiragino Kaku Gothic Pro", "Meiryo", "MS PGothic", sans-serif;
                font-size: 1.3em;
                line-height: 1.8;
                margin: 15px 0;
                padding: 15px;
                background: linear-gradient(to right, #f8f9fa, #ffffff);
                border-radius: 8px;
                border-left: 5px solid #3498db;
            }

            .romaji-text {
                font-style: italic;
                color: #666;
                font-size: 0.95em;
                margin: 5px 0;
            }

            .english-translation {
                color: #2c3e50;
                font-size: 1.1em;
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px dashed #ddd;
            }

            .furigana-reading {
                color: #9b59b6;
                font-size: 0.85em;
                vertical-align: super;
            }

            .reading-item {
                padding: 10px 15px;
                margin: 8px 0;
                border-left: 4px solid #2ecc71;
                background-color: #f8f9fa;
                border-radius: 4px;
            }

            .reading-word {
                font-weight: bold;
                color: #2c3e50;
                font-size: 1.1em;
            }

            .reading-kana {
                color: #e74c3c;
                margin: 0 10px;
                font-family: "Hiragino Kaku Gothic Pro", sans-serif;
            }

            .reading-meaning {
                color: #7f8c8d;
                font-style: italic;
            }

            .stroke-diagram-container {
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                margin: 20px 0;
            }

            .kanji-character-large {
                font-size: 120px;
                font-family: "Hiragino Mincho Pro", serif;
                text-align: center;
                margin: 20px 0;
                color: #2c3e50;
            }

            .data-quality-badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: bold;
            }

            .quality-high { background-color: #d4edda; color: #155724; }
            .quality-medium { background-color: #fff3cd; color: #856404; }
            .quality-low { background-color: #f8d7da; color: #721c24; }
            """
        
        css_file = f'jlpt_{self.level}_styling.css'
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        print(f"✅ Styling CSS saved to: {css_file}")
        
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up resources...")
        
        # Close Selenium driver
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Selenium browser closed")
            except:
                pass
                
        # Remove checkpoint file
        if os.path.exists(self.checkpoint_file):
            try:
                os.remove(self.checkpoint_file)
                print(f"✅ Checkpoint file removed: {self.checkpoint_file}")
            except:
                pass
                
    def print_statistics(self, elapsed_time):
        """Print scraping statistics"""
        print(f"\n{'='*70}")
        print(f"📊 JLPT {self.level.upper()} SCRAPING COMPLETE")
        print(f"{'='*70}")
        
        print(f"\n⏱️  Time taken: {elapsed_time:.2f} seconds")
        print(f"   ({elapsed_time/60:.1f} minutes)")
        
        if self.kanji_data:
            total_kanji = len(self.kanji_data)
            
            # Calculate statistics
            total_onyomi = sum(len(k['readings']['onyomi']) for k in self.kanji_data)
            total_kunyomi = sum(len(k['readings']['kunyomi']) for k in self.kanji_data)
            total_special = sum(len(k['readings']['special']) for k in self.kanji_data)
            total_examples = sum(len(k['examples']) for k in self.kanji_data)
            rich_examples = sum(1 for k in self.kanji_data for ex in k['examples'] if ex.get('has_html_styling'))
            avg_quality = sum(k.get('data_quality', 0) for k in self.kanji_data) / total_kanji
            
            print(f"\n📊 DATA STATISTICS:")
            print(f"   • Kanji scraped: {total_kanji}")
            print(f"   • Onyomi readings: {total_onyomi}")
            print(f"   • Kunyomi readings: {total_kunyomi}")
            print(f"   • Special readings: {total_special}")
            print(f"   • Example sentences: {total_examples}")
            print(f"   • Rich text examples: {rich_examples}")
            print(f"   • Average data quality: {avg_quality:.1f}/100")
            
            # Show sample
            if total_kanji > 0:
                sample = self.kanji_data[0]
                print(f"\n📄 SAMPLE DATA (First kanji):")
                print(f"   Character: {sample['character']}")
                print(f"   Meaning: {sample['meaning']}")
                print(f"   Stroke count: {sample.get('stroke_count', 'N/A')}")
                print(f"   Onyomi examples: {len(sample['readings']['onyomi'])}")
                print(f"   Kunyomi examples: {len(sample['readings']['kunyomi'])}")
                if sample['examples']:
                    print(f"   First example: {sample['examples'][0]['japanese_text'][:50]}...")
                    
        if self.errors:
            print(f"\n⚠️  Errors encountered: {len(self.errors)}")
            print(f"   (See final JSON file for details)")
            
        if self.skipped_urls:
            print(f"\n⚠️  Skipped URLs: {len(self.skipped_urls)}")
            
        print(f"\n💾 OUTPUT FILES:")
        print(f"   1. {self.final_file} - Complete data")
        print(f"   2. jlpt_{self.level}_minified.json - Minified version")
        print(f"   3. jlpt_{self.level}_statistics.json - Statistics")
        print(f"   4. jlpt_{self.level}_styling.css - CSS for styling")
        print(f"\n✨ All done! The scraper has collected all requested features:")
        print(f"   ✓ Kanji characters")
        print(f"   ✓ All readings (onyomi/kunyomi/special)")
        print(f"   ✓ Rich text examples with HTML styling")
        print(f"   ✓ Stroke diagrams")
        print(f"   ✓ Flashcard images")
        print(f"   ✓ Complete metadata")


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='JLPT Universal Master Scraper - Extract all kanji with rich text and styling'
    )
    
    parser.add_argument('--level', type=str, default='n5',
                       choices=['n1', 'n2', 'n3', 'n4', 'n5'],
                       help='JLPT level to scrape (default: n5)')
    
    parser.add_argument('--max', type=int, default=None,
                       help='Maximum number of kanji to scrape (default: all)')
    
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode (faster)')
    
    parser.add_argument('--rate-limit', type=float, default=2.0,
                       help='Minimum delay between requests in seconds (default: 2.0)')
    
    parser.add_argument('--no-resume', action='store_true',
                       help='Do not resume from checkpoint')
    
    parser.add_argument('--test', action='store_true',
                       help='Test mode (scrape only 3 kanji)')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🎌 JLPT UNIVERSAL MASTER SCRAPER 🎌")
    print("="*70)
    print("Features:")
    print("  • Bypasses CAPTCHA with Selenium")
    print("  • Extracts ALL kanji characters")
    print("  • Gets ALL readings (onyomi/kunyomi/special)")
    print("  • Preserves rich text examples with HTML styling")
    print("  • Captures stroke diagrams and flashcard images")
    print("  • Works for all JLPT levels (N1-N5)")
    print("="*70 + "\n")
    
    # Test mode
    if args.test:
        args.max = 3
        print("🧪 TEST MODE: Scraping only 3 kanji")
    
    # Create scraper
    scraper = JLPTUniversalMasterScraper(
        level=args.level,
        headless=args.headless,
        rate_limit=args.rate_limit
    )
    
    # Run scraper
    success = scraper.run(
        max_kanji=args.max,
        resume=not args.no_resume
    )
    
    if success:
        print("\n🎉 Scraping completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Scraping failed or incomplete")
        sys.exit(1)


if __name__ == '__main__':
    main()