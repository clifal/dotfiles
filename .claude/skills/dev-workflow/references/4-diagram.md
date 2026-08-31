# Phase 4 — Diagram the plan

Goal: the user can see where the plan lands in the system before a line is written.

## Steps

1. Read `3-plan.md` and the phase-1 diagrams in `diagrams/`.

2. Call the Skill tool for `archify`, into `diagrams/`:
   - **target architecture** — the system as it stands once every ticket is done, marking what is new and what changes
   - **a sequence diagram per ticket that crosses a seam** — the call path the ticket introduces or alters
   - the data or state flow, when the feature moves data through more than one component

3. Walk the user through each diagram against the ticket list.

## Gate

- The user can point at the diagram and name where each ticket lands.
- Anything the diagram exposed that the plan missed goes back to phase 3 as a ticket or a spec edit.

Update `state.md`, then stop.
