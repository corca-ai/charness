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


def test_run_nose_oserror_degrades_not_crashes(monkeypatch) -> None:
    # An invalid NOSE_BIN (unchecked override) must degrade to advisory, not crash.
    def boom(*_a, **_k):
        raise FileNotFoundError(2, "No such file or directory", "nope-nose")

    monkeypatch.setattr(nr.subprocess, "run", boom)
    result = nr.run_nose(REPO_ROOT, ["nope-nose", "query"])
    assert result["status"] == "error"
    assert result["families"] == []
    assert "could not be executed" in result["stderr"]


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
# nose_report_lib.collect_families — multi-root query merge (the 0.13.3 resolver).
# --------------------------------------------------------------------------- #
def test_collect_families_merges_dedupes_and_stamps_version(monkeypatch) -> None:
    calls = []

    def fake_run(_repo, command):
        calls.append(command)
        fams = [{"id": "a"}, {"id": "b"}] if command[2] == "scripts" else [{"id": "b"}, {"id": "c"}]
        return {"status": "findings", "exit_code": 0, "stdout": "", "stderr": "",
                "families": fams, "tool_version": "", "scope": {},
                "ranking": {"total_families": 2, "shown_families": 2}}

    monkeypatch.setattr(nr, "run_nose", fake_run)
    monkeypatch.setattr(nr, "resolve_tool_version", lambda _bin: "0.13.3")
    result = nr.collect_families(
        REPO_ROOT, "nose", ["scripts", "skills/public"], mode="m", min_size=24, top=10, sort="extractability"
    )
    assert sorted(nr.family_identity(f) for f in result["families"]) == ["a", "b", "c"]  # 'b' deduped
    assert result["status"] == "findings"
    assert result["tool_version"] == "0.13.3"  # query JSON has no version -> stamped
    assert result["ranking"]["total_families"] == 4  # summed per-root
    assert len(calls) == 2 and calls[0][:3] == ["nose", "query", "scripts"]


def test_collect_families_errored_path_degrades_to_error(monkeypatch) -> None:
    def fake_run(_repo, command):
        if command[2] == "scripts":
            return {"status": "error", "exit_code": 1, "stdout": "", "stderr": "boom", "families": [], "tool_version": ""}
        return {"status": "findings", "exit_code": 0, "stdout": "", "stderr": "",
                "families": [{"id": "a"}], "tool_version": "", "scope": {}, "ranking": {}}

    monkeypatch.setattr(nr, "run_nose", fake_run)
    monkeypatch.setattr(nr, "resolve_tool_version", lambda _bin: "0.13.3")
    result = nr.collect_families(
        REPO_ROOT, "nose", ["scripts", "skills/public"], mode="m", min_size=24, top=10, sort="extractability"
    )
    assert result["status"] == "error"  # any errored root degrades the whole scan (never a silent clean pass)
    assert "boom" in result["stderr"]


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


def test_extract_report_query_top_candidates_and_summary_ranking() -> None:
    # The no-`all` query dashboard emits `top_candidates`; ranking is derived from
    # the `summary` block when no explicit `ranking` is present (nose 0.13.x query).
    families, tool_version, scope, ranking = nr.extract_report(
        {"top_candidates": [{"id": "q"}], "summary": {"families": 10, "shown": 1}}
    )
    assert families == [{"id": "q"}]
    assert ranking == {"total_families": 10, "shown_families": 1}


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


def test_family_summary_query_shape_maps_fields() -> None:
    # nose 0.13.3 `query` output: identity `id` (not `family_id`), `shared` (not
    # `shared_lines`), location `start`/`end` (not `start_line`/`end_line`), and no
    # `dup_lines` (derived from member spans). family_summary normalizes them.
    summary = nr.family_summary(
        {
            "id": "qid",
            "shared": 5,
            "members": 2,
            "value": 1.0,
            "locations": [
                {"file": "a.py", "start": 1, "end": 10, "name": "a", "lang": "python"},
                {"file": "b.py", "start": 1, "end": 10, "name": "b", "lang": "python"},
            ],
        }
    )
    assert summary["family_id"] == "qid"
    assert summary["shared_lines"] == 5
    assert summary["dup_lines"] == 20  # two 10-line spans, derived
    assert summary["sample_locations"][0]["start_line"] == 1
    assert summary["sample_locations"][0]["end_line"] == 10


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


def test_load_baseline_ids_reads_code_family_ids(tmp_path: Path) -> None:
    rel = nb.DEFAULT_BASELINE_REL
    target = tmp_path / rel
    target.parent.mkdir(parents=True)
    target.write_text(
        json.dumps({"schemaVersion": nb.BASELINE_SCHEMA_VERSION, "code_family_ids": ["a", "b", 5, ""]}),
        encoding="utf-8",
    )
    assert nb.load_baseline_ids(tmp_path, rel) == {"a", "b"}


def test_load_baseline_ids_none_on_missing_legacy_or_malformed(tmp_path: Path) -> None:
    assert nb.load_baseline_ids(tmp_path, None) is None
    assert nb.load_baseline_ids(tmp_path, "nope.json") is None
    # A pre-migration cluster-key baseline (a bare [{key, members}] list) carries no
    # code_family_ids -> None, so everything reads as drift until re-seeded.
    legacy = tmp_path / "legacy.json"
    legacy.write_text(json.dumps([{"key": "x", "members": []}]), encoding="utf-8")
    assert nb.load_baseline_ids(tmp_path, "legacy.json") is None


def test_write_baseline_payload_writes_id_set(tmp_path: Path) -> None:
    payload = nb.write_baseline_payload(tmp_path, None, ["b", "a", "a", ""], ["scripts"])
    assert payload["status"] == "baseline-written"
    assert payload["advisory"] is True
    assert payload["paths"] == ["scripts"]
    assert payload["code_family_count"] == 2
    assert len(payload["notes"]) == 2
    written = json.loads((tmp_path / nb.DEFAULT_BASELINE_REL).read_text(encoding="utf-8"))
    assert written["code_family_ids"] == ["a", "b"]  # sorted, deduped, empties dropped
    assert written["schemaVersion"] == nb.BASELINE_SCHEMA_VERSION


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
    inv.print_human({"status": "baseline-written", "baseline": "b.json", "code_family_count": 3})
    out = capsys.readouterr().out
    assert "nose baseline written: b.json" in out and "3 code family_ids accepted" in out


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


def test_build_query_command_terms_and_flags() -> None:
    cmd = nr.build_query_command(
        "nose", "scripts", mode="syntax", min_size=24, top=20, sort="value",
        exclude=["a"], ignore_file="ig.json",
    )
    assert cmd[:3] == ["nose", "query", "scripts"]
    # all/top=/sort= are query TERMS (positional), not flags: passing --top/--sort
    # to `query` errors and yields zero families (nose 0.13.3 migration).
    assert "all" in cmd and "top=20" in cmd and "sort=value" in cmd
    assert "--top" not in cmd and "--sort" not in cmd
    assert "--mode" in cmd and "--min-size" in cmd
    assert "--exclude" in cmd and "--ignore-file" in cmd
    assert cmd[-2:] == ["--format", "json"]
    assert "scan" not in cmd and "--write-baseline" not in cmd and "--baseline" not in cmd


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


def _collected(families: list, **overrides) -> dict:
    base = {
        "status": "findings" if families else "clean",
        "exit_code": 0,
        "stdout": "",
        "stderr": "",
        "families": families,
        "tool_version": "0.13.3",
        "scope": {"paths": ["scripts"]},
        "ranking": {"total_families": len(families), "shown_families": len(families)},
    }
    base.update(overrides)
    return base


def test_payload_for_args_findings(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(
        inv.nose_report,
        "collect_families",
        lambda *_a, **_k: _collected(
            [
                {
                    "family_id": "fid",
                    "dup_lines": 12,
                    "locations": [{"file": "a.py", "start_line": 1, "end_line": 9, "name": "n", "kind": "Function"}],
                }
            ]
        ),
    )
    # No nose-baseline.json in tmp_path -> baseline reads None -> all families drift.
    payload = inv.payload_for_args(_args(tmp_path, path=["scripts"], exclude=["x"], ignore_file="ig.json"))
    assert payload["status"] == "findings"
    assert payload["family_count"] == 1
    assert payload["total_dup_lines"] == 12
    assert payload["families"][0]["family_id"] == "fid"
    assert payload["tool_version"] == "0.13.3"
    assert payload["baseline"] is None


def test_payload_for_args_drift_filters_baseline_ids(monkeypatch, tmp_path: Path) -> None:
    rel = inv.nose_baseline.DEFAULT_BASELINE_REL
    target = tmp_path / rel
    target.parent.mkdir(parents=True)
    target.write_text(
        json.dumps({"schemaVersion": inv.nose_baseline.BASELINE_SCHEMA_VERSION, "code_family_ids": ["keep"]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(
        inv.nose_report,
        "collect_families",
        lambda *_a, **_k: _collected([{"family_id": "keep"}, {"family_id": "newfam"}]),
    )
    payload = inv.payload_for_args(_args(tmp_path))
    assert payload["family_count"] == 1  # 'keep' is accepted in the baseline; only 'newfam' is drift
    assert payload["families"][0]["family_id"] == "newfam"
    assert payload["baseline"] == rel


def test_payload_for_args_error_status(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(
        inv.nose_report, "collect_families",
        lambda *_a, **_k: _collected([], status="error", stderr="scripts: boom"),
    )
    payload = inv.payload_for_args(_args(tmp_path))
    assert payload["status"] == "error"
    assert payload["family_count"] == 0
    assert "boom" in payload["stderr"]


def test_payload_for_args_write_baseline(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: "nose")
    seen = {}

    def fake_collect(_repo, _bin, _paths, **kwargs):
        seen.update(kwargs)
        return _collected([{"family_id": "fid2"}, {"family_id": "fid1"}, {"id": ""}])

    monkeypatch.setattr(inv.nose_report, "collect_families", fake_collect)
    payload = inv.payload_for_args(_args(tmp_path, path=["scripts"], top=20, write_baseline=True))
    assert payload["status"] == "baseline-written"
    assert payload["code_family_count"] == 2
    # A baseline write MUST enumerate the full set, never the display --top (which
    # would truncate it and re-flag the rest as drift forever).
    assert seen["top"] == inv.WRITE_BASELINE_TOP and seen["top"] != 20
    written = json.loads((tmp_path / inv.nose_baseline.DEFAULT_BASELINE_REL).read_text(encoding="utf-8"))
    assert written["code_family_ids"] == ["fid1", "fid2"]


def test_main_json_and_human(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(inv, "resolve_nose_bin", lambda: None)
    monkeypatch.setattr(sys, "argv", ["inv", "--repo-root", str(tmp_path), "--json"])
    assert inv.main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "missing"

    monkeypatch.setattr(sys, "argv", ["inv", "--repo-root", str(tmp_path)])
    assert inv.main() == 0
    assert "nose missing" in capsys.readouterr().out
