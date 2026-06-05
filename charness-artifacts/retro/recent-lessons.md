# Recent Retro Lessons

## Current Focus

- Closeout review of the `2026-06-06-306-316-open-followups` achieve goal: resolve six open follow-ups (#306, #311, #314, #315, #316, #317) via a sequential dynamic workflow, then a release. (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)
- Closed the active 2026-06-05 quality/test-economics goal after the v0.18.0 release. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`; sources: 7)
- **Minor:** the #314 slice-spec gotcha I wrote ("scripts/ needs no mirror sync") was wrong — `scripts/staged_commit_gate_plan.py` is mirrored to `plugins/charness/scripts/`, so the agent had to run the sync. The agent caught it and recorded the correction as a non-claim. My recon-derived gotcha was repo-inaccurate; the agent's re-verify instruction saved it. (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)
- **The single real defect slipped past the in-workflow review and was caught only by the main-loop broad gate.** The 4-dimension fresh-eye review returned 0 findings, yet `--release` immediately failed: #316's slice compressed `achieve/SKILL.md` to *exactly* the 160 core-nonempty hard limit (0 headroom), which `test_achieve_root_uses_reference_index_with_core_headroom` rejects (requires ≥4 buffer). The per-slice gate (`run_slice_closeout --predict-commit`) excludes broad pytest by design, and the review agents did not run the broad suite either — so a deterministic, already-existing test caught a regression that no slice-boundary check did. The bundle gate is the *correct* safety net and it worked, but the authoring agent satisfied the hard length gate while missing the separate headroom-buffer test. This is the #308 authoring-preflight lesson recurring on a *different* length surface (SKILL.md core headroom, not `check_python_lengths`). (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)
- A sync command was accidentally run while the release-inclusive quality wrapper was still reading generated plugin paths. That created a transient `check_current_pointer_writes` FileNotFound. The gate passed on a stable post-sync rerun, but the overlap was avoidable. (source: `charness-artifacts/retro/2026-06-05-3h-code-quality-bugfix.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`; sources: 7)
- **memory:** recon-derived "gotchas" about which paths are mirrored can be repo-inaccurate — `scripts/` is mirrored to `plugins/charness/scripts/`, not only `skills/`. The standing "re-verify the brief against real files" instruction already absorbed this; no separate gate needed. (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)
- **workflow / capability:** the SKILL.md `core_nonempty` headroom-buffer test (`remaining ≥ 4`) runs only in the broad gate, not at the commit boundary, so authoring a SKILL.md to the hard 160 limit passes the per-slice gate and fails late. Generalizes #308 (authoring preflight) and #314 (cheap structural gates at the commit boundary) to the SKILL.md core-headroom surface. Disposition: filed as a tracked issue (larger than this goal's scope; needs the per-slice-cost design the #314/#307 caution flags). → see Auto-Retro disposition for the issue number. (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)
- before editing any SKILL.md surface, check `recent-lessons.md` and grep for a per-skill budget test (`test_<skill>_skill_md_budget`) — both bit this run. (source: `charness-artifacts/retro/2026-06-05-quality-scaffold-and-testability-followups.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-19-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-3h-code-quality-bugfix.md`
- `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`
- `charness-artifacts/retro/2026-06-05-quality-scaffold-and-testability-followups.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-22-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`
