# Retro: Nose, issues #371-#373, and runtime goal

Mode: session

## Context

This retro covers the active goal
`charness-artifacts/goals/2026-06-15-nose-issues-371-373-test-runtime.md`:
runtime reduction, issue #373/#372/#371 disposition, and selected nose 0.10.0
clone reduction.

## Evidence Summary

- Commits through `7eb3e923 refactor: share adapter field helpers`.
- Goal slice log and critique artifacts for runtime, #373, #372, #371, and nose
  helper extraction.
- Broad pytest final proof: 3056 passed, 26 deselected in 244.91s.
- Nose 0.10.0 inventory: 559 ranked families / 2036 duplicate lines before the
  helper extraction, 551 ranked families / 2002 duplicate lines after.

## Waste

- The first #371 wording allowed a closure path without process/profile teardown
  proof; fresh-eye review caught it before commit.
- The nose helper extraction initially missed one `hotl` optional-path call
  site. Focused adapter tests caught the miss, and a direct helper test now pins
  the shared API.
- Final verification-lock closeout no-oped on a clean worktree, so broad pytest
  had to be run directly. This is acceptable but worth remembering for clean
  bundle closeouts.

## Critical Decisions

- Treat #371 as a non-closure upstream lifecycle split instead of pretending the
  local runtime guard proves invocation teardown.
- Keep nose work to identical adapter helpers and leave per-skill
  bootstrap/import/main boilerplate as intentional portability duplication.
- Run public-skill dogfood recommendations for the helper-only public skill
  changes and keep the scenario registry unchanged because routing/artifact
  contracts did not change.

## Expert Counterfactuals

- Gary Klein's premortem lens would have asked earlier: "How could this closeout
  falsely claim a lifecycle fix?" That would have removed the #371 wording
  loophole before reviewer review.
- Martin Fowler's refactoring lens would have started the nose slice with a
  characterization test around the new helper API; adding `tests/test_adapter_lib.py`
  after review closed that gap.

## Next Improvements

- workflow: When a final verification-lock closeout no-ops because the worktree
  is clean, run and record the broad pytest command directly rather than trying
  to force a fake diff.
- memory: Keep the #371 lesson visible: a healthcheck/reaper is drift
  mitigation unless the repo owns and proves the final lifecycle boundary.
- capability: No new gate is needed. Existing fresh-eye review, focused tests,
  and slice closeout caught the issues before commit.

## Sibling Search

- cross-file: `agent-browser` lifecycle ownership could recur for any external
  binary where Charness has only detect/healthcheck/update surfaces. Existing
  integration manifests and support-tool docs already distinguish external
  lifecycle ownership; monitor rather than adding a new floor.
- no cross-file sibling: adapter helper extraction used an existing shared owner
  and direct tests; remaining duplicates with different signatures are local
  payload parsers or intentional portability boilerplate.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-15-nose-issues-runtime-goal-retro.md`
