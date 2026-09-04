# Charness development

> Status: current
> Source of truth: this page and the executable commands it links
> Last verified: 2026-09-04

This page owns the shortest safe path for changing and dogfooding Charness
itself; detailed contracts stay with their owners.

## Start

Install the local dependencies once in a clean checkout:

```bash
npm ci
```

[Implementation discipline](./implementation-discipline.md) owns the change
loop; [README.md](../README.md) owns supported install.

## Local dogfood

To make an installed host use this checkout without pulling remote changes:

```bash
charness update --repo-root . --no-pull --skip-cli-install
```

The managed checkout entrypoint refreshes the managed CLI itself.

## Goal and issue work

An active goal is entered by its provider-backed parent objective, the
Issue-Native Goal Run:

```bash
./charness goal run --repo-root . --objective '/goal #<parent>'
```

[Goal lifecycle](./goal-lifecycle.md) owns parent/cursor state and issue
membership; [issue](../skills/public/issue/SKILL.md) owns GitHub writes and
readback. Neither exists in a local handoff or session hook.

## Worktrees and runtime

[Worktree prepare](./worktree-prepare.md) owns isolated mutation.

## Verification and export

Run focused tests for ordinary changes, the small quality lane when the core
contract is relevant, and the explicit full lane for broad, release, or review
work. [The standing pytest runner](../scripts/gates_support/run_standing_pytest.py)
is the pytest owner (xdist workers, chunk sizing, an external basetemp); a bare
`python3 -m pytest` gets none of them and is refused for a broad selection.

```bash
python3 scripts/gates_support/run_standing_pytest.py --repo-root . --pytest-target <path-or-nodeid>
python3 scripts/gates_support/run_standing_pytest.py --repo-root .
./scripts/run-quality.sh
./scripts/run-quality.sh --full --read-only
```

After an integration step the only green that counts is the standing runner
followed by the full read-only lane; any other green is a proxy
([P4](./design-north-star.md)). The slice order (commit, changed-line proof,
then the broad lane) and the serial `mutate -> sync -> verify -> publish` in
the parent are owned by
[parallel execution](./parallel-execution.md#disjoint-writers).

Each rule names the mechanism that holds it.

| Rule | Held by |
| --- | --- |
| A code push runs the full read-only and release lanes | the pre-push hook ([pushing](#pushing)) |
| `scripts/`/`skills/`/`docs/` commits need a matching release-lane receipt or `Slice-reopen:` | commit-msg [`check_release_lane_receipt.py`](../scripts/hooks/check_release_lane_receipt.py) |
| A stale `plugins/` mirror is regenerated or refused, never read as a failure | the standing runner and the quality engine ([generated surfaces](./operating-contract.md#generated-surfaces)) |
| A skipped gate is not a passed gate | the quality summary ([operating contract](./operating-contract.md#verification)) |
| A passing test is not a covered line | [`release_changed_line_coverage.py`](../scripts/mutation/release_changed_line_coverage.py), in the lane receipt and the pre-push hook |
| Production code spawns only through [`subprocess_guard.py`](../scripts/core/subprocess_guard.py) | [`check_subprocess_form.py`](../scripts/gates/check_subprocess_form.py) |
| A repo script's location is answered only by [`repo_layout.py`](../scripts/core/repo_layout.py) | [`check_script_lookup_form.py`](../scripts/gates/check_script_lookup_form.py) |
| A test never depends on wall-clock time | [`check_wall_clock_form.py`](../scripts/gates/check_wall_clock_form.py), record empty and shrinking only |
| A test's verdict never rides on a short deadline | [`check_timeout_bound_form.py`](../scripts/gates/check_timeout_bound_form.py), record shrinking only |
| A test module is evicted only through [`tests/module_eviction.py`](../tests/module_eviction.py) | [`check_module_eviction_form.py`](../scripts/gates/check_module_eviction_form.py) |
| A real spawn in a test is the claim, marked `boundary_contract(reason=...)` | [`check_staged_test_boundaries.py`](../scripts/hooks/check_staged_test_boundaries.py) in the commit hook |
| Inside this repo a skill script runs from the checkout | `script_origin` and `require_repo_local_helper` at write sites ([bootstrap resolution](../skills/shared/references/bootstrap-resolution.md)); nothing refuses a read-only run from a stale copy |
| A standing run's result outlives the caller that started it | [`standing_pytest_run_record.py`](../scripts/gates_support/standing_pytest_run_record.py), read back with `--print-last-run` |
| A subagent reads a named base, never whatever tree is on disk | the task run receipt's `base_sha` ([agent task runs](./agent-task-runs.md)) and the critique packet's `reviewed_input_identity`; nothing for a reviewer briefed by hand |
| A shared-tree review's findings apply only to the tree they were read against | [`reviewer_boundary_fingerprint.py`](../skills/shared/scripts/reviewer_boundary_fingerprint.py) ([reviewers stay read-only](./parallel-execution.md#reviewers-stay-read-only)); nothing for packet identity |
| In a probe record a field name sits at column 0 and an indented line continues it | [`probe_record_parse.py`](../scripts/evidence/probe_record_parse.py) |
| A lesson leaves the working set only by a person-settled lifecycle event; archive cites any canonical Markdown decision, graduation its owning `docs/` page | [`record_lesson_lifecycle.py`](../scripts/lessons/record_lesson_lifecycle.py) holds the form; nothing can see whether a person settled it |
| A gate's refusal names live surfaces and tokens; a documented flag or subcommand is one argparse accepts | nothing for the refusal text; [`check_documented_command_flags.py`](../scripts/gates/check_documented_command_flags.py) and [`check_documented_subcommands.py`](../scripts/gates/check_documented_subcommands.py) for the docs half |
| A layout fact is asserted on what the module bound, never on a global interpreter property | nothing; the distinction is semantic |
| An ephemeral worktree does not keep a dead git registration | [`worktree_lifetime.py`](../scripts/worktree/worktree_lifetime.py) on create, `audit --prune`, and the runtime sweep |

Tests import the script under test in-process through
[`tests/script_loader.py`](../tests/script_loader.py),
[`script_main.py`](../tests/script_main.py), and
[`script_closure.py`](../tests/script_closure.py), whose docstrings own the
child-interpreter emulation. A test that waits for a child blocks on a FIFO
through [`tests/fifo_witness.py`](../tests/fifo_witness.py) or drives a
controlled clock. A failure that passes alone is bisected over the collection
set first ([sibling search](../skills/public/debug/references/sibling-search.md)).

Everything that writes under the cache root (`resolve_cache_home` in
[`repo_layout.py`](../scripts/core/repo_layout.py)) has a row here, and the
writer's docstring owns its retention rule.

| Cache subtree | Writer |
| --- | --- |
| `pytest-tmp` | [`standing_pytest_basetemp.py`](../scripts/gates_support/standing_pytest_basetemp.py) |
| `test-seeds` | [`tests/seed_cache.py`](../tests/seed_cache.py) |
| `support-skills` | [`support_sync_lib.py`](../scripts/support_sync_lib.py) |
| `charness/runtime/<key>` and everything under it | [`runtime_bootstrap.py`](../scripts/runtime_bootstrap.py) writes the key; [`runtime_root_retention.py`](../scripts/gates_support/runtime_root_retention.py) sweeps on every standing run and by hand |
| `<key>/task-run/<id>` | [`task_run_completion.py`](../scripts/task_run/task_run_completion.py), then the sweep |
| `<key>/coverage/<repo-key>-<report-stem>` | [`coverage_runtime_paths()`](../scripts/mutation/mutation_sampling_lib.py), one directory per coverage report |

[`check-docs.sh`](../scripts/check-docs.sh) is the docs gate. The source tree
is authoritative; the plugin tree is generated.

### Pushing

Every push goes through the pre-push hook from
[`install-git-hooks.sh`](../scripts/install-git-hooks.sh). After the
irreversible [close-keyword scan](../scripts/prepush_close_keyword_guard.py), a push touching anything beyond docs and
artifacts runs `./scripts/run-quality.sh --full --read-only --release`, since
the standing lane deselects `release_only` and `slow_corpus`. A docs-artifact
push runs the docs subset. The hook reads the tree it runs in, so push from a
clean clone with the hooks installed and the mirror regenerated:

```bash
git clone --quiet . /tmp/charness-push && cd /tmp/charness-push
./scripts/install-git-hooks.sh
python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
git remote set-url origin <origin-url> && git push origin HEAD:main
```

The #778 closeout under `charness-artifacts/goal-runs/775/` records the
timings and the seeded refusal.

## Optional records

Use [artifact policy](./artifact-policy.md) for durable evidence and
[retro](../skills/public/retro/SKILL.md) for the optional lesson ledger;
neither is a session-start requirement. The retro persistence step seeds every
tagged recurrence class, and
[`check_lesson_ledger.py`](../scripts/lessons/check_lesson_ledger.py) names on
each standing lane every tagged class still unseeded and every graduated lesson
that a retro tags again outside the retros its lifecycle event reviewed; the
move on either is a person's. A lesson graduates only through the three
questions in
[lesson-graduation.md](../skills/shared/references/lesson-graduation.md).
