"""
JLPT HIGH-FIDELITY UNIVERSAL SCRAPER - MASTER VERSION
- Recursive Pagination (scrapes all pages)
- Direct SVG Injection
- Flashcard/Mnemonic Image Support
- Style-Preserving HTML Examples (Red/Bold/Underlined)
- Automatic Integrity Verification
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import sys
import os
import random
from datetime import datetime
from urllib.parse import urljoin

class JLPTMasterScraper:
    def __init__(self, level='n5', rate_limit=5.0):
        self.level = level.lower()
        self.base_url = f"https://jlptsensei.com/jlpt-{self.level}-kanji-list/"
        self.filename = f'jlpt_{self.level}_complete.json'
        self.checkpoint_file = f'jlpt_{self.level}_checkpoint.json'
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': self.base_url,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        self.rate_limit = rate_limit
        self.kanji_data = self._load_checkpoint()
        self.errors = []
        self.skipped_urls = []
        
    def _load_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return []
        return []

    def _save_checkpoint(self):
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(self.kanji_data, f, ensure_ascii=False, indent=2)

    def get_all_kanji_urls(self):
        """Recursively fetch all kanji detail URLs across all pages"""
        print(f"🔍 Starting Recursive Search for {self.level.upper()} Kanji...")
        all_urls = []
        current_page_url = self.base_url
        page_num = 1
        
        while current_page_url:
            print(f"   📑 Scanning Page {page_num}...")
            try:
                response = self.session.get(current_page_url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                print(f"      Debugging: Page Title is '{soup.title.string.strip() if soup.title else 'No Title'}'")
                
                # Extract URLs from the table
                page_urls = []
                kanji_links = soup.select('a[href*="/learn-japanese-kanji/"]')
                for link in kanji_links:
                    href = link['href']
                    if not href.endswith('/feed/') and '#' not in href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in all_urls:
                            page_urls.append(full_url)
                
                all_urls.extend(page_urls)
                print(f"      ✅ Found {len(page_urls)} new kanji on this page.")
                
                next_btn = soup.select_one('a.next.page-numbers')
                if next_btn and next_btn.get('href'):
                    current_page_url = next_btn['href']
                    page_num += 1
                    time.sleep(self.rate_limit)
                else:
                    current_page_url = None
                    
            except Exception as e:
                print(f"   ❌ Error scanning page {page_num}: {e}")
                break
                
        all_urls = list(dict.fromkeys(all_urls))
        print(f"✨ TOTAL UNIQUE KANJI FOUND: {len(all_urls)}")
        return all_urls

    def _extract_char(self, soup):
        regex = r'[\u4e00-\u9fff]'
        
        # 1. Broaden selectors
        selectors = ['.kanji-character', '.kanji-large', 'h1.entry-title', '.kanji-heading', '.main-kanji']
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                match = re.search(regex, el.get_text())
                if match: return match.group(0)
        
        # 2. Check Page Title (highly reliable fallback)
        if soup.title and soup.title.string:
            # Matches formats like "JLPT N5 Kanji: 日 (nichi)" or "Learn Kanji 日"
            match = re.search(regex, soup.title.string)
            if match: 
                print(f"      ⚠️ Extracted char '{match.group(0)}' from title (Classes failed)")
                return match.group(0)
        
        # 3. Check all headers
        for h in soup.find_all(['h1', 'h2']):
            match = re.search(regex, h.get_text())
            if match:
                return match.group(0)
            
        return None

    def scrape_kanji_detail(self, url, retries=3):
        """High-Fidelity Extraction with Retry and CAPTCHA detection"""
        # Check if already scraped
        for k in self.kanji_data:
            if k['page_url'] == url:
                return k

        for attempt in range(retries + 1):
            try:
                # Dynamic wait: increase wait on later attempts
                wait_time = self.rate_limit + (attempt * 15) + random.uniform(3, 8)
                time.sleep(wait_time)
                
                response = self.session.get(url, timeout=30)
                
                # Handle blocking status codes explicitly
                if response.status_code in [403, 429, 503]:
                    print(f"      ⚠️ Server blocking ({response.status_code}). Rotating UA & Waiting...")
                    self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
                    time.sleep(60 * (attempt + 1))
                    continue
                
                response.raise_for_status()
                
                # Content-based blocking detection
                if "sgcaptcha" in response.text or "unusual traffic" in response.text.lower() or "challenge-platform" in response.text:
                    wait_sec = 300 * (attempt + 1)
                    print(f"      ⚠️ CAPTCHA detected for {url}. Attempt {attempt+1}/{retries+1}. Rotating UA & Waiting {wait_sec}s...")
                    self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
                    time.sleep(wait_sec)
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                char = self._extract_char(soup)
                
                # Ultimate fallback: try to extract from URL (both encoded and raw)
                if not char:
                    try:
                        from urllib.parse import unquote
                        decoded_url = unquote(url)
                        regex_kanji = r'[\u4e00-\u9fff]'
                        
                        # Look for kanji in the last segment of the URL
                        # e.g. /learn-japanese-kanji/日-nichi.../
                        match = re.search(regex_kanji, decoded_url)
                        if match:
                            char = match.group(0)
                            print(f"      ⚠️ Extracted char '{char}' from URL (HTML failed)")
                    except Exception as e:
                        print(f"      ⚠️ URL extraction failed: {e}")

                if not char:
                    if attempt < retries:
                        print(f"      ⚠️ No char found, retrying... ({url})")
                        continue
                    with open("debug_fail.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print(f"      ❌ Character extraction failed. Saved to debug_fail.html")
                    return None
                
                data = {
                    'character': char,
                    'meaning': self._extract_meaning_robust(soup),
                    'flashcard_url': self._extract_flashcard(soup),
                    'stroke_diagram': self._extract_svg(soup),
                    'stroke_count': self._extract_strokes(soup),
                    'readings': self._extract_readings_advanced(soup),
                    'examples': self._extract_styled_examples(soup),
                    'jlpt_level': self.level,
                    'page_url': url
                }
                return data
                
            except Exception as e:
                if attempt < retries:
                    time.sleep(20)
                    continue
                self.errors.append(f"Detail fail ({url}): {e}")
                print(f"      ❌ Detail fail ({url}): {e}") # Keep print for final attempt failure
                return None

    def _extract_meaning_robust(self, soup):
        # 1. Try specific label
        m_label = soup.find(string=re.compile(r'Meaning:'))
        if m_label:
            txt = m_label.parent.get_text()
            m = re.search(r'Meaning:\s*(.*)', txt)
            if m: return m.group(1).strip()

        # 2. Try meta description
        meta = soup.find('meta', {'name': 'description'})
        if meta and "Meaning:" in meta['content']:
            m = re.search(r'Meaning:\s*(.*?)(?:\.|$)', meta['content'])
            if m: return m.group(1).strip()
        
        # 3. Try H2 with "Meaning"
        for h in soup.find_all(['h2', 'h3']):
            if "meaning" in h.get_text().lower():
                # Some are in the text node after the header
                next_sib = h.next_sibling
                while next_sib and not next_sib.get_text(strip=True):
                    next_sib = next_sib.next_sibling
                if next_sib: return next_sib.get_text(strip=True)
        
        return "Meaning not found"

    def _extract_flashcard(self, soup):
        img = soup.select_one('img[src*="mnemonic"], img[src*="flashcard"], .kanji-image img, img.img-responsive')
        if img: return img.get('src')
        return None

    def _extract_svg(self, soup):
        svg = soup.find('svg')
        if svg: return str(svg)
        return ""

    def _extract_strokes(self, soup):
        m = re.search(r'Stroke Count:\s*(\d+)', soup.get_text())
        return int(m.group(1)) if m else 0

    def _extract_readings_advanced(self, soup):
        readings = {'onyomi': [], 'kunyomi': [], 'special': []}
        div = soup.find('div', id=re.compile(r'related-words|readings'))
        if not div: div = soup # Fallback to whole soup
        
        current_type = None
        for p in div.find_all(['p', 'h4', 'li']):
            txt = p.get_text()
            if 'Onyomi' in txt: current_type = 'onyomi'
            elif 'Kunyomi' in txt: current_type = 'kunyomi'
            elif 'Special' in txt: current_type = 'special'
            elif current_type and '【' in txt:
                m = re.search(r'(.*?)【(.*?)】(.*)', txt)
                if m:
                    readings[current_type].append({
                        'word': m.group(1).strip(),
                        'reading': m.group(2).strip(),
                        'meaning': m.group(3).strip()
                    })
        return readings

    def _extract_styled_examples(self, soup):
        examples = []
        for cont in soup.find_all('div', class_=re.compile(r'example|sentence')):
            try:
                jp_p = cont.select_one('p.jp, .japanese-text')
                if not jp_p: continue
                jap_html = str(jp_p)
                en = cont.select_one('.english, .translation, p:nth-of-type(2)')
                examples.append({
                    'japanese_html': jap_html,
                    'english': en.get_text(strip=True) if en else ""
                })
            except: continue
        return examples

    def verify_integrity(self):
        print("\n🛡️ Running Integrity Check...")
        passed = 0
        for k in self.kanji_data:
            has_svg = len(k['stroke_diagram']) > 10
            has_img = k['flashcard_url'] is not None
            if has_svg and has_img: passed += 1
            else:
                self.skipped_urls.append(k['page_url'])
        print(f"📊 Integrity Score: {passed}/{len(self.kanji_data)}")

    def run(self, max_kanji=None):
        print(f"🚀 Starting High-Fidelity Scrape for {self.level.upper()}")
        urls = self.get_all_kanji_urls()
        if max_kanji: urls = urls[:max_kanji]
        
        for i, url in enumerate(urls, 1):
            # Check if already in data
            if any(k['page_url'] == url for k in self.kanji_data):
                print(f"   [{i}/{len(urls)}] Skipping (Already Scraped)...")
                continue

            print(f"   [{i}/{len(urls)}] Processing...")
            data = self.scrape_kanji_detail(url)
            if data:
                data['id'] = len(self.kanji_data) + 1
                self.kanji_data.append(data)
                self._save_checkpoint()
            else:
                self.skipped_urls.append(url)
        
        self.verify_integrity()
        self._save()
        
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)

        if self.errors:
            print(f"\n❌ Total Errors: {len(self.errors)}")
        if self.skipped_urls:
            print(f"\n⚠️ Skipped/Incomplete URLs ({len(self.skipped_urls)}):")
            for u in list(set(self.skipped_urls))[:10]:
                print(f"   - {u}")

    def _save(self):
        filename = f'jlpt_{self.level}_complete.json'
        output = {
            'metadata': {
                'jlpt_level': self.level.upper(),
                'scraped_at': datetime.now().isoformat(),
                'count': len(self.kanji_data)
            },
            'kanji': self.kanji_data
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"✅ Master file saved as: {filename}")

if __name__ == '__main__':
    lvl = input("Enter JLPT Level (n1-n2-n3-n4-n5): ") or 'n5'
    limit = input("Limit kanji count (press enter for all): ")
    limit = int(limit) if limit else None
    
    scraper = JLPTMasterScraper(level=lvl)
    scraper.run(max_kanji=limit)
