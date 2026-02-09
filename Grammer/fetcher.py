#!/usr/bin/env python3
"""
Missing Data Filler Script
This script checks an HTML file for missing "How to Use" data and fetches it from source URLs.

Usage:
    python fill_missing_data.py <input_html_file> <output_html_file>

Example:
    python fill_missing_data.py N5-G-Table-Enhanced.html N5-G-Table-Complete.html
"""

import sys
import time
import re
from bs4 import BeautifulSoup
import urllib.request
import urllib.error


def fetch_usage_table_from_url(url, delay=2):
    """
    Fetch the usage table from a JLPT Sensei URL.
    
    Args:
        url: The URL to fetch from
        delay: Delay in seconds before fetching (to be nice to the server)
        
    Returns:
        HTML string of the usage table, or None if not found
    """
    try:
        print(f"    ⏳ Waiting {delay} seconds before fetching...")
        time.sleep(delay)
        
        print(f"    🌐 Fetching from: {url}")
        
        # Add headers to avoid being blocked
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for usage table - try multiple selectors
        usage_table = None
        
        # Method 1: Look for table with class "usage"
        usage_table = soup.find('table', class_='usage')
        
        if not usage_table:
            # Method 2: Look for table with class "table-bordered" that contains usage info
            tables = soup.find_all('table', class_='table-bordered')
            for table in tables:
                # Check if this table looks like a usage table
                text = table.get_text().lower()
                if any(keyword in text for keyword in ['verb', 'noun', 'adjective', 'formation', '形', 'verbて', 'verbた']):
                    usage_table = table
                    break
        
        if not usage_table:
            # Method 3: Look in specific div sections
            grammar_section = soup.find('div', class_='entry-content')
            if grammar_section:
                tables = grammar_section.find_all('table')
                if tables:
                    usage_table = tables[0]  # Take the first table in content
        
        if usage_table:
            print(f"    ✅ Found usage table!")
            return str(usage_table)
        else:
            print(f"    ❌ No usage table found on page")
            return None
            
    except urllib.error.HTTPError as e:
        print(f"    ❌ HTTP Error {e.code}: {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"    ❌ URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"    ❌ Error fetching URL: {e}")
        return None


def is_data_missing(cell_content):
    """
    Check if the "How to Use" cell has missing or minimal data.
    
    Args:
        cell_content: BeautifulSoup element of the cell
        
    Returns:
        Boolean indicating if data is missing
    """
    # Get text content
    text = cell_content.get_text(strip=True)
    
    # Check for indicators of missing data
    if '(no usage table)' in text:
        return True
    
    # Check if content is too short (less than 20 characters, excluding button text)
    # Remove button text
    text_without_button = text.replace('▼ Hide', '').replace('▶ Show', '').strip()
    
    if len(text_without_button) < 20:
        return True
    
    # Check if there's no actual table
    tables = cell_content.find_all('table')
    if not tables:
        # No table found, might be missing
        return True
    
    return False


def extract_source_url(cell_content):
    """
    Extract the source URL from the "How to Use" cell.
    
    Args:
        cell_content: BeautifulSoup element of the cell
        
    Returns:
        URL string or None
    """
    # Look for source link
    link = cell_content.find('a', class_='source-link')
    if link and link.has_attr('href'):
        return link['href']
    
    # Look for any jlptsensei link
    all_links = cell_content.find_all('a', href=True)
    for link in all_links:
        if 'jlptsensei.com' in link['href']:
            return link['href']
    
    return None


def add_highlighting_to_usage_table(usage_content):
    """
    Add color highlighting to the usage table to match the example column style.
    
    Args:
        usage_content: HTML string of the usage table
        
    Returns:
        Enhanced HTML string with highlighting
    """
    soup = BeautifulSoup(usage_content, 'html.parser')
    
    # Find all table cells
    cells = soup.find_all('td')
    
    for cell in cells:
        text = cell.get_text()
        
        # Highlight grammar particles and endings
        grammar_patterns = [
            'だ', 'です', 'ます', 'ません', 'ました', 'ませんでした',
            'だった', 'でした', 'じゃない', 'ではない',
            'ちゃだめ', 'ちゃいけない', 'じゃダメ', 'じゃいけない',
            'から', 'ので', 'けど', 'が', 'けれども',
            'たい', 'たがる', 'たら', 'ば',
            'より', 'ほう', 'つもり', 'よう'
        ]
        
        # Wrap grammar patterns with highlighting
        for pattern in grammar_patterns:
            if pattern in text:
                new_html = str(cell)
                new_html = new_html.replace(pattern, f'<span class="hl-grammar">{pattern}</span>')
                cell.replace_with(BeautifulSoup(new_html, 'html.parser'))
                break
    
    return str(soup)


def fill_missing_data(input_file, output_file, delay=2):
    """
    Check for missing "How to Use" data and fill it by fetching from URLs.
    
    Args:
        input_file: Path to input HTML file
        output_file: Path to output HTML file
        delay: Delay between requests in seconds
    """
    print("=" * 70)
    print("Missing Data Filler")
    print("=" * 70)
    print(f"\nReading file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all rows
    tbody = soup.find('tbody')
    if not tbody:
        print("❌ ERROR: Could not find <tbody> in HTML file")
        return False
    
    all_rows = tbody.find_all('tr', recursive=False)
    print(f"Found {len(all_rows)} rows to check\n")
    
    # Statistics
    total_checked = 0
    missing_found = 0
    successfully_filled = 0
    failed_to_fill = 0
    
    # Check each row
    for row_idx, row in enumerate(all_rows, 1):
        cells = row.find_all('td', recursive=False)
        
        if len(cells) < 4:
            continue
        
        # Get row number
        row_number = cells[0].get_text(strip=True)
        
        # Get "How to Use" cell (column 3, index 2)
        how_to_use_cell = cells[2]
        
        total_checked += 1
        
        # Check if data is missing
        if is_data_missing(how_to_use_cell):
            missing_found += 1
            print(f"Row {row_number}: Missing 'How to Use' data")
            
            # Extract source URL
            source_url = extract_source_url(how_to_use_cell)
            
            if source_url:
                print(f"  📚 Source URL found: {source_url}")
                
                # Fetch the usage table
                fetched_table = fetch_usage_table_from_url(source_url, delay)
                
                if fetched_table:
                    # Add highlighting
                    enhanced_table = add_highlighting_to_usage_table(fetched_table)
                    
                    # Find the content wrapper div
                    content_wrapper = how_to_use_cell.find('div', class_='how-to-use-data-content')
                    
                    if content_wrapper:
                        # Clear old content (except source link)
                        source_link = content_wrapper.find('a', class_='source-link')
                        content_wrapper.clear()
                        
                        # Add new table
                        new_content = BeautifulSoup(enhanced_table, 'html.parser')
                        content_wrapper.append(new_content)
                        
                        # Re-add source link if it existed
                        if source_link:
                            content_wrapper.append(soup.new_tag('br'))
                            content_wrapper.append(source_link)
                        
                        successfully_filled += 1
                        print(f"  ✅ Successfully filled data for row {row_number}")
                    else:
                        print(f"  ⚠️  Could not find content wrapper in cell")
                        failed_to_fill += 1
                else:
                    failed_to_fill += 1
                    print(f"  ❌ Failed to fetch data for row {row_number}")
            else:
                failed_to_fill += 1
                print(f"  ⚠️  No source URL found for row {row_number}")
            
            print()  # Empty line for readability
    
    # Print statistics
    print("=" * 70)
    print("Summary:")
    print("=" * 70)
    print(f"Total rows checked: {total_checked}")
    print(f"Missing data found: {missing_found}")
    print(f"Successfully filled: {successfully_filled}")
    print(f"Failed to fill: {failed_to_fill}")
    print()
    
    # Save the file
    if successfully_filled > 0:
        print(f"💾 Saving updated file to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("✅ File saved successfully!")
        return True
    else:
        print("⚠️  No data was filled. Output file not created.")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python fill_missing_data.py <input_html_file> <output_html_file> [delay]")
        print("\nArguments:")
        print("  input_html_file   : HTML file to check for missing data")
        print("  output_html_file  : Output file with filled data")
        print("  delay (optional)  : Delay between requests in seconds (default: 2)")
        print("\nExample:")
        print("  python fill_missing_data.py N5-G-Table-Enhanced.html N5-G-Table-Complete.html")
        print("  python fill_missing_data.py N5-G-Table-Enhanced.html N5-G-Table-Complete.html 3")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    delay = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    print(f"\nSettings:")
    print(f"  Input file: {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Delay between requests: {delay} seconds")
    print()
    
    success = fill_missing_data(input_file, output_file, delay)
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! All missing data has been filled.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("⚠️  Process completed with warnings. Check the log above.")
        print("=" * 70)


if __name__ == "__main__":
    main()