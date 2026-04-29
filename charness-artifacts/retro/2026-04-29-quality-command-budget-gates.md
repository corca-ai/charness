# Session Retro: Quality Command And Runtime Budget Gates

## Context

This session ran repo-wide `quality`, then implemented the low-noise gates found
by delegated review: exact Charness quality command validation and runtime
budgets for stable 5s-class standing phases.

## Evidence Summary

- `./scripts/run-quality.sh --review` passed after repairs: 48 phases, 0 failed.
- Cautilus routing proof passed with recommendation `accept-now`.
- `check_changed_surfaces.py` flagged checked-in plugin export and
  integrations/control-plane surfaces, which triggered this retro.

## Waste

- The first refreshed quality artifact exceeded its line budget and included a
  command string that the freshness validator misread as a path. Artifact
  validators caught it, but later than ideal.
- The first runtime-budget pass moved the unbudgeted hotspot from duplicates and
  markdown to `check-cli-skill-surface`; the budget sweep should have covered
  all current top unbudgeted hot spots in one pass.

## Critical Decisions

- Promote exact `gate_commands` and `review_commands` validation instead of
  leaving command honesty as review prose.
- Budget `check-cli-skill-surface`, `check-duplicates`, and `check-markdown`
  together once runtime evidence showed each as a stable 5s-class phase.

## Expert Counterfactuals

- Gerald Weinberg lens: inspect the quality system feedback loop, not only the
  failing gate. That would have grouped all unbudgeted runtime hot spots before
  the first full rerun.
- Jef Raskin lens: keep the latest artifact more discoverable by starting with
  the validator's exact required phrases and line budget, then filling content.

## Next Improvements

- workflow: before updating `quality/latest.md`, check its validator-required
  phrases and line limit first.
- capability: consider a small helper that renders the current runtime-hotspot
  bullet from `check_runtime_budget.py` output to avoid hand-copy drift.
- memory: keep the README/operator proof ledger as the next active quality gate.

## Persisted

- yes: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`
