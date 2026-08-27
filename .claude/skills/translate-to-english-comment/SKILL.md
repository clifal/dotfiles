---
name: translate-to-english-comment
description: Use when the user runs /translate-to-english-comment with Japanese text, or asks to translate Japanese into a concise English programming comment.
---

# translate-to-english-comment

日本語入力を英語翻訳 → 簡潔なプログラミング用コメントに変換。

## 起動

`/translate-to-english-comment <日本語テキスト>`

## 手順

1. 入力の意図特定(処理目的・注意点・TODO・警告等、何を説明する文か)
2. 直訳禁止。英語ネイティブ開発者が実際書く自然な言い回しへ書き換え
3. 敬語・冗長語削除。技術用語・識別子・数値・否定/例外は正確維持
4. コメント記号(`//` `#` `/* */`等)は対象言語が指定された場合のみ付与。未指定時は平文出力(ユーザー側で好きな記号を付けられるよう)
5. 1〜2文以内。簡潔優先。冗長な直訳より意図が伝わる短文を選ぶ

## 例

入力: 「ここでnullチェックしてるのは、APIが稀にnullを返すバグがあるため」
出力: `Null check here — the API occasionally returns null due to a known bug.`

入力: 「この関数は非推奨。将来削除予定」
出力: `Deprecated; scheduled for removal.`

入力: 「リトライは3回まで。それ以上は呼び出し元にエラーを返す」
出力: `Retry up to 3 times; beyond that, return an error to the caller.`

## 注意

- word-for-wordの直訳調禁止 → 不自然な英語になる
- 言語未指定時にコメント記号(`//`等)を勝手に付与しない
- 識別子・数値・技術用語・否定/例外表現の欠落禁止(意味が変わる)
- 元の日本語が長い場合も、コメントとしては要点のみに圧縮(全文翻訳ではない)
