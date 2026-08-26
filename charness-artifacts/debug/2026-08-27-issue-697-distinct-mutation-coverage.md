# Debug Review
Date: 2026-08-27

## Problem

Issue #697 reports that the mutation sampler and the changed-line coverage
producer write the same report path, so a freshness marker cannot identify
which producer supplied the report. This can let the cheaper sampler satisfy a
changed-line proof contract without producing changed-line coverage.

## Correct Behavior

Each producer has a distinct report identity and freshness marker. The
changed-line producer accepts only its own fresh report, while mutation
sampling remains independently readable. The restored capability is a truthful
changed-line proof that cannot be satisfied by a different producer.

## Observed Facts

- GitHub issue #697 is open, labelled `bug`, and its comments were read.
- The issue body names `tests/quality_gates/test_changed_line_mutation_coverage.py`
  as the required focused target.
- Prior #695 work showed that proof producers and final consumers can drift when
  a shared report shape has no executable owner.
- The sampler and changed-line producer both defaulted to
  `reports/mutation/test-coverage.json`; the marker was only the changed-pool
  content hash and had no producer identity.
- The executable fixture reproduced a clean consumer result from a
  sampler-shaped report carrying a matching legacy marker.

## Reproduction

The smallest fixture writes a sampler-shaped report at the old shared path and
leaves a matching legacy changed-line marker in place, then invokes the real
changed-line consumer with `--reuse-coverage --require-fresh-coverage`. Before
the repair, the fixture passed with exit 0 and no blocking files; after the
repair, the foreign/legacy marker is unestablished and exits 3.

## Candidate Causes

- Both producer paths intentionally or accidentally derive one fixed report
  filename and the consumer checks only age or existence.
- A shared helper serializes coverage without carrying producer identity, so
  the caller cannot distinguish report ownership.
- The focused test exercises report presence but not producer attribution, or
  a stale shared fixture masks the missing distinction.

## Hypothesis

The producer identity was absent from the freshness contract, so a sampler
report could be accepted by the changed-line consumer. `disconfirmer:` a
producer-qualified marker and a distinct sampler path must make the same report
swap unestablished; if a foreign marker still passes, the repair is incomplete.

## Verification

Source inspection and the executable report swap reproduced the collision. The
post-repair focused tests verify that legacy and foreign markers no longer
establish a changed-line verdict.

## Root Cause

The two producers shared a report path, while the changed-line consumer trusted
only a content fingerprint that did not bind the report to its writer. A sampler
overwrite could therefore leave a matching changed-line marker behind and make
the consumer accept the wrong corpus.

## Invariant Proof

- Invariant: changed-line proof consumes a fresh report produced by the
  changed-line producer, not merely any coverage report.
- Producer Proof: `sample_mutation_files`, `run_cosmic_ray_mutation`, and
  `filter_cosmic_ray_mutants` now use `sample-coverage.json`; the changed-line
  producer keeps `test-coverage.json` and stamps its own marker.
- Final-Consumer Proof: the focused fixture rejects legacy and foreign markers;
  the changed-line marker path is parsed only when its schema and producer
  identity match.
- Interface-Shape Sibling Scan: `mutation_sampling_lib` namespaces runtime files
  by report stem, and retention now manages both report paths and the
  changed-line marker.
- Non-Claims: no host, evaluator, release, or installed-consumer behavior is
  claimed from this local investigation.

## Detection Gap

- Focused mutation coverage gate | it previously checked content freshness
  without producer attribution | fixed by a producer-qualified marker, a
  distinct sampler path, and a wrong-producer report fixture that is refused.

## Sibling Search

- Mental model: report freshness is an interface identity, not a filesystem
  existence check.
- same-layer: mutation sampler and changed-line producer | decision: same bug,
  fixed by separate report paths and marker ownership | proof: executable fixture.
- abstraction-up: shared coverage report helper/serializer | decision: inspect
  as the likely ownership seam | proof: static scan only.
- cross-file: `tests/quality_gates/test_changed_line_mutation_coverage.py` |
  decision: inspect the final consumer fixture | proof: static scan only.

## Seam Risk

- Interrupt ID: issue-697-distinct-mutation-coverage-2026-08-27
- Risk Class: contract-freeze-risk
- Seam: coverage producer -> changed-line proof consumer
- Disproving Observation: the consumer already binds and rejects the wrong
  producer marker in the minimal report swap.
- What Local Reasoning Cannot Prove: hosted evaluator behavior or installed
  consumer adoption.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: charness-artifacts/impl/2026-08-27-issue-697-distinct-mutation-coverage.md

## Prevention

Keep report paths and marker ownership producer-specific. Keep the focused
wrong-producer refusal beside the changed-line consumer so a future path
shortcut cannot silently restore the collision.

## Evidence Disposition

- Report Identity: goal-run:724#sha256:a52de5ded2e8eed2a35867e8e6d8b18dca3f2f456ce625b0d83b32abafbd80f7
- Reported Findings: 1
- Dispositioned Findings: DBG-697-F1
- Missing Findings: none
- Evidence Digest: sha256:e1073ac6f0ea00e09ac41d3a06696ecc7a5d4f87c2a000389af03aebeb3cd417
- Report Source: charness-artifacts/goal-runs/724/bodies/backlog-697.md
- Report Source SHA256: a52de5ded2e8eed2a35867e8e6d8b18dca3f2f456ce625b0d83b32abafbd80f7

## Adversarial Verification

- Finding: DBG-697-F1 | source: charness-artifacts/goal-runs/724/bodies/backlog-697.md | expected: the changed-line consumer must not treat a sampler-written coverage report as its authoritative fresh corpus | stimulus: write a sampler-shaped coverage report at reports/mutation/test-coverage.json while leaving a matching legacy changed-line fingerprint marker, then run the reuse consumer | disposition: reproduced | observed: the consumer returned exit 0 and reported no blocking files for the sampler-shaped report because the content-only marker could not identify its writer | proof: executable fixture | handoff: charness-artifacts/impl/2026-08-27-issue-697-distinct-mutation-coverage.md | next move: give the sampler a separate default report path and make the changed-line freshness marker identify the changed-line producer | receipt: charness-artifacts/debug/receipts/issue-697-producer-collision.json | receipt sha256: 63249062805505a453bb7f128d02bafe6d3720eb1b58c12428e94de18943ae9e
