# Retro: quality duplication workflow improvement goal

Mode: session

## Context

This retro covers the active 6h quality goal that continued from the user's
complaint about low-yield work. The run landed repeated quality slices and ended
with the release publish execute split, plus a small release contract fix for
durable install-refresh recording.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-12-quality-duplication-workflow-improvement-6h.md`
- Slice commits: `25201777`, `6287bb27`, `c863bac9`, `1f50ab7f`,
  `5c5ffa1e`, `9fdc07e8`, `c4b28eab`, `e6796431`, `8f44194d`
- Final broad gate: `pytest -q -m 'not release_only' tests/quality_gates
  tests/control_plane tests/test_*.py` passed 2807, 4 skipped, 26 deselected.
- Release focused gate: release publish/backend/resilience tests passed 48.
- Host metric window: recorded in the goal artifact; host-log probe rendered
  goal-window scoped measured/proxy signals.

## Waste

- The run still spent too much effort on repeated validation churn. Some of that
  was legitimate bundle proof, but the metric window shows repeated `pytest`,
  `ruff`, markdown/secrets, and VCS probes at a level that should push future
  goals toward a clearer gate cadence table before implementation starts.
- The release publish split initially fixed the line/function pressure but missed
  a direct-loader issue on `sys.modules[__name__]`; fresh-eye caught it before
  commit. The workflow worked, but the parent should have run a direct-loader
  smoke immediately after introducing the module boundary.
- The install-refresh artifact gap was pre-existing but was only surfaced by a
  reviewer after the split. That was worth fixing in-slice, but it shows the
  release contract lacked a focused assertion that "recorded" means durable
  artifact content, not only final JSON payload.

## Critical Decisions

- Continuing past the earlier low-yield point was correct. The run eliminated
  all Python length warn-band files and made several cohesive helper/test splits
  instead of stopping after the first small cleanup.
- Treating fresh-eye findings as blockers, not commentary, prevented a broken
  direct-loader path from shipping.
- Folding the install-refresh durability fix into Slice 9 was better than
  filing it as abstract follow-up because it had a narrow test and was directly
  inside the touched release path.

## Expert Counterfactuals

- Gary Klein would have run a pre-mortem at each helper extraction boundary:
  "what loader/import path fails on a fresh checkout?" That would have surfaced
  the `sys.modules` issue before fresh-eye review.
- Daniel Kahneman would have slowed the initial "this is just a split" framing:
  the install-refresh gap shows a visible output contract can be missed when the
  mind treats a change as behavior-preserving too early.

## Next Improvements

- workflow: The release resilience tests now include a direct
  `spec_from_file_location` loader regression for the extracted publish CLI
  context; future helper extractions should treat this as the local pattern.
- capability: The release resilience tests now assert that install-refresh
  status is recorded in the durable release artifact, not only in the final JSON
  payload.
- memory: Carry forward that broad gates are final/bundle proof; slice iteration
  should rely on focused tests plus surface validators until the bundle boundary.

## Sibling Search

- Direct-loader smoke pattern: applied locally to the release helper split with
  `tests/quality_gates/test_release_publish_resilience.py::test_publish_release_cli_direct_loader_context_without_sys_modules`.
  Sibling search result: release scripts are the active sibling family in this
  goal; no new issue filed because the relevant touched path now has regression
  proof.
- "Recorded means durable artifact" pattern: applied locally by adding the
  install-refresh artifact section and end-to-end assertion. No sibling issue
  filed because no second field with the same missed durable-output pattern was
  identified during this bounded closeout.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`
