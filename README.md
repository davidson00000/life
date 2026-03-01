# Life OS

ようこそ、あなたのパーソナルLife Operating Systemへ。このリポジトリは、GitHubを自動化された日々のニュース収集と、Antigravity（AI）によるトリアージシステムへと変えます。

## ディレクトリ構成

- `.agents/rules/`: Antigravityが動作するためのグローバルな行動ルール。
- `.agents/workflows/`: 標準作業手順書 (`/daily_triage`, `/draft_script`, `/weekly_review` など)。
- `.agents/skills/`: RSSを取得する `news-scout` のような実行可能なスキル。
- `NEWS/`: 日々集約されるニュースの要約。
- `IDEAS/`: 捉え、育てるためのアイデア群。
- `PUBLICATIONS/`: ドラフト済みのYouTubeスクリプトやX（Twitter）の投稿。
- `PORTFOLIO/`: 完成した作品や選ばれたアウトプット。
- `TASKS/`: 高レベルのタスクやプロジェクト。

## ローカルでの実行方法

手動で今日のニュースを取得する場合は、Antigravityに以下のコマンドを指示してください:
```
/news_fetch
```
（または裏側で直接 `python .agents/skills/news-scout/scripts/fetch_rss.py` を実行することも可能です。）

このスクリプトはPython 3の標準ライブラリのみを使用しており、外部依存関係はありません。生成されたレポートは `NEWS/yyyy-mm-dd.md` に保存されます。

## 手動でのトリガー方法 (GitHub Actions)

このGitHubリポジトリの **Actions** タブを開きます。左側のサイドバーで **Daily News Scout** を選択し、**Run workflow** をクリックしてください。

## `/daily_triage` の使い方

日々のニュースをトリアージしたい場合は、いつでも以下のワークフローコマンドでAntigravityに指示を出せます:
```
/daily_triage
```
Antigravityは自動的に `.agents/workflows/daily_triage.md` の指示を読み込みます。本日のニュースファイルを開き、最も関連性の高い5件を選択し、なぜそれが重要なのかを分析します。そして、それをアイデアに変換するか、より深く読むことを決定するか、あるいは無視するかを判断します。最後に、現在アクティブな日次Issue（Daily Issue）を更新し、必要であれば新しいタスクを作成します。

## フィードの調整方法

追跡するトピックやサイトを変更したい場合は、`.agents/skills/news-scout/scripts/fetch_rss.py` を開き、`FEEDS` 辞書を編集してください。

カテゴリの下に標準的なRSSやAtomフィードのURLを追加できます:
```python
FEEDS = {
    # ...
    "Your Category": [("Source Name", "https://example.com/feed")],
}
```

## ワークフローの拡張方法

新しいワークフローを作成するには:
1. `.agents/workflows/` 内に新しい `.md` ファイルを作成します。
2. YAMLフロントマターで説明を記述します:
    ```markdown
    ---
    description: このワークフローが何をするか（What this workflow does）
    ---
    ```
3. Antigravityが取るべき具体的な手順を、時系列に沿った番号付きの箇条書きで記述します。
4. これで、どこからでも `/your_workflow_name` （ファイル名ベース）とAntigravityにプロンプトを送ることで、そのワークフローをトリガーできるようになります。
