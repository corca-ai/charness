# Debug Review: release claims evidence durability
Date: 2026-09-06

## Problem

The 8.6.0 final release suite refused a new claims report after semantic review:
one test failed and 9398 passed. The report cited an ignored preparation receipt
as independently available proof. Publication did not occur.

## Correct Behavior

Given a reviewed preparation record, when its evidence child is committed,
the observations supporting approval must remain readable on a fresh checkout.
Runtime paths describe reproduction; retained bytes substantiate claims.

## Observed Facts

The [failure receipt](../probe/2026-09-06-v8.6.0-claims-durability-failure.json)
preserves the executed final-consumer refusal. The preparation receipt still
exists and reports 87 passed, zero failed, and deferred release pytest.
Git confirms its source is ignored. The previous
[preflight incident](2026-09-06-review-closeout-preflight.md) concerned the same
runtime-evidence assumption at an issue boundary; its fix deliberately did not
generalize the issue launcher to release reports.

## Reproduction

Final release pytest at claims child a769300dc failed
test_real_repo_passes; the standalone durability gate also printed the same
single current citation refusal. This is not an order-dependent test failure.

## Candidate Causes

- Candidate: the newly written claims narrative cites runtime-only proof.
  The exact ignored path and line are named by the gate and confirmed by Git.

## Hypothesis

Retaining the still-readable preparation receipt inside the already-allowed
claims Markdown carrier, and citing that retained block, will remove this
refusal without changing the prepared commit or weakening the verifier.
disconfirmer: the source is tracked, or the gate refuses a different citation.

## Verification

The disconfirmer did not hold: Git identifies the source as ignored and the
standalone gate identifies this new citation. After repair the direct gate passed
3143 documents and the exact failed test passed in 6.24s. An initial focused
invocation selected zero tests because its default excludes slow-corpus tests;
that exit 5 was not a pass. The corrected invocation included release-only tests.
Classification: subject-defect, not verifier-defect or scope-too-broad.

## Root Cause

The release report copied an observer's runtime-path citation; the evidence
child was committed without the cheap durability gate; semantic review checked
the receipt's contents but not fresh-checkout reachability; preparation gates
predated this newly written report. The final live-corpus test therefore caught
a known rule only after the expensive suite began. The rule and detector already
exist; this slice needs correct evidence placement and gate ordering, not code.

Pattern Ladder: observed failure is the executed report refusal; local pattern
is runtime availability mistaken for persistence; the prior issue-closeout
incident is an executable-fixture interface sibling; broader prevalence remains
unproven. Disconfirmation is the concrete path's Git status, not keyword counts.

## Invariant Proof

- Invariant: claims evidence must survive checkout before release publication.
- Producer Proof: the retained failure receipt binds the offending report and source hash.
- Final-Consumer Proof: release pytest and the direct durability gate refused it.
- Interface-Shape Sibling Scan: release report, frozen prepared record, prior issue carrier.
- Non-Claims: no new production behavior, completed publication, or security clearance.

## Detection Gap

The claims scaffold binds identity and scope, not citation durability.
The existing durability gate would have caught this before final resume.
No new gate or public workflow is being added.

## Sibling Search

- Mental model: readable runtime proof is durable proof.
- cross-file: issue preflight incident and the prepared release record.
- same layer: other citations in this report | decision: same class, diagnostic-only for this slice | proof: direct corpus gate named no other current refusal.
- abstraction up: claims scaffold versus durability gate | decision: intentional plain-text or non-rendering boundary | proof: static scan; separate owners already exist.
- specialization down: the sole ignored receipt citation | decision: same bug, fix now | proof: executable fixture.
- mental-model: prior issue closeout carrier | decision: same class, diagnostic-only for this slice | proof: prior fixture; no further production expansion is authorized.

## Seam Risk

- Interrupt ID: release-8-6-0-claims-durability
- Risk Class: none
- Seam: local Markdown evidence carrier
- Disproving Observation: final consumer rejected non-durable proof
- What Local Reasoning Cannot Prove: future publication or live efficiency
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/release-review/2026-09-06-v8.6.0-prepared-claims-review.md

## Prevention

Use the existing evidence-durability contract: retain source bytes with their
hash, label the original path reproduction-only, then run the direct cheap
gate before the failed test and full resume. Keep the prepared commit fixed;
amend only its unpublished evidence child. Separate reviewer Sartre approved
this bounded causal/repair proposal: retain the complete original bytes, cite
the in-document section, and mark only the source locator reproduction-only.
Parent received the findings; shared-tree fingerprint verification was clean.
The embedded receipt re-hashes to
ea7dee3367fb52491ef0f89d6d17c408b192af3d2203175ceb1490c3f0a36f39,
matching the original. Prepared commit 4fdd64ae9262 and machine-owned claims
identity remain unchanged. New narrative hash
3490edd9bf1fba3d9804ac07653811860ec7e2fda4190c08e95fcd19b5fe51e5
changed the retry key, authorizing the narrow recheck and final resume.
No new recurrence-preventing mechanism was added: the existing rule and gate
already cover this class, so the RCA conversion is explicitly unconverted.

## Evidence Disposition

- Report Identity: gate:release860-durability#sha256:0348b79c0fc4d4caee9c31496ffdd99157dce85ec812b64cdae16e9a70a83f91
- Reported Findings: 1
- Dispositioned Findings: DUR-1
- Missing Findings: none
- Evidence Digest: sha256:6a4476e94ee2fd1aeac533ecd28df1bba41d0a8c7ed6ff15e0fc0d383152dbed
- Report Source: charness-artifacts/probe/2026-09-06-v8.6.0-claims-durability-failure.json
- Report Source SHA256: 0348b79c0fc4d4caee9c31496ffdd99157dce85ec812b64cdae16e9a70a83f91

## Adversarial Verification

- Finding: DUR-1 | source: charness-artifacts/probe/2026-09-06-v8.6.0-claims-durability-failure.json | expected: A claims report must preserve cited preparation evidence in a fresh checkout | stimulus: Run final release pytest against claims child a769300dc without modifying its report | disposition: reproduced | observed: test_real_repo_passes refused the ignored preparation receipt citation; 1 failed and 9398 passed | proof: executable fixture | handoff: charness-artifacts/debug/2026-09-06-release-8-6-0-claims-durability.md | next move: retain preparation receipt inside claims narrative and amend evidence child | receipt: charness-artifacts/probe/2026-09-06-v8.6.0-claims-durability-failure.json | receipt sha256: 0348b79c0fc4d4caee9c31496ffdd99157dce85ec812b64cdae16e9a70a83f91
