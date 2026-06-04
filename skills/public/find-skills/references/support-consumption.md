# Support Consumption

When the best match is not a public skill, `find-skills` should explain the
layer honestly.

## Trusted Skill

Use this label when:

- the host adapter exposes a trusted skill root outside local `charness`
- the capability exists there but is not part of the local public skill bundle
- the right answer is "use the host's trusted skill" rather than "invent a new
  charness skill"

## Support Skill

Use this label when:

- the capability teaches the agent how to use a specialized tool
- the capability is not itself the user's public workflow concept

## Synced Support Skill

Use this label when:

- an external integration has already materialized a private support skill into
  the installed Charness plugin support surface
- the skill should stay off the public top-level surface
- the right answer is "read this synced support skill on demand" rather than
  "pretend the integration entry is the whole story"

## External Integration

Use this label when:

- the capability depends on an upstream binary or upstream support skill
- the repo should consume it through manifest, install/update/doctor policy
- or the host allows an external skill ecosystem rather than local ownership
- if an installed support skill exists, cross-link to it instead of hiding it

## Missing Capability

Classify the gap:

- new public skill
- new support skill
- new integration manifest

Do not blur these just to make the answer sound more complete.

## Discoverability Claim

`find-skills --recommend-for-task` proves that workflow language can route a
task to a hidden support skill without the user naming `support/<id>` first.

The canonical example is `support/specdown`:

- the strong-trigger set lives in the `strong_intent_triggers` field of
  `integrations/tools/specdown.json` and currently lists `*.spec.md`,
  `.spec.md`, `docs/specs`, `run:shell`, `check:jq`, `specdown`,
  `specdown report`, `specdown HTML report`, `specdown -filter`,
  `executable spec`, and `spec syntax`. `scripts/list_capabilities_lib.py`
  reads the field via `_strong_triggers_for` and gates support-skill
  surfacing on it (broad `intent_triggers` populates the match pool;
  `strong_intent_triggers` precision-gates which matches activate the skill)
- positive routing is exercised by the authoring-repo-internal
  `tests/test_find_skills_task_recommendations.py::test_list_capabilities_recommends_support_skill_from_task_text`,
  which asserts that a task mentioning `docs/specs`, `.spec.md`, `check:jq`,
  and `specdown` returns the support skill, its key references
  (`syntax.md`, `best-practices.md`, `cli.md`, `report.md`, `config.md`),
  and a `next_step` that points at the SKILL body; the other configured
  triggers are not individually proven by this fixture
- negative proof keeps generic `report.json` or `doctest output` from routing
  unrelated work through `support/specdown`
  (`test_list_capabilities_does_not_recommend_specdown_from_weak_task_text`)

This claim is reusable. To prove the same routing for another support skill,
add the strong-trigger set, ship a positive fixture that asserts the support
skill, references, and `next_step`, and ship at least one negative fixture so
incidental terminology overlap does not cause false positives.
