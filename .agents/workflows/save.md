---
description: 変更箇所を自動判定してGitにコミット＆GitHubへPushする
---
# /save

1. ワークスペース内の変更点（`git status` や `git diff` など）を確認する。
2. 変更内容全体を要約し、Conventional Commitsに沿った簡潔なコミットメッセージ（例: `feat: 〇〇機能の追加`, `chore: 設定ファイルの更新` など）を自動生成する。
3. 以下のコマンドを順に実行する。
   ```bash
   git add .
   git commit -m "生成したコミットメッセージ"
   git push origin HEAD
   ```
4. Pushが完了したら、生成したコミットメッセージとPush完了の旨をユーザーに報告する。
