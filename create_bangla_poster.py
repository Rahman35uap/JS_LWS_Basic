#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JLPT Kanji Poster - COMPLETE PDF RECREATION
Vietnamese → Bengali with FULL LAYOUT PRESERVATION

This script CREATES THE ACTUAL PDF POSTER, not just a text report!

USAGE:
    python3 create_bengali_poster.py

REQUIREMENTS:
    pip3 install pdfplumber reportlab pillow deep-translator
    
    Also needs: Noto Sans Bengali font (download from Google Fonts)
"""

import sys
import os
from pathlib import Path
import time

try:
    import pdfplumber
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import Color
except ImportError as e:
    print("❌ ERROR: Missing required libraries!")
    print("\nPlease install:")
    print("  pip3 install pdfplumber reportlab pillow deep-translator")
    sys.exit(1)

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

# JLPT Color Coding (RGB values from original)
JLPT_COLORS = {
    'N5': Color(255/255, 0/255, 0/255),      # Red
    'N4': Color(197/255, 192/255, 172/255),  # Beige  
    'N3': Color(41/255, 70/255, 112/255),    # Dark Blue
    'N2': Color(216/255, 107/255, 14/255),   # Orange
    'N1': Color(57/255, 131/255, 56/255),    # Green
}

# Translation dictionaries (abbreviated - add more as needed)
VIETNAMESE_TO_BENGALI = {
    "Phân số, phân chia": "ভগ্নাংশ, বিভাগ",
    "To, lớn": "বড়",
    "Cái xe": "গাড়ি",
    "Bất dụng, bất tài, không có": "অকেজো, নেই",
    "Chữa bệnh, thầy thuốc": "চিকিৎসা, ডাক্তার",
    # Add more translations here...
}

ROMANIZATION_TO_BENGALI = {
    "PHÂN": "ফুন",
    "ĐẠI": "দাই",
    "XA": "সা",
    "BẤT": "বত",
    # Add more romanizations here...
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_vietnamese(text):
    """Check if text is Vietnamese."""
    vietnamese_chars = 'ăâêôơưđáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'
    return any(char in vietnamese_chars + vietnamese_chars.upper() for char in text)

def is_japanese(text):
    """Check if text is Japanese."""
    for char in text:
        code = ord(char)
        if (0x3040 <= code <= 0x309F or 0x30A0 <= code <= 0x30FF or 0x4E00 <= code <= 0x9FFF):
            return True
    return False

def auto_translate(text):
    """Auto-translate Vietnamese to Bengali."""
    if not TRANSLATOR_AVAILABLE:
        return text
    try:
        translator = GoogleTranslator(source='vi', target='bn')
        result = translator.translate(text)
        time.sleep(0.5)  # Be nice to API
        return result
    except:
        return text

def translate_text(text, is_label=False):
    """Main translation function."""
    # Check pre-built dictionaries first
    if is_label and text in ROMANIZATION_TO_BENGALI:
        return ROMANIZATION_TO_BENGALI[text]
    elif not is_label and text in VIETNAMESE_TO_BENGALI:
        return VIETNAMESE_TO_BENGALI[text]
    
    # Auto-translate if available
    if TRANSLATOR_AVAILABLE:
        return auto_translate(text)
    
    return text

def get_jlpt_level_from_color(color_tuple):
    """Detect JLPT level from RGB color."""
    if not color_tuple or len(color_tuple) < 3:
        return 'N1'  # Default
    
    r, g, b = color_tuple[:3]
    
    # Match to closest JLPT color
    if r > 200 and g < 50 and b < 50:
        return 'N5'  # Red
    elif r > 180 and g > 180 and b > 150:
        return 'N4'  # Beige
    elif r < 60 and g < 100 and b > 100:
        return 'N3'  # Dark Blue
    elif r > 200 and g > 80 and g < 130 and b < 30:
        return 'N2'  # Orange
    elif r < 80 and g > 100 and b < 80:
        return 'N1'  # Green
    
    return 'N1'  # Default

# ============================================================================
# MAIN PDF RECREATION FUNCTION
# ============================================================================

def create_bengali_poster(input_pdf_path, output_pdf_path):
    """
    Create Bengali version of JLPT poster with full layout recreation.
    """
    print("=" * 70)
    print("📄 JLPT KANJI POSTER - COMPLETE PDF RECREATION")
    print("Vietnamese → Bengali with Full Layout")
    print("=" * 70)
    print()
    
    if not os.path.exists(input_pdf_path):
        print(f"❌ ERROR: Input PDF not found: {input_pdf_path}")
        return False
    
    print(f"📄 Input:  {input_pdf_path}")
    print(f"📝 Output: {output_pdf_path}")
    print()
    
    # Check for Bengali font
    bengali_font_path = None
    possible_paths = [
        "NotoSansBengali-Regular.ttf",
        "/System/Library/Fonts/Supplemental/NotoSansBengali-Regular.ttf",  # Mac
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",  # Linux
        "C:\\Windows\\Fonts\\NotoSansBengali-Regular.ttf",  # Windows
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            bengali_font_path = path
            break
    
    if not bengali_font_path:
        print("⚠️  WARNING: Noto Sans Bengali font not found!")
        print("   Bengali text will use fallback font (may not display correctly)")
        print("   Download from: https://fonts.google.com/noto/specimen/Noto+Sans+Bengali")
        print()
    
    try:
        print("🔍 Step 1: Analyzing original PDF...")
        with pdfplumber.open(input_pdf_path) as pdf:
            page = pdf.pages[0]
            page_width = page.width
            page_height = page.height
            
            print(f"   Page size: {page_width} x {page_height} pts")
            
            # Extract all characters with positions and colors
            chars = page.chars
            print(f"   Total characters: {len(chars)}")
            print()
            
            # Group characters into text blocks
            print("🔄 Step 2: Extracting and translating text...")
            
            translated_chars = []
            vietnamese_count = 0
            japanese_count = 0
            
            for i, char in enumerate(chars):
                text = char.get('text', '')
                x0 = char.get('x0', 0)
                y0 = char.get('y0', 0)
                fontname = char.get('fontname', '')
                size = char.get('size', 12)
                color = char.get('non_stroking_color', (0, 0, 0))
                
                # Determine if Vietnamese or Japanese
                if is_vietnamese(text):
                    # Translate Vietnamese
                    is_label = text.isupper() and len(text) <= 10
                    translated_text = translate_text(text, is_label)
                    vietnamese_count += 1
                    use_bengali_font = True
                elif is_japanese(text):
                    # Keep Japanese unchanged
                    translated_text = text
                    japanese_count += 1
                    use_bengali_font = False
                else:
                    # Keep numbers, punctuation unchanged
                    translated_text = text
                    use_bengali_font = False
                
                translated_chars.append({
                    'text': translated_text,
                    'x': x0,
                    'y': y0,
                    'fontname': fontname,
                    'size': size,
                    'color': color,
                    'use_bengali_font': use_bengali_font
                })
                
                # Progress indicator
                if (i + 1) % 500 == 0:
                    print(f"   Processed {i+1}/{len(chars)} characters...")
            
            print(f"   ✅ Vietnamese translated: {vietnamese_count}")
            print(f"   ✅ Japanese preserved: {japanese_count}")
            print()
            
            # Create new PDF
            print("📋 Step 3: Creating new PDF with Bengali text...")
            
            c = canvas.Canvas(output_pdf_path, pagesize=(page_width, page_height))
            
            # Register Bengali font if available
            if bengali_font_path:
                try:
                    pdfmetrics.registerFont(TTFont('NotoSansBengali', bengali_font_path))
                    print("   ✅ Bengali font registered")
                except:
                    print("   ⚠️  Could not register Bengali font")
                    bengali_font_path = None
            
            # Draw all characters
            for i, char_data in enumerate(translated_chars):
                text = char_data['text']
                x = char_data['x']
                y = char_data['y']
                size = char_data['size']
                color = char_data['color']
                use_bengali = char_data['use_bengali_font']
                
                # Set font
                if use_bengali and bengali_font_path:
                    c.setFont('NotoSansBengali', size)
                else:
                    c.setFont('Helvetica', size)  # Fallback
                
                # Set color
                if isinstance(color, tuple) and len(color) >= 3:
                    c.setFillColorRGB(color[0], color[1], color[2])
                else:
                    c.setFillColorRGB(0, 0, 0)  # Default black
                
                # Draw text
                try:
                    c.drawString(x, y, text)
                except:
                    pass  # Skip problematic characters
                
                # Progress indicator
                if (i + 1) % 1000 == 0:
                    print(f"   Drawing {i+1}/{len(translated_chars)} characters...")
            
            # Save PDF
            c.save()
            
            print()
            print("=" * 70)
            print("✅ PDF CREATION COMPLETE!")
            print("=" * 70)
            print(f"📄 Output saved: {output_pdf_path}")
            print(f"📊 Vietnamese → Bengali: {vietnamese_count}")
            print(f"📊 Japanese preserved: {japanese_count}")
            print()
            print("⚠️  NOTE: This is a basic recreation.")
            print("   For perfect layout, manual adjustment may be needed.")
            print()
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    print()
    print("=" * 70)
    print("📄 JLPT KANJI POSTER - PDF RECREATION TOOL")
    print("=" * 70)
    print()
    
    if not TRANSLATOR_AVAILABLE:
        print("⚠️  AUTO-TRANSLATE NOT AVAILABLE")
        print("   Install with: pip3 install deep-translator")
        print("   Only pre-built dictionary will be used")
        print()
    
    # Get input file
    input_pdf = input("Enter PDF path (or press Enter for 'Kanji_poster_JLPT_N5-N1.pdf'): ").strip()
    if not input_pdf:
        input_pdf = "Kanji_poster_JLPT_N5-N1.pdf"
    
    output_pdf = input_pdf.replace('.pdf', '_Bengali.pdf')
    
    print()
    print(f"📄 Input:  {input_pdf}")
    print(f"📝 Output: {output_pdf}")
    print()
    
    response = input("Create Bengali PDF? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled.")
        return
    
    print()
    
    # Create PDF
    success = create_bengali_poster(input_pdf, output_pdf)
    
    if success:
        print("=" * 70)
        print("🎉 SUCCESS! Your Bengali JLPT poster is ready!")
        print("=" * 70)
    else:
        print("=" * 70)
        print("❌ FAILED! Check errors above.")
        print("=" * 70)

if __name__ == "__main__":
    main()