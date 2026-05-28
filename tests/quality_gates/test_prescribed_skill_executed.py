from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB_PATH = REPO_ROOT / "scripts/check_prescribed_skill_executed_lib.py"
CLI_PATH = REPO_ROOT / "scripts/check_prescribed_skill_executed.py"

_spec = importlib.util.spec_from_file_location("check_prescribed_skill_executed_lib", LIB_PATH)
lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lib)


def _touch(path: Path, body: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_satisfies_with_existing_evidence_files(tmp_path: Path) -> None:
    retro = tmp_path / "charness-artifacts/retro/2026-05-28-x.md"
    probe = tmp_path / "charness-artifacts/probe/2026-05-28-x.json"
    _touch(retro, "retro body")
    _touch(probe, "{}")
    result = lib.check(
        repo_root=tmp_path,
        required=["retro_artifact", "host_log_probe"],
        evidence={
            "retro_artifact": "charness-artifacts/retro/2026-05-28-x.md",
            "host_log_probe": "charness-artifacts/probe/2026-05-28-x.json",
        },
        skips={},
    )
    assert result["ok"] is True
    assert {entry["name"] for entry in result["satisfied"]} == {"retro_artifact", "host_log_probe"}
    assert result["missing"] == []
    assert result["missing_evidence_files"] == []


def test_missing_evidence_file_fails(tmp_path: Path) -> None:
    result = lib.check(
        repo_root=tmp_path,
        required=["retro_artifact"],
        evidence={"retro_artifact": "charness-artifacts/retro/missing.md"},
        skips={},
    )
    assert result["ok"] is False
    assert len(result["missing_evidence_files"]) == 1
    assert result["missing_evidence_files"][0]["name"] == "retro_artifact"


def test_empty_evidence_file_fails(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/empty.md"
    _touch(path, "")
    result = lib.check(
        repo_root=tmp_path,
        required=["retro_artifact"],
        evidence={"retro_artifact": "charness-artifacts/retro/empty.md"},
        skips={},
    )
    assert result["ok"] is False
    assert result["missing_evidence_files"][0]["name"] == "retro_artifact"


def test_missing_name_with_neither_evidence_nor_skip_fails(tmp_path: Path) -> None:
    result = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={},
        skips={},
    )
    assert result["ok"] is False
    assert result["missing"] == ["resolution_critique"]


def test_valid_skip_with_enum_prefix_passes(tmp_path: Path) -> None:
    skip = "host-log-not-exposed: claude session jsonl not under ~/.claude on this hostname"
    result = lib.check(
        repo_root=tmp_path,
        required=["host_log_probe"],
        evidence={},
        skips={"host_log_probe": skip},
    )
    assert result["ok"] is True
    assert result["skipped"][0]["reason"] == skip


def test_skip_without_enum_prefix_fails(tmp_path: Path) -> None:
    result = lib.check(
        repo_root=tmp_path,
        required=["resolution_critique"],
        evidence={},
        skips={"resolution_critique": "host limit prevented review"},
    )
    assert result["ok"] is False
    assert len(result["invalid_skips"]) == 1
    assert "must start with" in result["invalid_skips"][0]["detail"]


def test_skip_too_short_fails(tmp_path: Path) -> None:
    # Right enum prefix but no concrete detail; below the 40-char floor.
    result = lib.check(
        repo_root=tmp_path,
        required=["host_log_probe"],
        evidence={},
        skips={"host_log_probe": "host-log-not-exposed: nope"},
    )
    assert result["ok"] is False
    assert "too short" in result["invalid_skips"][0]["detail"]


def test_parse_evidence_arg_round_trips() -> None:
    assert lib.parse_evidence_arg("retro_artifact:foo/bar.md") == (
        "retro_artifact",
        "foo/bar.md",
    )
    with pytest.raises(ValueError):
        lib.parse_evidence_arg("no-colon")
    with pytest.raises(ValueError):
        lib.parse_evidence_arg("retro_artifact:")


def test_parse_skip_arg_round_trips() -> None:
    assert lib.parse_skip_arg("host_log_probe:host-log-not-exposed: claude code missing") == (
        "host_log_probe",
        "host-log-not-exposed: claude code missing",
    )
    with pytest.raises(ValueError):
        lib.parse_skip_arg("only-name")


def test_cli_smoke_fails_with_exit_one(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "--repo-root",
            str(tmp_path),
            "--require",
            "retro_artifact",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["missing"] == ["retro_artifact"]


def test_cli_smoke_passes_with_real_file(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/x.md"
    _touch(path, "retro body")
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "--repo-root",
            str(tmp_path),
            "--require",
            "retro_artifact",
            "--evidence",
            "retro_artifact:charness-artifacts/retro/x.md",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True


def test_binding_passes_on_basename_token(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/2026-05-28-230-229-closeout.md"
    _touch(path, "body that does not mention the goal")
    binds, reason = lib.evidence_binds_to_context(path, tokens=["230-229"])
    assert binds is True
    assert "basename" in reason


def test_binding_passes_on_content_token(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/2026-05-28-unrelated.md"
    _touch(path, "this retro is about 230-229-self-substitution-pattern")
    binds, reason = lib.evidence_binds_to_context(
        path, tokens=["230-229-self-substitution-pattern"]
    )
    assert binds is True
    assert "content" in reason


def test_binding_fails_on_stale_unrelated_file(tmp_path: Path) -> None:
    # The #233 F1 attack: a present, non-empty, but unrelated pre-existing file.
    path = tmp_path / "charness-artifacts/retro/2026-04-10-some-old.md"
    _touch(path, "an old retro from a different goal entirely")
    binds, reason = lib.evidence_binds_to_context(
        path, tokens=["230-229-self-substitution-pattern", "230-229"]
    )
    assert binds is False
    assert "does not bind" in reason


def test_binding_opts_out_with_no_tokens(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/anything.md"
    _touch(path, "body")
    binds, _ = lib.evidence_binds_to_context(path, tokens=[])
    assert binds is True


def test_binding_numeric_token_does_not_false_match_digit_run(tmp_path: Path) -> None:
    # F-C: `185` must not bind on `21850` / `0185abc` (unanchored substring).
    path = tmp_path / "charness-artifacts/retro/2026-05-28-unrelated.md"
    _touch(path, "this body mentions 21850 and 0185abc but not the issue")
    binds, _ = lib.evidence_binds_to_context(path, tokens=["185"])
    assert binds is False


def test_binding_numeric_token_matches_on_boundary(tmp_path: Path) -> None:
    path = tmp_path / "charness-artifacts/retro/2026-05-28-185-foo.md"
    _touch(path, "body")
    binds, reason = lib.evidence_binds_to_context(path, tokens=["185"])
    assert binds is True
    assert "185" in reason
