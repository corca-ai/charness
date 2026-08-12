# Contract Register Proof Critique

Date: 2026-08-12

Execution: completed

## Reviewer Tier Evidence

- Requested tier: bounded read-only reviewer.
- Requested spawn fields: unnamed one-shot agent, `fork_turns=none`,
  `gpt-5.6-terra`, `medium`, `priority`.
- Host exposure state: applied
- Application state: host-confirmed: three independent reviewer results were
  delivered and the review-window fingerprint verified clean.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-12-011526-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-12-011526-packet.json`
- Packet SHA256: `2553a448d4eb03a89e681083e6f96b177535f385562f7112126d9373f2a13fe5`
- Identity SHA256: `904005f934ac89ae3ec704cfbe6be2c6c03ba4024cb712768f39b3105e0ff930`

## Target

Code critique of the schema-v1, proposal-only contract-register validator and
its checked-in state. Success means the register is a strict, inspectable
pre-contract-mutation probe; it must not write or approve a contract change.

## Angles

- Unit identity and proposal semantics — `register_semantics_angle`.
- Committed-prefix, export, and quality-boundary behavior —
  `register_boundary_angle`.
- Counterweight against speculative lifecycle enforcement —
  `register_counterweight`.

## Findings

- F1 | bin: act-before-ship | evidence: strong | ref:
  `scripts/contract_register_lib.py` | action: fixed | note: mixed fence markers
  could close a different opener and indented ATX H2 headings were missed.
- F2 | bin: act-before-ship | evidence: strong | ref:
  `scripts/contract_register_lib.py` | action: fixed | note: citation sources
  accepted `recent-lessons.md` and arbitrary Markdown instead of the session
  retro universe.
- F3 | bin: act-before-ship | evidence: strong | ref:
  `scripts/contract_register_lib.py` | action: fixed | note: two proposals could
  claim the same future unit ID.
- F4 | bin: act-before-ship | evidence: strong | ref:
  `scripts/contract_register_lib.py` | action: fixed | note: underscore escaped
  punctuation normalization, permitting identity collision avoidance.
- F5 | bin: act-before-ship | evidence: strong | ref:
  `scripts/contract_register_lib.py` | action: fixed | note: an empty register
  unnecessarily required a valid lesson ledger.
- F6 | bin: act-before-ship | evidence: strong | ref: `scripts/run-quality.sh` |
  action: fixed | note: an always-on quality gate contradicted the stated
  pre-mutation-only schema and would block a future reviewed membership change
  before an applied-transition protocol exists.
- F7 | bin: bundle-anyway | evidence: moderate | ref:
  `tests/test_contract_register.py` | action: fixed | note: a temporary Git
  fixture now pins the deliberate schema-v1 refusal of a post-commit contract
  membership rewrite.
- F8 | bin: over-worry | evidence: moderate | ref:
  `charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md` |
  action: defer | note: resolving an anchor against Markdown prose would exceed
  the declared non-empty-anchor probe contract.
- F9 | bin: valid-but-defer | evidence: strong | ref:
  `scripts/contract_register_lib.py` | action: defer | note: applying an
  approved add/remove/rename needs a new reviewed schema with membership
  transitions and retired-unit history; schema v1 intentionally refuses it.

## Counterweight Triage

Act Before Ship: F1-F6 were repaired and covered by targeted tests.

Bundle Anyway: F7 makes the pre-mutation non-claim executable rather than
pretending schema v1 supports contract retirement.

Over-Worry: anchor-text resolution and target-heading existence are content
interpretation or actual contract edits, neither of which this probe owns.

Valid but Defer: catch-to-unit mappings, applied graduation/retirement,
historical unit identities, and standalone plugin invocation with a consumer's
artifact state remain later workflow decisions.

## Boundary Ownership

- Producer: the local register validator rebuilds unit state and validates
  proposal evidence.
- Consumer: an explicit pre-contract-mutation operator invocation.
- Owning surface: `charness-artifacts/retro/contract-register.json` plus its
  repository-local checker.
- Verdict: owned-correctly

The validator and its JSON state remain charness-local. It is invoked explicitly
as a pre-mutation probe, not added to the universally blocking quality runner;
the future contract-change workflow owns any applied membership transition.

## Rounds

The pre-implementation review established the fixed capacity, canonical unit
identity, strict provenance, and pre-mutation scope. The first proof review
found catch-prefix, fence, and citation-source defects, all repaired. This
standalone critique found F3-F6 on the repaired surface; those repairs are
accepted-unreviewed under the proof-surface two-round cap.

## Next Move

Close schema v1 with the explicit checker and tests. A later reviewed slice may
define score-recording workflow and, separately, an applied contract-membership
transition; neither is authorized by this probe.
