# Triage Sweep And Birth Trigger
Date: 2026-07-28

## Decision Under Review

Executing the operator's two decisions: a full triage sweep over the 146
never-examined verdict-rendering proof surfaces, and a birth trigger for new proof
surfaces as an advisory with a durable closeout record.

Fresh-eye pass: scripts/new_proof_surface_advisory.py — bounded reviewer found 15
findings; the detector was rebuilt on measured recall as a result (see F1).

## Failure Angles

- **The birth-trigger detector silently misses the population it exists for.**
  Reviewed and CONFIRMED by execution: the first cut classified new files by their
  text and caught 18 of 30 known-defective surfaces (60%). It missed nine
  `scripts/*_lib.py` verdict modules and `check_staged_reversion.py`, whose
  verdict vocabulary is `clean`/`blocked` rather than `passed`/`violation`. A
  detector that quietly does not fire for exactly its target population is the
  class this repo is hunting, in the tool built to hunt it.
- **The same detector cries wolf.** Measured: 167 of 601 files in the scanned
  families classified as proof surfaces, including scaffolders, adapters,
  recorders and packet builders. A false advisory trains token-theater, which the
  repo's own floor-addition-restraint rule names as worse than silence.
- **The advisory reproduced the class in its own record.** `{"new_proof_surfaces":
  [], "fresh_eye_pass_recorded": false}` was byte-identical for "this slice added
  none", "the base ref did not resolve", and "a file could not be read" — a
  verdict over a scope never established, with a test pinning it as intended.
- **A sweep that reports "clean" becomes a terminal green.** Guarded: scanners
  were required to emit `surfaces_clean` explicitly, and the artifact states that
  clean means one lens, one pass, one agent.
- **1.52M tokens buys a confident number that is not proof.** The sweep traded the
  prior hunt's parent-reproduces-everything discipline for breadth. Recorded as
  three provenance tiers rather than a single "109 defects" headline.

## Counterweight Pass

Real and fixed: the 60% recall (path widened to the families, verified 30/30), the
false-fire (classification handed to the reader, because measurement showed the
signal is not in the token stream — the best variant reached 73% recall at 55%
false-fire), the slice-global marker that let one line silence N surfaces, the
fence-blind marker, the missing scope field, and a `UnicodeDecodeError` that could
abort a passing closeout.

Over-worry: the 16-20 new files per week the widened detector lists is a real nag
cost, but it is per-slice 1-5 files and the advisory asks a judgment question
rather than asserting a classification — which is what the measurement says is the
only honest option.

Deferred with reason: 109 survivors are NOT claimed as 109 defects. Four were
parent-reproduced. The rest are worked by reproducing first.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/new_proof_surface_advisory.py:44 | action: fix | note: text classifier caught only 18/30 known surfaces; replaced with family-wide listing plus a reader decision
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/new_proof_surface_advisory.py:52 | action: fix | note: classifier fired on 167/601 files including scaffolders and adapters
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/new_proof_surface_advisory.py:110 | action: fix | note: one marker applied a slice-wide boolean to every surface, making N-1 skips quiet
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/new_proof_surface_advisory.py:118 | action: fix | note: marker scan was fence-blind, so a quoted example counted as a disposition
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/new_proof_surface_advisory.py:96 | action: fix | note: empty record could not distinguish nothing-added from could-not-look; scope field added
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/slice_closeout_advisories.py:436 | action: fix | note: UnicodeDecodeError is a ValueError not OSError, so an undecodable new file aborted a passing closeout
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/new_proof_surface_advisory.py:78 | action: fix | note: skills/shared omitted from the path family, repeating audit row D9's own defect
- F8 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_new_proof_surface_advisory.py:143 | action: fix | note: a test pinned the could-not-look ambiguity as intended behavior, the C1 shape
- F9 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md:1 | action: document | note: 105 of 109 survivors are not parent-reproduced; provenance tiers recorded rather than a single count
- F10 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/inventory_ubiquitous_language.py:204 | action: defer | note: parent-reproduced zero-scan reporting ok; first row to work in the next cycle
- F11 | bin: over-worry | evidence: moderate | ref: scripts/new_proof_surface_advisory.py:78 | action: document | note: 16-20 new files per week is a real nag but per-slice it is 1-5 and the advisory asks rather than asserts

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded-reviewer (typed read-only agent) for the birth trigger; 5 scan + 5 refute + 1 rank workflow agents for the sweep
- Requested spawn fields: subagent_type, prompt, run_in_background; no host addressing name, per the repo spawn-shape rule
- Host exposure state: requested_fields_sent
- Application state: the birth-trigger reviewer reported `envelope-unbound` in reverse — it saw only Read/Grep/Glob and could not execute, so its table was hand-derived and the parent re-ran it
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No packet was consumed: reviewers were given the working tree and the audit rows directly. -->

## Boundary Ownership

- Producer: the closeout advisory surface and the evidence-surface audit record
- Consumer: the next session choosing which proof surfaces to reproduce and fix
- Owning surface: repo-owned closeout advisories (`scripts/`) and `charness-artifacts/audit/`
- Verdict: owned-correctly
