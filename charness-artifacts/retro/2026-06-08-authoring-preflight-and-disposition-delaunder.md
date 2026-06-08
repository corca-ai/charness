# Session Retro

Date: 2026-06-08

## Mode

session

## Context

Ran the achieve goal `2026-06-08-authoring-preflight-and-disposition-delaunder`
end to end: generalize the author-time shape preflight across the artifact-
authoring validator family, and de-launder the disposition escape — to
structurally close the recurring "authoring-preflight skip" loop instead of
filing its N-th narrow instance.

## Evidence Summary

- New `scripts/check_artifact_surface_preflight.py` (registry + `--type`/`--path`/
  `--emit-stub`/`--changed-artifacts`); blocking `check-artifact-shape (staged)`
  structural-sweep member for the prefix families (critique/ideation/retro).
- De-launder rung 1d (`apply_recurrence_lineage_floor` + shared
  `has_recurrence_lineage`) + rung-2 falsify mandate in `lifecycle.md`.
- Coverage report `charness-artifacts/spec/artifact-shape-preflight-coverage.md`
  (7/7 in-class surfaces have author-time shape help).
- Proof: 535 targeted tests green; broad read-only gate 72/73 (the one failure was
  a pre-existing stale `retro/lesson-selection-index.json`, rebuilt at closeout);
  two fresh-eye critiques (design SHIP-WITH-CHANGES folded; de-launder SHIP).

## Waste

Two avoidable commit-boundary re-runs this session, both caught by the broad
suite rather than at edit time: (1) a bare issue anchor `#284 -> #334` landed in a
skill-package helper docstring (`goal_artifact_disposition.py`) and tripped
`validate_skill_ergonomics`; (2) the mirror went un-synced after disposition edits
and tripped `check_staged_mirror_drift`. Both are the exact "author-time gate
discoverability" class this goal is about — for *skill-package* edits, which the
existing skill-surface preflight already covers but I did not re-run after each
edit. Low cost (caught pre-commit on retry), but on-theme.

## Critical Decisions

- The Slice-1 fresh-eye critique flipped the A3 wiring from an exit-0 advisory
  (doc-equivalent — the G2 trap) to a blocking structural-sweep member. This was
  the load-bearing design correction; without it the generalization would have
  repeated the very discretionary-skip failure it targets.
- Slice-4 two-tier decision: the adapter-scoped validate-all trio
  (debug/quality/handoff) is author-time-only, NOT in the fail-fast sweep, because
  a validate-all gate there reorders `run_slice_closeout`'s risk-interrupt stage
  and can block on a pre-existing sibling. Keeping the sweep changed-scoped is the
  principled line.

## Expert Counterfactuals

- A Tony Hoare "make the precondition explicit" lens would have caught the
  ergonomics + mirror-sync waste up front: before editing any `skills/**` package
  file, the precondition is "run the skill-surface preflight + sync the mirror."
  Encoding that as a habit (or a pre-edit checklist the preflight already prints)
  removes both waste instances.

## Sibling Search

- axis: same-layer authoring gates | location: scripts/check_skill_surface_preflight.py | decision: valid follow-up outside the slice | proof: the skill-surface preflight already covers skill packages but is discretionary to run; this session paid the ergonomics/mirror waste by not running it per-edit | follow-up: deferred handoff-authoring-preflight-habit

## Next Improvements

- workflow: the artifact-shape preflight now runs at the commit boundary for the prefix families, so artifact-shape failures surface pre-gate. Disposition: applied: shipped `check-artifact-shape (staged)` in the structural sweep.
- capability: the critique scaffold is now cited from the documented authoring path (the uncited-scaffold root cause). Disposition: applied: cited `scaffold_critique_artifact.py` from `counterweight-triage.md` + the dispatcher `--emit-stub`.
- memory: persist the two-tier preflight model + the de-launder rung-split so the next author does not relitigate them. Disposition: applied: recorded in this retro, the spec, and recent-lessons.
- workflow: extend the recurrence-lineage floor to standalone-retro `## Next Improvements`. Disposition: applied: Slice 6 (done-early continuation) wired `validate_recurrence_lineage` into the retro validator (enforce-from 2026-06-09, grandfathering all existing retros); closes the de-launder's named open escape.

## Persisted

yes: charness-artifacts/retro/2026-06-08-authoring-preflight-and-disposition-delaunder.md
