# Slice Retro — batch A, "an absent input is not a matching input"
Date: 2026-08-01

## Context

Slice 1 of the sweep-high-rows goal, reviewed on request mid-run rather than at
closeout. The unit: reproduce sweep rows S24, S28 and S35, write the shared
repair once, and disposition each row honestly. Three slices remain, and the
contract's midpoint goal-claims review fires after slice 2 — so what this retro
changes has three slices left to apply to.

## Window

From `/goal` activation through commit `faf355f5`, one slice. Two review rounds,
five bounded reviewers. The goal-shaping plan critique that preceded activation
(three more reviewers, commit `7de074c1`) is in scope as context because its
findings are what the slice was built against.

## Evidence Summary

- Commits `7de074c1` (shaped goal + plan critique) and `faf355f5` (the slice).
- `charness-artifacts/critique/2026-08-01-slice-1-absent-input-batch.md` — the
  two-round record, including the round-2 finding that three defects were
  created by round 1's own repairs.
- `charness-artifacts/probe/2026-08-01-adapter-yaml-uninterpreted.json` — the
  measurement, now carrying its own provenance and scope non-claim.
- Host log (`probe_host_logs.py`, claude session scope, thread-wide not
  per-goal): 238 function calls, 23 patch applications, 8 subagent spawns, 0
  context compactions. Proxy signals: `git add` ×5, `git worktree` ×3, no
  repeated broad gates. Token snapshots exist but are point-in-time, not a
  cumulative total, so no token claim is made.
- `mine_closeout_telemetry.py` over 1154 records: the recurring gate-runtime
  finding is the broad `pytest -q -m 'not release_only' …` at 16 occurrences and
  a 475s peak — a standing repo cost this slice did not incur (it ran
  `--skip-broad-pytest` throughout) and did not fix.
- `charness-artifacts/retro/recent-lessons.md` for the trend line.

## Waste

**The stop condition I wrote was violated by the implementation I wrote two
hours later.** The goal's Boundaries say a repair requiring a consumer repo to
change a file it authors stops at legible-plus-deferred. The first S24 repair
armed a hard refusal on `.agents/issue-adapter.yaml`. It was implemented,
tested, mirrored, and committed to the working tree before a reviewer read the
constraint back to me. Cost: one full repair-and-test cycle undone, plus the
tests rewritten to assert the opposite verdict. This is not a case of a missing
rule — the rule was in the artifact, in writing, in the same session.

**Three passes on one 100-line measurement script.** Written to justify arming;
round 1 found it measured this repo's corpus rather than the consumer-authored
population the refusal would govern; round 2 found it was itself a
zero-denominator green (0 files scanned printed a clean 0 and exited 0) and that
`--roots` never actually bounded the scan. The script built to prove "an
unreadable input is not a good one" excluded unreadable files from its own
denominator.

**Four dup-ratchet hard-blocks at the closeout boundary — the same count, and
the same shape, as the 2026-07-31 retro recorded.** Each repair rotated a
fingerprint; each rotation surfaced only when the aggregate ran. The lesson was
in `recent-lessons.md` under Repeat Traps and did not prevent the repeat. Two
cycles produced genuine extractions (`_line_shape`/`_is_ignorable`/
`_mapping_value`, then one unified adapter payload builder); two produced
classifications of unextractable boilerplate.

**Not waste, though it looks like it:** the second review round cost two
reviewers and found five blockers, three of them created by round 1's repairs. A
one-round slice would have shipped a parser change that silently merged YAML
documents. That is the contract earning its cost for the fifth measured time.

## Critical Decisions

- **Withdrawing the S24 arming rather than re-scoping the stop condition.** The
  cheaper move was to declare the condition inapplicable. The 2026-08-01 retro
  names post-hoc criterion weakening as the escape the operating contract
  forbids, so the repair moved instead of the rule. S24 closes NARROWED.
- **Extracting rather than re-baselining the dup families.** Four extractions
  landed; only two families were classified, each with a written reason.
- **Applying the batching lever.** Round-1 reviewers ran concurrently while the
  parent reproduced batches B and C and ran both their arming measurements. That
  is the largest single lever `recent-lessons.md` names, and it was applied
  rather than carried forward again.
- **Saying S24 and S35 are NARROWED.** Both had a defensible CLOSED story. The
  sweep rows now carry what stays open instead, including the admission that
  S35's own repair is an instance of the class the sweep catalogues.

## Trends vs Last Retro

- **Repeat, unchanged:** four dup-ratchet cycles at closeout. Third retro in a
  row to name it; second to name the exact count.
- **Applied, previously carried:** batching independent review rounds while
  doing real work. The prior retro measured 84.6 min of `sleep` against 50.5 min
  of review; this slice had no idle wait.
- **Held:** reproduce → repair → revert-check ran for all three rows, and 13 of
  the first cut's tests were confirmed failing against HEAD in a detached
  worktree. The prior retro flagged this as the contract working; it still is.
- **New:** the first measured instance of round 2 catching defects that round 1's
  own repairs introduced, in a slice where round 1 was itself a three-reviewer
  fan-out. The prior goal measured "the round that read the REPAIRS caught
  something the repair introduced, in all four repair slices" — this makes five.

## Expert Counterfactuals

**Engelbart — treat (H + LAM + T) as one unit; design T alongside LAM.** The
goal artifact's `## Boundaries` stop conditions are tooling in prose form: they
encode exactly the check a gate would run, and nothing reads them. I authored a
constraint and then violated it because the constraint lived only where a human
would notice it. The Engelbart move is not "read the artifact more carefully" —
it is to notice that the goal artifact is already a T-surface with no L. A
`check_goal_stop_conditions.py` that parses the artifact's stop conditions and
asks the slice's own diff whether any of them fired would have caught the arming
before the first test was written. The same shape covers the four dup-ratchet
cycles: `run_slice_closeout.py` already knows which files a slice touched, so the
dup gate could run at the FIRST edit to a gated file rather than at the
aggregate, converting four late blocks into one early one.

**Direct lens on evidence discipline — what would falsify this number?** The
measurement script was designed to support a decision already made, and it took
two review rounds to establish that it measured the wrong population and had no
floor on its own denominator. Neither question is subtle; both are the first two
questions a hostile reader asks. The changed action is small and mechanical:
before a number is cited in a decision, write down (a) the population the
decision governs and whether the number covers it, and (b) what the script
prints when the corpus is empty. Both fit in the script's docstring, which is
where they now are — but they arrived by review rather than by construction.

## Sibling Search

- same layer: `scripts/measure_evidence_residual.py` — the S3 floor's own
  measuring script, the direct sibling | decision: diagnostic-only | proof: ran
  it against an empty `/tmp` repo root; it reports `corpus_established: false`
  and `floor_below_every_measured_minimum: false`, so the state IS legible — but
  it exits 0 and no caller consumes the field, so a clean-looking run over an
  empty corpus still reads as a pass at the exit-code channel
- abstraction up: 50 of 56 repo scripts that enumerate files and report a count
  carry no visible empty-population guard | decision: valid follow-up outside the
  slice | proof: regex census over `git ls-files scripts/*.py
  skills/public/*/scripts/*.py`; this is a LEAD-shaped count, not 50 defects —
  most are validators over changed files where an empty set is correctly a pass,
  and separating "empty because nothing changed" from "empty because the scan
  broke" needs per-script judgment | follow-up: deferred
  `docs/handoff.md` `## Next Session` — carried as a named lead alongside the
  E-cluster, not as a claimed defect count
- specialization down: `scripts/measure_adapter_yaml_uninterpreted.py` | decision:
  same waste, fix now | proof: fixed in this slice — exit 2 with an explicit
  message when the roots resolve to no files, and `--roots` now actually bounds
  the scan
- mental-model siblings: the goal artifact's stop conditions, and any prose
  constraint an agent authors then implements against | decision: valid follow-up
  outside the slice | proof: this session produced one violation of a
  self-authored constraint within two hours of writing it; the Engelbart
  counterfactual above names the missing surface | follow-up: deferred
  `docs/handoff.md` `## Discuss` — needs an operator decision on whether goal
  stop conditions should become machine-readable

## Portable Candidate

- Abstract pattern: a measurement script whose number decides a threshold must
  refuse an empty or unestablished corpus, and must state the population its
  number does and does not cover.
- Triggering evidence: this slice's `measure_adapter_yaml_uninterpreted.py`
  shipped both defects and was caught by review, not construction; the repo's own
  `measure_evidence_residual.py` half-carries the same gap; sweep rows
  S1/S26/S30/S32 are the same class in gates rather than measurements.
- Intended consumer/repo shape: any repo where a checked-in threshold cites a
  script-produced number.
- Destination: not portable yet — one instance plus one half-instance. This repo
  has withdrawn one-instance floors twice; wait for a third before proposing a
  `create-skill` surface.
- First-prompt acceptance claim (for when it does land): "given a measurement
  script and an empty corpus, the run exits nonzero and names the empty
  population."

## Next Improvements

- workflow: run the dup-ratchet at the first edit to a gated file, not only at
  the closeout aggregate. Four late blocks in this slice, four in the last
  session, and the lesson has now failed to prevent itself twice.
- capability: `applied: scripts/measure_adapter_yaml_uninterpreted.py` refuses an
  empty corpus (exit 2) and bounds `--roots`, and its docstring states the
  population its number does not cover — the specialization-down sibling, fixed
  in this slice rather than recorded.
- memory: a self-authored constraint in a goal artifact is not a check. This
  session violated its own stop condition within two hours of writing it, and a
  reviewer, not the author, caught it. Either the constraint becomes machine-read
  or the slice's first move is to read its own goal's Boundaries against the
  planned diff.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-01-slice-1-absent-input-batch-retro.md
