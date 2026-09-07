# Reference resolution and one authoring suite

Pending local change, 2026-09-08. No release, install, push or root AGENTS change.

## Candidate and success

1. Change only `evals/fixtures/consumer-journeys/spec-impl-alias/prompts/impl.md`: say resolve each literal relative reference against the directory of the file containing it; preserve `../` components, for example `../../shared/...` in exported `skills/impl/SKILL.md` reaches package-root `shared/...`. Avoid reconstructing paths from basenames. Keep original acceptance, seed, exported skill bytes and oracle unchanged. Do not treat a one-run result as universal prompt reliability or speed proof. Blanket reading is a separate fixture instruction and remains outside this path repair.
2. Change `docs/development.md` and `docs/operating-contract.md`: authoring final integration uses the unfiltered full read-only lane, whose pytest phase runs the standing runner first and stops on failure. Explicitly export before that lane when generated files changed. Retain focused checks and committed changed-line proof before broad execution. Require the pytest result actually executed and passed; a filtered/skipped run is not the integration verdict. No executable gate, selection, release requirement, cache or receipt-reuse change.

## Verification scope decision

Claims: repair two observed wrong reference paths in one real implementation consumer; remove the redundant invocation from the authoring recipe without removing coverage or failure propagation. Minimum proof: unchanged consumer oracle and original tests/spec, actual reference-read trace, source/export/seed/prompt identities; exact runner command/selection/environment comparison; existing mirror and runner tests plus final unfiltered full read-only receipt. Negative controls: wrong paths absent while correct files exist; full-lane pytest failure remains nonzero and stops later phases; stale mirror still refuses read-only execution.

Omitted: release-only tests and online/advisory opt-ins remain governed by their existing lanes. No timing speedup, global equivalence across different environments, host install, release or public skill improvement claim. The final authoring run executes fresh; no previous result substitutes. A failed consumer test is subject-defect; lost test selection or hidden failure is verifier-defect; public-skill redesign is scope-too-broad.

## Deliberately not doing

No new gate, resolver program, export layout change, broad reference-loading rewrite or pytest caching. AGENTS files stay unchanged.

## Reviewed clarifications

Fixed decisions: preserve the standing marker exclusions (`release_only` and `slow_corpus`), optional gate applicability and omission reporting. Full means the configured full lane without an additional operator filter. Refresh the generated mirror explicitly before read-only; update its existing owning paragraph as well. No global process-environment equivalence is claimed.

Probe questions: can the unchanged consumer complete without the two guessed paths, and does final full verification freshly execute standing pytest and later applicable gates?

Deferred decisions: blanket reference-loading redesign, other fixture prompts, public skill wording, general runtime speedup and cross-run test reuse. These are non-claims, with no implementation commitment.

Success criteria: unchanged alias oracle passes, original test bodies/spec remain intact, exact target reads succeed without guessed-path failures, and a fresh final full-lane receipt records pytest passed and every omission. The existing 69 focused checks passed before implementation. Two distinct file-backed reviews found no architectural blocker and deferred final approval to these observed results; parent accepted marker/export wording corrections and rejected new resolver/cache/prose-pin machinery.

## Critique

- Interrupt Source: consumer-path-and-pytest
- Seam Summary: fixture instruction to executed consumer reads
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: independent causal and consumer reviewers requested the bounded candidate and actual proof; no design blocker remains after marker/export wording corrections
- What Disproving Observation Is Resolved: exported files exist; wrong consumer paths and duplicated recipe are locally reproduced; actual repaired behavior is the explicit implementation probe, not an inferred result
