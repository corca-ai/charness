# Critique Evidence Floor As One Subsystem
Date: 2026-07-28

## Decision Under Review

Closing bug-hunt rows C1-C4/C6 as a single subsystem contract change rather than
five patches, and reclassifying proof-surface authoring as an irreversible
boundary in the north star. The operator chose the structural framing first.

## Failure Angles

- **The fix reproduces the class.** Six prior slices, six reviews finding defects
  inside the fix. Reviewed: three bounded reviewers, eleven defects, and the
  sharpest was the scope record — added to stop verdicts over unestablished
  scope — asserting an unestablished scope on the common `run-quality.sh` path.
  Now seven of seven.
- **Tightening a floor 650 artifacts must satisfy refuses honest work.** Reviewed:
  the `n/a` packet declaration became a demand for SHA256 fields for a packet the
  artifact said does not exist; the scaffold pre-loaded three undisclosed
  failures; and one fix would have demanded a tier section for `nested-delegated`,
  a floor addition smuggled in as a repair.
- **The structural move becomes another gate.** The north star forbids meeting a
  gate-quality problem with another gate. Checked: the reclassification adds no
  gate — it names an existing boundary so the already-running fresh-eye review is
  the contractually required observer there.
- **The reclassification's evidence is thinner than its claim.** The 6-of-6 (now
  7-of-7) hit rate is this working session only, and the "introduced already
  broken" archaeology covered four of thirty defects. The north-star text says
  "measured" and cites the hunt; it does not claim a census.

## Counterweight Pass

Real blockers, all fixed inside the slice: the fabricated probe state, the
`observed_date is None` fail-open handing C4 back, the markup-defeated stub check,
the shadowable and fence-blind claim reader, the `n/a` over-block, and the
nested-delegated floor addition.

Over-worry: the `--all` tier-evidence tightening was measured against the full
corpus by the implementer and independently re-measured by a reviewer using a
different method; both found zero regressions, and the suite confirms.

Deferred with reason, not silently: C3's heading form and C6's committed-range
blindness are contract changes, not patches, and every widening of a content
trigger buys a false-refusal risk on artifacts that merely discuss this surface.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/critique_enforcement_scope.py:196 | action: fix | note: scope record asserted a probe resolution that never ran when zero artifacts were in scope
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/validate_critique_artifacts.py:478 | action: fix | note: observed_date None was fail-open, returning the whole of C4 under --all
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/critique_reviewer_evidence.py:115 | action: fix | note: stub check tested raw value so bold TODO passed while plain TODO was refused
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/critique_enforcement_scope.py:116 | action: fix | note: claim reader took first phrase match and was fence-blind, disarming the consistency check
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/critique_enforcement_scope.py:65 | action: fix | note: widened packet trigger refused artifacts declaring no packet, with no possible remediation
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/validate_critique_artifacts.py:471 | action: fix | note: routing the tier trigger through the completed-delegation set was a floor addition disguised as a repair
- F7 | bin: valid-but-defer | evidence: strong | ref: scripts/critique_enforcement_scope.py:47 | action: document | note: heading-form and mid-line packet declarations still unmatched; needs a different parse than a line trigger
- F8 | bin: valid-but-defer | evidence: strong | ref: scripts/boundary_probe_lib.py:79 | action: document | note: cross-surface probe reads the committed range so the slice under critique is invisible; contract change
- F9 | bin: valid-but-defer | evidence: strong | ref: scripts/validate_retro_artifact.py:136 | action: defer | note: retro keeps the body-first date fallback C2 replaced, so retro floors stay back-dateable
- F10 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_critique_artifacts.py:116 | action: defer | note: two legacy allowlist entries name prepare packets excluded by content kind, so they are dead rows reading as live decisions
- F11 | bin: over-worry | evidence: moderate | ref: skills/public/critique/scripts/scaffold_critique_artifact.py:135 | action: fix | note: authoring churn was real but one round-trip, and the collect-all reporter already returns every violation at once

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded-reviewer (typed read-only agent, three distinct angles)
- Requested spawn fields: subagent_type, prompt, run_in_background; no host addressing name, per the repo spawn-shape rule
- Host exposure state: requested_fields_sent
- Application state: two of three reviewers reported `envelope-unbound` — Bash/Edit/Write/Agent visible despite the read-only agent type; all three wrote nothing and boundary verify confirms it
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No packet was consumed: the reviewers were given the working tree plus the audit rows directly. -->

## Boundary Ownership

- Producer: the critique evidence-floor validator and its enforcement-scope module
- Consumer: every closeout that cites a critique artifact as proof a review happened
- Owning surface: repo-owned critique validation (`scripts/`), with the scaffold half in the portable public skill
- Verdict: owned-correctly
