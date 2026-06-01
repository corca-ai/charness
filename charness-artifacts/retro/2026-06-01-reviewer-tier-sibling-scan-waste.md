# Reviewer Tier Sibling Scan Waste Retro
Date: 2026-06-01

## Context

Reviewed the follow-up work after the critique adapter default fix: sibling scan
for other public skills that directly spawn bounded fresh-eye reviewers, fixes
for `quality`, issue causal review, and `setup`, setup scaffold safety, and the
handoff live-backlog test adjustment.

## Evidence Summary

- Commits: `45e4d51` and `9362288`.
- Debug: `charness-artifacts/debug/2026-06-01-reviewer-tier-sibling-scan.md`.
- Critique: `charness-artifacts/critique/2026-06-01-reviewer-tier-sibling-scan-critique.md`.
- Verification: targeted tests, changed-surface validators, and broad pytest
  (`1955 passed, 4 skipped`).
- Host metrics: not probed; waste assessment is based on command sequence and
  observed failures, not token or wall-clock totals.

## Waste

- I skipped the retro closeout until the user asked. That left the main lesson
  in chat and debug artifacts but not in the retro memory surface.
- I started broad pytest before fully disposing the fresh-eye blocker. That run
  was expected to be invalid once the setup scaffold safety issue was found, so
  it spent verification time before the triage lock was stable.
- I changed a live-backlog-sensitive handoff test during this slice because the
  broad run exposed it. The fix was useful, but it was opportunistic scope
  expansion triggered by verification rather than part of the reviewer-tier
  triage lock.

## Critical Decisions

- Correct: direct fresh-eye reviewer spawns should request the portable
  `high-leverage` tier without copying provider model names into portable skill
  prose.
- Correct: setup scaffold should carry evidence locations but not enable
  delegated-review recommendations for plain consumer repos without evidence or
  explicit opt-in.
- Costly: broad pytest should have waited until after fresh-eye disposition and
  targeted scaffold safety tests passed.

## Expert Counterfactuals

- Gary Klein premortem: before broad verification, ask "what would make this
  run invalid?" The answer was the still-open fresh-eye scaffold blocker.
- Daniel Kahneman base-rate lens: prior Charness slices often find one more
  contract/test anchor after fresh-eye review; assume the first broad run after
  review feedback is premature unless blocker disposition is complete.

## Next Improvements

- workflow: after a fresh-eye review reports any Act Before Ship item, pause
  broad verification until each blocker has a targeted regression and a short
  re-run proves the blocker is closed.
- workflow: when broad verification surfaces live-state drift unrelated to the
  current slice, classify it before patching; if fixed now, name it as bundled
  opportunistic maintenance in the artifact.
- memory: keep this retro with the reviewer-tier debug artifact so future
  prompt-surface sibling scans lock triage before broad pytest.

## Sibling Search

- same layer: prompt-surface sibling scans that combine direct skill prose,
  adapter scaffolds, and live tests | decision: same waste, fix now | proof:
  this retro and debug artifact record the corrected sequence.
- abstraction up: any task-completing repo change with fresh-eye Act Before
  Ship findings | decision: diagnostic-only | proof: operating contract already
  requires critique before closeout; the missing habit was sequencing, not a new
  rule.
- specialization down: handoff live-backlog test brittleness surfaced during
  reviewer-tier verification | decision: same waste, fix now | proof: test was
  changed to assert actionable candidates instead of exact live candidate count.
- mental-model siblings: "broad pytest will tell me if the slice is ready" |
  decision: diagnostic-only | proof: broad pytest caught real issues but one
  run was predictably premature before blocker disposition.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`.
