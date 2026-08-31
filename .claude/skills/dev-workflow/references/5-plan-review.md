# Phase 5 — Review the plan

Goal: zero open issues before implementation starts. The plan is cheap to change now and expensive to change later.

## Steps

1. Hand off:

   ```
   /mattpocock-skills:grill-with-docs
   ```

   Feed it the spec, the tickets, and the phase-4 diagrams. The target is the plan, not the requirements: sequencing, seams, missing tickets, hidden coupling, what breaks in production, what nobody owns.

2. Write `5-plan-review.md`: every point raised, what it resolved to, and what is still open.

3. Every open point takes one of three exits: answered here, folded back into the spec or the tickets, or recorded as an accepted risk with the reason it is acceptable. Loop back to step 1 if the resolutions changed the plan enough to be worth another pass.

## Gate

- `5-plan-review.md` has no unresolved point.
- The user says implementation can start.

Update `state.md`, then stop.
