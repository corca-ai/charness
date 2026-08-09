# Resolution critique — #554 and #571 (the executable backlog re-check)
Date: 2026-08-10

## Decision Under Review

Closing #554 (part 2: an automated recount helper consuming the tracker) and #571
(nothing re-checks a remedy a durable record already proposed) as resolved by the
backlog re-verification seam shipped in v4.2.0.

## Failure Angles

- **The remedy the issue NAMED was wrong.** #554's own text proposes calling
  `handoff`'s backlog reasoning. A predecessor's premise check refuted that: the
  named seam is gated behind the handoff adapter's optional `issue_source:` block,
  so a host disabling handoff pickup would silently disable this too, and it would
  have closed a dependency cycle. Building what the issue asked for literally would
  have made `achieve` the third consumer of a duplicate rather than the first
  consumer of the owner.
- **A tool that answers "is this still true?" is one step from answering "so close
  it".** That step is the whole defect this repo keeps finding, and the tool would
  be a new false-verdict surface inside the tool built to stop them.
- **Inferring a decline from record wording.** Built twice, deleted twice. See
  Structured Findings F1.
- **Closing #554 on part 1's evidence.** This is literally the instance the goal was
  designed from: #554 was FIXED-and-stale once already, and its part 2 stayed live
  while its premise read refuted.

## Counterweight Pass

- The concern that this seam duplicates `handoff`'s backlog reader is real in
  principle and does not apply: tracker access delegates to the `issue` skill's
  `issue_backend`, the contractual owner, and adds no third backend.
- The concern that `premise-refuted-clean` will be read as "close it" is mitigated
  in the only way available to a renderer: the state's own reason string says the
  channels are structural and that it is not a claim nobody declined.
- Over-worry, raised and not folded: that shipping an unexercised seam is unsafe.
  It renders and stops; the worst outcome of a wrong verdict is a human reading a
  cited line.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/recount_residue_lib.py | action: fix | note: the prose-matching design was MEASURED collapsing to 21-of-22 refusals, caused by this repo's own required `Not claimed:` bullets reading as declines — including one saying "closable now" of the issue it was cited against. Its proximity windows had been tuned by watching the output distribution (clean count 1, 3, 7, 10 across successive tunings), i.e. a verdict surface fitted to its own test set. Deleted entirely; residue is now a typed marker plus unchecked task items.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/recount_premise_lib.py | action: fix | note: an unread body, an absent record root, an unreadable file and a root present but never read each silently removed residue, which is an upgrade by subtraction toward the close-leaning state. `classify` now reads scan provenance and refuses; a channel that did not RUN is not a channel that came back clean.
- F3 | bin: over-worry | evidence: moderate | ref: skills/public/achieve/scripts/recount_residue_lib.py | action: defer | note: the scanner hardcodes `charness-artifacts` and two `docs/` paths, so a consumer with a different layout gets no record channel. It fails CLOSED (absent root becomes a refusal, never a clean verdict), so the cost is a misdiagnosing message rather than a wrong answer. Recorded in the release notes, not repaired.

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer (`bounded-reviewer`), unnamed and synchronous, two rounds.
- Requested spawn fields: subagent_type=bounded-reviewer, run_in_background=false, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: both rounds returned findings in-band, and `reviewer_boundary_fingerprint.py verify` reported `ok: true, verdict: clean` with empty drift after each.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Two bounded rounds ran, and the second round is why this closes honestly: it read the REPAIRS from round 1 and measured the collapse that round 1 could not have seen, because the design it found did not exist yet.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed: the reviewed input was the working tree at the time of each round, plus the goal artifact's slice log, cited in the goal rather than by packet digest. -->

## Boundary Ownership

- Producer: `achieve`'s Before-phase recount seam, which emits the premise state.
- Consumer: a goal being shaped, whose scope decision depends on whether an open issue is still true.
- Owning surface: `skills/public/achieve/**`, with tracker access delegated to `skills/public/issue/**` as the contractual backend owner.
- Verdict: owned-correctly
