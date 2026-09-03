# Charness development

> Status: current
> Source of truth: this page and the executable commands it links
> Last verified: 2026-09-02

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

Run focused tests for ordinary changes. Use the small quality lane when the
core contract is relevant and the explicit full lane for broad, release, or
review work.
[The standing pytest runner](../scripts/gates_support/run_standing_pytest.py) is the pytest
owner — it supplies xdist workers, chunk sizing, and an external basetemp, and a
bare `python3 -m pytest` gets none of them (and is refused for a broad
selection):

```bash
python3 scripts/gates_support/run_standing_pytest.py --repo-root . --pytest-target <path-or-nodeid>
python3 scripts/gates_support/run_standing_pytest.py --repo-root .
./scripts/run-quality.sh
./scripts/run-quality.sh --full --read-only
```

Production code spawns only through
[`subprocess_guard.py`](../scripts/core/subprocess_guard.py); the standing
[form check](../scripts/gates/check_subprocess_form.py) refuses a direct call.
Where a repo script lives, flat under `scripts/` or inside the concept package
that owns it, is answered only by the resolver in
[`repo_layout.py`](../scripts/core/repo_layout.py) (`repo_script`,
`find_repo_script`; a miss is typed, two owners is an ambiguity); the standing
[lookup form check](../scripts/gates/check_script_lookup_form.py) refuses a
by-name `glob` or `rglob` under `scripts/` anywhere else, tests included. A
test's claim never depends on wall-clock time: no sleep as synchronisation, no
deadline poll for something the child could signal, no assertion on elapsed
time. The standing
[wall-clock form check](../scripts/gates/check_wall_clock_form.py) refuses
any `time.sleep`, `time.monotonic`, or `time.perf_counter` call in `tests/`;
its record,
[`wall-clock-baseline.json`](../charness-artifacts/quality/wall-clock-baseline.json),
reached zero entries in #780 and can only shrink, so the first new call
anywhere is red. A test that must wait for a child blocks on a FIFO the child
holds through [`tests/fifo_witness.py`](../tests/fifo_witness.py), or drives
the module under test with a controlled clock. Tests
import the script under test in-process through the loaders in
[`tests/script_loader.py`](../tests/script_loader.py),
[`script_main.py`](../tests/script_main.py), and
[`script_closure.py`](../tests/script_closure.py), and keep a real spawn only
where the process boundary is the claim, marked `boundary_contract(reason=...)`.
An in-process run must emulate what a child interpreter gave for free: swap
`argv` before the import, put the script's directory first on `sys.path`, evict
a bare module name that would shadow a sibling file and restore it after, and
capture import-time exits. Never load a module under a bare name that the code
under test imports lazily; under xdist that rebinds `sys.modules` in every
worker at collection time. Evict a test module only through [`tests/module_eviction.py`](../tests/module_eviction.py) (`evict_module`), which pins the parent package attribute so a module's identity is never split; the standing [module eviction form check](../scripts/gates/check_module_eviction_form.py) refuses a raw `sys.modules` eviction. A failure that passes alone is bisected over the collection set first, following [sibling-search.md](../skills/public/debug/references/sibling-search.md). A test that proves a local layout fact asserts what the module under test bound, never a global interpreter property; where the arm taken is not observable from the module, force it with a `meta_path` finder rather than by filtering `sys.path`. No gate holds that one: whether an assertion targets a global property is semantic, and the repo's `sys.path` manipulations in tests are mostly legitimate bootstrap-shim proofs.

A `skills/` or `scripts/` edit leaves the generated `plugins/` mirror stale, and
you no longer have to remember that: both the standing pytest runner and the
quality engine regenerate it in a writing run, and refuse in read-only while
naming the regenerate command. Batch source edits anyway, and export by hand
only when you invoke `pytest` directly. The rule and the command live in
[operating-contract.md](./operating-contract.md#generated-surfaces).

Everything that writes under the cache root
(`scripts/core/repo_layout.py::resolve_cache_home`, normally `~/.cache/charness`)
states its retention here; a new cache writer adds a row and the code that
enforces it. The rule exists because on 2026-09-03 `pytest-tmp` was measured at
16 GB across 300 per-repo keys with no cross-key retention at all. Retention is
enforced by the writer itself, on the next run that touches the same root, so
nothing here needs a scheduled sweep.

| Cache subtree | Writer | Retention |
| --- | --- | --- |
| `pytest-tmp` | [`standing_pytest_basetemp.py`](../scripts/gates_support/standing_pytest_basetemp.py) | Per key: `FAILED_BASETEMP_KEEP` marked-failed run roots, `ORPHAN_BASETEMP_KEEP` unmarked orphans, passing roots deleted at once. Across keys: a key whose recorded repo root is gone is removed whole, and a key predating that marker after `LEGACY_KEY_MAX_AGE_DAYS` idle days. |
| `test-seeds` | [`tests/seed_cache.py`](../tests/seed_cache.py) | `SEED_CACHE_KEEP` entries per seed source hash, plus a `SHAPE_CACHE_KEEP` cap on the `shapes` namespace. |
| `support-skills` | [`support_sync_lib.py`](../scripts/support_sync_lib.py) | Per skill: the current digest tree plus the `SUPPORT_SKILL_CACHE_KEEP` most recently used, and any tree a live `skills/support/generated/` symlink resolves through. |

When docs change, run [`check-docs.sh`](../scripts/check-docs.sh). The source
tree is authoritative; the plugin tree is a generated install surface.

### Pushing

Every push goes through the pre-push hook installed by
[`install-git-hooks.sh`](../scripts/install-git-hooks.sh). After the
irreversible close-keyword scan, a push that touches anything beyond docs and
artifacts runs `./scripts/run-quality.sh --full --read-only --release`: the
standing lane deselects `release_only` and `slow_corpus`, so without
`--release` a release-only regression crosses the push unseen (#768 carried
three for four days). A docs-artifact-only push runs the docs subset instead;
the release lane is indivisible and cannot narrow to it. Measured on the #778
closeout in a clean clone, the hook lane took about 260 s for a passing code push (the release pytest alone about 100 s); a seeded release-only failure was refused in about 120 s because the lane stops at the failing release pytest.

The hook reads the working tree it runs in, so push from a clean tree. The
shape the Goal Run closeouts use: clone the tip, install the hooks, regenerate
the mirror, and push from there, so the lane judges exactly the bytes that
leave. The exporter line stays spelled out here because a fresh clone has no
`plugins/` at all and no runner has been through it yet.

```bash
git clone --quiet . /tmp/charness-push && cd /tmp/charness-push
./scripts/install-git-hooks.sh
python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
git remote set-url origin <origin-url> && git push origin HEAD:main
```

Proof that the hook refuses what it should: seed one `release_only` test that
fails, commit, push to a scratch remote, and read the refusal; drop the seed
and the same push passes. The #778 closeout records both runs.

## Optional records

Use [artifact policy](./artifact-policy.md) for durable evidence and
[retro](../skills/public/retro/SKILL.md) for the optional lesson ledger. These
records are useful state, but neither one is a session-start requirement.
A tagged recurrence class becomes selectable only when its seed transition is appended; the retro persistence step runs the seeder and records the result beside `## Persisted`, and [`check_lesson_ledger.py`](../scripts/lessons/check_lesson_ledger.py) names every tagged class still unseeded on each standing lane, so a stranded lesson is visible rather than silent.
A lesson graduates out of the ledger only through the three questions in [lesson-graduation.md](../skills/shared/references/lesson-graduation.md): one owning `docs/` page with duplicates removed, a code mechanism where one is possible, then the lifecycle event.

## Mutation phase barriers

Keep state-changing work and verification in separate phases:

1. mutate
2. sync generated surfaces
3. verify
4. publish

Read-only inventory may run in parallel. Do not run generated-surface sync,
version or install changes, or git mutations concurrently with validators.
