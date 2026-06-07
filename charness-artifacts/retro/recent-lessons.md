# Recent Retro Lessons

## Current Focus

- `achieve` goal: split `scripts/run_slice_closeout.py` (474/480, in the length warn band) into the orchestrator plus a cohesive reporting module, behavior-preserving, with the plugin mirror byte-synced. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- Activated and ran the shaped achieve goal `2026-06-07-332-commit-boundary-sweep-enforcement` end to end. (source: `charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`; sources: 11)
- **One avoidable gate failure cost a second full read-only gate run (~45s).** I hand-wrote the critique artifact and omitted the `## Reviewer Tier Evidence` section that `validate_critique_artifacts` requires; the gate caught it, I added the section, and re-ran the whole gate. Root cause: the critique skill's documented path produces a *prepare packet* with the reviewer-tier shape but does not route final-artifact authoring through `scaffold_critique_artifact.py` (the scaffold exists but no `SKILL.md`/reference cites it), so a hand-author can miss validator-required sections. Low-severity, but repeatable. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- Otherwise low waste: the byte-preserving migration script and pre-captured baselines made the proof cheap and unambiguous on the first pass. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- **A deterministic-gate blind spot.** `run_slice_closeout --skip-broad-pytest` (run first, green) does NOT run `check_spec_evidence_durability` (it is a broad-pytest test), so the spec-citation miss only surfaced at minute 6 of run1. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`; sources: 11)
- **capability:** The critique skill's prepare-packet path and the `scaffold_critique_artifact.py` scaffold are disconnected; the scaffold is uncited in `SKILL.md`/references. Candidate follow-up: cite the scaffold from the critique skill (or have prepare-packet emit an artifact stub with the required headings) so the validator-required shape is present by construction. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- **memory:** Persisted to recent-lessons (below) so the next critique author does not relearn the reviewer-tier-evidence requirement. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- **workflow:** When authoring a charness critique artifact, check `validate_critique_artifacts` required sections (or run `scaffold_critique_artifact.py`) BEFORE hand-writing — `## Reviewer Tier Evidence` with 4 fields and a host-exposure-state from the fixed set is mandatory. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)

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
- `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`
- `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`
