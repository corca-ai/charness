# 346 Claude metric scoping slice critique
Date: 2026-06-10

## Decision Under Review

Slice 2 of the 2026-06-10 next-queue goal: Claude-host per-goal metric scoping
for goal-closeout metrics (issue 346), before its direct-commit carrier locks
in — a new Claude single-session auditor, dual-key `Host metric window:`
grammar, render-path host/staleness disambiguation, and a Claude window source
for the recorder.

## Failure Angles

- The freshest-session fallback could misorder hosts and re-create the
  misattribution symmetrically (stale session presented as the measured block).
- The dual-key window grammar could break existing codex-keyed windows or admit
  ambiguous dual-host lines.
- Payload-key consumers elsewhere (closeout evidence, docs, validators) could
  still read the old single-key contract.
- Reference docs could keep teaching the codex-only grammar, leaving the new
  Claude path undiscoverable.

## Counterweight Pass

- Real blocker: B1 — `last_event_at` was dropped by the codex session-audit
  summary, so a stale Claude session would ALWAYS win the thread-wide fallback
  on a machine with both hosts (proven live by the reviewer with a fake home).
  Fixed in the same slice: the summary passes `last_event_at` through, the
  renderer compares chronologically (undated loses, ties keep codex), and two
  probe-to-render integration tests pin both directions.
- Folded nits: stale window-grammar docs updated (achieve goal-artifact +
  lifecycle, retro phase-aware-efficiency); `metric_window_attention` now
  flags a dual-host line as incomplete instead of recorded.
- Deferred (recorded, low risk): a named-but-missing `--claude-session-file`
  override also suppresses an independently valid claude-keyed
  `goal_window_audit`; honest-unavailable wins for v1.
- Over-worry (reviewer-dismissed with evidence): tie-break direction
  (cross-host exact ties practically impossible); shlex/quoting edges
  (pre-existing behavior, quoted paths handled); other payload-key consumers
  (none parse the window line or host payload keys; attention vocabulary
  unchanged).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/host_log_probe_lib.py | action: fix | note: B1 — codex session-audit summary dropped last_event_at so claude always won the dual-host thread-wide fallback; fixed with pass-through + chronological compare + two probe-to-render integration tests (fresh-codex-wins and fresh-claude-wins).
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/references/goal-artifact.md | action: fix | note: N1 — three reference docs taught the codex-only window grammar; updated to the exactly-one-host-key grammar with both recorder invocations.
- F3 | bin: act-before-ship | evidence: moderate | ref: skills/public/achieve/scripts/goal_metric_window_lib.py | action: fix | note: N2 — a hand-edited dual-host window line read as recorded at closeout attention while the probe rejects it as ambiguous; attention now reports incomplete.
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/host_log_probe_lib.py | action: document | note: N3 — a named-but-missing claude session override also suppresses an independently valid claude-keyed goal_window_audit; never-substitute honesty wins for v1, recorded in the slice log.
- F5 | bin: over-worry | evidence: strong | ref: scripts/goal_metrics_render_lib.py | action: defer | note: tie-break direction and sub-second lexical-compare worries; chronological parsing folded with B1, exact cross-host ties practically impossible, codex-on-tie keeps codex-only hosts byte-stable.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: fresh-eye bounded subagent reviewer (repo-contract pre-approved scope), read-only in the shared parent worktree.
- Requested spawn fields: subagent_type=general-purpose, name=slice2-critique, run_in_background=true, prompt carrying the full slice packet (intent, changed files, invariants, proof, non-claims, out-of-scope, reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: background agent completed with a structured HOLD verdict (19 tool uses, 274s) returned via task notification, including a live reproduction of the B1 misordering.

## Fresh-Eye Satisfaction

Reviewer verdict: HOLD on one concrete blocker (B1, with live reproduction);
B1 fixed in-slice with the reviewer-prescribed payload pass-through plus
integration tests pinning both fallback directions, N1/N2 nits folded, N3
recorded as a deliberate v1 trade, and the resulting suite (47 related tests)
green before the carrier commit. The reviewer confirmed the dual-key parse,
never-substitute posture, provenance line, codex byte-preservation, and the
codex-side window-scoping guard against the diff and live execution.
