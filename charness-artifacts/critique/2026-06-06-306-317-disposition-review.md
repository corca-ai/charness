# Rung-2 Disposition Review + Cross-Slice Closeout — `306-316-open-followups`

Verdict: **CLEAR** — every surfaced improvement is dispositioned and every non-weakening invariant HOLDS in the committed code; the goal is safe to flip to complete and release.

Scope: goal slug `306-316-open-followups`; issues #306, #311, #314, #315, #316, #317
(closed by the release push) and filed follow-up #319. Reviewed read-only against
the 7 commits ahead of `origin/main`
(`a09e6d95`/`ba48808e`/`c688e66c`/`309f7a21`/`4f1adc50`/`bb0ca089`/`54e1b6b1`).
This is a different agent context from the implementers.

## Disposition Verdicts

The retro's `## Next Improvements` surfaced exactly two notes; both are
dispositioned. No undispositioned improvement found.

- **Headroom-buffer improvement — DISPOSITIONED → issue #319 (verified).**
  `gh issue view 319` confirms #319 is OPEN and its body carries the required
  three-part split:
  - **Structural pattern:** "a per-surface buffer/headroom assertion distinct
    from the hard limit runs only in the broad/bundle gate" (the
    `core_nonempty ≤ 160` hard limit vs the separate `remaining ≥ 4` buffer test).
  - **Triggering instance(s):** the 2026-06-06 `306-316-open-followups` slice #316
    compressing `achieve/SKILL.md` to exactly 160, caught by
    `test_achieve_root_uses_reference_index_with_core_headroom`, fixed in
    `54e1b6b1`; explicitly generalizes #308 and #314.
  - **Destination:** "charness (quality-gate economics / commit-boundary checker
    set + #308 authoring-preflight reference)."
  The goal's `## Off-Goal Findings` and `## Auto-Retro` "Retro dispositions:" both
  bind this to #319. Honest filing, not an in-session hand-wave (the issue notes
  it needs the per-slice-cost design the #307/#314 caution flags).

- **"memory" note — DISPOSITIONED as `applied: n/a (no second item)`; HONEST,
  not a dodge.** The retro's second `## Next Improvements` bullet is a *memory*
  note: "recon-derived gotchas about which paths are mirrored can be
  repo-inaccurate (`scripts/` is mirrored to `plugins/charness/scripts/`)." The
  retro itself states the standing "re-verify the brief against real files"
  instruction already absorbed this, and the `## Sibling Search` decision is
  explicit: "file **one** tracked issue." This is a genuinely non-actionable
  observation, not a real second improvement left undispositioned — there is no
  gate/test/code artifact to build for it that the existing standing instruction
  does not already cover. The `applied: n/a (no second item)` framing is
  accurate.

## Non-Weakening Invariants

- **#315 — placeholder-only artifact CANNOT pass the complete-evidence gate —
  HOLDS (highest-risk invariant).**
  `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py:88` defines
  `_PLACEHOLDER_MARKER = re.compile(r"^(?:(?:TODO|TBD|FIXME)\b|<[^>\n]*>)", IGNORECASE)`;
  `is_placeholder_value` (line 91) and the `elif is_placeholder_value(raw_value):
  continue` branch in `parse_closeout_evidence` (lines 203–207) DROP a placeholder
  value so the evidence name falls back to `missing`. The diff confirms these
  lines are NEW this run (added in `4f1adc50`), not pre-existing. The end-to-end
  test `test_placeholder_only_artifact_cannot_pass_complete_evidence_gate`
  (`tests/quality_gates/test_goal_disposition_gate.py:388`) asserts
  `report["ok"] is False` with `missing == {retro_artifact, host_log_probe,
  disposition_review}`, and `test_auto_retro_placeholder_reads_as_blank_keeping_rung_1a_live`
  (line 408) confirms the seeded `Retro dispositions: TODO …` still reads as blank
  so rung-1a stays live. Placeholders are REJECTED, not silently accepted.

- **#306 — changed-line mutation gate still BLOCKS uncovered changed lines —
  HOLDS.** `scripts/mutation_changed_files_lib.py` has NO diff in this bundle:
  `classify_changed_line_scope_gap` (line 33) still appends a path to the blocking
  `gaps` list when `changed & missing` or when the file is untracked — unchanged
  and not demoted to advisory. The non-weakening test
  `test_changed_line_gate_still_blocks_genuinely_uncovered_line`
  (`tests/quality_gates/test_scaffold_changed_line_coverage.py:97`) is a real
  pure-library assertion: a changed statement line absent from the executed set
  must remain in the blocking set (`assert path in blocking`). The #306 fix raises
  coverage honesty (`tests/test_scaffold_inprocess_coverage.py` drives the
  previously subprocess-only happy + validator-fallback branches in-process); it
  does not weaken the gate.

- **#314 — per-slice aggregate and the literal pre-commit hook run the SAME fast
  subset; no existing gate dropped — HOLDS.**
  `scripts/staged_commit_gate_plan.py` introduces a single source of truth
  `FAST_SURFACE_VERIFY_COMMANDS` (validate-skill-ergonomics +
  check-boundary-bypass-ratchet) and appends `fast_surface_verify_gates(...)` to
  `staged_commit_gate_plan`. The aggregate
  (`scripts/run_slice_closeout.py:36–37`) imports and runs that same plan via
  `run_predict_commit`, so both commit-boundary paths draw the identical subset.
  The diff shows the mirror-drift gate was only REFACTORED into
  `_mirror_drift_gates` (same prefixes, same behavior) — not removed; all prior
  gates (`check-staged-reversion`, `py_compile`, `check-python-lengths`,
  `validate-attention-state-visibility`, `staged-plugin-mirror-drift`,
  `check-doc-links`, `check-markdown`, the validate-* domain gates) remain.
  `test_precommit_plan_agrees_with_aggregate_fast_subset_for_skill_change`/`_for_test_change`
  and `test_fast_surface_verify_allowlist_keys_exist_in_some_surface` pin the
  agreement and guard against silent drift.

- **#311 / #317 — setup inspector REPORTS, never mutates existing AGENTS.md —
  HOLDS.** #311 appends `"reviewer tier and concrete spawn fields"` to
  `FRESH_EYE_COMPACT_REQUIRED_SNIPPETS` so a pre-#303 body is FLAGGED stale. #317's
  `scripts/setup_commit_discipline_lib.py` `detect_commit_discipline_policy` only
  *appends a finding* (`commit_discipline_drift`, `review_required`) when a
  goal-routed body lacks the rule; it returns `(state, findings)` and touches no
  file. The greenfield `COMMIT_DISCIPLINE` block is seeded ONLY through
  `render_agents_template` (new-body path). The test
  `test_setup_commit_discipline.py:102` asserts
  `(repo / "AGENTS.md").read_text() == body` (byte-identical after inspection),
  and `test_setup_inspect_policy.py:375` documents the never-rewrite contract.

- **#316 — NO fragile deterministic word-list gate added; approval-boundary rule
  present in all three surfaces — HOLDS.** The phase-scoped external-side-effect
  rule lands in `skills/public/achieve/SKILL.md` (During step), in
  `references/lifecycle.md` (two sections: "External-side-effect approval is
  phase-scoped" + the Slice-Boundary Continuation paragraph), and in
  `scripts/goal_artifact_template.md` `## Boundaries` ("External side-effect
  scope"). `test_external_side_effect_approval_is_phase_scoped`
  (`tests/quality_gates/test_achieve_before_activation.py`) asserts the rule in
  all three surfaces AND, at its tail, that NO new gate was added
  (`publication_approval_carryforward` / `carry_forward_approval_gate` absent from
  every `scripts/*.py`). Prose + template only, matching the Non-Goal.

## Cross-Slice Drift

None. The two slices that share the achieve template (S5/#315 placeholders,
S6/#316 Boundaries) compose cleanly: #315 seeds `Retro: TODO …` /
`Host log probe: TODO …` / `Disposition review: TODO …` under `## Final
Verification` plus `Retro dispositions: TODO …` under `## Auto-Retro`, and #316
adds `## Boundaries` "External side-effect scope" — disjoint regions, both
present in the committed template. The two setup slices (S3/#311 reviewer-tier
snippet, S4/#317 commit-discipline) extend the same inspector additively
(separate finding types, separate snippet sets) with no overlap. The #316
compression that breached the `core_nonempty` headroom buffer was caught by the
broad `--release` gate and repaired in `54e1b6b1` (core 160→155); the current
`skills/public/achieve/SKILL.md` is 161 lines with 5 lines of buffer — consistent
with `remaining >= 4`. The `plugins/charness` mirror is in sync for every edited
`skills/` and `scripts/` path (diff-verified: achieve SKILL.md/lifecycle.md/
template/closeout-evidence, setup agent-docs-policy/default-surfaces, and the
three edited `scripts/*.py`). No bare `#NNN` issue anchors exist under
`skills/public|shared|support` (grep returned 0).

## Honesty Check

The goal's `## Final Verification` non-claims are accurate, not over-claiming:

- "#306 left the coverage *config* unchanged … the driver was uncovered branches,
  fixed via in-process tests" — confirmed: no diff to mutation-coverage config;
  the fix is the new in-process test module.
- "#316 is prose+template only — it cannot enforce that an agent applies the rule
  at runtime" — accurate; the no-new-gate assertion proves nothing enforces it
  deterministically, which is the intended bound.
- "the broad pytest ran once at closeout, not per slice (by gate design)" —
  consistent with the per-slice/aggregate boundary that intentionally excludes
  broad pytest.
- "#306 durable effect … only fully observable over subsequent scheduled cron
  runs — recorded as a non-claim" — correctly NOT asserted as proven in-session.
- The S8 release/CI proof is marked "pending at the moment of writing" and bound
  under Coordination Cues; the artifact does not pre-claim a green CI it has not
  yet observed. Honest.

## Material Findings

none.
