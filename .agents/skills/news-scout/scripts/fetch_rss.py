#!/usr/bin/env python3
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import re

FEEDS = {
    "AI research": [("ArXiv AI", "http://export.arxiv.org/rss/cs.AI")],
    "Security": [("Krebs on Security", "https://krebsonsecurity.com/feed/")],
    "Startup/product": [("TechCrunch", "https://techcrunch.com/feed/")],
    "Hardware": [("Tom's Hardware", "https://www.tomshardware.com/feeds/all")],
    "Developer ecosystem": [("Hacker News", "https://hnrss.org/frontpage")]
}

def clean_html(raw_html):
    """Remove HTML tags from a string."""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def fetch_feed(url):
    """Fetch and parse RSS feed. Returns top 3 items."""
    items = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Basic RSS/Atom parsing handling
            for item in root.findall('.//item')[:3]: 
                title = item.find('title').text if item.find('title') is not None else 'No Title'
                link = item.find('link').text if item.find('link') is not None else 'No Link'
                desc = item.find('description').text if item.find('description') is not None else ''
                
                desc = clean_html(desc)
                # Split roughly by sentences and take first two as summary bullets to avoid copyright issues
                sentences = [s.strip() for s in desc.split('. ') if s.strip()]
                bullets = sentences[:2]
                if not bullets:
                    bullets = ["No detailed summary available."]
                else:
                    bullets = [b + ("." if not b.endswith(".") else "") for b in bullets]
                
                items.append({
                    'title': title,
                    'url': link,
                    'summary': bullets
                })
    except Exception as e:
        print(f"Error fetching feed {url}: {e}")
    return items

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    # Assuming script is in .agents/skills/news-scout/scripts/, 
    # root directory is 4 levels up.
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    out_dir = os.path.join(root_dir, 'NEWS')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{today}.md")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"# Daily News: {today}\n\n")
        
        for category, sources in FEEDS.items():
            f.write(f"## {category}\n\n")
            for source_name, url in sources:
                f.write(f"### {source_name}\n\n")
                items = fetch_feed(url)
                if not items:
                    f.write("- No items fetched today.\n\n")
                
                for item in items:
                    f.write(f"**Title**: {item['title']}\n")
                    f.write(f"**URL**: {item['url']}\n")
                    f.write("**Summary**:\n")
                    for bullet in item['summary']:
                        f.write(f"- {bullet}\n")
                    f.write(f"**Tags**: #{category.replace(' ', '').replace('/', '')}\n\n")
    print(f"Daily news written to {out_file}")

if __name__ == '__main__':
    main()
