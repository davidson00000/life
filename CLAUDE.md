# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Life OS — a personal AI-augmented life management system ("Antigravity") that uses GitHub as a platform for automated daily news aggregation, AI-powered triage, idea management, and publishing workflows. The owner is a solo knowledge worker tracking AI research and startup news.

`davidson00000/life` は人生のアクションアイテムを GitHub Issues で管理するリポジトリ。
私（Kosuke）が「やること」「気になること」「アイデア」を投げたら、
Claude Code がIssue として整理・登録・管理する。

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
| `dashboard/` | Web ダッシュボード（GitHub Pages） |

## Issue ラベル定義

| ラベル | 対象 |
|-------|------|
| ACS | AI研究・ACSプロジェクト・Claude Code関連 |
| work | 仕事・シェフラー・副業・キャリア |
| life | 家族・生活・手続き・健康 |
| learn | 学習・読書・技術習得 |
| idea | アイデア・事業案・将来の検討事項 |
| someday | 緊急ではないが忘れたくないもの |
| urgent | 今週中に対応が必要なもの |
| waiting | 誰かのアクション待ち |

## Issue 登録のルール

### いつ Issue を作るか
- 複数のステップがある
- 後で参照したい情報・経緯がある
- 一度考える必要がある
- **作らない**: 5分以内に終わる、買い物レベルのもの

### Issue 作成の手順

1. ユーザーの投げかけ内容を理解する
2. 不足情報があれば **1つだけ** 質問する（複数一気に聞かない）
3. 以下のフォーマットで Issue を作成する

### Issue タイトルのルール
- 動詞から始める: 「〇〇を△△する」
- 具体的に: 「手続きをする」❌ → 「NISAの口座開設手続きをする」✅
- 20文字以内を目安

### 必ず聞くべき情報（不足の場合）
- **期限**: いつまでにやるのか
- **ラベル**: 上記のどのカテゴリか（自分で判断できる場合は不要）

### 聞かなくてよい情報
- 詳細な背景（後からコメントで追加できる）
- 完璧なチェックリスト（まず登録することを優先）

## ユーザーからの典型的な依頼パターン

### パターン1: タスクの登録
> 「確定申告の準備しないといけない」
→ ラベル `life`、期限を確認して Issue 作成

### パターン2: アイデアの記録
> 「〇〇みたいなビジネス面白そうだと思った」
→ ラベル `idea` で即 Issue 登録（詳細は後でOK）

### パターン3: ACS 関連のタスク
> 「Phase 7 の〇〇部分、設計しないといけない」
→ ラベル `ACS` で登録。チェックリストを自分で考えて入れてよい

### パターン4: Issue リストの表示
> 「Issueリストを出して」「Issue一覧見せて」「今のタスク見せて」
→ `gh issue list` で open な Issue を取得し、以下のフォーマットのテーブルで表示する:

```
| # | タイトル | ラベル | 期限 | 経過 |
|---|---------|--------|------|------|
| #1 | 〇〇をする | `life` `urgent` | 3/8 | 2日前 |
```

- デフォルトは open のみ。「全部見せて」「closedも」と言われたら `--state all` を使う
- ラベルでフィルターを求められたら `--label` を使う
- 期限は Issue 本文から抽出する。なければ「—」
- 件数が多い場合はラベルごとにグルーピングして表示してもよい

### パターン5: 週次レビュー
> 「今週のIssueを整理して」
→ open な Issue を一覧して、期限切れ・優先度が高いものを報告

### パターン6: Issue のクローズ
> 「確定申告終わった」
→ 該当 Issue を検索してクローズ。完了メモをコメントに残す

## コミュニケーションのルール

- 登録前に内容をサマリーして確認を取る（1行で）
- 「〇〇という内容で Issue を作成しました（#番号）」と報告する
- 迷ったらラベルは `idea` か `someday` にして後で整理
- 長い説明より、まず登録することを優先する

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
