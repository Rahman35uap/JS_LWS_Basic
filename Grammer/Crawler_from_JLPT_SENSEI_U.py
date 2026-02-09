import requests
from bs4 import BeautifulSoup
import time
import csv
import os
import re
from html import escape

# ------------- CONFIGURATION -------------
# Change this to N3 Vocabulary, N3 Kanji, or any other JLPT list URL
TARGET_URL = "https://jlptsensei.com/jlpt-n5-kanji-list/" 
OUTPUT_CSV = "N5_JS_K.csv"
OUTPUT_HTML = "N5_JS_K.html"
DELAY = 1.2 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}
# ----------------------------------------

def fetch_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return None

def extract_entries_and_next_page(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    entries = []
    
    # Try different table IDs used by the site for Grammar, Vocab, and Kanji
    table = soup.find("table", id=re.compile(r"jl-(grammar|vocab|kanji)"))
    if table:
        rows = table.select("tbody tr")
        for r in rows:
            # Finding the main link and title
            a_tag = r.find("a", href=True)
            if not a_tag: continue
            
            # The structure varies slightly, so we grab the row's text for meaning
            cells = [c.get_text(strip=True) for c in r.find_all("td")]
            
            entries.append({
                "href": a_tag["href"].strip(),
                "name_en": a_tag.get_text(strip=True),
                "list_meaning": cells[-1] if cells else "", # Usually the last column
                "raw_cells": cells # Keep for backup
            })
    
    next_tag = soup.select_one("a.next.page-numbers")
    next_url = next_tag["href"] if next_tag else None
    return entries, next_url

def extract_detail(html_text, entry):
    soup = BeautifulSoup(html_text, "lxml")
    
    # 1. Meaning (from Meta or specific class)
    meta = soup.find("meta", property="og:description")
    meaning = meta["content"].strip() if meta and meta.get("content") else entry["list_meaning"]

    # 2. Usage / Info Table (How to use for grammar, or stroke/onyomi for Kanji)
    info_table = soup.find("table", class_=re.compile(r"(usage|table-bordered)"))
    info_html = str(info_table) if info_table else "<em>(No detailed table found)</em>"

    # 3. Examples (Universal ID search)
    ex1 = soup.find(id="example_1") or soup.find("div", class_="example-main")
    ex2 = soup.find(id="example_2")
    
    return {
        "name": entry["name_en"],
        "meaning": re.sub(r'\s+', ' ', meaning).strip(),
        "info_html": info_html,
        "ex1": ex1.get_text(strip=True) if ex1 else "",
        "ex2": ex2.get_text(strip=True) if ex2 else "",
        "source": entry["href"]
    }

def main():
    all_entries = []
    current_url = TARGET_URL
    
    print(f"🔍 Crawling List: {current_url}")
    while current_url:
        html = fetch_url(current_url)
        if not html: break
        entries, next_url = extract_entries_and_next_page(html)
        all_entries.extend(entries)
        print(f"  Found {len(entries)} items on this page...")
        current_url = next_url
        if current_url: time.sleep(DELAY)

    # Resume Check
    processed_urls = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            processed_urls = {row["source"] for row in reader if "source" in row}

    print(f"📊 Total items found: {len(all_entries)}. Already done: {len(processed_urls)}")

    # Write Results
    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "meaning", "info_html", "ex1", "ex2", "source"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists: writer.writeheader()

        for i, entry in enumerate(all_entries, 1):
            if entry["href"] in processed_urls: continue
            
            print(f"[{i}/{len(all_entries)}] Scrapping: {entry['name_en']}")
            detail_html = fetch_url(entry["href"])
            if detail_html:
                writer.writerow(extract_detail(detail_html, entry))
                f.flush()
            time.sleep(DELAY)

    generate_html_report()

def generate_html_report():
    if not os.path.exists(OUTPUT_CSV): return
    rows = []
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        for idx, r in enumerate(reader, 1):
            ex_combined = "<br><br>".join(filter(None, [escape(r["ex1"]), escape(r["ex2"])]))
            rows.append(f"""
        <tr>
            <td><b>{idx}</b></td>
            <td>{escape(r['name'])}</td>
            <td>{escape(r['meaning'])}</td>
            <td>{r['info_html']}</td>
            <td>{ex_combined}<br><small><a href='{escape(r['source'])}' target='_blank'>source</a></small></td>
        </tr>""")

    html_content = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
    <style>table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;vertical-align:top}}th{{background:#f5f5f5}}</style>
    </head><body><h1>JLPT Scrape Results</h1><p>Total: {len(rows)}</p>
    <table><thead><tr><th>No.</th><th>Item</th><th>Meaning</th><th>Details</th><th>Examples</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table></body></html>"""
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f: f.write(html_content)
    print(f"✨ Report generated: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()