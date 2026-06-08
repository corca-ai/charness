# Recent Retro Lessons

## Current Focus

- `achieve` goal: split `scripts/run_slice_closeout.py` (474/480, in the length warn band) into the orchestrator plus a cohesive reporting module, behavior-preserving, with the plugin mirror byte-synced. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- Ran the achieve goal `2026-06-08-authoring-preflight-and-disposition-delaunder` end to end: generalize the author-time shape preflight across the artifact- authoring validator family, and de-launder the disposition escape — to structurally close the recurring "authoring-preflight skip" loop instead of filing its N-th narrow instance. (source: `charness-artifacts/retro/2026-06-08-authoring-preflight-and-disposition-delaunder.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`; sources: 12)
- **One avoidable gate failure cost a second full read-only gate run (~45s).** I hand-wrote the critique artifact and omitted the `## Reviewer Tier Evidence` section that `validate_critique_artifacts` requires; the gate caught it, I added the section, and re-ran the whole gate. Root cause: the critique skill's documented path produces a *prepare packet* with the reviewer-tier shape but does not route final-artifact authoring through `scaffold_critique_artifact.py` (the scaffold exists but no `SKILL.md`/reference cites it), so a hand-author can miss validator-required sections. Low-severity, but repeatable. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- Otherwise low waste: the byte-preserving migration script and pre-captured baselines made the proof cheap and unambiguous on the first pass. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- **A deterministic-gate blind spot.** `run_slice_closeout --skip-broad-pytest` (run first, green) does NOT run `check_spec_evidence_durability` (it is a broad-pytest test), so the spec-citation miss only surfaced at minute 6 of run1. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`; sources: 12)
- before committing a slice that touches `run_slice_closeout`/structural-sweep wiring, run the broad `surface_obligations` suite first — the Slice-3→4 reversal (the validate-all trio's `commit_boundary` True→False) was caught late by the broad gate, not at the slice commit. Disposition: applied: persisted to recent-lessons this run (the next-time checklist) so the precondition is workflow signal, not memory. (source: `charness-artifacts/retro/2026-06-08-authoring-preflight-and-disposition-delaunder.md`)
- **capability:** The critique skill's prepare-packet path and the `scaffold_critique_artifact.py` scaffold are disconnected; the scaffold is uncited in `SKILL.md`/references. Candidate follow-up: cite the scaffold from the critique skill (or have prepare-packet emit an artifact stub with the required headings) so the validator-required shape is present by construction. (source: `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`)
- extend the author-time preflight to the goal-closeout / coordination-floor surfaces — this run discovered the closeout line-shapes (Activation-time format, `Issue closeout:`, `Routing:` naming the routed skill) by FAILING the complete-flip ~4×, the same recurrence class for the one surface the goal did not cover. Disposition: none — deferred: recorded as the primary follow-on in the early-close report; same recurrence class, a candidate future issue carrying a `recurs:` lineage marker rather than a fresh narrow re-file. (source: `charness-artifacts/retro/2026-06-08-authoring-preflight-and-disposition-delaunder.md`)

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
- `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-authoring-preflight-and-disposition-delaunder.md`
- `charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md`
- `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`
