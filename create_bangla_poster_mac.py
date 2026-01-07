#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JLPT Kanji Poster - MAC VERSION WITH COMPLETE PDF RECREATION
Vietnamese → Bengali with Full Layout + Progress Tracking

THIS CREATES THE ACTUAL PDF POSTER, NOT JUST TEXT REPORT!

Mac-Optimized Features:
- Progress tracking with checkpoints
- Pause/resume capability
- macOS notifications
- Time estimation
- Error recovery

USAGE:
    python3 create_bengali_poster_mac.py

REQUIREMENTS:
    pip3 install pdfplumber reportlab pillow deep-translator
    
    Also needs: Noto Sans Bengali font
    Download: https://fonts.google.com/noto/specimen/Noto+Sans+Bengali
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime
import json

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

# Mac-specific notifications
try:
    import subprocess
    def send_mac_notification(title, message):
        """Send macOS notification."""
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(['osascript', '-e', script])
    MAC_NOTIFICATIONS = True
except:
    MAC_NOTIFICATIONS = False

# ============================================================================
# CONFIGURATION
# ============================================================================

# Translation delay
TRANSLATION_DELAY = 0.5

# Progress save frequency
SAVE_PROGRESS_EVERY = 50  # Save every 50 characters

# Progress file
PROGRESS_FILE = "pdf_creation_progress.json"

# JLPT Color Coding
JLPT_COLORS = {
    'N5': (255/255, 0/255, 0/255),      # Red
    'N4': (197/255, 192/255, 172/255),  # Beige  
    'N3': (41/255, 70/255, 112/255),    # Dark Blue
    'N2': (216/255, 107/255, 14/255),   # Orange
    'N1': (57/255, 131/255, 56/255),    # Green
}

# Pre-built translations (add more as needed)
VIETNAMESE_TO_BENGALI = {
    "Phân số, phân chia": "ভগ্নাংশ, বিভাগ",
    "To, lớn": "বড়",
    "Cái xe": "গাড়ি",
    "Bất dụng, bất tài, không có": "অকেজো, নেই",
    "Chữa bệnh, thầy thuốc": "চিকিৎসা, ডাক্তার",
    "Gấp gáp, vội vàng": "তাড়াহুড়া, জরুরি",
    "Phương hướng, 4 phương": "দিক, চার দিক",
    "Hỏi đáp, đáp án": "প্রশ্ন-উত্তর",
    "Giấy": "কাগজ",
    "Gửi đi": "পাঠানো",
    # Add more...
}

ROMANIZATION_TO_BENGALI = {
    "PHÂN": "ফুন", "ĐẠI": "দাই", "XA": "সা", "BẤT": "বত",
    "Y": "ই", "CẤP": "ক্যাপ", "PHƯƠNG": "ফুওং", "ĐÁP": "দাপ",
    # Add more...
}

# Translation cache
TRANSLATION_CACHE = {}

# ============================================================================
# PROGRESS MANAGEMENT
# ============================================================================

def save_progress(translated_chars, current_index, total):
    """Save PDF creation progress."""
    progress_data = {
        'timestamp': datetime.now().isoformat(),
        'current_index': current_index,
        'total': total,
        'translated_chars': translated_chars,
        'percentage': (current_index / total * 100) if total > 0 else 0
    }
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress():
    """Load previous progress."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

# ============================================================================
# TRANSLATION FUNCTIONS
# ============================================================================

def is_vietnamese(text):
    """Check if text is Vietnamese."""
    vietnamese_chars = 'ăâêôơưđáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'
    vietnamese_chars += vietnamese_chars.upper()
    return any(char in vietnamese_chars for char in text)

def is_japanese(text):
    """Check if text is Japanese."""
    for char in text:
        code = ord(char)
        if (0x3040 <= code <= 0x309F or 
            0x30A0 <= code <= 0x30FF or 
            0x4E00 <= code <= 0x9FFF):
            return True
    return False

def auto_translate(text, retry_count=3):
    """Auto-translate with retry logic."""
    if not TRANSLATOR_AVAILABLE:
        return text
    
    # Check cache first
    if text in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[text]
    
    for attempt in range(retry_count):
        try:
            translator = GoogleTranslator(source='vi', target='bn')
            result = translator.translate(text)
            TRANSLATION_CACHE[text] = result
            time.sleep(TRANSLATION_DELAY)
            return result
        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep(2)
            else:
                return text
    
    return text

def translate_text(text, is_label=False):
    """Main translation function."""
    # Check pre-built dictionaries
    if is_label and text in ROMANIZATION_TO_BENGALI:
        return ROMANIZATION_TO_BENGALI[text]
    elif not is_label and text in VIETNAMESE_TO_BENGALI:
        return VIETNAMESE_TO_BENGALI[text]
    
    # Auto-translate
    if TRANSLATOR_AVAILABLE:
        return auto_translate(text)
    
    return text

# ============================================================================
# MAIN PDF RECREATION WITH PROGRESS TRACKING
# ============================================================================

def create_bengali_poster_mac(input_pdf_path, output_pdf_path):
    """
    Mac-optimized PDF recreation with progress tracking.
    CREATES ACTUAL PDF POSTER!
    """
    print("=" * 70)
    print("🍎 JLPT KANJI POSTER - MAC PDF RECREATION")
    print("Vietnamese → Bengali with Full Layout + Progress Tracking")
    print("=" * 70)
    print()
    
    if not os.path.exists(input_pdf_path):
        print(f"❌ ERROR: Input PDF not found: {input_pdf_path}")
        return False
    
    start_time = time.time()
    
    print(f"📄 Input:  {input_pdf_path}")
    print(f"📝 Output: {output_pdf_path}")
    print(f"🤖 Auto-translate: {'ENABLED ✅' if TRANSLATOR_AVAILABLE else 'DISABLED ❌'}")
    print(f"💾 Progress tracking: ENABLED ✅")
    print()
    
    # Check for Bengali font
    bengali_font_path = None
    possible_paths = [
        "NotoSansBengali-Regular.ttf",
        "/System/Library/Fonts/Supplemental/NotoSansBengali-Regular.ttf",
        "/Library/Fonts/NotoSansBengali-Regular.ttf",
        os.path.expanduser("~/Library/Fonts/NotoSansBengali-Regular.ttf"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            bengali_font_path = path
            break
    
    if not bengali_font_path:
        print("⚠️  WARNING: Noto Sans Bengali font not found!")
        print("   Download: https://fonts.google.com/noto/specimen/Noto+Sans+Bengali")
        print("   Place in: ~/Library/Fonts/")
        print()
        print("   Continuing with fallback font (may not render correctly)...")
        print()
    else:
        print(f"✅ Bengali font found: {bengali_font_path}")
        print()
    
    # Check for existing progress
    previous_progress = load_progress()
    if previous_progress:
        print("🔄 FOUND PREVIOUS PROGRESS!")
        print(f"   Completed: {previous_progress['percentage']:.1f}%")
        print(f"   Last run: {previous_progress['timestamp']}")
        resume = input("\nResume from previous progress? (y/n): ").strip().lower()
        if resume != 'y':
            previous_progress = None
            print("   Starting fresh...")
        else:
            print("   Resuming from checkpoint...")
        print()
    
    try:
        print("🔍 STEP 1: Analyzing original PDF structure...")
        with pdfplumber.open(input_pdf_path) as pdf:
            page = pdf.pages[0]
            page_width = page.width
            page_height = page.height
            
            print(f"   Page size: {page_width} x {page_height} pts")
            
            # Extract all characters with positions
            chars = page.chars
            total_chars = len(chars)
            print(f"   Total characters: {total_chars}")
            print()
            
            # Process characters
            print("🔄 STEP 2: Translating and processing characters...")
            print("=" * 70)
            print()
            
            if previous_progress:
                translated_chars = previous_progress['translated_chars']
                start_index = previous_progress['current_index']
            else:
                translated_chars = []
                start_index = 0
            
            vietnamese_count = 0
            japanese_count = 0
            
            for i in range(start_index, total_chars):
                char = chars[i]
                text = char.get('text', '')
                x0 = char.get('x0', 0)
                y0 = char.get('y0', 0)
                fontname = char.get('fontname', '')
                size = char.get('size', 12)
                color = char.get('non_stroking_color', (0, 0, 0))
                
                # Progress indicator
                percentage = (i + 1) / total_chars * 100
                elapsed = time.time() - start_time
                if i > start_index:
                    estimated_total = (elapsed / (i - start_index)) * total_chars
                    remaining = estimated_total - elapsed
                else:
                    remaining = 0
                
                if i % 100 == 0:  # Update every 100 chars
                    print(f"[{i+1}/{total_chars}] ({percentage:.1f}%) | ⏱️  {int(remaining/60)}min remaining")
                
                # Determine text type and translate
                use_bengali_font = False
                
                if is_vietnamese(text):
                    # Translate Vietnamese
                    is_label = text.isupper() and len(text) <= 10
                    translated_text = translate_text(text, is_label)
                    vietnamese_count += 1
                    use_bengali_font = True
                    
                    if i % 100 == 0:
                        print(f"   VN→BN: {text[:30]} → {translated_text[:30]}")
                    
                elif is_japanese(text):
                    # Keep Japanese unchanged
                    translated_text = text
                    japanese_count += 1
                    use_bengali_font = False
                else:
                    # Numbers, punctuation
                    translated_text = text
                    use_bengali_font = False
                
                # Store translated character data
                char_data = {
                    'text': translated_text,
                    'x': x0,
                    'y': y0,
                    'fontname': fontname,
                    'size': size,
                    'color': color,
                    'use_bengali_font': use_bengali_font
                }
                
                if i >= len(translated_chars):
                    translated_chars.append(char_data)
                else:
                    translated_chars[i] = char_data
                
                # Save progress periodically
                if (i + 1) % SAVE_PROGRESS_EVERY == 0:
                    save_progress(translated_chars, i + 1, total_chars)
                    print(f"   💾 Progress saved (checkpoint at {percentage:.1f}%)")
                    print()
            
            print()
            print("=" * 70)
            print("📊 TRANSLATION SUMMARY")
            print("=" * 70)
            print(f"✅ Vietnamese → Bengali: {vietnamese_count}")
            print(f"✅ Japanese preserved: {japanese_count}")
            print(f"📝 Total characters: {total_chars}")
            print()
            
            # Create PDF
            print("📋 STEP 3: Creating new PDF with Bengali text...")
            print("=" * 70)
            print()
            
            c = canvas.Canvas(output_pdf_path, pagesize=(page_width, page_height))
            
            # Register Bengali font
            if bengali_font_path:
                try:
                    pdfmetrics.registerFont(TTFont('NotoSansBengali', bengali_font_path))
                    print("   ✅ Bengali font registered: NotoSansBengali")
                except Exception as e:
                    print(f"   ⚠️  Could not register Bengali font: {e}")
                    bengali_font_path = None
            
            # Draw all characters
            print("   Drawing characters with exact positioning...")
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
                    c.setFont('Helvetica', size)
                
                # Set color
                if isinstance(color, tuple) and len(color) >= 3:
                    c.setFillColorRGB(color[0], color[1], color[2])
                else:
                    c.setFillColorRGB(0, 0, 0)
                
                # Draw text at exact position
                try:
                    c.drawString(x, y, text)
                except:
                    pass  # Skip problematic characters
                
                # Progress
                if (i + 1) % 1000 == 0:
                    percentage = (i + 1) / len(translated_chars) * 100
                    print(f"   [{i+1}/{len(translated_chars)}] ({percentage:.1f}%) drawn")
            
            # Save PDF
            c.save()
            
            total_time = time.time() - start_time
            
            print()
            print("=" * 70)
            print("✅ PDF CREATION COMPLETE!")
            print("=" * 70)
            print(f"📄 Output saved: {output_pdf_path}")
            print(f"📊 Vietnamese → Bengali: {vietnamese_count}")
            print(f"📊 Japanese preserved: {japanese_count}")
            print(f"⏱️  Total time: {int(total_time/60)}m {int(total_time%60)}s")
            print()
            print("🎉 Your Bengali JLPT poster PDF is ready!")
            print()
            
            # Send Mac notification
            if MAC_NOTIFICATIONS:
                send_mac_notification(
                    "PDF Creation Complete! 🎉",
                    f"Bengali JLPT poster created successfully!"
                )
            
            # Clean up progress file
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
            
            return True
            
    except KeyboardInterrupt:
        print("\n\n⚠️  PDF creation interrupted!")
        print("   Progress has been saved. Run again to resume.")
        return False
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
    print("🍎 JLPT KANJI POSTER - MAC PDF CREATOR")
    print("=" * 70)
    print()
    print("This script CREATES THE ACTUAL PDF POSTER!")
    print("Not just a text report - full layout with Bengali text.")
    print()
    
    if not TRANSLATOR_AVAILABLE:
        print("⚠️  AUTO-TRANSLATE NOT AVAILABLE")
        print("   Install: pip3 install deep-translator")
        print()
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return
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
    print("💡 NOTE: This will take 15-30 minutes depending on:")
    print("   - Translation (if using auto-translate)")
    print("   - PDF complexity")
    print("   - Your Mac's speed")
    print()
    print("   You can pause anytime (Ctrl+C) and resume later!")
    print()
    
    response = input("Create Bengali PDF poster? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled.")
        return
    
    print()
    
    # Create PDF
    success = create_bengali_poster_mac(input_pdf, output_pdf)
    
    if success:
        print("=" * 70)
        print("🎉 SUCCESS! Your Bengali JLPT poster PDF is ready!")
        print("=" * 70)
        print()
        print(f"📁 Output file: {output_pdf}")
        print()
        print("✅ Open it with Preview or any PDF viewer!")
        print("✅ Print it as a poster!")
        print("✅ Share it with students!")
        print()
    else:
        print("=" * 70)
        print("⚠️  PDF CREATION INCOMPLETE")
        print("=" * 70)
        print()
        print("Run the script again to resume from last checkpoint.")
        print()

if __name__ == "__main__":
    main()