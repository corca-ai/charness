# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.43.0 shipped and public release is verified.** `main`/`origin/main`
  are at `263a767b Record release verification for v0.43.0`; tag `v0.43.0`
  is published, the maintainer install auto-refreshed to 0.43.0, and the
  real-host proof arms are closed on this host (see
  [release latest](../charness-artifacts/release/latest.md)).
- **v0.43.0 content** (2026-06-12 overnight autonomous goal,
  [goal artifact](../charness-artifacts/goals/2026-06-12-autonomous-structural-quality-bundle.md)):
  clone advisories consumed as structural signals plus the quality-signal
  scorecard and shared meaningful-slice cadence references (issues #356/#357,
  both verified CLOSED), two new authoring-repo gates
  (`check-bootstrap-shim-consistency` with `--fix`, advisory
  `check-public-doc-coupling`) with the exported-reusable-guidance provenance
  class, the log-backed contract-effectiveness cautilus fixture
  (deterministically validated; no live run by design), and the
  operator-approved retirement of the second-machine release-proof arm.
- **Open issues (`gh`, 2026-06-12): #184 only** — an operator
  product-metrics ideation decision, not an implementation slice.
- Restart note: active sessions carry pre-0.43.0 plugin cache paths; restart
  Claude/Codex sessions to load the refreshed install.

## Next Session

- No queued implementation work. The bundle closed early with a candidate
  ledger; the live deferrals are D28/D29 in
  [deferred decisions](./deferred-decisions.md) (D29: scorecard helper +
  metric-only closeout guard; reopens on consumer-repo discovery failure or
  operator request).
- Live execution of the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  needs an explicit log-backed request naming a
  failing-prompt/transcript/operator-log path, then the
  [cautilus eval wrapper](../scripts/run_cautilus_eval.py).
- **Keep #184 separate.** Schedule it only if the operator wants a product
  metrics ideation session.

## Discuss

- After #354's fix shipped, decide whether an operator announcement is still
  useful for the v0.40.0 scheduled-mutation-lane change and the v0.41.0
  YouTube/issue retrieval improvements — and now whether the v0.43.0
  scorecard/cadence contracts deserve one consumer-facing announcement.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [v0.43.0 release record](../charness-artifacts/release/latest.md)
- [overnight bundle critique](../charness-artifacts/critique/2026-06-12-autonomous-structural-quality-bundle.md)
