# Debug Review: quality catalog repo-native default
Date: 2026-09-11

## Problem

A consumer with a valid quality adapter and an adapter-owned gate is told that the catalog gate is missing because `scripts/run-quality.sh` is absent.

## Correct Behavior

Given a valid adapter, when it declares its own quality commands and the repo does not expose Charness's repo-native runner, then the planner omits that catalog default as not applicable and does not require consumer action.

## Observed Facts

The catalog labels `read-only-quality` as conditional on a repo-native command or equivalent standing gate. The applicability helper excludes the absent default, but the lifecycle converts that exclusion into `catalog_gate_unavailable`, adds it to `gaps`, and changes the final status to `action-required` even while routing `npm run check`.

## Reproduction

- A temporary repo containing only a valid `.agents/quality-adapter.yaml` with `gate_commands: [npm run check]` produces `declaration_lifecycle: action-required`, then `GAP catalog_gate_unavailable: read-only-quality: missing repo-native command scripts/run-quality.sh`.

## Candidate Causes

- The adapter failed to override defaults: disconfirmed; the resulting gate packets omit `read-only-quality` and include the adapter command.
- The repo-native runner is mandatory: disconfirmed by `catalog.yaml`'s conditional `run_when` and the maintainer-local-enforcement reference.
- An inapplicable catalog default is classified as an actionable declaration gap: confirmed by `quality_declaration_lifecycle.py`.

## Hypothesis

- Falsifiable claim: if excluded repo-native catalog defaults are reported as inapplicable metadata rather than gaps, a valid adapter with its own gate stays configured and routes only its declared command | disconfirmer: invalid adapters and genuinely unreachable declared surfaces must remain actionable.

## Verification

- Result: confirmed — after repair the same temporary consumer renders `declaration_lifecycle: configured (0 gap(s))`, routes `npm run check`, and reports the omitted default as non-actionable `INFO`. Focused verification passes 108 tests; final full read-only quality passes 83 gates with zero failures.
- Independent review found and the repair retained the v2 `unavailable_catalog_gates` key as an empty compatibility alias; it also required the default renderer to explain inapplicability without a gap.

## Root Cause

The planner conflates catalog applicability with declaration completeness. A gate that does not apply to the adapter-owned consumer is represented using the same actionable gap channel as a broken consumer declaration.

## Invariant Proof

- Invariant: when catalog applicability excludes a repo-native default, the final lifecycle must not turn that exclusion into a consumer repair requirement.
- Producer Proof: applicability helper excludes the absent default while preserving adapter commands.
- Final-Consumer Proof: the actual planner output changes from `action-required (1 gap)` to `configured (0 gap(s))` for the same adapter-owned consumer fixture.
- Interface-Shape Sibling Scan: preset, declared-surface, and declared-path gaps remain actionable because they describe consumer-owned declarations.
- Non-Claims: no named consumer repo, installed-host roundtrip, or release artifact is proven here.

## Detection Gap

- Planner tests | asserted the erroneous `catalog_gate_unavailable` gap as intended behavior | change the fixture to assert inapplicability without `action-required`.

## Sibling Search

- Mental model: every omitted default is a missing requirement, even when applicability says it is outside the consumer contract.
- same layer: preset and declared-surface gaps in `quality_declaration_lifecycle.py` | decision: intentional boundary | proof: static scan only; these originate in consumer declarations.
- abstraction up: catalog conditional gates in `catalog.yaml` | decision: same bug, fix now | proof: local payload proof.
- specialization down: adapter-owned command substitution | decision: same bug, fix now | proof: executable fixture.
- cross-file: `references/maintainer-local-enforcement.md` explicitly says recognition does not require adoption of `run-quality.sh`; decision: same bug, fix now | proof: static contract.

## Seam Risk

- Interrupt ID: quality-catalog-repo-native-default
- Risk Class: none
- Seam: catalog applicability to adapter declaration lifecycle
- Disproving Observation: an invalid adapter or unreachable declared surface becoming non-actionable
- What Local Reasoning Cannot Prove: installed-host wording until exported and exercised
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Excluded catalog defaults are now inapplicable planner metadata, not actionable gaps. The adapter contract names this ownership rule, and focused tests preserve both adapter-owned substitution and real declaration failures.
