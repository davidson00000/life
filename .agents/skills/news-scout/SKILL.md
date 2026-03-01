---
name: News Scout
description: 設定可能なRSSフィードから日々のニュースを取得し、著作権侵害を避けて要約し、NEWS/ に出力する。
---
# News Scout

このスキルは `scripts/fetch_rss.py` を実行して、設定されたRSSフィードから日次ニュースを集約します。

## 要求されるフォーマット
スクリプトは `NEWS/` ディレクトリにMarkdownファイル（`NEWS/yyyy-mm-dd.md`）を生成します。
各記事のエントリには以下が含まれます：
- タイトル (Title)
- URL
- 2つの箇条書きによる要約（著作権侵害を避けるため要約または切り詰められる）
- カテゴリに関連するタグ

## フィードの設定
フィードを追加または削除するには、`scripts/fetch_rss.py` 内の `FEEDS` 辞書を変更してください。カテゴリは以下の通りです：
- AIリサーチ (AI research)
- セキュリティ (Security)
- スタートアップ/プロダクト (Startup/product)
- ハードウェア (Hardware)
- 開発者エコシステム (Developer ecosystem)
