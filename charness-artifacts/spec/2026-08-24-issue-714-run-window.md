# Issue #714 TAP Run-Window Implementation Contract

## Problem

`NodeTestReporter` selected the final TAP summary but applied `exitCode:`
process-failure diagnostics to a window beginning after the previous duration.
Wrapper chatter and incomplete earlier runs could poison a valid later
assertion failure, while a trailing duration-shaped wrapper could be selected
as if it were a TAP run.

## Capability Contract

Node mutation accounting must use one exact selected TAP run: its summary
counts, final plan, top-level result ownership, duration boundary, and
process/module-load diagnostics are one observation. A candidate with missing
verdict-critical keys or inconsistent plan/count structure is unreadable. A
selected run with a process failure remains an error/refusal.

## Current Slice

Repair `scripts/mutation_test_reporters.py`, its checked-in plugin mirror, and
the focused reporter/classifier regressions. Keep the change local to Node TAP
observation ownership; leave the tree uncommitted after the consumed two-round
cap, with post-cap repairs recorded as accepted-unreviewed.

## Fixed Decisions

- `_selected_run()` owns candidate selection and returns the exact run consumed
  by both summary parsing and process-failure matching.
- A valid candidate has a structural TAP start when available, a final `1..N`
  plan, `# tests N`, all verdict-critical summary keys, exactly the plan-owned
  top-level result sequence, and an owned `# duration_ms` line. Compact starts
  derive from the plan and required result records; explicit starts use the
  first structurally valid top-level header in the region.
- `tests == plan`, the critical counts plus optional skip/todo counts account
  for the tests, and missing or duplicate summary keys invalidate the
  candidate. No verdict-critical key defaults to zero.
- A trailing duration-only wrapper is not a candidate; selection walks back to
  the latest complete TAP candidate.
- The existing `min(..., reported_failures)` safety cap and selected-run
  process-failure refusal remain unchanged in policy.
- Pytest parsing, TAP format recognition, and mutation verdict policy are not
  redesigned.

## Probe Questions

- Does the identical final assertion-failure run return `(0, 1, 0)` when the
  prefix is a complete run plus inter-run wrapper `exitCode: 1`? (unit)
- Does it return `(0, 1, 0)` after an incomplete earlier run plus wrapper
  diagnostics? (unit)
- Does a trailing wrapper `# duration_ms 99` leave the valid final run readable?
  (unit)
- Does a selected `_NODE_BROKEN` run still return `errors == 1` and no failed
  assertion? (unit)
- Does compact `not ok` plus `exitCode:` retain the first result rather than
  manufacture a kill from the last result? (unit/classifier)
- Does a later TAP-like header inside one run preserve the earlier diagnostic?
  (unit/classifier)
- Do missing keys, plan/count mismatches, and result/count mismatches refuse?
  (unit/classifier)

## Deferred Decisions

Host-specific Node output variants and installed-plugin replay remain outside
this bounded local lane. Changed-line mutation proof remains a post-commit
operation; this uncommitted slice cannot honestly claim it.

## Non-Goals

Do not weaken process/module-load refusal, change issue state, push, release,
run Cautilus, edit Ceal, invoke installed Charness impl, or touch lesson-session
state. Do not claim provider, host, or installed-plugin behavior from local
fixtures.

## Deliberately Not Doing

Do not count diagnostics from the full transcript or from a region merely after
the previous duration. Do not accept a count-only heuristic that would turn a
module-load failure into a mutation kill.

## Constraints

Preserve source/plugin mirror byte parity. Run focused reporter and
mutate-and-restore tests, compilation, length, packaging, diff hygiene, and
any stronger bounded test earned by the repair. Stop uncommitted; the
two-round cap is consumed and no third review is implied.

## Success Criteria

The compact, explicit-header, and completeness falsifiers refuse or preserve
the correct counts at both reporter and classifier boundaries; the retained
inter-run/incomplete-prefix/trailing-duration cases pass; the selected-run
process-failure control still refuses; focused reporter and
mutate-and-restore tests pass; both copies compile and are byte-identical; the
requested local quality checks pass without new warnings. No commit, push,
GitHub mutation, Cautilus run, or lesson-session mutation occurs.

## Acceptance Checks

- `python3 -m pytest -q tests/quality_gates/test_mutation_test_reporters.py`
  (unit)
- `python3 -m pytest -q tests/quality_gates/test_mutate_and_restore.py` (unit)
- `python3 -m py_compile scripts/mutation_test_reporters.py` (unit)
- source/plugin parity, length, packaging, diff hygiene, and local debug/spec
  validation (manual)

## Boundary Ownership

`NodeTestReporter._selected_run()` owns complete-duration boundary walking and
the selected transcript window. `_candidate_for_region()` owns structural
header/compact start selection; `_validated_run()` owns summary completeness,
plan/result ownership, and count consistency. `read()` derives counts and
`_NODE_PROCESS_FAILURE_RE` matches only inside the same returned run.
`RunCounts.errors` is the signal consumed by mutation accounting.

## Critique

- Round-1 disposition: blocker confirmed. The first repair scoped from a prior
  duration and lacked inter-run chatter, incomplete-prefix, and trailing-
  duration axes; it is superseded, not approved.
- Repair disposition: the candidate owner now requires complete TAP structure,
  keeps counts/diagnostics on one selected string, and refuses the three
  round-2 falsifier families. Focused reporter/classifier tests cover those
  boundaries plus the earlier paired cases.
- Mandatory round 2 status: unproven. The first unnamed spawn delivered no
  findings; the file-backed retry reported no file-reading capability. That is
  a capability non-claim, not an auth failure, and not review proof. Boundary
  verification was clean (`drift: []`, exit 0), which proves tree integrity
  only. The two-round cap is consumed; these post-cap repairs are
  accepted-unreviewed. No third review or same-agent substitute is claimed.
- Honest boundary: local source/tests and local downstream contract are proven;
  host Node variants, installed exports, mutation changed-line proof, and
  external state are not proven.

## Post-Merge Coverage Repair

Fresh base-to-HEAD coverage ran 11,343 standing tests clean but refused seven
uncovered reporter lines. The closeout repair adds semantic controls for a
trailing summary stopping at an earlier duration, duplicate/negative/count-total
summary rejection, valid plan-first compact ownership, and complete/absent
`summary()` outcomes. The count regex accepts a leading minus only so the
existing nonnegative guard can observe and refuse that malformed input; it does
not admit negative counts into a verdict.

## Canonical Artifact

`charness-artifacts/debug/2026-08-24-issue-714.md` records the RCA and review
non-claims; this file is the active implementation contract and accepted-
unreviewed post-cap handoff.

## Closeout Slice

Bind candidate selection, summary parsing, and process diagnostics to the same
complete structural TAP run; retain the selected process-failure refusal;
verify the direct reporter/classifier falsifiers and requested local checks;
stop uncommitted with the changed-line mutation proof and external/plugin
readback explicitly unclaimed.
