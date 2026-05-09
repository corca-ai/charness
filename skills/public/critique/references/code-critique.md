# Code Critique

Critique a commit, PR, snippet, or repo-level diff before it merges. The
substrate (multi-angle review with one counterweight pass and four-bin
triage) is shared with other `critique` targets; this reference shapes the
angle distribution and output for *code that is about to land*.

## When This Lens Fires

Pick this reference when the pending change is concrete code under review.
Trigger phrases:

- `code critique`, `PR critique`, `commit critique`, `snippet critique`
- "review this diff", "critique this PR", "before merge"
- pre-merge review where the merge button is the lock-in event
- repo-scope critique when several diffs cluster around one capability and
  the surface is locking together

If no diff exists yet (only a decision shape, a rename plan, a release
artifact, or a spec draft), route to one of the other target references —
`references/premortem-decision.md`, `references/rename-critique.md`,
`references/release-critique.md`, or `references/spec-critique.md`.

## Anchor Angle Distribution

For code under review, anchor weighting is asymmetric:

- **Michael Jackson (problem framing)** — strong default. Is the diff
  solving the named problem, or a more convenient adjacent problem? Hidden
  scope creep often hides here.
- **Gerald Weinberg (diagnostic)** — strong default. Is the bug actually
  where the diff puts the fix, or is this a fix at the symptom layer? Pulls
  back from "looks reasonable" to "is the cause located".
- **Atul Gawande (checklist / operational)** — moderate. What operator step
  changes? Does the diff add a silent failure mode (no error path, no
  rollback, no doctor signal)?
- **Barbara Minto (structure / communication)** — moderate when the PR
  description, commit message, or test names will be read later. Is the
  rationale legible to a future maintainer with no chat context?
- **Jef Raskin (humane interface)** — light unless the diff touches
  user-facing or operator-facing surface (CLI help, error message, doctor
  output, README first-touch).

Default slate for a non-trivial diff: Jackson + Weinberg + Gawande. Swap in
Minto when the change is doc/spec heavy or PR description quality matters.
Swap in Raskin when the change touches a user-facing surface.

## Counterweight Bins

The four bins from `counterweight-triage.md` apply directly. Code-specific
tightening:

- **Act Before Ship** — concerns that require a diff change before merge:
  missing test coverage on an important branch, unhandled error path, fixed
  symptom while the cause stays unfixed, regression in an adjacent contract.
- **Bundle Anyway** — cheap touch-ups already in the diff blast radius: a
  comment that names a non-obvious WHY, a one-line guardrail next to the new
  branch, a missing assertion in the new test, a one-file rename so the
  symbol matches the new shape.
- **Over-Worry** — concerns that demand expanding the diff into adjacent
  refactors, speculative API consumers, or aesthetic style. Counterweight
  pushes hard on "while we're here" creep that dilutes review surface.
- **Valid but Defer** — concerns that are real but belong in a separate
  slice (a deferred refactor, a Probe Question for the next contract, a
  follow-up test once the new branch has dogfood evidence).

## Defect Class Cross-Link

When a concern matches a recurring defect class, cross-link it to
`charness-artifacts/retro/recent-lessons.md` `Repeat Traps` so the next
slice does not relearn the same lesson. The cross-link is the cite path,
not a paste.

## Capability Gap Routing

When a counterweight bin surfaces a missing capability — for example, a
gate that should exist but does not, an integration manifest that the diff
implies but does not declare, an adapter the diff hardcodes around — route
the gap through `find-skills` so the next move resolves to the right
skill, support capability, or integration instead of inventing a new one
inline.

## Output Shape

In addition to the substrate `Output Shape` from `SKILL.md`, code critique
records:

- `Diff Scope` — one or two lines naming what is changing in the diff
- `Defect Class Cross-Link` — when applicable, retro-lessons path that
  matches the surfaced concern
- `Capability Gap` — when applicable, the missing capability and the
  `find-skills` query that should resolve it
- `Pre-Merge Action` — for each `Act Before Ship` concern, the concrete
  diff edit, test add, or rollback path required before merge
