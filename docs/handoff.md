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

- A rigorous `quality` pass closed the #283 mutation-regression hot spot in the
  Codex session/token reporter: new direct unit tests
  ([test_codex_session_audit_tokens.py](../tests/quality_gates/test_codex_session_audit_tokens.py))
  plus `main` routing + non-ASCII tests in
  [test_retro_codex_session_audit.py](../tests/quality_gates/test_retro_codex_session_audit.py).
  Verified with targeted local cosmic-ray (tokens survivors 23→12, audit `main`
  6→4; all residual are equivalent/annotation mutants). No production source
  changed. Fresh artifact:
  [quality latest](../charness-artifacts/quality/latest.md) (prior 2026-05-24 review
  archived to `history/`).
- #283 stays OPEN until the next scheduled mutation run on `main` confirms recovery
  above the 80% threshold; the `mutation-tests.yml` auto-issue owns close/reopen.
- Open issues: #283 (awaiting scheduled re-run), #282 (provider-safe goal closeout
  metrics — closeout/retro design slice), #184 (product success metrics — needs
  maintainer product judgment). #261/#273/#277 are closed.

## Next Session

1. After the next scheduled mutation run, confirm #283 cleared; otherwise inspect
   any remaining survived definitions.
2. Pick #184 for product-success synthesis or #282 for the closeout/retro metrics
   design slice.

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
- [mutation recovery goal](../charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md),
  [mutation recovery carrier](../charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md)
- [workflow review efficiency goal](../charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md)
