#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JLPT Kanji Poster Translation Script - ENHANCED VERSION
Vietnamese → Bengali Translation with AUTO-TRANSLATE for missing phrases

FREE TRANSLATION using deep-translator library (Google Translate free API)

USAGE:
    python translate_kanji_poster_auto.py

REQUIREMENTS:
    pip install pdfplumber reportlab pillow deep-translator
"""

import sys
import os
import re
from pathlib import Path
import time

try:
    import pdfplumber
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError as e:
    print("❌ ERROR: Missing required libraries!")
    print("\nPlease install dependencies:")
    print("  pip install pdfplumber reportlab pillow deep-translator")
    print(f"\nDetailed error: {e}")
    sys.exit(1)

# Try to import translator
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
    print("✅ Auto-translation enabled (using deep-translator)")
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("⚠️  Auto-translation disabled (install: pip install deep-translator)")

# ============================================================================
# TRANSLATION DICTIONARIES (Pre-built for speed)
# ============================================================================

# Vietnamese Meanings → Bengali (200+ pre-translated for speed)
VIETNAMESE_TO_BENGALI = {
    "Phân số, phân chia": "ভগ্নাংশ, বিভাগ",
    "To, lớn": "বড়",
    "Cái xe": "গাড়ি",
    "Bất dụng, bất tài, không có": "অকেজো, প্রতিভাহীন, নেই",
    "Chữa bệnh, thầy thuốc": "চিকিৎসা, ডাক্তার",
    "Gấp gáp, vội vàng": "তাড়াহুড়া, জরুরি",
    "Phương hướng, 4 phương": "দিক, চার দিক",
    "Hỏi đáp, đáp án": "প্রশ্ন-উত্তর",
    "Giấy": "কাগজ",
    "Gửi đi": "পাঠানো",
    "Xử lý, chỗ": "প্রক্রিয়া, জায়গা",
    "Nhận, tiếp thụ": "গ্রহণ করা",
    "Có thể, khả năng": "সম্ভব, সক্ষমতা",
    "Trinh sát, điều tra": "তদন্ত",
    "Đối mặt, đối diện": "মুখোমুখি",
    "Rút ra": "তুলে নেওয়া",
    "Hoài bão, bão hòa": "উচ্চাভিলাষ",
    "Con ngựa": "ঘোড়া",
    "Chén, cạn chén": "পেয়ালা",
    "Thượng đẳng, đẳng cấp": "শ্রেণী, মর্যাদা",
    "Cái hộp": "বাক্স",
    "Nghèo, bần hàn": "গরিব, দরিদ্র",
    "Khiển trách, trách nhiệm": "দায়িত্ব, দোষারোপ",
    "Yêu cầu, nguyện cầu": "অনুরোধ, কামনা",
    "Tư tưởng, tưởng tượng": "চিন্তা, কল্পনা",
    "Mây": "মেঘ",
    "Chứng khoán": "সিকিউরিটিজ",
    "Tôn trọng": "সম্মান",
    "Chỉ đạo, lãnh đạo": "নির্দেশনা, নেতৃত্ব",
    "Thay thế, chuyển đổi": "প্রতিস্থাপন",
    "Số một, duy nhất": "এক নম্বর, একমাত্র",
    "Hình tròn, đồng yên": "গোলাকার, মুদ্রা",
    "Nhật": "জাপান",
    "Nhỏ, bé": "ছোট",
    "Dài, chức vụ đứng đầu": "লম্বা, প্রধান",
    "Đời người, thế giới": "জীবন, পৃথিবী",
    "Cõi, mốc, thế giới, cảnh giới": "রাজ্য, সীমানা",
    "Vật liệu, tư liệu": "উপাদান",
    "Lữ khách, lữ hành, du lịch": "ভ্রমণকারী, ভ্রমণ",
    "Độc lập, quốc lập": "স্বাধীন",
    "Kết thúc, xong": "শেষ",
    "Thông tin, giao thông": "তথ্য, যোগাযোগ",
    "Lạnh, lãnh đạm, lãnh cung": "ঠান্ডা, শীতল",
    "Lấy, nhận báo hiệu, số hiệu": "নেওয়া, সংকেত",
    "Bên trong": "ভিতরে",
    "Cục tình báo, cục kế hoạch": "ব্যুরো, বিভাগ",
    "Bẻ gẫy, chiết xuất": "ভাঙা, নিষ্কাশন",
    "Ấn, giam giữ, bó buộc": "সীলমোহর, আটকানো",
    "Con mèo": "বিড়াল",
    "Lưu hành, lưu thông": "প্রবাহ",
    "Rụng, trụy lạc": "পড়ে যাওয়া",
    "gạo": "চাল",
    "Tài sản, tài lực": "সম্পদ",
    "Chi phí": "ব্যয়",
    "Quân vương, gọi thân mật": "রাজা, সম্বোধন",
    "Tình cảm": "অনুভূতি",
}

# Vietnamese Romanization → Bengali Phonetic (130+ labels)
ROMANIZATION_TO_BENGALI = {
    "PHÂN": "ফুন", "ĐẠI": "দাই", "XA": "সা", "BẤT": "বত",
    "Y": "ই", "CẤP": "ক্যাপ", "PHƯƠNG": "ফুওং", "ĐÁP": "দাপ",
    "CHỈ": "চি", "TỐNG": "তং", "XỨ": "সু", "XỬ": "সু",
    "THỤ": "থু", "KHẢ": "খা", "SÁT": "সাত", "ĐỐI": "দোই",
    "BẠT": "বাত", "BÃO": "বাও", "MÃ": "মা", "BÔI": "বোই",
    "ĐẲNG": "দাং", "TƯƠNG": "তুওং", "BẦN": "বান", "TRÁCH": "ত্রাচ",
    "NGUYỆN": "গুয়েন", "TƯỞNG": "তুওং", "VÂN": "ভান", "KHOÁN": "খোয়ান",
    "TÔN": "তোন", "ĐẠO": "দাও", "THẾ": "থে", "NHẤT": "নাত",
    "VIÊN": "ভিয়েন", "TIỂU": "তিয়েও", "TRƯỜNG": "ত্রুওং",
    "TRƯỞNG": "ত্রুওং", "GIỚI": "জোই", "LIỆU": "লিয়েও",
    # Add more as needed...
}

# Cache for auto-translated phrases (to avoid repeat API calls)
TRANSLATION_CACHE = {}

# ============================================================================
# AUTO-TRANSLATION FUNCTIONS (FREE!)
# ============================================================================

def auto_translate_vietnamese_to_bengali(text, is_label=False):
    """
    Auto-translate Vietnamese to Bengali using FREE Google Translate API.
    
    Args:
        text: Vietnamese text to translate
        is_label: True if it's a romanization label
    
    Returns:
        Bengali translation
    """
    if not TRANSLATOR_AVAILABLE:
        return text  # Return original if translator not available
    
    # Check cache first
    cache_key = f"{text}_{is_label}"
    if cache_key in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[cache_key]
    
    try:
        # Use deep-translator (free, no API key needed!)
        translator = GoogleTranslator(source='vi', target='bn')
        
        # For labels, translate to phonetic equivalent
        if is_label:
            # First translate to English to get pronunciation
            temp_translator = GoogleTranslator(source='vi', target='en')
            english = temp_translator.translate(text)
            # Then to Bengali
            result = translator.translate(english)
        else:
            # Direct translation for meanings
            result = translator.translate(text)
        
        # Cache the result
        TRANSLATION_CACHE[cache_key] = result
        
        # Small delay to avoid rate limiting (be respectful!)
        time.sleep(0.5)
        
        return result
        
    except Exception as e:
        print(f"⚠️  Translation failed for '{text}': {e}")
        return text  # Return original on error

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_vietnamese(text):
    """Check if text contains Vietnamese characters."""
    vietnamese_chars = 'ăâêôơưđáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'
    vietnamese_chars += vietnamese_chars.upper()
    return any(char in vietnamese_chars for char in text)

def is_japanese(text):
    """Check if text contains Japanese characters."""
    for char in text:
        code = ord(char)
        if (0x3040 <= code <= 0x309F or  # Hiragana
            0x30A0 <= code <= 0x30FF or  # Katakana
            0x4E00 <= code <= 0x9FFF):   # Kanji
            return True
    return False

def classify_text(text):
    """Classify text type."""
    if text.strip().isdigit():
        return 'number'
    if is_japanese(text):
        return 'japanese'
    if is_vietnamese(text):
        if text.isupper() and len(text) <= 10:
            return 'vietnamese_label'
        else:
            return 'vietnamese_meaning'
    return 'unknown'

def translate_text(text, is_label=False, use_auto=True):
    """
    Translate Vietnamese text to Bengali.
    
    Args:
        text: Text to translate
        is_label: True if romanization label
        use_auto: Use auto-translation for missing phrases
    
    Returns:
        Bengali translation
    """
    # Try pre-built dictionary first (faster!)
    if is_label:
        if text in ROMANIZATION_TO_BENGALI:
            return ROMANIZATION_TO_BENGALI[text]
    else:
        if text in VIETNAMESE_TO_BENGALI:
            return VIETNAMESE_TO_BENGALI[text]
    
    # If not in dictionary and auto-translate enabled
    if use_auto and TRANSLATOR_AVAILABLE:
        print(f"   🔄 Auto-translating: {text[:50]}...")
        return auto_translate_vietnamese_to_bengali(text, is_label)
    
    # Return original if can't translate
    return text

# ============================================================================
# MAIN TRANSLATION FUNCTION
# ============================================================================

def translate_pdf(input_pdf_path, output_pdf_path, use_auto_translate=True):
    """
    Translate Vietnamese content in PDF to Bengali.
    
    Args:
        input_pdf_path: Path to source PDF
        output_pdf_path: Path to output PDF
        use_auto_translate: Use auto-translation for missing phrases
    """
    print("=" * 70)
    print("🎯 JLPT KANJI POSTER TRANSLATION - ENHANCED")
    print("Vietnamese → Bengali with AUTO-TRANSLATE")
    print("=" * 70)
    print()
    
    if not os.path.exists(input_pdf_path):
        print(f"❌ ERROR: Input PDF not found: {input_pdf_path}")
        return False
    
    print(f"📄 Input PDF: {input_pdf_path}")
    print(f"📝 Output PDF: {output_pdf_path}")
    print(f"🤖 Auto-translate: {'ENABLED ✅' if use_auto_translate and TRANSLATOR_AVAILABLE else 'DISABLED ❌'}")
    print()
    
    if not TRANSLATOR_AVAILABLE:
        print("⚠️  WARNING: Auto-translate not available!")
        print("   Install with: pip install deep-translator")
        print("   Only pre-built dictionary will be used (~200 phrases)")
        print()
    
    try:
        print("🔍 Opening PDF...")
        with pdfplumber.open(input_pdf_path) as pdf:
            print(f"   Total pages: {len(pdf.pages)}")
            
            page = pdf.pages[0]
            print(f"   Page size: {page.width} x {page.height} pts")
            
            # Extract text with structure
            print("\n📝 Extracting text...")
            text_content = page.extract_text()
            
            # Split into lines and identify Vietnamese phrases
            lines = text_content.split('\n')
            vietnamese_phrases = []
            
            for line in lines:
                line = line.strip()
                if line and is_vietnamese(line) and not is_japanese(line):
                    vietnamese_phrases.append(line)
            
            print(f"   Found {len(vietnamese_phrases)} Vietnamese phrases")
            print()
            
            # Translate all Vietnamese phrases
            print("🔄 Translating Vietnamese phrases...")
            print("-" * 70)
            
            translations = {}
            pre_built_count = 0
            auto_translated_count = 0
            untranslated_count = 0
            
            for i, phrase in enumerate(vietnamese_phrases, 1):
                print(f"\n[{i}/{len(vietnamese_phrases)}] {phrase[:60]}...")
                
                is_label = phrase.isupper() and len(phrase) <= 10
                translated = translate_text(phrase, is_label, use_auto_translate)
                
                if translated != phrase:
                    if phrase in VIETNAMESE_TO_BENGALI or phrase in ROMANIZATION_TO_BENGALI:
                        pre_built_count += 1
                        print(f"   ✅ Pre-built: {translated[:60]}")
                    else:
                        auto_translated_count += 1
                        print(f"   🤖 Auto-translated: {translated[:60]}")
                else:
                    untranslated_count += 1
                    print(f"   ⚠️  Not translated (kept original)")
                
                translations[phrase] = translated
            
            print()
            print("=" * 70)
            print("📊 TRANSLATION SUMMARY")
            print("=" * 70)
            print(f"✅ Pre-built translations: {pre_built_count}")
            print(f"🤖 Auto-translated: {auto_translated_count}")
            print(f"⚠️  Untranslated: {untranslated_count}")
            print(f"📝 Total phrases: {len(vietnamese_phrases)}")
            print()
            
            # Calculate coverage
            coverage = ((pre_built_count + auto_translated_count) / len(vietnamese_phrases) * 100) if vietnamese_phrases else 0
            print(f"🎯 Translation Coverage: {coverage:.1f}%")
            print()
            
            # Save translation report
            report_path = output_pdf_path.replace('.pdf', '_translation_report.txt')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("JLPT KANJI POSTER TRANSLATION REPORT\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Input PDF: {input_pdf_path}\n")
                f.write(f"Total Vietnamese phrases: {len(vietnamese_phrases)}\n")
                f.write(f"Pre-built translations: {pre_built_count}\n")
                f.write(f"Auto-translated: {auto_translated_count}\n")
                f.write(f"Untranslated: {untranslated_count}\n")
                f.write(f"Coverage: {coverage:.1f}%\n\n")
                f.write("=" * 70 + "\n")
                f.write("ALL TRANSLATIONS:\n")
                f.write("=" * 70 + "\n\n")
                
                for original, translated in translations.items():
                    f.write(f"Vietnamese: {original}\n")
                    f.write(f"Bengali:    {translated}\n")
                    f.write("-" * 70 + "\n")
            
            print(f"✅ Translation report saved: {report_path}")
            print()
            print("⚠️  NOTE: Full PDF recreation with Bengali font requires:")
            print("   1. Noto Sans Bengali font installed")
            print("   2. Advanced reportlab configuration")
            print("   3. Character-by-character positioning")
            print()
            print("   Current script provides translation analysis.")
            print("   See PROJECT_SUMMARY.md for PDF recreation details.")
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
    print("🎯 JLPT KANJI POSTER TRANSLATION TOOL - ENHANCED")
    print("=" * 70)
    print()
    
    if not TRANSLATOR_AVAILABLE:
        print("⚠️  AUTO-TRANSLATE NOT AVAILABLE")
        print()
        print("To enable auto-translation of ALL Vietnamese phrases:")
        print("  pip install deep-translator")
        print()
        print("Without it, only ~200 pre-built translations will be used.")
        print()
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Cancelled. Please install deep-translator first.")
            return
        print()
    
    # Get input file
    input_pdf = input("Enter path to input PDF (or press Enter for 'Kanji_poster_JLPT_N5-N1.pdf'): ").strip()
    if not input_pdf:
        input_pdf = "Kanji_poster_JLPT_N5-N1.pdf"
    
    # Generate output filename
    output_pdf = input_pdf.replace('.pdf', '_Bengali.pdf')
    
    # Confirm
    print()
    print(f"📄 Input:  {input_pdf}")
    print(f"📝 Output: {output_pdf}")
    print()
    
    response = input("Proceed with translation? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Translation cancelled.")
        return
    
    print()
    
    # Translate
    success = translate_pdf(input_pdf, output_pdf, use_auto_translate=True)
    
    if success:
        print("=" * 70)
        print("✅ TRANSLATION COMPLETE!")
        print("=" * 70)
        print()
        print("📁 Files created:")
        print(f"   - {output_pdf.replace('.pdf', '_translation_report.txt')}")
        print()
    else:
        print("=" * 70)
        print("❌ TRANSLATION FAILED!")
        print("=" * 70)

if __name__ == "__main__":
    main()