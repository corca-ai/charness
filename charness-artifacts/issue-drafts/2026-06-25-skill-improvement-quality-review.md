## Situation

After improving `quality`, `gather`, `issue`, `handoff`, and the JS mutation
closeout path, the remaining public skill improvement candidates should be
tracked deliberately instead of handled as opportunistic edits.

The next target set is:

- `retro`
- `critique`
- `spec`
- `impl`

## Experience

The operator wants the next session to evaluate these skills one by one through
the improved `quality` skill, including whether the `quality` skill itself is
now good enough to surface useful skill-improvement proposals from a fresh
session. The risk is that improvements remain scattered across handoff notes,
critique packets, and deferred decisions without a single issue that names the
ordered scope.

## Evidence

- Current handoff says to continue planner-first patterns and then build
  per-skill Cautilus fixtures.
- Multiple critique packets note follow-up opportunities such as retro not
  consuming prepared packets.
- The public skill bodies for `retro`, `critique`, `spec`, and `impl` are still
  comparatively large and workflow-heavy, so they are good candidates for the
  same philosophy already applied to `quality`: code/scripts own mechanical
  steps, the skill body preserves intent and progressive disclosure, and
  references are routed deliberately.
- The operator explicitly requested this tracking issue so the next session can
  run `quality` on each target rather than jumping into ad hoc rewrites.

## Desired Outcome

Track and complete a deliberate skill-improvement pass for `retro`, `critique`,
`spec`, and `impl`.

For each skill:

- run the current `quality` workflow against the skill as the first lens;
- decide whether the issue is a body-design problem, reference-routing problem,
  helper-script problem, validator/test problem, or no-change decision;
- preserve the skill's essential intent while reducing unnecessary workflow
  prose, brittle coupling, and hidden next-action burden;
- keep tests/fixtures from overfitting to exact prose where a behavior contract
  is the real target;
- record explicit non-claims and deferred follow-ups.

## Acceptance Sketch

- A per-skill assessment exists for `retro`, `critique`, `spec`, and `impl`.
- Any implemented improvement includes focused tests or validators at the right
  layer.
- If `quality` misses a legitimate improvement opportunity, that miss is
  treated as evidence about `quality` itself and either fixed or recorded with a
  concrete follow-up.
- If a skill should not change, the decision says why and cites the evidence.

## Suggested Order

1. `retro` — strongest current signal; repeated notes say it does not consume
   prepared critique packets today.
2. `critique` — high leverage and broad closeout impact; handle after one
   narrower candidate calibrates the method.
3. `spec` — central contract-writing skill, likely benefits from clearer
   planner/helper split.
4. `impl` — high-use execution skill; improve after the preceding passes show
   the right pattern.

## Non-Goals

- Do not rewrite all four skills in one broad patch.
- Do not shrink prose merely to reduce line count.
- Do not add Cautilus fixtures that coach the target skill instead of observing
  behavior.
- Do not treat this issue as blocking #392 or #371; it is the next skill-quality
  track after the current open gather/browser work is sequenced.
