# Standing Pytest Root Lockfile Attribution Debug
Date: 2026-07-13

## Problem

An untracked 52-byte `uv.lock` appeared at the repository root after quality and
standing-pytest diagnostics, suggesting that a read-only proof path might mutate
the caller worktree.

## Correct Behavior

Given a clean repository without `uv.lock`, when read-only quality or canonical
standing pytest runs, then no new root file remains and the command reports its
actual proof result without mutating caller state.

## Observed Facts

- The session-opening status had no `uv.lock`; a later status showed a 52-byte
  file with `version = 1`, `revision = 3`, and `requires-python = ">=3.12"`.
- `python3 scripts/check_supply_chain.py --repo-root .` returned
  `python:manifest-only` and left no lockfile, disconfirming that direct gate.
- Two later canonical standing-pytest executions started without the file,
  passed 4,567 tests, and left no `uv.lock`.
- A full `run-quality.sh --read-only` under file/exec tracing passed and left no
  root lockfile. Its only `uv` execution and `uv.lock` writes were inside pytest
  temporary fixture repositories.

## Reproduction

- Initial symptom: after the first timing run, `git status --short` showed
  `?? uv.lock` and `stat` reported 52 bytes at 2026-07-13 15:13:07+09:00.
- Controlled reruns: `PYTEST_ADDOPTS='--durations=30' python3
  scripts/run_standing_pytest.py --repo-root . --mode read-only` twice; neither
  reproduced the root write. A traced full read-only quality run also did not.

## Candidate Causes

- A standing test or quality phase escaped its pytest temporary root and wrote
  to the caller repository.
- A tool bootstrap (`uv`, `ruff`, or an installed executable) inferred the
  caller `pyproject.toml` and created a lockfile outside the intended fixture.
- A concurrent diagnostic or subagent process created the file, making command
  ordering look causal when it was not.
- The file pre-existed one observation boundary and was attributed to the wrong
  command because status was sampled only before and after a bundle.

## Hypothesis

- Falsifiable claim: canonical standing pytest deterministically creates a root
  `uv.lock`; disconfirmer: delete the generated file, rerun the exact command,
  and trace root `uv.lock` opens/`uv` execs during a clean full quality pass.

## Verification

- disconfirmed — two exact standing-pytest reruns and one traced read-only
  quality run left the root clean. Trace evidence found only isolated pytest
  fixture writes. Attribution remains unproven and does not authorize a fix.

## Root Cause

No root cause was established. The observed file was real, but the candidate
claim that a canonical read-only command created it did not reproduce under a
different observation channel. The honest outcome is a bounded non-claim, not a
speculative guard or code change.

## Invariant Proof

- Invariant: read-only quality and standing pytest leave the caller worktree
  unchanged.
- Producer Proof: no confirmed root-writing producer; strace saw fixture-local
  `uv.lock` creation only.
- Final-Consumer Proof: post-command `git status --short` was clean except for
  this goal's expected artifacts on all controlled reruns.
- Interface-Shape Sibling Scan: direct supply-chain gate, canonical standing
  pytest, and full read-only quality were each checked independently.
- Non-Claims: no claim about the unidentified concurrent process that produced
  the initial file, and no claim that a one-off race cannot recur.

## Detection Gap

- bundle-level attribution | before/after status found drift but could not name
  the writer | if recurrence occurs, wrap the first reproducing command with
  root-scoped file tracing before adding any enforcement.

## Sibling Search

- Mental model: temporal adjacency was treated as command attribution before a
  writer-level observation existed.
- same layer: `check_supply_chain.py` | decision: same class, diagnostic-only
  for this slice | proof: local payload proof, no root write.
- abstraction up: read-only quality bundle | decision: same class,
  diagnostic-only for this slice | proof: traced local run, no root write.
- specialization down: standing pytest with duration reporting | decision: same
  class, diagnostic-only for this slice | proof: two local roundtrips, no write.
- no cross-file sibling: no confirmed writer exists to justify a structural
  sibling claim beyond the inspected command boundaries.

## Seam Risk

- Interrupt ID: standing-pytest-root-lockfile-attribution
- Risk Class: none
- Seam: local command to caller worktree
- Disproving Observation: exact reruns and syscall tracing did not reproduce the
  alleged write.
- What Local Reasoning Cannot Prove: identity of the initial writer.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Do not add a gate or code fix from this single disconfirmed attribution. If the
file recurs, preserve it and capture writer-level evidence around the smallest
reproducing command; the existing git-status boundary already surfaces drift.
