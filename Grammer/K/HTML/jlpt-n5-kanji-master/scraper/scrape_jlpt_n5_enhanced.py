#!/usr/bin/env python3
"""
JLPT N5 Kanji Enhanced Scraper with Anti-Bot Detection
Scrapes from jlptsensei.com with maximum stealth
"""

import requests
from bs4 import BeautifulSoup
import json
import base64
from io import BytesIO
from PIL import Image
import time
import random
import re
from urllib.parse import urljoin, urlparse, unquote
from datetime import datetime
import hashlib

class StealthScraper:
    """Advanced scraper with anti-detection measures"""
    
    def __init__(self):
        self.base_url = "https://jlptsensei.com/jlpt-n5-kanji-list/"
        self.kanji_data = []
        self.failed_images = []
        self.request_count = 0
        self.start_time = time.time()
        
        # 1. Define User Agents pool FIRST so they exist when the session is created
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # 2. Now create the session
        self.session = self._create_stealth_session()
        
    def _create_stealth_session(self):
        """Create a session that mimics real browser behavior"""
        session = requests.Session()
        
        # Rotate user agent - self.user_agents is now defined and accessible
        ua = random.choice(self.user_agents)
        
        # Full browser headers
        session.headers.update({
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
        
        return session

    def _smart_delay(self, min_delay=2.0, max_delay=5.0):
        """Human-like random delays between requests"""
        delay = random.uniform(min_delay, max_delay)
        
        # Add occasional longer pauses (simulating user reading)
        if random.random() < 0.15:  # 15% chance
            delay += random.uniform(3, 8)
        
        print(f"⏳ Waiting {delay:.1f}s... (human-like behavior)")
        time.sleep(delay)
        
        self.request_count += 1
        
        # Every 10 requests, take a longer break
        if self.request_count % 10 == 0:
            break_time = random.uniform(15, 30)
            print(f"☕ Taking a break for {break_time:.1f}s (every 10 requests)")
            time.sleep(break_time)
    
    def _safe_request(self, url, max_retries=3):
        """Make a request with retries and error handling"""
        for attempt in range(max_retries):
            try:
                # Rotate user agent occasionally
                if random.random() < 0.3:  # 30% chance
                    self.session.headers['User-Agent'] = random.choice(self.user_agents)
                
                # Add referer for subsequent requests
                if self.request_count > 0:
                    self.session.headers['Referer'] = self.base_url
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # FIX: Handle encoding properly for Japanese characters
                # Don't rely on response.encoding - we'll decode manually in _get_response_text()
                # But set it to UTF-8 to avoid warnings when response.text is accessed elsewhere
                if not response.encoding or response.encoding.lower() in ['iso-8859-1', 'latin-1', 'ascii']:
                    response.encoding = 'utf-8'
                
                # Check if we got blocked (check for common block patterns)
                if self._is_blocked(response):
                    print(f"⚠️ Detected possible block, waiting longer...")
                    time.sleep(60)  # Wait 1 minute
                    continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10  # Exponential backoff
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"💀 Failed to fetch {url} after {max_retries} attempts")
                    return None
        
        return None
    
    def _get_response_text(self, response):
        """Safely decode response content to text with proper UTF-8 handling
        
        This method manually decodes the response content to avoid Python's
        encoding warnings when invalid UTF-8 sequences are encountered.
        """
        # Always decode manually from content to avoid encoding warnings
        # Try UTF-8 first (most common for modern websites)
        try:
            return response.content.decode('utf-8', errors='replace')
        except (UnicodeDecodeError, UnicodeError, AttributeError):
            pass
        
        # Fallback: try Japanese-specific encodings
        for encoding in ['shift-jis', 'euc-jp', 'iso-2022-jp', 'cp932']:
            try:
                return response.content.decode(encoding, errors='replace')
            except (UnicodeDecodeError, UnicodeError, LookupError):
                continue
        
        # Last resort: latin-1 (never fails, but may show wrong characters)
        try:
            return response.content.decode('latin-1', errors='replace')
        except:
            # Absolute last resort: return empty string
            return ''
    
    def _is_blocked(self, response):
        """Check if response indicates we've been blocked"""
        # Check status code
        if response.status_code in [403, 429, 503]:
            return True
        
        # Check content for block indicators
        content_lower = self._get_response_text(response).lower()
        block_indicators = [
            'captcha',
            'cloudflare',
            'access denied',
            'rate limit',
            'too many requests',
            'robot',
            'bot detection'
        ]
        
        for indicator in block_indicators:
            if indicator in content_lower:
                return True
        
        # Check if content is suspiciously small
        if len(response.content) < 500:
            return True
        
        return False
    
    def scrape_all(self):
        """Main scraping orchestrator with progress tracking"""
        print("=" * 60)
        print("🎌 JLPT N5 Kanji Enhanced Scraper v2.0")
        print("=" * 60)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Get main page and find individual kanji links
        print("📡 Step 1: Fetching main kanji list page...")
        all_kanji_links = self.get_all_kanji_links()
        
        if not all_kanji_links:
            print("💀 Failed to get kanji links. Exiting.")
            return
        
        print(f"✅ Found {len(all_kanji_links)} kanji to scrape")
        print()
        
        # Step 2: Scrape each kanji detail page
        print("📥 Step 2: Scraping individual kanji pages...")
        for idx, (kanji_char, kanji_url) in enumerate(all_kanji_links, 1):
            print(f"\n{'='*60}")
            print(f"[{idx}/{len(all_kanji_links)}] Scraping: {kanji_char}")
            print(f"URL: {kanji_url}")
            print(f"{'='*60}")
            
            kanji_data = self.scrape_kanji_detail(kanji_url, idx)
            
            if kanji_data:
                self.kanji_data.append(kanji_data)
                print(f"✅ Successfully scraped {kanji_char}")
            else:
                print(f"⚠️ Failed to scrape {kanji_char}")
            
            # Smart delay between requests (except for last one)
            if idx < len(all_kanji_links):
                self._smart_delay(3.0, 6.0)  # Longer delays for detail pages
        
        print("\n" + "=" * 60)
        print("🔍 Step 3: Enhancing with metadata...")
        self.enhance_with_metadata()
        
        print("✅ Step 4: Validating all data...")
        self.validate_all_kanji()
        
        print("💾 Step 5: Exporting to JSON...")
        self.export_json()
        
        # Summary
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 60)
        print("🎉 SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"✅ Successfully scraped: {len(self.kanji_data)}/{len(all_kanji_links)} kanji")
        print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
        print(f"📊 Total requests: {self.request_count}")
        
        if self.failed_images:
            print(f"⚠️  Failed images: {len(self.failed_images)}")
            print(f"   {', '.join(self.failed_images)}")
        
        print("=" * 60)
    
    def get_all_kanji_links(self):
        """Get links to all individual kanji pages from the list page"""
        response = self._safe_request(self.base_url)
        if not response:
            print("❌ Failed to get response from server")
            return []
        
        print(f"✅ Got response: Status {response.status_code}, Size: {len(response.content)} bytes")
        
        # Check if we got blocked
        if self._is_blocked(response):
            print("⚠️  Response indicates we may have been blocked")
            # Save HTML for debugging
            try:
                with open('debug_response.html', 'w', encoding='utf-8') as f:
                    f.write(self._get_response_text(response)[:50000])  # First 50KB
                print("   💾 Saved first 50KB to debug_response.html for inspection")
            except:
                pass
            return []
        
        try:
            # Safely decode response content to avoid encoding errors
            html_text = self._get_response_text(response)
            soup = BeautifulSoup(html_text, 'html.parser')
            
            # Debug: Check if we got actual content
            title = soup.find('title')
            if title:
                print(f"📄 Page title: {title.text.strip()[:100]}")
            else:
                print("⚠️  No title found - page might be empty or blocked")
        except Exception as e:
            print(f"❌ Error parsing HTML: {e}")
            print(f"   Response encoding: {response.encoding}")
            print(f"   Response length: {len(response.content)} bytes")
            import traceback
            traceback.print_exc()
            return []
        
        kanji_links = []
        seen_urls = set()  # Track URLs to avoid duplicates
        
        # Method 1: Look for the kanji table with id="jl-kanji" (most reliable)
        kanji_table = soup.find('table', id='jl-kanji')
        if kanji_table:
            print("✅ Found kanji table with id='jl-kanji'")
            # Find all links in the kanji column (class="jl-td-k")
            kanji_cells = kanji_table.find_all('td', class_='jl-td-k')
            print(f"   Found {len(kanji_cells)} kanji cells")
            
            for cell in kanji_cells:
                link = cell.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    link_text = link.text.strip()
                    
                    # Check if link text is a single kanji
                    if re.match(r'^[\u4e00-\u9faf]$', link_text) and '/learn-japanese-kanji/' in href:
                        full_url = urljoin(self.base_url, href) if not href.startswith('http') else href
                        if full_url not in seen_urls:
                            kanji_links.append((link_text, full_url))
                            seen_urls.add(full_url)
        
        # Method 2: Fallback - search all links (original method)
        if len(kanji_links) == 0:
            print("⚠️  Table method didn't work, trying fallback method...")
            all_links_with_pattern = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                kanji_char = None
                full_url = urljoin(self.base_url, href) if not href.startswith('http') else href
                
                # Only process links to kanji pages
                if '/learn-japanese-kanji/' not in href:
                    continue
                    
                # Debug: collect all links with the pattern
                link_text = link.text.strip()
                all_links_with_pattern.append((href, link_text, repr(link_text)))
                
                # Method 2a: Check if link text is a single kanji
                if re.match(r'^[\u4e00-\u9faf]$', link_text):
                    kanji_char = link_text
                # Method 2b: Check if kanji is in a child element (span, div, etc.)
                else:
                    for child in link.find_all(['span', 'div', 'strong', 'em']):
                        child_text = child.text.strip()
                        if re.match(r'^[\u4e00-\u9faf]$', child_text):
                            kanji_char = child_text
                            break
                # Method 2c: Extract kanji from URL if not found in text
                # URLs are URL-encoded, so we need to decode them
                if not kanji_char:
                    try:
                        decoded_href = unquote(href)
                        url_match = re.search(r'/learn-japanese-kanji/([^/?-]+)', decoded_href)
                        if url_match:
                            potential_kanji = url_match.group(1).strip()
                            # Check if it's a single kanji character
                            if re.match(r'^[\u4e00-\u9faf]$', potential_kanji):
                                kanji_char = potential_kanji
                    except:
                        pass
                
                # Add to list if we found a valid kanji
                if kanji_char and full_url not in seen_urls:
                    kanji_links.append((kanji_char, full_url))
                    seen_urls.add(full_url)
            
            # Debug output for fallback
            print(f"🔍 Found {len(all_links_with_pattern)} links with '/learn-japanese-kanji/' pattern")
            if len(all_links_with_pattern) > 0 and len(kanji_links) == 0:
                print("⚠️  Links found but none matched kanji pattern. Sample links:")
                for href, char, char_repr in all_links_with_pattern[:5]:
                    print(f"   - href: {href[:80]}... | text: {char_repr}")
        
        # Debug output
        print(f"🔍 Found {len(kanji_links)} valid kanji links (single kanji character)")
        
        if len(kanji_links) == 0:
            print("⚠️  No kanji links found. Checking if page structure changed...")
            # Try alternative selectors
            # Maybe links are in a table or specific container
            tables = soup.find_all('table')
            print(f"   Found {len(tables)} tables in page")
            
            # Check for common containers
            containers = soup.find_all(['div', 'section'], class_=re.compile(r'kanji|list|table', re.I))
            print(f"   Found {len(containers)} potential kanji containers")
        
        return kanji_links[:80]

    def scrape_kanji_detail(self, url, kanji_id):
        """Scrape all data from a single kanji detail page"""
        response = self._safe_request(url)
        
        if not response:
            return None
        
        # Safely decode response content to avoid encoding errors
        html_text = self._get_response_text(response)
        soup = BeautifulSoup(html_text, 'html.parser')
        
        try:
            # Extract character (from title or main display)
            character = self._extract_character(soup)
            print(f"  📝 Character: {character}")
            
            # Extract SVG stroke diagram
            svg = self._extract_svg(soup)
            print(f"  🖼️  SVG: {'✓' if svg else '✗'}")
            
            # Extract flashcard image
            flashcard_base64 = self._extract_flashcard(soup, character)
            print(f"  🎴 Flashcard: {'✓' if flashcard_base64 else '✗'}")
            
            # Extract mnemonic
            mnemonic = self._extract_mnemonic(soup)
            print(f"  💭 Mnemonic: {'✓' if mnemonic else '✗'}")
            
            # Extract readings
            readings = self._extract_readings(soup)
            print(f"  📖 Readings: On={len(readings['onyomi'])}, Kun={len(readings['kunyomi'])}, Sp={len(readings['special'])}")
            
            # Extract examples
            examples = self._extract_examples(soup)
            print(f"  📚 Examples: {len(examples)}")
            
            return {
                'id': kanji_id,
                'character': character,
                'svg': svg,
                'svg_paths': self._parse_svg_paths(svg) if svg else [],
                'flashcard_base64': flashcard_base64,
                'mnemonic': mnemonic,
                'readings': readings,
                'examples': examples,
                'stroke_count': None,  # To be filled in enhance step
                'radical': None,
                'radical_meaning': None,
                'jlpt_level': 'N5',
                'frequency_rank': None,
                'related_kanji': [],
                'confusion_pairs': [],
                'user_data': {
                    'mastery_level': 0,
                    'last_reviewed': None,
                    'next_review': None,
                    'times_correct': 0,
                    'times_wrong': 0,
                    'bookmarked': False,
                    'notes': '',
                    'accuracy': 0
                }
            }
            
        except Exception as e:
            print(f"  ❌ Error extracting kanji data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_character(self, soup):
        """Extract the kanji character"""
        # Try multiple selectors
        
        # Method 1: Look for main kanji display
        kanji_display = soup.find('div', class_='kanji-display')
        if kanji_display:
            return kanji_display.text.strip()
        
        # Method 2: Look in title
        title = soup.find('h1')
        if title:
            # Extract first CJK character from title
            text = title.text
            for char in text:
                if ord(char) > 0x4E00:
                    return char
        
        # Method 3: Look for span with jp class
        jp_span = soup.find('span', class_='jp')
        if jp_span:
            text = jp_span.text.strip()
            if len(text) >= 1 and ord(text[0]) > 0x4E00:
                return text[0]
        
        return None
    
    def _extract_svg(self, soup):
        """Extract SVG stroke diagram"""
        svg_element = soup.find('svg', class_=re.compile(r'stroke_order_diagram'))
        
        if svg_element:
            return str(svg_element)
        
        return None
    
    def _parse_svg_paths(self, svg_str):
        """Parse individual stroke paths from SVG"""
        if not svg_str:
            return []
        
        soup = BeautifulSoup(svg_str, 'html.parser')
        paths = []
        
        for path in soup.find_all('path'):
            path_id = path.get('id', '')
            path_type = path.get('kvg:type', '')
            path_d = path.get('d', '')
            
            if path_d:
                paths.append({
                    'id': path_id,
                    'type': path_type,
                    'path': path_d
                })
        
        return paths
    
    def _extract_flashcard(self, soup, character):
        """Extract and encode flashcard image"""
        img = soup.find('img', class_='img-responsive')
        
        if not img:
            # Alternative: look for any image with kanji in filename
            for img_tag in soup.find_all('img'):
                src = img_tag.get('src', '')
                if 'kanji' in src.lower() or 'flashcard' in src.lower():
                    img = img_tag
                    break
        
        if not img:
            self.failed_images.append(character)
            return None
        
        img_url = img.get('src', '')
        
        if not img_url:
            self.failed_images.append(character)
            return None
        
        # Make absolute URL
        if not img_url.startswith('http'):
            img_url = urljoin(self.base_url, img_url)
        
        # Download and encode
        return self._download_and_encode_image(img_url, character)
    
    def _download_and_encode_image(self, url, character):
        """Download image and convert to base64"""
        try:
            # Use same session for consistency
            self._smart_delay(1.0, 2.0)  # Short delay for images
            
            response = self._safe_request(url)
            
            if not response or response.status_code != 200:
                self.failed_images.append(character)
                return None
            
            # Convert to WebP for compression (or keep as PNG if small)
            img = Image.open(BytesIO(response.content))
            
            # Determine format based on size
            buffer = BytesIO()
            
            # If image is already small, keep as PNG
            if len(response.content) < 50000:  # 50KB
                img.save(buffer, format='PNG', optimize=True)
                mime_type = 'image/png'
            else:
                # Convert to WebP for compression
                img.save(buffer, format='WEBP', quality=85)
                mime_type = 'image/webp'
            
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:{mime_type};base64,{base64_str}"
            
        except Exception as e:
            print(f"  ⚠️ Failed to download image: {e}")
            self.failed_images.append(character)
            return None
    
    def _extract_mnemonic(self, soup):
        """Extract mnemonic story/explanation"""
        # Look for various possible locations
        
        # Method 1: Dedicated mnemonic div
        mnemonic_div = soup.find('div', class_='mnemonic')
        if mnemonic_div:
            return mnemonic_div.text.strip()
        
        # Method 2: Description/meaning section
        desc_div = soup.find('div', class_='kanji-description')
        if desc_div:
            return desc_div.text.strip()
        
        # Method 3: Any paragraph with "meaning" or "remember"
        for p in soup.find_all('p'):
            text = p.text.lower()
            if 'meaning' in text or 'remember' in text or 'think of' in text:
                return p.text.strip()
        
        return None
    
    def _extract_readings(self, soup):
        """Extract onyomi, kunyomi, and special readings"""
        readings = {'onyomi': [], 'kunyomi': [], 'special': []}
        
        # Find the related-words div
        related_words = soup.find('div', id='related-words')
        
        if not related_words:
            return readings
        
        # Get the full text content
        full_text = related_words.get_text()
        
        # Split by sections
        sections = {
            'onyomi': r'Onyomi Readings\s*(.*?)(?=Kunyomi Readings|Special Readings|$)',
            'kunyomi': r'Kunyomi Readings\s*(.*?)(?=Special Readings|$)',
            'special': r'Special Readings\s*(.*?)$'
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            
            if match:
                section_text = match.group(1).strip()
                
                # Parse entries in format: word 【reading】 meaning
                # Using different patterns to handle variations
                entries = re.findall(r'([^\s【]+)\s*【([^】]+)】\s*([^\n]+)', section_text)
                
                for word, reading, meaning in entries:
                    readings[key].append({
                        'word': word.strip(),
                        'reading': reading.strip(),
                        'meaning': meaning.strip()
                    })
        
        return readings
    
    def _extract_examples(self, soup):
        """Extract example sentences with preserved formatting"""
        examples = []
        
        # Find all example containers
        example_divs = soup.find_all('div', class_='example-cont')
        
        for ex_div in example_divs:
            try:
                # Main sentence (with HTML formatting preserved)
                main_div = ex_div.find('div', class_='alert-secondary')
                
                if not main_div:
                    continue
                
                # Get the paragraph with Japanese text
                main_p = main_div.find('p', class_='jp') or main_div.find('p')
                
                if not main_p:
                    continue
                
                # Preserve HTML but clean ads
                japanese_html = str(main_p)
                japanese_html = self._clean_html(japanese_html)
                
                # Furigana (kana reading)
                furigana_div = ex_div.find('div', class_='alert-success')
                furigana = furigana_div.text.strip() if furigana_div else ''
                
                # Romaji
                romaji_div = ex_div.find('div', class_='alert-info')
                romaji = romaji_div.text.strip() if romaji_div else ''
                
                # English
                english_div = ex_div.find('div', class_='alert-primary')
                english = english_div.text.strip() if english_div else ''
                
                if japanese_html or furigana:  # At least one should exist
                    examples.append({
                        'japanese_html': japanese_html,
                        'furigana': furigana,
                        'romaji': romaji,
                        'english': english
                    })
                    
            except Exception as e:
                print(f"  ⚠️ Error parsing example: {e}")
                continue
        
        return examples
    
    def _clean_html(self, html_str):
        """Remove ads and tracking but preserve formatting"""
        soup = BeautifulSoup(html_str, 'html.parser')
        
        # Remove unwanted elements
        for unwanted in soup.find_all(['iframe', 'ins', 'script', 'noscript', 'style']):
            unwanted.decompose()
        
        # Remove ezoic elements
        for ez in soup.find_all(class_=re.compile('ezoic', re.IGNORECASE)):
            ez.decompose()
        
        # Remove ad containers
        for ad in soup.find_all(['div', 'span'], id=re.compile('ad|ads|google', re.IGNORECASE)):
            ad.decompose()
        
        # Remove data attributes used for tracking
        for tag in soup.find_all(True):
            tag.attrs = {k: v for k, v in tag.attrs.items() 
                        if not k.startswith('data-ez') and not k.startswith('data-google')}
        
        return str(soup)
    
    def enhance_with_metadata(self):
        """Add stroke count, radical info, and related kanji"""
        
        # Stroke count and radical lookup for all N5 kanji
        # (This is a curated dataset - more reliable than scraping)
        metadata_lookup = {
            '一': {'stroke_count': 1, 'radical': '一', 'radical_meaning': 'one'},
            '七': {'stroke_count': 2, 'radical': '一', 'radical_meaning': 'one'},
            '三': {'stroke_count': 3, 'radical': '一', 'radical_meaning': 'one'},
            '上': {'stroke_count': 3, 'radical': '一', 'radical_meaning': 'one'},
            '下': {'stroke_count': 3, 'radical': '一', 'radical_meaning': 'one'},
            '九': {'stroke_count': 2, 'radical': '乙', 'radical_meaning': 'second'},
            '二': {'stroke_count': 2, 'radical': '二', 'radical_meaning': 'two'},
            '人': {'stroke_count': 2, 'radical': '人', 'radical_meaning': 'person'},
            '入': {'stroke_count': 2, 'radical': '入', 'radical_meaning': 'enter'},
            '八': {'stroke_count': 2, 'radical': '八', 'radical_meaning': 'eight'},
            '十': {'stroke_count': 2, 'radical': '十', 'radical_meaning': 'ten'},
            '力': {'stroke_count': 2, 'radical': '力', 'radical_meaning': 'power'},
            '千': {'stroke_count': 3, 'radical': '十', 'radical_meaning': 'ten'},
            '口': {'stroke_count': 3, 'radical': '口', 'radical_meaning': 'mouth'},
            '土': {'stroke_count': 3, 'radical': '土', 'radical_meaning': 'earth'},
            '大': {'stroke_count': 3, 'radical': '大', 'radical_meaning': 'big'},
            '女': {'stroke_count': 3, 'radical': '女', 'radical_meaning': 'woman'},
            '子': {'stroke_count': 3, 'radical': '子', 'radical_meaning': 'child'},
            '小': {'stroke_count': 3, 'radical': '小', 'radical_meaning': 'small'},
            '山': {'stroke_count': 3, 'radical': '山', 'radical_meaning': 'mountain'},
            '川': {'stroke_count': 3, 'radical': '川', 'radical_meaning': 'river'},
            '五': {'stroke_count': 4, 'radical': '二', 'radical_meaning': 'two'},
            '六': {'stroke_count': 4, 'radical': '八', 'radical_meaning': 'eight'},
            '円': {'stroke_count': 4, 'radical': '冂', 'radical_meaning': 'upside down box'},
            '天': {'stroke_count': 4, 'radical': '大', 'radical_meaning': 'big'},
            '手': {'stroke_count': 4, 'radical': '手', 'radical_meaning': 'hand'},
            '文': {'stroke_count': 4, 'radical': '文', 'radical_meaning': 'literature'},
            '日': {'stroke_count': 4, 'radical': '日', 'radical_meaning': 'sun, day'},
            '月': {'stroke_count': 4, 'radical': '月', 'radical_meaning': 'moon, month'},
            '木': {'stroke_count': 4, 'radical': '木', 'radical_meaning': 'tree, wood'},
            '水': {'stroke_count': 4, 'radical': '水', 'radical_meaning': 'water'},
            '火': {'stroke_count': 4, 'radical': '火', 'radical_meaning': 'fire'},
            '犬': {'stroke_count': 4, 'radical': '犬', 'radical_meaning': 'dog'},
            '王': {'stroke_count': 4, 'radical': '玉', 'radical_meaning': 'jade'},
            '右': {'stroke_count': 5, 'radical': '口', 'radical_meaning': 'mouth'},
            '四': {'stroke_count': 5, 'radical': '囗', 'radical_meaning': 'enclosure'},
            '左': {'stroke_count': 5, 'radical': '工', 'radical_meaning': 'work'},
            '本': {'stroke_count': 5, 'radical': '木', 'radical_meaning': 'tree'},
            '正': {'stroke_count': 5, 'radical': '止', 'radical_meaning': 'stop'},
            '生': {'stroke_count': 5, 'radical': '生', 'radical_meaning': 'life'},
            '目': {'stroke_count': 5, 'radical': '目', 'radical_meaning': 'eye'},
            '石': {'stroke_count': 5, 'radical': '石', 'radical_meaning': 'stone'},
            '立': {'stroke_count': 5, 'radical': '立', 'radical_meaning': 'stand'},
            '出': {'stroke_count': 5, 'radical': '凵', 'radical_meaning': 'container'},
            '半': {'stroke_count': 5, 'radical': '十', 'radical_meaning': 'ten'},
            '母': {'stroke_count': 5, 'radical': '母', 'radical_meaning': 'mother'},
            '北': {'stroke_count': 5, 'radical': '匕', 'radical_meaning': 'spoon'},
            '白': {'stroke_count': 5, 'radical': '白', 'radical_meaning': 'white'},
            '百': {'stroke_count': 6, 'radical': '白', 'radical_meaning': 'white'},
            '年': {'stroke_count': 6, 'radical': '干', 'radical_meaning': 'shield'},
            '休': {'stroke_count': 6, 'radical': '人', 'radical_meaning': 'person'},
            '先': {'stroke_count': 6, 'radical': '儿', 'radical_meaning': 'legs'},
            '名': {'stroke_count': 6, 'radical': '口', 'radical_meaning': 'mouth'},
            '字': {'stroke_count': 6, 'radical': '子', 'radical_meaning': 'child'},
            '早': {'stroke_count': 6, 'radical': '日', 'radical_meaning': 'sun'},
            '気': {'stroke_count': 6, 'radical': '气', 'radical_meaning': 'steam'},
            '竹': {'stroke_count': 6, 'radical': '竹', 'radical_meaning': 'bamboo'},
            '糸': {'stroke_count': 6, 'radical': '糸', 'radical_meaning': 'silk'},
            '耳': {'stroke_count': 6, 'radical': '耳', 'radical_meaning': 'ear'},
            '虫': {'stroke_count': 6, 'radical': '虫', 'radical_meaning': 'insect'},
            '村': {'stroke_count': 7, 'radical': '木', 'radical_meaning': 'tree'},
            '男': {'stroke_count': 7, 'radical': '田', 'radical_meaning': 'rice field'},
            '町': {'stroke_count': 7, 'radical': '田', 'radical_meaning': 'rice field'},
            '見': {'stroke_count': 7, 'radical': '見', 'radical_meaning': 'see'},
            '車': {'stroke_count': 7, 'radical': '車', 'radical_meaning': 'vehicle'},
            '足': {'stroke_count': 7, 'radical': '足', 'radical_meaning': 'foot'},
            '金': {'stroke_count': 8, 'radical': '金', 'radical_meaning': 'metal, gold'},
            '雨': {'stroke_count': 8, 'radical': '雨', 'radical_meaning': 'rain'},
            '青': {'stroke_count': 8, 'radical': '青', 'radical_meaning': 'blue'},
            '食': {'stroke_count': 9, 'radical': '食', 'radical_meaning': 'eat, food'},
            '飲': {'stroke_count': 12, 'radical': '食', 'radical_meaning': 'eat'},
            '駅': {'stroke_count': 14, 'radical': '馬', 'radical_meaning': 'horse'},
            '高': {'stroke_count': 10, 'radical': '高', 'radical_meaning': 'tall'},
            '校': {'stroke_count': 10, 'radical': '木', 'radical_meaning': 'tree'},
            '時': {'stroke_count': 10, 'radical': '日', 'radical_meaning': 'sun'},
            '外': {'stroke_count': 5, 'radical': '夕', 'radical_meaning': 'evening'},
            '国': {'stroke_count': 8, 'radical': '囗', 'radical_meaning': 'enclosure'},
            '語': {'stroke_count': 14, 'radical': '言', 'radical_meaning': 'speech'},
            '学': {'stroke_count': 8, 'radical': '子', 'radical_meaning': 'child'},
        }
        
        # Apply metadata
        for kanji in self.kanji_data:
            char = kanji['character']
            if char in metadata_lookup:
                kanji.update(metadata_lookup[char])
            else:
                print(f"  ⚠️ No metadata for {char}")
        
        # Calculate related kanji (same radical)
        self._calculate_related_kanji()
        
        # Calculate confusion pairs (visually similar)
        self._calculate_confusion_pairs()
    
    def _calculate_related_kanji(self):
        """Find kanji with same radical"""
        for kanji in self.kanji_data:
            if not kanji.get('radical'):
                continue
            
            radical = kanji['radical']
            related = []
            
            for other in self.kanji_data:
                if other['id'] != kanji['id'] and other.get('radical') == radical:
                    related.append(other['id'])
            
            kanji['related_kanji'] = related[:5]  # Limit to 5
    
    def _calculate_confusion_pairs(self):
        """Find visually similar kanji"""
        # Manual confusion pairs for common N5 kanji
        confusion_map = {
            '日': ['目', '白', '田'],
            '目': ['日', '四'],
            '口': ['日'],
            '田': ['日', '白'],
            '白': ['日', '百'],
            '大': ['犬', '天'],
            '犬': ['大'],
            '天': ['大'],
            '人': ['入'],
            '入': ['人'],
            '土': ['士'],
            '千': ['十'],
        }
        
        for kanji in self.kanji_data:
            char = kanji['character']
            if char in confusion_map:
                # Convert to IDs
                confusion_ids = []
                for conf_char in confusion_map[char]:
                    for other in self.kanji_data:
                        if other['character'] == conf_char:
                            confusion_ids.append(other['id'])
                            break
                
                kanji['confusion_pairs'] = confusion_ids
    
    def validate_all_kanji(self):
        """Validate each kanji has required data"""
        issues = []
        
        for kanji in self.kanji_data:
            char = kanji['character']
            
            # Critical checks
            if not char:
                issues.append(f"Missing character at ID {kanji['id']}")
                continue
            
            if not kanji.get('svg'):
                issues.append(f"❌ Missing SVG for {char}")
            
            if len(kanji.get('examples', [])) == 0:
                issues.append(f"❌ No examples for {char}")
            
            # Warnings
            if not kanji.get('flashcard_base64'):
                issues.append(f"⚠️ Missing flashcard for {char}")
            
            if not kanji.get('stroke_count'):
                issues.append(f"⚠️ Missing stroke count for {char}")
            
            if not kanji.get('readings', {}).get('onyomi') and not kanji.get('readings', {}).get('kunyomi'):
                issues.append(f"⚠️ No readings for {char}")
        
        # Print summary
        if issues:
            print("\n⚠️ Validation Issues:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("✅ All kanji validated successfully!")
        
        return len(issues) == 0
    
    def export_json(self, filename='kanji_data_enhanced.json'):
        """Export to minified JSON"""
        output = {
            'metadata': {
                'scrape_date': datetime.now().isoformat(),
                'total_kanji': len(self.kanji_data),
                'version': '2.0',
                'source': 'jlptsensei.com',
                'features': ['svg', 'flashcards', 'srs', 'analytics', 'stroke_animation'],
                'scraper_version': '2.0-stealth'
            },
            'kanji': self.kanji_data
        }
        
        # Save pretty version for debugging
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # Save minified version for production
        minified_filename = filename.replace('.json', '.min.json')
        with open(minified_filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, separators=(',', ':'))
        
        print(f"✅ Exported to:")
        print(f"   📄 {filename} (readable)")
        print(f"   📦 {minified_filename} (minified)")
        
        # Calculate file sizes
        import os
        size_readable = os.path.getsize(filename) / 1024 / 1024
        size_minified = os.path.getsize(minified_filename) / 1024 / 1024
        
        print(f"   💾 Sizes: {size_readable:.2f}MB (readable), {size_minified:.2f}MB (minified)")


def main():
    """Run the scraper"""
    print("🎌 Starting JLPT N5 Kanji Scraper...")
    print()
    print("⚠️  IMPORTANT: This scraper uses anti-detection measures:")
    print("   • Random delays (2-6 seconds between requests)")
    print("   • Rotating user agents")
    print("   • Browser-like headers")
    print("   • Automatic retries with backoff")
    print()
    print("⏱️  Expected duration: 20-40 minutes (for 80 kanji)")
    print()
    
    # Ask for confirmation
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("Aborted.")
        return
    
    scraper = StealthScraper()
    scraper.scrape_all()


if __name__ == '__main__':
    main()



# #!/usr/bin/env python3
# """
# JLPT N5 Kanji Enhanced Scraper with Anti-Bot Detection
# Scrapes from jlptsensei.com with maximum stealth
# """

# import requests
# from bs4 import BeautifulSoup
# import json
# import base64
# from io import BytesIO
# from PIL import Image
# import time
# import random
# import re
# from urllib.parse import urljoin, urlparse
# from datetime import datetime
# import hashlib

# class StealthScraper:
#     """Advanced scraper with anti-detection measures"""
    
#     def __init__(self):
#         self.base_url = "https://jlptsensei.com/jlpt-n5-kanji-list/"
#         self.kanji_data = []
#         self.failed_images = []
#         self.request_count = 0
#         self.start_time = time.time()
        
#         # FIX 1: Define user_agents BEFORE calling _create_stealth_session
#         self.user_agents = [
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
#             'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
#         ]
        
#         self.session = self._create_stealth_session()
        
#     def _create_stealth_session(self):
#         """Create a session that mimics real browser behavior"""
#         session = requests.Session()
#         ua = random.choice(self.user_agents)
        
#         session.headers.update({
#             'User-Agent': ua,
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
#             'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'DNT': '1',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1',
#             'Sec-Fetch-Dest': 'document',
#             'Sec-Fetch-Mode': 'navigate',
#             'Sec-Fetch-Site': 'none',
#             'Sec-Fetch-User': '?1',
#             'Cache-Control': 'max-age=0',
#         })
#         return session
    
#     def _smart_delay(self, min_delay=2.0, max_delay=5.0):
#         """Human-like random delays between requests"""
#         delay = random.uniform(min_delay, max_delay)
#         if random.random() < 0.15:
#             delay += random.uniform(3, 8)
#         print(f"⏳ Waiting {delay:.1f}s... (human-like behavior)")
#         time.sleep(delay)
#         self.request_count += 1
        
#         if self.request_count % 10 == 0:
#             break_time = random.uniform(15, 30)
#             print(f"☕ Taking a break for {break_time:.1f}s")
#             time.sleep(break_time)
    
#     def _safe_request(self, url, max_retries=3):
#         """Make a request with retries and error handling"""
#         for attempt in range(max_retries):
#             try:
#                 if random.random() < 0.3:
#                     self.session.headers['User-Agent'] = random.choice(self.user_agents)
                
#                 if self.request_count > 0:
#                     self.session.headers['Referer'] = self.base_url
                
#                 response = self.session.get(url, timeout=30)
                
#                 # FIX 2: Force UTF-8 encoding to prevent REPLACEMENT CHARACTER error
#                 response.encoding = 'utf-8'
                
#                 response.raise_for_status()
                
#                 if self._is_blocked(response):
#                     print(f"⚠️ Detected possible block, waiting longer...")
#                     time.sleep(60)
#                     continue
                
#                 return response
                
#             except requests.exceptions.RequestException as e:
#                 print(f"❌ Attempt {attempt + 1}/{max_retries} failed: {e}")
#                 if attempt < max_retries - 1:
#                     time.sleep((attempt + 1) * 10)
#         return None
    
#     def _is_blocked(self, response):
#         """Check if response indicates we've been blocked"""
#         if response.status_code in [403, 429, 503]: return True
#         content_lower = response.text.lower()
#         block_indicators = ['captcha', 'cloudflare', 'access denied', 'rate limit', 'robot']
#         return any(indicator in content_lower for indicator in block_indicators)

#     def get_all_kanji_links(self):
#         """Get links to all individual kanji pages"""
#         response = self._safe_request(self.base_url)
#         if not response: return []
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         kanji_links = []
        
#         # Regex to match exactly one CJK Unified Ideograph (Kanji)
#         kanji_pattern = re.compile(r'^[\u4e00-\u9faf]$')

#         for link in soup.find_all('a', href=True):
#             href = link.get('href', '')
#             kanji_char = link.text.strip()
            
#             # Logic: Must be in the right sub-directory and be a single Kanji char
#             if '/learn-japanese-kanji/' in href and kanji_pattern.match(kanji_char):
#                 full_url = urljoin(self.base_url, href)
#                 if (kanji_char, full_url) not in kanji_links:
#                     kanji_links.append((kanji_char, full_url))
        
#         return kanji_links[:80] # Limit to N5

#     def _extract_character(self, soup):
#         kanji_display = soup.find('div', class_='kanji-display')
#         if kanji_display: return kanji_display.text.strip()
#         title = soup.find('h1')
#         if title:
#             for char in title.text:
#                 if ord(char) > 0x4E00: return char
#         return None

#     def _extract_svg(self, soup):
#         svg_element = soup.find('svg', class_=re.compile(r'stroke_order_diagram'))
#         return str(svg_element) if svg_element else None

#     def _parse_svg_paths(self, svg_str):
#         if not svg_str: return []
#         soup = BeautifulSoup(svg_str, 'html.parser')
#         paths = []
#         for path in soup.find_all('path'):
#             paths.append({
#                 'id': path.get('id', ''),
#                 'type': path.get('kvg:type', ''),
#                 'path': path.get('d', '')
#             })
#         return paths

#     def _extract_flashcard(self, soup, character):
#         img = soup.find('img', class_='img-responsive')
#         if not img:
#             for img_tag in soup.find_all('img'):
#                 src = img_tag.get('src', '')
#                 if 'kanji' in src.lower():
#                     img = img_tag; break
#         if not img: return None
#         img_url = urljoin(self.base_url, img.get('src', ''))
#         return self._download_and_encode_image(img_url, character)

#     def _download_and_encode_image(self, url, character):
#         try:
#             self._smart_delay(1.0, 2.0)
#             response = self._safe_request(url)
#             if not response: return None
#             img = Image.open(BytesIO(response.content))
#             buffer = BytesIO()
#             img.save(buffer, format='WEBP', quality=85)
#             return f"data:image/webp;base64,{base64.b64encode(buffer.getvalue()).decode()}"
#         except Exception:
#             self.failed_images.append(character)
#             return None

#     def _extract_mnemonic(self, soup):
#         m_div = soup.find('div', class_='mnemonic')
#         return m_div.text.strip() if m_div else None

#     def _extract_readings(self, soup):
#         readings = {'onyomi': [], 'kunyomi': [], 'special': []}
#         rel_words = soup.find('div', id='related-words')
#         if not rel_words: return readings
#         text = rel_words.get_text()
#         patterns = {
#             'onyomi': r'Onyomi Readings\s*(.*?)(?=Kunyomi Readings|Special Readings|$)',
#             'kunyomi': r'Kunyomi Readings\s*(.*?)(?=Special Readings|$)',
#             'special': r'Special Readings\s*(.*?)$'
#         }
#         for key, pat in patterns.items():
#             match = re.search(pat, text, re.DOTALL | re.IGNORECASE)
#             if match:
#                 entries = re.findall(r'([^\s【]+)\s*【([^】]+)】\s*([^\n]+)', match.group(1))
#                 for w, r, m in entries:
#                     readings[key].append({'word': w.strip(), 'reading': r.strip(), 'meaning': m.strip()})
#         return readings

#     def _extract_examples(self, soup):
#         examples = []
#         for ex_div in soup.find_all('div', class_='example-cont'):
#             main_p = ex_div.find('p', class_='jp') or ex_div.find('p')
#             if not main_p: continue
#             examples.append({
#                 'japanese_html': str(main_p),
#                 'furigana': ex_div.find('div', class_='alert-success').text.strip() if ex_div.find('div', class_='alert-success') else '',
#                 'english': ex_div.find('div', class_='alert-primary').text.strip() if ex_div.find('div', class_='alert-primary') else ''
#             })
#         return examples

#     def scrape_kanji_detail(self, url, kanji_id):
#         response = self._safe_request(url)
#         if not response: return None
#         soup = BeautifulSoup(response.text, 'html.parser')
#         char = self._extract_character(soup)
#         svg = self._extract_svg(soup)
#         return {
#             'id': kanji_id, 'character': char, 'svg': svg,
#             'svg_paths': self._parse_svg_paths(svg),
#             'flashcard_base64': self._extract_flashcard(soup, char),
#             'mnemonic': self._extract_mnemonic(soup),
#             'readings': self._extract_readings(soup),
#             'examples': self._extract_examples(soup),
#             'jlpt_level': 'N5'
#         }

#     def scrape_all(self):
#         print("🎌 JLPT N5 Scraper v2.0 Starting...")
#         links = self.get_all_kanji_links()
#         if not links:
#             print("💀 No links found. Site structure might have changed.")
#             return

#         for idx, (char, url) in enumerate(links, 1):
#             print(f"[{idx}/{len(links)}] Scraping: {char}")
#             data = self.scrape_kanji_detail(url, idx)
#             if data: self.kanji_data.append(data)
#             self._smart_delay(3.0, 6.0)

#         with open('n5_kanji_data.json', 'w', encoding='utf-8') as f:
#             json.dump(self.kanji_data, f, ensure_ascii=False, indent=2)
#         print(f"🎉 Done! Saved {len(self.kanji_data)} kanji.")

# def main():
#     print("🎌 Starting JLPT N5 Kanji Scraper...")
#     confirm = input("Continue? (yes/no): ")
#     if confirm.lower() == 'yes':
#         scraper = StealthScraper()
#         scraper.scrape_all()

# if __name__ == "__main__":
#     main()