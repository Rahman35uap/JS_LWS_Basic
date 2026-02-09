#!/usr/bin/env python3
"""
JLPT N5 Kanji Master - Build Script
Combines HTML, CSS, JS, and data into single file
"""

import json
import base64
import os
import sys

def build_app():
    print("=" * 60)
    print("🏗️  JLPT N5 Kanji Master - Build Script")
    print("=" * 60)
    print()
    
    # Check if all required files exist
    required_files = {
        'template.html': 'HTML template',
        'styles.css': 'CSS stylesheet',
        'app.js': 'JavaScript application',
        '../data/kanji_data_enhanced.min.json': 'Kanji data'
    }
    
    missing_files = []
    for filepath, description in required_files.items():
        if not os.path.exists(filepath):
            missing_files.append(f"  ❌ {filepath} ({description})")
    
    if missing_files:
        print("⚠️  Missing required files:")
        print("\n".join(missing_files))
        print()
        print("Please ensure all files are in the correct locations.")
        print("See COMPLETE_INSTRUCTIONS.md for details.")
        sys.exit(1)
    
    print("✅ All required files found")
    print()
    
    try:
        # Load template
        print("📄 Loading template.html...")
        with open('template.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Load CSS
        print("🎨 Loading styles.css...")
        with open('styles.css', 'r', encoding='utf-8') as f:
            css = f.read()
        
        # Load JavaScript
        print("⚙️  Loading app.js...")
        with open('app.js', 'r', encoding='utf-8') as f:
            js = f.read()
        
        # Load kanji data
        print("📊 Loading kanji data...")
        with open('../data/kanji_data_enhanced.min.json', 'r', encoding='utf-8') as f:
            kanji_data = f.read()
        
        # Validate JSON
        try:
            json.loads(kanji_data)
            print("✅ Kanji data is valid JSON")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in kanji data: {e}")
            sys.exit(1)
        
        # Create PWA manifest
        print("📱 Creating PWA manifest...")
        manifest = {
            "name": "JLPT N5 Kanji Master",
            "short_name": "Kanji N5",
            "description": "Learn all 80 JLPT N5 Kanji with SRS, quizzes, and stroke practice",
            "start_url": "./",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#3498db",
            "orientation": "portrait",
            "icons": [{
                "src": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48dGV4dCB5PSI3NSIgZm9udC1zaXplPSI4MCIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiPuaXpTwvdGV4dD48L3N2Zz4=",
                "sizes": "192x192",
                "type": "image/svg+xml"
            }]
        }
        
        manifest_b64 = base64.b64encode(json.dumps(manifest).encode()).decode()
        
        # Replace placeholders
        print("🔧 Injecting code into template...")
        html = html.replace('MANIFEST_BASE64_PLACEHOLDER', manifest_b64)
        html = html.replace('/* CSS_PLACEHOLDER */', css)
        html = html.replace('// KANJI_DATA_PLACEHOLDER', f'const KANJI_DATA = {kanji_data};')
        html = html.replace('// APP_SCRIPT_PLACEHOLDER', js)
        
        # Create output directory if it doesn't exist
        os.makedirs('../output', exist_ok=True)
        
        # Write output
        output_path = '../output/jlpt_n5_kanji_master.html'
        print(f"💾 Writing to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Calculate sizes
        size_bytes = os.path.getsize(output_path)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        print()
        print("=" * 60)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"📄 Output file: {output_path}")
        print(f"💾 Size: {size_mb:.2f} MB ({size_kb:.0f} KB)")
        print()
        print("📊 Statistics:")
        print(f"  • HTML lines: {len(html.splitlines()):,}")
        print(f"  • CSS lines: {len(css.splitlines()):,}")
        print(f"  • JS lines: {len(js.splitlines()):,}")
        print()
        print("🎉 Ready to use!")
        print("   Open the file in any modern browser (Chrome, Firefox, Safari, Edge)")
        print()
        print("💡 Tips:")
        print("   • Works 100% offline")
        print("   • Install as PWA for app-like experience")
        print("   • All progress saved to localStorage")
        print()
        print("頑張って！Good luck with your studies! 🎌")
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    build_app()