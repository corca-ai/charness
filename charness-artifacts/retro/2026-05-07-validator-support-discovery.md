# Validator And Support Discovery Retro

## Context

This session followed a user correction: `check_skill_contracts.py` had become
too exact-snippet driven, and `quality` had not surfaced that brittleness or
the hidden support-skill discoverability issue earlier.

## Evidence Summary

- User correction in the current session.
- GitHub issue #108 gathered at
  `charness-artifacts/gather/2026-05-07-github-issue-108-support-skill-discoverability.md`.
- Current diff across `scripts/check_skill_contracts.py`,
  `skills/public/find-skills/`, `skills/public/quality/`, and
  `skills/support/specdown/SKILL.md`.
- `./scripts/run-quality.sh --read-only`: 51 passed, 0 failed.

## Waste

- Exact snippet pins were meant to keep load-bearing behavior from being
  deleted, but they also made useful skill compression look unsafe unless
  anchor text stayed in `SKILL.md`.
- `quality` saw skill ergonomics in general but did not directly ask whether a
  validator was freezing wording instead of behavior.
- Support skills were present in the capability map, but workflow-language
  triggers such as `docs/specs`, `run:shell`, or `check:jq` did not have a
  deterministic recommendation path.

## Critical Decisions

- Split skill contract validation into core-only and package-level checks so
  selection/routing promises still stay in `SKILL.md`, while detailed rules can
  move into references.
- Add `find-skills --recommend-for-task` to surface support skills from task
  language without requiring the user to name the support skill.
- Treat #108 as a support-discoverability issue, not a Cautilus-specific issue.
- Improve `quality` skill-evaluation guidance so future reviews look for
  brittle prose source guards and hidden support-skill routing gaps.

## Expert Counterfactuals

- Gary Klein would have asked what failure mode the exact snippets were
  preventing before accepting them as a permanent test shape; that would have
  separated load-bearing core contracts from movable reference detail earlier.
- Daniel Kahneman would have challenged the easy feeling that a passing quality
  gate meant the skill-evaluation lens was good enough; the gate passed while a
  brittle validator design still shaped behavior.

## Next Improvements

- workflow: before compressing or judging a public skill, inspect exact-string
  validators and classify each checked phrase as core, package detail, or a
  candidate for behavior-level proof.
- capability: prefer reference-aware or scenario-backed validator assertions
  over exact prose snippets when the protected invariant is not classifier
  input.
- memory: support-skill discoverability must include workflow-language and file
  shape triggers, not only explicit `support/<id>` naming.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`
