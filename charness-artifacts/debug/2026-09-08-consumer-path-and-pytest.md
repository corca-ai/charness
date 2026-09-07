# Debug Review: consumer paths and duplicate authoring suite
Date: 2026-09-08

## Problem

The implementation consumer attempted two nonexistent reference paths; authoring instructions require standalone pytest before an aggregate that runs the same standing selection.

## Correct Behavior

Given an exported reference, preserve its literal path relative to its containing document. Given integrated Charness source, prepare the mirror and execute current standing tests plus applicable aggregate checks without an additional identical selection.

## Observed Facts

The previous optional-index trace reports `MISSING` for `skills/shared/references/bootstrap-resolution.md` and `skills/spec/design-lenses.md`. Corrected reads succeed and the consumer eventually passes eleven tests. The package has `shared/references/bootstrap-resolution.md` and `skills/spec/references/design-lenses.md`.

The quality manifest selects the canonical standing runner first, alone and fail-fast. Both command plans select the same expanded adapter targets and exclude `release_only` and `slow_corpus`. Environments are not identical: direct mode defaults to `full`, aggregate mode is `read-only`, and interpreter spelling and runtime orchestration differ.

## Reproduction

- PATH-1: test canonical exported targets exist and the two constructed targets do not; all six assertions passed. Original failed commands are retained in the preceding optional-index trace record.
- SUITE-1: print both runner command plans, normalize only Python spelling and unique external basetemp, compare remaining argv: equal. Inspect both owning documentation sentences and selected aggregate phase. Receipt: `charness-artifacts/probe/2026-09-08-reference-and-suite-diagnosis.json`.

## Candidate Causes

- Missing export: disconfirmed by target bytes and successful recovery.
- Manual path reconstruction: reproduced; an extra `skills/` segment and omitted `references/` segment explain the failures.
- Duplicated executable scheduler: disconfirmed; the additional invocation comes from development/operating-contract prose.

## Hypothesis

- Literal containing-document resolution in the fixture prompt will avoid the observed guessed paths. Disconfirmer: a fresh consumer using unchanged package, seed and oracle still guesses paths or fails acceptance.
- Export followed by the full read-only aggregate subsumes the standing selection. Disconfirmer: lost selection, stale mirror acceptance or suppressed pytest failure. Existing negative controls passed in the 69-test focused run.

## Verification

Diagnosis confirmed locally; repair effectiveness remains pending the protocol. No total environment equivalence, timing benefit or public-skill defect is claimed. Independent investigators confirmed target topology and carrier composition. Two file-backed critiques delivered `defer`: execute the bounded candidate and supply actual consumer/final evidence before approval.

## Root Cause

Path chain: broad fixture reference demand → manual array construction → literal links shortened → wrong directory → false absence. The missing affordance is explicit containing-document-relative resolution; fixture pressure is plausible, not experimentally isolated causation.

Suite chain: authoring prose names two carriers → both select one runner → same current test universe runs twice → earlier carrier uniquely refreshes the mirror. The repair should preserve readiness explicitly while making the aggregate the integration authority.

Pattern ladder: observed wrong paths/duplicate invocation (runtime trace and source); local pattern is reconstructed path/carrier identity (local payload proof); interface siblings are nested reference links and the second owning docs page (static scan); pattern of patterns beyond these bounded interfaces is unproven.

## Invariant Proof

- Invariant: reference bytes reached through literal links; fresh standing pytest and aggregate failures remain visible after consolidation.
- Producer Proof: canonical targets and equal normalized expanded argv in the diagnosis receipt.
- Final-Consumer Proof: previous consumer recovered; repaired consumer and final aggregate pending.
- Interface-Shape Sibling Scan: both phase skills share the exported sibling `shared/` tree; two docs own the duplicated recipe.
- Non-Claims: no installed-host, release, cache reuse or global equivalence claim.

## Detection Gap

- Export validators correctly accept existing targets; they cannot prevent invented shell paths. Actual consumer trace exposed the judgment failure; a new package validator is unjustified.
- Existing runner/mirror tests catch selection and failure propagation. They do not judge redundant prose requirements. Independent workflow review and final receipt are the bounded detection surfaces.

## Sibling Search

- Mental model: reconstruct a path or proof obligation from its container name instead of following its existing owner.
- same layer: `create-cli-refresh/seed/AGENTS.md` uses similar reference wording | decision: same class, diagnostic-only for this slice | proof: static scan only; no runtime failure or owner repair established.
- abstraction up: blanket reference reading | decision: same class, diagnostic-only for this slice | proof: trace; bounded observation: intentionally excluded from this path repair to avoid mixing interventions.
- specialization down: shared versus skill-local reference paths | decision: same bug, fix now | proof: local payload proof.
- mental-model siblings: release and changed-line standalone producers | decision: intentional plain-text or non-rendering boundary | proof: static scan; distinct inputs/claims, no reuse authorized.
- cross-file: `docs/development.md` and `docs/operating-contract.md` | decision: same bug, fix now | proof: source and command comparison.

## Seam Risk

- Interrupt ID: consumer-path-and-pytest
- Risk Class: repeated-symptom
- Seam: fixture instruction to executed consumer reads
- Disproving Observation: canonical export exists despite repeated MISSING reports
- What Local Reasoning Cannot Prove: fresh consumer behavior
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-09-08-reference-and-suite.md

## Prevention

Apply the reviewed bounded contract and run its consumer probe. Reviewers requested precise standing-marker exclusions and correction of the generated-surfaces paragraph that currently says manual export is needed only for direct pytest. Parent accepts both. Parent rejects a prose-pinning test and new resolver/cache as over-worry: existing executable negative controls already hold the invariant. Final approval remains pending evidence, not a requirement to seek operator permission for these authorized local edits.

## Evidence Disposition

- Report Identity: local:reference-suite#sha256:7740314fff20bef4324667718e98eb44b90339b9bb0aae4b4bdfaa9d6fc10718
- Reported Findings: 2
- Dispositioned Findings: PATH-1, SUITE-1
- Missing Findings: none
- Evidence Digest: sha256:254e09a714a2a53b21ddf67ac954f656722d8c5eb6d4c2bc00fb7a7274726ca0
- Report Source: charness-artifacts/probe/2026-09-08-reference-and-suite-diagnosis.json
- Report Source SHA256: 7740314fff20bef4324667718e98eb44b90339b9bb0aae4b4bdfaa9d6fc10718

## Adversarial Verification

- Finding: PATH-1 | source: charness-artifacts/probe/2026-09-08-reference-and-suite-diagnosis.json | expected: named exported references exist | stimulus: compare guessed and canonical paths against frozen package | disposition: reproduced | observed: canonical targets exist; guessed targets absent | proof: executable fixture | handoff: charness-artifacts/debug/2026-09-08-consumer-path-and-pytest.md | next move: explicit literal path prompt and fresh consumer | receipt: charness-artifacts/probe/2026-09-08-path-1-receipt.json | receipt sha256: bf84b6e8392ee2ae33c53ad6df4c551e8e1673726783ee733ac161a1527c5ef4
- Finding: SUITE-1 | source: charness-artifacts/probe/2026-09-08-reference-and-suite-diagnosis.json | expected: one fresh standing selection plus aggregate checks | stimulus: compare owning recipe and expanded commands; run existing negative controls | disposition: reproduced | observed: same selection is required twice; 69 focused tests pass | proof: executable fixture | handoff: charness-artifacts/debug/2026-09-08-consumer-path-and-pytest.md | next move: consolidate recipe with explicit exporter | receipt: charness-artifacts/probe/2026-09-08-suite-1-receipt.json | receipt sha256: 0b5603cd31e3db538553eef84a26df59cfeacd9571f745fbbb53368981a71de5
