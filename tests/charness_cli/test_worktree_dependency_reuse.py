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

SPEC = reuse.ReuseSpec(command_id="install-deps", lockfile="lock.json", directory="deps")

# The install command writes a marker so a test can tell "reused" from "ran".
MANIFEST = (
    "version: 1\n"
    "prepare:\n"
    "  commands:\n"
    "    - id: install-deps\n"
    "      argv:\n"
    "        - sh\n"
    "        - -c\n"
    "        - 'mkdir -p deps && echo installed > deps/marker && touch installer-ran'\n"
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
    monkeypatch.setattr(reuse, "runtime_fingerprint", lambda _spec: "linux/x86_64/npm=10/node=v20")
    seeded = reuse.seed_cache(donor, SPEC, cache_root=cache)
    assert seeded["seeded"] is True
    meta = json.loads((Path(seeded["entry"]) / reuse.CACHE_META_NAME).read_text(encoding="utf-8"))
    assert meta["runtime"] == "linux/x86_64/npm=10/node=v20"

    monkeypatch.setattr(reuse, "runtime_fingerprint", lambda _spec: "linux/x86_64/npm=10/node=v22")
    result = reuse.attempt_reuse(target, SPEC, source_root=None, cache_root=cache)

    assert result["strategy"] == reuse.STRATEGY_NONE
    assert not (target / "deps").exists()


def test_the_runtime_fingerprint_names_the_install_tool_and_node(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(reuse, "_VERSION_PROBES", {})

    def fake_capture(argv: list[str], timeout_seconds: int):
        return 0, "", {"npm": "10.9.0\n", "node": "v22.1.0\n"}[argv[0]]

    monkeypatch.setattr(reuse, "_run_capture", fake_capture)
    spec = reuse.ReuseSpec("install-deps", "package-lock.json", "node_modules", ("npm", "ci"))

    fingerprint = reuse.runtime_fingerprint(spec)

    assert fingerprint.endswith("/npm=10.9.0/node=v22.1.0")
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
