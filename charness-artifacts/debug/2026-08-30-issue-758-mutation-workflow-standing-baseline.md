# Issue #758 Mutation Workflow Standing-Baseline Debug
Date: 2026-08-30

## Problem

Mutation Tests run `33296181601` checked out the intended provider-main SHA
`ad17d9ef3c4f86a3221a93169096ff37ccdccefc`, but its standing baseline failed
before sample selection completed. Mutation execution was skipped, leaving the
issue's required capability unmeasured.

## Correct Behavior

Given a provider-main tree whose artifacts contain typed content identities,
when the standing corpus referent gate runs, then it checks Git commit citations
without asking Git to resolve non-Git packet/input/finding identities; after a
green baseline the workflow must run mutation and publish its report.

## Observed Facts

- Provider readback names the exact head SHA above and one failing nodeid:
  `tests/quality_gates/test_artifact_referents.py::test_the_repo_corpus_is_clean_and_reports_its_grandfathered_set`.
- The workflow comment is https://github.com/corca-ai/charness/issues/758#issuecomment-5467121353;
  the successful issue-update step appended evidence rather than replacing the
  stable issue body.
- Local focused reproduction on a descendant with byte-identical gate, test,
  and frozen Goal Draft files fails in 11.04s.
- The gate reports seven blocking tokens, all on frozen Goal Draft lines 214,
  228, and 236. Each is labeled `packet identity`, `reviewed-input identity`, or
  `findings identity`; their full values exist as SHA-256 fields in the source
  review packets.
- The deleted `docs/prompt-mutation-policy.md` finding shown at the end of the
  pytest message is grandfathered and non-blocking.

## Reproduction

- `python3 -m pytest -q tests/quality_gates/test_artifact_referents.py::test_the_repo_corpus_is_clean_and_reports_its_grandfathered_set`
  returns one failure.
- `python3 scripts/check_artifact_referents.py --repo-root .` reports status
  `blocked`, with exactly seven unresolvable commit references in the frozen
  Goal Draft.

## Candidate Causes

- The workflow checked out the wrong branch or SHA.
- The seven values are real Git commits absent from this clone.
- The SHA classifier treats typed SHA-256 identity prefixes as Git commits.
- The issue reporter failed to publish the new run because the body stayed old.

## Hypothesis

- Falsifiable claim: preserving only review-content producer labels (`packet`,
  input/finding identities, and `identity_sha256`) removes exactly these seven
  false blockers while a real unresolved commit identity on the same line
  remains a candidate | disconfirmer: focused classifier tests plus a full
  corpus referent run.

## Verification

- Result: confirmed. The checked-out SHA is exact; all seven values fail
  `git cat-file` but are introduced as packet/input/finding identities; the
  provider comment exists. After the classifier repair, all 71 focused referent
  tests pass and the 627-artifact corpus reports `status: clean`, while the mixed
  fixture still submits a real sibling commit token to the resolver.
- Luna fresh-eye round 1 blocked structured producer keys and a hidden
  `commit identity`; round 2 independently returned SHIP after both were repaired,
  rerunning 71 tests and the exact frozen-draft gate.

## Root Cause

`sha_candidates` classified every 7-40-character hex token outside UUIDs as a
Git commit, even when a review-content producer typed it as a packet or
input/finding identity. The referent gate lost the producer's type at its
classifier boundary. Preserving only those review-content labels at that single
owner removes the false verdict without hiding an actual `commit identity`.

## Invariant Proof

- Invariant: when an artifact producer types a value as an identity, the corpus
  gate must preserve that type and must not reinterpret it as a Git commit.
- Producer Proof: the review packet JSON records the full values under
  `identity_sha256`; the frozen draft summarizes their prefixes as identities.
- Final-Consumer Proof: 71 focused tests pass; the full local corpus gate is
  clean with 2,536 real SHA candidates still resolved.
- Interface-Shape Sibling Scan: UUID typed identities are already excluded by
  `UUID_RE`; identity-labeled hex digests are not.
- Non-Claims: mutation behavior remains unmeasured until a new provider run
  completes mutation and report publication.

## Detection Gap

- `tests/quality_gates/test_artifact_referents.py` | covers UUID identities and
  plain bad SHAs, but no labeled content identity beside a real commit token |
  add one mixed-line classifier test and the exact corpus regression.

## Sibling Search

- Mental model: every SHA-shaped token is a Git commit, even when its producer
  supplies a different type.
- same layer: `sha_candidates` UUID masking and structured producer keys |
  decision: same bug, fix now | proof: executable fixture.
- abstraction up: packet/input/finding identity labels in the frozen Goal Draft
  | decision: same bug, fix now | proof: local corpus reproduction.
- cross-file: `charness-artifacts/critique/*packet.json` typed
  `identity_sha256` producers and `scripts/artifact_referents.py` consumer.

## Seam Risk

- Interrupt ID: issue-758-standing-baseline-2026-08-30
- Risk Class: none
- Seam: none
- Disproving Observation: none; the exact failing test reproduces locally.
- What Local Reasoning Cannot Prove: none for the classifier repair; provider
  mutation execution remains an acceptance non-claim, not a debug seam.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/critique/2026-08-30-issue-758-typed-content-digest-referent-review.md

## Prevention

Implemented at the single SHA-classifier owner with a mixed-line regression.
Publish the repair, then rerun the exact provider workflow. Do not edit the
frozen Goal Draft or grandfather the new artifact.
