"""The shared adapter universe reader and its empty-scope rule."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scripts.quality_adapter_lib import load_quality_adapter
from scripts.quality_universes_lib import (
    DEFAULT_UNIVERSES,
    Universe,
    matching_files,
    refuse_if_declared_and_empty,
    resolve_universe,
)


def _adapter(tmp_path: Path, block: str = "") -> dict:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: testrepo\nlanguage: en\noutput_dir: charness-artifacts/quality\n"
        + block,
        encoding="utf-8",
    )
    return load_quality_adapter(repo)


def test_undeclared_family_uses_the_default(tmp_path: Path) -> None:
    payload = _adapter(tmp_path)

    resolved = resolve_universe(
        payload, "python_sources", default=DEFAULT_UNIVERSES["python_sources"]
    )

    assert resolved.patterns == tuple(DEFAULT_UNIVERSES["python_sources"])
    assert resolved.declared is False
    assert resolved.source == "default"


def test_declared_family_wins_over_the_default(tmp_path: Path) -> None:
    payload = _adapter(
        tmp_path,
        "universes:\n  python_sources:\n    - src/**/*.py\n",
    )

    resolved = resolve_universe(
        payload, "python_sources", default=DEFAULT_UNIVERSES["python_sources"]
    )

    assert resolved.patterns == ("src/**/*.py",)
    assert resolved.declared is True
    assert resolved.source == "adapter"


def test_declared_empty_family_refuses_with_gate_label(tmp_path: Path) -> None:
    payload = _adapter(tmp_path, "universes:\n  pytest_targets: []\n")
    resolved = resolve_universe(
        payload, "pytest_targets", default=DEFAULT_UNIVERSES["pytest_targets"]
    )

    refusal = refuse_if_declared_and_empty(resolved, [], "pytest")

    assert resolved.patterns == ()
    assert refusal is not None
    assert "pytest" in refusal
    assert "refusing empty declared universe" in refusal


def test_unknown_universe_subkey_is_refused_by_validator(tmp_path: Path) -> None:
    payload = _adapter(tmp_path, "universes:\n  made_up_family:\n    - src\n")

    assert payload["valid"] is False
    assert "universes.made_up_family is not a recognized universe" in payload["errors"]


def test_universes_wrong_shape_is_refused_by_validator(tmp_path: Path) -> None:
    payload = _adapter(tmp_path, "universes: []\n")

    assert payload["valid"] is False
    assert "universes must be a mapping" in payload["errors"]


def test_artifact_root_family_is_resolved_independently(tmp_path: Path) -> None:
    payload = _adapter(
        tmp_path,
        "universes:\n  artifact_roots:\n    spec: artifacts/spec\n",
    )

    spec = resolve_universe(payload, "artifact_roots.spec", default="charness-artifacts/spec")
    retro = resolve_universe(payload, "artifact_roots.retro", default="charness-artifacts/retro")

    assert spec == Universe(("artifacts/spec",), True, "adapter")
    assert retro == Universe(("charness-artifacts/retro",), False, "default")


def test_git_listing_and_raw_glob_fallback_have_the_same_matches(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    (repo / "src" / "nested").mkdir(parents=True)
    (repo / "src" / "one.py").write_text("", encoding="utf-8")
    (repo / "src" / "nested" / "two.py").write_text("", encoding="utf-8")
    universe = Universe(("src/**/*.py",), True, "adapter")

    def listed_process(*_args, **_kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout="src/one.py\0src/nested/two.py\0",
            stderr="",
        )

    monkeypatch.setattr("scripts.quality_universes_lib.run_process", listed_process)
    from_git = matching_files(repo, universe)

    def unavailable_process(*_args, **_kwargs):
        return SimpleNamespace(returncode=128, stdout="", stderr="not a git repo")

    monkeypatch.setattr("scripts.quality_universes_lib.run_process", unavailable_process)
    from_fallback = matching_files(repo, universe)

    assert from_git == from_fallback
    assert [path.relative_to(repo).as_posix() for path in from_git] == [
        "src/nested/two.py",
        "src/one.py",
    ]


def test_unconfigured_empty_is_reported_not_refused() -> None:
    universe = Universe(("src/**/*.py",), False, "default")

    assert refuse_if_declared_and_empty(universe, [], "ruff") is None
