# import requests
# from bs4 import BeautifulSoup
# import time
# import csv
# import os
# import re
# from html import escape

# # ------------- CONFIGURATION -------------
# # You can change this URL for other levels (N2, N1, etc.)
# START_URL = "https://jlptsensei.com/jlpt-n2-grammar-list/"
# OUTPUT_CSV = "results_merged.csv"
# OUTPUT_HTML = "results_merged.html"
# DELAY = 1.2  # Polite delay to prevent being blocked
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
# }
# # ----------------------------------------

# def fetch_url(url):
#     """Utility to fetch HTML content from a URL."""
#     try:
#         r = requests.get(url, headers=HEADERS, timeout=15)
#         r.raise_for_status()
#         return r.text
#     except Exception as e:
#         print(f"[ERROR] Failed to fetch {url}: {e}")
#         return None

# def get_already_scraped():
#     """Reads the CSV to see which URLs have already been processed for resuming."""
#     if not os.path.exists(OUTPUT_CSV):
#         return []
#     with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         return [row["source"] for row in reader if "source" in row]

# def extract_links_from_index(html_text):
#     """Parses the master list page for grammar entries."""
#     soup = BeautifulSoup(html_text, "lxml")
#     rows = soup.select("table#jl-grammar tbody tr.jl-row")
#     entries = []
#     for r in rows:
#         td_gr = r.select_one("td.jl-td-gr")
#         a = td_gr.find("a") if td_gr else None
        
#         if a and a.get("href"):
#             href = a["href"].strip()
#             name_en = a.get_text(strip=True)
            
#             a_jp = r.select_one("td.jl-td-gj a.jp")
#             name_jp = a_jp.get_text(strip=True) if a_jp else ""
            
#             meaning_td = r.select_one("td.jl-td-gm")
#             list_meaning = meaning_td.get_text(strip=True) if meaning_td else ""

#             entries.append({
#                 "href": href,
#                 "name_en": name_en,
#                 "name_jp": name_jp,
#                 "list_meaning": list_meaning
#             })
#     return entries

# def sanitize_multiline(text):
#     if not text: return ""
#     return re.sub(r'\s+', ' ', text).strip()

# def extract_detail(html_text, entry):
#     """Extracts the deep details from a specific grammar page."""
#     soup = BeautifulSoup(html_text, "lxml")
    
#     # Extract Meaning
#     meta = soup.find("meta", property="og:description")
#     meaning = meta["content"].strip() if meta and meta.get("content") else entry["list_meaning"]

#     # Extract Usage Table
#     usage_table = soup.find("table", class_=re.compile(r"\busage\b"))
#     usage_html = str(usage_table) if usage_table else "<em>(no usage table)</em>"

#     # Extract Examples
#     ex1 = soup.find(id="example_1")
#     ex2 = soup.find(id="example_2")
    
#     return {
#         "grammar_name_en": entry["name_en"],
#         "grammar_name_jp": entry["name_jp"],
#         "meaning": sanitize_multiline(meaning),
#         "how_to_use_html": usage_html,
#         "example_1": sanitize_multiline(ex1.get_text(strip=True)) if ex1 else "",
#         "example_2": sanitize_multiline(ex2.get_text(strip=True)) if ex2 else "",
#         "source": entry["href"]
#     }

# def main():
#     print(f"🚀 Starting dynamic scrape from: {START_URL}")
#     index_html = fetch_url(START_URL)
#     if not index_html: return

#     entries = extract_links_from_index(index_html)
#     already_done = get_already_scraped()
    
#     print(f"📊 Found {len(entries)} items. {len(already_done)} already completed.")

#     # Open CSV in append mode for Resuming
#     file_exists = os.path.exists(OUTPUT_CSV)
#     with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
#         fieldnames = ["grammar_name_en", "grammar_name_jp", "meaning", "how_to_use_html", "example_1", "example_2", "source"]
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         if not file_exists: writer.writeheader()

#         for i, entry in enumerate(entries, 1):
#             if entry["href"] in already_done:
#                 continue
            
#             print(f"[{i}/{len(entries)}] Scrapping: {entry['name_en']}")
#             detail_html = fetch_url(entry["href"])
            
#             if detail_html:
#                 data = extract_detail(detail_html, entry)
#                 writer.writerow(data)
#                 f.flush() # Save to disk immediately
            
#             time.sleep(DELAY)

#     # Generate the final HTML report (matches N3_Grammer.html format)
#     generate_html_report()

# def generate_html_report():
#     """Reads the final CSV and builds the formatted HTML file."""
#     if not os.path.exists(OUTPUT_CSV): return
    
#     rows = []
#     with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
#         reader = list(csv.DictReader(f))
#         for idx, r in enumerate(reader, 1):
#             ex_combined = "<br><br>".join(filter(None, [escape(r["example_1"]), escape(r["example_2"])]))
#             rows.append(f"""
#         <tr>
#         <td><b>{idx}</b></td>
#         <td>{escape(r['grammar_name_en'])}<br><small>{escape(r['grammar_name_jp'])}</small></td>
#         <td>{escape(r['meaning'])}</td>
#         <td>{r['how_to_use_html']}</td>
#         <td>{ex_combined}<br><small><a href="{escape(r['source'])}" target="_blank">source</a></small></td>
#         </tr>""")

#     html_content = f"""<!DOCTYPE html>
#     <html><head><meta charset="utf-8"><title>Grammar Merge Results</title>
#     <style>table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;vertical-align:top}}th{{background:#f5f5f5}}</style>
#     </head><body>
#     <h1>JLPT Grammar Merged Results</h1>
#     <p>Total: {len(rows)}</p>
#     <table><thead><tr><th>Number</th><th>Grammar</th><th>Meaning</th><th>How to Use</th><th>Examples</th></tr></thead><tbody>
#     {"".join(rows)}
#     </tbody></table></body></html>"""

#     with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
#         f.write(html_content)
#     print(f"✨ Successfully generated: {OUTPUT_HTML}")

# if __name__ == "__main__":
#     main()

import requests
from bs4 import BeautifulSoup
import time
import csv
import os
import re
from html import escape

# ------------- CONFIGURATION -------------
START_URL = "https://jlptsensei.com/jlpt-n5-grammar-list/"
OUTPUT_CSV = "N5-Grammar.csv"
OUTPUT_HTML = "N5-Grammar.html"
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

def get_already_scraped():
    if not os.path.exists(OUTPUT_CSV):
        return set()
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["source"] for row in reader if "source" in row}

def extract_entries_and_next_page(html_text):
    """Extracts grammar links and finds the 'Next' page URL."""
    soup = BeautifulSoup(html_text, "lxml")
    
    # 1. Get Grammar Links
    entries = []
    rows = soup.select("table#jl-grammar tbody tr.jl-row")
    for r in rows:
        td_gr = r.select_one("td.jl-td-gr")
        a = td_gr.find("a") if td_gr else None
        if a and a.get("href"):
            entries.append({
                "href": a["href"].strip(),
                "name_en": a.get_text(strip=True),
                "name_jp": r.select_one("td.jl-td-gj a.jp").get_text(strip=True) if r.select_one("td.jl-td-gj a.jp") else "",
                "list_meaning": r.select_one("td.jl-td-gm").get_text(strip=True) if r.select_one("td.jl-td-gm") else ""
            })
    
    # 2. Find Next Page Link
    next_tag = soup.select_one("a.next.page-numbers")
    next_url = next_tag["href"] if next_tag else None
    
    return entries, next_url

def extract_detail(html_text, entry):
    soup = BeautifulSoup(html_text, "lxml")
    meta = soup.find("meta", property="og:description")
    meaning = meta["content"].strip() if meta and meta.get("content") else entry["list_meaning"]
    usage_table = soup.find("table", class_=re.compile(r"\busage\b"))
    usage_html = str(usage_table) if usage_table else "<em>(no usage table)</em>"
    ex1 = soup.find(id="example_1")
    ex2 = soup.find(id="example_2")
    
    return {
        "grammar_name_en": entry["name_en"],
        "grammar_name_jp": entry["name_jp"],
        "meaning": re.sub(r'\s+', ' ', meaning).strip(),
        "how_to_use_html": usage_html,
        "example_1": ex1.get_text(strip=True) if ex1 else "",
        "example_2": ex2.get_text(strip=True) if ex2 else "",
        "source": entry["href"]
    }

def main():
    all_entries = []
    current_url = START_URL
    
    print("🔍 Gathering all grammar links across pages...")
    while current_url:
        print(f"  Parsing list: {current_url}")
        html = fetch_url(current_url)
        if not html: break
        
        entries, next_url = extract_entries_and_next_page(html)
        all_entries.extend(entries)
        current_url = next_url
        if current_url: time.sleep(DELAY)

    already_done = get_already_scraped()
    print(f"📊 Total items found: {len(all_entries)}. Already done: {len(already_done)}")

    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["grammar_name_en", "grammar_name_jp", "meaning", "how_to_use_html", "example_1", "example_2", "source"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists: writer.writeheader()

        for i, entry in enumerate(all_entries, 1):
            if entry["href"] in already_done: continue
            
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
            ex_combined = "<br><br>".join(filter(None, [escape(r["example_1"]), escape(r["example_2"])]))
            rows.append(f"<tr><td><b>{idx}</b></td><td>{escape(r['grammar_name_en'])}<br><small>{escape(r['grammar_name_jp'])}</small></td><td>{escape(r['meaning'])}</td><td>{r['how_to_use_html']}</td><td>{ex_combined}<br><small><a href='{escape(r['source'])}' target='_blank'>source</a></small></td></tr>")

    html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;vertical-align:top}}th{{background:#f5f5f5}}</style></head><body><h1>JLPT Grammar Results</h1><p>Total: {len(rows)}</p><table><thead><tr><th>Number</th><th>Grammar</th><th>Meaning</th><th>How to Use</th><th>Examples</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f: f.write(html_content)
    print(f"✨ Report generated: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()