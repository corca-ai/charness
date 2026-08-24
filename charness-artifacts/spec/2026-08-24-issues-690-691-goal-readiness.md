# Issues #690/#691 — Goal Readiness Implementation Contract

Date: 2026-08-24

## Current Slice

Repair the shared achieve readiness producer and its public CLI payload so
terminal goal records, active hollow shaping records, and duplicate required or
portability H2 sections cannot be offered for pursuit. Keep the source skill and
checked-in plugin export aligned through the canonical packaging sync.

## Fixed Decisions

- #690 and #691 are one fix unit at the pursue-readiness producer/consumer seam;
  #698 is outside this slice.
- Leading-token terminal statuses (`complete` and `superseded`, including
  annotations) force both `pursue_ready` and `activation_ready` false.
- Hollow shaping sections are evaluated for active work. Shaping sections block
  active pursuit; legitimate run-filled empty sections remain reported but do
  not block, and terminal records are refused by lifecycle status rather than
  mislabeled as hollow blockers.
- The CLI early-return report exposes typed lifecycle/refusal state so a final
  consumer does not infer terminal or hollow refusal by grepping prose.
- Required and portability H2 duplicate detection has one owner in
  `goal_artifact_markdown.required_heading_report`; readiness consumes its
  duplicate names and publishes a typed `duplicate_sections` blocker. Full
  validation and `--pursue-ready` therefore refuse the same substantive
  duplicate heading.
- Lifecycle token normalization and terminal/shaping applicability are owned by
  `skills/public/achieve/scripts/goal_artifact_lifecycle.py`; the pursue module
  re-exports its established public names for compatibility, and the plugin
  mirror carries the same owner through canonical packaging sync.
- `shape_ready` keeps its existing narrow placeholder meaning.

## Success Criteria

1. Terminal, active-hollow, and substantive duplicate-heading fixtures produce
   false readiness with explicit typed state and actionable reasons.
2. A superseded fixture proves full validation and pursue readiness agree on
   the terminal permission boundary for both missing and valid successor
   records; a valid record supplies traceability, never pursuit permission.
3. Source and checked-in plugin CLI invocations emit consumer-compatible,
   parity-equivalent readiness payloads.
4. Focused tests cover the four smallest proof fixtures and existing achieve
   behavior remains green.

## Acceptance Checks

- Focused achieve readiness, hollow, superseded, and CLI parity tests pass.
- Required and portability duplicate-heading regressions pass through source and
  plugin public checker CLIs, with full-validation/readiness agreement proven.
- Source/plugin mirrors are regenerated with
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and show no
  drift.
- Artifact validation, changed-line coverage for actual changed paths, and the
  fast packaging/bootstrap gates required by `impl`/`prove` pass or are
  explicitly recorded as unavailable/failed.
- No GitHub issue mutation, Cautilus evaluation, push, or commit is performed
  in this slice.

## Non-Claims

- This does not prove `/goal` host activation, Ceal mutation, hosted/public
  readback, or issue closure.
- This does not change #698 or broaden `shape_ready` into full lifecycle
  readiness.
- Full validation remains an artifact-contract check; a valid terminal record
  is not thereby activation-authorized.
- The two-round fresh-eye cap is consumed. The duplicate-heading repair is
  accepted-unreviewed under that cap; no third fresh-eye approval is claimed.
- The earlier round-2 packet was generated with `changed_ref: HEAD`, which
  resolved to the old committed content and left untracked reviewed paths with
  null hashes. It does not cover this repaired working tree. The parent must
  regenerate a working-tree-bound packet after this repair.

## Deferred Decisions

- Any Ceal-side status-gate change remains outside this Charness source/plugin
  slice; only the shared public payload contract is repaired here.
- The earlier reviewer packet measured `goal_artifact_pursue.py` at 339 code
  lines in the advisory band. The current working tree measures 355 after this
  small blocker addition and remains below the hard limit; the
  reviewer-identified Closeout Binding Plan parsing is still a separable concept
  for a later `goal_artifact_closeout_plan.py` extraction. That refactor is
  deferred to parent issue tracking and is not part of this capped repair; no
  line-shaving or extraction claim is made here.
