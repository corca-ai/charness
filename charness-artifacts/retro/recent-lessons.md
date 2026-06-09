# Recent Retro Lessons

## Current Focus

- Built #339 across four slices as one `achieve` goal: (1) `accepted-risk:` / `out-of-scope:` additive disposition arms + the `## Residual Ledger` presence/form floor (rung 1f) in the shared grammar; (2) `scripts/proof_semantics_adapter_lib.py` — the optional, domain-blind proof-semantics adapter boundary (proof_levels + `incomparable` partial order, acceptance_map, verifier_refs, gap_policy, missing-adapter degradation); (3) `scripts/proof_mismatch.py` — the portable three-condition proof-mismatch floor (no proof entry / reached < required / gap lacks disposition) wired into the achieve CLI; (4) the same floor wired into issue closeout-draft validation, plus the dogfood, broad gate, and changed-line coverage. (source: `charness-artifacts/retro/2026-06-09-339-portable-disposition-ledger.md`)
- One `achieve` goal cleared the operator-selected next queue in three independent, per-slice-closed-out slices: (1) **#N-anchor edit-time guard** (`scripts/skill_issue_anchor_scan.py` + `check_skill_surface_preflight.py --scan-issue-anchors`), (2) **#338** gather X/Twitter exact-source (`twitter_exact_source.py` identity-keyed route + `source_identity` answer-path verdict, `Closes #338`), (3) **charness-update release-closeout** — verification that the standing step already shipped (v0.29.0 to v0.30.1) + stale-handoff fix. (source: `charness-artifacts/retro/2026-06-09-nanchor-guard-338-gather-release-closeout.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-09-v0-35-0-release-auto-retro.md`; sources: 21)
- **#338 closeout-draft contract discovery (4 round-trips).** The `validate-closeout-draft` contract was learned incrementally: missing resolution_critique, then a critique artifact missing a `tool signal:`, then a wrong carrier-body source (for direct-commit the body is the COMMIT MESSAGE, not --body-file), then missing feature ledger fields. An author-time preflight listing the required closeout-draft shape would have collapsed these to one pass. (source: `charness-artifacts/retro/2026-06-09-nanchor-guard-338-gather-release-closeout.md`)
- **Coverage-producer DISCOVERED (not confirmed) an uncovered changed line** (`mutation_manifest_lib.py:124`, the `if not per_file_budget_excluded: return` early-return). The carried lesson said cover new branches IN the introducing slice so the bundle producer confirms; I covered 2 of the 3 branches in slice 1 and missed the empty-result early return. Cost: a fixup commit + a ~7-min producer re-run. Same recurring class as the recent-lessons "coverage-producer round-trip." (source: `charness-artifacts/retro/2026-06-09-deferred-queue-341-340-activation-preflight.md`)
- **Coverage-producer round-trip on pre-existing uncovered branches (the main waste, partly avoidable).** I carried the #339 lesson "cover any NEW module's lines IN the introducing slice so the bundle producer confirms, not discovers" into the operating frame — but still ran the bundle producer and had it *discover* 7 uncovered changed lines (the `_mask_fences` unbalanced-fence branch, `_section_body` heading-at-EOF branch, and 5 loader `raise ImportError` branches). Root cause: I reasoned "verbatim move ⇒ already covered" and missed that moving code into a NEW file makes every line a *changed* line, so pre-existing uncovered branches in the moved source become newly-gated. The branches were never covered even pre-split; the move surfaced them. Cost: a second ~6.5-min producer run after adding the coverage. The producer ran FIRST (per the guardrail), so the gap surfaced at the boundary, not post-merge — but it discovered rather than confirmed. (source: `charness-artifacts/retro/2026-06-09-achieve-closeout-module-split.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-09-v0-35-0-release-auto-retro.md`; sources: 21)
- an authoring-time guard would flag a `#N` issue anchor in a `skills/public/**` script at edit/preflight time, not only at the commit sweep — the trap recurred 3× this run despite the frame note. Disposition: accepted-risk: the package-level `validate_skill_ergonomics` sweep is the commit-time backstop and caught all three, so nothing escaped; the residual is edit-time friction, re-persisted to recent-lessons as a pre-write checklist item, not a new gate. (source: `charness-artifacts/retro/2026-06-09-339-portable-disposition-ledger.md`)
- applied — this retro records that the per-improvement disposition floor and the structural-follow-up destination floor are two distinct gates with two distinct valid-form summaries (VALID_FORM_SUMMARY vs DESTINATION_FORM_SUMMARY); the summary refresh surfaces it to recent-lessons. (source: `charness-artifacts/retro/2026-06-09-closeout-preflight-and-scaffold-validator-citation.md`)
- applied — when surfacing an enforced form/shape, render EVERY enumerable piece from the OWNING validator's live constant and drift-test each; never hand-copy a form from a nearby template (it may be a different floor's form). Encoded as the drift tests pinning VALID_FORM_SUMMARY / DESTINATION_FORM_SUMMARY in commit `bebdaa2d`. (source: `charness-artifacts/retro/2026-06-09-closeout-preflight-and-scaffold-validator-citation.md`)

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
- `charness-artifacts/retro/2026-06-09-339-portable-disposition-ledger.md`
- `charness-artifacts/retro/2026-06-09-achieve-closeout-module-split.md`
- `charness-artifacts/retro/2026-06-09-closeout-preflight-and-scaffold-validator-citation.md`
- `charness-artifacts/retro/2026-06-09-deferred-queue-341-340-activation-preflight.md`
- `charness-artifacts/retro/2026-06-09-nanchor-guard-338-gather-release-closeout.md`
- `charness-artifacts/retro/2026-06-09-v0-32-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-33-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-34-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-35-0-release-auto-retro.md`
