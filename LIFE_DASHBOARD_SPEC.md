# Life Dashboard — 設計仕様書

> `davidson00000/life` リポジトリを中心とした、人生のアクションアイテム管理システム

---

## 概要・ゴール

GitHub Issues を「人生のタスク管理ツール」として使う。  
PC では Web ダッシュボードで可視化・操作し、外出中は iPhone の Claude モバイルアプリからアイデアを拾い、Claude Code が GitHub Issues への登録・管理を担う。

**コアコンセプト：**
- 思い出したことを Claude Code に投げる → 自動的に Issue 登録
- PC では Web ダッシュボードで全体像を把握
- Claude Code が秘書として Issue の整理・提案も行う

---

## システム構成

```
[iPhone / Claude モバイル]
        ↓ アイデア・タスクを口頭でメモ
[Mac / Claude Code]  ←→  [GitHub API]  ←→  [davidson00000/life リポジトリ]
        ↓                                            ↑
[Web ダッシュボード]  ────────────────────────────────
```

---

## フェーズ構成

| フェーズ | 内容 | 優先度 |
|--------|------|--------|
| Phase 1 | GitHub リポジトリ構造の整備 + CLAUDE.md 作成 | 🔴 必須 |
| Phase 2 | Claude Code スキルの整備（Issue 登録・管理） | 🔴 必須 |
| Phase 3 | Web ダッシュボード構築 | 🟡 高 |
| Phase 4 | 自動化・通知（オプション） | 🟢 任意 |

---

## Phase 1: リポジトリ構造の整備

### ディレクトリ構成

```
davidson00000/life/
├── CLAUDE.md              # Claude Code への作業指示書（最重要）
├── README.md              # リポジトリの運用方針
├── dashboard/             # Web ダッシュボード（Phase 3）
│   ├── index.html
│   └── app.jsx
└── .github/
    └── ISSUE_TEMPLATE/
        ├── action-item.md  # 通常のアクションアイテム用
        └── idea.md         # アイデア用
```

### ラベル設計

以下のラベルを GitHub 上に作成する。

| ラベル名 | 色（hex） | 用途 |
|---------|----------|------|
| `ACS` | `#0075ca` | AI エージェント研究・開発関連 |
| `work` | `#0e8a16` | 仕事・キャリア・副業 |
| `life` | `#e4e669` | 家族・生活・手続き |
| `learn` | `#7057ff` | 学習・読書・インプット |
| `idea` | `#e99695` | アイデア・将来検討 |
| `someday` | `#cccccc` | いつかやる・保留 |
| `urgent` | `#d93f0b` | 期限が近い・緊急 |
| `waiting` | `#bfd4f2` | 他者待ち・ブロック中 |

### Issue テンプレート

**`.github/ISSUE_TEMPLATE/action-item.md`**

```markdown
---
name: Action Item
about: やること・タスク
labels: ''
---

## やること
<!-- 何をするか、1行で -->

## 背景・理由
<!-- なぜやるのか（任意） -->

## チェックリスト
- [ ] 
- [ ] 

## 期限
<!-- YYYY-MM-DD または「今週中」など -->

## 参考リンク
<!-- 関連URL・資料（任意） -->
```

---

## Phase 2: CLAUDE.md の設計

Claude Code がこのリポジトリで動作するときの「行動指針」となるファイル。  
以下の内容で `CLAUDE.md` を作成する。

```markdown
# CLAUDE.md — Life Repository 作業指示書

## このリポジトリの目的

`davidson00000/life` は人生のアクションアイテムを GitHub Issues で管理するリポジトリ。
私（Kosuke）が「やること」「気になること」「アイデア」を投げたら、
Claude Code がIssue として整理・登録・管理する。

## ラベル定義

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

## よく使うコマンド

\`\`\`bash
# Issue 一覧を見る
gh issue list

# Issue を作成する
gh issue create --title "〇〇をする" --body "詳細..." --label "life"

# Issue にコメントを追加する
gh issue comment <番号> --body "進捗メモ..."

# Issue をクローズする
gh issue close <番号>

# Issue を検索する
gh issue list --search "キーワード" --state all

# 今週の open Issue を見る
gh issue list --state open --limit 20
\`\`\`

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

### パターン4: 週次レビュー
> 「今週のIssueを整理して」
→ open な Issue を一覧して、期限切れ・優先度が高いものを報告

### パターン5: Issue のクローズ
> 「確定申告終わった」
→ 該当 Issue を検索してクローズ。完了メモをコメントに残す

## コミュニケーションのルール

- 登録前に内容をサマリーして確認を取る（1行で）
- 「〇〇という内容で Issue を作成しました（#番号）」と報告する
- 迷ったらラベルは `idea` か `someday` にして後で整理
- 長い説明より、まず登録することを優先する
```

---

## Phase 3: Web ダッシュボード

### 技術スタック

| 項目 | 選定 | 理由 |
|------|------|------|
| フレームワーク | React (JSX) | シンプルに動く |
| スタイリング | Tailwind CSS（CDN）またはインラインCSS | ビルド不要 |
| ホスティング | なし（ローカルファイルとして `file://` で開く） | ビルド不要・即起動 |
| データ取得 | GitHub REST API v3 | 追加ライブラリ不要 |
| 認証 | Personal Access Token（ローカル保存） | シンプル |

### 画面設計

#### ログイン画面

- GitHub Personal Access Token の入力フィールド
- トークンはブラウザの `localStorage` に保存（セキュリティ上、注意書きを表示）
- 「デモデータで見る」ボタンも用意

#### メイン画面（ダッシュボード）

```
┌─────────────────────────────────────────────────────┐
│  davidson00000/life              [+ New] [↻ Sync]   │
│  OPEN: 12  CLOSED: 34  TOTAL: 46                    │
├─────────────────────────────────────────────────────┤
│  [ALL] [OPEN] [CLOSED] [ACS] [work] [life] [learn]  │
│  [Board] [List]                  🔍 Search...       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌── ACS ──┐  ┌── work ──┐  ┌── life ──┐  ...     │
│  │ Issue   │  │ Issue    │  │ Issue    │           │
│  │ Issue   │  │          │  │ Issue    │           │
│  └─────────┘  └──────────┘  └──────────┘           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### Board ビュー（デフォルト）

- ラベルごとにカラム表示（カンバン形式）
- 各カードに: タイトル / Issue番号 / 経過時間 / コメント数
- Open は通常表示、Closed は半透明
- カードクリックで詳細モーダル

#### List ビュー

- 全 Issue を時系列で一覧
- 各行に: #番号 / タイトル / ラベル / 状態 / 作成日時

#### Issue 詳細モーダル

- タイトル・本文（Markdown レンダリング）
- ラベル表示
- 「Close Issue」ボタン（Open の場合のみ）
- GitHub の Issue ページへのリンク

#### New Issue モーダル

- タイトル入力
- 本文（テキストエリア・Markdown）
- ラベル選択（複数可）
- 「作成する」ボタン → GitHub API で即登録

### GitHub API 呼び出し仕様

```javascript
const REPO = "davidson00000/life";
const API_BASE = "https://api.github.com";
const HEADERS = {
  Authorization: `token ${token}`,
  Accept: "application/vnd.github.v3+json",
};

// Issues 取得（open）
GET /repos/{REPO}/issues?state=open&per_page=100

// Issues 取得（closed）
GET /repos/{REPO}/issues?state=closed&per_page=100

// Issue 作成
POST /repos/{REPO}/issues
Body: { title, body, labels }

// Issue クローズ
PATCH /repos/{REPO}/issues/{number}
Body: { state: "closed" }

// Issue にコメント
POST /repos/{REPO}/issues/{number}/comments
Body: { body }
```

**注意点:**
- Pull Request も `/issues` エンドポイントに含まれるので `pull_request` フィールドがあるものは除外
- API レートリミット: 認証あり 5000 req/h、未認証 60 req/h

### 起動方法（ローカルファイル）

```bash
# ブラウザで直接開く
open dashboard/index.html

# dashboard/index.html に React アプリを single-file で配置
# file:// プロトコルで動作する（サーバー不要）
# localStorage は file:// でも動作する（ブラウザ依存、フォールバック実装済み）
```

---

## Phase 4: 自動化・通知（オプション）

### GitHub Actions による週次レポート

毎週月曜日に open な Issue をまとめて、自分宛に通知する。

```yaml
# .github/workflows/weekly-review.yml
name: Weekly Review
on:
  schedule:
    - cron: '0 9 * * 1'  # 毎週月曜 9:00 JST
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Create weekly review issue
        uses: actions/github-script@v7
        with:
          script: |
            const issues = await github.rest.issues.listForRepo({
              owner: 'davidson00000',
              repo: 'life',
              state: 'open',
              per_page: 100,
            });
            // open Issue の一覧を本文にまとめて Issue 作成
```

---

## 実装の順番（推奨）

```
1. ラベルを GitHub 上に作成（手動 or gh CLI）
   gh label create "ACS" --color "0075ca" --repo davidson00000/life
   gh label create "work" --color "0e8a16" --repo davidson00000/life
   gh label create "life" --color "e4e669" --repo davidson00000/life
   gh label create "learn" --color "7057ff" --repo davidson00000/life
   gh label create "idea" --color "e99695" --repo davidson00000/life
   gh label create "someday" --color "cccccc" --repo davidson00000/life
   gh label create "urgent" --color "d93f0b" --repo davidson00000/life
   gh label create "waiting" --color "bfd4f2" --repo davidson00000/life

2. CLAUDE.md を作成してコミット

3. Issue テンプレートを作成してコミット

4. ダッシュボードを dashboard/index.html に作成（single-file, file:// で動作）

5. ブラウザで open dashboard/index.html して動作確認
```

---

## 参考・関連リソース

- [GitHub REST API — Issues](https://docs.github.com/en/rest/issues)
- [GitHub CLI — gh issue](https://cli.github.com/manual/gh_issue)
- [GitHub Pages 設定](https://docs.github.com/en/pages)
- 参考記事: [githubで人生を管理する (Zenn)](https://zenn.dev/hand_dot/articles/85c9640b7dcc66)
