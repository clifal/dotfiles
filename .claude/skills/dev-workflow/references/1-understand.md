# Phase 1 — Understand the existing code

Goal: the user can explain the code the feature touches without opening it.

## Steps

1. **Scope it.** Ask which subsystem, package, or paths the feature touches. A narrow scope reads better than a whole-repo sweep; widen only when the answer forces it.

2. Call the Skill tool for `understand-anything:understand` on that scope. It builds the knowledge graph.

3. Write `1-understanding.md`. Prose, not a graph dump:
   - what the area does today, and where it starts (entry points, with `file:line`)
   - how data moves through it
   - the constraints the new feature inherits: schemas, contracts, invariants, deliberate ADR decisions
   - what surprised you
   - open questions

4. Call the Skill tool for `archify`. Produce a current-architecture diagram and one flow diagram of the main path, into `diagrams/`.

5. Hand off:

   ```
   /mattpocock-skills:grill-with-docs
   ```

   Feed it `1-understanding.md`. It grills the understanding and captures the glossary and ADRs as it goes. Fold what it surfaces back into `1-understanding.md`.

## Gate

- The user confirms the write-up and the diagrams match the code as they know it.
- Every question raised is either answered in the doc or listed under open questions with a name against it.

Update `state.md`, then stop.
