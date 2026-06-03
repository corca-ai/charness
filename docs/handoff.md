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
  verified public) — resolved #282 and shipped the #283 mutation-survivor fix.
- **Open release follow-up:** the v0.16.0 real-host checklist (clean
  `charness update`, `tokei` doctor/install) is unrun — flagged by the
  conservative `integrations-and-control-plane` trigger; the shipped code is
  goal-metrics rendering, which does not touch the install runtime.
- Open issues: #289/#288/#287/#286/#285/#284 plus #184. #283 is no longer in
  the live open-issue list.
- **Testability + test-DSL initiative**: completed the
  [testability quality ratchet goal](../charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md):
  boundary-bypass no-increase ratchet is wired into quality, the portable
  `quality` payload/ratchet contract is skillified, and the first clean
  `inventory_*` bypass cluster is converted in-process.

## Next Session

1. Pick **#284** first: add a pre-edit preflight for skill-surface edits
   (headroom, coupling, markdown spans, mirror sync) so the ratchet-goal waste
   does not repeat.
2. Then pick **#286**: make handoff chunker propose agentic work packages, not
   ranked issue lists.
3. Then pick **#285** if #286 exposes live-issue fixture brittleness: stop
   hard-pinning live issue numbers in tests.
4. Keep **#184** for product-success synthesis after the workflow-hardening
   pair above; v0.16.0 real-host smoke also remains pending unless the release
   closeout updates it.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- Long goals should treat cached input as a context-pressure signal, not direct
  waste. The stronger efficiency signals are compactions, repeated
  status/diff/check commands, polling, and broad-gate cadence.
- #261's remaining coordination-cues survivors are policy residue after the
  mechanical hardening path, not another #273 coverage fix.
- For future workflow-improvement goals, one startup `find-skills` pass remains
  mandatory; use read-only/`--summary` recommendation probes at real routing
  boundaries and slice/bundle fresh-eye critique instead of per-commit review.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [testability quality ratchet goal](../charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md)
- [mutation recovery goal](../charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md),
  [mutation recovery carrier](../charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md)
