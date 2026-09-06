# Debug Review: multi-issue closeout cardinality
Date: 2026-09-06

## Problem

One review cannot bind two issue targets through the current scalar label, and
mixed close targets may receive only one classification's proof floor (#810).

## Correct Behavior

Given one review that genuinely covers two exact issue targets, the final issue
consumer can consume both without a format-only repeat. Given a bug and feature
close carrier, the hook and draft validator enforce each target's own floor.

## Observed Facts

Parent replay confirms both investigator reports. Singleton carrier is delegated;
adding target 43 returns `reviewed packet prepared_for does not bind exactly to
corca-ai/charness#43`. A mixed bug/feature message passes with one bug report.
`CLASSIFICATION_FIELDS` has incomparable bug/feature requirements, not a strict
bug superset. Exact-error GitHub search found no external result; local source
and executable fixtures own this diagnosis. Prior tracked-claim/ephemeral-carrier
and preview/live records informed retaining delivery identity and testing composed
transitions, not weakening existing integrity guards.

## Reproduction

`python3 charness-artifacts/probe/2026-09-06-closeout-cardinality/replay.py`
executes unchanged consumers in temporary fixtures and emits the two bound
receipts below. It never closes provider issues or claims a real bundled review.

## Candidate Causes

- Stale/incomplete packet delivery: disconfirmed by unchanged singleton passing.
- Plural grammar rejected upstream: disconfirmed by both targets reaching consumers.
- Plural discovery with scalar context/classification: confirmed by replay and owners.

## Hypothesis

Holding the delivered packet constant, singleton consumption passes but adding
a distinct target fails exact prefix binding. Holding a mixed carrier constant,
the hook ignores target-specific classification and applies a single floor.
Disconfirmer: unchanged singleton and plural/mixed stimuli through final consumers.

## Verification

Confirmed by final-consumer receipts. Existing four focused standing suites remain
green: 63 passed in 3.20s (runner 4.0s), including singleton identity and plural
close grammar. Claim type: attribution; cheapest falsifier was same-packet
singleton versus plural plus mixed targeted classification through the hook.
These are verifier defects, not defective user evidence that should be recopied.

## Root Cause

Five Whys: bundle is refused/misclassified → plural callers reach scalar checks
(`issue_resolution_observer.py:178`, hook:381) → shared checker repeats one prefix
for distinct numbers (`reviewer_worker_carrier_support.py:182`), while hook reads
only global classification (`check_issue_closeout_commit_msg.py:206`) → packet
producer defines only a display label (`prepare_packet.py:94`,
`critique_packet_lib.py:283`) and classifier dispatch has no target map → tests
cover singleton identity and plural syntax separately, not their composition.
Bottom: missing cardinality/ownership contract, bounded to these consumers.

Pattern Ladder: observed refusal/false-green (executable fixtures; disconfirm
with same inputs); local scalar loop/dispatch (static scan; disconfirm by an
alternate branch); interface sibling draft scalar delegation
(`issue_validate_closeout_draft.py:64`, static scan; disconfirm with target dispatch);
pattern of patterns is assuming a singleton proof context composes into a bundle
(two observed locations, not all batch workflows). Structural prevention: composed
exact-membership and per-target-floor checks; repair design awaits causal review.

## Invariant Proof

- Invariant: producer target/classification declarations reach the final issue
  consumer without losing membership or per-target proof requirements.
- Producer Proof: replay emits two target declarations; worker fixture has current
  packet/result/delivery joins, demonstrated by singleton success.
- Final-Consumer Proof: issue observer rejects second target; hook report is
  verified with both numbers under bug and no feature floor.
- Interface-Shape Sibling Scan: shared identity transport, issue observer, bare
  and staged hook classification, draft verifier delegation.
- Non-Claims: real reviewer observations, provider close, publication and mirrors.

## Detection Gap

- `test_issue_worker_carrier.py:255` | valid fixture only asks for 42 | add exact
  two-target success and changed-membership refusals without changing delivery.
- `test_issue_closeout_commit_msg_hook.py:248` | plural grammar tested apart from
  mixed classes | require both classification reports and refuse missing feature fields.
- `test_issue_closeout_draft_validation.py` | scalar parity | send same mixed
  declaration through draft and hook. Semantic misclassification remains reviewer
  judgment; parser equality cannot prove an issue truly is a feature.

## Sibling Search

- Mental model: repeating a singleton check over many targets proves a bundle.
- same layer: bare/staged hook scalar classifiers:171,206 | decision: same bug,
  fix now | proof: executable bare fixture; staged static scan only.
- abstraction up: shared checker contains issue membership policy:182 | decision:
  same bug, fix now | proof: executable fixture. Shared hash/delivery checks stay.
- specialization down: draft:64 passes one classification for all numbers |
  decision: same bug, fix now | proof: static scan only.
- mental-model: body parser already recognizes targeted classification:105 |
  decision: intentional plain-text or non-rendering boundary | proof: static scan;
  it terminates fields, not classification authority.
- cross-file: `reviewer_worker_carrier_support.py`, hook and draft validator.

## Seam Risk

- Interrupt ID: goal805-closeout-cardinality
- Risk Class: none
- Seam: local proof producer and final closeout consumer
- Disproving Observation: local mixed hook passes without feature-specific proof
- What Local Reasoning Cannot Prove: semantic coverage of an actual bundled review
- Generalization Pressure: none

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/closeout-carrier.md

## Prevention

Preserve singleton compatibility and current source/result/delivery refusals.
The living #810 contract owns repair design after one bounded multi-lens causal
review. No external-seam claim or broad batch taxonomy redesign is needed.

## Evidence Disposition

- Report Identity: issue:810#sha256:a453ce8ad7d18e7e6eb1a67034cafbdf53dd15fe109a962e4735dc5b9751673c
- Reported Findings: 2
- Dispositioned Findings: target-cardinality, classification-cardinality
- Missing Findings: none
- Evidence Digest: sha256:4b28049cfd093e844444702cdf798498c6078622a56912ab396b404a5bb721e1
- Report Source: charness-artifacts/probe/2026-09-06-closeout-cardinality/report.json
- Report Source SHA256: a453ce8ad7d18e7e6eb1a67034cafbdf53dd15fe109a962e4735dc5b9751673c

## Adversarial Verification

- Finding: target-cardinality | source: charness-artifacts/probe/2026-09-06-closeout-cardinality/report.json | expected: Distinct targets need representable source-bound membership | stimulus: Consume the same valid worker fixture for singleton 42 then targets 42 and 43 | disposition: reproduced | observed: Singleton delegated; plural carrier-unverified because prepared_for cannot bind target 43 | proof: executable fixture | handoff: charness-artifacts/debug/2026-09-06-multi-issue-closeout-cardinality.md | next move: causal review then spec | receipt: charness-artifacts/probe/2026-09-06-closeout-cardinality/target-cardinality.receipt.json | receipt sha256: 9d0f60092c322ce359895f5756572fd6e671b27d24951267d6fe5bb9da07de7d
- Finding: classification-cardinality | source: charness-artifacts/probe/2026-09-06-closeout-cardinality/report.json | expected: Each close target must receive its declared classification floor | stimulus: Close bug 1 and feature 2 using target declarations but omit feature-only fields | disposition: reproduced | observed: Hook passes with one bug report for both targets and no feature-floor report | proof: executable fixture | handoff: charness-artifacts/debug/2026-09-06-multi-issue-closeout-cardinality.md | next move: causal review then spec | receipt: charness-artifacts/probe/2026-09-06-closeout-cardinality/classification-cardinality.receipt.json | receipt sha256: 0988886cbdcc699b0b7bb1c39602998ae9f9cadbd4c30b1c75a5ad114228d19c
