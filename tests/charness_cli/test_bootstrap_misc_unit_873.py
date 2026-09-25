"""Direct unit tests for `bootstrap` uncovered branches (#873)."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.cli.bootstrap as bootstrap


def _result(returncode: int = 0, stdout: str = "", stderr: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_resolve_state_home_prefers_xdg_state_home(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("CHARNESS_STATE_HOME", raising=False)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg"))
    assert bootstrap.resolve_state_home(tmp_path) == (tmp_path / "xdg").resolve()


def test_git_upstream_ref_returns_none_on_failure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(bootstrap, "run", lambda *args, **kwargs: _result(returncode=1))
    assert bootstrap.git_upstream_ref(tmp_path) is None


def test_git_upstream_divergence_without_upstream(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(bootstrap, "git_upstream_ref", lambda path: None)
    assert bootstrap.git_upstream_divergence(tmp_path) is None


def test_git_upstream_divergence_returns_none_on_rev_list_failure(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(bootstrap, "git_upstream_ref", lambda path: "origin/main")
    monkeypatch.setattr(bootstrap, "run", lambda *args, **kwargs: _result(returncode=1))
    assert bootstrap.git_upstream_divergence(tmp_path) is None


def test_git_upstream_divergence_rejects_bad_counts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(bootstrap, "git_upstream_ref", lambda path: "origin/main")
    monkeypatch.setattr(
        bootstrap, "run", lambda *args, **kwargs: _result(stdout="only-one-token\n")
    )
    assert bootstrap.git_upstream_divergence(tmp_path) is None
    monkeypatch.setattr(bootstrap, "run", lambda *args, **kwargs: _result(stdout="a b\n"))
    assert bootstrap.git_upstream_divergence(tmp_path) is None


def test_packaging_version_returns_none_without_manifest(tmp_path: Path) -> None:
    assert bootstrap.packaging_version(tmp_path) is None


def test_read_install_state_rejects_bad_payloads(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CHARNESS_STATE_HOME", str(tmp_path))
    path = bootstrap.default_install_state_path(tmp_path / "home")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")
    assert bootstrap.read_install_state(tmp_path / "home") is None
    path.write_text(json.dumps({"repo_root": 123, "managed_checkout": True}), encoding="utf-8")
    assert bootstrap.read_install_state(tmp_path / "home") is None


def test_enforce_managed_cli_contract_passes_for_managed_or_skipped(
    tmp_path: Path,
) -> None:
    bootstrap.enforce_managed_cli_contract(
        home_root=tmp_path, repo_root=tmp_path, managed_checkout=True, skip_cli_install=False
    )
    bootstrap.enforce_managed_cli_contract(
        home_root=tmp_path, repo_root=tmp_path, managed_checkout=False, skip_cli_install=True
    )


def test_ensure_checkout_rejects_non_git_manifest_dir(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text('{"version": "1.0"}', encoding="utf-8")
    with pytest.raises(bootstrap.CharnessError):
        bootstrap.ensure_checkout(
            repo,
            managed=True,
            repo_url="https://example.test/r",
            allow_clone=False,
            allow_pull=True,
        )


def test_ensure_checkout_pulls_clean_managed_checkout(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text('{"version": "1.0"}', encoding="utf-8")
    (repo / ".git").mkdir()

    def _fake_run(command: list[str], **kwargs) -> SimpleNamespace:
        assert command[0] == "git"
        return _result(stdout="")

    monkeypatch.setattr(bootstrap, "run", _fake_run)
    outcome = bootstrap.ensure_checkout(
        repo, managed=True, repo_url="https://example.test/r", allow_clone=False, allow_pull=True
    )
    assert outcome["pulled"] is True


def test_ensure_checkout_rejects_non_empty_non_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "junk"
    repo.mkdir()
    (repo / "stray.txt").write_text("x", encoding="utf-8")
    with pytest.raises(bootstrap.CharnessError):
        bootstrap.ensure_checkout(
            repo,
            managed=True,
            repo_url="https://example.test/r",
            allow_clone=True,
            allow_pull=False,
        )


def test_ensure_checkout_rejects_missing_checkout_without_clone(tmp_path: Path) -> None:
    with pytest.raises(bootstrap.CharnessError):
        bootstrap.ensure_checkout(
            tmp_path / "missing",
            managed=True,
            repo_url="https://example.test/r",
            allow_clone=False,
            allow_pull=False,
        )


def test_ensure_checkout_rejects_explicit_missing_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "empty-explicit"
    repo.mkdir()
    with pytest.raises(bootstrap.CharnessError):
        bootstrap.ensure_checkout(
            repo,
            managed=False,
            repo_url="https://example.test/r",
            allow_clone=False,
            allow_pull=False,
        )


def test_ensure_checkout_clones_missing_managed_checkout(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "fresh" / "repo"
    monkeypatch.setattr(bootstrap, "run", lambda *args, **kwargs: _result(stdout=""))
    outcome = bootstrap.ensure_checkout(
        repo, managed=True, repo_url="https://example.test/r", allow_clone=True, allow_pull=False
    )
    assert outcome == {"repo_root": str(repo), "managed": True, "cloned": True, "pulled": False}
