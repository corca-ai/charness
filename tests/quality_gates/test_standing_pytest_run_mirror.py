"""The standing runner's answer to a stale generated plugin mirror.

The mirror under ``plugins/`` is derived from ``skills/`` and ``scripts/`` and is
gitignored, so every source edit makes it stale. Around thirty standing tests
read that on-disk tree, which means the runner used to surface an unrun exporter
as a scattering of unrelated red tests -- four sessions were spent tracing that
back. The runner now shares the quality engine's mirror preamble: a writing run
regenerates, a read-only run refuses and names the command.

Sibling to `test_standing_pytest_run_execution.py` (which owns the monitored
child and the run record) rather than an addition to it: nothing here spawns
pytest, and the question is what happens BEFORE the command is even built.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.gates_support import plugin_mirror_preamble

from .support import init_git_repo, write_executable

MARKER = "mirror-preamble-ran"


def _runner_args(repo: Path, **overrides: object) -> SimpleNamespace:
    defaults = dict(
        repo_root=repo,
        mode="read-only",
        basetemp=repo / "basetemp",
        include_release_only=False,
        keep_basetemp=True,
        pytest_target=[],
        extra_pytest_target=[],
        print_command=False,
        timeout_seconds=None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _stub(repo: Path, name: str, body: str) -> None:
    path = repo / "scripts" / "plugin_export" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    write_executable(path, body)


def _mirror_repo(tmp_path: Path, *, declared: bool = True, stale: bool = False) -> Path:
    """A gitignored-mirror repo whose exporter and validator are observable stubs.

    `declared` off is the CONSUMER shape: a repo with its own `plugins/`
    directory and no charness packaging manifest, which this preamble must never
    touch. `stale` makes the validator refuse the way `--validate-export` does
    when the mirror no longer matches a fresh export.
    """
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "plugins" / "charness").mkdir(parents=True)
    (repo / ".gitignore").write_text("/plugins/\n", encoding="utf-8")
    if declared:
        (repo / "packaging").mkdir()
        (repo / "packaging" / "charness.json").write_text(
            json.dumps(
                {"codex": {"repo_marketplace": {"materialized_source_path": "./plugins/charness"}}}
            ),
            encoding="utf-8",
        )
    _stub(
        repo,
        "sync_root_plugin_manifests.py",
        f"from pathlib import Path\nPath({MARKER!r}).write_text('synced')\n",
    )
    _stub(
        repo,
        "validate_packaging.py",
        "import sys\n"
        f"Path = __import__('pathlib').Path\nPath({MARKER!r}).write_text('validated')\n"
        + (
            "print('materialized export differs from a fresh export')\nsys.exit(1)\n"
            if stale
            else ""
        ),
    )
    init_git_repo(repo)
    return repo


def _patched_runner(monkeypatch, spawned: list[list[str]]):
    from scripts.gates_support import run_standing_pytest as runner

    def fake_phase(command, **kwargs):
        spawned.append(list(command))
        return SimpleNamespace(
            returncode=0, timed_out=False, elapsed_seconds=0.1, stdout="", stderr=""
        )

    monkeypatch.setattr(runner, "run_monitored_phase", fake_phase)
    monkeypatch.setattr(runner, "build_pytest_command", lambda *a, **k: ["pytest", "-q"])
    monkeypatch.setattr(runner, "ensure_external_temp_root", lambda *a, **k: None)
    return runner


def test_full_mode_regenerates_the_mirror_before_the_suite(tmp_path: Path, monkeypatch) -> None:
    """A writing run does the exporter's work rather than reporting its absence."""
    repo = _mirror_repo(tmp_path)
    spawned: list[list[str]] = []
    runner = _patched_runner(monkeypatch, spawned)

    assert runner.run_standing_pytest(_runner_args(repo, mode="full")) == 0

    assert (repo / MARKER).read_text(encoding="utf-8") == "synced"
    assert spawned == [["pytest", "-q"]], "the suite still runs after the refresh"


def test_read_only_mode_refuses_a_stale_mirror_and_names_the_command(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The point of the mechanism: a refusal carrying its remedy, not two red tests.

    Read-only is the lane that must not write, so it validates and stops. The
    exact regenerate command is asserted verbatim because a refusal that only
    says "stale" leaves the operator to rediscover the exporter -- which is the
    rediscovery this lesson graduated out of the ledger.
    """
    repo = _mirror_repo(tmp_path, stale=True)
    spawned: list[list[str]] = []
    runner = _patched_runner(monkeypatch, spawned)

    assert runner.run_standing_pytest(_runner_args(repo, mode="read-only")) != 0

    assert spawned == [], "pytest must not run against a mirror known to be stale"
    assert (repo / MARKER).read_text(encoding="utf-8") == "validated"
    stderr = capsys.readouterr().err
    assert (
        "standing-pytest: regenerate with `python3 "
        f"scripts/plugin_export/sync_root_plugin_manifests.py --repo-root {repo}`" in stderr
    )
    assert "materialized export differs from a fresh export" in stderr


def test_a_repo_without_the_packaging_manifest_is_untouched(tmp_path: Path, monkeypatch) -> None:
    """A consuming repo's own `plugins/` directory is not this runner's business."""
    repo = _mirror_repo(tmp_path, declared=False, stale=True)
    spawned: list[list[str]] = []
    runner = _patched_runner(monkeypatch, spawned)

    assert runner.run_standing_pytest(_runner_args(repo, mode="read-only")) == 0

    assert not (repo / MARKER).exists()
    assert spawned == [["pytest", "-q"]]


def test_print_command_does_not_touch_the_mirror(tmp_path: Path, monkeypatch, capsys) -> None:
    """`--print-command` plans a run; it spawns nothing, so it refreshes nothing."""
    repo = _mirror_repo(tmp_path, stale=True)
    spawned: list[list[str]] = []
    runner = _patched_runner(monkeypatch, spawned)

    assert runner.run_standing_pytest(_runner_args(repo, mode="full", print_command=True)) == 0

    assert not (repo / MARKER).exists()
    assert capsys.readouterr().out.strip() == "pytest -q"


def _unresolvable(repo: Path, body: str) -> "tuple[int, list[str]]":
    """Drive the preamble against a manifest it cannot turn into a plugin root."""
    (repo / "packaging").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text(body, encoding="utf-8")
    logged: list[str] = []

    def never(_command: "list[str]"):
        raise AssertionError("no child may run once the manifest cannot be resolved")

    code = plugin_mirror_preamble.ensure_plugin_mirror(
        repo, read_only=True, probe=never, log=logged.append
    )
    return code, logged


def test_a_manifest_that_resolves_to_no_plugin_root_stops_the_run(tmp_path: Path) -> None:
    """A declared-but-unusable manifest is a refusal, not a silent proceed.

    The absent-manifest case above is the consumer shape and returns 0. A
    manifest that IS declared and cannot be read is the opposite: the repo says
    it has a mirror and this preamble cannot tell whether it is stale, so
    proceeding would hand the suite exactly the scattered unrelated failures the
    module exists to prevent. Each shape below reaches the branch through a
    different exception, and none of them may spawn a child.
    """
    cases = {
        "malformed": "{not json",
        "missing-key": json.dumps({"codex": {"repo_marketplace": {}}}),
        "not-a-mapping": json.dumps(["codex"]),
        "escaping-root": json.dumps(
            {"codex": {"repo_marketplace": {"materialized_source_path": "../outside"}}}
        ),
    }
    for name, body in cases.items():
        code, logged = _unresolvable(tmp_path / name, body)
        assert code == 1, name
        assert logged and logged[0].startswith("could not resolve packaged plugin root: "), name


def test_an_unreadable_manifest_stops_the_run(tmp_path: Path) -> None:
    """The OSError arm of the same branch, reached without patching any seam."""
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    manifest = repo / "packaging" / "charness.json"
    manifest.write_text("{}", encoding="utf-8")
    manifest.chmod(0o000)
    logged: list[str] = []
    try:
        code = plugin_mirror_preamble.ensure_plugin_mirror(
            repo,
            read_only=True,
            probe=lambda _command: pytest.fail("no child may run"),
            log=logged.append,
        )
    finally:
        manifest.chmod(0o644)

    assert code == 1
    assert logged and logged[0].startswith("could not resolve packaged plugin root: ")


def test_a_plugin_root_git_does_not_ignore_is_left_alone(tmp_path: Path) -> None:
    """The second guard: a tracked `plugins/` tree is somebody else's directory.

    Both guards must hold before this preamble regenerates or refuses. A declared
    manifest alone is not enough -- if git tracks the resolved root then it is not
    a derived mirror, and neither the exporter nor the validator may be spawned
    against it.
    """
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text(
        json.dumps(
            {"codex": {"repo_marketplace": {"materialized_source_path": "./plugins/charness"}}}
        ),
        encoding="utf-8",
    )
    asked: list[list[str]] = []

    def not_ignored(command: "list[str]") -> SimpleNamespace:
        asked.append(list(command))
        return SimpleNamespace(returncode=1, stdout="", stderr="")

    code = plugin_mirror_preamble.ensure_plugin_mirror(
        repo,
        read_only=True,
        probe=not_ignored,
        log=lambda message: pytest.fail(f"nothing to report: {message}"),
    )

    assert code == 0
    assert asked == [
        ["git", "check-ignore", "--no-index", "-q", "--", "plugins/charness"]
    ], "the ignore question is the only child a non-mirror repo may provoke"
