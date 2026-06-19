"""In-process coverage for the nose clone-advisory scripts (issue #393).

Same recurring changed-line-coverage class as the scaffold scripts
(#219 -> #251 -> #260 -> #306 -> #335): the scheduled mutation gate's
changed-line signal blocks a changed line that coverage.py never recorded as
executed. The nose clone advisory split into three files
(``inventory_nose_clones.py`` -> ``nose_report_lib.py`` +
``nose_baseline_lib.py``); the two split-out libs are loaded at runtime through
the custom ``load_local_skill_module`` loader and exercised ONLY via
``subprocess.run([... inventory_nose_clones.py ...])`` happy paths in
``tests/quality_gates/test_quality_nose_advisory.py``. Their error/edge
branches (nose timeout, invalid JSON, non-zero exit, the 0.4-array / non-object
report shapes, malformed family locations, the baseline-write timeout, the
``print_human`` non-findings statuses, the bootstrap ImportError guard) stayed
uncovered, so over the split's base range every uncovered executable line reads
as a blocking changed line (#393).

These tests import each module IN-PROCESS (``spec_from_file_location`` +
``exec_module``) so a normal pytest+coverage run attributes the lines, and drive
the previously-uncovered branches directly. They do not weaken any gate; they
raise coverage for a known subprocess-only class, mirroring
``tests/test_scaffold_inprocess_coverage.py``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
QUALITY_SCRIPTS = REPO_ROOT / "skills" / "public" / "quality" / "scripts"


def _load(name: str):
    """Import a quality script by path so coverage attributes its lines."""
    path = QUALITY_SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


nr = _load("nose_report_lib")
nb = _load("nose_baseline_lib")
inv = _load("inventory_nose_clones")


def _completed(stdout: str = "", returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["nose"], returncode=returncode, stdout=stdout, stderr=stderr)


# --------------------------------------------------------------------------- #
# nose_report_lib.run_nose — the error/edge branches the happy path skips.
# --------------------------------------------------------------------------- #
def test_run_nose_timeout(monkeypatch) -> None:
    def boom(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd="nose", timeout=nr.NOSE_TIMEOUT_SECONDS, output="partial")

    monkeypatch.setattr(nr.subprocess, "run", boom)
    result = nr.run_nose(REPO_ROOT, ["nose", "scan"])
    assert result["status"] == "error"
    assert result["exit_code"] == 124
    assert "timed out" in result["stderr"]
    assert result["families"] == []
    assert result["stdout"] == "partial"
    assert result["tool_version"] == ""


def test_run_nose_invalid_json(monkeypatch) -> None:
    monkeypatch.setattr(nr.subprocess, "run", lambda *_a, **_k: _completed(stdout="not json", stderr="warn"))
    result = nr.run_nose(REPO_ROOT, ["nose"])
    assert result["status"] == "error"
    assert "invalid JSON" in result["stderr"]
    assert result["families"] == []


def test_run_nose_empty_stdout_is_clean(monkeypatch) -> None:
    monkeypatch.setattr(nr.subprocess, "run", lambda *_a, **_k: _completed(stdout="   "))
    result = nr.run_nose(REPO_ROOT, ["nose"])
    assert result["status"] == "clean"
    assert result["families"] == []


def test_run_nose_nonzero_returncode_is_error(monkeypatch) -> None:
    payload = json.dumps({"tool_version": "0.13.0", "families": [{"family_id": "abc", "dup_lines": 3, "locations": []}]})
    monkeypatch.setattr(nr.subprocess, "run", lambda *_a, **_k: _completed(stdout=payload, returncode=2, stderr="boom"))
    result = nr.run_nose(REPO_ROOT, ["nose"])
    assert result["status"] == "error"  # non-zero exit overrides "findings"
    assert result["exit_code"] == 2
    assert result["families"][0]["family_id"] == "abc"


def test_run_nose_success_findings(monkeypatch) -> None:
    payload = json.dumps(
        {
            "tool_version": "0.13.0",
            "scope": {"files": 1},
            "ranking": {"total_families": 1, "shown_families": 1},
            "families": [{"family_id": "abc", "dup_lines": 3, "locations": []}],
        }
    )
    monkeypatch.setattr(nr.subprocess, "run", lambda *_a, **_k: _completed(stdout=payload))
    result = nr.run_nose(REPO_ROOT, ["nose"])
    assert result["status"] == "findings"
    assert result["scope"] == {"files": 1}
    assert result["tool_version"] == "0.13.0"


# --------------------------------------------------------------------------- #
# nose_report_lib.extract_report — every report-shape branch.
# --------------------------------------------------------------------------- #
def test_extract_report_v04_array_filters_non_dicts() -> None:
    families, tool_version, scope, ranking = nr.extract_report([{"family_id": "a"}, "not-a-dict"])
    assert families == [{"family_id": "a"}]
    assert (tool_version, scope, ranking) == ("", {}, {})


def test_extract_report_non_dict_non_list_defaults() -> None:
    families, tool_version, scope, ranking = nr.extract_report(42)
    assert families == [] and tool_version == "" and scope == {} and ranking == {}


def test_extract_report_dict_with_wrong_typed_fields() -> None:
    families, tool_version, scope, ranking = nr.extract_report(
        {"families": "x", "tool_version": "0.13.0", "scope": "y", "ranking": "z"}
    )
    assert families == [] and scope == {} and ranking == {}
    assert tool_version == "0.13.0"


# --------------------------------------------------------------------------- #
# nose_report_lib.family_summary — malformed-location guards.
# --------------------------------------------------------------------------- #
def test_family_summary_skips_malformed_locations() -> None:
    fam = {
        "family_id": "fid",
        "dup_lines": 5,
        "locations": [
            123,  # not a dict -> continue
            {"file": None},  # file not a str -> continue
            {"file": "x.py", "start_line": 1, "end_line": 2, "name": "n", "kind": "Function"},
        ],
    }
    summary = nr.family_summary(fam)
    assert summary["family_id"] == "fid"
    assert summary["sample_locations"] == [
        {"file": "x.py", "start_line": 1, "end_line": 2, "name": "n", "kind": "Function"}
    ]


def test_family_summary_non_list_locations() -> None:
    summary = nr.family_summary({"family_id": "fid", "locations": "nope"})
    assert summary["sample_locations"] == []


# --------------------------------------------------------------------------- #
# nose_baseline_lib — resolve_baseline branches + write timeout/error.
# --------------------------------------------------------------------------- #
def test_resolve_baseline_write_mode_defaults() -> None:
    assert nb.resolve_baseline(write_baseline=True, baseline=None, repo_root=REPO_ROOT) == nb.DEFAULT_BASELINE_REL


def test_resolve_baseline_write_mode_explicit() -> None:
    assert nb.resolve_baseline(write_baseline=True, baseline="x.json", repo_root=REPO_ROOT) == "x.json"


def test_resolve_baseline_read_explicit() -> None:
    assert nb.resolve_baseline(write_baseline=False, baseline="x.json", repo_root=REPO_ROOT) == "x.json"


def test_resolve_baseline_read_default_present(tmp_path: Path) -> None:
    target = tmp_path / nb.DEFAULT_BASELINE_REL
    target.parent.mkdir(parents=True)
    target.write_text("[]", encoding="utf-8")
    assert nb.resolve_baseline(write_baseline=False, baseline=None, repo_root=tmp_path) == nb.DEFAULT_BASELINE_REL


def test_resolve_baseline_read_default_absent(tmp_path: Path) -> None:
    assert nb.resolve_baseline(write_baseline=False, baseline=None, repo_root=tmp_path) is None


def test_run_write_baseline_timeout(monkeypatch, tmp_path: Path) -> None:
    def boom(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd="nose", timeout=nb.NOSE_TIMEOUT_SECONDS)

    monkeypatch.setattr(nb.subprocess, "run", boom)
    result = nb.run_write_baseline(tmp_path, ["nose"], "b.json")
    assert result["status"] == "error"
    assert result["exit_code"] == 124
    assert "timed out" in result["stderr"]


def test_run_write_baseline_success_then_error(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(nb.subprocess, "run", lambda *_a, **_k: _completed(stdout="ok"))
    assert nb.run_write_baseline(tmp_path, ["nose"], "b.json")["status"] == "baseline-written"
    monkeypatch.setattr(nb.subprocess, "run", lambda *_a, **_k: _completed(returncode=1, stderr="fail"))
    assert nb.run_write_baseline(tmp_path, ["nose"], "b.json")["status"] == "error"


def test_write_baseline_payload_shape(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(nb.subprocess, "run", lambda *_a, **_k: _completed(stdout="wrote 3"))
    payload = nb.write_baseline_payload(tmp_path, ["nose", "--write-baseline"], None, ["scripts"])
    assert payload["status"] == "baseline-written"
    assert payload["advisory"] is True
    assert payload["paths"] == ["scripts"]
    assert len(payload["notes"]) == 2


# --------------------------------------------------------------------------- #
# inventory_nose_clones — bootstrap guard, print_human statuses, helpers, main.
# --------------------------------------------------------------------------- #
def test_load_skill_runtime_bootstrap_import_error(monkeypatch, tmp_path: Path) -> None:
    isolated = tmp_path / "deep" / "nest" / "x.py"
    isolated.parent.mkdir(parents=True)
    monkeypatch.setattr(inv, "__file__", str(isolated))
    with pytest.raises(ImportError):
        inv._load_skill_runtime_bootstrap()


def test_print_human_status_missing(capsys) -> None:
    inv.print_human({"status": "missing"})
    assert "nose missing" in capsys.readouterr().out


def test_print_human_status_error(capsys) -> None:
    inv.print_human({"status": "error", "stderr": "boom"})
    out = capsys.readouterr().out
    assert "nose inventory error" in out and "boom" in out


def test_print_human_status_baseline_written(capsys) -> None:
    inv.print_human({"status": "baseline-written", "baseline": "b.json", "stdout": "wrote 3"})
    out = capsys.readouterr().out
    assert "nose baseline written: b.json" in out and "wrote 3" in out


def _findings_payload(**overrides) -> dict:
    payload = {
        "status": "findings",
        "tool_version": "0.13.0",
        "family_count": 1,
        "total_dup_lines": 12,
        "ranking": {"total_families": 5, "shown_families": 1},
        "baseline": "charness-artifacts/quality/nose-baseline.json",
        "excludes": ["**/resolve_adapter.py"],
        "ignore_file": "nose.ignore.json",
        "families": [
            {
                "members": 2,
                "dup_lines": 12,
                "shared_lines": 10,
                "params": 1,
                "sample_locations": [{"file": "a.py", "start_line": 1, "end_line": 9}],
            }
        ],
        "interpretation": dict(inv.INTERPRETATION),
    }
    payload.update(overrides)
    return payload


def test_print_human_findings_full(capsys) -> None:
    inv.print_human(_findings_payload())
    out = capsys.readouterr().out
    assert "nose clone advisory (nose 0.13.0)" in out
    assert "RANKING: showing 1 of 5" in out
    assert "BASELINE: active" in out
    assert "SCOPE: filtered scan" in out
    assert "nose family #1" in out
    assert "INTERPRETATION" in out


def test_print_human_findings_minimal(capsys) -> None:
    inv.print_human(
        {
            "status": "findings",
            "tool_version": "",
            "family_count": 0,
            "total_dup_lines": 0,
            "ranking": {},
            "families": [],
        }
    )
    out = capsys.readouterr().out
    assert "nose clone advisory (nose unknown)" in out


def test_portable_path_outside_repo(tmp_path: Path) -> None:
    other = tmp_path / "elsewhere" / "file.py"
    assert inv._portable_path(tmp_path / "repo", other) == str(other)


def test_resolve_nose_bin_env_override(monkeypatch) -> None:
    monkeypatch.setenv("NOSE_BIN", "/custom/nose")
    assert inv.resolve_nose_bin() == "/custom/nose"


def test_resolve_nose_bin_path_lookup(monkeypatch) -> None:
    monkeypatch.delenv("NOSE_BIN", raising=False)
    monkeypatch.setattr(inv.shutil, "which", lambda _name: "/usr/bin/nose")
    assert inv.resolve_nose_bin() == "/usr/bin/nose"


def test_build_command_read_mode() -> None:
    cmd = inv.build_command(
        "nose", ["scripts"], mode="syntax", min_size=24, top=20, sort="value",
        exclude=["a"], ignore_file="ig.json", baseline="b.json", write_baseline=False,
    )
    assert "--format" in cmd and "json" in cmd
    assert "--top" in cmd and "--sort" in cmd
    assert "--exclude" in cmd and "--ignore-file" in cmd and "--baseline" in cmd
    assert "--write-baseline" not in cmd


def test_build_command_write_mode() -> None:
    cmd = inv.build_command("nose", ["scripts"], mode="syntax", min_size=24, top=20, sort="value", write_baseline=True)
    assert "--write-baseline" in cmd
    assert "--top" not in cmd and "--format" not in cmd


def _args(tmp_path: Path, **overrides) -> SimpleNamespace:
    base = dict(
        repo_root=tmp_path, path=[], exclude=[], ignore_file=None, write_baseline=False,
        baseline=None, mode=inv.DEFAULT_MODE, min_size=24, top=20, sort="extractability",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_payload_for_args_missing_nose(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: None)
    payload = inv.payload_for_args(_args(tmp_path))
    assert payload["status"] == "missing"
    assert payload["families"] == []
    assert len(payload["notes"]) == 2


def test_payload_for_args_findings(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(
        inv.nose_report,
        "run_nose",
        lambda _repo_root, _command: {
            "status": "findings",
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "families": [
                {
                    "family_id": "fid",
                    "dup_lines": 12,
                    "locations": [{"file": "a.py", "start_line": 1, "end_line": 9, "name": "n", "kind": "Function"}],
                }
            ],
            "tool_version": "0.13.0",
            "scope": {"files": 1},
            "ranking": {"total_families": 1, "shown_families": 1},
        },
    )
    payload = inv.payload_for_args(_args(tmp_path, path=["scripts"], exclude=["x"], ignore_file="ig.json"))
    assert payload["status"] == "findings"
    assert payload["family_count"] == 1
    assert payload["total_dup_lines"] == 12
    assert payload["families"][0]["family_id"] == "fid"


def test_payload_for_args_write_baseline(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(
        inv.nose_baseline,
        "write_baseline_payload",
        lambda _repo_root, _command, _baseline, _roots: {"status": "baseline-written", "advisory": True},
    )
    payload = inv.payload_for_args(_args(tmp_path, path=["scripts"], write_baseline=True))
    assert payload["status"] == "baseline-written"


def test_main_json_and_human(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: None)
    monkeypatch.setattr(sys, "argv", ["inv", "--repo-root", str(tmp_path), "--json"])
    assert inv.main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "missing"

    monkeypatch.setattr(sys, "argv", ["inv", "--repo-root", str(tmp_path)])
    assert inv.main() == 0
    assert "nose missing" in capsys.readouterr().out
