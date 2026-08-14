# Design Record Unread While Fixing The Gate Cohort
Date: 2026-08-14

## Context

Repaired the #618-#624 cohort (a broken `charness init`, six wrong-rooted shell
gates, probes that reported `false` for undetermined, an overwritten quality
record, a retro scaffold its own validator rejected, a drift message naming a
superseded probe) and wired the session-start half of the lesson lifecycle.

The work landed. The process around it did not: of ten mistakes, the repo owner
caught five, and four of those five were the same class — acting without
consulting decisions this repo had already recorded.

## Evidence Summary

- `--json` residue was seven live sites across five carrier kinds, not one. The
  widened gate names all eight against a pristine `HEAD` tree with zero false
  positives.
- `install-git-hooks.sh` run bare from the plugin mirror repointed the whole
  repository's `core.hooksPath` while printing success.
- `check-links-internal.sh` returned **exit 0** over the wrong tree — the causal
  reviewer predicted it would fail loudly; running it showed otherwise.
- 73 checked-in artifacts specify the lesson subsystem. Zero were read before an
  agent was briefed to design it.
- `check_auto_trigger.py` reports `triggered: true` for this slice on two
  surfaces. The probe was repaired in this slice and never run against it until
  the owner asked why no retro had happened.
- `TRIMBACK_INSTRUMENT invocations=1165 nonempty_paths=199 trims=0` (#605).
- Widened flags gate: 1.235s -> 5.36s wall, 1.97x CPU.

## Waste

- An agent was paid to redesign a decision the observability contract had
  already DEFERRED with a stated reason, because the brief was written without
  that contract. The workflow was stopped mid-flight and re-verified against the
  spec. (recurrence-class: premise-not-checked-against-source)
- Three causal reviewers were briefed on distinct hazard lenses and all three
  were pointed at `scripts/`, `skills/`, `tests/`. Lens-diverse, source-uniform.
  (recurrence-class: premise-not-checked-against-source)
- Audit greps carried `grep -v '^\./charness-artifacts'` to cut noise, which
  removed the only directory holding the answer. A spec path that did surface in
  one grep was classified as a past artifact and never opened.
- The #618 lane returned RED for checks that could only pass after a mirror sync
  the lane was forbidden to run — a sequencing error in the brief, not a defect
  in the work.
- A gate was piped through `head`, discarding its exit code, in a repo whose
  operating contract forbids exactly that.

## Critical Decisions

- Release withheld. The owner's condition is that the retro/lesson/quality loop
  must be complete before a version means anything; push, tag, bump and publish
  were withdrawn mid-session and stayed withdrawn.
- Hard break over a deprecating alias for `--json`, on the repo's own recorded
  ground that strict old-form refusal is not debt when capability equality holds.
- Split two oversized files rather than pass `--no-verify`. A cap bypass would
  have voided the commit's only proof.

## North Star Alignment

The north star asks for teeth only where a wrong answer escapes. The teeth this
repo has are aimed at code, and they worked: bounded reviewers found real
defects, and the spec-conformance verifier proved by executed tree snapshot that
the hook does not write. Nothing had teeth on *did you consult what was already
decided* — that check was performed by a human, five times. A wrong answer there
escapes silently and costs a redesign, so it is exactly where a tooth belongs.

## Expert Counterfactuals

**Douglas Engelbart — tool, language, and method as one unit.** The lesson that
would have prevented this session's largest failure was present, ranked, read,
and quoted, and changed nothing. It is language with no tool and no method: a
belief phrased in the vocabulary of the incident that produced it, bound to no
step. Engelbart's test is whether the three co-evolve. Here the ledger evolved
(selection, buckets, scoring schema) while the lesson stayed prose and no method
attached it to the moment of use. Designing the three together means a lesson
carries an executable step and declares the work-type it gates — which is what
`.agents/surfaces.json` already does for files and nothing does for lessons.

## Sibling Search

- Mental model: a lesson that is read has been applied.
- same layer: the auto-retro trigger repaired in this slice and never run
  against this slice | decision: same class, fixed now by running it | proof:
  `check_auto_trigger.py` exit 0, `triggered: true`, two surface hits.
  (recurrence-class: rule-exists-but-does-not-bind)
- cross-file: `scaffold_debug_artifact.py` pointing its write path at an
  unrelated OPEN investigation | decision: valid follow-up outside the slice |
  proof: scaffold payload showed `overwrite_existing_content` against a live
  `Resolution: open` artifact | follow-up: deferred #628
- abstraction up: durable persistence this session happened because the owner
  asked "is anything only in conversation?" rather than because any step
  required it | decision: valid follow-up outside the slice | proof: four
  findings were only in dialogue until that question | follow-up: deferred #627

## Lesson Evaluation

Lesson evaluation: {"reason":"missing-start","score_event_count":0,"session_id":"none","status":"not-evaluated"}

## Next Improvements

- workflow: when a fan-out reviews a surface this repo has designed before,
  assign one reviewer the design record rather than the code; recorded in
  `skills/shared/references/fresh-eye-subagent-review.md` so consuming repos
  inherit it.
- capability: a lesson needs an executable step and a declared work-type
  trigger, not only a claim; a planner can then emit it as a required read at
  the moment of use (#627).
- memory: this repo declares a lesson evaluator and still recorded
  `missing-start`, because nothing opened a session before the work. In a repo
  that HAS a ledger that value is a choice, not a configuration state, and
  should read as a finding.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-14-design-record-unread-while-fixing-the-gate-cohort.md
