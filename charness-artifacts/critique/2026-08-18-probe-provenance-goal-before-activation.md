# probe provenance goal, before activation

Date: 2026-08-18

## Decision Under Review

Activating the draft goal
`charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md`,
which ships a probe-provenance discipline and then pays down 45 adapter-consumer census rows
using it. Target reference: spec-critique (pre-impl contract lock-in). Out of scope: code not
yet written, and whether the underlying idea is worth doing at all — the counterweight was
asked that directly and answered it.

## Failure Angles

- **Structure (Minto).** Does the artifact read to a fresh session with none of the drafting
  session's memory; is any Fixed Decision an unresolved unknown; do the Slice Plan's `Proves`
  claims match what each slice would prove.
- **Problem framing (Jackson).** Is the diagnosed generator the actual generator of the three
  refutations, or a post-hoc unifying story; does bundling a mechanism with a 45-unit debt
  paydown let a hard mechanism problem hide behind countable progress.
- **Diagnostic and boundary ownership (Weinberg).** Is the pain in the layer this goal
  targets; does each proposed thing already have an owner in this repo; is the
  `safe-checks-errors` verdict actually AST-decidable.
- **Checklist (Gawande).** Will the acceptance checks actually run; per-bullet coverage audit
  against the verification plan; is there a stop condition, a timebox, or a trip-wire.
- **Counterweight (separate pass).** Four-bin triage over the collapsed list, with an explicit
  mandate to name over-worry and to say which "fixes" would make the goal worse.

## Counterweight Pass

- Six of seventeen collapsed items change what an autonomous run would do; the rest are
  one-line hygiene or reviewers designing slice 1 for it. The counterweight corrected two
  angle reviewers on the merits: "a Fixed Decision fixed while a Probe Question tests its edge
  arms" is a normal spec shape, not a defect, and the `enumerate-consumers` "category error"
  argues with the source retro rather than with the goal.
- The counterweight named pre-specifying the probe record's schema as the most dangerous fix
  on the list: slice 1 exists to discover whether a base/HEAD pair is even representable when
  the fix is a new file, and locking the fields first turns it into a transcription task that
  cannot report its own negative. Same reasoning rejected naming the ratchet's baseline path
  and accept-flag spelling, and rejected pre-deciding the AST trial's answer.
- On shape: keep one goal, keep the sequence. The discipline-first ordering is what the
  evidence most supports. The counterweight recommended re-scoping slice 5 to a severity-led
  subset and narrowing the two-boundary claim to one; the operator kept the full 45-row corpus
  and added a release-wiring slice instead. Both departures are recorded in the goal's
  `## Discuss Before Activation`, the slice-5 grinding risk explicitly as a live residual.
- Every factual claim folded into the goal was re-verified by the parent against the cited
  file before it changed the artifact — the discipline under review, applied to its own
  critique. Two reviewer claims did not survive that check unchanged and are recorded below
  at their measured strength rather than as stated.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md | action: fix | note: base/HEAD disagreement on ANY observable clears #528 but passes #628, the refutation the rule is named after; the bar now binds the disagreeing observable to the claim, under the conditions the source names
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/what_reads_this.py | action: fix | note: the slice proposed building `--impact` on the census gate while this file already ships `--symbol`/`--path`/`--config-key` and names #599 in its docstring; proposing a change without asking what already reads the question is the class the goal exists to fix
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_adapter_consumer_classification.py | action: fix | note: the AST trial was premised on an existing witness, but `VERDICTS` maps `safe-checks-errors` to None and only `guarded` carries a marker; baseline corrected and a falsifier pre-registered with a stop rule
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_focused_changed_line_coverage.py | action: fix | note: `status == "noop"` exits 0 when no mutation-pool file changed, so a manifest-string-only commit passed the goal's own low-cost proof AND its verification lock; `noop` on a debt commit now records the row UNPROVEN, and the lock leads with per-row probe records
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/adapter-consumer-classification.json | action: fix | note: the census classifies FILES not call sites (its own stated blind class), so a row could flip on one guarded site while a second still defaults — the third 2026-08-18 refutation replicated 45 times; a row's probe now covers every call site or names the unproven ones
- F6 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md | action: fix | note: all five acceptance bullets passed with zero rows repaid, bullet 4 was already satisfied because the gate refuses an empty `reason`, the real-close bullet was unsatisfiable, and the dup-ratchet precedent does not transfer because its accept validates an ID against a scanned universe with a regenerated baseline while a census verdict is authored
- F7 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/retro/2026-08-18-adapter-version-containment-and-the-consumer-census.md | action: fix | note: the goal said three refutations share one generator; the retro's own Klein analysis says "both probe errors" and assigns the third a different countermeasure, and the closes critique says it refuted one outright with two summaries loose rather than wrong
- F8 | bin: bundle-anyway | evidence: strong | ref: scripts/boundary_probe_lib.py | action: fix | note: the goal's free-text "this probe measured nothing" would be a fifth private spelling of a state this file already types as `not-established` with `undetermined_reasons`, and its comment says in terms that a further spelling is how the concept drifts apart
- F9 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/scripts/issue_closeout_rung1_floors.py | action: fix | note: `evaluate_source_preservation` already ships the verbatim `Source text:`/`Re-read obligation:`/`Source degraded reason:` shape and `evaluate_behavioral_verdict` is the record's reader, so the goal named them as the extension site instead of inventing both
- F10 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md | action: fix | note: no `## Active Operating Frame` and no `## Coordination Cues`; the standing pytest lane was filed as a commit-boundary low-cost check, and the sync-before-pytest step and `-m release_only` lane were omitted though release gates lead the paydown order
- F11 | bin: bundle-anyway | evidence: moderate | ref: tests/test_web_fetch_cleanup.py | action: fix | note: the red-lane precondition was disowned without an owner or a stop condition; the quarantine node id is now named as the expected-red baseline so any other red stops the run
- F12 | bin: over-worry | evidence: moderate | ref: charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md | action: defer | note: pre-specifying the probe record's path, format and fields is slice 1's job; the no-base and no-build arms determine the fields, and locking them first deletes slice 1's ability to report its own negative
- F13 | bin: over-worry | evidence: moderate | ref: scripts/boundary_bypass_ratchet_lib.py | action: defer | note: the required property (generated baseline, not hand-editable beside the increase) is fixed in the goal; naming the baseline path and accept-flag spelling is a design call that wants the code open, and this file is a precedent to read rather than a template to copy
- F14 | bin: over-worry | evidence: weak | ref: docs/conventions/operating-contract.md | action: defer | note: a review-round budget table was requested; the two-round obligation is contract-mandated by trigger, capped per triggering slice, discharged by a no-repair first round, and its executable half is already named in CLAUDE.md — the table adds length and changes nothing
- F15 | bin: valid-but-defer | evidence: moderate | ref: scripts/adapter-consumer-classification.json | action: defer | note: `reconcile_usage_episodes_host_hooks.py` is `safe-not-consequential` for a raw yaml.safe_load with no version field while `quality_label_universe.py` is `no-version-validation` for near-identical prose; a real row-level dispute, queued with a revisit trigger before any baseline is ratcheted rather than pre-litigated in the spec
- F16 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md | action: defer | note: the 55 `safe-checks-errors` rows are the largest class and have no witness, but excluding them from the debt frame is a deliberate scope choice; Open Question 2's stop rule is what keeps the exclusion honest

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer, read-only (Read/Grep/Glob), four angle rounds plus one separate counterweight round.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, one angle each, no nested spawns; primary-source paths and verbatim tool output supplied inline, never the parent's conclusions.
- Host exposure state: applied
- Application state: host-confirmed: all five reviewers returned findings and each reported `envelope-unbound: no`, naming Read/Grep/Glob as its only tools.
- Delivery state: findings-received
- Fresh-Eye Satisfaction: parent-delegated
- Reviewer boundary: snapshot/verify run around the review with `reviewer_boundary_fingerprint.py`; window `w-20260818T111738Z-4186464` verified `parent-attributed` after declaring the parent's own post-review write to the goal artifact. No review approvals quarantined.

## Reviewed Input Identity

- packet path: `charness-artifacts/critique/2026-08-18-111738-packet.json`
- packet sha256: `ce72b1262a4426f5c5f64bd7bbdca824fef65b032c16c35da11b83b3de71dcf3`
- identity sha256: `ad3cdd77f66fdc3cccb511e51403c8cb74809d8e6eff889ec609e188d2dc50b8`
- Honest scope of consumption: each reviewer was given the packet's markdown render PATH among
  its primary sources and could read it; the parent did not paste its contents into the briefs
  and does not claim every reviewer opened it. The binding above identifies the packet that was
  offered, not a proven read.

## Boundary Ownership

- Producer: the `achieve` Before-phase, which shapes the goal artifact.
- Consumer: the autonomous run that `/goal` starts, plus the census gate, the issue-closeout
  floor and the release publication floor the goal's slices would change.
- Owning surface: the goal artifact under `charness-artifacts/goals/`.
- Verdict: owned-correctly

## References

- [The goal under review](../goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md)
- [The source retro](../retro/2026-08-18-adapter-version-containment-and-the-consumer-census.md)
- [The closes critique](./2026-08-18-closing-four-verified-resolved-issues.md)
- [The design north star](../../docs/design-north-star.md)
