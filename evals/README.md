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

`contract-effectiveness.fixture.json` is the first log-backed tier member: its
cases derive from retro-documented operating-contract violations (the
counterweight-miss and proof-base records under `charness-artifacts/retro/` and
the self-substitution closeout lineage) and assert that the instruction surface
now produces the contract behavior. It is deterministically schema-validated by
`validate-cautilus-scenarios`; live execution stays behind the
`plan_cautilus_proof.py` planner consult and the `run_cautilus_eval.py`
justification-log wrapper, on demand.

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

## Per-Skill Claim-Fidelity Specs

`evals/cautilus/<skill>-claim-fidelity/spec.json` extends the quality
claim-fidelity harness to every public skill: each spec asks whether a real
`/charness:<skill>` run honors its own reference routing. The registry
[`cautilus/claim-fidelity-registry.json`](cautilus/claim-fidelity-registry.json)
lists all of them, and `scripts/validate_claim_fidelity_specs.py` (gate
`validate-claim-fidelity-specs`) keeps them honest:

- `declaredReferences` must be the skill's own `references/*.md` basenames.
- every declared reference carries a `referenceEngagement` entry on the
  `engage-always` / `on-demand` / `gate-sufficient` axis with a rationale;
  `on-demand` records a `trigger`, `gate-sufficient` names a `gate`.
- `requiredCommandFragments` (the docs a run must open to follow its own
  routing) must be `engage-always` declared references.

The axis and authoring rules are the locked methodology contract:
[`skill-claim-fidelity-doc-philosophy`](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md).
These specs are authored assets; the live capture plus cautilus observation
scoring stay eval-only and ask-before-run per
[`cautilus-on-demand`](../skills/public/quality/references/cautilus-on-demand.md).
`thresholds` (runtime budget) are added per skill only after a first baseline
capture, like the quality pilot.
