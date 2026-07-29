from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

from .support import run_script

SCRIPT = "skills/public/quality/scripts/check_changed_line_coverage.py"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _rev(repo: Path, ref: str = "HEAD") -> str:
    return subprocess.run(
        ["git", "rev-parse", ref], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _write_adapter(repo: Path, eligible_globs: list[str]) -> None:
    lines = [
        "version: 1",
        "repo: testrepo",
        "output_dir: charness-artifacts/quality",
        "changed_line_mutation_gate:",
        "  coverage_json: cov.json",
    ]
    if eligible_globs:
        lines.append("  eligible_globs:")
        lines += [f"    - {g}" for g in eligible_globs]
    else:
        lines.append("  eligible_globs: []")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_repo(tmp_path: Path) -> tuple[Path, str]:
    """A git repo whose pkg/foo.py gains line 4 in a second commit. Returns (repo, base_sha)."""
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    _git(repo, "init")
    (repo / "pkg" / "foo.py").write_text("a = 1\nb = 2\nc = 3\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "base")
    base = _rev(repo)
    (repo / "pkg" / "foo.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "add line 4")
    return repo, base


def _write_coverage(repo: Path, *, missing: list[int], executed: list[int]) -> None:
    (repo / "cov.json").write_text(
        json.dumps({"files": {"pkg/foo.py": {"executed_lines": executed, "missing_lines": missing}}}),
        encoding="utf-8",
    )


def _stamp(repo: Path, base: str) -> None:
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--stamp-marker", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["fingerprint"]


def test_flags_uncovered_changed_line(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    _stamp(repo, base)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD", "--json")
    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    assert payload["blocking"] == ["pkg/foo.py"]


def test_passes_when_changed_line_covered(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[], executed=[1, 2, 3, 4])
    _stamp(repo, base)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert payload["changed_pool_files"] == ["pkg/foo.py"]


def test_inert_when_no_eligible_globs(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, [])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["inert"] is True


def test_stale_coverage_skips_non_blocking(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    # No marker stamped => coverage is treated as stale => non-blocking skip.
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "stale" in payload["reason"]


def test_no_base_sha_is_non_blocking(tmp_path: Path) -> None:
    repo, _ = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", "", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["ok"] is True


def test_invalid_adapter_fails_closed(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nchanged_line_mutation_gate: not-a-mapping\n", encoding="utf-8"
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert any("changed_line_mutation_gate must be a mapping" in e for e in payload["adapter_errors"])


def test_help_explains_repo_root_and_json_options() -> None:
    result = run_script(SCRIPT, "--help")
    assert result.returncode == 0, result.stderr
    expected = {
        "--repo-root": "Repository root containing the quality adapter and changed files",
        "--json": "Emit the full gate report as JSON",
    }
    for option, fragment in expected.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", result.stdout, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", result.stdout[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(result.stdout)
        option_block = re.sub(r"\s+", " ", result.stdout[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_a_git_failure_is_unestablished_not_an_empty_change_set(tmp_path: Path) -> None:
    """S25, parent-reproduced: an unresolvable base_sha passed as `ok: true`.

    `_git_lines` collapsed a nonzero git exit to `[]`, so the gate reported "no
    eligible changed files in this range" and never invoked the blocking
    classifier at all. Recorded in the 2026-07-28 triage sweep as high severity;
    reproduced by the parent before this fix, which upgrades it from
    SUBAGENT-CONFIRMED to parent-reproduced.
    """
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])

    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", "deadbeef" * 5, "--json")

    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["unestablished"] is True
    assert "could not establish the changed set" in payload["reason"]

    # And the same run must not narrate itself as a pass in human output. With
    # `blocking` empty, the report fell through to the `OK:` line while exiting 1.
    human = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", "deadbeef" * 5)
    assert human.returncode == 1
    assert human.stdout.startswith("UNESTABLISHED:"), human.stdout
    assert "OK:" not in human.stdout

    # A resolvable base over the same tree still passes, so the new arm is not
    # simply refusing everything.
    clean = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--json")
    assert clean.returncode == 0, clean.stdout + clean.stderr
    assert json.loads(clean.stdout)["ok"] is True


def test_human_line_renders_one_word_per_report_shape() -> None:
    """The verdict WORD, tested directly.

    `unestablished` reports carry an empty `blocking` list, so before this
    renderer existed they fell through to the `OK:` line while the process
    exited 1. Each arm is asserted here because the shape that produced the
    wrong word was a fall-through, not a wrong branch.
    """
    module = import_repo_module(__file__, "skills.public.quality.scripts.check_changed_line_coverage")
    line = module.human_line
    assert line({"adapter_errors": ["bad glob"], "blocking": []}).startswith("quality adapter invalid:")
    assert "inert" in line({"adapter_errors": [], "inert": True, "blocking": []})
    assert line({"adapter_errors": [], "unestablished": True, "blocking": [], "reason": "git said no"}) == (
        "UNESTABLISHED: git said no"
    )
    assert line({"adapter_errors": [], "blocking": ["a.py", "b.py"]}).startswith("FAIL: 2 changed file(s)")
    assert line({"adapter_errors": [], "blocking": [], "reason": "nothing in range"}) == "OK: nothing in range"


def test_a_git_failure_while_fingerprinting_is_also_unestablished(tmp_path: Path) -> None:
    """The freshness fingerprint reads git too, and had the same collapse.

    Separate call site from the changed-set probe, so it needs its own arm: a
    stale-marker verdict computed from a file set git would not report is a
    freshness claim over a scope that was never read.
    """
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    repo, base = _seed_repo(tmp_path)
    (repo / "cov.json").write_text('{"files": {}}', encoding="utf-8")

    calls = {"n": 0}

    def flaky(repo_root, args):
        calls["n"] += 1
        if calls["n"] == 1:  # the changed-set probe succeeds
            return ["pkg/mod.py"]
        raise gate.GitUnavailable("git refused the fingerprint probe")

    original = gate._git_lines
    gate._git_lines = flaky
    try:
        report = gate.run_gate(
            repo,
            {"eligible_globs": ["pkg/**/*.py"], "coverage_json": "cov.json"},
            base_sha=base,
            head_sha="HEAD",
            classify=lambda **k: {"blocking": []},
            load_statement_lines=lambda *a, **k: {},
            marker_path=lambda path: path.with_suffix(".fp"),
        )
    finally:
        gate._git_lines = original

    assert report["ok"] is False
    assert report["unestablished"] is True
    assert "coverage-freshness fingerprint" in report["reason"]


def test_stamp_marker_refuses_to_certify_a_file_set_it_could_not_read(tmp_path: Path) -> None:
    """Deliberately uncaught: a marker is a freshness CLAIM the consumer trusts."""
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    repo, base = _seed_repo(tmp_path)
    original = gate._git_lines

    def refuse(repo_root, args):
        raise gate.GitUnavailable("git refused")

    gate._git_lines = refuse
    try:
        with pytest.raises(gate.GitUnavailable):
            gate.stamp_marker(
                repo, {"eligible_globs": ["pkg/**/*.py"], "coverage_json": "cov.json"}, base,
                marker_path=lambda path: path.with_suffix(".fp"),
            )
    finally:
        gate._git_lines = original


def test_gate_config_is_the_one_reader_for_both_entry_points() -> None:
    """The producer that stamps the marker and the consumer that checks it must
    be scoped to the same file set, so they read the adapter block through one
    function rather than each unpacking it."""
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    assert gate.gate_config({"eligible_globs": ["a"], "coverage_json": "c.json", "exclude_globs": ["b"]}) == (
        ["a"], "c.json", ["b"]
    )
    assert gate.gate_config({}) == ([], "", [])

