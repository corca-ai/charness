# Critique: Issue 179 Worktree Routing

Date: 2026-05-19
Target: code/workflow recurrence critique
Packet consumed: `charness-artifacts/critique/2026-05-19-112305-packet.md`
Fresh-Eye Satisfaction: parent-delegated

## Change

Resolve Charness #179 by making worktree workflow routing visible in the
startup `find-skills` inventory, keeping task-shaped workflow recommendations
available for `new worktree` requests, pointing emitted workflow paths at a
packaged plugin file, and tightening setup-generated Skill Routing guidance so
workflow/capability nouns trigger `find-skills --recommend-for-task` before ad
hoc shell use.

## Angles

- Routing and installed-plugin surface recurrence: reviewer `Wegener`
- Artifact semantics and test/dogfood coverage: reviewer `Heisenberg`
- Counterweight: reviewer `Locke`

## Findings

- Act Before Ship: default startup inventory needed a no-query assertion that
  `workflow_integrations` contains worktree create/cleanup while ad hoc
  `workflow_recommendations` stays empty.
- Act Before Ship: the original recurrence shape needed an exact fixture with
  `.agents/worktree-adapter.yaml` and task text containing `new worktree`,
  asserting steering to `charness worktree create --prepare`.
- Bundle Anyway: `find-skills` skill prose still described task-text
  recommendations as support-skill-only, leaving the old mental model in the
  installed routing surface.
- Bundle Anyway: plugin-export proof should assert the emitted packaged path
  exists under `plugins/charness/`.
- Valid but Defer: a manifest-backed workflow integration registry remains the
  longer-term recurrence fix for future non-tool workflow surfaces.

## Counterweight Triage

- Act Before Ship: add the default startup inventory assertion and exact
  `new worktree` recurrence fixture.
- Bundle Anyway: update `find-skills` wording, add a small plugin/export-facing
  assertion, and label the hardcoded workflow list as the temporary canonical
  source.
- Over-Worry: do not add adapter-state detection to `find-skills`; setup still
  owns adapter-missing detection.
- Over-Worry: do not run a broad schema migration or add extra setup
  adapter-missing tests for this slice.
- Valid but Defer: replace the hardcoded workflow list with a manifest-backed
  workflow registry in a future slice if more workflow integrations need the
  same treatment.

## Applied Before Commit

- `tests/test_find_skills.py` now asserts the default startup artifact carries
  `workflow_integrations` for worktree create/cleanup and keeps
  `workflow_recommendations` empty.
- `tests/test_find_skills_task_recommendations.py` now has an exact
  `.agents/worktree-adapter.yaml` plus `new worktree` fixture that expects
  `charness worktree create --prepare`.
- `tests/test_find_skills_plugin_export.py` now proves the plugin-emitted
  workflow path exists in the checked-in plugin export.
- `skills/public/find-skills/SKILL.md` now tells operators to use task-text
  recommendations for workflow/capability language, including new-worktree
  requests before raw `git worktree add`.
- `WORKFLOW_RECOMMENDATIONS` is explicitly marked as the temporary canonical
  workflow source until a manifest-backed registry exists.

## Next Move

Commit after regenerating `find-skills` and the plugin export, then rerunning
the deterministic closeout gate with Cautilus skill-review acknowledgement.
