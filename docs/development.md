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

Each rule below is held by a mechanism, and the last column names what it
cannot see. A new gate adds a row with that column filled; an empty cell is a
gap to state. Dated evidence lives in `charness-artifacts/`, not here.

| Rule | Mechanism | Record | Cannot see |
| --- | --- | --- | --- |
| A code push runs the full read-only and release lanes | the pre-push hook ([pushing](#pushing)) | none | the tree it does not run in; push from a clean clone |
| A stale `plugins/` mirror is never read as a test failure | the standing runner and the quality engine regenerate it in a writing run and refuse in read-only, naming the command ([generated surfaces](./operating-contract.md#generated-surfaces)) | none | a bare `pytest` invocation; export by hand there |
| A skipped gate is not a passed gate | the quality summary names every gate it did not run and why ([operating contract](./operating-contract.md#verification)) | the lane receipt | not stated |
| A passing test is not a covered line | [`release_changed_line_coverage.py`](../scripts/mutation/release_changed_line_coverage.py) measures line reach, in the lane receipt's `changed_line_gate` and in the pre-push hook | `reports/mutation/` | a test importing a `scripts/` module by bare name is unmapped; a tests-only slice leaves the freshness marker unchanged ([deferred decisions](./deferred-decisions.md)) |
| Production code spawns only through [`subprocess_guard.py`](../scripts/core/subprocess_guard.py) | [`check_subprocess_form.py`](../scripts/gates/check_subprocess_form.py) | none | `tests/` (the row below owns them) |
| Where a repo script lives is answered only by [`repo_layout.py`](../scripts/core/repo_layout.py) | [`check_script_lookup_form.py`](../scripts/gates/check_script_lookup_form.py) refuses a by-name `glob`/`rglob` under `scripts/`, tests included | none | an enumeration (`rglob("*.py")`) is allowed by design |
| A test's claim never depends on wall-clock time | [`check_wall_clock_form.py`](../scripts/gates/check_wall_clock_form.py) refuses `time.sleep`, `time.monotonic`, `time.perf_counter` in `tests/` | [`wall-clock-baseline.json`](../charness-artifacts/quality/wall-clock-baseline.json), empty, shrinks only | a sleep inside a seeded child script; `time.time()` used as data; `fixtures/` directories |
| A test's verdict never rides on a short deadline | [`check_timeout_bound_form.py`](../scripts/gates/check_timeout_bound_form.py) refuses a sub-5 s `*_TIMEOUT_SECONDS` knob or a sub-second `communicate`/`run`/`wait` deadline whose handler asserts | [`timeout-bound-baseline.json`](../charness-artifacts/quality/timeout-bound-baseline.json), kept sites with reasons, shrinks only | a knob set in a fixture, helper, or module constant; a deadline through a variable; a value reached by call or tuple unpack; a fake raising `TimeoutExpired` |
| A test module is evicted only through [`tests/module_eviction.py`](../tests/module_eviction.py) | [`check_module_eviction_form.py`](../scripts/gates/check_module_eviction_form.py) refuses a raw `sys.modules` eviction | empty, shrinks only | `monkeypatch.setitem` (adds, does not evict); reads of `sys.modules`; `fixtures/` directories |
| A real spawn in a test is the claim, declared with `boundary_contract(reason=...)` | the staged test-boundary advisory in the commit hook ([`check_staged_test_boundaries.py`](../scripts/hooks/check_staged_test_boundaries.py)); the loaders below are the rule | none | dynamic commands, aliases, helper indirection, fixture builders, unparseable files |
| Inside this repo a skill script runs from the checkout | `script_origin` from the pickup, the release planner, and the publish guard ([bootstrap resolution](../skills/shared/references/bootstrap-resolution.md)) | none | a copy old enough to predate the check does not carry it |
| A local layout fact is asserted on what the module bound, never on a global interpreter property; force an arm with a `meta_path` finder, not by filtering `sys.path` | none: the distinction is semantic, and most `sys.path` edits in tests are legitimate shim proofs | none | everything; held by review |

Tests import the script under test in-process through
[`tests/script_loader.py`](../tests/script_loader.py),
[`script_main.py`](../tests/script_main.py), and
[`script_closure.py`](../tests/script_closure.py), which emulate the child
interpreter: `argv` swapped before the import, the script's directory first on
`sys.path`, a shadowing bare name evicted and restored, import-time exits
captured. Never load a module under a bare name the code under test imports
lazily; under xdist that rebinds `sys.modules` in every worker. A test that
waits for a child blocks on a FIFO through
[`tests/fifo_witness.py`](../tests/fifo_witness.py) or drives a controlled
clock. A failure that passes alone is bisected over the collection set first
([sibling search](../skills/public/debug/references/sibling-search.md)).

Everything that writes under the cache root (`resolve_cache_home` in
[`repo_layout.py`](../scripts/core/repo_layout.py), normally `~/.cache/charness`)
has a row here; the writer enforces its retention on the next run that touches
the root, and its docstring owns the exact rule. A new cache writer adds a row
and the code.

| Cache subtree | Writer | Retention |
| --- | --- | --- |
| `pytest-tmp` | [`standing_pytest_basetemp.py`](../scripts/gates_support/standing_pytest_basetemp.py) | Per key, a bounded number of failed and orphan run roots; passing roots deleted at once. A key whose recorded repo root is gone is removed whole. |
| `test-seeds` | [`tests/seed_cache.py`](../tests/seed_cache.py) | `SEED_CACHE_KEEP` entries per seed hash; `SHAPE_CACHE_KEEP` on `shapes`. |
| `support-skills` | [`support_sync_lib.py`](../scripts/support_sync_lib.py) | The current digest tree, the `SUPPORT_SKILL_CACHE_KEEP` most recent, and any live `skills/support/generated/` symlink target. |
| `charness/runtime/<key>` (normally under `~/.cache/tmp`) | [`runtime_bootstrap.py`](../scripts/runtime_bootstrap.py) writes the key and its `.charness-repo-root` marker; [`runtime_root_retention.py`](../scripts/gates_support/runtime_root_retention.py) sweeps on every standing pytest run and by hand with `--repo-root . [--dry-run]` | A key is removed whole when its recorded repo root is gone, or when unmarked and idle past `LEGACY_KEY_MAX_AGE_DAYS`; skipped while a `pytest-tmp` run lock is live or any entry is inside `ACTIVE_WINDOW_DAYS`. Keys are siblings, never nested. Every removal and skip is logged under `<key>/retention/`. |
| `<key>/task-run/<id>` | [`task_run_completion.py`](../scripts/task_run/task_run_completion.py), then the sweep | A `completed` commit-only lane releases its worktree and runtime at once. Any other finished lane is salvaged first (`uncommitted.patch`, `uncommitted-untracked.tar` beside `result.json`), then removed. `result.json` and the logs stay. |
| Nested `<key>/xdg-cache/.../runtime/*` keys; `<key>/pycache`, `coverage`, `tmp`, `ruff`, `npm`, `pip`, `pytest-cache` | the sweep | Removed whole once idle past the window; rebuilt on demand. |

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
