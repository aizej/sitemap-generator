from urllib.parse import urljoin, urlparse
from collections import deque
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import sys

# Configuration
ROOT_URL = 'http://158.101.167.252'
MAX_PAGES = 100
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; SitemapGeneratorBot/1.0)'}

visited_pages = set()
seen_urls = set()

def normalize_url(url):
    return url.split('#')[0].split('?')[0].rstrip('/')

def is_internal(link, root_domain):
    parsed = urlparse(link)
    return parsed.netloc in ['', root_domain]

def is_a_file(url):
    endings = [
        '.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.tar.gz', '.rar',
        '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.avi', '.mov',
        '.apk', '.mkv', '.webm', '.flv', '.wmv', '.txt', '.csv', '.json', '.xml'
    ]
    return any(url.lower().endswith(ext) for ext in endings)

def crawl_page(url, root_domain):
    visited_pages.add(url)
    found_links = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if not response.ok or 'text/html' not in response.headers.get('Content-Type', ''):
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        for a in soup.find_all('a', href=True):
            href = a['href']
            full_link = normalize_url(urljoin(url, href))

            if full_link in visited_pages or full_link in seen_urls:
                continue
            if not is_internal(full_link, root_domain):
                continue
            if is_a_file(full_link):
                continue
            if full_link == ROOT_URL:
                continue

            if full_link.startswith("mailto:") or full_link.startswith("javascript:"):
                continue

            seen_urls.add(full_link)
            found_links.append(full_link)

        return found_links

    except Exception:
        return []

def crawl_bfs(start_url, root_domain, MAX_PAGES):
    queue = deque([start_url])

    while queue and len(visited_pages) < MAX_PAGES:
        print(f"Queue size: {len(queue)}")
        print(f"Visited pages: {len(visited_pages)}")
        #clear the output to avoid clutter
        

        current_url = queue.popleft()
        if current_url in visited_pages:
            continue

        

        found_links = crawl_page(current_url, root_domain)
        for link in found_links:
            if link not in visited_pages and link not in queue:
                queue.append(link)

def generate_sitemap_xml(urls):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in sorted(urls):
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = url

    tree = ET.ElementTree(urlset)
    #tree.write("sitemap.xml", encoding="utf-8", xml_declaration=True)
    print(f"✅ All done! Here is your sitemap with {len(visited_pages)} URLs \n\n")

    print("<?xml version='1.0' encoding='UTF-8'?>")
    
    xml_str = ET.tostring(urlset, encoding="utf-8", method="xml").decode("utf-8")
    for i in range(0, len(xml_str), 500):  # 500 chars per line, for example
        print(xml_str[i:i+500])  

def main(ROOT_URL=ROOT_URL, MAX_PAGES=MAX_PAGES):
    root_domain = urlparse(ROOT_URL).netloc
    crawl_bfs(ROOT_URL, root_domain, MAX_PAGES)
    generate_sitemap_xml(visited_pages)
    


if __name__ == "__main__":
    #get the arguments from the command line

    if len(sys.argv) > 2:
        ROOT_URL = sys.argv[1]
        MAX_PAGES = int(sys.argv[2])
        print(f"Using ROOT_URL: {ROOT_URL} and MAX_PAGES: {MAX_PAGES}")
        main(ROOT_URL=ROOT_URL, MAX_PAGES=MAX_PAGES)

    else:
        print("fatal error: not enough arguments")