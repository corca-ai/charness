# Issue Draft: Real Repo Git Index Lock Flake In Pre-Push Quality

## Observed Problem

During the v0.17.0 release push, the release helper had already created the
release commit and `v0.17.0` tag, then stopped at `git push origin main v0.17.0`
because the pre-push hook's full `./scripts/run-quality.sh --read-only` run
failed inside pytest.

The failing test was:

```text
tests/quality_gates/test_closeout_headroom_and_mirror_gate.py::test_gate_passes_on_real_repo_in_sync
```

The exact failure was:

```text
`git write-tree` failed in `/home/hwidong/codes/charness`:
fatal: Unable to create '/home/hwidong/codes/charness/.git/index.lock': File exists.
Another git process seems to be running in this repository
```

The same test passed immediately when run outside `git push`:

```text
pytest tests/quality_gates/test_closeout_headroom_and_mirror_gate.py::test_gate_passes_on_real_repo_in_sync -q
1 passed in 2.93s
```

The full `./scripts/run-quality.sh --read-only` also passed outside the push
hook before the branch/tag push was retried.

## Why This Hurts

This turns release/push closeout into a flaky host-state problem after the
expensive release helper has already done local mutation work. The operator
then has to decide whether to rerun, manually continue, or bypass the hook after
separately proving the gate. That is exactly the kind of late closeout waste the
next #284 pre-edit/preflight work is supposed to prevent.

## Current Suspected Cause

`test_gate_passes_on_real_repo_in_sync` runs
`scripts/check_staged_mirror_drift.py --repo-root <real repo>`. That script calls
`git write-tree`, which reads the real repository index. Under `pytest -n auto`
inside the pre-push hook, this means a test process is touching the same real
worktree/index that the enclosing `git push` process and hook are using.

This is likely a test isolation bug, not a stale lock-file cleanup problem.

## Useful Outcome

A useful fix would keep the staged mirror drift gate tested without reading the
live parent repo index from a parallel pytest worker. Likely directions:

- move the real-repo e2e coverage to a temp clone or copied-index fixture;
- or mark the real-index test serial/non-xdist as a narrow containment step;
- and add a regression check that quality/pre-push tests do not call
  `git write-tree` against the shared parent worktree during parallel pytest.

## Linkage

Handle this with #284 or immediately before it. The pre-edit preflight should
treat "real repo git index access from parallel quality tests" as a known
workflow-boundary hazard.
