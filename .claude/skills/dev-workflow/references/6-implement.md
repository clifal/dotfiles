# Phase 6 — Implement

## Ask first

One question, before any code:

> 実装は AI が進めるか、ペアプロ(あなたがキーボードを持つ)か？

Do not pick for them.

## AI implements

Hand off:

```
/mattpocock-skills:implement
```

Feed it `3-plan.md` and the ticket list.

## Pair programming

Call the Skill tool for `pair`. The user writes the code; you navigate against the spec and tickets.

## Either way

- Work ticket by ticket, in the order `3-plan.md` set.
- Append one line to the `## Log` in `state.md` as each ticket closes.
- Typecheck and run the affected tests per ticket; run the full suite once at the end.

## Gate

- Every ticket is closed, or listed in `state.md` as dropped with a reason.
- Typecheck and the full test suite pass, and the user has seen the output.

Update `state.md`, then stop.
