# #!/usr/bin/env python3
# """
# Grammar Table Merger Script
# This script merges the "How to Use" column from a source HTML file into a target HTML file.

# Usage:
#     python merge_grammar_tables.py <source_file> <target_file> <output_file>

# Example:
#     python merge_grammar_tables.py N5_Grammar.html N5-G-Table.html N5-G-Table-Merged.html
# """

# import sys
# from bs4 import BeautifulSoup


# def extract_how_to_use_data(source_file):
#     """
#     Extract 'How to Use' data from the source HTML file.
    
#     Args:
#         source_file: Path to the source HTML file (N5_Grammar.html format)
        
#     Returns:
#         Dictionary mapping row numbers to 'How to Use' HTML content
#     """
#     print(f"Reading source file: {source_file}")
    
#     with open(source_file, 'r', encoding='utf-8') as f:
#         source_html = f.read()
    
#     source_soup = BeautifulSoup(source_html, 'html.parser')
    
#     # Find all rows in source table
#     source_tbody = source_soup.find('tbody')
#     if not source_tbody:
#         print("ERROR: Could not find <tbody> in source file")
#         return {}
    
#     source_rows = source_tbody.find_all('tr', recursive=False)
#     how_to_use_data = {}
    
#     for row in source_rows:
#         # Get only direct child td elements (not nested ones)
#         cells = row.find_all('td', recursive=False)
        
#         # Source file structure: [Number, Grammar, Meaning, How to Use, Examples]
#         if len(cells) >= 4:
#             number = cells[0].get_text(strip=True)
#             how_to_use_html = str(cells[3])  # Column index 3 is "How to Use"
#             how_to_use_data[number] = how_to_use_html
    
#     print(f"✓ Extracted 'How to Use' data for {len(how_to_use_data)} entries")
#     return how_to_use_data


# def merge_tables(target_file, how_to_use_data, output_file):
#     """
#     Merge 'How to Use' data into the target HTML file.
    
#     Args:
#         target_file: Path to target HTML file (N5-G-Table.html format)
#         how_to_use_data: Dictionary with 'How to Use' content
#         output_file: Path for the merged output file
#     """
#     print(f"\nReading target file: {target_file}")
    
#     with open(target_file, 'r', encoding='utf-8') as f:
#         target_html = f.read()
    
#     target_soup = BeautifulSoup(target_html, 'html.parser')
    
#     # Update the header row
#     print("Updating table header...")
#     thead = target_soup.find('thead')
#     if not thead:
#         print("ERROR: Could not find <thead> in target file")
#         return False
    
#     header_row = thead.find('tr')
#     header_cells = header_row.find_all('th', recursive=False)
    
#     print(f"Original header has {len(header_cells)} columns:")
#     for i, th in enumerate(header_cells):
#         print(f"  Column {i}: {th.get_text(strip=True)}")
    
#     # Create new header for "How to Use"
#     new_header = target_soup.new_tag('th')
#     new_header.string = "How to Use"
    
#     # Insert between column 1 (Grammar Point & Meaning) and column 2 (Examples & Translation)
#     # Target structure should be: [#, Grammar Point & Meaning, How to Use, Examples & Translation]
#     if len(header_cells) >= 3:
#         header_cells[2].insert_before(new_header)
#     else:
#         print("ERROR: Target file doesn't have expected header structure")
#         return False
    
#     print("New header structure:")
#     for i, th in enumerate(header_row.find_all('th', recursive=False)):
#         print(f"  Column {i}: {th.get_text(strip=True)}")
    
#     # Update body rows
#     print("\nUpdating table body rows...")
#     tbody = target_soup.find('tbody')
#     if not tbody:
#         print("ERROR: Could not find <tbody> in target file")
#         return False
    
#     all_rows = tbody.find_all('tr', recursive=False)
#     print(f"Processing {len(all_rows)} rows...")
    
#     success_count = 0
#     missing_count = 0
    
#     for row in all_rows:
#         # Get only direct child td elements (not nested ones in tables)
#         row_cells = row.find_all('td', recursive=False)
        
#         if len(row_cells) < 3:
#             print(f"WARNING: Row has fewer than 3 cells, skipping")
#             continue
        
#         # Get the row number from first cell
#         number = row_cells[0].get_text(strip=True)
        
#         # Create new cell for "How to Use"
#         new_cell = target_soup.new_tag('td')
        
#         if number in how_to_use_data:
#             # Parse the HTML content and add it to the cell
#             content = BeautifulSoup(how_to_use_data[number], 'html.parser')
#             new_cell.append(content)
#             success_count += 1
#         else:
#             new_cell.string = "(no usage table)"
#             missing_count += 1
        
#         # Insert the new cell before the Examples column (index 2)
#         row_cells[2].insert_before(new_cell)
    
#     print(f"✓ Successfully added 'How to Use' data to {success_count} rows")
#     if missing_count > 0:
#         print(f"⚠ {missing_count} rows had no matching 'How to Use' data")
    
#     # Verify the result
#     print("\nVerifying result...")
#     sample_row = all_rows[0]
#     final_cells = sample_row.find_all('td', recursive=False)
#     print(f"Sample row now has {len(final_cells)} cells (expected: 4)")
    
#     # Save the merged file
#     print(f"\nSaving merged file to: {output_file}")
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write(target_soup.prettify())
    
#     print("✓ Merge complete!")
#     return True


# def main():
#     """Main function to handle command-line arguments and run the merge."""
    
#     if len(sys.argv) != 4:
#         print("Usage: python merge_grammar_tables.py <source_file> <target_file> <output_file>")
#         print("\nExample:")
#         print("  python merge_grammar_tables.py N5_Grammar.html N5-G-Table.html N5-G-Table-Merged.html")
#         print("\nDescription:")
#         print("  source_file: HTML file containing the 'How to Use' column to extract")
#         print("  target_file: HTML file where the 'How to Use' column will be inserted")
#         print("  output_file: Path for the merged output file")
#         sys.exit(1)
    
#     source_file = sys.argv[1]
#     target_file = sys.argv[2]
#     output_file = sys.argv[3]
    
#     print("=" * 70)
#     print("Grammar Table Merger")
#     print("=" * 70)
    
#     # Step 1: Extract "How to Use" data from source file
#     how_to_use_data = extract_how_to_use_data(source_file)
    
#     if not how_to_use_data:
#         print("ERROR: No data extracted from source file. Exiting.")
#         sys.exit(1)
    
#     # Step 2: Merge into target file and save
#     success = merge_tables(target_file, how_to_use_data, output_file)
    
#     if success:
#         print("\n" + "=" * 70)
#         print("SUCCESS! Merged file created.")
#         print("=" * 70)
#         print(f"\nOutput file: {output_file}")
#         print("\nFinal table structure:")
#         print("  Column 0: #")
#         print("  Column 1: Grammar Point & Meaning")
#         print("  Column 2: How to Use (NEWLY ADDED)")
#         print("  Column 3: Examples & Translation")
#     else:
#         print("\nERROR: Merge failed.")
#         sys.exit(1)


# # if __name__ == "__main__":
# #     main()

# #!/usr/bin/env python3
# """
# Grammar Table Merger Script - FIXED VERSION
# This script merges the "How to Use" column from a source HTML file into a target HTML file.

# Usage:
#     python merge_grammar_tables.py <source_file> <target_file> <output_file>

# Example:
#     python merge_grammar_tables.py N5_Grammar.html N5-G-Table.html N5-G-Table-Merged.html
# """

# import sys
# from bs4 import BeautifulSoup


# def extract_how_to_use_data(source_file):
#     """
#     Extract 'How to Use' data from the source HTML file.
    
#     Args:
#         source_file: Path to the source HTML file (N5_Grammar.html format)
        
#     Returns:
#         Dictionary mapping row numbers to 'How to Use' HTML content
#     """
#     print(f"Reading source file: {source_file}")
    
#     with open(source_file, 'r', encoding='utf-8') as f:
#         source_html = f.read()
    
#     source_soup = BeautifulSoup(source_html, 'html.parser')
    
#     # Find all rows in source table
#     source_tbody = source_soup.find('tbody')
#     if not source_tbody:
#         print("ERROR: Could not find <tbody> in source file")
#         return {}
    
#     source_rows = source_tbody.find_all('tr', recursive=False)
#     how_to_use_data = {}
    
#     for row in source_rows:
#         # Get only direct child td elements (not nested ones)
#         cells = row.find_all('td', recursive=False)
        
#         # Source file structure: [Number, Grammar, Meaning, How to Use, Examples]
#         if len(cells) >= 4:
#             number = cells[0].get_text(strip=True)
#             # Get the inner HTML content (not the outer <td> tag)
#             how_to_use_inner = ''.join(str(child) for child in cells[3].children)
#             how_to_use_data[number] = how_to_use_inner
    
#     print(f"✓ Extracted 'How to Use' data for {len(how_to_use_data)} entries")
#     return how_to_use_data


# def merge_tables(target_file, how_to_use_data, output_file):
#     """
#     Merge 'How to Use' data into the target HTML file.
    
#     Args:
#         target_file: Path to target HTML file (N5-G-Table.html format)
#         how_to_use_data: Dictionary with 'How to Use' content
#         output_file: Path for the merged output file
#     """
#     print(f"\nReading target file: {target_file}")
    
#     with open(target_file, 'r', encoding='utf-8') as f:
#         target_html = f.read()
    
#     target_soup = BeautifulSoup(target_html, 'html.parser')
    
#     # Update the header row
#     print("Updating table header...")
#     thead = target_soup.find('thead')
#     if not thead:
#         print("ERROR: Could not find <thead> in target file")
#         return False
    
#     header_row = thead.find('tr')
#     header_cells = list(header_row.find_all('th', recursive=False))
    
#     print(f"Original header has {len(header_cells)} columns:")
#     for i, th in enumerate(header_cells):
#         print(f"  Column {i}: {th.get_text(strip=True)}")
    
#     # Create new header for "How to Use" and insert it at position 2
#     new_header = target_soup.new_tag('th')
#     new_header.string = "How to Use"
    
#     if len(header_cells) >= 3:
#         # Insert the new header before the Examples column
#         header_cells[2].insert_before(new_header)
#     else:
#         print("ERROR: Target file doesn't have expected header structure")
#         return False
    
#     print("New header structure:")
#     for i, th in enumerate(header_row.find_all('th', recursive=False)):
#         print(f"  Column {i}: {th.get_text(strip=True)}")
    
#     # Update body rows
#     print("\nUpdating table body rows...")
#     tbody = target_soup.find('tbody')
#     if not tbody:
#         print("ERROR: Could not find <tbody> in target file")
#         return False
    
#     all_rows = tbody.find_all('tr', recursive=False)
#     print(f"Processing {len(all_rows)} rows...")
    
#     success_count = 0
#     missing_count = 0
    
#     for row in all_rows:
#         # Get only direct child td elements (not nested ones in tables)
#         row_cells = list(row.find_all('td', recursive=False))
        
#         if len(row_cells) < 3:
#             print(f"WARNING: Row has fewer than 3 cells, skipping")
#             continue
        
#         # Get the row number from first cell
#         number = row_cells[0].get_text(strip=True)
        
#         # Create new cell for "How to Use"
#         new_cell = target_soup.new_tag('td')
        
#         if number in how_to_use_data:
#             # Add the inner HTML content to the new cell
#             content_soup = BeautifulSoup(how_to_use_data[number], 'html.parser')
#             for element in content_soup:
#                 new_cell.append(element)
#             success_count += 1
#         else:
#             new_cell.string = "(no usage table)"
#             missing_count += 1
        
#         # THE KEY FIX: Insert the new cell BEFORE the third cell (Examples column)
#         # This ensures it goes into position 2 (index 2)
#         row_cells[2].insert_before(new_cell)
    
#     print(f"✓ Successfully added 'How to Use' data to {success_count} rows")
#     if missing_count > 0:
#         print(f"⚠ {missing_count} rows had no matching 'How to Use' data")
    
#     # Verify the result
#     print("\nVerifying result...")
#     sample_row = all_rows[0]
#     final_cells = sample_row.find_all('td', recursive=False)
#     print(f"Sample row now has {len(final_cells)} cells (expected: 4)")
    
#     if len(final_cells) == 4:
#         print("✓ Cell count is correct!")
#         # Double-check the order
#         print("\nVerifying cell order in first row:")
#         print(f"  Cell 0: {final_cells[0].get_text(strip=True)[:20]}... (should be row number)")
#         print(f"  Cell 1: {final_cells[1].get_text(strip=True)[:20]}... (should be grammar point)")
#         print(f"  Cell 2: {final_cells[2].get_text(strip=True)[:20]}... (should be 'How to Use')")
#         print(f"  Cell 3: {final_cells[3].get_text(strip=True)[:20]}... (should be examples)")
#     else:
#         print(f"⚠ WARNING: Expected 4 cells but found {len(final_cells)}")
    
#     # Save the merged file
#     print(f"\nSaving merged file to: {output_file}")
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write(target_soup.prettify())
    
#     print("✓ Merge complete!")
#     return True


# def main():
#     """Main function to handle command-line arguments and run the merge."""
    
#     if len(sys.argv) != 4:
#         print("Usage: python merge_grammar_tables.py <source_file> <target_file> <output_file>")
#         print("\nExample:")
#         print("  python merge_grammar_tables.py N5_Grammar.html N5-G-Table.html N5-G-Table-Merged.html")
#         print("\nDescription:")
#         print("  source_file: HTML file containing the 'How to Use' column to extract")
#         print("  target_file: HTML file where the 'How to Use' column will be inserted")
#         print("  output_file: Path for the merged output file")
#         sys.exit(1)
    
#     source_file = sys.argv[1]
#     target_file = sys.argv[2]
#     output_file = sys.argv[3]
    
#     print("=" * 70)
#     print("Grammar Table Merger - FIXED VERSION")
#     print("=" * 70)
    
#     # Step 1: Extract "How to Use" data from source file
#     how_to_use_data = extract_how_to_use_data(source_file)
    
#     if not how_to_use_data:
#         print("ERROR: No data extracted from source file. Exiting.")
#         sys.exit(1)
    
#     # Step 2: Merge into target file and save
#     success = merge_tables(target_file, how_to_use_data, output_file)
    
#     if success:
#         print("\n" + "=" * 70)
#         print("SUCCESS! Merged file created.")
#         print("=" * 70)
#         print(f"\nOutput file: {output_file}")
#         print("\nFinal table structure:")
#         print("  Column 0: #")
#         print("  Column 1: Grammar Point & Meaning")
#         print("  Column 2: How to Use (NEWLY ADDED)")
#         print("  Column 3: Examples & Translation")
#     else:
#         print("\nERROR: Merge failed.")
#         sys.exit(1)


# # if __name__ == "__main__":
# #     main()


# #!/usr/bin/env python3
# """
# Enhanced Grammar Table Merger Script
# Features:
# 1. Column-level toggle buttons
# 2. Cell-level toggle buttons for Grammar Point & How to Use columns
# 3. Source hyperlinks in How to Use column
# 4. Web scraping for empty How to Use cells
# 5. Color-coded How to Use column matching Example column

# Usage:
#     python merge_grammar_tables.py <source_file> <target_file> <output_file> [--no-fetch]

# Example:
#     python merge_grammar_tables.py N5_Grammar.html N5-G-Table.html N5-G-Table-Enhanced.html
# """

# import sys
# import re
# from bs4 import BeautifulSoup
# import urllib.request
# import time


# def fetch_usage_table_from_url(url):
#     """
#     Fetch the usage table from a JLPT Sensei URL.
    
#     Args:
#         url: The URL to fetch from
        
#     Returns:
#         HTML string of the usage table, or None if not found
#     """
#     try:
#         print(f"    Fetching from: {url}")
        
#         # Add headers to avoid being blocked
#         req = urllib.request.Request(
#             url,
#             headers={
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#             }
#         )
        
#         with urllib.request.urlopen(req, timeout=10) as response:
#             html = response.read().decode('utf-8')
        
#         soup = BeautifulSoup(html, 'html.parser')
        
#         # Look for usage table - it typically has class "usage" or is in a specific section
#         usage_table = soup.find('table', class_='usage')
        
#         if not usage_table:
#             # Try alternative selectors
#             usage_table = soup.find('table', class_='table-bordered')
        
#         if usage_table:
#             print(f"    ✓ Found usage table")
#             return str(usage_table)
#         else:
#             print(f"    ✗ No usage table found")
#             return None
            
#     except Exception as e:
#         print(f"    ✗ Error fetching URL: {e}")
#         return None


# def extract_how_to_use_data(source_file, fetch_missing=True):
#     """
#     Extract 'How to Use' data from the source HTML file.
#     Also extracts source URLs and fetches missing data if needed.
    
#     Args:
#         source_file: Path to the source HTML file
#         fetch_missing: Whether to fetch from URLs for empty cells
        
#     Returns:
#         Dictionary with 'content' and 'url' for each row number
#     """
#     print(f"Reading source file: {source_file}")
    
#     with open(source_file, 'r', encoding='utf-8') as f:
#         source_html = f.read()
    
#     source_soup = BeautifulSoup(source_html, 'html.parser')
#     source_tbody = source_soup.find('tbody')
    
#     if not source_tbody:
#         print("ERROR: Could not find <tbody> in source file")
#         return {}
    
#     source_rows = source_tbody.find_all('tr', recursive=False)
#     how_to_use_data = {}
    
#     for row in source_rows:
#         cells = row.find_all('td', recursive=False)
        
#         if len(cells) >= 5:
#             number = cells[0].get_text(strip=True)
            
#             # Get How to Use content (column 3)
#             how_to_use_inner = ''.join(str(child) for child in cells[3].children)
            
#             # Get source URL from Examples column (column 4)
#             examples_cell = cells[4]
#             link = examples_cell.find('a', href=True)
#             source_url = link['href'] if link else None
            
#             # Check if How to Use is empty/minimal
#             text_content = cells[3].get_text(strip=True)
#             is_empty = len(text_content) < 20
            
#             # If empty and we have a URL, try to fetch the table
#             if is_empty and source_url and fetch_missing:
#                 print(f"  Row {number}: How to Use is minimal, fetching from URL...")
#                 fetched_table = fetch_usage_table_from_url(source_url)
#                 if fetched_table:
#                     how_to_use_inner = fetched_table
#                 time.sleep(0.5)  # Be nice to the server
            
#             how_to_use_data[number] = {
#                 'content': how_to_use_inner,
#                 'url': source_url
#             }
    
#     print(f"✓ Extracted data for {len(how_to_use_data)} entries")
#     return how_to_use_data


# def add_highlighting_to_usage_table(usage_content):
#     """
#     Add color highlighting to the usage table to match the example column style.
#     Highlights verb forms, particles, and grammar patterns.
    
#     Args:
#         usage_content: HTML string of the usage table
        
#     Returns:
#         Enhanced HTML string with highlighting
#     """
#     soup = BeautifulSoup(usage_content, 'html.parser')
    
#     # Find all table cells
#     cells = soup.find_all('td')
    
#     for cell in cells:
#         text = cell.get_text()
        
#         # Highlight grammar particles and endings
#         grammar_patterns = [
#             'だ', 'です', 'ます', 'ません', 'ました', 'ませんでした',
#             'だった', 'でした', 'じゃない', 'ではない',
#             'ちゃだめ', 'ちゃいけない', 'じゃダメ', 'じゃいけない',
#             'から', 'ので', 'けど', 'が', 'けれども',
#             'たい', 'たがる', 'たら', 'ば',
#             'より', 'ほう', 'つもり', 'よう'
#         ]
        
#         # Wrap grammar patterns with highlighting
#         for pattern in grammar_patterns:
#             if pattern in text:
#                 # Find and wrap the pattern
#                 new_html = str(cell)
#                 new_html = new_html.replace(pattern, f'<span class="hl-grammar">{pattern}</span>')
#                 cell.replace_with(BeautifulSoup(new_html, 'html.parser'))
#                 break
    
#     return str(soup)


# def create_enhanced_html(target_soup):
#     """
#     Add JavaScript for toggle functionality and enhanced styles.
    
#     Args:
#         target_soup: BeautifulSoup object of the target HTML
#     """
    
#     # Add CSS for toggle buttons and hidden state
#     style_tag = target_soup.find('style')
#     if style_tag:
#         additional_css = """
        
#         /* Toggle buttons */
#         .toggle-btn {
#             background-color: #6c757d;
#             color: white;
#             border: none;
#             padding: 3px 8px;
#             margin: 2px;
#             border-radius: 4px;
#             cursor: pointer;
#             font-size: 0.75rem;
#             transition: all 0.3s;
#         }
        
#         .toggle-btn:hover {
#             background-color: #5a6268;
#             transform: scale(1.05);
#         }
        
#         .toggle-btn.active {
#             background-color: #28a745;
#         }
        
#         .cell-toggle-btn {
#             background-color: #17a2b8;
#             padding: 2px 6px;
#             font-size: 0.7rem;
#             margin-bottom: 5px;
#             display: inline-block;
#         }
        
#         .cell-toggle-btn:hover {
#             background-color: #138496;
#         }
        
#         /* Column visibility */
#         .col-hidden-1 td:nth-child(2),
#         .col-hidden-1 th:nth-child(2) {
#             display: none;
#         }
        
#         .col-hidden-2 td:nth-child(3),
#         .col-hidden-2 th:nth-child(3) {
#             display: none;
#         }
        
#         .col-hidden-3 td:nth-child(4),
#         .col-hidden-3 th:nth-child(4) {
#             display: none;
#         }
        
#         /* Cell content visibility */
#         .cell-content-hidden {
#             display: none;
#         }
        
#         /* Source link styling */
#         .source-link {
#             display: block;
#             margin-top: 8px;
#             font-size: 0.8rem;
#             color: #0d6efd;
#             text-decoration: none;
#         }
        
#         .source-link:hover {
#             text-decoration: underline;
#         }
        
#         /* Control panel */
#         .control-panel {
#             background: #f8f9fa;
#             padding: 15px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#             border: 1px solid #dee2e6;
#         }
        
#         .control-panel h3 {
#             font-size: 1rem;
#             margin-bottom: 10px;
#             color: #495057;
#         }
#         """
#         style_tag.string += additional_css
    
#     # Add JavaScript for toggle functionality
#     script_tag = target_soup.new_tag('script')
#     script_tag.string = """
#     // Column toggle functionality
#     function toggleColumn(columnIndex) {
#         const table = document.querySelector('table');
#         const className = 'col-hidden-' + columnIndex;
#         const btn = document.getElementById('col-toggle-' + columnIndex);
        
#         if (table.classList.contains(className)) {
#             table.classList.remove(className);
#             btn.classList.add('active');
#             btn.textContent = btn.textContent.replace('Show', 'Hide');
#         } else {
#             table.classList.add(className);
#             btn.classList.remove('active');
#             btn.textContent = btn.textContent.replace('Hide', 'Show');
#         }
#     }
    
#     // Cell content toggle functionality
#     function toggleCellContent(cellId) {
#         const content = document.getElementById(cellId);
#         const btn = event.target;
        
#         if (content.classList.contains('cell-content-hidden')) {
#             content.classList.remove('cell-content-hidden');
#             btn.textContent = '▼ Hide';
#         } else {
#             content.classList.add('cell-content-hidden');
#             btn.textContent = '▶ Show';
#         }
#     }
    
#     // Initialize all column buttons as active (visible)
#     window.addEventListener('DOMContentLoaded', function() {
#         for (let i = 1; i <= 3; i++) {
#             const btn = document.getElementById('col-toggle-' + i);
#             if (btn) {
#                 btn.classList.add('active');
#             }
#         }
#     });
#     """
    
#     # Insert script before closing body tag
#     body_tag = target_soup.find('body')
#     if body_tag:
#         body_tag.append(script_tag)


# def add_control_panel(target_soup):
#     """
#     Add a control panel with column toggle buttons.
    
#     Args:
#         target_soup: BeautifulSoup object of the target HTML
#     """
    
#     control_panel_html = """
#     <div class="control-panel">
#         <h3>📊 Column Visibility Controls</h3>
#         <button id="col-toggle-1" class="toggle-btn" onclick="toggleColumn(1)">Hide Grammar Point & Meaning</button>
#         <button id="col-toggle-2" class="toggle-btn" onclick="toggleColumn(2)">Hide How to Use</button>
#         <button id="col-toggle-3" class="toggle-btn" onclick="toggleColumn(3)">Hide Examples & Translation</button>
#     </div>
#     """
    
#     control_panel = BeautifulSoup(control_panel_html, 'html.parser')
    
#     # Insert before the table
#     table_div = target_soup.find('div', class_='table-responsive')
#     if table_div:
#         table_div.insert_before(control_panel)


# def merge_tables_enhanced(target_file, how_to_use_data, output_file):
#     """
#     Enhanced merge with all features.
#     """
#     print(f"\nReading target file: {target_file}")
    
#     with open(target_file, 'r', encoding='utf-8') as f:
#         target_html = f.read()
    
#     target_soup = BeautifulSoup(target_html, 'html.parser')
    
#     # Update header
#     print("Updating table header...")
#     thead = target_soup.find('thead')
#     header_row = thead.find('tr')
#     header_cells = list(header_row.find_all('th', recursive=False))
    
#     new_header = target_soup.new_tag('th')
#     new_header.string = "How to Use"
#     header_cells[2].insert_before(new_header)
    
#     print("Header structure:")
#     for i, th in enumerate(header_row.find_all('th', recursive=False)):
#         print(f"  Column {i}: {th.get_text(strip=True)}")
    
#     # Update body rows
#     print("\nUpdating table body rows with enhanced features...")
#     tbody = target_soup.find('tbody')
#     all_rows = tbody.find_all('tr', recursive=False)
    
#     success_count = 0
    
#     for row_idx, row in enumerate(all_rows):
#         row_cells = list(row.find_all('td', recursive=False))
#         number = row_cells[0].get_text(strip=True)
        
#         if number not in how_to_use_data:
#             continue
        
#         data = how_to_use_data[number]
        
#         # Create new cell for "How to Use"
#         new_cell = target_soup.new_tag('td')
        
#         # Add cell toggle button
#         toggle_btn = target_soup.new_tag('button', 
#                                          onclick=f'toggleCellContent("how-to-use-content-{number}")',
#                                          **{'class': 'cell-toggle-btn toggle-btn'})
#         toggle_btn.string = '▼ Hide'
#         new_cell.append(toggle_btn)
        
#         # Add content wrapper
#         content_wrapper = target_soup.new_tag('div', id=f'how-to-use-content-{number}')
        
#         # Add the usage table/content with highlighting
#         enhanced_content = add_highlighting_to_usage_table(data['content'])
#         content_soup = BeautifulSoup(enhanced_content, 'html.parser')
#         for element in content_soup:
#             content_wrapper.append(element)
        
#         # Add source link if available
#         if data['url']:
#             source_link = target_soup.new_tag('a', 
#                                              href=data['url'],
#                                              target='_blank',
#                                              **{'class': 'source-link'})
#             source_link.string = '📚 Source: JLPT Sensei'
#             content_wrapper.append(target_soup.new_tag('br'))
#             content_wrapper.append(source_link)
        
#         new_cell.append(content_wrapper)
        
#         # Also add toggle to Grammar Point cell (column 1)
#         grammar_cell = row_cells[1]
#         grammar_toggle = target_soup.new_tag('button',
#                                             onclick=f'toggleCellContent("grammar-content-{number}")',
#                                             **{'class': 'cell-toggle-btn toggle-btn'})
#         grammar_toggle.string = '▼ Hide'
        
#         # Wrap existing grammar content
#         grammar_wrapper = target_soup.new_tag('div', id=f'grammar-content-{number}')
#         for child in list(grammar_cell.children):
#             grammar_wrapper.append(child)
        
#         grammar_cell.clear()
#         grammar_cell.append(grammar_toggle)
#         grammar_cell.append(grammar_wrapper)
        
#         # Insert the How to Use cell
#         row_cells[2].insert_before(new_cell)
        
#         success_count += 1
    
#     print(f"✓ Successfully processed {success_count} rows")
    
#     # Add control panel and enhanced features
#     print("\nAdding enhanced features...")
#     add_control_panel(target_soup)
#     create_enhanced_html(target_soup)
    
#     # Save
#     print(f"\nSaving enhanced file to: {output_file}")
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write(target_soup.prettify())
    
#     print("✓ Enhanced merge complete!")
#     return True


# def main():
#     if len(sys.argv) < 4:
#         print("Usage: python merge_grammar_tables.py <source_file> <target_file> <output_file> [--no-fetch]")
#         print("\nOptions:")
#         print("  --no-fetch    Skip fetching missing usage tables from URLs")
#         sys.exit(1)
    
#     source_file = sys.argv[1]
#     target_file = sys.argv[2]
#     output_file = sys.argv[3]
#     fetch_missing = '--no-fetch' not in sys.argv
    
#     print("=" * 70)
#     print("Enhanced Grammar Table Merger")
#     print("=" * 70)
    
#     # Extract data
#     how_to_use_data = extract_how_to_use_data(source_file, fetch_missing)
    
#     if not how_to_use_data:
#         print("ERROR: No data extracted. Exiting.")
#         sys.exit(1)
    
#     # Merge with enhancements
#     success = merge_tables_enhanced(target_file, how_to_use_data, output_file)
    
#     if success:
#         print("\n" + "=" * 70)
#         print("SUCCESS! Enhanced file created with:")
#         print("  ✓ Column toggle buttons")
#         print("  ✓ Cell-level toggles for Grammar & How to Use")
#         print("  ✓ Source hyperlinks")
#         print("  ✓ Auto-fetched missing usage tables")
#         print("  ✓ Color-coded highlighting")
#         print("=" * 70)


# if __name__ == "__main__":
#     main()


# #!/usr/bin/env python3
# """
# Enhanced Grammar Table Merger Script
# Features:
# 1. Column-level toggle buttons
# 2. Cell-level toggle buttons for Grammar Point & How to Use columns
# 3. Source hyperlinks in How to Use column
# 4. Web scraping for empty How to Use cells
# 5. Color-coded How to Use column matching Example column

# Usage:
#     python merge_grammar_tables.py <source_file> <target_file> <output_file> [--no-fetch]

# Example:
#     python merge_grammar_tables.py N5_Grammar.html N5-G-Table.html N5-G-Table-Enhanced.html
# """

# import sys
# import re
# from bs4 import BeautifulSoup
# import urllib.request
# import time


# def fetch_usage_table_from_url(url):
#     """
#     Fetch the usage table from a JLPT Sensei URL.
    
#     Args:
#         url: The URL to fetch from
        
#     Returns:
#         HTML string of the usage table, or None if not found
#     """
#     try:
#         print(f"    Fetching from: {url}")
        
#         # Add headers to avoid being blocked
#         req = urllib.request.Request(
#             url,
#             headers={
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#             }
#         )
        
#         with urllib.request.urlopen(req, timeout=10) as response:
#             html = response.read().decode('utf-8')
        
#         soup = BeautifulSoup(html, 'html.parser')
        
#         # Look for usage table - it typically has class "usage" or is in a specific section
#         usage_table = soup.find('table', class_='usage')
        
#         if not usage_table:
#             # Try alternative selectors
#             usage_table = soup.find('table', class_='table-bordered')
        
#         if usage_table:
#             print(f"    ✓ Found usage table")
#             return str(usage_table)
#         else:
#             print(f"    ✗ No usage table found")
#             return None
            
#     except Exception as e:
#         print(f"    ✗ Error fetching URL: {e}")
#         return None


# def extract_how_to_use_data(source_file, fetch_missing=True):
#     """
#     Extract 'How to Use' data from the source HTML file.
#     Also extracts source URLs and fetches missing data if needed.
    
#     Args:
#         source_file: Path to the source HTML file
#         fetch_missing: Whether to fetch from URLs for empty cells
        
#     Returns:
#         Dictionary with 'content' and 'url' for each row number
#     """
#     print(f"Reading source file: {source_file}")
    
#     with open(source_file, 'r', encoding='utf-8') as f:
#         source_html = f.read()
    
#     source_soup = BeautifulSoup(source_html, 'html.parser')
#     source_tbody = source_soup.find('tbody')
    
#     if not source_tbody:
#         print("ERROR: Could not find <tbody> in source file")
#         return {}
    
#     source_rows = source_tbody.find_all('tr', recursive=False)
#     how_to_use_data = {}
    
#     for row in source_rows:
#         cells = row.find_all('td', recursive=False)
        
#         if len(cells) >= 5:
#             number = cells[0].get_text(strip=True)
            
#             # Get How to Use content (column 3)
#             how_to_use_inner = ''.join(str(child) for child in cells[3].children)
            
#             # Get source URL from Examples column (column 4)
#             examples_cell = cells[4]
#             link = examples_cell.find('a', href=True)
#             source_url = link['href'] if link else None
            
#             # Check if How to Use is empty/minimal
#             text_content = cells[3].get_text(strip=True)
#             is_empty = len(text_content) < 20
            
#             # If empty and we have a URL, try to fetch the table
#             if is_empty and source_url and fetch_missing:
#                 print(f"  Row {number}: How to Use is minimal, fetching from URL...")
#                 fetched_table = fetch_usage_table_from_url(source_url)
#                 if fetched_table:
#                     how_to_use_inner = fetched_table
#                 time.sleep(0.5)  # Be nice to the server
            
#             how_to_use_data[number] = {
#                 'content': how_to_use_inner,
#                 'url': source_url
#             }
    
#     print(f"✓ Extracted data for {len(how_to_use_data)} entries")
#     return how_to_use_data


# def add_highlighting_to_usage_table(usage_content):
#     """
#     Add color highlighting to the usage table to match the example column style.
#     Highlights verb forms, particles, and grammar patterns.
    
#     Args:
#         usage_content: HTML string of the usage table
        
#     Returns:
#         Enhanced HTML string with highlighting
#     """
#     soup = BeautifulSoup(usage_content, 'html.parser')
    
#     # Find all table cells
#     cells = soup.find_all('td')
    
#     for cell in cells:
#         text = cell.get_text()
        
#         # Highlight grammar particles and endings
#         grammar_patterns = [
#             'だ', 'です', 'ます', 'ません', 'ました', 'ませんでした',
#             'だった', 'でした', 'じゃない', 'ではない',
#             'ちゃだめ', 'ちゃいけない', 'じゃダメ', 'じゃいけない',
#             'から', 'ので', 'けど', 'が', 'けれども',
#             'たい', 'たがる', 'たら', 'ば',
#             'より', 'ほう', 'つもり', 'よう'
#         ]
        
#         # Wrap grammar patterns with highlighting
#         for pattern in grammar_patterns:
#             if pattern in text:
#                 # Find and wrap the pattern
#                 new_html = str(cell)
#                 new_html = new_html.replace(pattern, f'<span class="hl-grammar">{pattern}</span>')
#                 cell.replace_with(BeautifulSoup(new_html, 'html.parser'))
#                 break
    
#     return str(soup)


# def create_enhanced_html(target_soup):
#     """
#     Add JavaScript for toggle functionality and enhanced styles.
    
#     Args:
#         target_soup: BeautifulSoup object of the target HTML
#     """
    
#     # Add CSS for toggle buttons and hidden state
#     style_tag = target_soup.find('style')
#     if style_tag:
#         additional_css = """
        
#         /* Toggle buttons */
#         .toggle-btn {
#             background-color: #6c757d;
#             color: white;
#             border: none;
#             padding: 3px 8px;
#             margin: 2px;
#             border-radius: 4px;
#             cursor: pointer;
#             font-size: 0.75rem;
#             transition: all 0.3s;
#         }
        
#         .toggle-btn:hover {
#             background-color: #5a6268;
#             transform: scale(1.05);
#         }
        
#         .toggle-btn.active {
#             background-color: #28a745;
#         }
        
#         .cell-toggle-btn {
#             background-color: #17a2b8;
#             padding: 2px 6px;
#             font-size: 0.7rem;
#             margin-bottom: 5px;
#             display: inline-block;
#         }
        
#         .cell-toggle-btn:hover {
#             background-color: #138496;
#         }
        
#         /* Cell content visibility */
#         .cell-content-hidden {
#             display: none;
#         }
        
#         /* Source link styling */
#         .source-link {
#             display: block;
#             margin-top: 8px;
#             font-size: 0.8rem;
#             color: #0d6efd;
#             text-decoration: none;
#         }
        
#         .source-link:hover {
#             text-decoration: underline;
#         }
        
#         /* Control panel */
#         .control-panel {
#             background: #f8f9fa;
#             padding: 15px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#             border: 1px solid #dee2e6;
#         }
        
#         .control-panel h3 {
#             font-size: 1rem;
#             margin-bottom: 10px;
#             color: #495057;
#         }
#         """
#         style_tag.string += additional_css
    
#     # Add JavaScript for toggle functionality
#     script_tag = target_soup.new_tag('script')
#     script_tag.string = """
#     // Cell content toggle functionality
#     function toggleCellContent(cellId) {
#         const content = document.getElementById(cellId);
#         const btn = event.target;
        
#         if (content.classList.contains('cell-content-hidden')) {
#             content.classList.remove('cell-content-hidden');
#             btn.textContent = '▼ Hide';
#         } else {
#             content.classList.add('cell-content-hidden');
#             btn.textContent = '▶ Show';
#         }
#     }
#     """
    
#     # Insert script before closing body tag
#     body_tag = target_soup.find('body')
#     if body_tag:
#         body_tag.append(script_tag)


# def add_control_panel(target_soup):
#     """
#     Add a control panel (removed - keeping only cell-level toggles).
    
#     Args:
#         target_soup: BeautifulSoup object of the target HTML
#     """
#     # Control panel removed - columns always visible, only cell content toggles
#     pass


# def merge_tables_enhanced(target_file, how_to_use_data, output_file):
#     """
#     Enhanced merge with all features.
#     """
#     print(f"\nReading target file: {target_file}")
    
#     with open(target_file, 'r', encoding='utf-8') as f:
#         target_html = f.read()
    
#     target_soup = BeautifulSoup(target_html, 'html.parser')
    
#     # Update header
#     print("Updating table header...")
#     thead = target_soup.find('thead')
#     header_row = thead.find('tr')
#     header_cells = list(header_row.find_all('th', recursive=False))
    
#     new_header = target_soup.new_tag('th')
#     new_header.string = "How to Use"
#     header_cells[2].insert_before(new_header)
    
#     print("Header structure:")
#     for i, th in enumerate(header_row.find_all('th', recursive=False)):
#         print(f"  Column {i}: {th.get_text(strip=True)}")
    
#     # Update body rows
#     print("\nUpdating table body rows with enhanced features...")
#     tbody = target_soup.find('tbody')
#     all_rows = tbody.find_all('tr', recursive=False)
    
#     success_count = 0
    
#     for row_idx, row in enumerate(all_rows):
#         row_cells = list(row.find_all('td', recursive=False))
#         number = row_cells[0].get_text(strip=True)
        
#         # Add toggle to Grammar Point cell (column 1) - ALWAYS
#         grammar_cell = row_cells[1]
#         grammar_toggle = target_soup.new_tag('button',
#                                             onclick=f'toggleCellContent("grammar-content-{number}")',
#                                             **{'class': 'cell-toggle-btn toggle-btn'})
#         grammar_toggle.string = '▼ Hide'
        
#         # Wrap existing grammar content
#         grammar_wrapper = target_soup.new_tag('div', id=f'grammar-content-{number}')
#         for child in list(grammar_cell.children):
#             grammar_wrapper.append(child)
        
#         grammar_cell.clear()
#         grammar_cell.append(grammar_toggle)
#         grammar_cell.append(grammar_wrapper)
        
#         # Create new cell for "How to Use"
#         new_cell = target_soup.new_tag('td')
        
#         # Add cell toggle button - ALWAYS present
#         toggle_btn = target_soup.new_tag('button', 
#                                          onclick=f'toggleCellContent("how-to-use-content-{number}")',
#                                          **{'class': 'cell-toggle-btn toggle-btn'})
#         toggle_btn.string = '▼ Hide'
#         new_cell.append(toggle_btn)
        
#         # Add content wrapper
#         content_wrapper = target_soup.new_tag('div', id=f'how-to-use-content-{number}')
        
#         if number in how_to_use_data:
#             data = how_to_use_data[number]
            
#             # Add the usage table/content with highlighting
#             enhanced_content = add_highlighting_to_usage_table(data['content'])
#             content_soup = BeautifulSoup(enhanced_content, 'html.parser')
#             for element in content_soup:
#                 content_wrapper.append(element)
            
#             # Add source link if available
#             if data['url']:
#                 source_link = target_soup.new_tag('a', 
#                                                  href=data['url'],
#                                                  target='_blank',
#                                                  **{'class': 'source-link'})
#                 source_link.string = '📚 Source: JLPT Sensei'
#                 content_wrapper.append(target_soup.new_tag('br'))
#                 content_wrapper.append(source_link)
#         else:
#             # No data available
#             no_data = target_soup.new_tag('p')
#             no_data.string = '(no usage table)'
#             content_wrapper.append(no_data)
        
#         new_cell.append(content_wrapper)
        
#         # Insert the How to Use cell
#         row_cells[2].insert_before(new_cell)
        
#         # Add toggle to Examples cell (column 3, now column 4 after insertion) - ALWAYS
#         examples_cell = row.find_all('td', recursive=False)[3]  # Get updated cell list
#         examples_toggle = target_soup.new_tag('button',
#                                              onclick=f'toggleCellContent("examples-content-{number}")',
#                                              **{'class': 'cell-toggle-btn toggle-btn'})
#         examples_toggle.string = '▼ Hide'
        
#         # Wrap existing examples content
#         examples_wrapper = target_soup.new_tag('div', id=f'examples-content-{number}')
#         for child in list(examples_cell.children):
#             examples_wrapper.append(child)
        
#         examples_cell.clear()
#         examples_cell.append(examples_toggle)
#         examples_cell.append(examples_wrapper)
        
#         success_count += 1
    
#     print(f"✓ Successfully processed {success_count} rows")
    
#     # Add control panel and enhanced features
#     print("\nAdding enhanced features...")
#     add_control_panel(target_soup)
#     create_enhanced_html(target_soup)
    
#     # Save
#     print(f"\nSaving enhanced file to: {output_file}")
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write(target_soup.prettify())
    
#     print("✓ Enhanced merge complete!")
#     return True


# def main():
#     if len(sys.argv) < 4:
#         print("Usage: python merge_grammar_tables.py <source_file> <target_file> <output_file> [--no-fetch]")
#         print("\nOptions:")
#         print("  --no-fetch    Skip fetching missing usage tables from URLs")
#         sys.exit(1)
    
#     source_file = sys.argv[1]
#     target_file = sys.argv[2]
#     output_file = sys.argv[3]
#     fetch_missing = '--no-fetch' not in sys.argv
    
#     print("=" * 70)
#     print("Enhanced Grammar Table Merger")
#     print("=" * 70)
    
#     # Extract data
#     how_to_use_data = extract_how_to_use_data(source_file, fetch_missing)
    
#     if not how_to_use_data:
#         print("ERROR: No data extracted. Exiting.")
#         sys.exit(1)
    
#     # Merge with enhancements
#     success = merge_tables_enhanced(target_file, how_to_use_data, output_file)
    
#     if success:
#         print("\n" + "=" * 70)
#         print("SUCCESS! Enhanced file created with:")
#         print("  ✓ Cell-level toggle buttons in all data columns")
#         print("  ✓ Columns always visible, only content toggles")
#         print("  ✓ Source hyperlinks in How to Use cells")
#         print("  ✓ Auto-fetched missing usage tables")
#         print("  ✓ Color-coded highlighting")
#         print("=" * 70)


# # if __name__ == "__main__":
# #     main()


# #!/usr/bin/env python3
# """
# Enhanced Grammar Table Merger Script
# Features:
# 1. Column-level toggle buttons
# 2. Cell-level toggle buttons for Grammar Point & How to Use columns
# 3. Source hyperlinks in How to Use column
# 4. Web scraping for empty How to Use cells
# 5. Color-coded How to Use column matching Example column

# Usage:
#     python merge_grammar_tables.py <source_file> <target_file> <output_file> [--no-fetch]

# Example:
#     python merge_grammar_tables.py N5_Grammar.html N5-G-Table.html N5-G-Table-Enhanced.html
# """

# import sys
# import re
# from bs4 import BeautifulSoup
# import urllib.request
# import time


# def fetch_usage_table_from_url(url):
#     """
#     Fetch the usage table from a JLPT Sensei URL.
    
#     Args:
#         url: The URL to fetch from
        
#     Returns:
#         HTML string of the usage table, or None if not found
#     """
#     try:
#         print(f"    Fetching from: {url}")
        
#         # Add headers to avoid being blocked
#         req = urllib.request.Request(
#             url,
#             headers={
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#             }
#         )
        
#         with urllib.request.urlopen(req, timeout=10) as response:
#             html = response.read().decode('utf-8')
        
#         soup = BeautifulSoup(html, 'html.parser')
        
#         # Look for usage table - it typically has class "usage" or is in a specific section
#         usage_table = soup.find('table', class_='usage')
        
#         if not usage_table:
#             # Try alternative selectors
#             usage_table = soup.find('table', class_='table-bordered')
        
#         if usage_table:
#             print(f"    ✓ Found usage table")
#             return str(usage_table)
#         else:
#             print(f"    ✗ No usage table found")
#             return None
            
#     except Exception as e:
#         print(f"    ✗ Error fetching URL: {e}")
#         return None


# def extract_how_to_use_data(source_file, fetch_missing=True):
#     """
#     Extract 'How to Use' data from the source HTML file.
#     Also extracts source URLs and fetches missing data if needed.
    
#     Args:
#         source_file: Path to the source HTML file
#         fetch_missing: Whether to fetch from URLs for empty cells
        
#     Returns:
#         Dictionary with 'content' and 'url' for each row number
#     """
#     print(f"Reading source file: {source_file}")
    
#     with open(source_file, 'r', encoding='utf-8') as f:
#         source_html = f.read()
    
#     source_soup = BeautifulSoup(source_html, 'html.parser')
#     source_tbody = source_soup.find('tbody')
    
#     if not source_tbody:
#         print("ERROR: Could not find <tbody> in source file")
#         return {}
    
#     source_rows = source_tbody.find_all('tr', recursive=False)
#     how_to_use_data = {}
    
#     for row in source_rows:
#         cells = row.find_all('td', recursive=False)
        
#         if len(cells) >= 5:
#             number = cells[0].get_text(strip=True)
            
#             # Get How to Use content (column 3)
#             how_to_use_inner = ''.join(str(child) for child in cells[3].children)
            
#             # Get source URL from Examples column (column 4)
#             examples_cell = cells[4]
#             link = examples_cell.find('a', href=True)
#             source_url = link['href'] if link else None
            
#             # Check if How to Use is empty/minimal
#             text_content = cells[3].get_text(strip=True)
#             is_empty = len(text_content) < 20
            
#             # If empty and we have a URL, try to fetch the table
#             if is_empty and source_url and fetch_missing:
#                 print(f"  Row {number}: How to Use is minimal, fetching from URL...")
#                 fetched_table = fetch_usage_table_from_url(source_url)
#                 if fetched_table:
#                     how_to_use_inner = fetched_table
#                 time.sleep(0.5)  # Be nice to the server
            
#             how_to_use_data[number] = {
#                 'content': how_to_use_inner,
#                 'url': source_url
#             }
    
#     print(f"✓ Extracted data for {len(how_to_use_data)} entries")
#     return how_to_use_data


# def add_highlighting_to_usage_table(usage_content):
#     """
#     Add color highlighting to the usage table to match the example column style.
#     Highlights verb forms, particles, and grammar patterns.
    
#     Args:
#         usage_content: HTML string of the usage table
        
#     Returns:
#         Enhanced HTML string with highlighting
#     """
#     soup = BeautifulSoup(usage_content, 'html.parser')
    
#     # Find all table cells
#     cells = soup.find_all('td')
    
#     for cell in cells:
#         text = cell.get_text()
        
#         # Highlight grammar particles and endings
#         grammar_patterns = [
#             'だ', 'です', 'ます', 'ません', 'ました', 'ませんでした',
#             'だった', 'でした', 'じゃない', 'ではない',
#             'ちゃだめ', 'ちゃいけない', 'じゃダメ', 'じゃいけない',
#             'から', 'ので', 'けど', 'が', 'けれども',
#             'たい', 'たがる', 'たら', 'ば',
#             'より', 'ほう', 'つもり', 'よう'
#         ]
        
#         # Wrap grammar patterns with highlighting
#         for pattern in grammar_patterns:
#             if pattern in text:
#                 # Find and wrap the pattern
#                 new_html = str(cell)
#                 new_html = new_html.replace(pattern, f'<span class="hl-grammar">{pattern}</span>')
#                 cell.replace_with(BeautifulSoup(new_html, 'html.parser'))
#                 break
    
#     return str(soup)


# def create_enhanced_html(target_soup):
#     """
#     Add JavaScript for toggle functionality and enhanced styles.
    
#     Args:
#         target_soup: BeautifulSoup object of the target HTML
#     """
    
#     # Add CSS for toggle buttons and hidden state
#     style_tag = target_soup.find('style')
#     if style_tag:
#         additional_css = """
        
#         /* Toggle buttons */
#         .toggle-btn {
#             background-color: #6c757d;
#             color: white;
#             border: none;
#             padding: 3px 8px;
#             margin: 2px;
#             border-radius: 4px;
#             cursor: pointer;
#             font-size: 0.75rem;
#             transition: all 0.3s;
#         }
        
#         .toggle-btn:hover {
#             background-color: #5a6268;
#             transform: scale(1.05);
#         }
        
#         .toggle-btn.active {
#             background-color: #28a745;
#         }
        
#         .cell-toggle-btn {
#             background-color: #17a2b8;
#             padding: 2px 6px;
#             font-size: 0.7rem;
#             margin-bottom: 5px;
#             display: inline-block;
#         }
        
#         .cell-toggle-btn:hover {
#             background-color: #138496;
#         }
        
#         /* Column visibility - hides entire column */
#         .col-hidden-1 td:nth-child(2),
#         .col-hidden-1 th:nth-child(2) {
#             display: none;
#         }
        
#         .col-hidden-2 td:nth-child(3),
#         .col-hidden-2 th:nth-child(3) {
#             display: none;
#         }
        
#         .col-hidden-3 td:nth-child(4),
#         .col-hidden-3 th:nth-child(4) {
#             display: none;
#         }
        
#         /* Data visibility - hides only content, keeps toggle buttons */
#         .data-hidden-1 .grammar-data-content {
#             display: none;
#         }
        
#         .data-hidden-2 .how-to-use-data-content {
#             display: none;
#         }
        
#         .data-hidden-3 .examples-data-content {
#             display: none;
#         }
        
#         /* Cell content visibility */
#         .cell-content-hidden {
#             display: none;
#         }
        
#         /* Source link styling */
#         .source-link {
#             display: block;
#             margin-top: 8px;
#             font-size: 0.8rem;
#             color: #0d6efd;
#             text-decoration: none;
#         }
        
#         .source-link:hover {
#             text-decoration: underline;
#         }
        
#         /* Control panel */
#         .control-panel {
#             background: #f8f9fa;
#             padding: 15px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#             border: 1px solid #dee2e6;
#         }
        
#         .control-panel h3 {
#             font-size: 1rem;
#             margin-bottom: 10px;
#             color: #495057;
#         }
#         """
#         style_tag.string += additional_css
    
#     # Add JavaScript for toggle functionality
#     script_tag = target_soup.new_tag('script')
#     script_tag.string = """
#     // Column visibility toggle - hides entire column
#     function toggleColumn(columnIndex) {
#         const table = document.querySelector('table');
#         const className = 'col-hidden-' + columnIndex;
#         const btn = document.getElementById('col-toggle-' + columnIndex);
        
#         if (table.classList.contains(className)) {
#             table.classList.remove(className);
#             btn.classList.add('active');
#             btn.textContent = btn.textContent.replace('Show Column', 'Hide Column');
#         } else {
#             table.classList.add(className);
#             btn.classList.remove('active');
#             btn.textContent = btn.textContent.replace('Hide Column', 'Show Column');
#         }
#     }
    
#     // Data visibility toggle - hides only content, keeps toggle buttons
#     function toggleAllData(columnIndex) {
#         const table = document.querySelector('table');
#         const className = 'data-hidden-' + columnIndex;
#         const btn = document.getElementById('data-toggle-' + columnIndex);
        
#         if (table.classList.contains(className)) {
#             table.classList.remove(className);
#             btn.classList.add('active');
#             btn.textContent = btn.textContent.replace('Expand All', 'Collapse All');
#         } else {
#             table.classList.add(className);
#             btn.classList.remove('active');
#             btn.textContent = btn.textContent.replace('Collapse All', 'Expand All');
#         }
#     }
    
#     // Cell content toggle functionality - individual cells
#     function toggleCellContent(cellId) {
#         const content = document.getElementById(cellId);
#         const btn = event.target;
        
#         if (content.classList.contains('cell-content-hidden')) {
#             content.classList.remove('cell-content-hidden');
#             btn.textContent = '▼ Hide';
#         } else {
#             content.classList.add('cell-content-hidden');
#             btn.textContent = '▶ Show';
#         }
#     }
    
#     // Initialize all buttons as active (visible/expanded)
#     window.addEventListener('DOMContentLoaded', function() {
#         for (let i = 1; i <= 3; i++) {
#             const colBtn = document.getElementById('col-toggle-' + i);
#             const dataBtn = document.getElementById('data-toggle-' + i);
#             if (colBtn) colBtn.classList.add('active');
#             if (dataBtn) dataBtn.classList.add('active');
#         }
#     });
#     """
    
#     # Insert script before closing body tag
#     body_tag = target_soup.find('body')
#     if body_tag:
#         body_tag.append(script_tag)


# def add_control_panel(target_soup):
#     """
#     Add a control panel with column visibility and data visibility controls.
    
#     Args:
#         target_soup: BeautifulSoup object of the target HTML
#     """
    
#     control_panel_html = """
#     <div class="control-panel">
#         <h3>🎛️ Column Controls</h3>
#         <div style="margin-bottom: 10px;">
#             <strong>Hide/Show Entire Column:</strong><br>
#             <button id="col-toggle-1" class="toggle-btn" onclick="toggleColumn(1)">Hide Column: Grammar Point</button>
#             <button id="col-toggle-2" class="toggle-btn" onclick="toggleColumn(2)">Hide Column: How to Use</button>
#             <button id="col-toggle-3" class="toggle-btn" onclick="toggleColumn(3)">Hide Column: Examples</button>
#         </div>
#         <div>
#             <strong>Collapse/Expand All Data (keeps toggle buttons):</strong><br>
#             <button id="data-toggle-1" class="toggle-btn" onclick="toggleAllData(1)">Collapse All: Grammar Point</button>
#             <button id="data-toggle-2" class="toggle-btn" onclick="toggleAllData(2)">Collapse All: How to Use</button>
#             <button id="data-toggle-3" class="toggle-btn" onclick="toggleAllData(3)">Collapse All: Examples</button>
#         </div>
#     </div>
#     """
    
#     control_panel = BeautifulSoup(control_panel_html, 'html.parser')
    
#     # Insert before the table
#     table_div = target_soup.find('div', class_='table-responsive')
#     if table_div:
#         table_div.insert_before(control_panel)


# def merge_tables_enhanced(target_file, how_to_use_data, output_file):
#     """
#     Enhanced merge with all features.
#     """
#     print(f"\nReading target file: {target_file}")
    
#     with open(target_file, 'r', encoding='utf-8') as f:
#         target_html = f.read()
    
#     target_soup = BeautifulSoup(target_html, 'html.parser')
    
#     # Update header
#     print("Updating table header...")
#     thead = target_soup.find('thead')
#     header_row = thead.find('tr')
#     header_cells = list(header_row.find_all('th', recursive=False))
    
#     new_header = target_soup.new_tag('th')
#     new_header.string = "How to Use"
#     header_cells[2].insert_before(new_header)
    
#     print("Header structure:")
#     for i, th in enumerate(header_row.find_all('th', recursive=False)):
#         print(f"  Column {i}: {th.get_text(strip=True)}")
    
#     # Update body rows
#     print("\nUpdating table body rows with enhanced features...")
#     tbody = target_soup.find('tbody')
#     all_rows = tbody.find_all('tr', recursive=False)
    
#     success_count = 0
    
#     for row_idx, row in enumerate(all_rows):
#         row_cells = list(row.find_all('td', recursive=False))
#         number = row_cells[0].get_text(strip=True)
        
#         # Add toggle to Grammar Point cell (column 1) - ALWAYS
#         grammar_cell = row_cells[1]
#         grammar_toggle = target_soup.new_tag('button',
#                                             onclick=f'toggleCellContent("grammar-content-{number}")',
#                                             **{'class': 'cell-toggle-btn toggle-btn'})
#         grammar_toggle.string = '▼ Hide'
        
#         # Wrap existing grammar content with special class for data-level hiding
#         grammar_wrapper = target_soup.new_tag('div', 
#                                               id=f'grammar-content-{number}',
#                                               **{'class': 'grammar-data-content'})
#         for child in list(grammar_cell.children):
#             grammar_wrapper.append(child)
        
#         grammar_cell.clear()
#         grammar_cell.append(grammar_toggle)
#         grammar_cell.append(grammar_wrapper)
        
#         # Create new cell for "How to Use"
#         new_cell = target_soup.new_tag('td')
        
#         # Add cell toggle button - ALWAYS present
#         toggle_btn = target_soup.new_tag('button', 
#                                          onclick=f'toggleCellContent("how-to-use-content-{number}")',
#                                          **{'class': 'cell-toggle-btn toggle-btn'})
#         toggle_btn.string = '▼ Hide'
#         new_cell.append(toggle_btn)
        
#         # Add content wrapper with special class for data-level hiding
#         content_wrapper = target_soup.new_tag('div', 
#                                               id=f'how-to-use-content-{number}',
#                                               **{'class': 'how-to-use-data-content'})
        
#         if number in how_to_use_data:
#             data = how_to_use_data[number]
            
#             # Add the usage table/content with highlighting
#             enhanced_content = add_highlighting_to_usage_table(data['content'])
#             content_soup = BeautifulSoup(enhanced_content, 'html.parser')
#             for element in content_soup:
#                 content_wrapper.append(element)
            
#             # Add source link if available
#             if data['url']:
#                 source_link = target_soup.new_tag('a', 
#                                                  href=data['url'],
#                                                  target='_blank',
#                                                  **{'class': 'source-link'})
#                 source_link.string = '📚 Source: JLPT Sensei'
#                 content_wrapper.append(target_soup.new_tag('br'))
#                 content_wrapper.append(source_link)
#         else:
#             # No data available
#             no_data = target_soup.new_tag('p')
#             no_data.string = '(no usage table)'
#             content_wrapper.append(no_data)
        
#         new_cell.append(content_wrapper)
        
#         # Insert the How to Use cell
#         row_cells[2].insert_before(new_cell)
        
#         # Add toggle to Examples cell (column 3, now column 4 after insertion) - ALWAYS
#         examples_cell = row.find_all('td', recursive=False)[3]  # Get updated cell list
#         examples_toggle = target_soup.new_tag('button',
#                                              onclick=f'toggleCellContent("examples-content-{number}")',
#                                              **{'class': 'cell-toggle-btn toggle-btn'})
#         examples_toggle.string = '▼ Hide'
        
#         # Wrap existing examples content with special class for data-level hiding
#         examples_wrapper = target_soup.new_tag('div', 
#                                                id=f'examples-content-{number}',
#                                                **{'class': 'examples-data-content'})
#         for child in list(examples_cell.children):
#             examples_wrapper.append(child)
        
#         examples_cell.clear()
#         examples_cell.append(examples_toggle)
#         examples_cell.append(examples_wrapper)
        
#         success_count += 1
    
#     print(f"✓ Successfully processed {success_count} rows")
    
#     # Add control panel and enhanced features
#     print("\nAdding enhanced features...")
#     add_control_panel(target_soup)
#     create_enhanced_html(target_soup)
    
#     # Save
#     print(f"\nSaving enhanced file to: {output_file}")
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write(target_soup.prettify())
    
#     print("✓ Enhanced merge complete!")
#     return True


# def main():
#     if len(sys.argv) < 4:
#         print("Usage: python merge_grammar_tables.py <source_file> <target_file> <output_file> [--no-fetch]")
#         print("\nOptions:")
#         print("  --no-fetch    Skip fetching missing usage tables from URLs")
#         sys.exit(1)
    
#     source_file = sys.argv[1]
#     target_file = sys.argv[2]
#     output_file = sys.argv[3]
#     fetch_missing = '--no-fetch' not in sys.argv
    
#     print("=" * 70)
#     print("Enhanced Grammar Table Merger")
#     print("=" * 70)
    
#     # Extract data
#     how_to_use_data = extract_how_to_use_data(source_file, fetch_missing)
    
#     if not how_to_use_data:
#         print("ERROR: No data extracted. Exiting.")
#         sys.exit(1)
    
#     # Merge with enhancements
#     success = merge_tables_enhanced(target_file, how_to_use_data, output_file)
    
#     if success:
#         print("\n" + "=" * 70)
#         print("SUCCESS! Enhanced file created with:")
#         print("  ✓ 3 buttons to hide/show entire columns")
#         print("  ✓ 3 buttons to collapse/expand all data (keeps toggle buttons)")
#         print("  ✓ Individual cell toggle buttons in all data columns")
#         print("  ✓ Source hyperlinks in How to Use cells")
#         print("  ✓ Auto-fetched missing usage tables")
#         print("  ✓ Color-coded highlighting")
#         print("=" * 70)


# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
"""
Enhanced Grammar Table Merger Script
Features:
1. Column-level toggle buttons
2. Cell-level toggle buttons for Grammar Point & How to Use columns
3. Source hyperlinks in How to Use column
4. Web scraping for empty How to Use cells
5. Color-coded How to Use column matching Example column

Usage:
    python merge_grammar_tables.py <source_file> <target_file> <output_file> [--no-fetch]

Example:
    python merge_grammar_tables.py N5_Grammar.html N5-G-Table.html N5-G-Table-Enhanced.html
"""

import sys
import re
from bs4 import BeautifulSoup
import urllib.request
import time


def fetch_usage_table_from_url(url):
    """
    Fetch the usage table from a JLPT Sensei URL.
    
    Args:
        url: The URL to fetch from
        
    Returns:
        HTML string of the usage table, or None if not found
    """
    try:
        print(f"    Fetching from: {url}")
        
        # Add headers to avoid being blocked
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for usage table - it typically has class "usage" or is in a specific section
        usage_table = soup.find('table', class_='usage')
        
        if not usage_table:
            # Try alternative selectors
            usage_table = soup.find('table', class_='table-bordered')
        
        if usage_table:
            print(f"    ✓ Found usage table")
            return str(usage_table)
        else:
            print(f"    ✗ No usage table found")
            return None
            
    except Exception as e:
        print(f"    ✗ Error fetching URL: {e}")
        return None


def extract_how_to_use_data(source_file, fetch_missing=True):
    """
    Extract 'How to Use' data from the source HTML file.
    Also extracts source URLs and fetches missing data if needed.
    
    Args:
        source_file: Path to the source HTML file
        fetch_missing: Whether to fetch from URLs for empty cells
        
    Returns:
        Dictionary with 'content' and 'url' for each row number
    """
    print(f"Reading source file: {source_file}")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        source_html = f.read()
    
    source_soup = BeautifulSoup(source_html, 'html.parser')
    source_tbody = source_soup.find('tbody')
    
    if not source_tbody:
        print("ERROR: Could not find <tbody> in source file")
        return {}
    
    source_rows = source_tbody.find_all('tr', recursive=False)
    how_to_use_data = {}
    
    for row in source_rows:
        cells = row.find_all('td', recursive=False)
        
        if len(cells) >= 5:
            number = cells[0].get_text(strip=True)
            
            # Get How to Use content (column 3)
            how_to_use_inner = ''.join(str(child) for child in cells[3].children)
            
            # Get source URL from Examples column (column 4)
            examples_cell = cells[4]
            link = examples_cell.find('a', href=True)
            source_url = link['href'] if link else None
            
            # Check if How to Use is empty/minimal
            text_content = cells[3].get_text(strip=True)
            is_empty = len(text_content) < 20
            
            # If empty and we have a URL, try to fetch the table
            if is_empty and source_url and fetch_missing:
                print(f"  Row {number}: How to Use is minimal, fetching from URL...")
                fetched_table = fetch_usage_table_from_url(source_url)
                if fetched_table:
                    how_to_use_inner = fetched_table
                time.sleep(0.5)  # Be nice to the server
            
            how_to_use_data[number] = {
                'content': how_to_use_inner,
                'url': source_url
            }
    
    print(f"✓ Extracted data for {len(how_to_use_data)} entries")
    return how_to_use_data


def add_highlighting_to_usage_table(usage_content):
    """
    Add color highlighting to the usage table to match the example column style.
    Highlights verb forms, particles, and grammar patterns.
    
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
                # Find and wrap the pattern
                new_html = str(cell)
                new_html = new_html.replace(pattern, f'<span class="hl-grammar">{pattern}</span>')
                cell.replace_with(BeautifulSoup(new_html, 'html.parser'))
                break
    
    return str(soup)


def create_enhanced_html(target_soup):
    """
    Add JavaScript for toggle functionality and enhanced styles.
    
    Args:
        target_soup: BeautifulSoup object of the target HTML
    """
    
    # Add CSS for toggle buttons and hidden state
    style_tag = target_soup.find('style')
    if style_tag:
        additional_css = """
        
        /* Toggle buttons */
        .toggle-btn {
            background-color: #6c757d;
            color: white;
            border: none;
            padding: 3px 8px;
            margin: 2px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.75rem;
            transition: all 0.3s;
        }
        
        .toggle-btn:hover {
            background-color: #5a6268;
            transform: scale(1.05);
        }
        
        .toggle-btn.active {
            background-color: #28a745;
        }
        
        .cell-toggle-btn {
            background-color: #17a2b8;
            padding: 2px 6px;
            font-size: 0.7rem;
            margin-bottom: 5px;
            display: inline-block;
        }
        
        .cell-toggle-btn:hover {
            background-color: #138496;
        }
        
        /* Column visibility - hides entire column */
        .col-hidden-1 td:nth-child(2),
        .col-hidden-1 th:nth-child(2) {
            display: none;
        }
        
        .col-hidden-2 td:nth-child(3),
        .col-hidden-2 th:nth-child(3) {
            display: none;
        }
        
        .col-hidden-3 td:nth-child(4),
        .col-hidden-3 th:nth-child(4) {
            display: none;
        }
        
        /* Data visibility - hides only content, keeps toggle buttons */
        .data-hidden-1 .grammar-data-content {
            display: none;
        }
        
        .data-hidden-2 .how-to-use-data-content {
            display: none;
        }
        
        .data-hidden-3 .examples-data-content {
            display: none;
        }
        
        /* Individual cell override - when manually shown, override collapse-all */
        .data-hidden-1 .grammar-data-content.force-visible,
        .data-hidden-2 .how-to-use-data-content.force-visible,
        .data-hidden-3 .examples-data-content.force-visible {
            display: block !important;
        }
        
        /* Cell content visibility */
        .cell-content-hidden {
            display: none;
        }
        
        /* Source link styling */
        .source-link {
            display: block;
            margin-top: 8px;
            font-size: 0.8rem;
            color: #0d6efd;
            text-decoration: none;
        }
        
        .source-link:hover {
            text-decoration: underline;
        }
        
        /* Control panel */
        .control-panel {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
        }
        
        .control-panel h3 {
            font-size: 1rem;
            margin-bottom: 10px;
            color: #495057;
        }
        """
        style_tag.string += additional_css
    
    # Add JavaScript for toggle functionality
    script_tag = target_soup.new_tag('script')
    script_tag.string = """
    // Column visibility toggle - hides entire column
    function toggleColumn(columnIndex) {
        const table = document.querySelector('table');
        const className = 'col-hidden-' + columnIndex;
        const btn = document.getElementById('col-toggle-' + columnIndex);
        
        if (table.classList.contains(className)) {
            table.classList.remove(className);
            btn.classList.add('active');
            btn.textContent = btn.textContent.replace('Show Column', 'Hide Column');
        } else {
            table.classList.add(className);
            btn.classList.remove('active');
            btn.textContent = btn.textContent.replace('Hide Column', 'Show Column');
        }
    }
    
    // Data visibility toggle - hides only content, keeps toggle buttons
    function toggleAllData(columnIndex) {
        const table = document.querySelector('table');
        const className = 'data-hidden-' + columnIndex;
        const btn = document.getElementById('data-toggle-' + columnIndex);
        
        // Determine which class to look for based on column
        let contentClass;
        if (columnIndex === 1) contentClass = 'grammar-data-content';
        else if (columnIndex === 2) contentClass = 'how-to-use-data-content';
        else if (columnIndex === 3) contentClass = 'examples-data-content';
        
        if (table.classList.contains(className)) {
            // Currently collapsed, expanding all
            table.classList.remove(className);
            btn.classList.add('active');
            btn.textContent = btn.textContent.replace('Expand All', 'Collapse All');
            
            // Update all cell buttons to show "Hide" (since data is now visible by default)
            const allCells = document.querySelectorAll('.' + contentClass);
            allCells.forEach(cell => {
                // Only update cells that don't have force-visible (weren't manually toggled)
                if (!cell.classList.contains('force-visible')) {
                    cell.classList.remove('cell-content-hidden');
                    const cellBtn = cell.previousElementSibling;
                    if (cellBtn && cellBtn.classList.contains('cell-toggle-btn')) {
                        cellBtn.textContent = '▼ Hide';
                    }
                }
                // Remove force-visible since we're back to normal state
                cell.classList.remove('force-visible');
            });
        } else {
            // Currently expanded, collapsing all
            table.classList.add(className);
            btn.classList.remove('active');
            btn.textContent = btn.textContent.replace('Collapse All', 'Expand All');
            
            // Update all cell buttons to show "Show" and remove individual toggles
            const allCells = document.querySelectorAll('.' + contentClass);
            allCells.forEach(cell => {
                // Remove both force-visible and individual cell-content-hidden
                cell.classList.remove('force-visible');
                cell.classList.remove('cell-content-hidden');
                
                const cellBtn = cell.previousElementSibling;
                if (cellBtn && cellBtn.classList.contains('cell-toggle-btn')) {
                    cellBtn.textContent = '▶ Show';
                }
            });
        }
    }
    
    // Cell content toggle functionality - individual cells
    function toggleCellContent(cellId) {
        const content = document.getElementById(cellId);
        const btn = event.target;
        
        // Check if content is hidden by individual toggle OR by collapse-all
        const isHiddenByToggle = content.classList.contains('cell-content-hidden');
        const isForceVisible = content.classList.contains('force-visible');
        
        if (isHiddenByToggle) {
            // Was hidden by individual toggle, show it
            content.classList.remove('cell-content-hidden');
            content.classList.add('force-visible');  // Override collapse-all
            btn.textContent = '▼ Hide';
        } else {
            // Was visible, hide it
            content.classList.add('cell-content-hidden');
            content.classList.remove('force-visible');  // Remove override
            btn.textContent = '▶ Show';
        }
    }
    
    // Initialize all buttons as active (visible/expanded)
    window.addEventListener('DOMContentLoaded', function() {
        for (let i = 1; i <= 3; i++) {
            const colBtn = document.getElementById('col-toggle-' + i);
            const dataBtn = document.getElementById('data-toggle-' + i);
            if (colBtn) colBtn.classList.add('active');
            if (dataBtn) dataBtn.classList.add('active');
        }
    });
    """
    
    # Insert script before closing body tag
    body_tag = target_soup.find('body')
    if body_tag:
        body_tag.append(script_tag)


def add_control_panel(target_soup):
    """
    Add a control panel with column visibility and data visibility controls.
    
    Args:
        target_soup: BeautifulSoup object of the target HTML
    """
    
    control_panel_html = """
    <div class="control-panel">
        <h3>🎛️ Column Controls</h3>
        <div style="margin-bottom: 10px;">
            <strong>Hide/Show Entire Column:</strong><br>
            <button id="col-toggle-1" class="toggle-btn" onclick="toggleColumn(1)">Hide Column: Grammar Point</button>
            <button id="col-toggle-2" class="toggle-btn" onclick="toggleColumn(2)">Hide Column: How to Use</button>
            <button id="col-toggle-3" class="toggle-btn" onclick="toggleColumn(3)">Hide Column: Examples</button>
        </div>
        <div>
            <strong>Collapse/Expand All Data (keeps toggle buttons):</strong><br>
            <button id="data-toggle-1" class="toggle-btn" onclick="toggleAllData(1)">Collapse All: Grammar Point</button>
            <button id="data-toggle-2" class="toggle-btn" onclick="toggleAllData(2)">Collapse All: How to Use</button>
            <button id="data-toggle-3" class="toggle-btn" onclick="toggleAllData(3)">Collapse All: Examples</button>
        </div>
    </div>
    """
    
    control_panel = BeautifulSoup(control_panel_html, 'html.parser')
    
    # Insert before the table
    table_div = target_soup.find('div', class_='table-responsive')
    if table_div:
        table_div.insert_before(control_panel)


def merge_tables_enhanced(target_file, how_to_use_data, output_file):
    """
    Enhanced merge with all features.
    """
    print(f"\nReading target file: {target_file}")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        target_html = f.read()
    
    target_soup = BeautifulSoup(target_html, 'html.parser')
    
    # Update header
    print("Updating table header...")
    thead = target_soup.find('thead')
    header_row = thead.find('tr')
    header_cells = list(header_row.find_all('th', recursive=False))
    
    new_header = target_soup.new_tag('th')
    new_header.string = "How to Use"
    header_cells[2].insert_before(new_header)
    
    print("Header structure:")
    for i, th in enumerate(header_row.find_all('th', recursive=False)):
        print(f"  Column {i}: {th.get_text(strip=True)}")
    
    # Update body rows
    print("\nUpdating table body rows with enhanced features...")
    tbody = target_soup.find('tbody')
    all_rows = tbody.find_all('tr', recursive=False)
    
    success_count = 0
    
    for row_idx, row in enumerate(all_rows):
        row_cells = list(row.find_all('td', recursive=False))
        number = row_cells[0].get_text(strip=True)
        
        # Add toggle to Grammar Point cell (column 1) - ALWAYS
        grammar_cell = row_cells[1]
        grammar_toggle = target_soup.new_tag('button',
                                            onclick=f'toggleCellContent("grammar-content-{number}")',
                                            **{'class': 'cell-toggle-btn toggle-btn'})
        grammar_toggle.string = '▼ Hide'
        
        # Wrap existing grammar content with special class for data-level hiding
        grammar_wrapper = target_soup.new_tag('div', 
                                              id=f'grammar-content-{number}',
                                              **{'class': 'grammar-data-content'})
        for child in list(grammar_cell.children):
            grammar_wrapper.append(child)
        
        grammar_cell.clear()
        grammar_cell.append(grammar_toggle)
        grammar_cell.append(grammar_wrapper)
        
        # Create new cell for "How to Use"
        new_cell = target_soup.new_tag('td')
        
        # Add cell toggle button - ALWAYS present
        toggle_btn = target_soup.new_tag('button', 
                                         onclick=f'toggleCellContent("how-to-use-content-{number}")',
                                         **{'class': 'cell-toggle-btn toggle-btn'})
        toggle_btn.string = '▼ Hide'
        new_cell.append(toggle_btn)
        
        # Add content wrapper with special class for data-level hiding
        content_wrapper = target_soup.new_tag('div', 
                                              id=f'how-to-use-content-{number}',
                                              **{'class': 'how-to-use-data-content'})
        
        if number in how_to_use_data:
            data = how_to_use_data[number]
            
            # Add the usage table/content with highlighting
            enhanced_content = add_highlighting_to_usage_table(data['content'])
            content_soup = BeautifulSoup(enhanced_content, 'html.parser')
            for element in content_soup:
                content_wrapper.append(element)
            
            # Add source link if available
            if data['url']:
                source_link = target_soup.new_tag('a', 
                                                 href=data['url'],
                                                 target='_blank',
                                                 **{'class': 'source-link'})
                source_link.string = '📚 Source: JLPT Sensei'
                content_wrapper.append(target_soup.new_tag('br'))
                content_wrapper.append(source_link)
        else:
            # No data available
            no_data = target_soup.new_tag('p')
            no_data.string = '(no usage table)'
            content_wrapper.append(no_data)
        
        new_cell.append(content_wrapper)
        
        # Insert the How to Use cell
        row_cells[2].insert_before(new_cell)
        
        # Add toggle to Examples cell (column 3, now column 4 after insertion) - ALWAYS
        examples_cell = row.find_all('td', recursive=False)[3]  # Get updated cell list
        examples_toggle = target_soup.new_tag('button',
                                             onclick=f'toggleCellContent("examples-content-{number}")',
                                             **{'class': 'cell-toggle-btn toggle-btn'})
        examples_toggle.string = '▼ Hide'
        
        # Wrap existing examples content with special class for data-level hiding
        examples_wrapper = target_soup.new_tag('div', 
                                               id=f'examples-content-{number}',
                                               **{'class': 'examples-data-content'})
        for child in list(examples_cell.children):
            examples_wrapper.append(child)
        
        examples_cell.clear()
        examples_cell.append(examples_toggle)
        examples_cell.append(examples_wrapper)
        
        success_count += 1
    
    print(f"✓ Successfully processed {success_count} rows")
    
    # Add control panel and enhanced features
    print("\nAdding enhanced features...")
    add_control_panel(target_soup)
    create_enhanced_html(target_soup)
    
    # Save
    print(f"\nSaving enhanced file to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(target_soup.prettify())
    
    print("✓ Enhanced merge complete!")
    return True


def main():
    if len(sys.argv) < 4:
        print("Usage: python merge_grammar_tables.py <source_file> <target_file> <output_file> [--no-fetch]")
        print("\nOptions:")
        print("  --no-fetch    Skip fetching missing usage tables from URLs")
        sys.exit(1)
    
    source_file = sys.argv[1]
    target_file = sys.argv[2]
    output_file = sys.argv[3]
    fetch_missing = '--no-fetch' not in sys.argv
    
    print("=" * 70)
    print("Enhanced Grammar Table Merger")
    print("=" * 70)
    
    # Extract data
    how_to_use_data = extract_how_to_use_data(source_file, fetch_missing)
    
    if not how_to_use_data:
        print("ERROR: No data extracted. Exiting.")
        sys.exit(1)
    
    # Merge with enhancements
    success = merge_tables_enhanced(target_file, how_to_use_data, output_file)
    
    if success:
        print("\n" + "=" * 70)
        print("SUCCESS! Enhanced file created with:")
        print("  ✓ 3 buttons to hide/show entire columns")
        print("  ✓ 3 buttons to collapse/expand all data (keeps toggle buttons)")
        print("  ✓ Individual cell toggle buttons in all data columns")
        print("  ✓ Source hyperlinks in How to Use cells")
        print("  ✓ Auto-fetched missing usage tables")
        print("  ✓ Color-coded highlighting")
        print("=" * 70)


if __name__ == "__main__":
    main()