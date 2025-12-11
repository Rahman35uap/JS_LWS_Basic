#!/bin/bash

# --- macOS Setup and Dependency Installation Script ---

echo "Starting macOS dependency setup using Homebrew..."

# 1. Check if Homebrew is installed
if ! command -v brew &> /dev/null
then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for non-shell environment (standard for M1/M2/M3 Macs)
    if [ -d "/opt/homebrew" ]; then
        echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
        source ~/.zshrc
    fi
fi

# 2. Install FFmpeg and yt-dlp via Homebrew
echo "Installing/Updating ffmpeg and yt-dlp..."
brew install ffmpeg yt-dlp

# 3. Install Python dependencies
echo "Installing Python dependencies (yt-dlp)..."
pip3 install yt-dlp

echo "Setup complete. You can now run the Python script."
echo "Use: python3 voice_shifter_mac.py"