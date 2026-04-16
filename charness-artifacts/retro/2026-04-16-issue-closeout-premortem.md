# Issue Discovery Dogfood Retro

## Context

This retro corrects the scope of the previous closeout retro. The real question
is not only how to close GitHub issues #25-#31 safely. Those issues were found
while dogfooding charness skills in other repos. The sharper question is: how
should charness development have surfaced those same failures earlier, before
external dogfood made them obvious?

## Evidence Summary

- Issues #25-#31 covered failures in `quality`, `narrative`, `init-repo`,
  `gather`, and `find-skills`.
- The failures were mostly agent-behavior and mature-repo-fit gaps, not pure
  unit-test bugs.
- Final fixes landed on `main` through `04dcf01`; the retro was first persisted
  too narrowly and corrected after the user pointed out the scope mismatch.
- `./scripts/run-quality.sh` and push-time pre-push passed with
  `37 passed, 0 failed`.

## Waste

- Charness development tested many scripts as producers, but not enough skills
  as products used by an agent under messy prompts. The missing layer was
  prompt-to-skill and repo-context dogfood.
- We validated greenfield/bootstrap paths more than mature-repo sanity-check
  paths. That let #30 survive until `init-repo` was run on a real mature repo
  with local naming conventions.
- We treated public skill descriptions as documentation, not as routing
  classifiers. That let #28, #29, and #31 survive until a live agent picked
  WebFetch or Bash instead of the intended skill.
- We did not run hostile prose/source mutation checks against quality contracts.
  That let #27 survive until a real README rewrite hit hard-wrap plus fixed
  substring guards.
- We used narrative less often on charness's own first-touch surfaces than on
  sibling repo landing surfaces. That let #26 surface during a cautilus README
  rewrite instead of a charness README/docs rewrite.

## Earlier Discovery Points

- #25 would likely have surfaced from a standing-gate operability review of
  charness and sibling-style fixtures: run the quality skill in review mode, not
  only the quiet pre-push gate, and inventory runner reporter, orchestrator
  output, per-gate chatter, phase signal, and verbose escape hatch.
- #26 would likely have surfaced from using `narrative` on charness's own README
  or plugin landing surface with a declared audience, comparables, claim audit,
  and compression metric before applying it to cautilus.
- #27 would likely have surfaced from a quality mutation fixture that inserts a
  fixed-string source guard over hard-wrapped prose, then asks whether the
  bootstrap policy makes that fragile pair constructible.
- #28 and #29 would likely have surfaced from prompt-routing drills using only
  installed skill descriptions and generated AGENTS hints: Slack URL, Notion
  page, Google Doc, arbitrary URL, and "which skill handles this?" prompts.
- #30 would likely have surfaced from an `init-repo` fixture corpus of mature
  repos with legitimate naming divergence: lowercase `install.md`, roadmap as
  `docs/master-plan.md`, and intentionally absent uninstall docs.
- #31 would likely have surfaced from a Bash-biased adversarial drill: "specdown
  support skill 있죠?" should call `find-skills` before filesystem search, and
  one discovery call should return enough metadata to be more useful than `ls`.

## Critical Decisions

- The useful recovery was fresh-eye premortem before remote close, but the
  better upstream fix is earlier dogfood fixtures that encode these lived
  failure modes.
- The durable change should not be "remember to be more careful." It should be a
  small dogfood matrix that exercises skill selection, mature repo inspection,
  first-touch narrative rewrite, and quality fragility inventory.

## Expert Counterfactuals

- Gary Klein's premortem lens would have asked during charness development:
  "If this skill fails in a sibling repo, what exact prompt or repo shape will
  make it fail?" That points to prompt-routing and mature-repo fixtures, not
  more implementation-only unit tests.
- Atul Gawande's checklist lens would have required a small release/dogfood
  checklist before considering a skill improvement complete: one messy prompt,
  one mature repo fixture, one generated AGENTS surface, and one full standing
  quality pass.

## Next Improvements

- workflow: Before closing a skill-behavior slice, run a "consumer dogfood"
  check: give the skill a realistic user prompt and only the surfaces an agent
  would actually see.
- workflow: Maintain a small mature-repo fixture corpus for `init-repo` and
  `quality`, including divergent but valid naming and intentionally absent
  optional surfaces.
- workflow: For public skill descriptions, treat frontmatter as classifier
  training data. Test concrete prompts against the expected skill route.
- capability: Add an issue-batch or dogfood helper that emits a matrix:
  prompt/repo shape, expected skill, expected artifact, and acceptance evidence.
- capability: Add adversarial fixtures for "Bash is easier than the skill" so
  `find-skills` must beat filesystem search for named support capabilities.
- memory: Keep this as the repeat trap: charness can pass producer-side gates
  while still failing consumer-side dogfood.

## Persisted

yes: `charness-artifacts/retro/2026-04-16-issue-closeout-premortem.md`
