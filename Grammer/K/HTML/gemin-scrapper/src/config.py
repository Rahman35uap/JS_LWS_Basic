import os
import random

# --- Target Settings ---
BASE_URL = "https://jlptsensei.com/jlpt-n5-kanji-list/" # Example safe testing site
START_URLS = [
    "https://jlptsensei.com/jlpt-n5-kanji-list/",
    "https://jlptsensei.com/jlpt-n4-kanji-list/",
    "https://jlptsensei.com/jlpt-n3-kanji-list/"
]

# --- Advanced User Agent Rotation (5 Real Browsers) ---
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
]

# --- Complete Browser Headers Template ---
def get_browser_headers(user_agent=None, referer=None):
    """
    Generates complete browser headers with 20+ headers for realistic simulation.
    """
    if user_agent is None:
        user_agent = random.choice(USER_AGENTS)
    
    # Detect browser type from user agent
    is_chrome = "Chrome" in user_agent and "Edg" not in user_agent
    is_firefox = "Firefox" in user_agent
    is_edge = "Edg" in user_agent
    
    # Chrome/Edge sec-ch-ua headers
    if is_chrome or is_edge:
        chrome_version = "120"
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none" if referer is None else "same-origin",
            "Sec-Fetch-User": "?1",
            "sec-ch-ua": f'"Not_A Brand";v="8", "Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"' if "Windows" in user_agent else '"macOS"',
            "Cache-Control": "max-age=0",
        }
    elif is_firefox:
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none" if referer is None else "same-origin",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
    else:
        # Fallback headers
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    # Add referer if provided
    if referer:
        headers["Referer"] = referer
    
    return headers

# --- Default Headers (for backward compatibility) ---
HEADERS = get_browser_headers()

# --- Human-Like Behavior Settings ---
MIN_DELAY = 2.0          # Minimum seconds between requests
MAX_DELAY = 6.0          # Maximum seconds between requests
LONG_PAUSE_PROBABILITY = 0.15  # 15% chance of a long pause (simulating reading)
LONG_PAUSE_MIN = 8.0     # Minimum long pause duration
LONG_PAUSE_MAX = 15.0    # Maximum long pause duration
BREAK_EVERY_N_REQUESTS = 10  # Take a break every N requests
BREAK_DURATION_MIN = 15  # Minimum break duration (seconds)
BREAK_DURATION_MAX = 30  # Maximum break duration (seconds)

# --- Network Settings ---
TIMEOUT = 20             # Seconds to wait for a server response
KEEP_ALIVE = True        # Use keep-alive connections
MAX_REDIRECTS = 5        # Maximum redirects to follow

# --- Retry & Recovery Logic ---
MAX_RETRIES = 3          # Maximum retry attempts
RETRY_STATUS_CODES = [500, 502, 503, 504, 408, 429]  # Retry on these status codes
COOLDOWN_ON_DETECTION = 60  # Seconds to wait if bot detected
COOLDOWN_ON_429 = 60    # Seconds to wait if rate limited
EXPONENTIAL_BACKOFF_BASE = 2  # Base for exponential backoff (2^retry_count)

# --- Bot Detection Patterns ---
BLOCK_INDICATORS = [
    # Status codes
    403,  # Forbidden
    429,  # Too Many Requests
    # Response content patterns
    "cloudflare",
    "cloudflare-nginx",
    "checking your browser",
    "please wait",
    "access denied",
    "blocked",
    "captcha",
    "challenge",
    "rate limit",
    "too many requests",
    "forbidden",
    # Common bot detection services
    "datadome",
    "perimeterx",
    "shape security",
    "akamai",
    "incapsula"
]

# --- Response Validation ---
MIN_RESPONSE_LENGTH = 100  # Minimum expected response length (bytes)
VALID_HTML_INDICATORS = ["<html", "<!DOCTYPE", "<body", "<div"]  # Must contain at least one

# --- Progress Tracking ---
SAVE_PROGRESS_EVERY = 5  # Save progress every N successful requests
TRACK_FAILED_IMAGES = True  # Track failed image downloads

# --- Paths ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(base_dir, 'data')
LOG_DIR = os.path.join(base_dir, 'logs')
PROGRESS_FILE = os.path.join(base_dir, 'progress.json')
FAILED_IMAGES_FILE = os.path.join(DATA_DIR, 'failed_images.txt')