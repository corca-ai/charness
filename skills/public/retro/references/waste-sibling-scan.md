# Waste Sibling Scan

A per-session lesson typically names one waste pattern (e.g., "commit message
without a closing keyword"). What the lesson usually does NOT carry is a scan
for the OTHER places the same waste shape could recur, with a per-location
decision. Without that scan-before-learning, the next session pays for waste
the current session could have surfaced. This is the same cost `debug` named in
`references/sibling-search.md`: durable artifacts intended to prevent recurrence
should pay the sibling-scan cost so the next session does not inherit the queue.

When the lesson names a *transferable* waste pattern — one that could plausibly
recur in another skill, script, doc, or workflow — add an opt-in
`## Sibling Search` section to the per-session retro artifact. Narrowly local,
single-session waste with no plausible siblings uses the short-circuit instead.

The scan lives in the per-session retro artifact written by
`scripts/persist_retro_artifact.py`. Do NOT add it to
`charness-artifacts/retro/recent-lessons.md` (a generated digest refreshed from
the selection index — hand edits are reverted) or to the selection index JSON.

## Schema

Reuse the four axes and four-decision taxonomy from
`skills/public/debug/references/sibling-search.md`:

```text
## Sibling Search

- same layer: <location> | decision: <decision> | proof: <how-checked>
- abstraction up: <location> | decision: <decision> | proof: <how-checked>
- specialization down: <location> | decision: <decision> | proof: <how-checked>
- mental-model siblings: <location> | decision: <decision> | proof: <how-checked>
```

Decisions: `same waste, fix now` / `diagnostic-only` / `intentional boundary` /
`valid follow-up outside the slice`.

When a bullet's decision is `valid follow-up outside the slice`, the same bullet
(or the next continuation line) must record a follow-up identifier:

- `follow-up: <issue-url>` — filed via the `issue` skill, or
- `follow-up: deferred <handoff-anchor>` — a named handoff/doc anchor

A bare `follow-up: deferred` with no anchor is rejected: it silently re-exports
the follow-up to the next session, which is exactly the waste the rule blocks.

## Empty / Trivial Short-Circuit

If the waste is narrowly local with no plausible siblings, record it explicitly
with a single bullet rather than omitting the section reasoning:

```text
## Sibling Search

- n/a — trivial fix; no plausible siblings
```

## Enforcement

`scripts/validate_retro_artifact.py` enforces the follow-up grammar when a
`## Sibling Search` section is present in a per-session retro artifact. The
section is opt-in: artifacts without it pass unchanged, so historical retros and
narrowly-local sessions are not retroactively gated. The validator shares
`scripts/artifact_validator.py:validate_sibling_followups` with the `debug`
validator so the two skills enforce one grammar, not two.
