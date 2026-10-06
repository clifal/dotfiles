// 日本語と半角英数字の間に半角スペースを入れる markdownlint のカスタムルール
// コード、URL、HTML の中は対象外。句読点と括弧の隣には入れない
"use strict";

const JA = "\\p{Script=Hiragana}\\p{Script=Katakana}\\p{Script=Han}ー";
const AN = "A-Za-z0-9";
const boundary = new RegExp(`(?<=[${JA}])(?=[${AN}])|(?<=[${AN}])(?=[${JA}])`, "gu");
const skipTypes = new Set([
  "codeText", "codeFenced", "codeIndented", "htmlFlow", "htmlText",
  "autolink", "literalAutolink", "definition", "resourceDestination",
  "frontmatter", "mathFlow", "mathText",
]);

module.exports = {
  names: ["ja-space"],
  description: "日本語と半角英数字の間に半角スペースを入れる",
  tags: ["spaces"],
  parser: "micromark",
  function: (params, onError) => {
    const walk = (tokens) => {
      for (const token of tokens) {
        if (skipTypes.has(token.type)) continue;
        if (token.type === "data" && token.startLine === token.endLine) {
          for (const match of token.text.matchAll(boundary)) {
            const column = token.startColumn + match.index;
            onError({
              lineNumber: token.startLine,
              range: [column - 1, 2],
              fixInfo: { editColumn: column, insertText: " " },
            });
          }
        }
        walk(token.children);
      }
    };
    walk(params.parsers.micromark.tokens);
  },
};
