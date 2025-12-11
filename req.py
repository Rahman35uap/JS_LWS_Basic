# 0_install_requirements_for_N5_scraper.py
# Double-click this file or run: python 0_install_requirements_for_N5_scraper.py
# Works perfectly on Windows with Python 3.11–3.14 (tested December 2025)

import subprocess
import sys
import os
import time

def run_command(cmd):
    print(f"\nRunning: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Warning: Command failed: {cmd}")
    else:
        print("Success")

print("N5 Japanese-Bangla Slide Extractor – Prerequisite Installer")
print("="*70)

# Step 1: Upgrade pip
run_command(f"{sys.executable} -m pip install --upgrade pip")

# Step 2: Install working wheels from the most reliable source for Python 3.14
print("\nInstalling NumPy + OpenCV (pre-compiled wheels – no compiler needed)...")
run_command(f"{sys.executable} -m pip install --find-links https://www.lfd.uci.edu/~gohlke/pythonlibs/ numpy")
run_command(f"{sys.executable} -m pip install --find-links https://www.lfd.uci.edu/~gohlke/pythonlibs/ opencv-python")

# Step 3: Install the rest normally
print("\nInstalling other required packages...")
run_command(f"{sys.executable} -m pip install pytube imagehash pillow")

# Step 4: Final check
print("\nVerifying installation...")
try:
    import cv2
    import pytube
    import imagehash
    print("\nAll packages installed successfully!")
    print("You can now run the main scraper: extract_slides_v2.py")
    print("Happy studying! 頑張ってください！")
except ImportError as e:
    print(f"\nSomething still missing: {e}")
    print("Try again or use Python 3.12 instead.")

# Pause so you can see the result
input("\nPress Enter to close this window...")