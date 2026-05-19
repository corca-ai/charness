# Seed Cache + Orphan Teardown Critique

Date: 2026-05-20

## Target

Closeout critique of the two-item handoff slice: content-addressed seed cache
(`tests/seed_cache.py` + fixture refactor) and agent-browser orphan teardown
(`pytest_sessionfinish` hook + `--help` → `--version` fix in
`agent_browser_runtime_guard.py`).

## Fresh-Eye Satisfaction

bounded-subagent

## Packet Consumed

Inline brief — the review covered `tests/seed_cache.py`, the refactored
fixtures in `tests/repo_copy.py` and `tests/charness_cli/support.py`, the
`pytest_sessionfinish` hook in `tests/conftest.py`, the `run_help_check`
change in both copies of `agent_browser_runtime_guard.py`, and the refreshed
[docs/handoff.md](../../docs/handoff.md) plus
[charness-artifacts/quality/latest.md](../quality/latest.md).

## Findings

### Act Before Ship

- None. The reviewer's verdict was "safe to commit."

### Bundle Anyway

- The `--help` → `--version` switch on `run_help_check` matches the handoff
  Discuss hypothesis exactly and removes the orphan source at its root; the
  `pytest_sessionfinish` hook stays as a controller-side defensive backstop.
- Verify spec satisfied: `./scripts/run-quality.sh` ran twice consecutively
  with no manual cleanup, both 64/0, with 0 orphans between runs.

### Over-Worry

- Read-only enforcement on the cached seed directory would catch a future
  contract violation but is unnecessary today because the existing call sites
  (`clone_seeded_charness_repo`, `clone_seeded_managed_home`) all copy out.
- `subprocess.run(check=False, capture_output=True, timeout=30)` plus the
  bare `except (OSError, subprocess.SubprocessError)` is sufficient
  containment for the cleanup hook — it cannot fail the session.

### Valid But Defer

- `filelock` dependency is not declared in `pyproject.toml`; fresh clones
  could see an `ImportError` instead of a managed install hint. Add a
  declared dev/test extra when the next dependency surface change lands.
- Full-content hashing of untracked-not-ignored files inflates source-hash
  compute cost if someone drops a large untracked artifact under the repo
  root; bounded today, worth a TODO.
- The `run_help_check` function name and `"helpcheck"` JSON field are now
  misleading since the call uses `--version`. Cosmetic rename deferred to a
  coordinated downstream-consumer bump.
- LRU eviction for `~/.cache/charness/test-seeds/<hash>/` is carried as a
  passive next gate; the cache is easy to clean manually until growth
  becomes operationally noticeable.

## Applied Decision

Commit the slice as-is. The cosmetic rename, declared `filelock` extra,
read-only seed enforcement, and seed-cache LRU are recorded as passive
follow-ups in the refreshed quality artifact and handoff.
