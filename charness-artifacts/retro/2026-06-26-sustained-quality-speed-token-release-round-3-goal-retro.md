# Retro: sustained quality speed token release round 3
Date: 2026-06-26
Mode: session

## Context

Three-hour quality continuation for
`charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-3.md`.
The run continued the previous round's lesson: do not publish early; keep
improving until the closeout window, then prove and release.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-3.md`
- Host log probe:
  `charness-artifacts/probe/2026-06-26-sustained-quality-speed-token-release-round-3-host-log.json`
- Boundary inventory moved from 69 raw candidate keys / 28 clean-convertible
  early in the round to 67 raw candidate keys / 3 clean-convertible before
  final proof.
- Main implementation pattern: replace incidental Python subprocess smokes with
  `main()` calls through a shared `tests.script_main.run_loaded_script_main()`
  helper while preserving real process boundaries for generated commands,
  browser cleanup, git state, committed-surface checks, and release proof.

## Waste

- Many small subprocess-conversion slices still created commit and artifact
  churn. The shared runner reduced duplicate helper code, but it should have
  been extracted earlier in the round.
- Boundary inventory improvements are useful but can incentivize mechanical
  conversion. Several remaining candidates were intentionally left because the
  process boundary is the behavior under test.
- Codex host log probing could bind to `~/.codex/history.jsonl`, but that file
  did not expose goal-window event records in the same way as the Claude
  project session JSONL. The probe artifact records this as measured evidence,
  not as a made-up cost total.

## Critical Decisions

- Held release work until final closeout instead of publishing when the first
  slices passed.
- Converted parent script process startup only when assertions still covered the
  same output, filesystem side effects, or child command behavior.
- Left Cautilus, web-fetch browser cleanup, release-host proof, and committed
  packaging checks as process boundaries because those tests validate runtime
  isolation or irreversible-boundary evidence.

## Expert Counterfactuals

- Gawande would have turned the recurring subprocess conversion judgment into a
  checklist sooner: "is parent interpreter startup the behavior under test?"
- Minto would have grouped the repeated slice records by pattern earlier, then
  recorded individual metrics as supporting evidence rather than equal-weight
  story units.
- Raskin would have made the shared runner the first operator affordance once
  the same argv/stdout/env patching appeared in more than one test area.

## Next Improvements

- applied: extracted `tests.script_main.run_loaded_script_main()` and reused it
  across control-plane, quality-gate, scaffold, packaging, setup, and agent
  browser tests.
- applied: preserved generated/exported command subprocess tests while
  converting local setup/validator/export smokes in process.
- applied: recorded the host metric window and probe artifact before final
  closeout so host-cost claims stay scoped and honest.
- accepted-risk: did not convert Cautilus, web-fetch, release-host, or
  committed-packaging process boundaries because their remaining subprocesses
  are the behavior being validated or are safer to keep for release proof.

## Sibling Search

No external issue is needed. The transferable waste item was repo-local and
already applied through `tests/script_main.py`; the remaining candidates are
documented as intentionally process-boundary-shaped in the goal artifact.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-06-26-sustained-quality-speed-token-release-round-3-goal-retro.md
