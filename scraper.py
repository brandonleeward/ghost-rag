import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
import sys

OUTPUT_DIR = "docs"

def get_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def parse_links(html, base_url, base_domain, path_prefix=None):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith(base_domain):
            if path_prefix is None or full_url.startswith(path_prefix):
                links.add(full_url.split('#')[0])
    return links

def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)

def url_to_filename(url, base_domain):
    path = urlparse(url).path.strip('/')
    clean = path.replace('/', '_') or 'index'
    domain = urlparse(base_domain).netloc.replace('.', '_')
    filename = f"{domain}_{clean}"
    # Truncate to 200 chars to stay under macOS 255 limit
    if len(filename) > 200:
        filename = filename[:200]
    return f"{filename}.txt"

def save_doc(url, text, base_domain):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = url_to_filename(url, base_domain)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Source: {url}\n\n")
        f.write(text)
    print(f"Saved: {filepath}")

def scrape(base_url):
    base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
    path_prefix = base_url
    visited = set()
    to_visit = {base_url}

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue

        print(f"Scraping: {url}")
        html = get_page(url)

        if html:
            text = extract_text(html)
            save_doc(url, text, base_domain)
            new_links = parse_links(html, url, base_domain, path_prefix)
            to_visit.update(new_links - visited)

        visited.add(url)
        time.sleep(0.5)

    print(f"\nDone. Scraped {len(visited)} pages from {base_url}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <url>")
        print("Example: python scraper.py https://docs.ghost.org")
        sys.exit(1)
    
    scrape(sys.argv[1])
