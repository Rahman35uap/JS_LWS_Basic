#!/usr/bin/env python3
"""
Examples Column Formatter Script
This script adds proper line breaks and spacing to the Examples column for better readability.

Usage:
    python format_examples.py <input_html_file> <output_html_file>

Example:
    python format_examples.py N5-G-Table-Final.html N5-G-Table-Formatted.html
"""

import sys
from bs4 import BeautifulSoup


def format_examples_column(input_file, output_file):
    """
    Add proper spacing and line breaks to Examples column.
    
    Args:
        input_file: Path to input HTML file
        output_file: Path to output HTML file with formatted examples
    """
    print("=" * 70)
    print("Examples Column Formatter")
    print("=" * 70)
    print(f"\nReading file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find existing style tag
    style_tag = soup.find('style')
    
    if style_tag:
        # Add enhanced spacing CSS for examples
        additional_css = """
        
        /* ========================================
           ENHANCED EXAMPLES COLUMN FORMATTING
           ======================================== */
        
        /* Example block container */
        .example-block {
            padding: 12px 0;
            line-height: 1.8;
        }
        
        /* Japanese text with furigana */
        .example-jp {
            font-weight: 500;
            color: #198754;
            font-size: 1.1rem;
            margin-bottom: 16px;
            line-height: 2;
            display: block;
        }
        
        /* English translation */
        .example-en {
            display: block;
            font-size: 0.9rem;
            color: #495057;
            margin-bottom: 12px;
            margin-top: 16px;
            line-height: 1.6;
        }
        
        /* Bengali/other translation */
        .example-bn {
            display: block;
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 8px;
            line-height: 1.6;
        }
        
        /* Divider between examples */
        .example-divider {
            margin: 15px 0;
            border: 0;
            border-top: 1px solid #dee2e6;
            opacity: 0.5;
        }
        
        /* Ruby (furigana) spacing */
        ruby {
            ruby-position: over;
        }
        
        ruby rt {
            font-size: 0.55em;
            color: #6c757d;
            line-height: 1;
            margin-bottom: 2px;
        }
        
        /* Add breathing room around highlighted grammar */
        .example-jp .hl-grammar,
        .example-jp .hl-verb,
        .example-jp .hl-subj,
        .example-jp .hl-obj {
            padding: 0 2px;
        }
        
        /* Responsive adjustments for examples */
        @media screen and (max-width: 768px) {
            .example-jp {
                font-size: 1rem;
                margin-bottom: 6px;
                line-height: 1.9;
            }
            
            .example-en, .example-bn {
                font-size: 0.85rem;
                margin-bottom: 5px;
            }
            
            .example-block {
                padding: 10px 0;
            }
            
            ruby rt {
                font-size: 0.5em;
            }
        }
        
        @media screen and (max-width: 480px) {
            .example-jp {
                font-size: 0.9rem;
                line-height: 1.8;
            }
            
            .example-en, .example-bn {
                font-size: 0.75rem;
            }
            
            .example-block {
                padding: 8px 0;
            }
        }
        """
        
        style_tag.string += additional_css
        print("✅ Enhanced CSS for examples added")
    
    # Find all example blocks and ensure proper structure
    tbody = soup.find('tbody')
    if not tbody:
        print("⚠️  No tbody found")
        return False
    
    all_rows = tbody.find_all('tr', recursive=False)
    formatted_count = 0
    
    print(f"\nProcessing {len(all_rows)} rows...")
    
    for row in all_rows:
        cells = row.find_all('td', recursive=False)
        
        # Find the Examples column (should be the last column, index -1)
        if len(cells) >= 4:
            examples_cell = cells[-1]
            
            # Find all example blocks within this cell
            example_blocks = examples_cell.find_all('div', class_='example-block')
            
            for block in example_blocks:
                # Find Japanese, English, and Bengali paragraphs
                jp_elem = block.find('p', class_='example-jp')
                en_elem = block.find('p', class_='example-en')
                bn_elem = block.find('p', class_='example-bn')
                
                # Ensure proper spacing by verifying they're block elements
                if jp_elem:
                    # Already has class, just ensure it's a block
                    jp_elem['style'] = jp_elem.get('style', '') + ' display: block; margin-bottom: 16px;'
                
                if en_elem:
                    en_elem['style'] = en_elem.get('style', '') + ' display: block; margin-top: 16px; margin-bottom: 12px;'
                
                if bn_elem:
                    bn_elem['style'] = bn_elem.get('style', '') + ' display: block; margin-bottom: 8px;'
                
                formatted_count += 1
    
    print(f"✅ Formatted {formatted_count} example blocks")
    
    # Save the file
    print(f"\n💾 Saving formatted file to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print("✅ File saved successfully!")
    
    print("\n" + "=" * 70)
    print("Formatting Applied:")
    print("=" * 70)
    print("  ✅ Double line spacing between JP/EN/BN")
    print("  ✅ Better furigana positioning and spacing")
    print("  ✅ Enhanced divider visibility between examples")
    print("  ✅ Improved readability on all devices")
    print("  ✅ Breathing room around highlighted text")
    print("=" * 70)
    
    return True


def main():
    if len(sys.argv) != 3:
        print("Usage: python format_examples.py <input_html_file> <output_html_file>")
        print("\nExample:")
        print("  python format_examples.py N5-G-Table-Final.html N5-G-Table-Formatted.html")
        print("\nThis script adds proper line breaks and spacing to the Examples column")
        print("for better readability and comfort.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    success = format_examples_column(input_file, output_file)
    
    if success:
        print("\n✅ SUCCESS! Examples column is now properly formatted!")
        print("\nFormatting includes:")
        print("  📝 Japanese text with proper furigana spacing")
        print("  📝 Clear separation between JP/EN/BN translations")
        print("  📝 Enhanced readability on mobile devices")
    else:
        print("\n❌ Failed to format examples column")
        sys.exit(1)


if __name__ == "__main__":
    main()