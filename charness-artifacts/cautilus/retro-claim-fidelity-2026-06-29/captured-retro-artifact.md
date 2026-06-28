# Retro — claim-fidelity fixture calibration sweep

Mode: session

## Context

Reviewing the per-skill claim-fidelity fixture calibration sweep that shipped in
`v0.57.0`: all 20 public-skill `evals/cautilus/*-claim-fidelity/spec.json`
fixtures were calibrated against the locked methodology contract
(`charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md`) so
that each fixture's `requiredCommandFragments` (RCF — the engage-always doc
floors a representative run is *forced* to open) and pinned prompt honestly
match the skill's documented routing. Tree is clean, sweep is committed and
released. What matters next is the pinned follow-on: live-capture validation,
which empirically closes the still-open "did a real run actually open these
docs?" gap and sets the first per-skill `thresholds.max_duration_ms` baseline.

## Evidence Summary

- The 20-skill commit chain `8fb030ca..c389d916` (`claim-fidelity(<skill>): RCF
  N -> M ...`), plus release `2654b1ff`, critique `86ba6f3f`, handoff
  `852e2f16`/`482352dc`.
- Methodology spec (8 calibration lenses, three-value engagement axis, schema).
- Representative diff `29260c26` (impl RCF 5 -> 1) and the mid-sweep lens-8
  addition `bb715a88`; protocol-nuance commit `5fd343b2`.
- `prepare_packet.py` packet (changed-files section: clean tree, no surfaces).
- No host-log efficiency probe run: this work spans many compaction-separated
  sessions, so no single-session turn/token window is a faithful measure; waste
  below is drawn from the commit record, not proxy token counts.

## Waste

- **Over-broad RCF was a systemic first-pass defect, corrected one skill at a
  time.** Nearly every skill's initial fixture declared too many floors versus
  calibrated peers (impl 5->1, release 5->3, retro 4->1, hitl 4->1, spec 4->2),
  each needing its own tightening commit. The unifying rule — lens 7
  (script-briefs-judge): a doc is an RCF floor only if its *unique, non-inlined*
  content is forced open; gist that SKILL.md already inlines is
  engage-always-but-not-a-floor — was applied per skill rather than set as the
  default before the sweep began. This is the dominant repeated correction.
- **Calibration vocabulary was incomplete when the sweep started.** Lens 8
  (executable-subject) was added mid-sweep at `bb715a88` after the operator
  caught that the impl prompt described a run's *shape* ("implement a small code
  slice") with no concrete subject — so the RCF floor rested on a run that never
  occurs. The audit then found the same flaw in hotl and ideation, forcing
  re-pins of three already-"finished" skills. Seven prior critique passes never
  asked "is the prompt executable?" — the check did not exist yet.
- **Zero empirical anchoring.** All 20 fixtures are static inferences about what
  a run *would* open; `thresholds` is omitted everywhere pending a real capture.
  Honestly flagged and deliberately deferred, but it means the whole sweep's
  central claim is still unverified by a single live trace.

## Critical Decisions

- **Lens 7 (engage-always vs RCF-floor split).** Separating "the run engages
  this concern" from "the run is forced to open *this doc*" is what made the
  fixtures honest rather than aspirational; it constrained every subsequent
  per-skill call and is the reusable core of the methodology.
- **Ungameable prompts.** Prompts pin a representative subject *without naming
  the reference file*, so the matcher scores real file-opens, not prompt
  wording. This kept the fixtures from grading themselves.
- **Don't-manufacture-a-defect.** When a skill genuinely inlines its gist
  correctly (impl, hitl, gather), ship fixture-only and invent no churn
  (`5fd343b2`). Prevented the sweep from "fixing" correct skills.
- **Ship static-only, defer live-capture to a named next phase.** Released the
  calibrated fixtures as `v0.57.0` rather than blocking on 20 captures — a
  defensible scope cut, but it is the source of the open verification gap.

## Expert Counterfactuals

- **Michael Feathers (characterization-first lens).** Feathers' rule for legacy
  behavior is: don't reason about what code *should* do, pin what it *actually*
  does with a characterization test, then refactor against that pin. Applied
  here he would have inverted the order — take the single cleanest skill
  (retro->expert-lens) through one *live capture* first, let the observed
  file-opens define its RCF floor empirically, and only then generalize the lens
  to the other 19. That ordering would likely have surfaced lens 8's
  executable-subject requirement on skill #1 (a non-executable prompt produces an
  empty or garbage trace immediately), instead of after the operator caught it
  mid-sweep and forced three re-pins. The sweep did 20 reasoned calibrations and
  0 captures; one capture up front was the cheapest place to complete the
  vocabulary.
- **Direct lens — spike one end-to-end before fanning out.** Independent of the
  name: when a fan-out applies a not-yet-proven rubric N times, drive *one* item
  through the entire loop (calibrate -> live capture -> threshold -> confirm)
  before sweeping the rest, so the rubric is frozen and empirically anchored
  before it scales. This is exactly the pinned next task — its value is that it
  *should have been item 1, not item 21*.

## Next Improvements

- **workflow:** For any fixture/eval fan-out over an unproven rubric, make
  "spike one item end-to-end (including its live capture)" a hard gate before the
  remaining items, so calibration vocabulary is complete before it scales. The
  live-capture phase is already pinned; do it on the cleanest single-floor skill
  first and treat any RCF miss as a calibration signal, never a matcher to
  soften.
- **capability:** Add an advisory check that flags a claim-fidelity fixture
  whose `requiredCommandFragments` count exceeds the calibrated-peer norm (1-2),
  or whose RCF basename's key phrases already appear in the skill's always-loaded
  SKILL.md body (a `skill-inlined-context` candidate that should be
  engage-always-not-floor). This mechanizes the lens-7 question and would have
  caught the over-broad first-pass floors before per-skill review.
- **memory:** Record two durable lessons (below, into `recent-lessons` via the
  digest refresh): (1) first-pass claim-fidelity fixtures systematically
  over-declare RCF — default to the minimal floor (the one doc whose unique,
  non-inlined content a run is forced to open); (2) freeze the calibration
  vocabulary with one end-to-end spike before a fan-out, or pay re-pin churn when
  a new lens lands mid-sweep.

## Sibling Search

The transferable pattern is "apply a not-yet-empirically-proven rubric across a
fan-out before completing/anchoring it." Scanning for where the same shape recurs:

- same layer: support-skill claim-fidelity tier (handoff: "not started") |
  decision: valid follow-up outside the slice | proof: handoff "Next Session"
  names it as a future fan-out that will inherit the exact RCF/engagement rubric;
  it must start from the minimal-floor default + spike-one-end-to-end, not repeat
  the over-broad first pass. follow-up: deferred docs/handoff.md "Next Session" item 2
- abstraction up: any future eval-fixture family that fans a rubric across N
  targets (not just claim-fidelity) | decision: diagnostic-only | proof: the
  workflow Next Improvement already generalizes the spike-one gate to all
  fixture/eval fan-outs; no separate carrier to fix now.
- specialization down: quality pilot #397 runtime-consultation proof (handoff:
  "still open") | decision: valid follow-up outside the slice | proof: it is the
  one skill whose live capture is independently pending; it is the natural
  spike-one candidate for the quality lane. follow-up: deferred docs/handoff.md
  "Next Session" item 2
- mental-model siblings: the 20 shipped fixtures themselves | decision:
  intentional boundary | proof: they are statically calibrated and released;
  re-opening them is the pinned live-capture phase, not unswept siblings — each
  capture revises its own fixture under the established "miss = calibration
  signal" rule.

## Persisted

Persisted: yes: `charness-artifacts/retro/2026-06-29-claim-fidelity-fixture-calibration-sweep-retro.md`
(digest `recent-lessons.md` + `lesson-selection-index.json` refreshed by
`persist_retro_artifact.py`).

## Packet Consumed

`changed-files-and-owning-surfaces` (clean working tree; no owning surfaces
matched — the reviewed work is already committed, consistent with a
post-release session retro).
