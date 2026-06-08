# Retro — #339 portable residual/disposition ledger + adapter-owned proof semantics

Date: 2026-06-09

## Context

Built #339 across four slices as one `achieve` goal: (1) `accepted-risk:` /
`out-of-scope:` additive disposition arms + the `## Residual Ledger` presence/form
floor (rung 1f) in the shared grammar; (2) `scripts/proof_semantics_adapter_lib.py`
— the optional, domain-blind proof-semantics adapter boundary (proof_levels +
`incomparable` partial order, acceptance_map, verifier_refs, gap_policy,
missing-adapter degradation); (3) `scripts/proof_mismatch.py` — the portable
three-condition proof-mismatch floor (no proof entry / reached < required / gap
lacks disposition) wired into the achieve CLI; (4) the same floor wired into issue
closeout-draft validation, plus the dogfood, broad gate, and changed-line coverage.
The #339 maintainer evidence-update comment landed mid-run and pinned the exact
three-condition contract — it confirmed Slices 1–2 and drove Slice 3's condition (i).
Each slice got a fresh-eye critique (SHIP-WITH-NITS ×2, SHIP ×1). Broad gate: 73
passed, 0 failed; changed-line mutation coverage: 0 uncovered.

## What created waste

- **The `#N`-anchor-in-skill-package trap fired three times** (Slices 1, 3, 4): a
  `(#339)` comment in `skills/public/**` scripts trips the package-level
  `validate_skill_ergonomics` `portable_package_issue_anchor` scan. It was caught
  each time by the commit-time sweep (no escape), but only AFTER writing it,
  despite the carried frame note. The friction is edit-time, not escape-time.
- **Attention-state vocabulary trip** (Slice 1): the word `skipped` in a docstring
  string-constant tripped `validate_attention_state_visibility`; reworded.
- **Boundary-bypass ratchet trip** (Slice 3): a CLI subprocess test of
  `check_goal_artifact.py` added a new test->script delivery boundary; converted to
  an in-process `main()` call (the ratchet's intended form).
- **Changed-line coverage round-trip** (Slice 4 bundle boundary): the producer
  flagged 32 uncovered changed lines (mostly adapter validation/defensive branches
  added across Slices 2–4). Running it FIRST at the boundary surfaced them there,
  not post-merge — but covering each branch in its introducing slice would have made
  the producer a confirmation, not a discovery (the standing guardrail, re-proven).

## What worked

- Pushing heavy logic to the shared `scripts/` grammar (which has headroom) and
  keeping the at-cap achieve closeout modules' additions to a few lines — the only
  way to land rung 1f and the proof-mismatch wiring without blowing the length gate.
- `load_repo_module_from_skill_script` for loading the portable `from scripts.`
  modules in the achieve/issue skill contexts (resolved the import-mechanics wall).
- The fresh-eye critiques caught the multi-table under-fire (Slice 1) and steered
  the `acceptance_classes` accessor (Slice 2) before they shipped.

## Next Improvements

- workflow: an authoring-time guard would flag a `#N` issue anchor in a
  `skills/public/**` script at edit/preflight time, not only at the commit sweep —
  the trap recurred 3× this run despite the frame note.
  Disposition: accepted-risk: the package-level `validate_skill_ergonomics` sweep is the
  commit-time backstop and caught all three, so nothing escaped; the residual is edit-time
  friction, re-persisted to recent-lessons as a pre-write checklist item, not a new gate.
- workflow: cover new normalization/guard/validation branches IN the introducing
  slice so the bundle-boundary mutation producer confirms rather than discovers.
  Disposition: applied: covered all 32 flagged changed lines in the bundle coverage
  commit (3d3cd561) and re-persisted the in-slice-coverage guardrail to recent-lessons.
- structural: the achieve closeout module family (`goal_artifact_disposition.py`
  352/360, `goal_artifact_closeout_evidence.py` 348/360) is at the length cap and
  forced this run to route logic through the shared grammar and wire new floors from
  the CLI. Disposition: accepted-risk: the hard length gate blocks further growth (it
  is the backstop that forced the clean factoring this run); a cohesive split is
  deferred structural debt, re-persisted to recent-lessons so the next at-cap addition
  to this family starts from a split rather than another workaround.

## Sibling Search

- n/a — the waste items are session-local process/authoring friction caught by
  existing gates, not a transferable code-pattern with siblings to fix now.

## Persisted

Yes — this file is the persisted retro; its dispositions are mirrored into the
`## Auto-Retro` of the #339 goal artifact, and the two `applied`/`accepted-risk`
process lessons are added to `charness-artifacts/retro/recent-lessons.md`.
