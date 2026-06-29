from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# run_skill_efficiency_ab.py does `from runtime_bootstrap import ...`, so scripts/
# must be importable when the module is exec'd.
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

ab = load_script_module("run_skill_efficiency_ab_under_test", ROOT / "scripts" / "run_skill_efficiency_ab.py")


def test_aggregate_metrics_basic() -> None:
    runs = [
        {"outcome": "passed", "total_tokens": 100, "tool_count": 4, "output_lines": 10},
        {"outcome": "failed", "total_tokens": 200, "tool_count": 6, "output_lines": 20},
    ]
    agg = ab.aggregate_metrics(runs)
    assert agg["n"] == 2
    assert agg["pass_rate"] == 0.5
    assert agg["total_tokens"]["mean"] == 150.0
    assert agg["total_tokens"]["min"] == 100
    assert agg["total_tokens"]["max"] == 200
    assert agg["total_tokens"]["median"] == 150
    # A metric none of the runs carried aggregates to None, not a crash.
    assert agg["output_tokens"] is None


def test_aggregate_metrics_empty() -> None:
    agg = ab.aggregate_metrics([])
    assert agg["n"] == 0
    assert agg["pass_rate"] is None
    assert agg["total_tokens"] is None


def test_relative_deltas() -> None:
    base = {"total_tokens": {"mean": 100}, "tool_count": {"mean": 0}, "duration_ms": None}
    arm = {"total_tokens": {"mean": 120}, "tool_count": {"mean": 5}, "duration_ms": {"mean": 3}}
    deltas = ab.relative_deltas(base, arm)
    assert deltas["total_tokens"] == 20.0
    assert deltas["tool_count"] is None  # baseline mean 0 -> undefined percent
    assert deltas["duration_ms"] is None  # baseline side missing


def test_ranks_worse_gate() -> None:
    keys = ("total_tokens", "tool_count", "waste_smell_count")
    lean = {"total_tokens": 45, "tool_count": 3, "waste_smell_count": 0}
    wasteful = {"total_tokens": 250, "tool_count": 8, "waste_smell_count": 4}
    assert ab.ranks_worse(lean, wasteful, keys) == []
    # When the wasteful run is NOT strictly worse on a key, that key is reported.
    tie = {"total_tokens": 250, "tool_count": 3, "waste_smell_count": 4}
    assert ab.ranks_worse(lean, tie, keys) == ["tool_count"]


def test_build_report_contents() -> None:
    config = {"name": "demo", "runs": 2}
    agg = {
        "baseline": ab.aggregate_metrics([{"outcome": "passed", "total_tokens": 100, "tool_count": 4}]),
        "treatment": ab.aggregate_metrics([{"outcome": "passed", "total_tokens": 80, "tool_count": 3}]),
    }
    report = ab.build_report(config, agg)
    assert "Efficiency A/B — demo" in report
    assert "baseline" in report and "treatment" in report
    assert "total_tokens" in report
    assert "Deltas vs `baseline`" in report
    assert "-20%" in report  # 80 vs 100 mean
    assert "Honest caveats" in report
    assert "No LLM judge yet" in report


def test_parse_session_tree() -> None:
    assert ab._parse_session_tree("noise\nSESSION_TREE=/a/b/c\ntail") == "/a/b/c"
    assert ab._parse_session_tree("no marker here") is None


def test_metrics_from_packet() -> None:
    packet = {"evaluations": [{"outcome": "passed", "metrics": {"total_tokens": 100, "tool_count": 5}}]}
    metrics = ab._metrics_from_packet(packet)
    assert metrics["outcome"] == "passed"
    assert metrics["total_tokens"] == 100
    assert metrics["tool_count"] == 5
    assert ab._metrics_from_packet({})["outcome"] is None


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def test_git_added_lines_counts_tracked_diff_and_untracked(tmp_path: Path) -> None:
    repo = tmp_path / "wt"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "base.txt").write_text("a\nb\nc\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    # +2 tracked lines, +2 untracked lines
    (repo / "base.txt").write_text("a\nb\nc\nd\ne\n", encoding="utf-8")
    (repo / "new.txt").write_text("x\ny\n", encoding="utf-8")
    assert ab._git_added_lines(repo) == 4
    # A non-git directory yields None, not a crash.
    assert ab._git_added_lines(tmp_path / "nope") is None


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required to run the real metric extractor")
def test_selftest_ranks_wasteful_worse() -> None:
    # The instruments' own gate: extractor must rank the synthetic wasteful tree
    # worse than the lean tree on every SELFTEST_KEYS metric.
    assert ab.selftest(ROOT) == 0


def test_run_refuses_when_selftest_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The load-bearing honesty fix: --run gates on the self-test and never spends
    # (never reaches run_ab) when the instruments are not trustworthy.
    cfg = tmp_path / "c.json"
    cfg.write_text(json.dumps({"name": "x", "spec_path": "s", "runs": 1, "arms": []}), encoding="utf-8")
    spent = {"ran": False}
    monkeypatch.setattr(ab, "selftest", lambda repo_root: 1)
    monkeypatch.setattr(ab, "run_ab", lambda *a, **k: spent.__setitem__("ran", True) or {})
    rc = ab.main(["--run", str(cfg), "--repo-root", str(tmp_path)])
    assert rc == 1
    assert spent["ran"] is False


def test_run_proceeds_when_selftest_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "c.json"
    cfg.write_text(json.dumps({"name": "x", "spec_path": "s", "runs": 1, "arms": []}), encoding="utf-8")
    monkeypatch.setattr(ab, "selftest", lambda repo_root: 0)
    monkeypatch.setattr(ab, "run_ab", lambda *a, **k: {"report": "R", "aggregate": {}, "runs": []})
    rc = ab.main(["--run", str(cfg), "--repo-root", str(tmp_path), "--out-dir", str(tmp_path / "out")])
    assert rc == 0
