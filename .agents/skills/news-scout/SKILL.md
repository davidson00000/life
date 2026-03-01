---
name: News Scout
description: Fetches daily news from configurable RSS feeds, summarizes without copyright violation, and outputs to NEWS/.
---
# News Scout

This skill runs `scripts/fetch_rss.py` to aggregate daily news from configured RSS feeds.

## Required Format
The script generates a Markdown file in the `NEWS/` directory (`NEWS/yyyy-mm-dd.md`).
Each article entry includes:
- Title
- URL
- 2 bullet point summary (summarized or truncated to avoid copyright infringement)
- Tags related to the category

## Feeds Configuration
To add or remove feeds, modify the `FEEDS` dictionary inside `scripts/fetch_rss.py`. The categories are:
- AI research
- Security
- Startup/product
- Hardware
- Developer ecosystem
