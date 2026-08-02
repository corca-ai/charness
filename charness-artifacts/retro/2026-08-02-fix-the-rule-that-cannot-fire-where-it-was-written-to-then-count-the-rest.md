# Session Retro
Date: 2026-08-02

## Context

Goal `fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest`.
Three lanes: repair the operator-reported #475 (bounded review MANDATED by several
skills, inert in any repo that never ran `setup`), then MEASURE the rest of that
class, then give the duplicate-ratchet trap the edit-time affordance the
length-headroom trap already has (#474). Six bounded reviewers plus a 12-agent
sweep workflow across three commits.

## Evidence Summary

- Lane A: the three-rung authorization ladder in
  `skills/shared/references/fresh-eye-subagent-review.md`, backed by
  `skills/shared/scripts/resolve_subagent_delegation.py` +
  `subagent_delegation_record.py`; 44 tests in
  `tests/quality_gates/test_subagent_delegation_ladder.py`; commit `7e452912`.
- Lane A measurement: 688 critique artifacts validate green after the change
  (988 files in the directory = 688 artifacts + 300 prepare packets, excluded by
  content kind in both selection modes). Taken AFTER this run's own artifacts
  landed, and stated as such.
- Lane B: `charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md` —
  197 units assigned, 172 read (87%), 25 unread and counted, 201 rules
  classified, 14 `cannot-fire` claims, **11 refuted** by adversarial
  verification, 1 confirmed and repaired.
- Lane C: `scripts/dup_ratchet_edit_advisory.py` + 16 tests; commit `39a2768a`.
- Four reviewer boundary windows (`lane-a-round-1`, `lane-a-round-2`,
  `lane-c-round-1`), every `verify` exit 0 with `{"ok": true, "verdict":
  "clean", "drift": []}` and nothing parent-declared.

## Waste

- **The dup ratchet hard-blocked three separate times in this run**, each after a
  slice was finished. This is the FOURTH consecutive run to write "run it early"
  into a plan and hit the aggregate anyway. That is exactly what Lane C existed
  to fix, and the run produced its own fourth data point before the fix landed.
- **Round-1 repairs on a proof surface shipped the class they repaired, twice.**
  The `delegation signal` heading added to let a decline be recorded honestly
  could not fire on the one-line record the contract prescribes, because the
  floor matched the heading only at line start. And `blocked_kind` was computed
  while the operator-facing advisory still said "confirm the host genuinely
  could not spawn one". Neither was visible to round 1 — it was reviewing code
  that did not exist yet.
- **A test fixture spelled a string the way the matcher wanted.** The first
  version of the decline-record test hand-built a TWO-line status that appears
  nowhere in the contract, and passed, while the prescribed one-line form was
  still refused. Same shape as #471's synthetic fixture.
- **Two of three duplicate families raised in Lane C were real duplication I had
  just written** — a second repo-relative-path resolver and a repeated subprocess
  block — reachable by reusing `path_portability_lib.resolve_within_repo`. The
  reflex to classify rather than to look would have made the ratchet's report
  true and useless.

## Critical Decisions

- **Verify the premise before shaping the slice.** Both of #475's code consumers
  were read first and both already degrade open, so Lane A was scoped as a
  contract-and-mechanism change rather than a validator fix. That read cost two
  minutes and removed a whole false lane.
- **Write the predicate down before reading the population.** Committed as its
  own commit ahead of any finding, so the count is a measurement rather than an
  impression.
- **Verify adversarially, defaulting to refuted.** This is the decision that
  mattered most: it killed 11 of 14 findings. A sweep that trusted its surveyors
  would have checked in a confident wrong measurement, which is worse than none.
- **#473 resolved as a tripwire, not deleted.** The predicate's own wording
  settled it — the situation the flag was written for is the grandfather
  LEAKING, not the current corpus. Deleting a guard because its regression has
  not happened yet is the opposite error from this goal's.
- **#476 filed rather than fixed.** Both repair directions newly APPLY floors to
  repos previously outside them, which needs its own measurement (D49).

## Expert Counterfactuals

- **A security reviewer's "who signs this?" lens** would have reached the
  provenance hole in one question. `recorded_by: "user"` was a hardcoded literal
  that no reader ever read, so a self-grant and a real grant were byte-identical.
  It took a bounded reviewer to name it; the lens would have caught it at design
  time, before the first version shipped.
- **Direct counterfactual: had the Lane C advisory existed at the start of this
  run**, it would have fired on the first large edit to
  `validate_critique_artifacts.py` — before Lane A's gate run — and the three
  hard blocks would have been one early check. It did fire, on the edit that
  implemented it, which is the cheapest proof available that it works.

## Sibling Search

- axis: same-class-elsewhere | decision: valid follow-up outside the slice | proof: `charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md` records the consuming-repo reading as under-measured — most refuted claims were "inert where the skill is installed" answered by a firing input in the AUTHORING repo, and the verifiers were tuned to refute on uncertainty | follow-up: deferred handoff-consuming-repo-inertness
- axis: fixture-shaped-to-the-matcher | decision: valid follow-up outside the slice | proof: this run's decline-record test and #471's synthetic `AGENTS.md` fixture are the same failure — a test input written to match the implementation rather than the contract | follow-up: deferred handoff-fixture-from-source-constants

## Next Improvements

- workflow: build test inputs from the source constant, never by retyping the
  string the code is supposed to accept. Applied in this run
  (`_decline_status_line` reads `_DECLINE_ACTION` and splits it) after the
  hand-typed version passed against a form nothing prescribes.
- capability: the edit-time dup-ratchet advisory, so the trap is a workflow
  signal instead of a plan bullet nobody reads mid-slice.
- memory: a proof-surface repair owes its second round, and the round that reads
  the REPAIRS is where the class reappears — twice in this run, neither visible
  to round 1.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md
