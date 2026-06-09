# Recent Retro Lessons

## Current Focus

- Built #339 across four slices as one `achieve` goal: (1) `accepted-risk:` / `out-of-scope:` additive disposition arms + the `## Residual Ledger` presence/form floor (rung 1f) in the shared grammar; (2) `scripts/proof_semantics_adapter_lib.py` — the optional, domain-blind proof-semantics adapter boundary (proof_levels + `incomparable` partial order, acceptance_map, verifier_refs, gap_policy, missing-adapter degradation); (3) `scripts/proof_mismatch.py` — the portable three-condition proof-mismatch floor (no proof entry / reached < required / gap lacks disposition) wired into the achieve CLI; (4) the same floor wired into issue closeout-draft validation, plus the dogfood, broad gate, and changed-line coverage. (source: `charness-artifacts/retro/2026-06-09-339-portable-disposition-ledger.md`)
- Release publish triggered a configured automatic session retro for `v0.32.0`. (source: `charness-artifacts/retro/2026-06-09-v0-32-0-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`; sources: 18)
- **Coverage-producer round-trip on pre-existing uncovered branches (the main waste, partly avoidable).** I carried the #339 lesson "cover any NEW module's lines IN the introducing slice so the bundle producer confirms, not discovers" into the operating frame — but still ran the bundle producer and had it *discover* 7 uncovered changed lines (the `_mask_fences` unbalanced-fence branch, `_section_body` heading-at-EOF branch, and 5 loader `raise ImportError` branches). Root cause: I reasoned "verbatim move ⇒ already covered" and missed that moving code into a NEW file makes every line a *changed* line, so pre-existing uncovered branches in the moved source become newly-gated. The branches were never covered even pre-split; the move surfaced them. Cost: a second ~6.5-min producer run after adding the coverage. The producer ran FIRST (per the guardrail), so the gap surfaced at the boundary, not post-merge — but it discovered rather than confirmed. (source: `charness-artifacts/retro/2026-06-09-achieve-closeout-module-split.md`)
- **Verdict-parity harness confound iteration (minor, well-handled).** The first parity diff flagged `remaining_minutes` (wall-clock) then `head_sha` (HEAD advanced on commit) — two benign confounds owned by untouched modules. Resolved cleanly by normalizing wall-clock in the harness and finally doing a pristine temp-revert (same HEAD, same goal text) so only the slice logic varied. The temp-revert is the gold-standard form; reaching for it first would have skipped the two normalization iterations. (source: `charness-artifacts/retro/2026-06-09-achieve-closeout-module-split.md`)
- **Changed-line coverage round-trip (anticipated, partly avoidable).** The Slice-3 prep affordance added input-normalization branches (list/string/None) and three defensive `SystemExit` guards, plus a refactor that relocated the clean-worktree check. Slice-3 tests covered the happy path but not those branches, so the bundle-boundary producer flagged 6 uncovered changed lines, costing a cover-then-re-run-producer cycle (each producer run is multi-minute mutation coverage). Running the producer FIRST (per the carried guardrail) worked — it surfaced the gap at the boundary, not post-merge — but covering the branches IN Slice 3 would have made the producer a confirmation, not a discovery. (source: `charness-artifacts/retro/2026-06-08-workflow-ergonomics-bundle-336-goal-slot.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`; sources: 18)
- an authoring-time guard would flag a `#N` issue anchor in a `skills/public/**` script at edit/preflight time, not only at the commit sweep — the trap recurred 3× this run despite the frame note. Disposition: accepted-risk: the package-level `validate_skill_ergonomics` sweep is the commit-time backstop and caught all three, so nothing escaped; the residual is edit-time friction, re-persisted to recent-lessons as a pre-write checklist item, not a new gate. (source: `charness-artifacts/retro/2026-06-09-339-portable-disposition-ledger.md`)
- cover new normalization/guard/validation branches IN the introducing slice so the bundle-boundary mutation producer confirms rather than discovers. Disposition: applied: covered all 32 flagged changed lines in the bundle coverage commit (3d3cd561) and re-persisted the in-slice-coverage guardrail to recent-lessons. (source: `charness-artifacts/retro/2026-06-09-339-portable-disposition-ledger.md`)
- **memory:** Persist the refinement above to recent-lessons so the next module-split goal starts from it (this retro's persistence refreshes the digest). (source: `charness-artifacts/retro/2026-06-09-achieve-closeout-module-split.md`)

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
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-31-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-workflow-ergonomics-bundle-336-goal-slot.md`
- `charness-artifacts/retro/2026-06-09-339-portable-disposition-ledger.md`
- `charness-artifacts/retro/2026-06-09-achieve-closeout-module-split.md`
- `charness-artifacts/retro/2026-06-09-v0-32-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`
