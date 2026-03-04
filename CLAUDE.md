# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Life OS — a personal AI-augmented life management system ("Antigravity") that uses GitHub as a platform for automated daily news aggregation, AI-powered triage, idea management, and publishing workflows. The owner is a solo knowledge worker tracking AI research and startup news.

## Key Rules

- **Default language is Japanese.** All non-code output (descriptions, summaries, task content) must be in Japanese unless otherwise specified.
- **Always produce artifacts.** Every action should leave a trace: Issues, Markdown files, or commits. No throwaway text generation.
- **Strict directory structure.** Follow the predefined layout — do not create ad-hoc directories.
- **Minimal automation.** Prefer simplicity. Do not over-engineer solutions or configs.
- **Idempotency.** All automated behavior must be safe to re-run and produce the same result.

## Directory Structure

| Directory | Purpose |
|---|---|
| `.agents/rules/` | Global behavioral rules for the AI agent |
| `.agents/workflows/` | Standard operating procedures (triggered via `/workflow_name`) |
| `.agents/skills/` | Executable capabilities (e.g., `news-scout`) |
| `NEWS/` | Daily auto-generated news summaries (`YYYY-MM-DD.md`) |
| `IDEAS/` | Captured ideas |
| `PUBLICATIONS/` | Drafted YouTube scripts and X posts |
| `PORTFOLIO/` | Finished works |
| `TASKS/` | High-level projects and tasks |

## Commands

### Fetch today's news
```bash
python .agents/skills/news-scout/scripts/fetch_rss.py
```

### Run auto-triage (requires GEMINI_API_KEY in .env)
```bash
python .agents/skills/news-scout/scripts/auto_triage.py
```

### Run full daily job locally (fetch + triage + git push)
```bash
bash .agents/skills/news-scout/scripts/daily_job.sh
```

### GitHub Actions
Manual trigger via Actions tab → "Daily News Scout" → "Run workflow".

## Architecture

### News Scout Pipeline
1. **fetch_rss.py** — Fetches from ~25 RSS/Atom feeds across two categories (AI Research, Startup/Product). Uses a keyword-based scoring engine (title match = +3, summary match = +1; AI keywords at 1.5x weight, startup keywords at 1.0x). Deduplicates by URL. Outputs top 10 to `NEWS/YYYY-MM-DD.md`. Zero external Python dependencies (stdlib only).
2. **auto_triage.py** — Optional LLM-based triage via Google Gemini API. Reads today's news file, selects top 5, categorizes actions (深く読む / アイデアに変換 / 無視する), and appends a triage section to the news file.
3. **daily_job.sh** — macOS cron wrapper that runs fetch → triage → git commit/push.

### Workflow System
Workflows live in `.agents/workflows/*.md` with YAML frontmatter. They are triggered by name (e.g., `/save`, `/daily_triage`, `/draft_script`). To add a new workflow, create a `.md` file with numbered steps.

### Feed Configuration
Edit the `FEEDS` dict in `fetch_rss.py` to add/remove RSS sources. Keywords for scoring are in `AI_KEYWORDS` and `STARTUP_KEYWORDS` lists in the same file.

## Commit Conventions

Uses Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `style:`. Automated daily updates use `chore: auto-update daily news & triage list for YYYY-MM-DD`.
