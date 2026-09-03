# Phase 2 — Define the requirements

Goal: a decision record a human can act on, with a reason behind every choice.

## Steps

1. Hand off the interview:

   ```
   /mattpocock-skills:grill-with-docs
   ```

   This is the sparring session. Feed it `1-understanding.md` and whatever the user has said about the feature so far. Let it run to its end before writing anything down.

2. Write `2-requirements.md` from what the grilling settled:
   - **やること / やらないこと** — the scope, and the non-goals that were explicitly ruled out
   - **決定事項** — one entry per decision: what was decided, the alternatives that were on the table, why this one won
   - **前提と制約** — what has to hold for the decision to stand, and what the existing code forces
   - **未決事項** — open questions, each with an owner and what unblocks it

   A decision without a reason is not recorded yet. Go back and ask.

3. Call the Skill tool for `sanitize-artifacts` on `2-requirements.md`, so it reads as a standalone document rather than a transcript of this conversation.

4. Then give it the suiko pass — see **Finishing an artifact** in `SKILL.md`. This doc is mostly bullets, so flatten a prose copy before linting.

## Gate

- Every entry under 決定事項 carries its reason.
- Nothing under 未決事項 blocks the plan; anything that does goes back to step 1.
- The user confirms the doc says what they meant.

Update `state.md`, then stop.
