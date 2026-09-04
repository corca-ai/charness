"""#792: prepare links an installed dependency tree instead of re-running the installer."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.worktree import worktree_create_lib as create_lib
from scripts.worktree import worktree_dependency_reuse as reuse
from scripts.worktree import worktree_doctor_lib as lib
from tests.charness_cli.worktree_fixtures import copy_worktree_seed

SPEC = reuse.ReuseSpec(
    command_id="install-deps",
    lockfile="lock.json",
    directory="deps",
    install_argv=("python3", "-c", "pass"),
)

# The install command writes a marker so a test can tell "reused" from "ran".
MANIFEST = (
    "version: 1\n"
    "prepare:\n"
    "  commands:\n"
    "    - id: install-deps\n"
    "      argv:\n"
    "        - python3\n"
    "        - -c\n"
    "        - \"import pathlib; pathlib.Path('deps').mkdir(exist_ok=True); "
    "pathlib.Path('deps/marker').write_text('installed'); pathlib.Path('installer-ran').touch()\"\n"
    "  dependency_reuse:\n"
    "    command_id: install-deps\n"
    "    lockfile: lock.json\n"
    "    directory: deps\n"
)


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _committed_primary(tmp_path: Path) -> Path:
    repo = copy_worktree_seed(tmp_path, "primary")
    (repo / ".agents").mkdir()
    (repo / ".agents" / "worktree-adapter.yaml").write_text(MANIFEST, encoding="utf-8")
    (repo / "lock.json").write_text('{"v": 1}\n', encoding="utf-8")
    (repo / ".gitignore").write_text("deps/\ninstaller-ran\n", encoding="utf-8")
    _git("add", ".", cwd=repo)
    _git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "adapter", cwd=repo)
    return repo


def _install(root: Path, content: str = "parent") -> None:
    (root / "deps" / "pkg").mkdir(parents=True)
    (root / "deps" / "pkg" / "index.js").write_text(content, encoding="utf-8")


def _doctor_pass(*_args, **_kwargs):
    return {"status": "pass", "checks": [], "manifest": {}, "next_step": None}


def test_validation_requires_a_declared_command_id_and_relative_paths() -> None:
    errors: list[str] = []
    reuse.validate_dependency_reuse(
        {
            "commands": [{"id": "install-deps", "argv": ["true"]}],
            "dependency_reuse": {
                "command_id": "other",
                "lockfile": "/abs/lock",
                "directory": "../deps",
            },
        },
        errors,
    )
    assert any("command_id 'other' names no prepare command id" in e for e in errors)
    assert any("lockfile must be a relative path" in e for e in errors)
    assert any("directory must be a relative path" in e for e in errors)


def test_reuse_must_name_exactly_one_prepare_command() -> None:
    errors: list[str] = []
    reuse.validate_dependency_reuse(
        {
            "commands": [
                {"id": "install-deps", "argv": ["true"]},
                {"id": "install-deps", "argv": ["false"]},
            ],
            "dependency_reuse": {
                "command_id": "install-deps",
                "lockfile": "lock.json",
                "directory": "deps",
            },
        },
        errors,
    )
    assert errors == [
        "manifest.prepare.dependency_reuse.command_id 'install-deps' names 2 prepare commands; "
        "reuse replaces exactly one"
    ]


def test_manifest_validation_reaches_the_reuse_block() -> None:
    errors = lib.validate_manifest(
        {
            "version": 1,
            "prepare": {
                "commands": [{"id": "install-deps", "argv": ["true"]}],
                "dependency_reuse": {"command_id": "install-deps"},
            },
        }
    )
    assert any("dependency_reuse.lockfile must be a non-empty string" in e for e in errors)


def test_reuse_links_the_parent_tree_when_the_lockfile_digest_matches(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    target = tmp_path / "target"
    for root in (parent, target):
        root.mkdir()
        (root / "lock.json").write_text("same", encoding="utf-8")
    _install(parent)

    result = reuse.attempt_reuse(target, SPEC, source_root=parent, cache_root=tmp_path / "cache")

    assert result["strategy"] in {reuse.STRATEGY_REFLINK, reuse.STRATEGY_HARDLINK}
    assert result["origin"] == reuse.ORIGIN_PARENT
    assert (target / "deps" / "pkg" / "index.js").read_text(encoding="utf-8") == "parent"
    assert not list(target.glob(".deps.charness-reuse-*")), "staging directory left behind"


def test_reflink_is_probed_on_one_file_before_the_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = tmp_path / "parent"
    target = tmp_path / "target"
    for root in (parent, target):
        root.mkdir()
        (root / "lock.json").write_text("same", encoding="utf-8")
    _install(parent)
    calls: list[list[str]] = []
    real_run = reuse._run

    def recording_run(argv: list[str], timeout_seconds: int):
        calls.append(list(argv))
        if "--reflink=always" in argv:
            return 1, "cp: failed to clone: Operation not supported"
        return real_run(argv, timeout_seconds)

    monkeypatch.setattr(reuse, "_run", recording_run)

    result = reuse.attempt_reuse(target, SPEC, source_root=parent, cache_root=None)

    reflink_calls = [argv for argv in calls if "--reflink=always" in argv]
    assert len(reflink_calls) == 1 and "-a" not in reflink_calls[0], calls
    assert result["strategy"] == reuse.STRATEGY_HARDLINK
    assert result["attempts"][0]["link"][0] == {
        "strategy": reuse.STRATEGY_REFLINK,
        "ok": False,
        "detail": "cp: failed to clone: Operation not supported",
    }
    assert not list(target.glob(".charness-reflink-probe-*"))


def test_reuse_refuses_a_parent_whose_lockfile_differs(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    target = tmp_path / "target"
    parent.mkdir()
    target.mkdir()
    (parent / "lock.json").write_text("old", encoding="utf-8")
    (target / "lock.json").write_text("new", encoding="utf-8")
    _install(parent)

    result = reuse.attempt_reuse(target, SPEC, source_root=parent, cache_root=None)

    assert result["strategy"] == reuse.STRATEGY_NONE
    assert not (target / "deps").exists()
    assert result["attempts"][0]["declined"] == "parent lockfile digest differs"


def test_reuse_falls_back_to_the_cache_keyed_by_lockfile_digest(tmp_path: Path) -> None:
    donor = tmp_path / "donor"
    target = tmp_path / "target"
    cache = tmp_path / "cache"
    for root in (donor, target):
        root.mkdir()
        (root / "lock.json").write_text("same", encoding="utf-8")
    _install(donor, "cached")

    seeded = reuse.seed_cache(donor, SPEC, cache_root=cache)
    assert seeded["seeded"] is True
    meta = json.loads((Path(seeded["entry"]) / reuse.CACHE_META_NAME).read_text(encoding="utf-8"))
    assert meta["directory"] == "deps"

    result = reuse.attempt_reuse(target, SPEC, source_root=None, cache_root=cache)

    assert result["origin"] == reuse.ORIGIN_CACHE
    assert (target / "deps" / "pkg" / "index.js").read_text(encoding="utf-8") == "cached"
    assert (
        reuse.seed_cache(donor, SPEC, cache_root=cache)["reason"] == "cache entry already present"
    )


def test_cache_entries_are_keyed_by_the_runtime_fingerprint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    donor = tmp_path / "donor"
    target = tmp_path / "target"
    cache = tmp_path / "cache"
    for root in (donor, target):
        root.mkdir()
        (root / "lock.json").write_text("same", encoding="utf-8")
    _install(donor, "old-abi")
    monkeypatch.setattr(
        reuse, "runtime_fingerprint", lambda _spec, **_k: "linux/x86_64/npm=10/node=v20"
    )
    seeded = reuse.seed_cache(donor, SPEC, cache_root=cache)
    assert seeded["seeded"] is True
    meta = json.loads((Path(seeded["entry"]) / reuse.CACHE_META_NAME).read_text(encoding="utf-8"))
    assert meta["runtime"] == "linux/x86_64/npm=10/node=v20"

    monkeypatch.setattr(
        reuse, "runtime_fingerprint", lambda _spec, **_k: "linux/x86_64/npm=10/node=v22"
    )
    result = reuse.attempt_reuse(target, SPEC, source_root=None, cache_root=cache)

    assert result["strategy"] == reuse.STRATEGY_NONE
    assert not (target / "deps").exists()


def test_an_unanswered_version_probe_neither_publishes_nor_consumes_the_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    donor = tmp_path / "donor"
    target = tmp_path / "target"
    cache = tmp_path / "cache"
    for root in (donor, target):
        root.mkdir()
        (root / "lock.json").write_text("same", encoding="utf-8")
    _install(donor)
    good = reuse.seed_cache(donor, SPEC, cache_root=cache)
    assert good["seeded"] is True
    unknown = reuse.ReuseSpec("install-deps", "lock.json", "deps", ("no-such-tool-792",))

    refused = reuse.seed_cache(donor, unknown, cache_root=cache)
    result = reuse.attempt_reuse(target, unknown, source_root=None, cache_root=cache)

    assert refused["seeded"] is False
    assert refused["reason"] == "runtime fingerprint unknown; not published to the cache"
    assert result["strategy"] == reuse.STRATEGY_NONE
    assert result["attempts"][0]["declined"] == "runtime fingerprint unknown"
    assert len(list(cache.iterdir())) == 1


def test_the_runtime_fingerprint_names_the_install_tool_and_node(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_capture(argv: list[str], timeout_seconds: int, *, cwd=None):
        return 0, "", {"npm": "10.9.0\n", "node": "v22.1.0\n"}[argv[0]]

    monkeypatch.setattr(reuse, "_run_capture", fake_capture)
    spec = reuse.ReuseSpec("install-deps", "package-lock.json", "node_modules", ("npm", "ci"))

    fingerprint = reuse.runtime_fingerprint(spec, cwd=Path("/tree"))

    assert fingerprint.endswith("/npm=10.9.0/node=v22.1.0")
    monkeypatch.setattr(
        reuse, "_run_capture", lambda argv, timeout_seconds, cwd=None: (1, "boom", "")
    )
    assert reuse.runtime_fingerprint(spec, cwd=Path("/tree")) is None
    assert reuse.ReuseSpec.from_manifest(
        {
            "commands": [{"id": "install-deps", "argv": ["npm", "ci"]}],
            "dependency_reuse": {
                "command_id": "install-deps",
                "lockfile": "package-lock.json",
                "directory": "node_modules",
            },
        }
    ).install_argv == ("npm", "ci")


def test_version_probes_are_not_cached_between_fingerprint_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers = iter(["10.0.0\n", "11.0.0\n"])

    def changing_capture(argv: list[str], timeout_seconds: int, *, cwd=None):
        return 0, "", next(answers)

    monkeypatch.setattr(reuse, "_run_capture", changing_capture)
    spec = reuse.ReuseSpec("install-deps", "uv.lock", ".venv", ("uv", "sync"))

    first = reuse.runtime_fingerprint(spec, cwd=Path("/tree"))
    second = reuse.runtime_fingerprint(spec, cwd=Path("/tree"))

    assert first.endswith("/uv=10.0.0") and second.endswith("/uv=11.0.0")


def test_one_fingerprint_observation_keys_both_the_entry_path_and_its_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    donor = tmp_path / "donor"
    target = tmp_path / "target"
    cache = tmp_path / "cache"
    for root in (donor, target):
        root.mkdir()
        (root / "lock.json").write_text("same", encoding="utf-8")
    _install(donor, "snap")
    counter = iter(range(1, 100))
    monkeypatch.setattr(
        reuse, "runtime_fingerprint", lambda _spec, **_k: f"linux/x86_64/tool={next(counter)}"
    )

    seeded = reuse.seed_cache(donor, SPEC, cache_root=cache)
    entry = Path(seeded["entry"])
    meta = json.loads((entry / reuse.CACHE_META_NAME).read_text(encoding="utf-8"))

    assert seeded["seeded"] is True
    assert entry == reuse.cache_entry(
        cache, reuse.lockfile_digest(donor / "lock.json"), SPEC, meta["runtime"]
    )
    assert meta["runtime"] == "linux/x86_64/tool=1"
    monkeypatch.setattr(reuse, "runtime_fingerprint", lambda _spec, **_k: "linux/x86_64/tool=1")
    assert reuse.attempt_reuse(target, SPEC, source_root=None, cache_root=cache)["origin"] == (
        reuse.ORIGIN_CACHE
    )


def test_a_non_node_install_tool_never_probes_node(monkeypatch: pytest.MonkeyPatch) -> None:
    probed: list[str] = []

    def trapping_capture(argv: list[str], timeout_seconds: int, *, cwd=None):
        probed.append(argv[0])
        if argv[0] == "node":
            raise AssertionError("node was probed for a non-Node install tool")
        return 0, "", "0.4.0\n"

    monkeypatch.setattr(reuse, "_run_capture", trapping_capture)
    spec = reuse.ReuseSpec("install-deps", "uv.lock", ".venv", ("uv", "sync"))

    assert reuse.runtime_fingerprint(spec, cwd=Path("/tree")).endswith("/uv=0.4.0")
    assert probed == ["uv"]


def test_version_probes_run_in_the_worktree_not_the_launcher_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    donor = tmp_path / "donor"
    target = tmp_path / "target"
    for root in (donor, target):
        root.mkdir()
        (root / "lock.json").write_text("same", encoding="utf-8")
    _install(donor)
    seen: list[tuple[str, Path | None]] = []
    real = reuse._run_capture

    def recording(argv: list[str], timeout_seconds: int, *, cwd=None):
        if argv[-1] == "--version":
            seen.append((argv[0], cwd))
            return 0, "", "1.0\n"
        return real(argv, timeout_seconds, cwd=cwd)

    monkeypatch.setattr(reuse, "_run_capture", recording)
    monkeypatch.chdir(tmp_path)

    reuse.seed_cache(donor, SPEC, cache_root=tmp_path / "cache")
    reuse.attempt_reuse(target, SPEC, source_root=None, cache_root=tmp_path / "cache")

    assert seen == [("python3", donor.resolve()), ("python3", target.resolve())]


def test_reuse_leaves_an_existing_install_directory_alone(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "lock.json").write_text("same", encoding="utf-8")
    _install(target, "mine")

    result = reuse.attempt_reuse(target, SPEC, source_root=None, cache_root=None)

    assert result["strategy"] == reuse.STRATEGY_NONE
    assert result["reason"] == "install directory already present"
    assert (target / "deps" / "pkg" / "index.js").read_text(encoding="utf-8") == "mine"


def test_prepare_reuses_the_parent_and_skips_the_install_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    primary = _committed_primary(tmp_path)
    _install(primary)
    monkeypatch.setattr(lib, "run_doctor", _doctor_pass)
    target = tmp_path / "feature"

    payload = create_lib.run_create(
        primary,
        target_path=target,
        branch="feature",
        base="main",
        prepare=True,
        dependency_cache_root=tmp_path / "cache",
    )

    prepare = payload["prepare"]
    assert payload["status"] == create_lib.PASS, payload
    assert prepare["executed"] == []
    assert prepare["dependency_reuse"]["origin"] == reuse.ORIGIN_PARENT
    assert prepare["dependency_reuse"]["command_id"] == "install-deps"
    assert (target / "deps" / "pkg" / "index.js").read_text(encoding="utf-8") == "parent"
    assert not (target / "installer-ran").exists()


def test_prepare_runs_the_installer_and_seeds_the_cache_when_nothing_matches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    primary = _committed_primary(tmp_path)
    monkeypatch.setattr(lib, "run_doctor", _doctor_pass)
    cache = tmp_path / "cache"

    first = lib.run_prepare(primary, force=True, dependency_cache_root=cache)

    assert first["status"] == "pass"
    assert [item["id"] for item in first["executed"]] == ["install-deps"]
    assert first["dependency_reuse"]["strategy"] == reuse.STRATEGY_NONE
    assert first["dependency_reuse"]["cache_seed"]["seeded"] is True

    # A later worktree with the same lockfile and no parent install reuses the cache.
    target = tmp_path / "later"
    target.mkdir()
    (target / "lock.json").write_text('{"v": 1}\n', encoding="utf-8")
    (target / ".agents").mkdir()
    (target / ".agents" / "worktree-adapter.yaml").write_text(MANIFEST, encoding="utf-8")
    second = lib.run_prepare(target, force=True, dependency_cache_root=cache)

    assert second["executed"] == []
    assert second["dependency_reuse"]["origin"] == reuse.ORIGIN_CACHE
    assert (target / "deps" / "marker").read_text(encoding="utf-8").strip() == "installed"


def test_prepare_can_disable_reuse_and_records_why(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    primary = _committed_primary(tmp_path)
    monkeypatch.setattr(lib, "run_doctor", _doctor_pass)

    payload = lib.run_prepare(
        primary, force=True, dependency_cache_root=tmp_path / "cache", dependency_reuse=False
    )

    assert [item["id"] for item in payload["executed"]] == ["install-deps"]
    assert payload["dependency_reuse"]["reason"] == "disabled by --no-dependency-reuse"
    assert "cache_seed" not in payload["dependency_reuse"]


def test_prepare_names_the_reused_tree_when_doctor_rejects_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    primary = _committed_primary(tmp_path)
    _install(primary)
    target = tmp_path / "feature"
    _git("worktree", "add", "-q", "-b", "feature", str(target), "main", cwd=primary)
    (target / ".agents" / "worktree-adapter.yaml").write_text(
        MANIFEST
        + (
            "doctor:\n"
            "  checks:\n"
            "    - id: deps-ready\n"
            "      covers:\n"
            "        - install-deps\n"
            "      argv:\n"
            "        - '/bin/false'\n"
        ),
        encoding="utf-8",
    )
    failing = {"id": "deps-ready", "status": "fail"}
    verdicts = iter(
        [
            {"status": "fail", "checks": [failing], "manifest": {}, "next_step": "pre"},
            {"status": "fail", "checks": [failing], "manifest": {}, "next_step": "post"},
        ]
    )
    monkeypatch.setattr(lib, "run_doctor", lambda *_a, **_k: next(verdicts))

    payload = lib.run_prepare(target, source_root=primary, dependency_cache_root=tmp_path / "cache")

    assert payload["status"] == "fail"
    assert "--no-dependency-reuse" in payload["next_step"]
    assert str(primary.resolve() / "deps") in payload["next_step"]


def test_an_unrelated_doctor_failure_keeps_the_doctors_own_next_step(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    primary = _committed_primary(tmp_path)
    _install(primary)
    target = tmp_path / "feature"
    _git("worktree", "add", "-q", "-b", "feature", str(target), "main", cwd=primary)
    hooks = {"id": "hooks_path", "status": "fail"}
    verdicts = iter(
        [
            {"status": "fail", "checks": [hooks], "manifest": {}, "next_step": "pre"},
            {"status": "fail", "checks": [hooks], "manifest": {}, "next_step": "fix hooks"},
        ]
    )
    monkeypatch.setattr(lib, "run_doctor", lambda *_a, **_k: next(verdicts))

    payload = lib.run_prepare(target, source_root=primary, dependency_cache_root=tmp_path / "cache")

    assert payload["dependency_reuse"]["origin"] == reuse.ORIGIN_PARENT
    assert payload["next_step"] == "fix hooks"


def test_a_fresh_install_the_doctor_rejects_is_not_published_to_the_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    primary = _committed_primary(tmp_path)
    verdicts = iter(
        [
            {"status": "fail", "checks": [], "manifest": {}, "next_step": "pre"},
            {"status": "fail", "checks": [], "manifest": {}, "next_step": "post"},
        ]
    )
    monkeypatch.setattr(lib, "run_doctor", lambda *_a, **_k: next(verdicts))
    cache = tmp_path / "cache"

    payload = lib.run_prepare(primary, force=True, dependency_cache_root=cache)

    assert [item["id"] for item in payload["executed"]] == ["install-deps"]
    assert payload["dependency_reuse"]["cache_seed"]["seeded"] is False
    assert "doctor rejected" in payload["dependency_reuse"]["cache_seed"]["reason"]
    assert not cache.exists() or not any(cache.iterdir())
    later = tmp_path / "later"
    later.mkdir()
    (later / "lock.json").write_text('{"v": 1}\n', encoding="utf-8")
    result = reuse.attempt_reuse(later, SPEC, source_root=None, cache_root=cache)
    assert result["strategy"] == reuse.STRATEGY_NONE


def test_plain_prepare_on_a_linked_worktree_reuses_the_main_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    primary = _committed_primary(tmp_path)
    _install(primary)
    target = tmp_path / "feature"
    _git("worktree", "add", "-q", "-b", "feature", str(target), "main", cwd=primary)
    monkeypatch.setattr(lib, "run_doctor", _doctor_pass)

    payload = lib.run_prepare(target, dependency_cache_root=tmp_path / "cache")

    assert payload["executed"] == []
    assert payload["dependency_reuse"]["origin"] == reuse.ORIGIN_PARENT
    assert payload["dependency_reuse"]["source"] == str(primary.resolve() / "deps")


def test_cache_root_defaults_to_the_owning_repo_runtime_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import runtime_bootstrap

    primary = _committed_primary(tmp_path)
    target = tmp_path / "feature"
    _git("worktree", "add", "-q", "-b", "feature", str(target), "main", cwd=primary)
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT", raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))

    derived = lib.default_dependency_cache_root(target, None)

    assert derived == runtime_bootstrap.runtime_root(primary) / reuse.CACHE_DIR_NAME
    assert lib.default_dependency_cache_root(target, primary) == derived


# --- edge branches the release changed-line gate requires to be exercised ---


def _spec(**overrides) -> reuse.ReuseSpec:
    base = dict(
        command_id="install-deps",
        lockfile="lock.json",
        directory="deps",
        install_argv=("python3", "-c", "pass"),
    )
    base.update(overrides)
    return reuse.ReuseSpec(**base)


def test_validation_rejects_a_non_mapping_reuse_block() -> None:
    errors: list[str] = []
    reuse.validate_dependency_reuse({"commands": [], "dependency_reuse": "yes"}, errors)
    assert errors == ["manifest.prepare.dependency_reuse must be a mapping"]


def test_lockfile_digest_is_none_for_a_missing_file(tmp_path: Path) -> None:
    assert reuse.lockfile_digest(tmp_path / "absent") is None


def test_fingerprint_is_unknown_without_an_install_argv_or_without_node(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert reuse.runtime_fingerprint(_spec(install_argv=()), cwd=Path("/tree")) is None

    def npm_only(argv: list[str], timeout_seconds: int, *, cwd=None):
        return (0, "", "10.0.0\n") if argv[0] == "npm" else (1, "", "")

    monkeypatch.setattr(reuse, "_run_capture", npm_only)
    assert reuse.runtime_fingerprint(_spec(install_argv=("npm", "ci")), cwd=Path("/t")) is None


def test_run_capture_reports_a_timeout_and_a_missing_binary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess as sp

    monkeypatch.setattr(
        reuse,
        "run_process",
        lambda argv, cwd, timeout_seconds: sp.CompletedProcess(
            argv, reuse.TIMEOUT_EXIT_CODE, "", ""
        ),
    )
    assert reuse._run_capture(["slow"], 1) == (None, "timed out after 1s", "")
    monkeypatch.undo()
    assert reuse._run(["no-such-binary-792-x"], 1)[1].startswith("command not found")


def test_reflink_probe_declines_an_empty_source(tmp_path: Path) -> None:
    (tmp_path / "empty").mkdir()
    assert reuse._reflink_supported(tmp_path / "empty", tmp_path) == (
        False,
        "no regular file to probe",
    )


def test_link_tree_tries_reflink_first_when_the_probe_says_supported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "src"
    _install(source)
    monkeypatch.setattr(reuse, "_reflink_supported", lambda *_a: (True, ""))
    tried: list[list[str]] = []
    real_run = reuse._run

    def recording(argv: list[str], timeout_seconds: int):
        tried.append(argv[:2])
        return real_run(argv, timeout_seconds)

    monkeypatch.setattr(reuse, "_run", recording)
    strategy, attempts = reuse._link_tree(source / "deps", tmp_path / "dst", timeout_seconds=30)
    assert tried[0][1] == "-a" and strategy in {reuse.STRATEGY_REFLINK, reuse.STRATEGY_HARDLINK}
    assert attempts[-1]["ok"] is True


def test_link_tree_reports_a_failed_rename_and_a_total_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "src"
    _install(source)

    def boom(*_a, **_k):
        raise OSError("rename refused")

    monkeypatch.setattr(reuse.os, "rename", boom)
    strategy, attempts = reuse._link_tree(source / "deps", tmp_path / "dst", timeout_seconds=30)
    assert strategy is None and attempts[-1]["detail"] == "rename refused"
    assert not list(tmp_path.glob(".dst.charness-reuse-*"))

    monkeypatch.setattr(reuse, "_run", lambda argv, timeout_seconds: (1, "nope"))
    strategy, attempts = reuse._link_tree(source / "deps", tmp_path / "dst2", timeout_seconds=30)
    assert strategy is None and all(not a["ok"] for a in attempts)


def test_remove_tree_handles_files_and_directories(tmp_path: Path) -> None:
    f = tmp_path / "f"
    f.write_text("x", encoding="utf-8")
    d = tmp_path / "d"
    (d / "inner").mkdir(parents=True)
    reuse._remove_tree(f)
    reuse._remove_tree(d)
    assert not f.exists() and not d.exists()


def test_attempt_reuse_declines_unreadable_lockfile_self_parent_and_uninstalled_parent(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    assert (
        "unreadable"
        in reuse.attempt_reuse(target, SPEC, source_root=None, cache_root=None)["reason"]
    )
    (target / "lock.json").write_text("same", encoding="utf-8")
    result = reuse.attempt_reuse(target, SPEC, source_root=target, cache_root=None)
    assert result["attempts"][0]["declined"] == "parent is the worktree itself"
    parent = tmp_path / "parent"
    parent.mkdir()
    (parent / "lock.json").write_text("same", encoding="utf-8")
    result = reuse.attempt_reuse(target, SPEC, source_root=parent, cache_root=None)
    assert result["attempts"][0]["declined"] == "parent has no install directory"


def test_a_parent_whose_lockfile_changes_during_the_link_is_discarded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = tmp_path / "parent"
    target = tmp_path / "target"
    for root in (parent, target):
        root.mkdir()
        (root / "lock.json").write_text("same", encoding="utf-8")
    _install(parent)
    real_link = reuse._link_tree

    def racing(source: Path, destination: Path, *, timeout_seconds: int):
        result = real_link(source, destination, timeout_seconds=timeout_seconds)
        (parent / "lock.json").write_text("moved", encoding="utf-8")
        return result

    monkeypatch.setattr(reuse, "_link_tree", racing)
    result = reuse.attempt_reuse(target, SPEC, source_root=parent, cache_root=None)
    assert result["strategy"] == reuse.STRATEGY_NONE
    assert result["attempts"][0]["link"][-1]["detail"] == "parent lockfile changed during link"
    assert not (target / "deps").exists()


def test_seed_cache_names_every_reason_it_declines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    donor = tmp_path / "donor"
    donor.mkdir()
    assert reuse.seed_cache(donor, SPEC, cache_root=None)["reason"] == "no cache root"
    assert "absent" in reuse.seed_cache(donor, SPEC, cache_root=tmp_path / "c")["reason"]
    _install(donor)
    assert "unreadable" in reuse.seed_cache(donor, SPEC, cache_root=tmp_path / "c")["reason"]
    (donor / "lock.json").write_text("same", encoding="utf-8")
    blocker = tmp_path / "blocker"
    blocker.write_text("not a dir", encoding="utf-8")
    assert "not writable" in reuse.seed_cache(donor, SPEC, cache_root=blocker / "c")["reason"]

    monkeypatch.setattr(reuse, "_run", lambda argv, timeout_seconds: (1, "cp refused"))
    failed = reuse.seed_cache(donor, SPEC, cache_root=tmp_path / "c2")
    assert failed["reason"].startswith("hard-link into cache failed: cp refused")
    monkeypatch.undo()

    def boom(*_a, **_k):
        raise OSError("exists")

    monkeypatch.setattr(reuse.os, "rename", boom)
    raced = reuse.seed_cache(donor, SPEC, cache_root=tmp_path / "c3")
    assert raced["reason"] == "cache entry appeared concurrently" and raced["seeded"] is False


def test_prepare_command_missing_binary_and_timeout_are_reported(tmp_path: Path) -> None:
    from scripts.worktree import worktree_prepare_lib as prepare_lib

    result, failed = prepare_lib._execute_prepare_command(
        {"id": "x", "argv": ["no-such-binary-792"]}, tmp_path
    )
    assert failed and result.exit_code is None and "command not found" in result.stderr_tail
    result, failed = prepare_lib._execute_prepare_command(
        {"id": "slow", "argv": ["sleep", "5"], "timeout_seconds": 1}, tmp_path
    )
    assert failed and result.timed_out is True
    assert (
        prepare_lib._covers_by_check({"doctor": {"checks": ["not-a-mapping", {"id": "a"}]}}) == {}
    )


def test_task_run_records_the_dependency_path_beside_the_create_payload() -> None:
    from scripts.task_run import task_run_support

    payload: dict = {}
    task_run_support.record_create(
        payload, {"created": True, "prepare": {"dependency_reuse": {"strategy": "hardlink"}}}
    )
    assert payload["created"] is True and payload["dependency_reuse"] == {"strategy": "hardlink"}


def test_the_prepare_script_and_the_reuse_modules_run_as_scripts(tmp_path: Path) -> None:
    import subprocess as sp
    import sys

    primary = _committed_primary(tmp_path)
    root = Path(__file__).resolve().parents[2]
    out = sp.run(
        [
            sys.executable,
            str(root / "scripts/worktree/worktree_prepare.py"),
            "--repo-root",
            str(primary),
            "--no-dependency-reuse",
            "--force",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )
    assert "disabled by --no-dependency-reuse" in out.stdout, out.stderr
    for module in ("worktree_dependency_reuse.py", "worktree_prepare_lib.py"):
        assert (
            sp.run(
                [sys.executable, str(root / "scripts/worktree" / module)],
                cwd=tmp_path,
                capture_output=True,
            ).returncode
            == 0
        )
