<!-- charness-work-item-key: backlog-668 -->
# Existing Work Item #668 — Standing-pytest timing friction

## JTBD and premise

Stop a machine-dependent pytest wall-time sample from blocking an otherwise
correct local push or release lane. The trigger's requested profiling and
standing-set reduction were completed and did not move the in-gate wall-time
signal: the tail was flat, and a 12% isolated test-CPU reduction bought only
0.6% of in-gate wall time under contention from roughly 95 concurrent checks.

## Owned change and acceptance

Charness owns the local runtime-budget checker and the `run-quality` lane
policy. The checker now has an explicit `--advisory` mode: a measured timing
overrun stays visible as `ADVISORY:` and returns success, while malformed
configuration, profile, and runtime-budget-universe errors still fail. Direct
checker invocation remains blocking by default. Normal `scripts/run-quality.sh`
and its release mode use the advisory timing path; the separate
`check-runtime-budget-universe` structural contract remains blocking.

No budget was relevelled. Scheduler/concurrency redesign is a successor
boundary, not a hidden part of this fix.

## Verification and evidence boundary

Implementation commit: `8241d9922c37e8e63ab407091931a10ff3c839e6`.

Proof used `/tmp/charness-668-proof-20260827` on named branch
`proof/issue-668-runtime-budget-20260827`, created at target
`8241d9922c37e8e63ab407091931a10ff3c839e6` with explicit base
`c1e527abb75a69bd1645c8eac9381ccf0caa68cc`. Preflight and the isolated
worktree doctor passed with no tracked or untracked changes. The exact path
scope was:

- `.agents/quality-adapter.yaml`
- `docs/deferred-decisions.md`
- `scripts/run-quality.sh` and `plugins/charness/scripts/run-quality.sh`
- canonical/plugin runtime-budget checker and quality references
- `tests/quality_gates/test_runtime_budget_gate.py`
- `tests/quality_gates/test_quality_runner.py`

Direct focused pytest returned `86 passed`; the standing wrapper returned
`86 passed` with pytest cache, pycache, and basetemp directed outside the
worktree; the selected `run-quality` gate returned `2 passed`. Source/plugin
parity, `git diff --check`, isolated clean-status, and final cache/pycache
absence passed.

This is a narrow local verdict-policy proof. Changed-line proof was not made a
universal implementation gate. No hosted timing claim is made.

## Explicit non-claims

This does not claim that wall time is a CPU-normalized regression metric, that
the scheduler/concurrency shape of `run-quality.sh` was redesigned, or that
the 4-core profile was re-derived. It does not claim hosted enforcement,
remote CI, consumer-repository adoption, release publication, push, tag,
installed-host behavior, or a clean parent worktree. Forced fresh-eye,
handoff, and micro-slice rituals were omitted by operator direction.
