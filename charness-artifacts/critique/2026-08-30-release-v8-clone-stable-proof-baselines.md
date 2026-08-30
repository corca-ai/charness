# Clone-Stable Proof Baseline Structural Critique

Date: 2026-08-30

## Decision Under Review

Replace two symptom repairs with one authority correction: durable commit
citations derive from complete HEAD ancestry, while current inventory safety
derives live instead of rewriting a dated measurement.

Final verdict: **SHIP after the recorded act-before-ship repairs**. Release
quality, claims review, publication, and public/install readback remain separate.

## Verification Scope Decision

- Claim under test: identical tracked HEAD bytes yield clone-stable referent
  verdicts, and valid corpus growth does not require historical-probe rewrites.
- Changed surfaces: artifact referent library/checker/config/tests, inventory
  measurement safety owner/tests, debug/spec evidence, and release pytest.
- Minimum sufficient proof: side-branch, absent/non-commit, shallow, declaration
  binding/staleness, live-safety negative controls, original corpus consumers,
  Python lint, and Quality Core.
- Deliberately omitted checks: hosted Mutation Tests and empirical consumer speed;
  neither is claimed by this repair.
- Verifier contract: `scripts/check_artifact_referents.py`,
  `scripts/measure_inventory_consumption_floor.py`, and their release tests; both
  verifier contracts changed because the failure was in their authority model.
- Failure classification: verifier-defect
- Negative control: command `python3 -m pytest -q tests/quality_gates/test_artifact_referents.py` | expected refusal for side-branch commit without an exact declaration | observed result non-durable false and blocking fixture | receipt 172 proof tests, 14 hook tests, 86 referent tests, 8,699 standing tests, 82 broad gates, and exact changed-line coverage passed
- Subject identity: sha256:14e4012470ffa52e11ab23f86d328cd9d6096a7c1eb70b2dbdf674a16facf6e4
- Verifier identity: sha256:87968461e7d4d5e0e811db479d53506ac0d288fe5ff49ca8fb37807f733609b3
- Input identity: sha256:72aff882342dd9d14ce579cd73b50249de94fb994f41788d9933f58d843d3e53
- Failure identity: stable:ambient-observation-promoted-to-durable-authority
- Evidence identity: sha256:073e7f724c02a524ddda122e60e8939bb4dd64bb5c4106b7f941a30df74e1638
- Retry disposition: first-attempt
- Retry key: sha256:bab66bbcbf426115303bf28d1bb3b133570298b0c76eb434cb287400302c5139

## Failure Angles

- Clone leakage: an unrelated local object made frozen bytes look durable.
- Historical rewrite pressure: a growing corpus made a dated observation look stale.
- Exception laundering: path/line/token/reason alone could survive changed context.
- Candidate leakage: untracked declaration bytes could alter a prepublish verdict.
- Incomplete history: a shallow clone could misclassify absent ancestry.
- Performance regression: one Git subprocess per SHA made the structural repair slow.
- Dead-owner preservation: removing the final equality caller could leave a
  large diagnostic/test surface whose only JTBD was telling operators to rewrite history.
- Ownership leakage: a repo-only declaration could become consumer Git policy.

## Counterweight Pass

The first Luna review correctly blocked changed-line, untracked-candidate, shallow,
and performance gaps. Full-line SHA-256, Git-index byte binding, explicit shallow
stand-down, and one HEAD ancestry snapshot close them with negative fixtures.

Hardcoding the two current Goal sites in Python is rejected. It would replace a
structured, visible, stale-checked repo capability with a one-off exception. The
exact declaration remains reviewable and reported; it is not exported as consumer
topology policy. Requiring the floor-cost measurement to reject zero-engagement
artifacts is also over-worry: the end-to-end inventory validator owns that defect,
while this measurement explicitly measures loss caused by the value floor.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/check_artifact_referents.py` | action: fix | note: bind declarations to full line content and the Git index candidate; refuse stale, malformed, and unbound entries. Fixed with negative fixtures.
- F2 | bin: act-before-ship | evidence: strong | ref: `scripts/artifact_referents.py` | action: fix | note: shallow history cannot disprove ancestry, and per-SHA Git calls create avoidable friction. Fixed with explicit unestablished status and one ancestry snapshot.
- F3 | bin: act-before-ship | evidence: strong | ref: `scripts/measure_inventory_consumption_floor.py` | action: fix | note: dated mutable payload equality is not a live safety contract. Fixed by one live invariant owner while preserving the probe unchanged.
- F4 | bin: over-worry | evidence: strong | ref: `scripts/artifact-referent-local-context.json` | action: document | note: hardcoding exactly two sites in checker code would remove composability; exact structured declarations plus review own future additions.
- F5 | bin: over-worry | evidence: strong | ref: `scripts/measure_inventory_consumption_floor.py` | action: document | note: zero engagement is owned by the end-to-end inventory validator, not the floor-loss measurement.
- F6 | bin: valid-but-defer | evidence: strong | ref: `charness-artifacts/spec/2026-08-30-release-v8-clone-stable-proof-baselines.md` | action: defer | note: a generic consumer-facing local-history contract and hosted Mutation Tests remain non-goals.
- F7 | bin: act-before-ship | evidence: strong | ref: `tests/test_probe_drift_message.py` | action: fix | note: the caller-derived guard proved the inventory drift helper had zero live consumers; its helper and dedicated tests were deleted while the independently live residual diagnostic was split to one owner.
- F8 | bin: act-before-ship | evidence: strong | ref: `scripts/install-git-hooks.sh` | action: fix | note: maintainer setup chmodded a sourced helper and dirtied the release clone; installation now mutates execute permission only for direct Git hook entrypoints, with a negative fixture.
- F9 | bin: act-before-ship | evidence: strong | ref: `tests/quality_gates/test_artifact_referents.py` | action: fix | note: release changed-line coverage found ten unexecuted refusal branches before mutation; typed negative fixtures now cover each branch and the exact release coverage owner reports no blocking targets.

## Reviewer Tier Evidence

- Requested tier: high-leverage proof-surface and release-boundary review.
- Requested spawn fields: `model=gpt-5.6-luna`, bounded read-only proof-surface review.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden
- Delivery state: findings-received
- Execution mode: typed-subagent
- Worker report: n/a
- Worker report identity: n/a
- Worker report approval: n/a
- Worker report delivery: n/a
- Worker report packet identity: n/a
- Worker report input identity: n/a
- Worker report parent receipt identity: n/a
- Worker report findings identity: n/a

## Fresh-Eye Satisfaction

parent-delegated — Luna first returned BLOCK with five bypass angles. The parent
implemented the four verifier-owned repairs, counterweighted the two ownership
expansions, and requested a fresh review of the resulting diff. Luna then
returned SHIP for this proof-surface slice; the parent additionally collapsed
the remaining snapshot/wrapper reachability logic onto one semantic owner.

## Reviewed Input Identity

<!-- No packet was consumed; the reviewer inspected the live candidate diff and
the exact debug/spec paths. -->

## Boundary Ownership

- Producer: complete Git HEAD ancestry, indexed repo declaration, artifact text,
  and current inventory scan.
- Consumer: Charness's repo-owned release pytest and artifact gates.
- Owning surface: clone-stable proof-baseline verifier.
- Verdict: owned-correctly
