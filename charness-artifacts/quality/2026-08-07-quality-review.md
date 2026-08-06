# Quality Review
Date: 2026-08-07
Title: awiki dependency and declaration-to-verdict quality boundary

## Scope

Target boundary: the `quality` skill's external `awiki` dependency, its Charness documentation-graph run, and the #518 declaration-to-final-verdict seam.

Ambient repo findings: #514/#515 implementation, issue closeout, remote CI, release publication, and consumer product behavior remain outside this initial quality packet.

## Surface Contract Review

- semantic coverage: `partial` — the local awiki binary and Charness docs graph are observed; install lifecycle, final quality-artifact routing, plugin parity, and remediation behavior remain unexamined.
- surface: quality dependency readiness and documentation graph verdict
- owner: the quality integration manifest and final quality artifact own the dependency/readout; awiki owns graph analysis.
- projections: `integrations/tools/awiki.json`, quality runner output, parsed awiki counts, quality artifact, and synchronized plugin manifest
- state scope: per-run local host and checked-in documentation graph
- transitions: missing binary, detected binary, healthy invocation, non-clean graph, and repaired graph
- proof boundary: `awiki --version` plus `awiki lint -root docs -recursive` in the Charness checkout
- unexamined axes: install/update lifecycle, quality-skill dispatch, root/plugin parity, consumer repository graph, and remediation of the current graph findings

## Current Gates

- `awiki 0.5.0` is present at `/home/hwidong/.cargo/bin/awiki`.
- `awiki lint -root docs -recursive` executed against Charness and returned exit 1.
- Existing `check-doc-links`, `markdownlint`, `check-links-internal`, and `nose` document-duplicate review remain present; their observed contracts are not identical to awiki graph connectivity.

## Runtime Signals

- runtime source: direct command output captured in this review turn and summarized here; awiki timing capture is missing because no standing awiki timing stream exists yet. <!-- reproduction-source -->
- runtime hot spots: no timing measurement was requested; the awiki command completed locally and returned its graph verdict.
- coverage gate: no full `run-quality.sh` claim; this is a focused dependency/quality inventory.
- evaluator depth: deterministic-gates-only; Cautilus was not run because it remains ask-before-run and is outside this goal.

## Healthy

- The dependency binary is discoverable and responds with version `0.5.0`.
- The repository command reaches awiki's final graph consumer and exposes a non-clean result instead of silently skipping.

## Weak

- The dependency has no checked-in Charness integration manifest or quality-runner route yet.
- The current command is not a clean graph: `documents=40`, `orphans=7`, `islands=0`, `link_only_lines=230`, `largest_component_ratio=0.8250`, `orphan_rate=0.1750`, `content_coverage=1.0000`.
- The result is not yet bound to a typed final quality-artifact disposition, so a green aggregate could still hide it until #518's fold is repaired.

## Missing

- `integrations/tools/awiki.json`, dependency installation/discovery wiring, doctor/readiness state, update/degradation policy, and plugin projection.
- A quality-skill command path that preserves version, exact args, exit code, parsed counts, and non-clean status.
- A command-level overlap matrix proving whether any existing linter is fully subsumed; no deletion is justified by the current evidence.

## Deferred

- Do not delete `check-doc-links`, `markdownlint`, `check-links-internal`, or `nose` until their semantic boundaries are compared against awiki and a replacement proof exists.
- Do not promote the current awiki graph failure to a repaired-quality claim; remediation belongs to the #518 implementation slice after the declaration/applicability/final-consumer contract is fixed.

## Advisory

- structural review result: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --target-skill quality`; the target capability is explicit dependency-to-final-verdict reconciliation, with awiki as a graph reader and the quality artifact as final consumer.
- prose review result: `awiki lint -root docs -recursive` found seven orphan pages and 230 link-only lines; this is a concrete docs-graph remediation queue, not proof that Markdown syntax or source-path references are broken.
- sibling evidence: `cmanki` delegates `docs:lint` to awiki while allowing a missing binary to exit 0; `craken-agents` documents awiki as a manual graph check outside its standing quality gate. Both are comparison evidence for #518's declaration/reconciliation gap, not proof of Charness behavior.

## Delegated Review

- Delegated Review: not_applicable — this is the initial focused inventory; the goal's bounded fresh-eye design review and later repaired-verdict second round remain required before implementation claims.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not re-delegated because no standing runner, threshold, or proof logic was changed in this inventory.

## Commands Run

- `command -v awiki` — `/home/hwidong/.cargo/bin/awiki`.
- `awiki --version` — `0.5.0`.
- `awiki lint -root docs -recursive` — exit 1; graph counts recorded above.
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --target-skill quality` — planner returned required quality primers and a structural review packet.
- Read-only sibling inspection of `/home/hwidong/codes/cmanki` and `/home/hwidong/codes/craken-agents`; no sibling files were changed.

## Recommended Next Quality Moves

- active — capability_needed=quality dependency-to-verdict reconciliation; next_center=the awiki integration manifest and final artifact consumer; transformation=add manifest/install/doctor/degradation metadata, synchronized plugin projection, exact command routing, and typed non-clean folding; proof_boundary=integration validator plus Charness awiki execution and parsed artifact readback; enforcement_posture=existing-gate-reuse.
- active — capability_needed=semantic linter ownership; next_center=the four existing Charness doc/link/duplicate surfaces; transformation=produce a command-level overlap matrix and delete only a fully subsumed detector with replacement proof; proof_boundary=side-by-side findings and reader-boundary tests; enforcement_posture=advisory.
- passive — capability_needed=docs graph repair; next_center=the seven orphan pages and 230 link-only lines; transformation=repair or explicitly classify each finding after the #518 final-consumer contract exists; proof_boundary=a fresh awiki run with the same scope and a distinct review; enforcement_posture=no-gate because remediation is not yet designed.

## History

- [Prior runtime evidence quality review](./history/2026-08-06-runtime-evidence-and-nose.md)
