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


def test_changed_files_lists_added_and_modified_not_deleted(tmp_path: Path) -> None:
    repo = tmp_path / "wt"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "keep.txt").write_text("base\n", encoding="utf-8")
    (repo / "gone.txt").write_text("bye\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    (repo / "keep.txt").write_text("base\nmore\n", encoding="utf-8")  # modified
    (repo / "new.txt").write_text("x\n", encoding="utf-8")  # untracked add
    (repo / "gone.txt").unlink()  # deletion -> excluded
    assert ab._changed_files(repo) == ["keep.txt", "new.txt"]
    assert ab._changed_files(tmp_path / "nope") == []  # non-git dir -> empty, not crash


def test_preserve_outputs_copies_changed_with_size_cap(tmp_path: Path) -> None:
    repo = tmp_path / "wt"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "seed.txt").write_text("s\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    (repo / "sub").mkdir()
    (repo / "sub" / "small.md").write_text("hello\n", encoding="utf-8")
    (repo / "big.bin").write_text("z" * 200, encoding="utf-8")
    out = tmp_path / "preserved" / "outputs"
    manifest = ab.preserve_outputs(repo, out, max_bytes=50)
    assert manifest["copied"] == ["sub/small.md"]  # under cap, dir structure preserved
    assert (out / "sub" / "small.md").read_text(encoding="utf-8") == "hello\n"
    assert manifest["omitted"][0]["path"] == "big.bin" and "size 200" in manifest["omitted"][0]["reason"]
    assert json.loads((out / "outputs-manifest.json").read_text(encoding="utf-8"))["copied"] == ["sub/small.md"]


def test_write_transcript_keeps_assistant_text_only(tmp_path: Path) -> None:
    tree = tmp_path / "tree"
    tree.mkdir()
    events = [
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "chunk 1 assessment"}]}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "secret --token=ABC"}}]}},  # no text -> dropped
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "SECRET_OUTPUT"}]}},  # tool_result -> dropped
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Recommended Disposition: accept"}]}},
        "{ malformed",  # tolerated
    ]
    (tree / "session.jsonl").write_text(
        "".join((e if isinstance(e, str) else json.dumps(e)) + "\n" for e in events), encoding="utf-8")
    dest = tmp_path / "transcript.txt"
    ab._write_transcript(tree, dest)
    text = dest.read_text(encoding="utf-8")
    assert "chunk 1 assessment" in text and "Recommended Disposition: accept" in text
    assert "SECRET_OUTPUT" not in text and "secret --token" not in text  # secret-safe: no tool contents


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


def test_main_requires_a_mode(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        ab.main(["--repo-root", str(tmp_path)])


def test_main_dispatches_selftest(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ab, "selftest", lambda repo_root: 0)
    assert ab.main(["--selftest"]) == 0


def _completed(cmd: object, rc: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(cmd, rc, stdout=stdout, stderr=stderr)


def test_run_one_captures_observes_and_returns_metrics(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out_dir = tmp_path / "work" / "a__0"
    out_dir.mkdir(parents=True)
    tree = tmp_path / "tree"
    tree.mkdir()
    spec = tmp_path / "spec.json"
    spec.write_text("{}", encoding="utf-8")

    def fake_run(cmd, **_kwargs):
        joined = " ".join(cmd)
        if "capture-skill-run.sh" in joined:
            return _completed(cmd, 0, stdout=f"SESSION_TREE={tree}\n")
        # observe step writes the packet to --output
        (out_dir / "observed.v1.json").write_text(
            json.dumps({"evaluations": [{"outcome": "passed", "metrics": {"total_tokens": 100, "tool_count": 5}}]}),
            encoding="utf-8",
        )
        return _completed(cmd, 0)

    monkeypatch.setattr(ab.subprocess, "run", fake_run)
    monkeypatch.setattr(ab, "_git_added_lines", lambda wt: 7)
    metrics = ab.run_one(tmp_path, "HEAD", "do the task", spec, out_dir, 600)
    assert metrics["outcome"] == "passed"
    assert metrics["total_tokens"] == 100
    assert metrics["output_lines"] == 7


def test_run_one_raises_with_stderr_on_capture_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ab.subprocess, "run", lambda cmd, **_k: _completed(cmd, 1, stderr="boom"))
    with pytest.raises(RuntimeError, match="capture failed"):
        ab.run_one(tmp_path, "HEAD", "t", tmp_path / "s.json", tmp_path / "o", 600)


def test_run_one_raises_on_observe_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd, **_k):
        joined = " ".join(cmd)
        if "capture-skill-run.sh" in joined:
            return _completed(cmd, 0, stdout="SESSION_TREE=/x\n")
        return _completed(cmd, 1, stderr="observe boom")

    monkeypatch.setattr(ab.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="observe failed"):
        ab.run_one(tmp_path, "HEAD", "t", tmp_path / "s.json", tmp_path / "o", 600)


def test_run_one_raises_when_no_session_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # capture exits 0 but prints no SESSION_TREE= marker.
    monkeypatch.setattr(ab.subprocess, "run", lambda cmd, **_k: _completed(cmd, 0, stdout="no marker here\n"))
    with pytest.raises(RuntimeError, match="no SESSION_TREE"):
        ab.run_one(tmp_path, "HEAD", "t", tmp_path / "s.json", tmp_path / "o", 600)


def test_run_ab_skips_failed_preserves_and_cleans(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"prompt": "P"}), encoding="utf-8")
    config = {"name": "t", "spec_path": "spec.json", "runs": 2, "arms": [{"name": "a", "ref": "HEAD"}]}
    cleaned: list = []
    monkeypatch.setattr(ab, "_cleanup_run", lambda _repo, out_dir: cleaned.append(out_dir))
    calls = {"i": 0}

    def fake_run_one(_repo_root, _ref, _invocation, _spec_path, out_dir, _timeout):
        index = calls["i"]
        calls["i"] += 1
        if index == 1:
            raise RuntimeError("flaky")  # second run fails -> skipped, not crashed
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "observed.v1.json").write_text("{}", encoding="utf-8")
        (out_dir / "trace-digest.jsonl").write_text("{}\n", encoding="utf-8")
        return {"outcome": "passed", "total_tokens": 100, "tool_count": 4, "output_lines": 1}

    monkeypatch.setattr(ab, "run_one", fake_run_one)
    out = ab.run_ab(tmp_path, config, tmp_path / "res", 600, keep_runs=False)
    assert out["aggregate"]["a"]["n"] == 1  # the flaky run was skipped, not fatal
    assert (tmp_path / "res" / "results.json").is_file()
    assert (tmp_path / "res" / "preserved" / "a__0" / "observed.v1.json").is_file()  # preserve-copy ran
    assert len(cleaned) == 2  # cleanup ran for both runs (success + skipped)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required to run the real metric extractor")
def test_selftest_refuses_when_instruments_untrustworthy(monkeypatch: pytest.MonkeyPatch) -> None:
    # Force the ranking to look broken; selftest must refuse (return 1) — the gate
    # that keeps a live matrix from running on instruments it can't trust.
    monkeypatch.setattr(ab, "ranks_worse", lambda _lean, _waste, _keys: ["total_tokens"])
    assert ab.selftest(ROOT) == 1


def test_cleanup_run_removes_the_out_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out_dir = tmp_path / "o"
    (out_dir / "worktree").mkdir(parents=True)
    monkeypatch.setattr(ab.subprocess, "run", lambda cmd, **_k: _completed(cmd, 0))
    ab._cleanup_run(tmp_path, out_dir)
    assert not out_dir.exists()
