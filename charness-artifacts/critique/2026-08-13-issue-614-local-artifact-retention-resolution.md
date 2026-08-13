# Issue 614 Local Artifact Retention Resolution Critique
Date: 2026-08-13

## Decision Under Review

Whether automatic failed-pytest-root retention and an explicit mutation-report
prune command can bound the two observed local growth paths without deleting
operator-kept evidence, managed reports, or a candidate changed after review.

## Execution

Target: code critique. Round 1 used two bounded operational and failure-semantics
angles plus a separate counterweight. Its blockers were repaired. The first
round-2 window was quarantined after a concurrent parent-session goal edit made
both boundary fingerprints fail; its approval was not used, although its root
swap and pre-unlink counterexamples were reproduced and repaired. A clean retry
of round 2 read packet `2026-08-13-120724-packet.md`; its boundary fingerprint
verified `verdict: clean` and its only blocker was repaired. That capped repair
is accepted-unreviewed under the mandatory two-round proof-surface limit and is
bound by the final rebinding packet.

## Failure Angles

- Retention semantics: does the runner distinguish failed evidence from an
  explicitly kept success, a legacy root, a custom basetemp, and an active run?
- Operator error: can zero, negative, or malformed retention input silently
  weaken the safe default?
- Deletion boundary: can a stale digest, root replacement, symlink replacement,
  newly managed path, or change immediately before unlink escape refusal?
- Reader contract: do the documented dry-run and execute commands work on both
  an established checkout and a fresh checkout with no report directory?
- Counterweight: are transactional deletion, recursive cleanup, and a generic
  cache framework required by the observed incident or speculative expansion?

## Findings

- Round 1 found the failed/success-kept ambiguity, nonpositive override bug,
  successful-run off-by-one, missing managed Stryker HTML output, and missing
  CLI-level refusal proof. Marker-backed failed roots, safe fallback, producer
  inventory, and operator-command tests repair those defects.
- The quarantined round-2 attempt identified report-root replacement and a
  change after full preflight but before a later unlink. The implementation now
  anchors the root through a directory descriptor and revalidates each candidate
  immediately before descriptor-relative unlink. Documentation explicitly says
  a multi-file cleanup is not transactional against concurrent writers.
- The clean round-2 retry found that inventory called `stat()` on an absent
  `reports/mutation` root. The accepted-unreviewed repair renders a deterministic
  empty inventory, requires the same confirmation for execute, returns a no-op,
  and never creates the directory. Its CLI regression passes.
- Review-snapshot parity states the intended delta as absent-root inventory
  changing from `FileNotFoundError` to an empty payload and confirmed execute
  becoming a no-op. After normalizing that new presence field and its digest,
  existing empty-root inventory, populated-root inventory, and unchanged
  one-candidate deletion had zero divergences; this is corpus evidence, not a
  claim of full equivalence.
- Forty focused behavioral tests pass across both operator surfaces. No live
  mutation report was deleted during proof; live inspection remained dry-run.

## Counterweight Pass

- Act Before Ship: every observed retention ambiguity, confirmation bypass,
  root/candidate replacement, and absent-root command failure was concrete and
  repaired in this slice.
- Bundle Anyway: CLI assertions and producer-derived managed-path assertions
  were added beside helper-level tests.
- Over-Worry: recursive cleanup, a generic ignored-cache framework, and hostile
  transactional filesystem guarantees have no second demonstrated owner or are
  outside the documented operator concurrency contract.
- Valid but Defer: fully atomic multi-file cleanup may be revisited only if
  concurrent mutation production becomes a supported execution scenario.

## Deliberately Not Doing

The cleanup command does not recurse, run automatically, delete legacy unmarked
pytest roots, or promise an all-files transaction. Small hidden roots remain a
monitoring follow-up only if their growth reproduces. This critique does not
cover issue #616's separate lesson and contract lifecycle feature.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run_standing_pytest.py | action: fix | note: marker-backed failure retention now preserves explicit-kept, legacy, custom, and active roots while invalid limits retain the safe default
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/manage_mutation_reports.py | action: fix | note: digest confirmation, directory-FD anchoring, managed-path recheck, and immediate pre-unlink validation guard the explicit prune boundary
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_manage_mutation_reports.py | action: fix | note: an absent report root now produces an empty CLI inventory and confirmed no-op without creating the directory; accepted-unreviewed under the two-round cap
- F4 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_standing_pytest_runner.py | action: fix | note: operator-visible CLI and lifecycle combinations are covered beside helper semantics
- F5 | bin: over-worry | evidence: strong | ref: docs/development.md | action: defer | note: recursive or automatic cleanup and generic cache retention exceed the observed owners
- F6 | bin: valid-but-defer | evidence: moderate | ref: docs/development.md | action: defer | note: transactional cleanup against a hostile concurrent writer remains outside the supported operator contract

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields and delivered findings; provider-side application metadata was not independently exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Round-1 angle reviewers and counterweight delivered findings.
The drifted first round-2 window was quarantined. The clean round-2 retry
delivered findings and its parent-side fingerprint verified with no drift.
The retry's repair is accepted-unreviewed under the two-round cap.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-13-120724-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-13-121401-packet.json`
- Packet SHA256: `ff36cbc19e48f0aff1c5db89efa9d42762e16c39081f4ba49ec352462b8e0e47`
- Identity SHA256: `ed814a91d77ed69cca1bb902204c48bd876d128eb6e8eed26175594103c47b78`
- Review-time packet path: `charness-artifacts/critique/2026-08-13-120724-packet.json`
- Review-time Packet SHA256: `dae969453b3d350071cae99fd45dd461dcbc8566adeaf042f69e53c850bf7999`
- Review-time Identity SHA256: `2939cb6c8b942fc4b081e1f76ed5e7a4975bdca960dbb5e7f1f8af4a0e816a0c`

The final packet binds the accepted-unreviewed absent-root repair bytes; it is
not a claim that a third reviewer read edits made after the capped round.

## Boundary Ownership

- Producer: the standing pytest runner owns runner-created basetemp lifecycle; mutation producers and the quality adapter declare managed report identities.
- Consumer: operators inspect retained failures and explicitly inventory or prune old unmanaged mutation reports.
- Owning surface: the runner owns automatic failed-root retention, while the standalone report manager owns explicit mutation-report deletion and its receipt.
- Verdict: owned-correctly

## Next Move

Run the broad related gates and artifact validators, synchronize generated
surfaces, then create an issue-bound local carrier for #614. No third review
round or remote-close claim is made.
