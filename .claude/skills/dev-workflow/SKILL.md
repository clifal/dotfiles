---
name: dev-workflow
description: Run a feature end to end — understand the code, define requirements, plan, diagram, review, implement, code-review — with a human gate between phases.
disable-model-invocation: true
---

# Dev Workflow

Seven phases, one feature. Each phase ends at a **gate**: the user confirms before the next phase opens. Every phase leaves an artifact a human can read on its own, months later, without this conversation.

## Read one phase at a time

Read exactly one reference file: the phase you are in. Reading ahead pulls later work into view and rushes the phase in front of you.

1. Understand the existing code — `references/1-understand.md`
2. Define the requirements — `references/2-requirements.md`
3. Turn requirements into a plan — `references/3-plan.md`
4. Diagram the plan — `references/4-diagram.md`
5. Review the plan — `references/5-plan-review.md`
6. Implement — `references/6-implement.md`
7. Code review — `references/7-code-review.md`

## Workspace

Agree a feature slug with the user, then create `docs/dev-workflow/<slug>/` and write `state.md`:

```md
# <feature>

Phase: 1 — Understand
Slug: <slug>

## Log
- phase 1 opened
```

Every artifact lands in that directory. Diagrams go in `docs/dev-workflow/<slug>/diagrams/`.

Write artifacts in the language the user is speaking, in prose, for a reader who was not in the room. Compressed chat style stays in chat.

At each gate, append one line to the `## Log` naming what was decided, and set `Phase:` to the next phase.

## Finishing an artifact

An artifact written in Japanese gets a `suiko` pass before its gate: call the Skill tool for `suiko`, `quick` for the short docs and `full` once one runs past roughly 10,000 characters or leaves the team.

Lint with the experimental detectors on:

```sh
suiko lint <file> --genre tech --reading-load --experimental --json
```

`--experimental` turns on the uncalibrated detectors. It raises the finding count, which is fine — you judge each one anyway.

`suiko lint` does not read bullet lines. A doc that is mostly bullets lints as a handful of fragments and comes back with false positives, so read `doc_char_count`, `readability.particle_token_ratio`, and `lexical_diversity.skipped_too_short` before trusting any finding. When the character count sits far below the real doc, strip the markers into a prose copy and lint that; the fixes still land in the original.

Judge each finding rather than clearing it. A term the spec fixed, or a list that is flat because the items are genuinely parallel, stays as it is.

`state.md`, the diagrams, and artifacts written in English skip this pass.

## Resuming

Before starting anything, look for existing `docs/dev-workflow/*/state.md`. If any exist, list them and ask which feature this is. Open the phase its `Phase:` names.

## Handing off to user-invoked skills

`grill-with-docs`, `to-spec`, `to-tickets`, and `implement` are user-invoked: you cannot fire them. When a phase calls for one, print the exact command on its own line, say what to feed it, and stop. Pick the work back up when the user returns.

```
/mattpocock-skills:grill-with-docs
```

From phase 3 on, those skills need `docs/agents/issue-tracker.md`. If it is missing, hand off `/mattpocock-skills:setup-matt-pocock-skills` first.
