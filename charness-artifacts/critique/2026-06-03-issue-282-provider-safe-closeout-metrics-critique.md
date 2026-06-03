# Resolution Critique: #282 Provider-Safe Goal Closeout Metrics

Date: 2026-06-03

Fresh-Eye Satisfaction: bounded general-purpose subagent (read-only, shared worktree)

## Scope

- Issue: #282 (Make goal closeout metrics and evidence provider-safe)
- Classification: feature (closeout/retro enhancement)
- Reviewed change: deterministic goal-window recording, standardized provider-safe
  measured-vs-proxy closeout renderer, broad-gate attestation hook, and the
  non-blocking closeout attention signal.
- Files: `scripts/goal_metrics_render_lib.py`,
  `skills/public/retro/scripts/probe_host_logs.py`,
  `skills/public/achieve/scripts/goal_metric_window_lib.py`,
  `skills/public/achieve/scripts/record_metric_window.py`,
  `skills/public/achieve/scripts/goal_artifact_lib.py`,
  `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`,
  `skills/public/achieve/SKILL.md`,
  `skills/public/achieve/references/goal-artifact.md`,
  `skills/public/retro/SKILL.md`,
  `tests/quality_gates/test_goal_metrics_render.py`,
  `tests/quality_gates/test_record_metric_window.py`.

## Verdict

SHIP-WITH-FIXES → fixes folded; now SHIP.

## Blocker Folded

- **Recurrence was not prevented (the issue reported `status: absent` twice).** The
  first implementation made window recording *possible* (`record_metric_window.py`)
  and *loud at read time* (the rendered block says "ABSENT"), but no closeout gate
  surfaced an absent window, so the same operator could forget a third time. Fixed
  by adding a presence-only, **non-blocking** `metric_window` attention signal to
  `check_complete_evidence` (`recorded` / `incomplete` / `absent`), surfaced by
  `check_goal_artifact.py` at flip-to-complete. It never gates the flip because a
  host that legitimately lacks timestamps records the documented `unavailable`
  case. Pinned by the differential test
  `test_absent_window_is_surfaced_at_closeout_but_never_gates_the_flip` (the
  highest-value missing test the reviewer named).

## Over-Worry Dismissed (counterweight)

- **Provider safety "only by convention":** dismissed — it is structural. The
  attestation renderer has no `command` field, and `_safe_field` flattens a pasted
  command blob to a single result line (pinned by a test). The renderer emits only
  counts, aggregated family labels, and the gate/outcome/state_ref triple.
- **`shlex.quote` vs probe `shlex.split` round-trip for paths with spaces:**
  dismissed — verified to round-trip to `parsed`.
- **`_load_sibling` re-export in repo / exported `plugins/` / test-by-file-spec
  layouts:** dismissed — the reviewer ran the exported CLI and confirmed all three.
- **Module extraction as gratuitous splitting:** dismissed — `goal_artifact_lib.py`
  was at the `check_python_lengths` 360-code-line gate; the split is required.

## Non-Blocking Note Accepted As-Is

- `goal_metric_window_lib` uses plain (non-fence-masked) search deliberately, to
  mirror the probe reader so the artifact written is exactly the one the probe
  scores. The realistic risk (a fenced example line in a real goal artifact) is low
  because the goal template carries no fenced example; the module docstring records
  the rationale.

## Binding

- Issue #282 is bound by this artifact's basename and the issue-number references
  throughout. Deterministic gates own closeout (cautilus `run_mode: ask`,
  `next_action: none`); no live cautilus run was made.

## Blockers

- None remaining.
