import requests
import time
import random
import logging
import os
import sys
from . import config

# Ensure log directory exists
os.makedirs(config.LOG_DIR, exist_ok=True)

# Custom StreamHandler that handles encoding errors gracefully
class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            super().emit(record)
        except UnicodeEncodeError:
            # Replace problematic characters with safe alternatives
            try:
                msg = self.format(record)
                # Replace common emojis with text equivalents
                msg = msg.replace('⏳', '[WAIT]')
                msg = msg.replace('✅', '[OK]')
                msg = msg.replace('🛑', '[STOP]')
                msg = msg.replace('⚠️', '[WARN]')
                msg = msg.replace('❌', '[ERROR]')
                msg = msg.replace('💀', '[FAIL]')
                msg = msg.replace('💾', '[SAVE]')
                stream = self.stream
                stream.write(msg + self.terminator)
                self.flush()
            except Exception:
                self.handleError(record)

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{config.LOG_DIR}/scraper.log", encoding='utf-8'),
        SafeStreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)

    def _wait_politely(self):
        """Sleeps for a random interval to mimic human reading time."""
        delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
        logger.info(f"⏳ Pausing for {delay:.2f} seconds...")
        time.sleep(delay)

    def fetch(self, url):
        """
        Fetches a URL with robust error handling and exponential backoff.
        """
        retries = 0
        while retries < config.MAX_RETRIES:
            try:
                self._wait_politely()
                
                response = self.session.get(url, timeout=config.TIMEOUT)
                
                # Handle Rate Limiting (429) specifically
                if response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", config.COOLDOWN_ON_429))
                    logger.warning(f"🛑 Rate limited. Cooling down for {wait_time}s.")
                    time.sleep(wait_time)
                    retries += 1
                    continue

                # Raise errors for 4xx and 5xx
                response.raise_for_status()
                
                logger.info(f"✅ Success: {url}")
                return response.text

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code
                if status in config.RETRY_STATUS_CODES:
                    logger.warning(f"⚠️ Server Error ({status}). Retrying...")
                    retries += 1
                    time.sleep(2 ** retries) # Exponential backoff
                else:
                    logger.error(f"❌ Client Error ({status}): {url}. Skipping.")
                    return None # Do not retry 404s
            
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Network Error: {e}. Retrying...")
                retries += 1
                time.sleep(2 ** retries)

        logger.error(f"💀 Failed to fetch {url} after {config.MAX_RETRIES} attempts.")
        return None