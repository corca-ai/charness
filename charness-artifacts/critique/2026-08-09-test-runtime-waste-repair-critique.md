# Critique Review
Date: 2026-08-09

## Decision Under Review

Whether the #577/#578/#579 lifecycle, scope, and regenerable-inventory repair,
plus evidence-backed test deduplication, can land without weakening production
verdicts, leaking test-owned resources, or hiding versioned source.

## Execution

Target: code critique. Two round-1 angles (problem framing and diagnostic
ownership) plus a separate counterweight reviewed the first packet. Because the
checker is a proof surface and round 1 caused repairs, one round-2 reviewer read
the full repaired surface. Round 2 found one late-registration race; its repair
is accepted-unreviewed under the two-round cap and is bound by the final packet.
Issue #579 then ran its own two bounded rounds after closeout reproduced a new
proof-surface boundary; its capped repair is also accepted-unreviewed.

## Failure Angles

- Problem framing: does every fixture own every child it creates, including the
  ordinary group-owned holder and failure paths?
- Diagnostic ownership: can zombie state or PID reuse make cleanup lie or signal
  a stranger, and does fixture temp scope stay distinct from ambient runner state?
- Operational: are production defaults, generated mirrors, unique test behavior,
  and durable non-claims preserved?
- Round 2: can the repaired side-channel itself miss a retry-owned holder and
  render a false clean verdict?
- SLOC rounds: can output self-exclusion overmatch a same-name/same-suffix
  source or interpret path metacharacters as glob syntax?

## Findings

- Round 1 found the ordinary holder lacked registration/finally cleanup and the
  escaped-holder helper used raw PID-only liveness/signalling. Both were fixed
  with a controlled holder, unique stop-path identity, state+argv inspection,
  and exit acknowledgement.
- Round 2 reproduced a race where the child wrote its PID after cleanup took a
  one-time snapshot. Registration now happens synchronously in the fixture
  parent immediately after `Popen`; all three tests assert registered-holder
  count equals the checker's retry attempt count. Five repeated race runs pass.
- Root/plugin checker copies are byte-identical, production defaults remain five
  seconds, and explicit footprint tests continue to override the synthetic
  helper's fixture-owned default root.
- SLOC round 1 rejected a basename-global exclusion that hid any directory
  named `sloc-inventory`; round 2 rejected a suffix glob that hid legitimate
  source and mishandled `[]*?`. The capped repair filters the exact resolved
  output identity from Tokei's report and preserves every other report.

## Counterweight Pass

- Act Before Ship: ordinary-child ownership, raw-PID identity, and late retry
  registration were real, evidence-backed blockers; all are fixed.
- Bundle Anyway: the retry-attempt/holder-count assertion was added beside the
  repair so future fixture changes cannot silently narrow the population.
- Over-Worry: a generic subprocess framework, repo-wide env sanitizer, and
  scheduler rewrite lack another demonstrated owner or are refuted by A/B.
- Valid but Defer: the worker optimum is one-host evidence and may be remeasured
  after a host/profile change; it is not a current defect.
- Act Before Ship: both broad SLOC exclusions were false-verdict blockers and
  were replaced with literal report-identity filtering.

## Deliberately Not Doing

No production cleanup of `setsid` escapees is claimed: the production checker
owns bounded drain, while tests own their deliberately escaped descendants.
No hosted-CI green claim, runtime-budget change, generic lifecycle framework,
git-tracked hidden-file SLOC contract, or third review round is included.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_cli_skill_surface.py | action: fix | note: ordinary holder registration, production survivor assertion, and finally cleanup added
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_cli_skill_surface.py | action: fix | note: raw PID signalling replaced with unique identity, process state, stop side-channel, and exit acknowledgement
- F3 | bin: act-before-ship | evidence: strong | ref: round-2 late-registration counterexample | action: fix | note: parent now registers every retry holder synchronously and tests bind holder count to attempts; accepted-unreviewed under the cap
- F4 | bin: over-worry | evidence: moderate | ref: scripts/check_cli_skill_surface.py | action: defer | note: generic subprocess or environment framework has no second demonstrated consumer
- F5 | bin: over-worry | evidence: strong | ref: charness-artifacts/quality/2026-08-09-test-runtime-waste-repair.md | action: defer | note: 16 workers beat 12 and 8 in the exact local cohort; no scheduler change
- F6 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/2026-08-09-test-runtime-waste-repair.md | action: defer | note: cross-host worker optimum remains unclaimed until another profile regresses
- F7 | bin: act-before-ship | evidence: strong | ref: issue #579 round-1 basename counterexample | action: fix | note: static basename exclusion removed because it hid legitimate same-named source
- F8 | bin: act-before-ship | evidence: strong | ref: issue #579 round-2 suffix/metacharacter counterexamples | action: fix | note: exact resolved report identity replaces raw glob matching; accepted-unreviewed under the cap
- F9 | bin: valid-but-defer | evidence: moderate | ref: Tokei hidden-file default | action: defer | note: defining SLOC over all git-tracked hidden source is a separate scope contract

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`, `fork_turns=none`.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields and delivered findings; provider-side application metadata was not independently exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Round-1 problem-framing and diagnostic reviewers, a separate
counterweight, and one round-2 repaired-surface reviewer returned findings.
Issue #579 also received two bounded rounds over its repaired proof surface.
Each parent-side boundary fingerprint verified `verdict: clean` with no drift.

## Reviewed Input Identity

- Packet consumed: the two test-runtime packets plus `charness-artifacts/critique/2026-08-09-issue-579-sloc-runtime-exclusion-round1-packet.md` and `charness-artifacts/critique/2026-08-09-issue-579-sloc-runtime-exclusion-round2-packet.md`.
- Packet path: `charness-artifacts/critique/2026-08-09-test-runtime-waste-repair-final-binding-packet.json`
- Packet SHA256: `cb9d95e4f7984e6fff8afc2a3caf2765924a4bb73bb7438879c2c9f3216922c6`
- Identity SHA256: `72deffa2d31f78a70ce9ec9456da79f4f67e99a5503224b47eb6d0b6894f8cd8`
- Review-time round-1 binding: packet `1bbc560799edbb060f390e57e5bc4fb7b109837e68e01a5ad75bf90c3a8b0466`, identity `dc1ad1c0fa4f4bdb23423b6a7a72d6efcaf53f66300147dfabaaac366e730ec4`.
- Review-time round-2 binding: packet `903336a4dc9c1689e812265d5311c522346dbb307e8c29835179fa3c2d40070f`, identity `578b2b3aa64a049c878d3239f36a1dfd1eda2bf23ce0e817d92e4ca52ad2cdd1`.

The final packet binds the accepted-unreviewed round-2 repair bytes; it is not
a claim that reviewers read edits made after the capped round.
The regenerable SLOC JSON is deliberately outside that byte identity because it
counts the packet itself; sync plus the artifact validator own that output,
while the bound generator, mirror, tests, and reviewed dogfood own its behavior.

## Boundary Ownership

- Producer: each test fixture produces descendant identity/lifecycle state and
  synthetic temp scope; the checker produces timeout/drain observations.
- Consumer: focused tests consume lifecycle/scope evidence; the CLI checker
  consumes only its production timeout configuration and probe outputs.
- Owning surface: test fixtures own stop/ack and temp-root isolation; the shared
  checker owns group termination and bounded drain; SLOC inventory owns exact
  output-report removal, with both plugin projections synchronized.
- Verdict: owned-correctly

## Next Move

Run final sync, changed-surface and full quality proof, bind mutation/changed-line
coverage, then carry #577/#578/#579 through the issue closeout draft. No third review
round is claimed.
