from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

def parse_book_page(html):
    """
    Parses the HTML and extracts kanji data from JLPT Sensei kanji list pages.
    """
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    results = []

    # Find the kanji table
    table = soup.find('table')
    if not table:
        logger.warning("No table found on page")
        return []

    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
    else:
        rows = table.find_all('tr')

    # Skip header row if present
    start_idx = 0
    if rows:
        first_row_text = rows[0].get_text()
        if 'kanji' in first_row_text.lower() or 'onyomi' in first_row_text.lower():
            start_idx = 1

    for row in rows[start_idx:]:
        try:
            # Get all text from the row
            row_text = row.get_text(separator=' ', strip=True)
            
            # Pattern to match: number, kanji character, onyomi, kunyomi, meaning
            # Example: "1 日 nichi, jitsu ひ, -び, -か day, sun, Japan"
            # Try to extract structured data
            cells = row.find_all(['td', 'th'])
            
            if not cells:
                continue
            
            # Get full text and try to parse
            full_text = ' '.join([cell.get_text(strip=True) for cell in cells])
            
            # Pattern: number (optional), kanji, readings, meaning
            # Look for kanji character (Japanese/Chinese character)
            kanji_match = re.search(r'([一二三四五六七八九十\d]+)?([\u4e00-\u9faf]+)', full_text)
            if not kanji_match:
                continue
            
            # Extract components
            number = kanji_match.group(1) if kanji_match else None
            kanji = kanji_match.group(2) if kanji_match else None
            
            # Try to find onyomi and kunyomi (usually after kanji, before meaning)
            # Onyomi: katakana or romaji after kanji
            # Kunyomi: hiragana or romaji
            text_after_kanji = full_text[full_text.find(kanji) + len(kanji):] if kanji else ""
            
            # Simple extraction: split by common patterns
            parts = re.split(r'[,\s]+', text_after_kanji)
            
            # Find meaning (usually English text at the end)
            meaning_parts = []
            readings = []
            for part in parts:
                if part and not re.match(r'^[\u3040-\u309F\u30A0-\u30FF]+$', part):  # Not pure hiragana/katakana
                    if re.search(r'[a-zA-Z]', part):  # Contains English
                        meaning_parts.append(part)
                    elif part:
                        readings.append(part)
            
            meaning = ' '.join(meaning_parts) if meaning_parts else text_after_kanji.split(',')[-1] if text_after_kanji else "N/A"
            
            # Clean up
            kanji = kanji[0] if kanji and len(kanji) > 0 else None
            
            if kanji:
                results.append({
                    'number': number or "N/A",
                    'kanji': kanji,
                    'readings': ', '.join(readings[:3]) if readings else "N/A",  # Limit readings
                    'meaning': meaning[:100] if meaning else "N/A"  # Limit meaning length
                })
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing row: {e}")
            continue

    return results