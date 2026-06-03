# Testability + Test-DSL Initiative

Working record for the test-quality effort started 2026-06-03. Tracks the
original intent, the decisions taken, what shipped, and the remaining
obligations. Update this doc as slices land; link it from
[handoff](./handoff.md).

## Original Intent

Raise this repo's test quality, with three conjoined goals (user-stated):

1. **This repo improves** — concretely, reduce test boilerplate and raise
   testability.
2. **Good patterns stay, bad patterns can't easily take root** — a *structural
   ratchet*, not prose: a measure that cannot silently regress.
3. **Skillify so other repos benefit** — portability is critical: NOT coupled to
   Python, NOT coupled to charness's repo layout.

The seed task was narrower: "build a lazy-eval, highly composable, minimal test
DSL." The conversation widened it to the three goals above once we separated two
ideas that were sharing the word *testability*.

## Key Reframe (load-bearing)

Two different "goods" were being conflated:

- **A. Production-code testability** — can a behavior be reached cheaply,
  in-process, to check it? Raised by *moving the test's call site* from a
  spawned subprocess to an in-process import + call (or a `*_lib` function).
- **B. Test-code maintainability** — are test files DRY/readable? Raised by the
  **DSL**.

The DSL improves **B, not A**. A subprocess test stays a subprocess test after
you prettify it; coverage/type/mutation tools still cannot see across the
process boundary (this repo has no subprocess coverage hook — `COVERAGE_PROCESS_START`
is unused — and instead drives coverage via in-process `exercise_*` harnesses).
So **DSL usefulness is roughly the inverse of testability**: the heavy
`seed_repo` + subprocess tests it helps most are exactly the lower-testability
zone the [testability lens](../skills/public/quality/references/testability-and-selection.md)
flags as `Weak`. The DSL is an accelerator that must not *comfort-pave* that
structure — hence pairing it with a testability sensor.

## Decisions

- **Skill boundary = C** (no new skill). `quality` keeps test-quality
  *diagnosis/recommendation* (portable); the DSL *authoring* is repo `impl`. A
  test skill, if ever, is a support-layer extraction, not a public skill — a
  stack-specific DSL cannot stay portable as a public skill.
- **3-layer architecture** (mirrors the proven `mutation_testing` /
  `coverage_floor` seams):

| Layer | Owner | Portable? |
| --- | --- | --- |
| policy · payload contract · ratchet · exemptions | `quality` skill | yes (no language/layout tokens) |
| stack/layout-specific probe | repo (`scripts/`, adapter command slot) | no — all coupling confined here |
| test-ergonomics DSL | repo `impl` | no — per language |

## Done

- **Slice 1 — test DSL** (commit `1e857cf0`): [`tests/dsl.py`](../tests/dsl.py)
  `Repo` (frozen, lazy, composable tmp-repo spec) + `Result` (chainable
  assertions) + `run_at`/`run_raw`; self-test
  [`tests/test_dsl.py`](../tests/test_dsl.py); migrated
  [`test_retro_lesson_selection_index.py`](../tests/quality_gates/test_retro_lesson_selection_index.py)
  (4 tests) + one `validate_integrations` function. Verified (ruff/lengths/attention + 2094-pass subset). Critique:
  [test-dsl-first-slice](../charness-artifacts/critique/2026-06-03-test-dsl-first-slice-critique.md).
- **Slice 2 — boundary-bypass advisory probe** (this commit):
  [`scripts/inventory_boundary_bypass_lib.py`](../scripts/inventory_boundary_bypass_lib.py)
  plus a thin CLI and an in-process test (dogfoods the principle: it tests the
  probe by importing the `_lib`, building synthetic repos via the DSL's
  `build()`). Detects
  tests that spawn an import-safe entrypoint when in-process reachable. Advisory
  only. **Baseline on this repo: 134 candidates (121 "convertible", 13 likely
  keep-boundary) across 235 test files.** Critique:
  [boundary-bypass-probe](../charness-artifacts/critique/2026-06-03-boundary-bypass-probe-critique.md).

## Honest Non-Claims (what is NOT yet true)

- **This does NOT yet satisfy goal (2).** The probe is a *sensor with no teeth*:
  no gate wiring, no committed baseline, no no-increase ratchet. Bad patterns are
  now *visible*, not yet *costly*. The ratchet is the named next obligation (below).
- **Placement honesty:** boundary-spawn detection is *not* inherently
  un-portable — [`standing_test_economics_lib.py`](../skills/public/quality/scripts/standing_test_economics_lib.py)
  already ships a multi-language spawn detector (`nested_cli_fanout`) inside the
  public skill. This probe is the *stack-specific refinement* of that smell
  (`is_import_safe` + in-repo target resolution), which is the genuine
  Python+layout-coupled delta and so is correctly repo-owned.
- **`convertible_count` overstates the actionable surface:** ~30% of import-safe
  targets themselves spawn subprocesses/git internally, so converting their tests
  moves the boundary inward rather than removing it. The count is candidates, not
  guaranteed wins.
- The detector over-reports ~7–9% (a script path named only in an assertion
  string is counted); acceptable for advisory, disclosed in the payload notes.

## Remaining (sequenced)

1. **The ratchet** (delivers goal 2): committed baseline, a `no_increase` policy,
   a consumer-declared exemption list (`# why:` rationale, mirror
   [coverage-floor-policy](../skills/public/quality/references/coverage-floor-policy.md)),
   and advisory→standing wiring in `run-quality.sh`. Route gate design through
   `quality`. Fix ratchet-correctness first: `.read_text(` over-match in
   `behavior_assert` (W3), `convertible_count` jitter, "candidate" naming (J5),
   and subtract/flag internally-spawning targets (W2).
2. **Convert the backlog** (goal 1, raises A): start with the import-safe
   `inventory_*` cluster (subprocess → in-process `*_lib`/`main()` calls, like
   [`test_check_coverage_inventory.py`](../tests/quality_gates/test_check_coverage_inventory.py)
   already does). Use `Repo().build()` for the
   on-disk fixture without `run_at`. Skip targets that shell out internally.
3. **`quality` lens boost** (goal 3, portable): extend
   [testability-and-selection](../skills/public/quality/references/testability-and-selection.md)
   to name (a) DSL ergonomics signals — lazy / composable / implementation-simple —
   and (b) "a test needing the heavy repo-builder DSL is a prompt to ask whether
   the behavior is in-process reachable." Write against the now-validated concrete
   shapes, not speculation.
4. **Portable skillification** (goal 3): a `quality` adapter block + reference
   defining the boundary-bypass payload contract + ratchet policy stack-neutrally
   (mirror [mutation-testing](../skills/public/quality/references/mutation-testing.md)).
   A Go/TS repo then ships its own one-screen probe emitting the same payload.
5. **DSL follow-ups** (from slice-1 critique): `env=` merge semantics (when the
   first explicit-`env` control_plane test migrates), broad `seed_repo` sweep.
