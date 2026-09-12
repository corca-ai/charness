# v8.6.3 consumer release critique

Date: 2026-09-12

## Decision Under Review

Publish v8.6.3 as a patch: repair existing review evidence retention, task
completion, scratch ownership, and release recovery without a new public skill
or incompatible invocation. Retire the unconsumed workflow experiment.
Whole-workflow automation acceptance remains unproven, not shipped as complete.

## Release Scope

v8.6.3 repairs failure handling. The experimental runner/dogfood/test were
uncommitted and are not release deletions relative to v8.6.2.

## Surface-Lock Inventory

- Canonical critique/shared scripts, task runtime, release recovery, quality helpers.
- Generated plugin export and version/install manifests, owned by the sync helper.
- Critique usage, task-run docs, development guidance, and the regression page.
- Repo critique adapter follow-up scope; no new release scheduler adapter.

## Verification Scope Decision

- Claim under test: bounded lifecycle repair retains evidence without premature approval.
- Changed surfaces: hold-out restoration, durable promotion, release claims ancestry and consumers.
- Minimum sufficient proof: injected restoration/integrity failures, retry readback, classified state consumed by authorization, independent bounded reviews.
- Deliberately omitted checks: no third review round; no scheduled mutation rerun; full release quality and public readback belong to publication.
- Verifier contract: existing standing pytest and identity-bound review carrier; test coverage formerly stopped at classification, now reaches authorization.
- Failure classification: subject-defect
- Negative control: command: standing pytest on declared-path and release-edge tests; expected: four failures before repair; observed: four failures and forty passes, then seventy-nine focused passes; receipt: retained reviewer result paths below and checked-in regression tests.
- Subject identity: sha256:438cc4ecbaba7d5af3d3e3c28b8f688d0da01e3ad3e9d6f4bf95b22d57bdb8a6
- Verifier identity: sha256:8fb989b4a49cffebf5445d1992d8405126e5ccb9a56444606826642d14f39586
- Input identity: sha256:222a2616ec01bb4835ef5f70ebfc3f76708acc31858d684cee97a383928241ca
- Failure identity: stable:retained-semantic-refusal-typeerror
- Evidence identity: sha256:cc48be55fae41d5553040359497be96a4e1f0d7d093cd17f1eb9fcc5fa674e46
- Retry disposition: retry-new-identity
- Retry key: sha256:a67f8f13ce68de9df57b8c20995763f554dce4be118cdf09f35812bb6b981300

## Failure Angles

Gawande operational recovery/Minto claims and Weinberg lifecycle integrity ran
independently in parallel. Their original worker directories are
`workers/release-863-bounded-operator-20260912` and
`workers/release-863-bounded-lifecycle-20260912`.
They reassessed the retained earlier operator/lifecycle-final findings rather
than inheriting their verdicts. Both found concrete remaining defects.

## Counterweight Pass

Act Before Ship: all four reproduced failures were repaired. Bundle Anyway:
failure-injection regressions and current historical-record disposition.
Over-Worry: restoring the unconsumed experiment, hypothetical redesign, and
inheriting old security blockers whose current premise was disconfirmed.
Valid but Defer: actual host credential-canary proof and whole-release workflow
acceptance, explicitly not established by unit fixtures or historical timings.

## Structured Findings

- LIFECYCLE-001 | bin: act-before-ship | evidence: strong | ref: skills/public/critique/scripts/run_review_hold_out.py | action: fix | note: restore failure now retains original bytes and mappings; regression passes.
- LIFECYCLE-002 | bin: act-before-ship | evidence: strong | ref: skills/public/critique/scripts/run_review_carrier.py | action: fix | note: approval is the last atomic manifest replacement after readback.
- LIFECYCLE-003 | bin: act-before-ship | evidence: strong | ref: skills/public/critique/scripts/run_review_promotion.py | action: fix | note: derived lifecycle is rewritable on same-attempt retry; immutable inputs remain checked.
- REC-001 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py | action: fix | note: authorization consumes the bounded generated ancestry and permits verified remote R, C, or carrier; unrelated remote refuses.
- SCOPE | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/2026-09-12-release-consumer-acceptance.md | action: defer | note: production workflow acceptance remains unproven.
- EXPERIMENT | bin: over-worry | evidence: strong | ref: docs/release-workflow-dogfood.md | action: document | note: do not restore a runner whose only consumer was dogfood.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: adapter-selected codex_exec, read-only-worker, timeout 900 seconds; provider model application not independently exposed.
- Host exposure state: metadata-hidden
- Application state: observed file-backed execution, no provider-tier application claim.
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/release863-refusal-repair-20260912/worker-report.yaml
- Worker report identity: 45b5692af81721df19f883ebd2ce8e1801e00d479ade14cf9fc2bc164fc6de2f
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: 438cc4ecbaba7d5af3d3e3c28b8f688d0da01e3ad3e9d6f4bf95b22d57bdb8a6
- Worker report input identity: 222a2616ec01bb4835ef5f70ebfc3f76708acc31858d684cee97a383928241ca
- Worker report parent receipt identity: parent-5122fdafbe9581e4fe8cb081f1e368056f74fade03e1174b
- Worker report findings identity: cc48be55fae41d5553040359497be96a4e1f0d7d093cd17f1eb9fcc5fa674e46

## Fresh-Eye Satisfaction

worker-delivered for the bounded lifecycle repairs. Operator follow-up is
retained at `workers/release-863-repair-operator-20260912/result.json`; it
found the remote-R sibling. That final authorization correction is
accepted-unreviewed-under-round-cap: two bounded rounds exhausted, not operator
approval. Thirty-five release edge/state/surface tests passed after correction.
This record does not transform the operator block into a passing report.

### Release-gate failure disposition

Release prepare subsequently refused 553 uncovered changed lines. Five isolated
test-only tasks retained their results: three completed; two timed out and
preserved WIP commits `f41790c13dc4` and `3e7aba0daeefe`. Parent reused those
candidates, corrected test expectations, and verified 198 combined tests. An
instrumented consumer run then passed 6,283 tests and failed the module-eviction
form test; its raw coverage was reused for diagnosis, never as a passing receipt.
The new tests now use the existing module-eviction owner; its focused set passed
59 tests. Four bounded integrity/terminal matrices subsequently passed 87 tests.

One matrix reproduced an actual recovery refusal defect: invalid semantic bytes
passed `reason` both positionally and by keyword, raising TypeError instead of a
typed invalid result. The duplicate detail is now `verification_reason`. Also
removed the unreachable `final_carrier is None` fallback: a missing report or
failed validation already returns before promotion; every remaining path builds
the carrier. Initially dispositioned under the old round cap, these repairs
made the prior current-input binding stale. A distinct bounded review of this
newly reproduced defect consumed four files / 39,182 semantic bytes, reused the
prior lifecycle partial-result as hypotheses, and passed in 29 seconds without
findings. Its counterweight independently confirms all routes skipping carrier
construction refuse before finalization. This is not a third round reopening
the earlier release design or an upgrade of the retained operator block.
Parent owns final integration gates; mocked validator tests are not a live proof.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release863-refusal-repair-20260912-packet.json
- Packet path: charness-artifacts/critique/release863-refusal-repair-20260912-packet.json
- Packet SHA256: 438cc4ecbaba7d5af3d3e3c28b8f688d0da01e3ad3e9d6f4bf95b22d57bdb8a6
- Identity SHA256: 222a2616ec01bb4835ef5f70ebfc3f76708acc31858d684cee97a383928241ca

## Boundary Ownership

- Producer: reviewer worker receipts and Git release commit graph.
- Consumer: durable critique finalizer and release-resume authorization.
- Owning surface: shared review evidence and release skill, with repo adapter configuration.
- Verdict: owned-correctly

## Operator Action Required

Use the release helper for patch prepare, claims review, publication and distinct
public readback. Do not close #764 without scheduled recovery proof. Retained
scratch remains at its recovery paths and is locally excluded from Git; the
retired fixture was moved outside the checkout, not destroyed.

## Upgrade Path

After publication, run `charness update` and `charness version`. No public release
or installed refresh is claimed by this pre-publication critique.
