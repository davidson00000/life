---
description: GitHub IssueをテーブルUIで一覧表示する
---
# /issues

1. `gh issue list --repo davidson00000/life --state open --limit 50 --json number,title,labels,createdAt,state,body` を実行してIssueを取得する。
2. 各Issueの `body` から期限情報を抽出する（「期限」「deadline」「YYYY-MM-DD」等のパターンを探す）。見つからなければ「—」とする。
3. 以下のMarkdownテーブル形式でユーザーに表示する:

```
| # | タイトル | ラベル | 期限 | 経過 |
|---|---------|--------|------|------|
| #1 | 〇〇をする | `life` `urgent` | 3/8 | 2日前 |
```

4. テーブルの下に、サマリー行を追加する:
   - open 件数
   - `urgent` ラベル付きの件数（あれば強調）
   - 期限切れの件数（あれば警告）

5. オプション:
   - ユーザーが「全部」「closedも」と言った場合は `--state all` で取得し、closed は取り消し線または (closed) マークを付ける
   - ユーザーがラベルを指定した場合は `--label <ラベル名>` でフィルターする
