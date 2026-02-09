#!/usr/bin/env python3
"""
Responsive CSS Injector Script
This script adds responsive design CSS to an existing HTML file.

Usage:
    python add_responsive_css.py <input_html_file> <output_html_file>

Example:
    python add_responsive_css.py N5-G-Table-Complete.html N5-G-Table-Responsive.html
"""

import sys
from bs4 import BeautifulSoup


def add_navigation_buttons(soup):
    """Add floating navigation buttons (top/bottom) to the page."""
    
    nav_html = """
    <div class="nav-buttons">
        <button class="nav-btn" id="goTopBtn" onclick="scrollToTop()" title="Go to top">
            ⬆️
        </button>
        <button class="nav-btn" id="goBottomBtn" onclick="scrollToBottom()" title="Go to bottom">
            ⬇️
        </button>
    </div>
    """
    
    nav_element = BeautifulSoup(nav_html, 'html.parser')
    
    # Insert at the end of body
    body_tag = soup.find('body')
    if body_tag:
        body_tag.append(nav_element)


def add_bottom_controls(soup):
    """Add global control buttons at the bottom of the page."""
    
    # Find if control panel already exists to copy its structure
    existing_panel = soup.find('div', class_='control-panel')
    
    if existing_panel:
        bottom_html = """
        <div class="bottom-global-controls">
            <h3>🎛️ Column Controls (Bottom)</h3>
            <div style="margin-bottom: 10px;">
                <strong>Hide/Show Entire Column:</strong><br>
                <button id="col-toggle-1-bottom" class="toggle-btn" onclick="toggleColumn(1)">Hide Column: Grammar Point</button>
                <button id="col-toggle-2-bottom" class="toggle-btn" onclick="toggleColumn(2)">Hide Column: How to Use</button>
                <button id="col-toggle-3-bottom" class="toggle-btn" onclick="toggleColumn(3)">Hide Column: Examples</button>
            </div>
            <div>
                <strong>Collapse/Expand All Data (keeps toggle buttons):</strong><br>
                <button id="data-toggle-1-bottom" class="toggle-btn" onclick="toggleAllData(1)">Collapse All: Grammar Point</button>
                <button id="data-toggle-2-bottom" class="toggle-btn" onclick="toggleAllData(2)">Collapse All: How to Use</button>
                <button id="data-toggle-3-bottom" class="toggle-btn" onclick="toggleAllData(3)">Collapse All: Examples</button>
            </div>
        </div>
        """
    else:
        # Simple version if no controls exist
        bottom_html = """
        <div class="bottom-global-controls">
            <h3>📜 Navigation</h3>
            <button class="toggle-btn" onclick="scrollToTop()">⬆️ Back to Top</button>
        </div>
        """
    
    bottom_element = BeautifulSoup(bottom_html, 'html.parser')
    
    # Insert before the closing of main container or body
    main_container = soup.find('div', class_='main-container')
    if main_container:
        main_container.append(bottom_element)
    else:
        body_tag = soup.find('body')
        if body_tag:
            body_tag.append(bottom_element)


def add_navigation_script(soup):
    """Add JavaScript for smooth scrolling navigation."""
    
    script_html = """
    <script>
    // Smooth scroll to top
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
    
    // Smooth scroll to bottom
    function scrollToBottom() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    // Show/hide nav buttons based on scroll position
    window.addEventListener('scroll', function() {
        const goTopBtn = document.getElementById('goTopBtn');
        const goBottomBtn = document.getElementById('goBottomBtn');
        
        if (!goTopBtn || !goBottomBtn) return;
        
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;
        
        // Show top button after scrolling down 200px
        if (scrollTop > 200) {
            goTopBtn.classList.remove('hidden');
        } else {
            goTopBtn.classList.add('hidden');
        }
        
        // Hide bottom button when near bottom (within 100px)
        if (scrollTop + clientHeight >= scrollHeight - 100) {
            goBottomBtn.classList.add('hidden');
        } else {
            goBottomBtn.classList.remove('hidden');
        }
    });
    
    // Sync bottom control buttons with top ones (if they exist)
    window.addEventListener('DOMContentLoaded', function() {
        // Sync column toggle buttons
        for (let i = 1; i <= 3; i++) {
            const topBtn = document.getElementById('col-toggle-' + i);
            const bottomBtn = document.getElementById('col-toggle-' + i + '-bottom');
            
            if (topBtn && bottomBtn) {
                // Initialize bottom button state
                bottomBtn.classList.add('active');
            }
        }
        
        // Sync data toggle buttons
        for (let i = 1; i <= 3; i++) {
            const topBtn = document.getElementById('data-toggle-' + i);
            const bottomBtn = document.getElementById('data-toggle-' + i + '-bottom');
            
            if (topBtn && bottomBtn) {
                // Initialize bottom button state
                bottomBtn.classList.add('active');
            }
        }
    });
    
    // Override toggle functions to sync top and bottom buttons
    if (typeof toggleColumn !== 'undefined') {
        const originalToggleColumn = toggleColumn;
        toggleColumn = function(columnIndex) {
            originalToggleColumn(columnIndex);
            
            // Sync both top and bottom buttons
            const topBtn = document.getElementById('col-toggle-' + columnIndex);
            const bottomBtn = document.getElementById('col-toggle-' + columnIndex + '-bottom');
            
            if (topBtn && bottomBtn) {
                bottomBtn.className = topBtn.className;
                bottomBtn.textContent = topBtn.textContent;
            }
        };
    }
    
    if (typeof toggleAllData !== 'undefined') {
        const originalToggleAllData = toggleAllData;
        toggleAllData = function(columnIndex) {
            originalToggleAllData(columnIndex);
            
            // Sync both top and bottom buttons
            const topBtn = document.getElementById('data-toggle-' + columnIndex);
            const bottomBtn = document.getElementById('data-toggle-' + columnIndex + '-bottom');
            
            if (topBtn && bottomBtn) {
                bottomBtn.className = topBtn.className;
                bottomBtn.textContent = topBtn.textContent;
            }
        };
    }
    </script>
    """
    
    script_element = BeautifulSoup(script_html, 'html.parser')
    
    # Insert before closing body tag
    body_tag = soup.find('body')
    if body_tag:
        body_tag.append(script_element)


def add_responsive_css(input_file, output_file):
    """
    Add responsive CSS to an existing HTML file.
    
    Args:
        input_file: Path to input HTML file
        output_file: Path to output HTML file with responsive CSS
    """
    print("=" * 70)
    print("Responsive CSS Injector")
    print("=" * 70)
    print(f"\nReading file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the existing style tag
    style_tag = soup.find('style')
    
    if not style_tag:
        print("⚠️  No <style> tag found. Creating one...")
        style_tag = soup.new_tag('style')
        head_tag = soup.find('head')
        if head_tag:
            head_tag.append(style_tag)
        else:
            print("❌ ERROR: No <head> tag found in HTML")
            return False
    
    # Responsive CSS to add
    responsive_css = """
        
        /* ========================================
           FLOATING NAVIGATION BUTTONS
           ======================================== */
        
        /* Navigation button container */
        .nav-buttons {
            position: fixed;
            right: 20px;
            bottom: 20px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        /* Individual nav buttons */
        .nav-btn {
            background-color: #0d6efd;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.2rem;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .nav-btn:hover {
            background-color: #0b5ed7;
            transform: scale(1.1);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }
        
        .nav-btn:active {
            transform: scale(0.95);
        }
        
        /* Hide buttons initially, show after scrolling */
        .nav-btn.hidden {
            opacity: 0;
            pointer-events: none;
        }
        
        /* Bottom global buttons container */
        .bottom-global-controls {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #dee2e6;
        }
        
        .bottom-global-controls h3 {
            font-size: 1rem;
            margin-bottom: 10px;
            color: #495057;
        }
        
        /* ========================================
           RESPONSIVE DESIGN FOR MOBILE DEVICES
           ======================================== */
        
        /* Tablet and smaller devices (≤768px) */
        @media screen and (max-width: 768px) {
            /* Make control panel buttons stack vertically */
            .control-panel button {
                display: block;
                width: 100%;
                margin: 5px 0;
            }
            
            /* Reduce padding on mobile */
            .main-container {
                padding: 20px !important;
            }
            
            /* Smaller base font size */
            body {
                font-size: 14px;
                padding-top: 30px;
                padding-bottom: 30px;
            }
            
            /* Adjust title size */
            h1.title {
                font-size: 1.8rem;
                margin-bottom: 30px;
            }
            
            /* Adjust grammar point size */
            .grammar-pt {
                font-size: 1rem;
            }
            
            /* Adjust example text size */
            .example-jp {
                font-size: 0.95rem;
            }
            
            .example-en, .example-bn {
                font-size: 0.8rem;
            }
            
            .meaning-sub, .meaning-bn {
                font-size: 0.85rem;
            }
            
            /* Make table scrollable horizontally */
            .table-responsive {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                margin-left: -20px;
                margin-right: -20px;
                padding-left: 20px;
                padding-right: 20px;
            }
            
            /* Adjust cell padding */
            td, th {
                padding: 8px 6px !important;
            }
            
            /* Smaller toggle buttons */
            .cell-toggle-btn {
                font-size: 0.65rem;
                padding: 2px 5px;
            }
            
            .toggle-btn {
                font-size: 0.75rem;
                padding: 5px 8px;
            }
            
            /* Adjust control panel */
            .control-panel {
                padding: 12px;
                margin-left: -10px;
                margin-right: -10px;
            }
            
            .control-panel h3 {
                font-size: 0.9rem;
            }
            
            /* Make source links smaller */
            .source-link {
                font-size: 0.7rem;
            }
            
            /* Adjust nav buttons for mobile */
            .nav-buttons {
                right: 10px;
                bottom: 10px;
            }
            
            .nav-btn {
                width: 45px;
                height: 45px;
                font-size: 1rem;
            }
            
            /* Bottom controls more compact */
            .bottom-global-controls {
                padding: 15px;
                margin-top: 20px;
            }
        }
        
        /* Mobile phones (≤480px) */
        @media screen and (max-width: 480px) {
            /* Extra compact for small phones */
            .main-container {
                padding: 15px !important;
            }
            
            body {
                font-size: 13px;
                padding-top: 20px;
                padding-bottom: 20px;
            }
            
            /* Smaller title */
            h1.title {
                font-size: 1.4rem;
                margin-bottom: 20px;
                padding-bottom: 8px;
            }
            
            /* Stack control panel sections with spacing */
            .control-panel > div {
                margin-bottom: 15px;
            }
            
            .control-panel strong {
                font-size: 0.85rem;
            }
            
            /* Very compact fonts */
            .grammar-pt {
                font-size: 0.9rem;
            }
            
            .meaning-sub, .meaning-bn {
                font-size: 0.75rem;
            }
            
            .example-jp {
                font-size: 0.85rem;
            }
            
            .example-en, .example-bn {
                font-size: 0.7rem;
            }
            
            /* Extra small toggle buttons */
            .cell-toggle-btn {
                font-size: 0.6rem;
                padding: 2px 4px;
            }
            
            .toggle-btn {
                font-size: 0.7rem;
                padding: 4px 6px;
            }
            
            /* Compact table cells */
            td, th {
                padding: 6px 4px !important;
            }
            
            /* Smaller row numbers */
            td:first-child {
                font-size: 0.8rem;
            }
            
            /* Adjust usage tables inside cells */
            table.usage {
                font-size: 0.75rem;
            }
            
            table.usage td {
                padding: 4px 3px !important;
            }
            
            /* Smaller nav buttons */
            .nav-btn {
                width: 40px;
                height: 40px;
                font-size: 0.9rem;
            }
            
            .bottom-global-controls {
                padding: 12px;
            }
        }
        
        /* Extra small phones (≤360px) */
        @media screen and (max-width: 360px) {
            .main-container {
                padding: 10px !important;
            }
            
            h1.title {
                font-size: 1.2rem;
            }
            
            .grammar-pt {
                font-size: 0.85rem;
            }
            
            .control-panel {
                padding: 10px;
            }
            
            .toggle-btn {
                font-size: 0.65rem;
                padding: 3px 5px;
            }
        }
        
        /* Landscape orientation adjustments */
        @media screen and (max-height: 500px) and (orientation: landscape) {
            body {
                padding-top: 15px;
                padding-bottom: 15px;
            }
            
            .main-container {
                padding: 15px !important;
            }
            
            h1.title {
                margin-bottom: 15px;
            }
            
            .control-panel {
                padding: 10px;
                margin-bottom: 15px;
            }
        }
        
        /* Print styles */
        @media print {
            .control-panel {
                display: none;
            }
            
            .cell-toggle-btn {
                display: none;
            }
            
            .nav-buttons {
                display: none;
            }
            
            .bottom-global-controls {
                display: none;
            }
            
            .main-container {
                box-shadow: none;
            }
            
            body {
                background-color: white;
            }
        }
    """
    
    # Append responsive CSS to existing styles
    style_tag.string += responsive_css
    
    print("✅ Responsive CSS added successfully!")
    
    # Add floating navigation buttons
    print("Adding floating navigation buttons...")
    add_navigation_buttons(soup)
    
    # Add bottom global controls
    print("Adding bottom global controls...")
    add_bottom_controls(soup)
    
    # Add navigation JavaScript
    print("Adding navigation JavaScript...")
    add_navigation_script(soup)
    
    # Save the file
    print(f"\n💾 Saving file to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print("✅ File saved successfully!")
    
    print("\n" + "=" * 70)
    print("Features Added:")
    print("=" * 70)
    print("  ✅ Floating navigation buttons (top/bottom)")
    print("  ✅ Bottom control panel (mirrors top controls)")
    print("  ✅ Smooth scrolling")
    print("  ✅ Auto-hide nav buttons (smart positioning)")
    print("  ✅ Tablet optimization (≤768px)")
    print("  ✅ Mobile optimization (≤480px)")
    print("  ✅ Small phone optimization (≤360px)")
    print("  ✅ Landscape orientation support")
    print("  ✅ Print-friendly styles")
    print("  ✅ Touch-friendly scrolling")
    print("  ✅ Progressive font scaling")
    print("=" * 70)
    
    return True


def main():
    if len(sys.argv) != 3:
        print("Usage: python add_responsive_css.py <input_html_file> <output_html_file>")
        print("\nExample:")
        print("  python add_responsive_css.py N5-G-Table.html N5-G-Table-Responsive.html")
        print("\nThis script adds responsive CSS to make the table mobile-friendly.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    success = add_responsive_css(input_file, output_file)
    
    if success:
        print("\n✅ SUCCESS! Your HTML file is now responsive!")
        print(f"\nOpen '{output_file}' on different devices to test:")
        print("  📱 Mobile phones")
        print("  📱 Tablets")
        print("  💻 Desktop")
    else:
        print("\n❌ Failed to add responsive CSS")
        sys.exit(1)


if __name__ == "__main__":
    main()