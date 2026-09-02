"""Tests for the #432 lingering `.invalid` git identity refusal gate.

The gate (`scripts/gates/check_git_identity.py`) resolves the EFFECTIVE commit
identity the way git itself would (`git var GIT_AUTHOR_IDENT` / `git var
GIT_COMMITTER_IDENT`, which honor config AND environment overrides) and refuses
when either resolved email's domain is the RFC 2606 `.invalid` placeholder TLD.
"""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
from pathlib import Path

import pytest

from .support import run_script

cgi = importlib.import_module("scripts.gates.check_git_identity")

_RELEASE_PREFLIGHT_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "public"
    / "release"
    / "scripts"
    / "publish_release_preflight.py"
)


def _load_release_preflight():
    spec = importlib.util.spec_from_file_location(
        "publish_release_preflight_parity_probe", _RELEASE_PREFLIGHT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _repo(tmp_path: Path) -> Path:
    from tests.quality_gates.git_fixture_support import init_git_repo

    repo = tmp_path / "repo"
    repo.mkdir()
    init_git_repo(repo)
    return repo


def test_local_invalid_email_is_flagged() -> None:
    finding = cgi.find_invalid_identity(
        {"author": "hotl proof <x@example.invalid>", "committer": "hotl proof <x@example.invalid>"}
    )
    assert finding is not None
    kind, ident = finding
    assert kind == "author"
    assert "x@example.invalid" in ident


def test_normal_email_passes() -> None:
    assert (
        cgi.find_invalid_identity(
            {"author": "Dev <dev@example.com>", "committer": "Dev <dev@example.com>"}
        )
        is None
    )


def test_env_committer_override_is_flagged(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    _git(repo, "config", "user.email", "dev@example.com")
    _git(repo, "config", "user.name", "Dev")
    # Clean config alone would pass; a lingering committer env override (the
    # #432 shape when a proof script sets GIT_COMMITTER_* without restoring it)
    # must still be caught, because it changes the EFFECTIVE identity git uses.
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "y@host.invalid")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "hotl proof")

    idents = cgi.resolve_idents(str(repo))
    finding = cgi.find_invalid_identity(idents)

    assert finding is not None
    kind, ident = finding
    assert kind == "committer"
    assert "y@host.invalid" in ident


def test_git_var_failure_does_not_block(monkeypatch) -> None:
    # Simulate `git var` being unable to resolve either identity at all (a
    # fresh environment with no user.email configured anywhere). This gate
    # must not add a new failure mode there -- git itself refuses the commit.
    monkeypatch.setattr(
        cgi,
        "run_process",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr="fatal: empty ident\n"
        ),
    )
    assert cgi.main(["--repo-root", "."]) == 0


def test_cli_blocks_local_invalid_config(tmp_path: Path, no_ambient_git_identity) -> None:
    repo = _repo(tmp_path)
    _git(repo, "config", "user.email", "x@example.invalid")
    _git(repo, "config", "user.name", "hotl proof")

    result = run_script("scripts/gates/check_git_identity.py", "--repo-root", str(repo))

    assert result.returncode == 1, result.stdout
    assert "BLOCKED" in result.stdout
    assert "x@example.invalid" in result.stdout


def test_cli_passes_clean_identity(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _git(repo, "config", "user.email", "dev@example.com")
    _git(repo, "config", "user.name", "Dev")

    result = run_script("scripts/gates/check_git_identity.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stdout
    assert "clean" in result.stdout


@pytest.mark.parametrize(
    ("email", "expect_blocked"),
    [
        ("dev@example.com", False),
        ("hotl-proof@example.invalid", True),
        ("x@HOST.INVALID", True),
        ("synthetic@internal.test", False),
    ],
)
def test_release_preflight_parity(email: str, expect_blocked: bool) -> None:
    # The release preflight duplicates the resolve+check logic because the
    # plugin ships standalone and cannot import repo-root scripts. This parity
    # matrix binds the two copies: a semantic divergence in either detector
    # fails here instead of drifting silently.
    ident = f"Someone <{email}>"
    repo_root_verdict = cgi.find_invalid_identity({"author": ident, "committer": ident}) is not None
    preflight = _load_release_preflight()
    match = preflight._IDENTITY_EMAIL_RE.search(ident)
    parsed = match.group(1) if match else None
    release_verdict = bool(
        parsed and parsed.strip().lower().endswith(preflight._INVALID_IDENTITY_SUFFIX)
    )
    assert repo_root_verdict == release_verdict == expect_blocked


def test_release_preflight_unresolvable_ident_not_blocked(monkeypatch) -> None:
    # Parity with the repo-root gate's `git var` failure path: when neither
    # ident resolves (fresh environment, no identity anywhere), the release
    # blocker must not add a new failure mode -- git itself refuses the commit.
    preflight = _load_release_preflight()
    monkeypatch.setattr(
        preflight,
        "run_process",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr="fatal: empty ident\n"
        ),
    )
    assert preflight.invalid_git_identity_blocker(Path(".")) is None
