import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

base = 'https://jlptsensei.com/jlpt-n5-kanji-list/'
r = requests.get(base)
soup = BeautifulSoup(r.content, 'html.parser')
links = soup.select('a[href*="/learn-japanese-kanji/"]')
urls = []
for a in links:
    href = a['href']
    if not href.endswith('/feed/') and '#' not in href:
        urls.append(urljoin(base, href))

urls = sorted(list(set(urls)))
with open('urls.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(urls))
print(f"Found {len(urls)} URLs")
