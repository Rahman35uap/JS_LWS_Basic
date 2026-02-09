import os
from src.scraper import WebScraper
from src.parser import parse_book_page
from src.storage import save_to_csv
from src import config

def main():
    # Ensure directories exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)

    print("[START] Starting Scraper Project...")
    
    # Initialize Scraper
    bot = WebScraper()
    
    all_data = []

    # Process URLs
    for url in config.START_URLS:
        html = bot.fetch(url)
        
        if html:
            data = parse_book_page(html)
            if data:
                all_data.extend(data)
                print(f"   found {len(data)} items on page.")
    
    # Save Results
    if all_data:
        save_to_csv(all_data)
        print("[DONE] Done! Data saved to 'data/results.csv'")
    else:
        print("[WARN] No data collected.")

if __name__ == "__main__":
    main()