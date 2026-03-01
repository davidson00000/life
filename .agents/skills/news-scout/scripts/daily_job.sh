#!/bin/bash
# macOSのcronから実行するためのラッパースクリプト
# 実行ディレクトリを固定
cd /Users/kousukenakamura/life

# パスを設定（cron環境では環境変数がロードされないため）
export PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH

# 環境変数の読み込み（もしあれば .env からAPIキーなどを取得）
if [ -f .env ]; then
  source .env
fi

echo "--- 実行開始: $(date) ---"

# 1. ニュースのフェッチと重複排除（最大30件）
python3 .agents/skills/news-scout/scripts/fetch_rss.py

# 2. 自動トリアージの実行 (GEMINI_API_KEY が .env などで設定されている場合のみ動作します)
if [ -n "$GEMINI_API_KEY" ]; then
  python3 .agents/skills/news-scout/scripts/auto_triage.py
else
  echo "GEMINI_API_KEY が未設定のため、LLM自動トリアージはスキップします。"
fi

# 3. GitHubへの反映
git add NEWS/
git commit -m "chore: auto-update daily news & triage list for $(date +'%Y-%m-%d')" || echo "No changes to commit"
git push origin main || echo "No changes to push"

echo "--- 実行完了: $(date) ---"
