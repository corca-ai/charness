# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **[gate-recurrence (#335) + closeout-floor preflight goal](../charness-artifacts/goals/2026-06-08-gate-recurrence-mutation-and-closeout-preflight.md) COMPLETE, awaiting push.**
  Closed two recurring seams. **#335** (Nth changed-line mutation instance):
  root-caused as genuinely-uncovered changed lines (debug artifact); the next run's
  range (`base=858c9eab`) had **85 uncovered v0.28.0 lines** beyond #335's 8
  survivors — covered all; local producer green over `858c9eab..HEAD` + the
  merge-base range (`ok: true`). Recurrence reduced: the changed-line gate's
  **silent skip now surfaces a loud non-blocking obligation** (Slice 3; no new hard
  gate). **Closeout-floor preflight** extended to `goal-coordination` +
  `goal-early-close` (Slice 4). Two fresh-eye critiques (SHIP); RCA conversion logged.
- **Prior unpushed goals (also COMPLETE, awaiting push):** authoring-preflight +
  disposition de-launder (#284→#334 loop; 7-surface preflight + recurrence-lineage
  rung 1d), run_slice_closeout module split, #332 commit-boundary sweep. v0.27.0
  shipped; #322/#328/#329/#330/#331 closed earlier this cycle.
- Open issues (`gh`): **#184** (product metrics); **#335** (mutation regression —
  fixed locally, auto-closes on the next green scheduled run after push).

## Next Session

- **Push the staged closeouts** (maintainer; `achieve` does not push):
  `origin/main..HEAD` carries the #335 gate-recurrence + closeout-floor goal's
  commits (plus prior unpushed work); the pre-push broad gate is the attestation.
  The #335 changed-line coverage is freshly produced + fingerprint-stamped this
  session, so the pre-push changed-line consumer trusts it.
- **#335** auto-closes on the **next green scheduled mutation run** after push (the
  mutation-workflow marker owns it) — do NOT manually close. The local producer is
  green over the next-run range; the CI run is the authoritative verdict.
- **`goal-activation-preflight-surface`** (deferred follow-up): surface the goal
  `Activation:` preamble line in the preflight (needs preamble extraction). See
  [preflight coverage spec](../charness-artifacts/spec/artifact-shape-preflight-coverage.md).
- **#184** (product metrics) — product-level; needs `ideation`/`spec`, not a slice.
- **v0.27.0 human real-host smoke** (release left open; agent cannot do):
  `charness update` on a clean temp-home + the nose checklist in
  [release latest](../charness-artifacts/release/latest.md).

## Discuss

- **No push/tag CI.** The local `--release` gate is the bundle proof. Open: add
  light push/tag CI and/or mirror the changed-line gate into a CI-PR check (spec
  "Deferred Decisions").

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical; Slice 2 delivered, freshness identity, portability follow-up),
  [release v0.25.0 critique](../charness-artifacts/critique/2026-06-07-release-v0-25-0.md)
- [nose-clone interpretation (#322)](../charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
