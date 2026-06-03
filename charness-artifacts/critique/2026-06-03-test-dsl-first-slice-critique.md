# Code Critique: Test DSL First Slice

Date: 2026-06-03

Fresh-Eye Satisfaction: parent-delegated (4 bounded fresh-eye general-purpose subagents — 3 angle: Jackson/Weinberg/Gawande + 1 counterweight; read-only in the shared parent worktree, prior versions inspected via `git show`)

Packet Consumed: charness-artifacts/critique/2026-06-03-091616-packet.md

Target: skills/public/critique/references/code-critique.md

## Scope

- Change: new test DSL `tests/dsl.py` (`Repo` — frozen, lazy, composable tmp-repo
  spec; `Result` — chainable assertions over a finished subprocess; `run_at`/`run_raw`),
  self-test `tests/test_dsl.py`, and a first-slice migration of
  `tests/quality_gates/test_retro_lesson_selection_index.py` (4 tests, full) plus
  one function in `tests/control_plane/test_integrations_validation.py`.
- Goal: lazy-eval, high composability, minimal implementation. Explicitly a FIRST
  SLICE; broad migration of the ~141 quality_gates `seed_repo` files is deferred.
- Verification at critique time: ruff clean, check_python_lengths clean (new files
  not in warn band), test-production ratio 0.85/1.00, validate_attention_state
  clean, declared repo-python pytest subset 2094 passed / 4 skipped.

## Verdict

SHIP — no behavioral change required. Folded a docstring/diagnostic pass; the
remaining angle pressures are over-worry or deferred against the minimal-first-slice
and high-composability framing.

## Angles

- Jackson (problem framing), Weinberg (diagnostic/behavior-preservation), Gawande
  (operational/silent-failure), plus a separate counterweight triage pass.
- Agreed load-bearing positive: the retro before/after deletes the per-file
  `seed_repo` (24 lines) into a shared `RETRO = Repo().adapter(...)` and collapses
  the `returncode==0/json.loads/read_text` couplets into `.ok()`/`.json`/`.file_json()`.
  The core thesis holds; the value is portfolio-wide across the deferred sweep.

## Folded Before Ship (bundled into tests/dsl.py)

- **Env contract documented.** `_run` passes `env=None` (inherits the full parent
  env, including the conftest-autouse `CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS`
  and `GIT_CEILING_DIRECTORIES`); an explicit `env=` *fully replaces* rather than
  merging onto `os.environ` like the area `support.run_script`. Behavior-preserving
  for this env-less slice (verified rc/marker identical), but the latent foot-gun
  is now a documented contract in the module docstring.
- **Multi-build re-materialization documented.** `Repo.run()` builds a fresh repo
  and re-evaluates thunks each call; the docstring now directs multi-step flows to
  `build()` + `run_at` (the one multi-step migrated test already does this).
- **Scope boundary documented.** Module docstring now states the DSL targets the
  subprocess + tmp-repo idiom only; in-process direct-call tests keep plain pytest.
- **`ok()` diagnostics widened.** Failure message now includes exit code, repo path,
  and both stdout and stderr (was stderr-only), so `--json` scripts that fail on
  stdout are debuggable without a re-run.

## Over-Worry Dismissed (counterweight)

- **Cut `merge`/`files`/`run_raw`/`stdout_has` as speculative.** Dismissed — these
  are the composable primitives the explicit high-composability goal asked for, all
  covered by self-test assertions; `merge` is the mechanism a shared base spec reuses
  across files in the deferred sweep. Cutting them is YAGNI applied against a written
  requirement.
- **Force a required `failed(code=...)`.** Dismissed — every migrated failure pairs
  `.failed(1)` with `.stderr_has("real message")` (the self-test models the pairing),
  so no assertion was weakened; `code=None` keeps a legitimate "just non-zero" escape.
- **`Result.json` property vs method peers.** Dismissed — cosmetic; `res.json` reads
  naturally and the migration already uses it.

## Deliberately Not Doing / Deferred

- **`env=` merge semantics** (overlay onto `os.environ` like `support.run_script`):
  deferred until the first explicit-`env` control_plane test migrates onto the DSL.
  Documented as a contract for now; not implemented because no consumer exists yet.
- **Sibling `validate_integrations` migrations + `write_manifest_schema` removal:**
  the migrated file is intentionally mixed (1 of 14); the doctor tests legitimately
  keep `seed_control_plane_repo`/`run_script`, so the file is permanently mixed by
  design. The 3 same-shape rejection siblings are a cheap later sweep, out of this
  slice's "module + 3-5 tests" scope. Not reverted.
- **Broad ~141 quality_gates `seed_repo` sweep:** the main deferred follow-up.
- **`quality` testability-lens boost** (lazy/composable/simplicity as recommend-only
  signals) — the agreed portable closeout for routing this capability, to be written
  against this now-validated concrete shape.

## Next Move

This slice ships as-is. Follow-ups above are deferred, not blockers.
