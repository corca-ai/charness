# Focused Mutation Coverage Producer Critique

## Execution

Fresh-eye code critique executed for the producer-speed slice before final
closeout. Target reference: `code-critique`.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

charness-artifacts/critique/2026-06-15-213551-packet.md

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `requested_fields_sent`
- **Application state**: `unverified-by-host`

## Diff Scope

`run_slice_closeout.py --produce-mutation-coverage` now accepts
`--mutation-coverage-command`. Without the new flag, the old broad-pytest
producer path remains. With the flag, broad pytest stays on the ordinary closeout
proof/cache path and the explicit focused pytest command alone is instrumented to
produce `reports/mutation/test-coverage.json` and its freshness fingerprint.

## Findings

- Michael Jackson angle: found a plan-only validation bypass and a wording issue.
  Fixed by moving producer argument validation before the plan-only return path
  and by updating the lock/skip wording.
- Gerald Weinberg angle: found stale plugin export and missing invalid-command
  regression coverage. Fixed by adding the pytest-shape guard test and rerunning
  `sync_root_plugin_manifests.py`.
- Atul Gawande angle: found focused command unsafe-command bypass, stale quality
  evidence, and untracked critique packet risk. Fixed by including the focused
  command in the unsafe blocker input, moving runner behavior tests to the runner
  surface, and keeping the critique packet/artifacts in the commit.
- Counterweight: confirmed the validation, plan-only, unsafe-command, and plugin
  export findings were resolved. Remaining `run_slice_closeout.py` size pressure
  is valid to defer; artifact/quality finalization is parent-owned closeout work.

## Structured Findings

- plan-only-validation | bin: act-before-ship | evidence: strong | ref: scripts/run_slice_closeout.py | action: fix | note: Focused producer misuse could be planned even though execution would reject it; fixed by centralizing producer validation and running it before plan-only output.
- unsafe-focused-command | bin: act-before-ship | evidence: strong | ref: scripts/run_slice_closeout.py | action: fix | note: Focused producer commands were outside the normal command plan and therefore outside unsafe-command scanning; fixed by adding them to the blocker input before execution.
- plugin-export-sync | bin: act-before-ship | evidence: strong | ref: plugins/charness/scripts/mutation_coverage_producer.py | action: fix | note: The plugin mirror initially lagged the new pytest-shape guard; reran sync and verified root/plugin copies.
- quality-evidence-refresh | bin: act-before-ship | evidence: strong | ref: charness-artifacts/quality/latest.md | action: fix | note: The previous quality artifact still recorded the 462.9s broad-coverage producer path; refreshed it with the focused producer closeout evidence.
- runner-size-pressure | bin: valid-but-defer | evidence: moderate | ref: scripts/run_slice_closeout.py | action: defer | note: The runner module is near its advisory length limit and main is exactly 100 lines; this slice kept new logic in helpers, and the next runner touch should extract producer planning/validation. | follow-up: deferred run-slice-closeout-producer-split

## Defect Class Cross-Link

The main repeat trap was proof drift: a successful implementation could still
ship stale evidence if the quality artifact and critique packet were not folded
into the same commit. The slice records both finalization artifacts before
closeout.

## Capability Gap

None.

## Pre-Merge Action

No critique blocker remains. Final closeout must include the refreshed quality
artifact and this critique artifact.
