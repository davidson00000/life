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
    """文字列からHTMLタグを削除する。"""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def fetch_feed(url):
    """RSSフィードを取得してパースする。上位3件のアイテムを返す。"""
    items = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # 基本的なRSS/Atom解析の処理
            for item in root.findall('.//item')[:3]: 
                title = item.find('title').text if item.find('title') is not None else 'タイトルなし'
                link = item.find('link').text if item.find('link') is not None else 'リンクなし'
                desc = item.find('description').text if item.find('description') is not None else ''
                
                desc = clean_html(desc)
                # 著作権問題を回避するため、文でおおまかに分割し、最初の2つを要約として取得する
                sentences = [s.strip() for s in desc.split('. ') if s.strip()]
                bullets = sentences[:2]
                if not bullets:
                    bullets = ["詳細な要約は利用できません。"]
                else:
                    bullets = [b + ("." if not b.endswith(".") else "") for b in bullets]
                
                items.append({
                    'title': title,
                    'url': link,
                    'summary': bullets
                })
    except Exception as e:
        print(f"フィードの取得エラー {url}: {e}")
    return items

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    # スクリプトが .agents/skills/news-scout/scripts/ にあると仮定し、
    # 4階層上のディレクトリをルートディレクトリとする。
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
                    f.write("- 本日は取得されたアイテムがありませんでした。\n\n")
                
                for item in items:
                    f.write(f"**タイトル**: {item['title']}\n")
                    f.write(f"**URL**: {item['url']}\n")
                    f.write("**要約**:\n")
                    for bullet in item['summary']:
                        f.write(f"- {bullet}\n")
                    f.write(f"**タグ**: #{category.replace(' ', '').replace('/', '')}\n\n")
    print(f"日次ニュースを書き込みました: {out_file}")

if __name__ == '__main__':
    main()
