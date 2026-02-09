# 🎌 JLPT N5 Kanji Master

A comprehensive Progressive Web App (PWA) for learning all 80 JLPT N5 kanji with Spaced Repetition System (SRS), interactive quizzes, stroke practice, and detailed analytics.

## ✨ Features

### Core Features
- **📚 Complete N5 Kanji Set**: All 80 kanji with comprehensive data
- **🎮 Interactive Quiz Mode**: Multiple question types (reading, meaning, context)
- **📖 Study Mode**: Detailed kanji information with examples
- **🔥 Streak System**: Track your learning streak and best performance
- **📊 Progress Tracking**: Visual progress bar and statistics

### Enhanced Features
- **🧠 Spaced Repetition System (SRS)**: SM-2 algorithm for optimal review scheduling
- **🔍 Search & Filter**: Find kanji by character, reading, or meaning
- **⭐ Bookmarking**: Mark favorite kanji for quick access
- **📝 Personal Notes**: Add your own notes to each kanji
- **🎨 Multiple Themes**: Ocean, Sakura, Forest, Midnight, High Contrast
- **📱 Progressive Web App**: Works offline, installable on mobile devices
- **💾 Export/Import**: Backup and restore your progress
- **📈 Analytics Dashboard**: Detailed performance metrics

### Advanced Features
- **✍️ Stroke Practice**: Interactive canvas for writing practice (coming soon)
- **🔊 Audio Pronunciation**: Text-to-speech for readings (coming soon)
- **🏆 Achievements**: Unlock badges for milestones
- **⏱️ Session Timer**: Track study time
- **🌙 Dark Mode**: Eye-friendly dark theme

## 🚀 Getting Started

### Prerequisites
- Python 3.7+ (for scraping)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Scrape kanji data** (optional - sample data included):
   ```bash
   python scrape_enhanced.py
   ```
   This will create `kanji_data_enhanced.json` with all 80 N5 kanji.

4. **Open the application**:
   - Simply open `jlpt_n5_kanji_master.html` in your web browser
   - Or serve it with a local web server:
     ```bash
     # Python 3
     python -m http.server 8000
     
     # Node.js
     npx http-server
     ```
   - Then visit `http://localhost:8000/jlpt_n5_kanji_master.html`

## 📖 Usage

### Study Mode
1. Navigate through kanji using arrow buttons or keyboard arrows (← →)
2. Click **"📖 Study Deeply"** to open detailed information
3. View readings, examples, and stroke diagrams
4. Bookmark kanji by clicking the star (☆) icon

### Quiz Mode
1. Click **"🎮 Quiz"** to start a quiz session
2. Answer questions about kanji readings, meanings, or context
3. Track your score, accuracy, and streak
4. Your progress is automatically saved with SRS scheduling

### Search & Filter
1. Click the **🔍** icon in the header
2. Type to search by kanji character, reading, or meaning
3. Click any result to jump to that kanji

### Settings
1. Click the **⚙️** icon in the header
2. Change theme, export/import progress, or adjust preferences

### Keyboard Shortcuts
- `←` / `→`: Navigate between kanji
- `Space`: Open study modal
- `Esc`: Close modals/panels
- `1-4`: Select quiz answer (in quiz mode)

## 🗂️ Project Structure

```
.
├── jlpt_n5_kanji_master.html  # Main application (single-file)
├── scrape_enhanced.py          # Python scraper for kanji data
├── kanji_data_enhanced.json    # Scraped kanji data (generated)
├── manifest.json               # PWA manifest
├── sw.js                       # Service worker for offline support
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📊 Data Structure

The kanji data JSON follows this structure:

```json
{
  "metadata": {
    "scrape_date": "2026-02-06T15:30:00Z",
    "total_kanji": 80,
    "version": "2.0",
    "source": "jlptsensei.com"
  },
  "kanji": [
    {
      "id": 1,
      "character": "日",
      "stroke_count": 4,
      "radical": "日",
      "radical_meaning": "sun, day",
      "jlpt_level": "N5",
      "svg": "<svg>...</svg>",
      "readings": {
        "onyomi": [{"word": "日", "reading": "ニチ", "meaning": "day"}],
        "kunyomi": [{"word": "日", "reading": "ひ", "meaning": "day, sun"}]
      },
      "examples": [...],
      "user_data": {
        "mastery_level": 0,
        "last_reviewed": null,
        "next_review": null,
        "times_correct": 0,
        "times_wrong": 0,
        "bookmarked": false,
        "notes": ""
      }
    }
  ]
}
```

## 🧠 SRS Algorithm

The app uses a simplified SM-2 algorithm for spaced repetition:

- **Quality 0-1**: Wrong answer → Reset to 1 day interval
- **Quality 2-3**: Hard answer → Repeat current interval
- **Quality 4-5**: Easy answer → Advance to next interval

Intervals: 1, 3, 7, 14, 30, 60, 120 days

## 💾 Data Storage

The app uses:
- **IndexedDB**: For kanji data and user progress (primary)
- **localStorage**: Fallback and settings storage

All data is stored locally in your browser - no server required!

## 🎨 Themes

- **🌊 Ocean** (Default): Blue gradient theme
- **🌸 Sakura**: Pink cherry blossom theme
- **🌲 Forest**: Green nature theme
- **🌙 Midnight**: Dark purple theme
- **🔆 High Contrast**: Accessibility-focused theme

## 🔧 Development

### Adding New Features

The app is built as a single HTML file for easy deployment. To modify:

1. Edit `jlpt_n5_kanji_master.html`
2. CSS is in the `<style>` section
3. JavaScript is in the `<script>` section at the bottom

### Scraping New Data

To update kanji data:

1. Run `scrape_enhanced.py`
2. The script will:
   - Scrape all pages from jlptsensei.com
   - Extract SVG stroke diagrams
   - Download and encode flashcard images
   - Parse readings and examples
   - Export to `kanji_data_enhanced.json`

**Note**: Be respectful of the website's rate limits. The scraper includes delays.

## 📱 PWA Installation

### Desktop (Chrome/Edge)
1. Visit the app in your browser
2. Click the install icon in the address bar
3. Or: Menu → "Install JLPT N5 Kanji Master"

### Mobile (iOS Safari)
1. Visit the app
2. Tap Share button
3. Select "Add to Home Screen"

### Mobile (Android Chrome)
1. Visit the app
2. Tap menu (⋮)
3. Select "Add to Home screen" or "Install app"

## 🌐 Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Android)

## 📝 License

This project is for educational purposes. The kanji data is scraped from jlptsensei.com for personal learning use.

## 🙏 Acknowledgments

- **jlptsensei.com** for providing comprehensive kanji data
- **Jisho.org** for kanji reference (mentioned in requirements)
- SM-2 algorithm for spaced repetition

## 🐛 Known Issues / TODO

- [ ] Writing practice canvas (stroke recognition)
- [ ] Audio pronunciation (Web Speech API)
- [ ] More quiz types (stroke count, radical)
- [ ] Achievement badges system
- [ ] Daily challenge mode
- [ ] Share card generator
- [ ] Cloud sync (optional)

## 📞 Support

For issues or questions:
1. Check the browser console for errors
2. Ensure `kanji_data_enhanced.json` exists or sample data loads
3. Try clearing browser cache/localStorage
4. Check IndexedDB in browser DevTools

---

**Happy Learning! 頑張ってください！** 🎌
