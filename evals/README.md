# Evals

`evals/` holds repo-owned smoke scenarios for `charness` itself.

These are not broad benchmark suites. They are small, deterministic scenarios
that prove the harness still works as a product:

- public skill package validation still accepts a minimal valid skill
- profile validation still accepts a minimal valid bundle
- markdown link validation still accepts valid internal docs
- adapter bootstrap scripts still work on a clean repo
- handoff-style absolute in-repo links still pass portability checks

Canonical runner:

```bash
python3 scripts/run-evals.py
```

The quality runner should call this script so eval drift becomes part of the
normal repo bar.
