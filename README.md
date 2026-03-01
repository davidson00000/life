# Life OS

Welcome to your personal Life Operating System. This repository turns GitHub into an automated daily news ingestion and AI-assisted triage system using Antigravity.

## Structure

- `.agents/rules/`: Global behavioral rules for Antigravity interactions.
- `.agents/workflows/`: Standard operating procedures (`/daily_triage`, `/draft_script`, `/weekly_review`).
- `.agents/skills/`: Executable skills like the `news-scout` RSS fetcher.
- `NEWS/`: Daily aggregated news summaries.
- `IDEAS/`: Your captured and cultivated ideas.
- `PUBLICATIONS/`: Drafted YouTube scripts and X posts.
- `PORTFOLIO/`: Selected outputs and completed works.
- `TASKS/`: High-level tasks and projects.

## How to Run Locally

You can manually fetch today's news by running the `news-scout` Python script:
```bash
python .agents/skills/news-scout/scripts/fetch_rss.py
```
This requires no external dependencies beyond the Python 3 standard library. The generated report will be saved to `NEWS/yyyy-mm-dd.md`.

## How to Trigger Manually (GitHub Actions)

Navigate to the **Actions** tab in this GitHub repository. Select **Daily News Scout** in the left sidebar, and click **Run workflow**.

## How to use `/daily_triage`

Whenever you want to triage your daily news, instruct Antigravity using the workflow command:
```
/daily_triage
```
Antigravity will automatically read the workflow instructions from `.agents/workflows/daily_triage.md`. It will open today's news file, select the 5 most relevant items, analyze why they matter, and either convert them to ideas, decide to read deeper, or ignore them. Finally, it will update your current daily Issue and create new tasks if needed.

## How to Tune Feeds

If you want to track different topics or sites, open `.agents/skills/news-scout/scripts/fetch_rss.py` and modify the `FEEDS` dictionary.

You can add any standard RSS or Atom feed URL under a category:
```python
FEEDS = {
    # ...
    "Your Category": [("Source Name", "https://example.com/feed")],
}
```

## How to Extend Workflows

To create a new workflow:
1. Create a new `.md` file inside `.agents/workflows/`.
2. Provide a YAML frontmatter description:
    ```markdown
    ---
    description: What this workflow does
    ---
    ```
3. List the chronological, numbered bullet points explaining exactly what steps Antigravity should take.
4. You can then trigger it anywhere by prompting Antigravity with `/your_workflow_name`.
