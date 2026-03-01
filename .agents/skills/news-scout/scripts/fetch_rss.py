#!/usr/bin/env python3
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import re

FEEDS = {
    "AI research": [
        ("ArXiv cs.AI", "http://export.arxiv.org/rss/cs.AI"),
        ("ArXiv cs.LG", "http://export.arxiv.org/rss/cs.LG"),
        ("ArXiv cs.CL", "http://export.arxiv.org/rss/cs.CL"),
        ("ArXiv cs.CR", "http://export.arxiv.org/rss/cs.CR"),
        ("Reddit r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.rss"),
        ("Reddit r/LocalLLaMA", "https://www.reddit.com/r/LocalLLaMA/.rss"),
        ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
        ("OpenAI blog", "https://openai.com/blog/rss/")
    ],
    "Startup/product": [
        ("Reddit r/startups", "https://www.reddit.com/r/startups/.rss"),
        ("Product Hunt", "https://www.producthunt.com/feed"),
        ("Y Combinator blog", "https://blog.ycombinator.com/feed/"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("Hacker News", "https://hnrss.org/frontpage")
    ]
}

AI_KEYWORDS = [
    "agent", "benchmark", "reasoning", "inference", "scaling",
    "alignment", "agi", "transformer", "multimodal", "evaluation"
]

STARTUP_KEYWORDS = [
    "funding", "seed", "series a", "saas", "launch",
    "revenue", "product-market fit", "yc", "acquisition"
]

import json
import urllib.parse
import time

def clean_html(raw_html):
    """HTMLタグを削除してクリーンなテキストを返す"""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def translate_to_japanese(text):
    """DeepL等のAPIキーがないため、フリーの翻訳API(Google Translate URL-based)を使用して日本語に翻訳・要約する"""
    if not text or text.strip() == "":
        return ""
    
    # 連続のAPI呼び出しを防ぐための簡易スリープ
    time.sleep(0.5)
    
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            translated = "".join([sentence[0] for sentence in result[0] if sentence[0]])
            
            # 要約を200文字以内に丸める
            if len(translated) > 195:
                translated = translated[:195] + "..."
            return translated
    except Exception as e:
        print(f"翻訳エラー: {e}")
        # フォールバックとして元のテキストを最大200文字にする
        fallback = text if len(text) <= 195 else text[:195] + "..."
        return "[Eng] " + fallback

def calculate_score(title, summary_bullets):
    """簡易的なキーワードベースのスコアリングエンジン"""
    score = 0.0
    t_lower = title.lower()
    s_lower = " ".join(summary_bullets).lower()
    
    # AI Keywords (x1.5 weight)
    for kw in AI_KEYWORDS:
        if kw in t_lower:
            score += 3.0 * 1.5
        if kw in s_lower:
            score += 1.0 * 1.5
            
    # Startup Keywords (x1.0 weight)
    for kw in STARTUP_KEYWORDS:
        if kw.lower() in t_lower:
            score += 3.0 * 1.0
        if kw.lower() in s_lower:
            score += 1.0 * 1.0
            
    return score

def extract_text(element):
    """XML要素から安全にテキストを抽出する"""
    if element is not None and element.text:
        return element.text.strip()
    return ""

def generate_why_it_matters(score, category):
    """Why It Matters の自動生成 (1-2行)"""
    if score >= 6.0:
        return "重要キーワードが複数含まれており、業界に大きな影響を与える可能性が高い必読のニュースです。"
    elif score >= 3.0:
        return f"最新の動向や技術に関する注目すべき{category}関連のトピックです。"
    return "日々の情報収集として目を通しておく価値がある内容です。"

def parse_feed_xml(xml_data):
    """XMLデータを解析し、RSS/Atom双方に対応してエントリのリストを返す"""
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return []
        
    entries = root.findall('.//item') # RSS
    if not entries:
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry') # Atom
    
    parsed_items = []
    for item in entries[:10]: # feeds up to 10
        # Title
        title_elem = item.find('title')
        if title_elem is None:
            title_elem = item.find('{http://www.w3.org/2005/Atom}title')
        title = extract_text(title_elem) or 'タイトルなし'
        
        # Link
        link_elem = item.find('link')
        url = ""
        if link_elem is not None:
            if link_elem.text and link_elem.text.strip():
                url = link_elem.text.strip()
            else:
                url = link_elem.attrib.get('href', '')
        if not url:
            link_atom = item.find('{http://www.w3.org/2005/Atom}link')
            if link_atom is not None:
                url = link_atom.attrib.get('href', '')
        if not url:
            url = 'リンクなし'
            
        # Description/Summary
        desc_elem = item.find('description')
        if desc_elem is None:
            desc_elem = item.find('{http://www.w3.org/2005/Atom}summary')
        if desc_elem is None:
            desc_elem = item.find('{http://www.w3.org/2005/Atom}content')
            
        desc = extract_text(desc_elem)
        clean_desc = clean_html(desc)
        
        # Bullet extraction and translation
        sentences = [s.strip() for s in clean_desc.split('. ') if s.strip()]
        bullets = sentences[:2]
        if not bullets:
            bullets = ["詳細な要約は利用できません。"]
        else:
            bullets = [b + ("." if not b.endswith(".") else "") for b in bullets]
            
        # 英語の要素をスコアリングするわけではないので、先にタイトルと要約を翻訳しておく
        # ただし、スコアリングエンジン（AI_KEYWORDS, STARTUP_KEYWORDS）は英語を前提としているため、
        # 解析自体は元の英語に対して行い、保存・表示用として翻訳版をデータにもたせる形にする。
        
        parsed_items.append({
            'title_en': title,
            'title_ja': translate_to_japanese(title),
            'url': url,
            'summary_en': bullets,
            # 要約を100〜200字に収めるため、翻訳して連結した上で必要ならカット
            'summary_ja': translate_to_japanese(" ".join(bullets))
        })
        
    return parsed_items

def fetch_feed(url, category):
    """RSSフィードから最大10件取得しスコアリングしたリストを返す"""
    items = []
    try:
        # User-Agentを一般的なモダンブラウザに見せかけて403ブロックを回避する
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            
            parsed = parse_feed_xml(xml_data)
            
            for p in parsed:
                # 英語のテキストに対してスコアリングを実行
                score = calculate_score(p['title_en'], p['summary_en'])
                items.append({
                    'title': p['title_ja'], # 出力用は日本語
                    'url': p['url'],
                    'summary': p['summary_ja'], # 出力用は日本語の単一文字列
                    'score': score,
                    'category': category,
                    'why_it_matters': generate_why_it_matters(score, category)
                })
    except Exception as e:
        print(f"フィードの取得エラー {url}: {e}")
    return items

def deduplicate_items(items):
    """URLベースの重複排除。重複する場合はスコアが高いものを残す"""
    unique_items = {}
    for item in items:
        url = item['url']
        if url == 'リンクなし':
            # リンクなしの場合はタイトルで代用
            url = item['title']
            
        if url not in unique_items or item['score'] > unique_items[url]['score']:
            unique_items[url] = item
    return list(unique_items.values())

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    out_dir = os.path.join(root_dir, 'NEWS')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{today}.md")
    
    all_items = []
    
    for category, sources in FEEDS.items():
        for source_name, url in sources:
            items = fetch_feed(url, category)
            all_items.extend(items)
            
    # 2. Deduplication across all feeds
    all_items = deduplicate_items(all_items)
    
    # Check if scoring worked at all across the items
    scoring_worked = any(item['score'] > 0 for item in all_items)
    
    # 4. Global Ranking / Fallback Behavior
    if scoring_worked:
        # Sort globally by score descending
        all_items.sort(key=lambda x: x['score'], reverse=True)
        top_items = all_items[:10]
    else:
        # Fallback to simple top 3 per feed behavior to maintain backward compatibility
        # If scoring fails, we just want to grab a reasonable chunk of latest news
        all_items.sort(key=lambda x: x['category']) # simple group by cat
        top_items = all_items[:30] # rough fallback
        
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"# Daily News: {today}\n\n")
        f.write("## Top Ranked (AI / Startup Focus)\n\n")
        
        if not top_items:
            f.write("- 本日は取得されたアイテムがありませんでした。\n\n")
        else:
            # Markdownテーブルのヘッダーを作成
            f.write("| スコア | タイトル | 概要 | キーワード |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            for item in top_items:
                # リンク付きのタイトル
                title_link = f"[{item['title']}]({item['url']})"
                
                # 要約テキスト（翻訳済み・リストではなく単一文字列）
                summary_text = item['summary']
                
                # なぜ重要かも追加
                summary_text = f"**{item['why_it_matters']}**<br>{summary_text}"
                
                # タグ
                tag_str = f"#{item['category'].replace(' ', '').replace('/', '')}"
                
                # パイプ文字などテーブルを壊す文字をエスケープ
                title_link = title_link.replace("|", "&#124;")
                summary_text = summary_text.replace("|", "&#124;")
                tag_str = tag_str.replace("|", "&#124;")
                
                f.write(f"| {item['score']} | {title_link} | {summary_text} | {tag_str} |\n")
            
    print(f"日次ニュースを書き込みました: {out_file}")

if __name__ == '__main__':
    main()
