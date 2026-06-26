import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os

BASE_URL = "https://docs.ghost.org"
OUTPUT_DIR = "docs"

def get_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def parse_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith(BASE_URL):
            links.add(full_url)
    return links

def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)

def save_doc(url, text):
    filename = urlparse(url).path.strip('/').replace('/', '_') or 'index'
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Source: {url}\n\n")
        f.write(text)
    print(f"Saved: {filepath}")

def scrape():
    visited = set()
    to_visit = {BASE_URL}
    
    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        
        print(f"Scraping: {url}")
        html = get_page(url)
        
        if html:
            text = extract_text(html)
            save_doc(url, text)
            new_links = parse_links(html, url)
            to_visit.update(new_links - visited)
        
        visited.add(url)
        time.sleep(1)
    
    print(f"Done. Scraped {len(visited)} pages.")

if __name__ == "__main__":
    scrape()
