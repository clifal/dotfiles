# Phase 7 — Code review

## Steps

1. Pin the fixed point: the merge-base with the branch this work came off (`git merge-base HEAD <base>`). Confirm it with the user.

2. Call the Skill tool for `mattpocock-skills:code-review`. It reviews two axes in parallel: does the code follow this repo's standards, and does it do what the spec asked.

3. Write `7-code-review.md`: each finding, its axis, and what it resolved to — fixed, deferred to a ticket, or dismissed with a reason.

4. Fix what you agreed to fix, then re-run the review until both axes come back clean.

5. Give `7-code-review.md` the suiko pass — see **Finishing an artifact** in `SKILL.md`.

## Gate

- Both axes clean, or every remaining finding is written down as a ticket or a stated accepted risk.
- The user confirms.

Close out: set `Phase: done` in `state.md` and give the user the artifact list in `docs/dev-workflow/<slug>/`.
