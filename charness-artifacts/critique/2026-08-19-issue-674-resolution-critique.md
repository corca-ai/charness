# issue 674 resolution critique
Date: 2026-08-19

## Decision Under Review

The resolution of [#674](https://github.com/corca-ai/charness/issues/674): building
`check_probe_record.py --replay-stimulus` as a per-declaration ABLATION over the adapter
documents a probe record's `## Stimulus` writes, rather than the CLI replay-and-diff against
the recorded observables that the issue's acceptance names.

## Failure Angles

- **The narrowing could be a dodge.** `#674` asks for a replay diffed against
  `## Base observable` / `## Head observable`; this resolves nothing about the recorded
  observables at all. If the ablation missed the measured defect class, the narrowing would
  be a cheaper mechanism substituted for the asked-for one.
- **A detector nobody runs is not a detector.** An opt-in flag on a CLI called only by two
  closeout floors leaves `#674`'s own premise ("thirteen review rounds, no gate") intact.
- **The generator could carry the defect class it detects.** The module constructs YAML
  inputs for a reader whose dialect is narrower than YAML — the exact trap the corpus fell
  into four times.
- **Per-key ablation could pass by accident.** If each measured dead declaration happened to
  be the only entry under its key, a top-level ablation would catch all four for a reason
  that does not generalise.

## Counterweight Pass

REAL BLOCKERS, all folded before close:

- The generator carried the class three separate times — a flow sequence, a suffixed inline
  comment the reader strips back off, and type-invalid variants for booleans, floats, quoted
  and block scalars. Each measured, each repaired.
- The detector WAS inert; nothing in the repo ran it until
  `tests/quality_gates/test_probe_record_corpus_replays.py` was added.
- Per-key ablation did pass by accident. Appending `id: probe-one` — the original defect key
  — to the CORRECTED quality probe left the parent live while the control still could not
  fail. Ablation is per declaration LINE now.

OVER-WORRY, raised and not folded: the narrowing itself. A whole-output diff is defeated by
the PARTIAL dead control this corpus actually produced (the quality record's dead control
flipped three of its five CLIs), and again by volatile bytes, and it would execute a record's
own shell at a proof surface. The ablation catches every arm in the regression corpus,
including a FIFTH record no review round had found. The deviation from the issue's literal
command is recorded in the goal's `## Operator Decision Queue` rather than absorbed.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/probe_stimulus_documents.py | action: fix | note: the variant generator emitted shapes this repo's own reader cannot parse, so it measured nothing — the defect class reproduced inside the detector for it
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_probe_record_corpus_replays.py | action: fix | note: no floor, surface or standing check invoked the detector, leaving the issue's premise true for the next record
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/probe_stimulus_documents.py | action: fix | note: per-top-level-key ablation caught the measured records by accident of their content; one honest sibling hides a dead declaration
- F4 | bin: over-worry | evidence: moderate | ref: charness-artifacts/goals/2026-08-19-adapter-debt-tooling-and-remainder.md | action: document | note: the narrowing from CLI replay to declaration ablation, raised twice and not folded — recorded as an operator decision instead

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (this repo's read-only typed subagent).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name, read-only tools (Read, Grep, Glob), one bounded packet per round naming intent, changed files, invariants, non-claims and out-of-scope lines.
- Host exposure state: applied
- Application state: host-confirmed: four reviewer reports were returned to the parent across two rounds, each naming the tools it actually used and the findings it could not construct.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; each round's packet was authored inline in the spawn prompt and is reproduced in the goal's `## Slice Log` slice 1 critique field. -->

## Boundary Ownership

- Producer: `scripts/probe_stimulus_documents.py` (what a stimulus declares) and `scripts/probe_stimulus_replay.py` (whether the reader honors it).
- Consumer: `scripts/check_probe_record.py --replay-stimulus`, and `tests/quality_gates/test_probe_record_corpus_replays.py` as the standing-lane sweep.
- Owning surface: probe-record proof surface.
- Verdict: owned-correctly
