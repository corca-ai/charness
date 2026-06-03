# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` → **invoke `charness:handoff`**. A bare
  `/handoff` fires chunked routing (#249); the chunker unions the **live
  open-issue backlog** with the list below, so `## Next Session` is a
  curation/sequencing memo, not the full queue. Then read
  [quality latest](../charness-artifacts/quality/latest.md) +
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- Released **v0.16.0** ([release](../charness-artifacts/release/latest.md),
  verified public) — resolved **#282** (provider-safe goal closeout metrics, now
  CLOSED): deterministic `Host metric window:` recorder, standardized
  provider-safe measured-vs-proxy renderer
  (`probe_host_logs.py --format markdown`), a broad-gate attestation hook, and a
  non-blocking `metric_window` closeout signal. Critiques:
  [resolution](../charness-artifacts/critique/2026-06-03-issue-282-provider-safe-closeout-metrics-critique.md),
  [release](../charness-artifacts/critique/2026-06-03-release-v0.16.0-critique.md).
- The #283 mutation-survivor fix (`9fb08f6f`) shipped in v0.16.0. #283 stays OPEN
  until the next scheduled `mutation-tests.yml` run on `main` confirms recovery
  above 80%; that auto-issue owns close/reopen.
- **Open release follow-up:** the v0.16.0 real-host checklist (clean
  `charness update`, `tokei` doctor/install) is unrun — flagged by the
  conservative `integrations-and-control-plane` trigger; the shipped code is
  goal-metrics rendering, which does not touch the install runtime.
- Open issues: #283 (awaiting scheduled re-run), #184 (product success — needs
  maintainer judgment). #282/#261/#273/#277 are closed.
- **Testability + test-DSL initiative** (new, 2026-06-03): shipped a
  lazy/composable test DSL ([`tests/dsl.py`](../tests/dsl.py), commit `1e857cf0`)
  and a boundary-bypass advisory probe (134-candidate baseline). The probe is a
  **sensor with no teeth yet** — the no-increase ratchet is the named next
  obligation. Full intent/done/remaining + honest non-claims:
  [testability-dsl-initiative](./testability-dsl-initiative.md).

## Next Session

1. After the next scheduled mutation run, confirm #283 cleared; otherwise inspect
   any remaining survived definitions.
2. Pick #184 for product-success synthesis. (Also pending, not issue-linked: the
   v0.16.0 real-host smoke noted under Current State.)
3. Testability initiative — next obligation is the boundary-bypass **ratchet**
   (committed baseline + `no_increase` + exemptions + `run-quality` wiring),
   then convert the import-safe `inventory_*` cluster subprocess→in-process. See
   [testability-dsl-initiative](./testability-dsl-initiative.md).

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- Long goals should treat cached input as a context-pressure signal, not direct
  waste. The stronger efficiency signals are compactions, repeated
  status/diff/check commands, polling, and broad-gate cadence.
- #261's remaining coordination-cues survivors are policy residue after the
  mechanical hardening path, not another #273 coverage fix.
- If a future bare handoff pickup offers setup checks, completed goals, or
  cadence constraints as choices, inspect the parser filter before blaming the
  handoff prose.
- For future workflow-improvement goals, one startup `find-skills` pass remains
  mandatory; use read-only/`--summary` recommendation probes at real routing
  boundaries and slice/bundle fresh-eye critique instead of per-commit review.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [testability + test-DSL initiative](./testability-dsl-initiative.md)
- [mutation recovery goal](../charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md),
  [mutation recovery carrier](../charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md)
- [workflow review efficiency goal](../charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md)
