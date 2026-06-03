# Retro: Auto-Retro Trigger Miss
Date: 2026-06-03
Mode: session

## Context

The user pointed out that waste retros still appear not to happen automatically. This is a workflow miss, not a wording preference: the repo advertises automatic retro behavior, but the practical trigger boundary is narrower than the closeout path operators experience.

## Evidence Summary

- `skills/public/retro/SKILL.md` says to trigger a short session retro for real workflow misses and after slice closeout when `check_auto_trigger.py` reports `triggered: true`.
- `.agents/retro-adapter.yaml` configures trigger globs/surfaces for release, support, install/update, discovery, and plugin/export seams.
- `python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root .` returned `triggered: false` after the release because `changed_paths` was empty.
- `skills/public/achieve/SKILL.md` requires an automatic efficiency retro at goal closeout, but that obligation is handled by the agent following the skill, not by an enforcing closeout orchestrator.

## Waste

- The phrase "automatic retro" is overloaded. In `achieve`, it means a required After-phase step for goal operators. In `retro`, it means a narrow adapter-triggered check over current changed paths. Those are not the same mechanism.
- `check_auto_trigger.py` is state-sensitive: once a helper commits and pushes the release, the current diff is empty and the trigger cannot reconstruct the just-finished slice.
- Release publishing performs critique, quality, public verification, and issue closeout, but it does not run a post-publish waste retro or preserve the changed-path set for `retro` to evaluate afterward.
- The final user-facing report can honestly say the goal retro exists while still failing to explain the structural waste pattern that appeared during the release/publish tail.

## Critical Decisions

- Keep "every meaningful closeout produces a waste review" separate from "some surfaces auto-trigger retro from changed paths." The first is a lifecycle policy; the second is only a detector.
- Treat post-helper clean-tree state as hostile to retro detection. A trigger that depends on uncommitted diff must run before commit/push or receive explicit paths/commit range.
- Do not make every release publish pay for a long postmortem. The needed behavior is a bounded session retro when the slice hits configured surfaces or when the user identifies a real workflow miss.

## Expert Counterfactuals

- Gary Klein would have asked what cue was missing at the decision point. The missing cue was a hard closeout prompt: after `publish_release.py` verifies the public release and closes issues, the operator should be told whether a retro trigger matched the release delta before the session can close.
- Jef Raskin would have reduced the mode confusion: "automatic retro" should name the actual control path, such as `goal-after-retro` versus `changed-path-triggered-retro`, so the user and agent do not expect daemon-like behavior from an advisory script.

## Next Improvements

- workflow: In release/goal closeout, run `check_auto_trigger.py --paths <release-delta-paths>` before the tree is cleaned, or persist the changed-path list from the helper so post-publish retro can evaluate the same slice.
- capability: Add an explicit release-helper handoff field such as `retro_trigger_evaluation` that records `triggered`, `paths`, and whether a bounded session retro was written or intentionally skipped.
- memory: Filed issue #281 so this does not remain a prose-only retro lesson.

## Sibling Search

- `achieve` closeout already has deterministic evidence gates for retro artifact, host probe, and disposition review, so the same miss is less likely there when a formal goal artifact is used.
- `release` is exposed: the helper can finish with a clean tree and verified publication without a retro-trigger evaluation in the returned ledger.
- `impl` is exposed when work is committed before `check_auto_trigger.py` runs; the changed-path detector loses context the same way.
- `quality` is less exposed because it is primarily a verification workflow, but quality-triggered repo changes would have the same problem if a mutating helper commits before retro evaluation.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`
