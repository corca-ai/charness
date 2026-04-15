# Session Retro: Quality Review Diagnostics
Date: 2026-04-15

## Context
The user correctly challenged a prior quality closeout that reported only the quiet `run-quality.sh` summary. The quiet gate had hidden PASS-phase diagnostics, so the quality skill did not surface missing `gitleaks`, skipped online link checking, or unauthenticated GitHub release probing until asked.

## Waste
We treated the pre-push output shape as sufficient evidence for a quality review. That created extra loops: re-running verbose phases, discovering the `lychee --files-from` misuse only after enabling online mode, and then uncovering the `gitleaks` fast-path gap.

## Critical Decisions
- Split quiet enforcement from review mode with `./scripts/run-quality.sh --review`.
- Record `review_commands` and additional `runtime_budgets` in the quality adapter.
- Prefer authenticated `gh api` for GitHub release probes.
- Remove `crill` until its product/support surface is stable enough to track.

## Expert Counterfactuals
A fresh-eye reviewer would have asked whether `quality` was consuming phase logs or only the pass/fail envelope. Gary Klein's premortem lens would have flagged exactly this failure mode: a quiet standing gate passes while hiding the diagnostic signal the quality skill is supposed to report.

## Next Improvements
- workflow: when running `quality`, use the adapter's review command, not only the pre-push gate.
- capability: keep online direct-link checking and runtime budgets in the repo-owned quality surface.
- memory: keep this miss in the retro digest so future quality sessions do not equate quiet PASS output with full quality evidence.

## Persisted
Yes. This artifact was persisted through the retro persistence helper, which refreshes the recent lessons digest.
