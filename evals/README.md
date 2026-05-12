# Evals

`evals/` holds repo-owned smoke scenarios and representative intent checks for
`charness` itself.

These are not broad benchmark suites. They are small, deterministic scenarios
that prove the harness still works as a product:

- public skill package validation still accepts a minimal valid skill
- profile validation still accepts a minimal valid bundle
- markdown link validation still accepts valid internal docs
- adapter bootstrap scripts still work on a clean repo
- handoff-style absolute in-repo links still pass portability checks
- checked-in adapters still resolve to the declared repo contract
- representative discovery workflows still honor local-first packaging rules
- representative public skills still retain their required contract markers
- Cautilus instruction-surface fixtures can declare `requiredConcepts` so
  summary-level behavior checks are structured in the observed packet instead
  of relying on manual `result.json` inspection or brittle prose pins

## Cautilus Fixture Tiers

Current route-only fixtures under `evals/cautilus/*.fixture.json` are legacy
sentinels. They are kept so schema, runner, and concept-assertion contracts stay
deterministically validated, but they are not routine live Cautilus closeout
proof.

New behavior-proving Cautilus fixtures should be log-backed: start from a real
failing prompt, transcript, or operator log, then assert that the same input now
produces the intended behavior. Those fixtures are run on demand for the bug or
regression they protect, not as a standing substitute for the local quality bar.

## Cautilus Required Concepts

Instruction-surface fixtures under `evals/cautilus/*.fixture.json` may add
`requiredConcepts` to a case:

- `id`: stable assertion id for the concept being checked
- `terms`: non-empty list of exact terms that must all appear
- `sourceFields`: optional list of observed fields to scan; supported values
  are `summary` and `routingDecision.reasonSummary`

When `sourceFields` is omitted, the runner scans both `summary` and
`routingDecision.reasonSummary`. The observed packet records
`conceptAssertions[].matchedTerms`, `missingTerms`, and `status`; any failed
concept assertion makes `run-local-eval-test.mjs` exit non-zero after writing
the packet.

Canonical runner:

```bash
python3 scripts/run_evals.py
```

The quality runner should call this script so eval drift becomes part of the
normal repo bar.
