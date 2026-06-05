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
- **Slice 3 — the ratchet** (commit `43e70e4c`, delivers goal 2): committed
  baseline [`scripts/boundary-bypass-baseline.json`](../scripts/boundary-bypass-baseline.json)
  under a `no_increase` policy, a `# why:`-rationale exemption list
  [`scripts/boundary-bypass-exemptions.txt`](../scripts/boundary-bypass-exemptions.txt),
  and the standing `check-boundary-bypass-ratchet` gate wired in `run-quality.sh`.
  The ratchet-correctness fixes landed with it (separate internally-spawning
  targets, drop the `.read_text(` over-match, rename "candidate"), which is why
  the committed baseline now reads **96 candidates / 57 convertible /
  38 internally-spawning / 23 keep-boundary** — far below the advisory probe's 121
  "convertible" once internally-spawning targets are split out. The probe is now
  *costly*, not just *visible*.

## Honest Non-Claims (what is NOT yet true)

- **Goal (2) ships; goal (1) is barely started.** The ratchet makes bad patterns
  *costly*, not just *visible* (see Done). But the committed baseline is a freeze
  line, not a reduction: 57 convertible candidates remain. Lowering it requires
  real in-process conversions (goal 1, below), not exemptions.
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

1. **Convert the backlog** (goal 1, raises A): the import-safe `inventory_*`
   cluster (subprocess → in-process `*_lib`/`main()` calls, like
   [`test_check_coverage_inventory.py`](../tests/quality_gates/test_check_coverage_inventory.py)
   already does). Use `Repo().build()` for the
   on-disk fixture without `run_at`. Skip targets that shell out internally.
   *Started:* [`test_quality_standing_gate_verbosity.py`](../tests/quality_gates/test_quality_standing_gate_verbosity.py)
   (direct `inventory()` lib call) and
   [`test_quality_lint_ignores.py`](../tests/quality_gates/test_quality_lint_ignores.py)
   (in-process `main()` with captured stdout, preserving its adapter-wrapped
   payload) are converted — the two documented patterns. Baseline convertible
   57→55. Remaining convertible
   `inventory_*` tests: `inventory_adapter_gate_design`, `_brittle_source_guards`,
   `_cli_side_effect_probes`, `_public_spec_quality`, `_skill_ergonomics` (skip the
   internally-spawning `_entrypoint_docs_ergonomics`, `_ubiquitous_language`).
   *Per conversion:* regenerate the
   [boundary-bypass baseline](../scripts/boundary-bypass-baseline.json) to canonical
   form (`inventory_boundary_bypass_lib.find_boundary_bypass_candidates` →
   `boundary_bypass_ratchet_lib.build_baseline`, as commit `0604f3d2` did) and sync the
   plugin mirror — the `no_increase` ratchet tolerates decreases silently, so skipping
   the regen leaves a stale baseline that never records the convertible-count drop.
2. **`quality` lens boost** (goal 3, portable): extend
   [testability-and-selection](../skills/public/quality/references/testability-and-selection.md)
   to name (a) DSL ergonomics signals — lazy / composable / implementation-simple —
   and (b) "a test needing the heavy repo-builder DSL is a prompt to ask whether
   the behavior is in-process reachable." Write against the now-validated concrete
   shapes, not speculation.
3. **Portable skillification** (goal 3): a `quality` adapter block + reference
   defining the boundary-bypass payload contract + ratchet policy stack-neutrally
   (mirror [mutation-testing](../skills/public/quality/references/mutation-testing.md)).
   A Go/TS repo then ships its own one-screen probe emitting the same payload.
4. **DSL follow-ups** (from slice-1 critique): `env=` merge semantics (when the
   first explicit-`env` control_plane test migrates), broad `seed_repo` sweep.
