
## 📁 **5. SETUP SCRIPT**

### **File 11: `run_project.py`** (One-click Setup)
#!/usr/bin/env python3
"""
JLPT N5 Kanji Master - One-Click Setup Script
Automatically sets up the complete project
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def run_command(command, description):
    print(f"\n🔧 {description}...")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"   ✅ Success")
        if result.stdout:
            print(f"   Output: {result.stdout[:200]}...")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr[:200]}")
        return False

def create_directory_structure():
    """Create the complete project directory structure"""
    print_header("CREATING PROJECT STRUCTURE")
    
    directories = [
        'data',
        'scrapers',
        'web_app',
        'docs',
        'backups'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created: {directory}/")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_header("INSTALLING DEPENDENCIES")
    
    requirements = [
        'beautifulsoup4==4.12.2',
        'requests==2.31.0',
        'lxml==4.9.3',
        'Pillow==10.1.0',
        'tqdm==4.66.1'
    ]
    
    # Create requirements file
    with open('scrapers/requirements.txt', 'w') as f:
        for req in requirements:
            f.write(req + '\n')
    
    print("📝 Created requirements.txt")
    
    # Install packages
    for req in requirements:
        package = req.split('==')[0]
        command = f"{sys.executable} -m pip install {package}"
        if not run_command(command, f"Installing {package}"):
            print(f"⚠️  Could not install {package}, continuing...")
    
    return True

def setup_scrapers():
    """Set up the scraper scripts"""
    print_header("SETTING UP SCRAPERS")
    
    # The scraper code is already provided in the main script
    print("✅ Scrapers ready in scrapers/ directory")
    print("   Run: python scrapers/scrape_jlpt_n5.py")
    
    return True

def setup_web_app():
    """Set up the web application"""
    print_header("SETTING UP WEB APPLICATION")
    
    # Check if web files exist
    web_files = ['index.html', 'study_deeply_modal.html', 'complete_quiz_system.html']
    
    for file in web_files:
        if not os.path.exists(f'web_app/{file}'):
            print(f"⚠️  Missing: web_app/{file}")
            print("   Please copy the HTML files to web_app/ directory")
            return False
    
    print("✅ Web application files ready")
    print("   Open: web_app/index.html in your browser")
    
    return True

def create_readme():
    """Create comprehensive README file"""
    print_header("CREATING DOCUMENTATION")
    
    readme_content = """
    # 🎌 JLPT N5 Kanji Master - Complete Learning Tool

    ## 📋 Overview
    Complete application for learning all 80 JLPT N5 kanji with:
    - Stroke order diagrams
    - Readings and examples
    - Interactive quizzes
    - Progress tracking
    - PWA (Progressive Web App)

    ## 🚀 Quick Start

    ### Option 1: Web App Only
    1. Open `web_app/index.html` in your browser
    2. Start learning immediately (uses sample data)

    ### Option 2: Full Setup with Data
    1. Install Python dependencies:
    ```bash
    cd scrapers
    pip install -r requirements.txt
    """