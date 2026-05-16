# Quality Cautilus Behavior Testing Contract

- Date: 2026-05-16
- Charness issue: [#168](https://github.com/corca-ai/charness/issues/168)
- Cautilus issue: [corca-ai/cautilus#44](https://github.com/corca-ai/cautilus/issues/44)
- Current quality anchor:
  [skills/public/quality/references/behavior-testing.md](../../skills/public/quality/references/behavior-testing.md)

## Problem

#168 started as a broad question: should Charness expose mutation-testing-like
robustness testing for user behavior? The better boundary is narrower. Charness
should make `quality` capable of noticing when a repo needs behavior proof and
of recommending or recording a Cautilus-backed experiment. Cautilus should own
the actual evaluator semantics, execution, and result shape.

Without that split, Charness risks either under-serving installed repos
(`quality` never thinks to ask for behavior proof) or overreaching into a
second behavior-test runner that will drift from Cautilus.

## Current Slice

Define the Charness-side contract for behavior-test recommendation:

- reframe #168 from "build user-action fuzzing in Charness" to "route behavior
  proof through quality toward Cautilus"
- open a Cautilus issue for the evaluator/result contract Charness needs
- add a quality reference that agents can use before proposing gates
- update handoff so the next session starts from this boundary

This slice is a design and routing slice, not a live evaluator implementation.

## Fixed Decisions

1. Charness does not own a behavior-test runner.
   - It may recommend behavior proof, preserve proof state, and wire adapter
     fields once Cautilus publishes a stable consumer contract.

2. Cautilus owns agent behavior evaluation.
   - The relevant current surfaces are `fixture`, `observation`, and
     `skill-experiment`; future behavior-test vocabulary should come from
     Cautilus, not be invented in Charness.

3. `quality` owns the first local user value.
   - Installed repos should get a concrete recommendation when deterministic
     tests are insufficient for an agent behavior seam.

4. Deterministic validators remain the default closeout path.
   - A behavior recommendation is not permission to run Cautilus. Live runs
     still require the planner and a log-backed behavior source.

5. Source-guard migration is adjacent but not identical.
   - Exact-prose guards can be retired into structure-aware validators,
     scenario-backed tests, or Cautilus behavior proof depending on what they
     actually protect.

## Probe Questions

1. What machine-readable result fields will Cautilus expose for consumer
   quality artifacts?
2. Should Charness add adapter fields such as `behavior_testing.declined`,
   `behavior_testing.surfaces`, or `behavior_testing.preferred_mode`, or wait
   until Cautilus #44 settles?
3. Can `quality` ship a read-only inventory that flags likely behavior seams
   without producing noisy recommendations?
4. Which Charness dogfood seam should be the first recommend-only fixture:
   routing robustness, handoff/resumption, skill-clone regression, or
   source-coverage behavior?

## Deferred Decisions

- Whether to install a reusable consumer workflow for behavior tests in
  installed repos.
- Whether Cautilus should support product UI/user-action fuzzing separately
  from agent behavior tests.
- Whether behavior-test recommendations should auto-file issues like mutation
  testing can do.

## Non-Goals

- Do not implement user-action fuzzing in Charness.
- Do not wrap pytest, lint, type checks, doc links, or deterministic validators
  under Cautilus.
- Do not run live Cautilus during routine quality review without an explicit
  log-backed behavior source.
- Do not promote exact-prose source guards into permanent policy.

## Deliberately Not Doing

This slice does not add `behavior_testing` adapter fields yet. Adding adapter
schema before Cautilus #44 defines the consumer contract would freeze local
vocabulary too early.

This slice also does not create a maintained Cautilus scenario for #168. There
is no failing behavior log yet; the current job is boundary definition and
recommendation design.

## Constraints

- Follow the repo Cautilus policy in [AGENTS.md](../../AGENTS.md): eval-only
  surfaces, planner consult, and `scripts/run_cautilus_eval.py` for live runs.
- Keep `quality` recommendation language honest about executed versus missing
  proof.
- Keep exact-prose guard review temporary and migration-oriented.

## Success Criteria

1. A maintainer can tell where #168 now lives: Charness `quality` recommends
   behavior proof; Cautilus defines and runs the proof.
2. Cautilus has a tracked issue for the missing consumer contract.
3. The quality skill has local guidance that can produce a behavior-test
   recommendation without inventing a runner.
4. The handoff points future sessions to this contract instead of reopening the
   broad product question from scratch.

## Acceptance Checks

- `gh issue view 44 --repo corca-ai/cautilus --json number,state,url,title`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`
- `./scripts/check-markdown.sh`

## Critique

- Risk: Charness may still drift into owning behavior execution because the
  quality skill naturally proposes gates.
  - Counterweight: the new reference explicitly limits Charness to detection,
    recommendation, configuration, and honest artifact state.
- Risk: Waiting on Cautilus #44 may make #168 feel unresolved.
  - Counterweight: the local value is still real once `quality` can name the
    seam and avoid false deterministic proof.
- Risk: behavior-test vocabulary may become another adapter taxonomy.
  - Counterweight: adapter fields are deferred until the Cautilus result
    contract exists.
- Fresh-eye status: blocked by current host policy unless the user explicitly
  asks for subagent critique in this turn; this is recorded rather than
  replaced by same-agent review.

## Canonical Artifact

This file is the canonical Charness-side contract for #168 until Cautilus #44
settles a consumer-facing behavior-test contract.

## First Implementation Slice

After Cautilus #44 is resolved, add the smallest `quality` implementation that
can emit a recommend-only behavior-test finding for one dogfooded seam, with
artifact fields that distinguish executed proof from missing or policy-blocked
proof.
