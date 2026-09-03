# Charness development

> Status: current
> Source of truth: this page and the executable commands it links
> Last verified: 2026-09-03

This page answers one question: what is the shortest safe path for changing and
dogfooding Charness itself? Detailed contracts stay with their owners.

## Start

Install the local dependencies once in a clean checkout:

```bash
npm ci
```

Then read [implementation discipline](./implementation-discipline.md) and the
owner page for the surface being changed. [README.md](../README.md) owns
supported install; this page owns repository development.

## Local dogfood

To make an installed host use this checkout without pulling remote changes:

```bash
charness update --repo-root . --no-pull --skip-cli-install
```

To refresh the managed CLI itself, use the managed checkout entrypoint. Return
to the normal `charness update` path after a release or ordinary operator cycle.

## Goal and issue work

Use the exact provider-backed parent objective for an active goal. This is the
Issue-Native Goal Run:

```bash
./charness goal run --repo-root . --objective '/goal #<parent>'
```

[Goal lifecycle](./goal-lifecycle.md) owns parent/cursor state and issue
membership. [Issue](../skills/public/issue/SKILL.md) owns GitHub writes and
readback. Do not recreate either state in a local handoff or session hook.

## Worktrees and runtime

Use [worktree prepare](./worktree-prepare.md) for isolated mutation. Its
commands own clean checkout, named branch, scope, and external runtime paths.
For one-off local commands, keep Python bytecode, pytest cache, coverage, and
temporary output outside the checkout; `.gitignore` only hides output.

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

Verify in the shape production uses: after an integration step the only green
that counts is the standing runner followed by the full read-only lane. A green
from an older tree, a bare pytest, a focused run, or a lane that skipped the
check is a proxy; a family rerun locates, it does not claim. The slice order
(commit, changed-line proof, then the broad lane) is owned by
[parallel execution](./parallel-execution.md#disjoint-writers).

Each rule below names the mechanism that holds it. The mechanism's docstring
owns the exact form and what it cannot see; this table does not repeat it.

| Rule | Held by |
| --- | --- |
| A code push runs the full read-only and release lanes | the pre-push hook ([pushing](#pushing)) |
| A stale `plugins/` mirror is regenerated or refused, never read as a failure | the standing runner and the quality engine ([generated surfaces](./operating-contract.md#generated-surfaces)) |
| A skipped gate is not a passed gate | the quality summary ([operating contract](./operating-contract.md#verification)) |
| A passing test is not a covered line | [`release_changed_line_coverage.py`](../scripts/mutation/release_changed_line_coverage.py), in the lane receipt and the pre-push hook |
| Production code spawns only through [`subprocess_guard.py`](../scripts/core/subprocess_guard.py) | [`check_subprocess_form.py`](../scripts/gates/check_subprocess_form.py) |
| A repo script's location is answered only by [`repo_layout.py`](../scripts/core/repo_layout.py) | [`check_script_lookup_form.py`](../scripts/gates/check_script_lookup_form.py) |
| A test never depends on wall-clock time | [`check_wall_clock_form.py`](../scripts/gates/check_wall_clock_form.py), record empty and shrinking only |
| A test's verdict never rides on a short deadline | [`check_timeout_bound_form.py`](../scripts/gates/check_timeout_bound_form.py), record shrinking only |
| A test module is evicted only through [`tests/module_eviction.py`](../tests/module_eviction.py) | [`check_module_eviction_form.py`](../scripts/gates/check_module_eviction_form.py) |
| A real spawn in a test is the claim, marked `boundary_contract(reason=...)` | [`check_staged_test_boundaries.py`](../scripts/hooks/check_staged_test_boundaries.py) in the commit hook |
| Inside this repo a skill script runs from the checkout | `script_origin` ([bootstrap resolution](../skills/shared/references/bootstrap-resolution.md)) |
| A gate's refusal names live surfaces and tokens, never a remembered rule; a documented flag or subcommand is one the script's own argparse accepts | nothing for the refusal text; [`check_documented_command_flags.py`](../scripts/gates/check_documented_command_flags.py) and [`check_documented_subcommands.py`](../scripts/gates/check_documented_subcommands.py) hold the docs half |
| A layout fact is asserted on what the module bound, never on a global interpreter property; force an arm with a `meta_path` finder | nothing; the distinction is semantic, so review holds it |

Tests import the script under test in-process through
[`tests/script_loader.py`](../tests/script_loader.py),
[`script_main.py`](../tests/script_main.py), and
[`script_closure.py`](../tests/script_closure.py), which emulate the child
interpreter; never load a module under a bare name the code under test imports
lazily. A test that waits for a child blocks on a FIFO
([`tests/fifo_witness.py`](../tests/fifo_witness.py)) or drives a controlled
clock. A failure that passes alone is bisected over the collection set first
([sibling search](../skills/public/debug/references/sibling-search.md)).

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

When docs change, run [`check-docs.sh`](../scripts/check-docs.sh). The source
tree is authoritative; the plugin tree is a generated install surface.

### Pushing

Every push goes through the pre-push hook from
[`install-git-hooks.sh`](../scripts/install-git-hooks.sh). After the
irreversible close-keyword scan, a push touching anything beyond docs and
artifacts runs `./scripts/run-quality.sh --full --read-only --release`, since
the standing lane deselects `release_only` and `slow_corpus`. A docs-artifact
push runs the docs subset; the release lane is indivisible. The hook reads the
tree it runs in, so push from a clean clone with the hooks installed and the
mirror regenerated (a fresh clone has no `plugins/`):

```bash
git clone --quiet . /tmp/charness-push && cd /tmp/charness-push
./scripts/install-git-hooks.sh
python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
git remote set-url origin <origin-url> && git push origin HEAD:main
```

Timings and the seeded-refusal proof are recorded in the #778 closeout under
`charness-artifacts/goal-runs/775/`.

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

## Mutation phase barriers

Keep state-changing work and verification in separate phases:

1. mutate
2. sync generated surfaces
3. verify
4. publish

Read-only inventory may run in parallel. Do not run generated-surface sync,
version or install changes, or git mutations concurrently with validators.
