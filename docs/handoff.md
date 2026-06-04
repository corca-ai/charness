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

- Released **v0.17.0** ([release](../charness-artifacts/release/latest.md),
  verified public) — shipped the testability quality ratchet and reusable
  `quality`/`find-skills` routing surface.
- **Open release follow-up:** the v0.17.0 real-host checklist (clean
  `charness update`, `tokei` doctor/install) is unrun — flagged by the
  conservative `integrations-and-control-plane` trigger; the shipped code is
  quality/routing/handoff work, which does not touch the install runtime.
- Open issues before pushing this closeout: #293, #285-#289, and #184. Local
  closeout now stages direct-commit close keywords for #285, #286, #287, #288,
  and #289; those five remain OPEN until the closeout commit is pushed and
  verified.
- Completed workflow-hardening chunk: #291, #292, and #284 were closed by
  direct carrier `e93e5fa6` after verified local/pre-push broad quality and
  `issue_tool.py verify-closeout --expect-state CLOSED`.
- **Testability + test-DSL initiative**: completed the
  [testability quality ratchet goal](../charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md):
  boundary-bypass no-increase ratchet is wired into quality, the portable
  `quality` payload/ratchet contract is skillified, and the first clean
  `inventory_*` bypass cluster is converted in-process.

## Next Session

1. If this branch has not been pushed yet, push the future-work-efficiency
   closeout commit and run post-push issue verification:
   `python3 skills/public/issue/scripts/issue_tool.py verify-closeout --repo-root . --repo corca-ai/charness --number 285 --number 286 --number 287 --number 288 --number 289 --classification feature --carrier direct-commit --commit-ref HEAD --expect-state CLOSED`.
2. Then pick **#293**: mutation test regression on main. Treat it as a quality
   regression first; run the `quality`/debug path before changing mutation or
   testability policy.
3. Keep **#184** for product-success synthesis after #293; v0.16.0 real-host
   smoke also remains pending unless a release closeout updates it.

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
