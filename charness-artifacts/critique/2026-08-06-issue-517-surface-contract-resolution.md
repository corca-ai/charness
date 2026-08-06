# Issue #517 Surface Contract Resolution Critique
Date: 2026-08-06

## Decision Under Review

Add a required, portable `Surface Contract Review` packet to quality artifacts so a routed gate receipt cannot be mistaken for semantic coverage. Reject contradictory duplicate packets and prove the enforcement path against legacy artifacts.

## Execution

The issue was selected by the issue planner as the newest open bug. The public cmanki debug review was gathered into `charness-artifacts/gather/2026-08-06-cmanki-debug-review-517.md` before it shaped the implementation. The change was implemented, source/plugin surfaces were synchronized, and the current artifact was migrated before the final verification pass.

## Packet Consumed

- Packet consumed: `charness-artifacts/critique/2026-08-06-150947-packet.json`

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-06-150947-packet.json`
- Packet SHA256: `a37380b6068d12ed4da3f84d8a5c243a2b74212bd0c36f374fc63ade4e9835aa`
- Identity SHA256: `21ef0cd95d8e613ceeb4d060b53082532d597bd0e7da236efc684ba5b5d9d317`

## Target

Issue #517: `quality 점검이 표면 계약의 의미 손실을 검출하지 못하는 문제`.

## Change

The quality artifact now requires explicit semantic coverage, surface owner, projections, state scope, transitions, proof boundary, and unexamined axes. `partial` and `not-in-scope` dispositions must disclose what is not proven. The parser rejects duplicate `## Surface Contract Review` sections and duplicate fields. The scaffold emits an honest explicit `not-in-scope` default. A CLI-level regression disables the test fixture's migration helper and proves that a complete legacy artifact without the section is refused.

## Capability at Stake

This is a `skill-capability` change: the disclosure contract is portable across Charness consumers and is not tied to a host, provider, browser, or product UI. The quality validator owns form and proof-boundary disclosure; product-specific semantic truth remains human reviewer judgment.

## Failure Angles

- Jackson: a receipt-shaped artifact can expose routed gates while hiding missing semantic axes.
- Weinberg: duplicate sections or a bypassed CLI call can leave the final consumer with a weaker claim than the author intended.
- Gawande: migration and generated plugin surfaces can drift even when the root helper is correct.
- Counterweight: the form floor must not become a false semantic truth oracle.
- Proof-surface round 2: the repaired parser, CLI path, and plugin export must reproduce the bug class they repair.

## Findings

- Round 1 found two blockers: the parser read only the first surface-contract section while duplicate headings were accepted, and integration fixtures hid the missing-section enforcement path. Both were repaired with a duplicate-section rejection and a CLI-level legacy-artifact regression.
- The counterweight classified the duplicate-section and export-parity risk as `act-before-ship`, the CLI regression as required bundled evidence, and automated semantic truth checking as valid but deferred.
- Round 2 found no blocker. It confirmed the validator invokes the parser, the CLI regression disables fixture injection, root/plugin copies are byte-identical, and both validator entrypoints accept the migrated current artifact. The round-2 finding status is accepted-unreviewed under the two-round cap; no further review round is claimed.
- After round 2, the parser's section-boundary walk was refactored onto the shared Markdown section primitive and the quality reference catalog was synchronized. These are source-of-truth/duplication and catalog repairs, not new semantic policy; they are accepted-unreviewed under the two-round cap.
- The post-commit mutation lane identified three uncovered parser branches; duplicate-field and invalid-status regressions were added without changing verdict policy. This coverage-only repair is accepted-unreviewed under the same cap.

## Counterweight Pass

- C1 — Act Before Ship: reject duplicate headings and synchronize the plugin export because contradictory packets must not bypass the authoritative consumer.
- C2 — Bundle Anyway: retain the CLI-level legacy-artifact regression because helper-only tests do not prove the operator path.
- C3 — Valid but Defer: do not automate whether a human `observed` claim is semantically true; that belongs to product/domain review and would drift toward issue #515.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/quality_surface_contract.py` duplicate-heading guard | action: fix | note: reject repeated surface-contract sections before reading the first body
- F2 | bin: bundle-anyway | evidence: strong | ref: `tests/test_quality_artifact.py` legacy artifact regression | action: fix | note: keep the integration-level enforcement proof with fixture injection disabled
- F3 | bin: bundle-anyway | evidence: strong | ref: `scripts/sync_root_plugin_manifests.py` and staged mirror check | action: fix | note: keep root and exported plugin copies aligned
- F4 | bin: valid-but-defer | evidence: strong | ref: `skills/public/quality/references/surface-contract-review.md` human judgment boundary | action: defer | note: do not claim an automatic semantic oracle
- F5 | bin: bundle-anyway | evidence: strong | ref: `issue-517-proof-surface-r2` clean boundary and findings | action: document | note: record the second proof-surface review as accepted-unreviewed per the cap

## Deliberately Not Doing

No product-specific geometry, interaction, browser, provider, cross-host, or live-agent semantic judge was added. Issue #515's quality-surface routing concern remains a distinct sibling and is not silently closed by this artifact disclosure floor. No Cautilus evaluation or external provider roundtrip was run.

## Next Move

Run the final focused and repository gates, validate the critique and quality artifacts, commit with the complete bug closeout ledger, push only if the conditioned pre-push gate passes, then verify issue #517 is CLOSED through the adapter.

## Reviewer Tier Evidence

- Requested tier: `gpt-5.6-terra`, medium reasoning, priority service
- Requested spawn fields: `model=gpt-5.6-terra; reasoning_effort=medium; service_tier=priority; fork_context=false; unnamed one-shot reviewer`
- Host exposure state: requested_fields_sent
- Application state: host returned distinct unnamed reviewer agents and their completed findings to the parent transcript
- Delivery state: findings-received — three angle reviews, one counterweight, and the round-2 repaired-surface review were read by the parent

## Fresh-Eye Satisfaction

- parent-delegated — all required bounded review findings were received; round-1 and counterweight boundaries were checked, and the repaired proof-surface round had a clean boundary.

## Boundary Ownership

- Producer: quality planner/scaffold and the quality artifact author produce the surface-contract disclosure.
- Consumer: `scripts/validate_quality_artifact.py`, the plugin validator, and the operator reading the final quality artifact consume it.
- Owning surface: quality artifact form and proof-boundary contract; product semantics remain with the human/domain reviewer.
- Verdict: owned-correctly — the change strengthens the quality surface without moving product meaning into a host-local validator.

## Verification

- `pytest -q tests/test_quality_surface_contract.py tests/test_quality_artifact.py tests/test_quality_artifact_report_all.py tests/test_quality_delegated_review.py tests/test_quality_scaffold.py` — 57 passed after the repairs.
- `python3 scripts/validate_quality_artifact.py --repo-root .` — current migrated artifact accepted.
- `python3 scripts/check_staged_mirror_drift.py --repo-root .` — root/plugin mirror parity checked after synchronization.
- Round-2 delegated reviewer — no blockers; root/plugin parity, CLI enforcement, and parser behavior independently read back.

Floor-Addition Restraint: this adds a narrow form/disclosure floor because #517 and the gathered cmanki evidence show a recurrence of routed receipts being mistaken for semantic coverage. The scaffold supplies an explicit honest default, weaker dispositions name unexamined axes, and the validator does not attempt product truth judgment.

Portability: `skill-capability` — the parser, reference, scaffold, and artifact shape are portable Charness quality capability; host/provider behavior stays outside the contract.

Fresh-Eye Review Status: parent-delegated; round-2 repaired-surface findings are accepted-unreviewed under the two-round cap.
