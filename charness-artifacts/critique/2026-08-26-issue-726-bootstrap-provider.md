# Issue 726 Minimum Bootstrap Provider Critique

Date: 2026-08-26

## Decision Under Review

Ship the minimum issue-provider mechanics needed to bootstrap the existing
`corca-ai/charness#724` Goal Run graph without claiming guarded close, `/goal`
pickup, concurrency, or full `goal-run-*` orchestration.

## Verification Scope Decision

- Claim under test: create/reuse, body update, exact child-graph reads, and real
  sub-issue relationship mutations fail closed across ambiguous provider writes
  and render honest typed verdicts.
- Changed surfaces: canonical and checked-in plugin issue skill code, tracker
  observations, operator contract, tests, and the file-backed review guidance.
- Minimum sufficient proof: focused provider tests; source/plugin sync; exact
  #724 preflight and graph reads; two packet-bound review rounds with clean
  reviewer boundaries; deterministic closeout gates.
- Deliberately omitted checks: no live GitHub mutation, issue closure, push,
  installed-host readback, Cautilus evaluation, or deferred orchestration claim.
- Verifier contract: `skills/shared/scripts/run_reviewer_worker.py`,
  sha256:4569dbe9e65dba710c945c83d3fc1732662c88d68979dc6185a6d16257dc5178.
- Failure classification: subject-defect
- Negative control: command: focused standing pytest command retained in `charness-artifacts/impl/issue-726-bootstrap-provider.md` | expected refusal: changed-body retry cannot invoke create twice and malformed metadata/template/graph inputs cannot return success | observed result: 154 passed | receipt: current closeout transcript.
- Subject identity: sha256:0c2b955d1366b8ccab9883fab8d0cb01434daf5946abed984cac47617eda8cd6
- Verifier identity: sha256:4569dbe9e65dba710c945c83d3fc1732662c88d68979dc6185a6d16257dc5178
- Input identity: sha256:95897ea4bafc964f25222e214f0a32d9a21a98f7c6b3b7fbfc5971b235c0aae4
- Failure identity: stable:issue-726-r2-body-digest-interlock
- Evidence identity: sha256:04e076bfb989930e7211ce77aa708a16a8edd17b7a0c4a644e89d15fa2699c78
- Retry disposition: first-attempt
- Retry key: sha256:43e3384469d3a1bba6dfc35d0d9b7324862dc37c15375c139692e55276be71d1

The subject digest covers every reviewed canonical `issue` script and focused
`test_issue_*` quality-gate file as sorted path, NUL, content, NUL tuples. This
keeps the modular provider implementation inside the subject after the
closeout-driven architecture split.

## Failure Angles

- Recovery and identity: ambiguous create responses must converge by stable
  Work Item identity without issuing a second external create.
- Verdict honesty: empty exact sets, malformed Goal Run metadata, and malformed
  adapter templates must refuse rather than look current or ready.
- Operator reachability: the parser, retained invocations, immutable
  observations, and provider readbacks must describe one executable path.
- Proof-rail integrity: reviewer outputs must be outside the observed Git state,
  producer-bound before launch, packet-bound to every relied-on contract, and
  capability-bound at collection.

## Counterweight Pass

The independent round-1 counterweight retained four provider blockers and two
proof/evidence blockers, while rejecting expansion into guarded close, `/goal`,
concurrency, and complete orchestration. Round 2 disconfirmed the repaired
empty-set, metadata, and template concerns, then found one residual escape:
changing body bytes hid a prior ambiguous create because the digest was part of
the interlock key. The final capped repair makes `(repo, parent, Work Item key)`
the logical identity and retains body hashes only as evidence.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `skills/public/issue/scripts/issue_tracker_observation.py` | action: fix | note: unresolved create state now blocks all later body variants for the same stable Work Item key while exact discovery can still recover.
- F2 | bin: act-before-ship | evidence: strong | ref: `skills/public/issue/scripts/issue_tool.py` | action: fix | note: explicit expectation presence is independent of cardinality, so expected `[]` rejects any actual child.
- F3 | bin: act-before-ship | evidence: strong | ref: `skills/public/issue/scripts/issue_tracker.py` | action: fix | note: malformed, duplicate, or foreign-version Goal Run metadata is parsed before already-current success or mutation.
- F4 | bin: act-before-ship | evidence: strong | ref: `skills/public/issue/scripts/issue_backend.py` | action: fix | note: malformed template types and format grammar become typed preflight errors rather than tracebacks.
- F5 | bin: bundle-anyway | evidence: strong | ref: `skills/shared/references/fresh-eye-subagent-review.md` | action: document | note: the operating contract now names the producer-bound transaction runner and assigns capability non-claim fields to the launch envelope.
- F6 | bin: valid-but-defer | evidence: strong | ref: `charness-artifacts/impl/issue-726-bootstrap-provider.md` | action: defer | note: live mutation receipts belong to the authorized #724 dogfood reconciliation and are not fabricated for this read-only provider closeout.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded review of external-mutation and verdict
  surfaces.
- Requested spawn fields: file-backed `codex_exec` worker, read-only filesystem,
  no external reads/effects, timeout 900 seconds.
- Host exposure state: host-defaulted
- Application state: host ran the configured file-backed worker; no independent
  provider tier-application signal was exposed.
- Delivery state: findings-received
- Worker report: `.charness/critique/issue-726-r2-retry/report.yaml`
- Worker report identity: bcf7f2d6a9ff77136fd9842d23de90ac70dbc4c5c15e10e929838a0dae9a3522
- Worker report approval: approval_eligible: false
- Worker report delivery: findings-received
- Worker report packet identity: 26ca1b0c9fa2ea47b706ca2731c518ddc06ee6e918ae38c119869efff8dfdafd
- Worker report input identity: ee9be6bf30bedf59b7a7b263e58552518f4c7509c5891884a37e7ff034e17b7f
- Worker report parent receipt identity: 01a03c37-b39b-7541-9dc2-95459b1d7479
- Worker report findings identity: 04e076bfb989930e7211ce77aa708a16a8edd17b7a0c4a644e89d15fa2699c78

## Fresh-Eye Satisfaction

accepted-unreviewed-under-round-cap issue-726-r2-create-interlock-repair — the
second bounded review returned one reproduced blocker. Its repair and focused
two-attempt regression are recorded as explicit non-approval under the two-round
cap; no third fresh-eye approval is claimed.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/issue-726-bootstrap-closeout-final-packet.json`
- Packet path: `charness-artifacts/critique/issue-726-bootstrap-closeout-final-packet.json`
- Packet SHA256: 483da914c17bee36f8cd5b46153494b7e8cc862333dca3cb63013f06c1dfdfe7
- Identity SHA256: 95897ea4bafc964f25222e214f0a32d9a21a98f7c6b3b7fbfc5971b235c0aae4

## Boundary Ownership

- Producer: the issue provider adapter plus immutable Goal Run observation
  writer.
- Consumer: the #724 achieve lifecycle, which decides policy from exact issue
  and relationship facts.
- Owning surface: issue owns provider mechanics and evidence; achieve owns
  lifecycle completion, transfer, and orchestration policy.
- Verdict: owned-correctly

## Deliberately Not Doing

- No third bounded review after the explicit two-round verdict-surface cap.
- No live GitHub write or issue close in this provider implementation slice.
- No push, release, tag, PR, installed-machine mutation, or Cautilus evaluation.
