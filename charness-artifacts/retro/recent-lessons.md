# Recent Retro Lessons

## Current Focus

- Reviewed the active achieve goal that turned the boundary-bypass advisory probe into a no-increase ratchet, skillified the portable `quality` contract, and converted the first clean `inventory_*` boundary-bypass test in-process. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`; sources: 2)
- Goal run implementing the A4-lite contract that turns retro waste findings into **structural, destination-routed** issue proposals instead of incident-coupled ones (shared reference + retro/achieve/issue wiring + issue-adapter `harness_upstream` + presence-only `validate_proposal_fields.py` + tests). (source: `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`)

## Repeat Traps

- I ran a broad final gate before the fresh-eye critique was consumed, then had to rerun it after real critique findings changed the public contract. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`; sources: 2)
- The first public payload contract under-specified two machine invariants already used by the repo-local ratchet: candidate keys and clean/internal target disjointness. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`; sources: 2)
- The first Slice 4 payload validator test accidentally added a new boundary-bypass candidate, proving the new ratchet was useful but costing an extra correction pass. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`; sources: 2)
- `check_auto_trigger.py` is state-sensitive: once a helper commits and pushes the release, the current diff is empty and the trigger cannot reconstruct the just-finished slice. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)

## Next-Time Checklist

- applied: Encode portable boundary-bypass invariants as validator-enforced fields, not only reference prose. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`; sources: 2)
- applied: Keep new quality-gate tests in-process by default; subprocess tests need an explicit CLI-contract reason. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`; sources: 2)
- applied: Make fresh-eye critique precede the final broad gate when the critique can still change prompt/public contract surfaces. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`; sources: 2)
- a `--report-all` (collect-all) mode for `validate_quality_artifact.py` and peers would surface every violation in one pass; 21 `validate_*.py` raise on the first error today vs 10 that already collect failures. Optional candidate, not committed here. (source: `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/.tmp-testability-quality-ratchet-retro.md`
- `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`
- `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`
- `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`
- `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`
