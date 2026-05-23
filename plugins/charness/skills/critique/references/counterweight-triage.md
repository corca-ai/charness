# Counterweight Triage

Critique should not end as a flat list of fears.

After the angle pass, run one counterweight review that pushes back on
speculation, YAGNI, and maintenance cost amnesia.

In the canonical critique path, the counterweight reviewer is a separate
subagent spawned by the parent. That reviewer should triage directly and record
`Fresh-Eye Satisfaction: parent-delegated`; it should not spawn a further
reviewer unless the parent explicitly requested recursive delegation.

Use four bins:

- `Act Before Ship`
  The concern changes the change, acceptance, or release requirement now.
- `Bundle Anyway`
  The concern is real and cheap to fix while touching the surface already.
- `Over-Worry`
  The concern is hypothetical, aesthetic, or unsupported relative to the
  standing maintenance cost.
- `Valid but Defer`
  The concern is real, but deferring it is the honest tradeoff for this slice.

When a concern's evidence basis is easy to overstate, tag it before triage:

- `strong`: current source, a failing or passing gate, measured behavior, or a
  durable artifact directly supports the concern
- `moderate`: repeated local observations or adjacent repo evidence support it,
  but no standing gate owns it yet
- `weak`: the concern is expert judgment, plausible practice, or analogy and
  needs a small experiment before it can drive expensive work
- `contested`: available evidence points in different directions and the next
  move should reduce uncertainty before broad implementation

Counterweight prompts should push especially hard on:

- speculative consumers with no reported user
- "free oracle" arguments that quietly require maintaining two paths forever
- aesthetic claims disguised as contract needs
- "reversal is expensive" when version control or a thinner wrapper would make
  reversal cheap
- authority-only concerns that sound senior but cannot name the repo evidence
  they depend on

The purpose is not bravado.
The purpose is to stop a good critique from turning into an unowned paranoia
backlog.

## Structured Findings Emission

When the caller orchestrator needs to act on findings without re-classifying
each one — for example, a parent skill running three sequential critique
passes per slice — append a machine-readable `## Structured Findings` section
to the critique artifact alongside the prose. The schema reuses the existing
four bins and four evidence tags so this is a serialization, not a parallel
taxonomy.

Each finding is one bullet with `|`-separated `key: value` fields, matching
the convention used by `debug/references/sibling-search.md`. The bin values
are the same four labels above; the evidence values are the same four
strength tags; the action values name the smallest next move:

```markdown
## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/impl/SKILL.md:139 | action: fix | note: closeout omits Lint Gate field
- F2 | bin: valid-but-defer | evidence: moderate | ref: docs/conventions/operating-contract.md#critique | action: file-issue | note: bin/action coupling for impl handoffs is real but slice-scoped
- F3 | bin: over-worry | evidence: weak | ref: n/a | action: document | note: speculative future schema churn
```

Field grammar:

- `id`: caller-stable label (`F1`, `F2`, …); the orchestrator uses this when
  re-citing findings across phases.
- `bin`: one of `act-before-ship`, `bundle-anyway`, `over-worry`,
  `valid-but-defer` — the same four bins from the counterweight pass above.
- `evidence`: one of `strong`, `moderate`, `weak`, `contested` — the same
  four tags from the evidence basis list above.
- `ref`: free-form pointer to the supporting source — `file:line`, doc
  anchor, runtime trace name, or `n/a`. The looser shape is intentional;
  critique commonly cites cross-file invariants and runtime behavior that
  do not collapse to one line number.
- `action`: one of `fix` (apply in current slice), `file-issue` (open a
  follow-up via the `issue` skill), `document` (record in a
  `Deliberately Not Doing` section or commit body), `defer` (leave to the
  named next slice with no separate filing).
- `follow-up`: optional issue URL or `deferred <handoff-anchor>` — required
  when `action: file-issue` so the deferred work cannot disappear into the
  artifact. Same field grammar as
  `debug/references/sibling-search.md` `follow-up:`; the validator rejects
  bare `deferred` tokens with no anchor.
- `note`: one-line description; the prose `Findings` and
  `Counterweight Triage` sections still own the longer narrative.

The section is opt-in. Critique runs that produce only prose stay
back-compatible. When the section is present, `scripts/validate_critique_artifacts.py`
fails on unknown enum values, missing required fields, or duplicate ids so
the caller can rely on the schema instead of re-parsing prose.

Do not treat the bullet schema as a substitute for the counterweight pass.
The bins still come from the counterweight reviewer's judgment; structured
emission is the persistence layer, not the analysis.
