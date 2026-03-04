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
        ("OpenAI blog", "https://openai.com/blog/rss/"),
        ("Hugging Face blog", "https://huggingface.co/blog/feed.xml"),
        ("Hugging Face papers", "https://rsshub.app/huggingface/daily-papers"),
        ("DeepMind blog", "https://deepmind.com/blog/feed/basic"),
        ("BAIR blog", "http://bair.berkeley.edu/blog/feed.xml"),
        ("Zenn topic llm", "https://zenn.dev/topics/llm/feed"),
        ("Google News (AI agent)", "https://news.google.com/rss/search?q=%22AI+agent%22+OR+%22LLM+agent%22&hl=en-US&gl=US&ceid=US:en"),
        ("Google News (AIエージェント)", "https://news.google.com/rss/search?q=%22AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%22+OR+%22%E7%94%9F%E6%88%90AI%22+OR+%22LLM%22&hl=ja&gl=JP&ceid=JP:ja")
    ],
    "Startup/product": [
        ("Reddit r/startups", "https://www.reddit.com/r/startups/.rss"),
        ("Product Hunt", "https://www.producthunt.com/feed"),
        ("Y Combinator blog", "https://blog.ycombinator.com/feed/"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("Hacker News", "https://hnrss.org/frontpage"),
        ("Hacker News Official", "https://news.ycombinator.com/rss"),
        ("Zenn trend", "https://zenn.dev/feed"),
        ("Hatena IT hotentry", "https://b.hatena.ne.jp/hotentry/it.rss"),
        ("Google News (Solopreneur)", "https://news.google.com/rss/search?q=solopreneur+OR+%22indie+hacker%22&hl=en-US&gl=US&ceid=US:en"),
        ("Google News (一人起業)", "https://news.google.com/rss/search?q=%22%E4%B8%80%E4%BA%BA%E8%B5%B7%E6%A5%AD%22&hl=ja&gl=JP&ceid=JP:ja")
    ]
}

AI_KEYWORDS = [
    "agent", "benchmark", "reasoning", "inference", "scaling",
    "alignment", "agi", "transformer", "multimodal", "evaluation",
    "agentic", "tool use", "function calling", "computer use",
    "rag", "eval", "post-training", "rlhf", "dpo", "moe", "diffusion",
    "aiエージェント", "生成ai", "自律", "評価"
]

STARTUP_KEYWORDS = [
    "funding", "seed", "series a", "saas", "launch",
    "revenue", "product-market fit", "yc", "acquisition",
    "bootstrapping", "solopreneur", "indiehacker", "monetize",
    "pricing", "mvp", "churn", "cac", "ltv", "pmf", "distribution",
    "一人起業", "収益化", "価格", "顧客獲得"
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

def parse_feed_xml(xml_data, url=""):
    """XMLデータを解析し、RSS/Atom双方に対応してエントリのリストを返す"""
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        print(f"URL {url} の XML パースに失敗しました")
        return []
        
    entries = root.findall('.//item') # RSS
    if not entries:
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry') # Atom
    
    parsed_items = []
    for item in entries[:30]: # feeds up to 30件取得
        # Title
        title_elem = item.find('title')
        if title_elem is None:
            title_elem = item.find('{http://www.w3.org/2005/Atom}title')
        title = extract_text(title_elem) or 'タイトルなし'
        
        # Link
        link_elem = item.find('link')
        item_url = ""
        if link_elem is not None:
            if link_elem.text and link_elem.text.strip():
                item_url = link_elem.text.strip()
            else:
                item_url = link_elem.attrib.get('href', '')
        if not item_url:
            link_atom = item.find('{http://www.w3.org/2005/Atom}link')
            if link_atom is not None:
                item_url = link_atom.attrib.get('href', '')
        if not item_url:
            item_url = 'リンクなし'
            
        # Date (pubDate / published / updated)
        date_elem = item.find('pubDate')
        if date_elem is None:
            date_elem = item.find('{http://www.w3.org/2005/Atom}published')
        if date_elem is None:
            date_elem = item.find('{http://www.w3.org/2005/Atom}updated')
            
        raw_date = extract_text(date_elem)
        parsed_date = ""
        if raw_date:
            try:
                # Try to parse standard RSS date format, fallback to raw string if it fails
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(raw_date)
                parsed_date = dt.strftime('%Y-%m-%d')
            except Exception:
                # If it's Atom or ISO, do a rough chop to get YYYY-MM-DD
                parsed_date = raw_date[:10]
                
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
            
        # 英語の要素をスコアリングするため、ここでは翻訳を遅延し生のまま返す
        parsed_items.append({
            'title_en': title,
            'url': item_url,
            'date': parsed_date,
            'summary_en': bullets
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
            
            parsed = parse_feed_xml(xml_data, url)
            
            for p in parsed:
                # 英語のテキストに対してスコアリングを実行
                score = calculate_score(p['title_en'], p['summary_en'])
                items.append({
                    'title_en': p['title_en'],
                    'url': p['url'],
                    'date': p.get('date', ''),
                    'summary_en': p['summary_en'],
                    'score': score,
                    'category': category
                })
    except Exception as e:
        print(f"カテゴリ {category} のソース (URL: {url}) 取得でエラー: {e}")
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

def get_historical_urls(out_dir, days=7):
    """過去指定日数のNEWSファイルからURLを抽出し、セットとして返す"""
    from datetime import timedelta
    historical_urls = set()
    
    target_dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, days + 1)]
    
    for date_str in target_dates:
        file_path = os.path.join(out_dir, f"{date_str}.md")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Markdown形式のリンク [タイトル](URL) からURLを抽出
                urls = re.findall(r'\[.*?\]\((https?://[^\)]+)\)', content)
                historical_urls.update(urls)
                
    return historical_urls

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    out_dir = os.path.join(root_dir, 'NEWS')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{today}.md")
    
    historical_urls = get_historical_urls(out_dir, days=7)
    all_items = []
    
    for category, sources in FEEDS.items():
        for source_name, url in sources:
            items = fetch_feed(url, category)
            all_items.extend(items)
            
    # 2. Deduplication across all feeds
    all_items = deduplicate_items(all_items)
    
    # 3. Filter out historical URLs
    new_items = []
    for item in all_items:
        if item['url'] not in historical_urls and item['url'] != 'リンクなし':
            new_items.append(item)
        elif item['url'] == 'リンクなし':
            new_items.append(item)
            
    all_items = new_items
    
    # Check if scoring worked at all across the items
    scoring_worked = any(item['score'] > 0 for item in all_items)
    
    # 4. Global Ranking / Fallback Behavior
    if scoring_worked:
        # Sort globally by score descending
        all_items.sort(key=lambda x: x['score'], reverse=True)
        top_items = all_items[:30] # 30件取得

    else:
        # Fallback to simple top 30 per feed behavior to maintain backward compatibility
        all_items.sort(key=lambda x: x['category']) # simple group by cat
        top_items = all_items[:30] # rough fallback
        
    # 5. Top 30 items obtained. Translate them here to save translation API calls.
    for item in top_items:
        item['title_ja'] = translate_to_japanese(item['title_en']).replace('\n', ' ').replace('\r', '')
        summary_raw = translate_to_japanese(" ".join(item['summary_en']))
        item['summary_ja'] = summary_raw.replace('\n', ' ').replace('\r', '')
        item['why_it_matters'] = generate_why_it_matters(item['score'], item['category'])
        
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"# Daily News: {today}\n\n")
        f.write("## Top Ranked (AI / Startup Focus)\n\n")
        
        if not top_items:
            f.write("- 本日は新しい取得アイテムがありませんでした。\n\n")
        else:
            for item in top_items:
                # リンク付きのタイトル
                title_link = f"[{item['title_ja']}]({item['url']})"
                
                # 要約テキスト（翻訳済み・リストではなく単一文字列）
                summary_text = item['summary_ja']
                
                # なぜ重要か
                why = item['why_it_matters']
                
                # タグ
                tag_str = f"#{item['category'].replace(' ', '').replace('/', '')}"
                
                # 日付（あれば）
                date_str = f" ({item['date']})" if item.get('date') else ""
                
                # リスト形式で出力
                f.write(f"- **(スコア: {item['score']})** {title_link}{date_str}\n")
                f.write(f"  - **なぜ重要か**: {why}\n")
                f.write(f"  - **概要**: {summary_text}\n")
                f.write(f"  - **タグ**: {tag_str}\n")
                f.write("\n")
            
    print(f"日次ニュースを書き込みました: {out_file}")

if __name__ == '__main__':
    main()
