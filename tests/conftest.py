from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml

from scripts.core.repo_file_listing import (
    RepoFileSnapshot,
    bind_subject_listing,
    unbind_subject_listing,
)
from tests import seed_cache
from tests.script_main import load_script_module, run_loaded_script_main

pytest_plugins = [
    "tests.repo_copy",
    "tests.quality_gates.support",
    "tests.charness_cli.support",
]

_REPO_ROOT = Path(__file__).resolve().parents[1]


def pytest_configure(config) -> None:
    """Compute the source-bound seed key once before xdist workers are spawned.

    Also bind this checkout's file listing so inventory of the subject repo
    observes once per worker. The snapshot is empty until first list: tests
    that monkeypatch listing still see that patch if they run first.
    """
    if not hasattr(config, "workerinput") and config.pluginmanager.hasplugin("xdist"):
        try:
            os.environ.setdefault(seed_cache._SOURCE_HASH_ENV, seed_cache.source_hash())
        except seed_cache.SourceStateUnreadable as exc:
            # This call is an OPTIMISATION: compute the key once so xdist workers
            # inherit it instead of each recomputing. Letting the refusal escape
            # here turns "seed-backed tests cannot run" into "pytest INTERNALERRORs
            # and zero tests are collected" -- a strictly worse outcome than the
            # fail-open collision the refusal exists to prevent, and one that lands
            # on any checkout git reports dubious ownership for.
            #
            # So it degrades: the key stays unset, every test that does not touch a
            # cached seed runs normally, and the ones that do fail individually with
            # the message below rather than taking the session down with them.
            print(f"seed cache disabled: {exc}", file=sys.stderr)
    bind_subject_listing(RepoFileSnapshot(_REPO_ROOT, require_git=True))


def pytest_unconfigure(config) -> None:
    unbind_subject_listing(_REPO_ROOT, require_git=True)


@pytest.fixture(scope="session", autouse=True)
def _confine_git_discovery_to_pytest_temp(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[None]:
    # Stop git repo discovery from escaping the pytest temp tree into an ambient
    # ancestor .git (e.g. a dotfiles repo above $TMPDIR). Otherwise the
    # fail-closed-outside-git fixtures can non-deterministically find an ancestor
    # repo depending on where the (xdist) basetemp lands. See issue #225.
    ceiling = str(tmp_path_factory.getbasetemp().resolve().parent)
    previous = os.environ.get("GIT_CEILING_DIRECTORIES")
    os.environ["GIT_CEILING_DIRECTORIES"] = ceiling if not previous else f"{ceiling}:{previous}"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("GIT_CEILING_DIRECTORIES", None)
        else:
            os.environ["GIT_CEILING_DIRECTORIES"] = previous


AMBIENT_RUNNER_ENV = (
    "MUTATION_BASE_SHA",
    "MUTATION_HEAD_SHA",
    "GITHUB_OUTPUT",
    "CHARNESS_RUNTIME_REGIME",
    "CHARNESS_RUNTIME_PROFILE",
)


@pytest.fixture(scope="session", autouse=True)
def _scrub_ambient_runner_state() -> Iterator[None]:
    """Stop AMBIENT state from reaching the suite (#466, #544).

    Originally the CI runner's own environment; it now also covers local
    `run-quality.sh` state, which is exported on a developer machine and reaches
    the `pytest` gate the same way. The unifying property is not where the
    variable comes from, it is that a reader inside the suite defaults from it.

    The scheduled mutation workflow's "Select mutation sample" step launches the
    coverage-baseline pytest (`env CHARNESS_ALLOW_BARE_PYTEST=1 python3 -m pytest -q -m 'not release_only' tests`)
    with the STEP's environment, and the suite inherited it in two ways, both
    reproduced:

    * `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA` -- `check_changed_line_coverage.py`
      and `sample_mutation_files.py` default their base/head to these. A test that
      seeds a throwaway git repo and runs the gate against it got THIS repo's HEAD
      as the analyzed head, an invalid revision range, and an UNESTABLISHED
      refusal where it expected a clean pass. The gate was right; the suite was
      reading the runner's environment.
    * `GITHUB_OUTPUT` -- `sample_mutation_files.py:append_github_output` writes
      `sample_files=<...>` there whenever it is set, and the in-process
      `main()` call in `test_mutation_baseline_abort.py` reaches it. Observed
      writing a tmp-repo `sample_files=scripts/a.py` line into the real step
      output file that the "Run mutation" step then consumes. Masked in practice
      only by ordering (the baseline pytest runs before the real publish, and
      GitHub keeps the last value for a duplicate key) -- luck, not isolation.

    * `CHARNESS_RUNTIME_REGIME`/`CHARNESS_RUNTIME_PROFILE` -- both are defaults
      for `record_quality_runtime.py`'s `--runtime-regime`/`--runtime-profile`,
      and `run-quality.sh` EXPORTS the regime for the whole run, so the `pytest`
      gate inherits it. Under `CHARNESS_QUALITY_LABELS=pytest ./scripts/run-quality.sh`
      the regime is `filtered`, and the recorder tests that drive `main()`
      in-process then file their samples under `default.filtered` instead of
      `default`. Reproduced: `CHARNESS_RUNTIME_REGIME=filtered pytest
      tests/quality_gates/test_quality_runtime_recorder.py` fails three cases,
      including the one written to pin the absent-regime path. A false red caused
      purely by how the gate was invoked -- which is the same defect class as the
      issue that introduced the regime (#544), one layer up.
      `CHARNESS_RUNTIME_PROFILE` is scrubbed alongside it: identical shape, and
      masked today only because no test asserts on a DERIVED profile id without
      pinning it -- the two recorder tests that pass no `--runtime-profile` happen
      to read `profiles[next(iter(profiles))]` or assert only on archive
      filenames. That is a property of the current assertions, not of the name,
      and the next test to assert a concrete derived id would inherit the bug.

    Scrubbed session-wide rather than per test: individual tests had already
    started deleting the range one at a time, which only ever fixes the test that
    remembers. A test that wants any of these sets it explicitly (via
    `monkeypatch` or an explicit `env=` dict), which still works over this.

    Not scrubbed: `MUTATION_SAMPLE_*`. Every reader was checked and none can change
    a verdict TODAY -- but state the property accurately, because it is weaker than
    it looks: it holds because the three live `sample_mutation_files.main()` call
    sites happen to pin `MUTATION_SAMPLE_MAX_FILES`, the one knob whose workflow
    value (`.agents/quality-adapter.yaml` `max_files: 5`) differs from the code
    default (10). That is a call-site convention, not an attribute of the names,
    and nothing enforces it. A future test that pins `SEED` and `CHANGED_QUOTA` but
    not `MAX_FILES` -- the copy-paste-obvious subset -- would pass locally and fail
    only in the nightly cron. Add the name here if that happens.
    """
    previous = {name: os.environ.pop(name, None) for name in AMBIENT_RUNNER_ENV}
    try:
        yield
    finally:
        # Restores the ABSENT case too, matching the two sibling fixtures in this
        # file. Three session fixtures with two restore contracts is how the next
        # editor copies the wrong one.
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


GIT_IDENTITY_ENV = {
    "GIT_AUTHOR_NAME": "Charness Test",
    "GIT_AUTHOR_EMAIL": "tests@example.com",
    "GIT_COMMITTER_NAME": "Charness Test",
    "GIT_COMMITTER_EMAIL": "tests@example.com",
}


@pytest.fixture(scope="session", autouse=True)
def _git_identity_from_the_environment(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[None]:
    """Give every test-seeded repo a commit identity WITHOUT spawning `git config`.

    Measured on this suite: `git` is 8552 of 12527 subprocess spawns, and 764 of
    those were `git config` calls existing only so `git commit` would work in a
    throwaway repo. Git reads the same identity from GIT_AUTHOR_* / GIT_COMMITTER_*,
    so setting it once per session removes a process launch from every seeded repo.
    The repos are still built per test -- this is not the fixture caching the
    standing measurement ruled out.

    `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` are the load-bearing half. Without
    them the suite silently reads the developer's real `~/.gitconfig`, which means a
    seeded `git commit` passes on a machine that happens to have a global identity
    and fails on one that does not -- exactly the ambient dependency that hid a
    missing version of this fixture during review. Pointing global config at an
    empty temp file makes the identity above the only source, so a green run here
    means a green run on a bare CI box.

    A test that exercises missing or invalid identity manages this itself;
    `tests/quality_gates/test_check_git_identity.py` and the `.invalid`-placeholder
    guards in `tests/quality_gates/test_release_publish_resilience.py` keep their
    explicit `git config` spawns for that reason.
    """
    # Not empty: pin the settings the suite would otherwise inherit from whatever
    # the developer happens to have. `init.defaultBranch` is load-bearing --
    # isolating global config revealed that tests asserting on `origin/main` were
    # silently relying on the developer's own default, and got `master` without it.
    #
    # `maintenance.auto = false` is load-bearing too. git >= 2.46 detaches
    # `maintenance run --auto` after every `git commit`, and the daemon takes
    # `.git/objects/maintenance.lock` BEFORE it forks, so the lock is still there
    # for a moment after `commit` has returned. A seed builder publishes its shape
    # the instant that commit returns, and the next test's `shutil.copytree` then
    # lists the lock and finds it gone -- 82 `shutil.Error`s in one CI baseline
    # run (#764), on whichever tests asked for a fresh shape first. A fast
    # machine loses that race about 1 commit in 40 and a two-core runner far
    # more often; git 2.34 never detaches, which is why it never showed locally.
    # Fixture repos have nothing to maintain, so the knob costs nothing.
    empty_global = tmp_path_factory.getbasetemp() / "test-gitconfig"
    empty_global.write_text(
        "[init]\n\tdefaultBranch = main\n[maintenance]\n\tauto = false\n",
        encoding="utf-8",
    )
    overrides = {
        **GIT_IDENTITY_ENV,
        "GIT_CONFIG_GLOBAL": str(empty_global),
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    previous = {name: os.environ.get(name) for name in overrides}
    os.environ.update(overrides)
    try:
        yield
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


@pytest.fixture
def no_ambient_git_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Opt out of the session git identity, for tests that assert ON identity.

    Git resolves author/committer from GIT_AUTHOR_*/GIT_COMMITTER_* BEFORE
    `user.name`/`user.email` config, so the session default would mask an identity a
    test deliberately configured -- e.g. a lingering `.invalid` placeholder a guard
    is supposed to catch. Request this fixture in any test that sets identity via
    `git config` and expects the tool to see it.
    """
    for name in GIT_IDENTITY_ENV:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def _disable_plugin_fallback_manifests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")


NESTED_PYTEST_ENV = "CHARNESS_NESTED_PYTEST"

#: Set by `run_standing_pytest.py` in the child env it launches, so its SERIAL
#: fallback is not mistaken for a bare run. NOT `PYTEST_DEBUG_TEMPROOT`: that one
#: survives in any shell descended from a run that set it, so it reports "the
#: runner owns this" for a hand-typed command in the same terminal -- the ambient
#: state class `_scrub_ambient_runner_state` above already exists for.
CANONICAL_RUNNER_ENV = "CHARNESS_STANDING_PYTEST"
#: The two invocations that legitimately run bare and serial declare themselves:
#: `cosmic-ray.toml`'s per-mutant test-command and the coverage baseline it shares.
BARE_PYTEST_ESCAPE_ENV = "CHARNESS_ALLOW_BARE_PYTEST"
#: A focused run is cheap serially and startup-sensitive; only a broad selection is
#: worth refusing. Sized well above any single test module in this repo.
BARE_PYTEST_ITEM_FLOOR = 300


def bare_pytest_refusal(config: pytest.Config, items: list[pytest.Item]) -> str | None:
    """The refusal decision, separated from the act of stopping the session.

    Returning a message instead of calling `pytest.exit` directly keeps this
    testable: `pytest.exit` raises `Exit`, which a worker interprets as "the
    session is over" and reports as a crashed worker, so a test cannot simply
    drive the hook and catch it.
    """
    # The primary test is not "who launched this" but "is the fast path in use":
    # the runner always passes `-n`, so a broad selection with `numprocesses`
    # unset is the expensive case no matter who typed it.
    if getattr(config.option, "numprocesses", None):
        return None
    if os.environ.get(CANONICAL_RUNNER_ENV) or os.environ.get(BARE_PYTEST_ESCAPE_ENV) == "1":
        return None
    if os.environ.get("PYTEST_XDIST_WORKER") or os.environ.get(NESTED_PYTEST_ENV):
        return None
    if len(items) < BARE_PYTEST_ITEM_FLOOR:
        return None

    import importlib.util

    guidance = (
        f"\n{len(items)} tests selected without the repo's pytest runner.\n\n"
        "  whole suite:  python3 scripts/gates_support/run_standing_pytest.py --repo-root .\n"
        "  focused:      python3 scripts/gates_support/run_standing_pytest.py --repo-root . "
        "--pytest-target <path-or-nodeid>\n"
        "  full battery: ./scripts/run-quality.sh --full --release\n\n"
        f"Set {BARE_PYTEST_ESCAPE_ENV}=1 to run single-process on purpose.\n"
    )
    if importlib.util.find_spec("xdist") is None:
        # Nothing to refuse: without xdist the runner would also run serially.
        print(f"warning: pytest-xdist is not installed.{guidance}", file=sys.stderr)
        return None
    return f"pytest-xdist is installed but unused, so this run would be single-process.{guidance}"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Refuse a broad run that bypasses `scripts/gates_support/run_standing_pytest.py`.

    That script owns xdist worker selection, `--dist load` chunk sizing, an
    external basetemp, and serial fallback. A bare `python3 -m pytest tests`
    inherits none of it and runs single-process, and nothing in the output says
    the fast path was skipped -- measured on this repo, 8400 tests take ~110s
    through the runner and over half an hour without it.

    This lived only in prose before: `docs/development.md` said "run focused
    tests" without naming a command, and the command was written down once, in
    `.agents/lane-brief-template.md`, which is read on the DELEGATION path only --
    a session implementing directly never sees it. The 2026-07-19 runner-reuse
    retro migrated every checked-in raw-pytest call site and verified with `rg`
    that none remained, but a scan over files cannot see a command an agent types.
    `2026-07-26-lesson-recurrence-mechanism.md` then measured why repeating the
    prose does not help: "the prose channel does not change behavior at the moment
    of action." This is that rule moved into the channel that does.

    Scope is deliberately narrow. A focused selection passes untouched. A host
    without xdist is warned rather than refused, because there the fast path does
    not exist to be skipped.
    """
    refusal = bare_pytest_refusal(config, items)
    if refusal is None:
        return
    # `pytest.exit`, not `raise`: an exception raised inside this hook is absorbed
    # by the hook caller and the run continues. Verified here -- the hook entered,
    # raised `UsageError`, and 5935 tests were still reported as collected.
    pytest.exit(refusal, returncode=4)


def _residue_pids(payload_text: str) -> list[int]:
    """Every pid `--assert-no-orphans` named in the YAML payload it printed.

    The three residue kinds it counts are the orphan daemon trees it can reap,
    reparented browser processes whose daemon is gone, and unreaped zombies.
    A payload that will not parse yields an empty list: the stderr line is
    diagnostic, so an unreadable payload must not raise out of a session hook.
    """
    try:
        runtime = (yaml.safe_load(payload_text) or {}).get("runtime") or {}
    except yaml.YAMLError:
        return []
    return sorted(
        {
            *runtime.get("orphan_tree_pids", []),
            *runtime.get("reparented_residue_pids", []),
            *runtime.get("zombie_residue_pids", []),
        }
    )


def pytest_sessionfinish(session: pytest.Session) -> None:
    # A NESTED session (one a test spawned) must not reap orphans against the real
    # repo while the OUTER run is still going: the cleanup sends SIGTERM/SIGKILL to
    # agent-browser trees it did not start, which silently repairs the very state
    # `agent-browser-runtime-hygiene` exists to observe -- the suite erasing its own
    # evidence. Only `PYTEST_XDIST_WORKER` guarded this, so a nested run was safe
    # solely when the outer run happened to use xdist; `cosmic-ray.toml`'s
    # test-command is serial, so under the scheduled mutation baseline it was not.
    if os.environ.get("PYTEST_XDIST_WORKER") or os.environ.get(NESTED_PYTEST_ENV):
        return
    guard = _REPO_ROOT / "scripts" / "evidence" / "agent_browser_runtime_guard.py"
    if not guard.is_file():
        return
    guard_module = load_script_module("agent_browser_runtime_guard_session_cleanup", guard)
    cleanup = ("--repo-root", str(_REPO_ROOT), "--cleanup-orphans", "--execute")
    inspect = ("--repo-root", str(_REPO_ROOT), "--assert-no-orphans")
    # ONE cleanup, ONE inspect. The retry used to run this pair once a second for
    # ten seconds, which only re-ran `ps` and hoped. `cleanup_orphans` already
    # SIGTERMs the owned orphan tree, waits its own grace, and SIGKILLs whatever
    # is left, so nothing it targeted can still be alive when it returns. A pid
    # killed but not yet reaped is a zombie, and `inspect_runtime` attributes
    # residue by the process working directory -- which a zombie has already
    # released -- so an unattributable process is fail-closed to NOT this
    # checkout's and a just-killed pid cannot be why this inspect fails.
    #
    # A failure here is therefore real residue the cleanup does not own:
    # reparented browser processes, or a tree the container init has not reaped.
    # Report it and let the session end. This hook never failed a run, and still
    # does not -- it only stops pretending a second look would change the answer.
    try:
        run_loaded_script_main(str(guard), guard_module, *cleanup)
        result = run_loaded_script_main(str(guard), guard_module, *inspect)
    except (OSError, subprocess.SubprocessError):
        return
    if result.returncode == 0:
        return
    print(
        f"agent-browser runtime residue survived session cleanup: "
        f"pids={_residue_pids(result.stdout)}",
        file=sys.stderr,
    )
