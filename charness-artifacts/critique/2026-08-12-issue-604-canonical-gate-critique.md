# #604 Canonical Gate Recognition Critique

Date: 2026-08-12

## Execution

Two bounded, read-only fresh-eye rounds reviewed this proof-surface change.
Round 1 repaired command-mention overmatching; round 2 repaired dotted filename
suffix overmatching. The second repair is accepted-unreviewed under the two-round cap.

## Fresh-Eye Satisfaction

parent-delegated — both reviewer results were received; their repairs were applied
before the slice proof, with the round-2 cap recorded explicitly.

## Reviewer Tier Evidence

- Requested tier: n/a — host inherited the session model.
- Requested spawn fields: bounded read-only scope, exact default-regex policy, and consumer non-requirement checks through the host agent interface.
- Host exposure state: metadata-hidden
- Application state: the host returned no reviewer-tier application metadata.
- Delivery state: findings-received

## Boundary Ownership

- Producer: quality's default canonical-gate tuple determines CI/local parity anchoring.
- Consumer: a consumer-repository operator reading a parity inventory verdict.
- Owning surface: `skills/public/quality` and its generated plugin projection.
- Verdict: owned-correctly

## Decision Under Review

Recognize only actual Charness `run-quality.sh` command invocations by default;
do not make that runner a requirement for consumer repositories.

## Findings and Counterweight Triage

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/ci_local_gate_parity_lib.py | action: fix | note: round 1 found direct-path matching anchored echo, test, assignment, and comment mentions; command-position patterns plus end-to-end unmatched controls repaired it.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/ci_local_gate_parity_lib.py | action: fix | note: round 2 found `run-quality.sh.bak` matched at a word boundary; the exact-token delimiter and `.bak`/`.shx` controls repaired it, accepted-unreviewed under the cap.
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/references/maintainer-local-enforcement.md | action: document | note: release notes must announce that existing direct runner forms may now yield parity findings; no release is authorized in this slice.

## Deliberately Not Doing

- Do not require every repository to ship `run-quality.sh`.
- Do not broaden recognition to arbitrary shell grammars or consumer-specific gate names.
- Do not publish a release, run hosted consumer CI, or close #604.

## Next Move

Commit the locally proven floor change and its release-note obligation, then move
to #581 without treating a local green as consumer-hosted proof.
