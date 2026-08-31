---
name: create-commit-message
description: Use when the user runs /create-commit-message, or asks to turn a Japanese description of changes into an English Conventional Commits message. Triggers on requests to write, generate, or fix up a commit message from staged changes or a Japanese summary. Outputs the English message and its Japanese translation as two separate blocks.
---

# create-commit-message

日本語の変更内容を英語に翻訳し、Conventional Commits形式のコミットメッセージを生成する。あわせて同じ内容の日本語訳を別ブロックで出す。

## 入力

引数として渡された日本語の変更内容。引数がない場合は `git diff` / `git status` の差分から判断する。

## 手順

1. 入力(日本語)と、参照できる場合は `git diff` / `git status` の実際の差分を読み、変更内容の意図を理解する。
2. prefix を次の5つから1つ選ぶ。他の prefix は使わない。
   - `feat`: 新機能の追加
   - `fix`: バグ修正
   - `update`: 既存の実装・ドキュメント・設定の更新
   - `refactor`: 挙動を変えないコードの整理・改善
   - `chore`: ビルド・依存・CI など機能に影響しない雑務
3. summary は命令形(imperative mood)の英語にする。
   - 例: 「ログイン機能を追加した」→ "add login functionality"
4. 英語のコミットメッセージを次の形式で出力する。

```
<prefix>: <summary>

- <detail 1>
- <detail 2>
- <detail 3>
```

5. 続けて、同じ内容の日本語訳を別のコードブロックで出力する。prefix は次の対応で訳し、全角コロン「：」で区切る。

   | prefix | 日本語 |
   | --- | --- |
   | `feat` | 機能 |
   | `fix` | 修正 |
   | `update` | 更新 |
   | `refactor` | リファクタリング |
   | `chore` | 雑務 |

```
<prefix の日本語>：<summary の日本語>

- <detail 1 の日本語>
- <detail 2 の日本語>
- <detail 3 の日本語>
```

## 制約

- **scope は付けない。** `fix: summary` の形にする(`fix(auth): summary` は不可)。
- summary は50文字以内。短く簡潔に。
- details は**最大3つ**。1つも不要なら summary のみで出力する。重要度の高い順に並べ、3つに収まらない変更は上位3件へ集約する。
- 各 detail は1行。命令形の英語で短く書く。
- summary と details の間に空行を1行入れる(git が本文として扱うため)。
- 出力は英語ブロックと日本語ブロックの2つのみ。前置き・説明・確認や、ブロックを指すラベルは付けない。
- 入力が曖昧でも、最も妥当な prefix を選んで断定的に出力する。

### 日本語訳

- 英語ブロックと同じ行構成にする。details の数も揃える。
- 命令形をそのまま移さず、「〜を追加」「〜を作成」のような体言止めにする。
- 製品名・サービス名・識別子(ArgoCD / WordPress / ALB / Route53 など)は訳さずそのまま残す。
- 英語側に無い情報を足さない。訳しにくい語も省略せず、意味の等しい日本語に置き換える。
