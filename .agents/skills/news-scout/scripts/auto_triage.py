import os
import json
import urllib.request
import re
from datetime import datetime

def get_today_news_path():
    today = datetime.now().strftime('%Y-%m-%d')
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    return os.path.join(root_dir, 'NEWS', f"{today}.md")

def call_gemini(prompt, api_key):
    """Call Gemini API using only standard libraries"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Gemini API Error: {e}")
    return None

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    file_path = get_today_news_path()
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # If it already has triage, skip
    if "## 🎯 本日のトリアージ (Top 5 Actions)" in content:
        print("Triage already exists for today.")
        return

    # Or if there's no API key, we skip triage step
    if not api_key:
        print("GEMINI_API_KEY is not set. Skipping automated LLM triage.")
        return

    prompt = f"""
以下のニュース一覧から、AIリサーチ、スタートアップ、技術開発に関連する最も重要な上位5件を選んでください。
それぞれについて、「[深く読む]」「[アイデアに変換]」「[無視する]」のいずれかのアクションと、その理由を1文で書いてください。

出力フォーマットは必ず以下に厳密に従ってください。その他の挨拶や前置きは一切出力しないでください。

## 🎯 本日のトリアージ (Top 5 Actions)

- 🧠 **[深く読む]** [記事タイトル](URL)
  - **理由**: なぜそれが重要かの理由
- 💡 **[アイデアに変換]** [記事タイトル](URL)
  - **理由**: なぜそれが重要かの理由
- ⏭️ **[無視する]** [記事タイトル](URL)
  - **理由**: 無視する理由

---

ニュース本文:
{content}
"""
    
    print("Running automated triage generation...")
    triage_result = call_gemini(prompt, api_key)
    
    if triage_result:
        # Avoid double markdown block if Gemini generated it
        triage_result = triage_result.replace("```markdown", "").replace("```", "").strip()
        
        # Insert triage_result into content right after the main header
        parts = content.split('\n\n', 1)
        if len(parts) == 2:
            new_content = parts[0] + "\n\n" + triage_result + "\n\n" + parts[1]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Successfully injected automated triage into the news file.")
        else:
            print("Failed to parse the news file for injection.")
    else:
        print("Triage generation failed.")

if __name__ == '__main__':
    main()
