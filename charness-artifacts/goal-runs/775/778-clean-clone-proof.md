# #778 clean-clone proof, 2026-09-03

Clone of the local tree at the #777 closeout (`9e915f281`) with the working-tree hook, regime test, and docs copied in and committed; hooks installed with `scripts/install-git-hooks.sh`; mirror regenerated; a local bare remote baselined with `--no-verify`. Script: `/tmp/proof-778.sh` at proof time (reproduced below in prose).

## Seeded push: one failing `release_only` test, refused

Commit: a `tests/test_seeded_release_only_778.py` whose only test is marked `release_only` and asserts False. `git push proof HEAD:main` returned 1 after 123 s.

```
charness pre-push: running full ./scripts/run-quality.sh --read-only --release (source/test/config path touched: tests/test_seeded_release_only_778.py)
FAIL pytest-release           106.5s
FAILED tests/test_seeded_release_only_778.py::test_seeded_release_only_regression_778
run-quality: release pytest failed; stopping before later release checks.
Quality summary: 0 passed, 1 failed (FAILED: pytest-release [log: /home/hwidong/.cache/tmp/charness-runtime/9f9c6cb49ffff4c7/quality-failure-logs/pytest-release.log]), total 122.3s
error: failed to push some refs to '/tmp/charness-778-proof/remote.git'
```

## Clean push: seed removed plus a code change, passed

Commit: the seed deleted and one comment appended to `scripts/core/repo_layout.py` so the push classifies as code (a seed-plus-unseed range has an empty diff and takes the docs-only subset; recorded as a finding). Mirror regenerated before the push. `git push proof HEAD:main` returned 0 after 257 s.

```
charness pre-push: running full ./scripts/run-quality.sh --read-only --release (source/test/config path touched: scripts/core/repo_layout.py)
PASS pytest-release           100.7s
Quality summary: 85 passed, 0 failed, total 256.8s
```

## Finding recorded for the operator

The first proof attempt caught `tests/quality_gates/test_scaffold_changed_line_coverage.py::test_scaffold_changed_lines_read_covered_through_gate_probe`, a `release_only` test that located the scaffold fallback by the literal `_repo_script` anchor that #777 renamed. The standing lane cannot see `release_only`; the hook with `--release` refused the push. Fixed in the #777 commit before this proof.
