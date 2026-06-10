# Next-queue goal activation plan critique
Date: 2026-06-10

## Decision Under Review

Activation of `charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md`
(three slices: push/release-lane verification, #346 Claude-host metric scoping,
#348 portable hotl skill) before slice execution locks in.

## Failure Angles

- Slice 2 could implement the mechanism the issue body describes instead of the
  mechanism the code actually has, shipping a green-but-wrong fix.
- Slice 2's named surfaces could be the thin CLI wrappers rather than the
  libraries that own the behavior, mispricing the slice and misaiming
  mirror-sync verification.
- Timebox compression: slice 3 was priced as the big slice, but slice 2 needs a
  new Claude session auditor.
- Slice 1 could re-record an already-retired deferred proof as still pending.

## Counterweight Pass

- Real blockers: the slice 2 mechanism premise (B1) and surface set (B2) —
  folded into the goal artifact before slice 2 design.
- Over-worry (raised, dismissed with evidence): the lane might be red (verified
  green: quality-core 27264481707 on fd3c2c6c; v0.38.0 published; the one
  cancelled run is normal supersede-cancellation); `../ceal` drifting from the
  pinned permalink (verified zero diff since `70170c5`); `hotl` package
  collision (does not exist; `hitl` relationship is a named boundary); #347
  carrier-slip repeat (no issue filing in this goal; validate-closeout-draft
  gates each carrier).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/goal_metrics_render_lib.py:101 | action: fix | note: B1 — the misattributed measured block is a STALE CODEX rollout (newest-by-mtime under ~/.codex/sessions, 2026-06-05) rendered on a Claude-host run, not a Claude project-dir aggregate; probe_claude already picks a single newest file and counts nothing. Slice 2 = Claude-format single-session audit + host/staleness disambiguation in the render path; #346 closeout draft must state the corrected root cause.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/host_log_probe_lib.py:332 | action: fix | note: B2 — true owner surfaces are host_log_probe_lib.py, goal_metric_window_lib.py, goal_metrics_render_lib.py, a new Claude audit module, the plugins/charness/scripts/ mirrors, and the three existing test modules; the goal's named surfaces were the thin CLI shims.
- F3 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md | action: fix | note: pre-name a slice-2 deferral seam (land misattribution fix + Claude single-session measured block; defer window-filtered goal_window_audit parity with an honest non-claim) so a timebox squeeze produces a staged v1, not an improvised cut.
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md | action: fix | note: mutation-tests run 27261418055 (07:48Z) over 39ff5432 is green — the carried deferred proof is retired; the residual deferred check targets fd3c2c6c only. (Already recorded this way in the slice 1 log.)
- F5 | bin: over-worry | evidence: strong | ref: ../ceal/.agents/skills/close-loop/SKILL.md | action: defer | note: ceal reference drift — verified byte-stable since the pinned permalink revision 70170c5; no action.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: fresh-eye bounded subagent reviewer (repo-contract pre-approved scope), read-only in the shared parent worktree.
- Requested spawn fields: subagent_type=general-purpose, name=plan-critique, run_in_background=true, prompt carrying the goal path, read-only constraints, and the structured verdict shape.
- Host exposure state: applied
- Application state: host-confirmed: background agent completed with a structured PROCEED-WITH-ADJUSTMENTS verdict (24 tool uses, 320s) returned via task notification.

## Fresh-Eye Satisfaction

Reviewer verdict: PROCEED-WITH-ADJUSTMENTS — four adjustments (B1 mechanism
restatement, B2 surface set, pre-named slice-2 deferral seam, slice-1
deferred-proof re-aim), all folded into the goal artifact before slice 2
design; goal shape, ordering, non-goals, and external-side-effect scope
confirmed against ground truth (local main == origin/main, lane green, ceal
reference pinned).
