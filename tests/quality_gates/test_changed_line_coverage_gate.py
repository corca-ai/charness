from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module
from tests.quality_gates.git_fixture_support import init_git_repo

from .repo_shapes import install_two_commit_repo
from .support import run_script

SCRIPT = "skills/public/quality/scripts/check_changed_line_coverage.py"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


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
    """Install the shared two-commit checkout used by coverage-gate tests."""
    repo, base, _head = install_two_commit_repo(
        tmp_path / "repo",
        {"pkg/foo.py": "a = 1\nb = 2\nc = 3\n"},
        {"pkg/foo.py": "a = 1\nb = 2\nc = 3\nd = 4\n"},
        first_message="base",
        second_message="add line 4",
    )
    return repo, base


def _write_coverage(repo: Path, *, missing: list[int], executed: list[int]) -> None:
    (repo / "cov.json").write_text(
        json.dumps({"files": {"pkg/foo.py": {"executed_lines": executed, "missing_lines": missing}}}),
        encoding="utf-8",
    )


def _stamp(repo: Path, base: str) -> None:
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--stamp-marker")
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["fingerprint"]


def _run(repo: Path, base: str, *args: str, env: dict[str, str] | None = None):
    return run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, *args, env=env)


def _payload(result):
    return yaml.safe_load(result.stdout)


def _assert_scope_refusals(repo: Path, base: str) -> None:
    empty_base = _run(repo, "")
    assert empty_base.returncode == 0, empty_base.stderr
    assert _payload(empty_base)["ok"] is True

    _write_adapter(repo, [])
    inert = _run(repo, base)
    assert inert.returncode == 0, inert.stderr
    assert _payload(inert)["inert"] is True
    _write_adapter(repo, ["pkg/**/*.py"])

    git_failure = _run(repo, "deadbeef" * 5)
    assert git_failure.returncode == 1, git_failure.stdout + git_failure.stderr
    git_payload = _payload(git_failure)
    assert git_payload["ok"] is False
    assert git_payload["unestablished"] is True
    assert "could not establish the changed set" in git_payload["reason"]
    assert git_payload["verdict"] == "unestablished"
    clean = _run(repo, base)
    assert clean.returncode == 0, clean.stdout + clean.stderr
    clean_payload = _payload(clean)
    assert clean_payload["ok"] is True
    assert clean_payload["verdict"] == "ok"

    missing_head = run_script(
        SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "nosuchref"
    )
    assert missing_head.returncode == 1, missing_head.stdout + missing_head.stderr
    assert _payload(missing_head)["verdict"] == "unestablished"
    assert "Traceback" not in missing_head.stderr, missing_head.stderr


def _assert_coverage_and_tag(repo: Path, base: str) -> None:
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    stale = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD")
    assert stale.returncode == 0, stale.stderr
    stale_payload = _payload(stale)
    assert stale_payload["ok"] is True
    assert "stale" in stale_payload["reason"]

    _stamp(repo, base)
    uncovered = run_script(
        SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD"
    )
    assert uncovered.returncode == 1, uncovered.stderr
    assert _payload(uncovered)["blocking"] == ["pkg/foo.py"]

    _write_coverage(repo, missing=[], executed=[1, 2, 3, 4])
    covered = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD")
    assert covered.returncode == 0, covered.stderr
    covered_payload = _payload(covered)
    assert covered_payload["ok"] is True
    assert covered_payload["blocking"] == []
    assert covered_payload["changed_pool_files"] == ["pkg/foo.py"]

    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    empty_range = run_script(
        SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", base
    )
    assert empty_range.returncode == 0, empty_range.stdout + empty_range.stderr
    empty_payload = _payload(empty_range)
    assert empty_payload["ok"] is True
    assert empty_payload.get("unestablished") is None
    assert empty_payload["reason"] == "no eligible changed files in this range"
    assert "is not the checked-out HEAD" in empty_payload["analyzed_head_not_checked_out_head"]
    assert "ANALYZED head's, not this tree's" in empty_range.stderr, empty_range.stderr
    assert empty_payload["verdict"] == "ok"
    assert empty_payload["analyzed_head"] == base

    _git(repo, "tag", "-a", "v1", "-m", "release")
    tagged = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "v1")
    assert tagged.returncode == 1, tagged.stdout + tagged.stderr
    tagged_payload = _payload(tagged)
    assert tagged_payload.get("unestablished") is None
    assert tagged_payload["blocking"] == ["pkg/foo.py"]
    assert tagged_payload["resolved_head_sha"] == _rev(repo)
    assert tagged_payload["verdict"] == "fail"
    assert tagged_payload["analyzed_head"] == _rev(repo)


def _assert_stale_head_and_invalid_adapter(repo: Path, base: str) -> None:
    stale_head = _rev(repo)
    (repo / "pkg" / "foo.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "add line 5")

    mismatched = run_script(
        SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", stale_head
    )
    assert mismatched.returncode == 3, mismatched.stdout + mismatched.stderr
    mismatched_payload = _payload(mismatched)
    assert mismatched_payload["ok"] is True
    assert mismatched_payload["unestablished"] is True
    assert "is not the checked-out HEAD" in mismatched_payload["reason"]
    assert mismatched_payload["verdict"] == "unestablished"
    assert mismatched_payload["analyzed_head"] == stale_head

    env_stale = _run(repo, base, env={**os.environ, "MUTATION_HEAD_SHA": stale_head})
    assert env_stale.returncode == 3, env_stale.stdout + env_stale.stderr
    env_payload = _payload(env_stale)
    assert env_payload["verdict"] == "unestablished"
    assert env_payload["analyzed_head"] == stale_head

    head = _rev(repo)
    _stamp(repo, base)
    matching = _run(repo, base, env={**os.environ, "MUTATION_HEAD_SHA": head})
    assert matching.returncode == 1, matching.stdout + matching.stderr
    matching_payload = _payload(matching)
    assert matching_payload["verdict"] == "fail"
    assert matching_payload["analyzed_head"] == head

    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nchanged_line_mutation_gate: not-a-mapping\n", encoding="utf-8"
    )
    invalid = _run(repo, base)
    assert invalid.returncode == 1
    invalid_payload = _payload(invalid)
    assert any("changed_line_mutation_gate must be a mapping" in e for e in invalid_payload["adapter_errors"])
    assert invalid_payload["verdict"] == "adapter-invalid"


def test_coverage_gate_shapes_on_one_checkout(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _assert_scope_refusals(repo, base)
    _assert_coverage_and_tag(repo, base)
    _assert_stale_head_and_invalid_adapter(repo, base)


def test_help_explains_repo_root_and_offers_no_json_option() -> None:
    result = run_script(SCRIPT, "--help")
    assert result.returncode == 0, result.stderr
    expected = {
        "--repo-root": "Repository root containing the quality adapter and changed files",
    }
    for option, fragment in expected.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", result.stdout, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", result.stdout[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(result.stdout)
        option_block = re.sub(r"\s+", " ", result.stdout[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"

    assert not re.search(r"^\s*--json\b", result.stdout, re.MULTILINE), result.stdout

    rejected = run_script(SCRIPT, "--json")
    assert rejected.returncode == 2, rejected.stdout + rejected.stderr
    assert "unrecognized arguments: --json" in rejected.stderr, rejected.stderr


def test_verdict_renders_one_word_per_report_shape() -> None:
    module = import_repo_module(__file__, "skills.public.quality.scripts.check_changed_line_coverage")
    verdict = module.verdict
    adapter_invalid = verdict({"adapter_errors": ["bad glob"], "blocking": []})
    assert adapter_invalid["verdict"] == "adapter-invalid"
    assert adapter_invalid["verdict_detail"].startswith("quality adapter invalid:")
    inert = verdict({"adapter_errors": [], "inert": True, "blocking": []})
    assert inert["verdict"] == "inert"
    assert "inert" in inert["verdict_detail"]
    assert verdict({"adapter_errors": [], "unestablished": True, "blocking": [], "reason": "git said no"}) == {
        "verdict": "unestablished",
        "verdict_detail": "git said no",
    }
    failing = verdict({"adapter_errors": [], "blocking": ["a.py", "b.py"]})
    assert failing["verdict"] == "fail"
    assert failing["verdict_detail"].startswith("2 changed file(s)")
    assert verdict({"adapter_errors": [], "blocking": [], "reason": "nothing in range"}) == {
        "verdict": "ok",
        "verdict_detail": "nothing in range",
    }


def test_git_probe_contracts_on_one_checkout(tmp_path: Path) -> None:
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    entry = import_repo_module(__file__, "skills.public.quality.scripts.check_changed_line_coverage")
    repo, base = _seed_repo(tmp_path)
    (repo / "cov.json").write_text('{"files": {}}', encoding="utf-8")
    original = gate._git_lines
    entry_original = entry._gate_lib._git_lines

    def flaky(repo_root, args):
        if args[:2] == ["rev-parse", "--verify"]:
            return ["0" * 40]
        if ".." in args[-1]:
            return ["pkg/mod.py"]
        raise gate.GitUnavailable("git refused the fingerprint probe")

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

    for head_sha in ("HEAD", "deadbeef"):
        def silent(repo_root, args, requested=head_sha):
            if requested != "HEAD" and args[-1] == "HEAD^{commit}":
                return original(repo_root, args)
            return []

        gate._git_lines = silent
        try:
            scope = gate.resolve_head_scope(repo, head_sha)
        finally:
            gate._git_lines = original
        assert scope.resolved is None
        assert scope.mismatch is None
        assert "could not resolve" in scope.error

    def fail_the_worktree_probe(repo_root, args):
        if args[:2] == ["diff", "--name-only"]:
            raise entry._gate_lib.GitUnavailable("git refused the worktree probe")
        return entry_original(repo_root, args)

    entry._gate_lib._git_lines = fail_the_worktree_probe
    try:
        assert entry._false_green_warning(repo, "HEAD", ["pkg/**/*.py"], []) is None
    finally:
        entry._gate_lib._git_lines = entry_original

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


def test_an_unborn_repo_cannot_resolve_head_and_says_so(tmp_path: Path) -> None:
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    repo = tmp_path / "repo"
    repo.mkdir()
    init_git_repo(repo)

    scope = gate.resolve_head_scope(repo, "HEAD")

    assert scope.resolved is None
    assert scope.mismatch is None
    assert "could not resolve `HEAD`" in scope.error


def test_gate_config_is_the_one_reader_for_both_entry_points() -> None:
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    assert gate.gate_config({"eligible_globs": ["a"], "coverage_json": "c.json", "exclude_globs": ["b"]}) == (
        ["a"], "c.json", ["b"]
    )
    assert gate.gate_config({}) == ([], "", [])
