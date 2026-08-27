---
name: rewrite-document
description: Use when the user runs /rewrite-document with a document file, or asks to rewrite a design/spec/README as the final version with no trace of how it was arrived at. Triggers on requests to make a doc read as if planned from the start for a reader unfamiliar with the conversation history.
---

# rewrite-document

会話の残骸(改訂履歴・「代わりにこうする」「前述の通り」等)が溜まったdocを、
最初から計画された最終形として全面リライトする。読者=会話経緯を知らない新規参加者。

## 起動

`/rewrite-document @doc_file` — 対象ファイルを引数で受け取る。

## 手順

1. 対象ファイル全文読了。
2. 各セクション最終決定版を特定 → 却下案・修正履歴・会話的つなぎ言葉除外。
3. 全文書き直し。単一著者が最初からこの設計で書いたテイに統一。禁止:
   - 過去参照(「前述の通り」「〜から〜に変更」「当初は〜だったが」)
   - 変更履歴・decision log セクション(ADR等、目的上必須な場合除く)
   - ドキュメント自体へのメタ言及(「本節は旧版を置換」等)
4. 全文 会話文脈なしで単独理解可能に。「前述の通り」等削るだけで文が壊れるなら文自体を書き直す。
5. 技術内容・決定事項・制約は完全維持 — 表現のリライトであり内容編集ではない。要件の黙殺・新規決定の捏造禁止。
6. 対象ファイルへ上書き。

## チェック

- [ ] 会話履歴・旧版・「〜に決定」等の参照ゼロ
- [ ] チャット文脈依存の宙ぶらりん指示語ゼロ
- [ ] 一発設計の体裁
- [ ] 技術内容 欠落なし

## よくある事故

- 「前述の通り」等の句だけ削除→前後文法破綻・文脈依存のまま放置
- 目的なきChangelog/Historyセクション習慣的温存
- リライトのつもりが要約化→具体性欠落
