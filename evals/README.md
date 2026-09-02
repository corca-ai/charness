# Evals

`evals/` holds repo-owned smoke scenarios and representative intent checks for
`charness` itself.

These are not broad benchmark suites. They are small, deterministic scenarios
that prove the harness still works as a product:

- public skill package validation still accepts a minimal valid skill
- profile validation still accepts a minimal valid bundle
- markdown link validation still accepts valid internal docs
- adapter bootstrap scripts still work on a clean repo
- in-repo documentation links still pass portability checks
- checked-in adapters still resolve to the declared repo contract
- representative discovery workflows still honor local-first packaging rules
- representative public skills still retain their required contract markers

## Scenario Guidance

Keep repo-owned scenarios small, deterministic, and tied to a concrete local
contract. A scenario should name its input, expected result, and the command
that owns the verdict. Use a focused scenario for a real regression instead of
creating a broad benchmark or a second evaluator inside Charness.

Canonical runner:

```bash
python3 -m tools.run_evals
```

The quality runner should call this script so eval drift becomes part of the
normal repo bar.
