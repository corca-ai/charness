# Recent Retro Lessons

## Current Focus

- Closeout review of the `2026-06-06-306-316-open-followups` achieve goal: resolve six open follow-ups (#306, #311, #314, #315, #316, #317) via a sequential dynamic workflow, then a release. (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)
- Release publish triggered a configured automatic session retro for `v0.24.0`. (source: `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`; sources: 9)
- **Minor:** a markdown inline-code span wrapped across a line in `lifecycle.md`, caught by `check-markdown` in the same broad-gate failure as the anchors. (source: `charness-artifacts/retro/2026-06-06-318-319-closeout.md`)
- **Minor (gate caught it early):** slice 1's first edit pushed `staged_commit_gate_plan` to 105 lines (limit 100); `check_python_lengths` at the predict-commit boundary caught it, forcing a clean extract-helper refactor. Working as intended — the cheap boundary gate paid for itself. (source: `charness-artifacts/retro/2026-06-06-318-319-closeout.md`)
- **Minor:** the #314 slice-spec gotcha I wrote ("scripts/ needs no mirror sync") was wrong — `scripts/staged_commit_gate_plan.py` is mirrored to `plugins/charness/scripts/`, so the agent had to run the sync. The agent caught it and recorded the correction as a non-claim. My recon-derived gotcha was repo-inaccurate; the agent's re-verify instruction saved it. (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`; sources: 9)
- **memory:** recon-derived "gotchas" about which paths are mirrored can be repo-inaccurate — `scripts/` is mirrored to `plugins/charness/scripts/`, not only `skills/`. The standing "re-verify the brief against real files" instruction already absorbed this; no separate gate needed. (source: `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`)
- **memory:** the authoring-preflight "portable skill packages" section already names the issue-anchor trap; this run is another instance, carried into `recent-lessons.md` by this retro. (source: `charness-artifacts/retro/2026-06-06-318-319-closeout.md`)
- **workflow:** after editing skill-package references/scripts/JSON, run the cheap `run_slice_closeout.py --predict-commit` aggregate (which already runs `validate_skill_ergonomics` + `check-markdown`) *before* the full broad gate — the documented mutate→sync→verify rhythm (verify = the aggregate, not the broad gate). The teeth and the doc already exist; the gap was the habit. (source: `charness-artifacts/retro/2026-06-06-318-319-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-19-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-22-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md`
- `charness-artifacts/retro/2026-06-06-318-319-closeout.md`
- `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`
