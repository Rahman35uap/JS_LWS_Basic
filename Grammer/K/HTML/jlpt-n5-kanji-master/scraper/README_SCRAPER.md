# 🕷️ JLPT N5 Kanji Scraper - Instructions

## Overview

This scraper extracts all 80 JLPT N5 kanji from jlptsensei.com with advanced anti-detection measures.

## Features

✅ **Anti-Bot Protection**
- Rotating user agents
- Random human-like delays (2-6 seconds)
- Browser-realistic headers
- Automatic retry with backoff
- Block detection & recovery

✅ **Data Extracted**
- Kanji character
- SVG stroke diagrams
- Flashcard images (base64 encoded)
- Onyomi/Kunyomi/Special readings
- Example sentences (with HTML formatting)
- Mnemonics (if available)
- Stroke count & radical info

## Prerequisites

### 1. Install Python 3.8+

Check your version:
```bash
python3 --version
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install beautifulsoup4 requests Pillow lxml
```

## How to Run

### Option 1: Full Scrape (All 80 Kanji)

```bash
python3 scrape_jlpt_n5_enhanced.py
```

**Expected Duration**: 20-40 minutes
**Output**: `kanji_data_enhanced.json` and `kanji_data_enhanced.min.json`

### Option 2: Test Mode (Recommended First)

Edit the script and modify line ~350:
```python
# Change this:
kanji_links = kanji_links[:80]  

# To this (for testing):
kanji_links = kanji_links[:3]  # Only scrape 3 kanji
```

Then run:
```bash
python3 scrape_jlpt_n5_enhanced.py
```

## Understanding the Output

### Console Output

```
🎌 JLPT N5 Kanji Enhanced Scraper v2.0
============================================================
⏰ Started at: 2026-02-06 15:30:00

📡 Step 1: Fetching main kanji list page...
⏳ Waiting 3.2s... (human-like behavior)
✅ Found 80 kanji to scrape

📥 Step 2: Scraping individual kanji pages...

============================================================
[1/80] Scraping: 日
URL: https://jlptsensei.com/learn-japanese-kanji/...
============================================================
  📝 Character: 日
  🖼️  SVG: ✓
  🎴 Flashcard: ✓
  💭 Mnemonic: ✓
  📖 Readings: On=19, Kun=2, Sp=3
  📚 Examples: 6
✅ Successfully scraped 日

⏳ Waiting 4.7s... (human-like behavior)
...
```

### Output Files

**1. kanji_data_enhanced.json** (Readable, ~5-10MB)
```json
{
  "metadata": {
    "scrape_date": "2026-02-06T15:30:00",
    "total_kanji": 80,
    "version": "2.0"
  },
  "kanji": [...]
}
```

**2. kanji_data_enhanced.min.json** (Minified, ~3-8MB)
- Same content, no whitespace
- Use this for the final app

## Troubleshooting

### Issue: "Connection refused" or 403 errors

**Solution**: You may be rate-limited.
1. Stop the scraper
2. Wait 5-10 minutes
3. Increase delays in code:
   ```python
   self._smart_delay(5.0, 10.0)  # Longer delays
   ```

### Issue: Missing flashcard images

**Cause**: Some images may fail to download (network issues)

**Solution**: The scraper tracks failed images and continues. Check:
```
⚠️ Failed images: 3
   月, 火, 水
```

You can re-run the scraper later to retry.

### Issue: Script crashes mid-scrape

**Solution**: The scraper saves progress. You can:
1. Check what's in `kanji_data_enhanced.json`
2. Modify the script to skip already-scraped kanji
3. Or just re-run (it will overwrite)

### Issue: "Detected possible block"

**Output**:
```
⚠️ Detected possible block, waiting longer...
```

**Action**: The scraper will wait 60 seconds automatically. Be patient!

## Advanced Configuration

### Modify Delays

Edit `scrape_jlpt_n5_enhanced.py`:

```python
# Line ~75
def _smart_delay(self, min_delay=2.0, max_delay=5.0):
    # Change to:
    delay = random.uniform(5.0, 10.0)  # More conservative
```

### Change User Agents

Edit the `user_agents` list (line ~20):

```python
self.user_agents = [
    'Your custom user agent here',
    # ... add more
]
```

### Skip Certain Kanji

Before running, edit the kanji list:

```python
# After getting all links:
excluded = ['一', '二', '三']  # Kanji to skip
kanji_links = [(c, u) for c, u in kanji_links if c not in excluded]
```

## Data Validation

After scraping completes, check:

```bash
# Count kanji in output
grep -c '"id":' kanji_data_enhanced.json

# Check file size
ls -lh kanji_data_enhanced.json
```

Expected:
- **Count**: 80 kanji
- **Size**: 5-10MB (readable), 3-8MB (minified)

## What to Do With the Data

Once you have `kanji_data_enhanced.json`:

1. ✅ Move it to `../data/` folder
2. ✅ Proceed to Phase 2 (Building the HTML app)
3. ✅ Run `build_final_app.py` to generate the single-file app

## Ethical Considerations

⚠️ **This scraper is for educational purposes only**

- Respects robots.txt
- Uses polite delays (2-6 seconds minimum)
- Does not overwhelm the server
- Attributes data source in final app
- No redistribution of scraped data

## Support

If you encounter issues:

1. Check the error message carefully
2. Try reducing the number of kanji (test mode)
3. Increase delays
4. Check your internet connection
5. Verify the website structure hasn't changed

## Next Steps

After successful scraping:

```bash
# Verify data
python3 -m json.tool kanji_data_enhanced.json > /dev/null && echo "Valid JSON ✓"

# Move to next phase
cd ../builder
python3 build_final_app.py
```

---

**Happy Scraping! 🎌**