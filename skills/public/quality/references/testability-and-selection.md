# Testability And Test Selection

Use this reference when quality review touches slow tests, mutation testing,
changed-file test selection, broad end-to-end coverage, or claims that a test
tool can identify the relevant subset.

## Principle

Testability is a structural quality property. A codebase is more testable when
the smallest meaningful behavior can be exercised through a narrow, stable,
in-process surface, while delivery boundaries such as CLIs, subprocesses,
network protocols, browser sessions, schedulers, and packaging entrypoints
remain covered by thinner contract smokes.

Do not let an affected-test tool hide an untestable structure. Observation
tools are accelerators and diagnostics; they should not be the only reason an
operator can find or run the tests for a small change.

Do not claim that deterministic affected-test selection is always possible.
The healthier contract is that the repo should expose a cheap deterministic
candidate subset, then use broader gates or observation data until the subset
has earned trust.

When the selector cannot discover changed files, affected tests, or observed
dependencies, do not treat that as an empty set. Either run the broader safety
gate or fail with a diagnostic that names the failed discovery command.

## Review Questions

Ask these before recommending a new test runner, mutation runner, cache, or
runtime budget:

- Can the core behavior be invoked without starting the delivery boundary?
- Is the delivery boundary thin enough that most behavior assertions live below
  it?
- Can a maintainer predict a fast test subset from module, package, target, or
  component boundaries without reading a tool database?
- Are expensive tests tagged, named, or targeted by cost and boundary, not by a
  manually maintained source-to-test dependency map?
- Does the fast subset fail for the behavior defect, while the broader smoke
  proves packaging, process, protocol, or deployment wiring?
- Are observation-based selectors checked against a full-suite or broader-suite
  backstop often enough to reveal hidden dependencies?

Classify a repo as `Weak` when broad tests are compensating for behavior that
should be reachable through a smaller surface. Classify a repo as `Missing`
when no predictable fast path exists for routine behavior changes.

## Healthy Shape

A healthy stack usually has these layers, regardless of language:

- core behavior tests: fast, deterministic, import/in-process/library-level, and
  close to the behavior under change
- boundary adapter tests: still mostly in-process, but exercising argument
  parsing, request/response shaping, serialization, config, or environment
  handling through explicit seams
- real-boundary smokes: small count, real process or protocol, focused on
  entrypoint installation, exit status, stdout/stderr/API shape, packaging, or
  cross-process isolation
- end-to-end or operator workflows: few, expensive, and clearly marked as
  release, integration, or scheduled confidence rather than default local
  proof

Prefer structural naming or target conventions over hand-maintained dependency
maps. Examples: one production module has a corresponding fast test file, a
package target owns its tests, a component target declares its local tests, or a
domain module exposes a testable service/function below the CLI or UI shell.
The convention should be cheap to infer and cheap to violate visibly.

## Markers And Tags

Tags and markers are useful when they describe cost, boundary, or environment:

- fast/unit/core
- integration/protocol/network/database
- subprocess/real-binary/packaging
- slow/release/scheduled
- flaky/quarantine, only when paired with a repair owner and revisit condition

Avoid tags that ask humans to maintain a source dependency graph by hand, such
as a long list of covered files on each test. Those tags drift away from real
execution and make quality look deterministic while remaining manual.

## Observation-Based Tools

Coverage-guided or dependency-observing tools can be valuable when introduced
as a diagnostic layer:

- run the full or broad suite once to build the observation baseline
- use the selected subset for local speed or exploratory mutation work
- periodically compare selected-subset results with the broad gate
- treat misses as hidden dependency or test isolation findings, not only as
  tool defects
- keep the broad correctness gate until the selector has local evidence and a
  failure mode operators understand

For mutation testing, do not assume a runner's native test command gives
affected-test selection. Many mutation runners repeatedly execute one fixed
test command per mutant unless they are explicitly integrated with coverage or
dependency data. A mutation score should say whether unselected, unobserved, or
uncovered mutants are scope gaps rather than silently counting them as quality
proof.

## Tradeoffs

Real-boundary tests are not smells by themselves. They catch packaging,
entrypoint, process-environment, filesystem, isolation, protocol, and
installation failures that in-process tests often cannot prove. They become a
smell when they are the primary way to verify ordinary domain behavior.

Import-only or in-process-only tests are also not a complete strategy. They
should carry most behavior proof, but they need a thin shell of real-boundary
tests to prove that the shipped interface still reaches that behavior.

## Duplicate-Pressure Cleanup vs Hiding Test Bodies

Broad duplicate, length, or pressure gates over a test suite catch accumulated
debt, but a passing percentage is not the goal and the failure response matters
more than the number. When such a gate fails, distinguish two very different
cleanups:

- **Structural cleanup (good)**: extract fixture builders, lifecycle wrappers
  (setup/teardown), command runners, and shared assertions into clearly named
  support helpers, while the behavioral intent — what the test asserts and why —
  stays in the `.test.*` / `*_test.*` file. The behavior is still readable at the
  test site; only the mechanical scaffolding moved.
- **Hiding test bodies (bad)**: moving the behavioral assertions themselves into
  support files so the duplicate gate stops counting them. This games the metric,
  scatters the behavior contract away from the test, and makes the suite harder
  to read and trust. Classify this as a `Weak` finding even when the gate passes.

The test is: could a reader still see what behavior each test proves by reading
the `.test.*` file alone? If the assertions and intent left the test file to
satisfy a counter, the cleanup is hiding, not structuring.

When the gate fails, do not stop at reporting the failing percentage. Identify
whether the pressure is new (introduced by the current change) or accumulated
(pre-existing suite debt), then name the smallest next structural extraction
(the specific shared builder, wrapper, runner, or assertion to lift) rather than
only failing the broad gate. This keeps repair cheap and incremental instead of
deferring an expensive late unwind. Charness owns this detection and
recommendation contract; the duplicate/length gate itself stays a repo-local
deterministic gate, not a Charness-owned runner.

## Language Notes

Keep language-specific details here or in sibling references, not in
`SKILL.md`.

- Python/pytest: path, node id, keyword, and marker selection are explicit test
  selection mechanisms. Prefer importable core logic and thin CLI/subprocess
  smokes. Dynamic imports, fixtures, `conftest.py`, monkeypatching, subprocesses,
  and plugins make purely static affected-test inference incomplete. Tools such
  as pytest-testmon or build-system selectors can help, but should be treated
  as diagnostics until compared against the broader suite.
- JavaScript/TypeScript: runners such as Jest or Vitest may offer watch-mode or
  changed-file selection based on module graphs. Still inspect whether the
  graph is proving behavior locality or merely hiding broad component or
  browser-level tests.
- Go/Rust/JVM and build-system based repos: package, crate, module, or build
  targets, including Pants/Bazel-style build graphs, often provide deterministic
  selection and cache boundaries. Review whether target granularity maps to
  behavior seams rather than one oversized integration target.

## Recommended Outcomes

Prefer recommendations in this order:

1. Split production code so core behavior is reachable below the boundary.
2. Move repeated broad assertions into focused lower-layer tests.
3. Keep or add a small real-boundary smoke for the shipped interface.
4. Add markers/tags for cost and boundary selection.
5. Add deterministic target or naming conventions for predictable fast subsets.
6. Add observation-based selection as an accelerator and hidden-dependency
   detector.
7. Add runtime budgets or mutation sampling only after the structure and
   selection boundary are honest.

When a broad duplicate/length/pressure gate over tests fails, apply the same
ordering: prefer extracting shared scaffolding (builders, lifecycle wrappers,
command runners, shared assertions) over either widening the threshold or
hiding assertions in support files, and report the smallest next extraction.
