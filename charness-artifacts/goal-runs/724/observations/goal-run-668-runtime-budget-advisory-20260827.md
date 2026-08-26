# Goal Run observation — #668 runtime-budget timing advisory

Date: 2026-08-27 Asia/Seoul

## Scope receipt

- Parent: `corca-ai/charness#724`
- Child: `#668`, `backlog-668`
- Base SHA: `c1e527abb75a69bd1645c8eac9381ccf0caa68cc`
- Target SHA: `8241d9922c37e8e63ab407091931a10ff3c839e6`
- Path scope: runtime-budget checker, local/release `run-quality` routing,
  adapter/reference contract text, and the two focused quality test files
- Proof worktree: `/tmp/charness-668-proof-20260827`
- Proof branch: `proof/issue-668-runtime-budget-20260827`

## Decision and implementation

The trigger's requested profiling and standing-set reduction did not move the
in-gate wall-time signal. The standing set was contention-bound by the local
runner's roughly 95 concurrent checks, so another budget relevel would preserve
the false blocker rather than improve correctness.

Commit `8241d9922c37e8e63ab407091931a10ff3c839e6` adds explicit `--advisory`
support to the canonical and plugin runtime-budget checkers and routes normal
and release `run-quality` timing checks through it. Timing overruns remain
visible as `ADVISORY:` and do not block those lanes. Direct checker invocation,
malformed configuration/profile errors, and the separate runtime-budget-universe
contract remain blocking.

## Verification

- Clean isolated worktree preflight and `worktree doctor --require-isolation`:
  passed before proof.
- Direct focused suite for `test_runtime_budget_gate.py` and
  `test_quality_runner.py`: `86 passed`.
- Standing focused suite with `PYTEST_ADDOPTS` cache directory,
  `PYTHONPYCACHEPREFIX`, and basetemp outside the worktree: `86 passed`.
- Selected combined `run-quality` labels
  (`check-runtime-budget-universe`, `check-runtime-budget`): `2 passed`.
- Canonical/plugin parity, `git diff --check`, final clean status, and final
  absence of worktree `.pytest_cache`, `__pycache__`, and `.coverage`: passed.

The proof used the explicit base/target and path scope above; it did not
aggregate the dirty parent diff. The parent worktree remains intentionally
dirty and was not reset, restored, stashed, or broadly cleaned.

## Goal Run provider evidence

The #724 Goal Run provider updated #668 and returned `status: verified-write`
with `body_verified: true`. The operation receipts are:

- `charness-artifacts/goal-runs/724/observations/backlog-668-runtime-budget-advisory-20260827-1.started.json`
  (`ad39f0835ba4df01b6c2ac6c4666b9aee0703f3e4039ac87f2b024075e9981c3`)
- `charness-artifacts/goal-runs/724/observations/backlog-668-runtime-budget-advisory-20260827-1.terminal.json`
  (`ddbe7636b54f5f1ee3decd303bc97c15dbe55c764f48ae4fabdc5c5ae4d5c9f0`)

An independent issue read returned `comments_read: true`, `body_verified` by
the provider, and `state: OPEN` before the closeout operation.

The manual closeout draft passed with classification `decision-needed` and
manual-fallback reason `operator-directed-manual-close`. The close comment was
posted at
`https://github.com/corca-ai/charness/issues/668#issuecomment-5430269085`.
The independent `verify-closeout --expect-state CLOSED` readback returned
`ok: true`, `status: verified`, `state: CLOSED`, empty missing-field,
state-mismatch, and manual-comment gaps, and recorded the advisory that this
classification skips behavioral-verdict and resolution-critique floors.

## Boundary and non-claims

This is a local Charness quality-policy decision. It does not claim a
CPU-normalized metric, a re-derived 4-core profile, scheduler/concurrency
redesign, hosted or remote-CI enforcement, consumer-repository adoption,
release publication, push, tag, installed-host behavior, or a clean parent.
Forced fresh-eye, handoff, and micro-slice steps were omitted by operator
direction.
