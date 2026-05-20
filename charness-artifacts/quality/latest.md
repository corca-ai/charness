# Quality Review
Date: 2026-05-20

## Scope

Current slice: extend the public `quality` skill so testability and
affected-test selection are reviewed as structure-first code quality, not only
as runner configuration. The portable core in `SKILL.md` now links to
`references/testability-and-selection.md`; Python/pytest, Jest/Vitest,
pytest-testmon, and Pants/Bazel examples stay in the reference and plugin
mirror.

## Current Gates

- Plugin export synced with `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- Dogfood acceptance now requires affected-test selection to be treated as
  structural testability before caches, observation tools, or broader runtime
  budgets.
- Focused doc test guards that detailed tool names stay out of `SKILL.md` and
  the reference carries the negative deterministic-selection claim.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` <!-- reproduction-source --> rendered by `render_runtime_summary.py`.
- runtime hot spots: prior rendered samples still show pytest and check-coverage as the dominant timed phases; this slice did not change runtime budgets.
- coverage gate: changed-surface closeout and pre-commit coverage-related validators passed.
- evaluator depth: `validate_cautilus_proof.py` passed; planner reported `next_action: none` and required dogfood/scenario review rather than live Cautilus execution.

## Healthy

- `quality` now asks whether core behavior is reachable through a narrow,
  predictable candidate subset before recommending affected-test tools.
- The new reference explicitly rejects claiming deterministic affected-test
  selection is always possible; it requires broader gates or observation data
  until a focused subset earns trust.
- Mutation-testing and standing-gate references now cross-link testability so
  sampling, timeout, or cache work does not hide broad boundary-heavy tests.
- Checked-in plugin copies include the same skill core, references, and helper
  script changes.
- Agent-browser orphan daemon state that blocked the first pre-push attempt was
  cleaned with the repo-owned runtime guard.

## Weak

- This is a public-skill guidance and dogfood slice, not yet a structural
  refactor of this repo's own mutation runner. Cosmic Ray still uses the
  declared test command rather than per-mutant affected-test selection.
- The quality artifact is intentionally concise; detailed prior seed-cache and
  orphan-cleanup history remains in git history and earlier quality artifacts.

## Missing

- No maintained Cautilus scenario-registry edit; `quality` is
  HITL-recommended and this slice records deterministic dogfood plus delegated
  critique instead.
- No release/version bump yet, so installed users receive this after the next
  plugin update/release path consumes the pushed repo state.

## Deferred

- Repo-local structural testability refactor for mutation targets: split or
  expose faster lower-layer behavior tests before adding another selector.
- Evaluate observation-based selectors such as pytest-testmon only after the
  deterministic candidate subset structure is visible enough to compare misses
  against the broader gate.

## Advisory

- command: `inventory_skill_ergonomics.py --skill-path skills/public/quality`
  reported `zero_heuristic_findings` and `prose_review_status=still_required`.
- artifact: `docs/public-skill-dogfood.json` now records the consumer-facing
  acceptance requirement for structure-first affected-test selection.
- evidence: two delegated reviewers inspected design and implementation; the
  second reviewer found dogfood and fragile-test gaps that were fixed.

## Delegated Review

- status: executed. `Dirac` critiqued the design and required language-neutral
  core wording, cost/boundary markers instead of manual source maps, and
  observation tools with broad-suite backstops.
- status: executed. `Archimedes` reviewed the implementation, found that
  dogfood did not yet require the new consumer behavior and that a doc test
  pinned a fragile substring; both were fixed.
- slow-gate lenses reviewed: fixture-economics, parallel-critical-path, and
  duplicated-proof remain covered by the standing-test economics path; this
  slice adds testability selection as an adjacent structural lens.

## Commands Run

- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- focused pytest for the quality doc contract and public-skill dogfood case
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/check_skill_contracts.py --repo-root .`
- `python3 scripts/validate_current_pointer_freshness.py --repo-root .`
- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`
- `python3 scripts/agent_browser_runtime_guard.py --repo-root . --cleanup-orphans --execute`
- `git push origin main` pre-push quality gate initially found artifact length
  and agent-browser orphan issues; both were repaired before retry.

## Recommended Next Gates

- active `AUTO_EXISTING` because pre-push previously caught local machine-state
  drift: retry `git push origin main` after the artifact-length and
  agent-browser-orphan repairs.
- passive `AUTO_CANDIDATE` until the repo-local mutation design resumes:
  refactor mutation targets toward predictable lower-layer behavior tests before
  adding observation-based affected-test selection.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
