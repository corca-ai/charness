"""Slice 1: the edit-time issue-anchor scan flags disallowed `#N` anchors in a
skill-package file before the commit-time validate_skill_ergonomics sweep, and
mirrors that sweep's allow-list so legitimate contexts do not false-positive."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts import check_skill_surface_preflight as preflight
from scripts import skill_issue_anchor_scan as anchor_scan

tqlib = anchor_scan._load_text_quality_lib()


def _write(repo: Path, rel: str, text: str) -> Path:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- canonical lib: issue_anchor_findings_for_file (per-file verdict) ---


def test_lib_flags_disallowed_anchor_in_helper_script(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    path = _write(repo, "skills/public/demo/scripts/helper.py", '"""Fix the regression (#340)."""\n')
    findings = tqlib.issue_anchor_findings_for_file(repo.resolve(), path)
    assert len(findings) == 1
    assert findings[0]["heuristic"] == "portable_package_issue_anchor"
    assert findings[0]["line"] == 1
    assert findings[0]["path"] == "skills/public/demo/scripts/helper.py"


def test_lib_skips_allowed_version_field_and_placeholder_url(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    path = _write(
        repo,
        "skills/public/demo/SKILL.md",
        "defaults_version is issue-340 here\n"
        "see https://github.com/owner/.../issues/340 placeholder\n",
    )
    # Both lines match ISSUE_ANCHOR_RE but are allowed contexts the commit sweep
    # also skips, so the edit-time verdict matches: no findings.
    assert tqlib.issue_anchor_findings_for_file(repo.resolve(), path) == []


def test_lib_ignores_non_package_text_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    path = _write(repo, "skills/public/demo/data.bin", "track #340\n")  # .bin is not package text
    assert tqlib.issue_anchor_findings_for_file(repo.resolve(), path) == []


def test_lib_ignores_unreadable_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    directory = repo / "skills" / "public" / "demo" / "looks_like.md"
    directory.mkdir(parents=True)  # a directory named *.md: read_text raises -> no findings
    assert tqlib.issue_anchor_findings_for_file(repo.resolve(), directory) == []


def test_lib_excludes_pycache_for_sweep_parity(tmp_path: Path) -> None:
    # Exact parity with the package sweep's _iter_package_text_files: a real .py
    # under __pycache__ is ignored even though it carries an anchor.
    repo = tmp_path / "repo"
    path = _write(repo, "skills/public/demo/scripts/__pycache__/helper.py", "# track #340\n")
    assert tqlib.issue_anchor_findings_for_file(repo.resolve(), path) == []


def test_lib_no_anchor_lines_yield_no_findings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    path = _write(repo, "skills/public/demo/SKILL.md", "# Demo\nplain prose, no anchors here\n")
    assert tqlib.issue_anchor_findings_for_file(repo.resolve(), path) == []


# --- preflight: scan_issue_anchors + CLI ---


def test_scan_blocks_on_disallowed_anchor(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    rel = "skills/public/demo/scripts/helper.py"
    _write(repo, rel, "x = 1\n# regression fix for #340\n")
    report = anchor_scan.scan_issue_anchors(repo.resolve(), [rel])
    assert report["status"] == "blocked"
    assert report["blocked"] == [rel]
    assert report["findings"][0]["line"] == 2
    assert report["checked"][0] == {"path": rel, "findings": 1}


def test_scan_ok_on_allowed_context(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    rel = "skills/support/demo/SKILL.md"
    _write(repo, rel, "defaults_version is issue-340 for the demo\n")
    report = anchor_scan.scan_issue_anchors(repo.resolve(), [rel])
    assert report["status"] == "ok"
    assert report["blocked"] == []
    assert report["checked"][0]["findings"] == 0


def test_scan_rejects_non_skill_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo, "docs/note.md", "see #340\n")
    with pytest.raises(anchor_scan.IssueAnchorScanError, match="issue-anchor scan target"):
        anchor_scan.scan_issue_anchors(repo.resolve(), ["docs/note.md"])


def test_scan_rejects_path_outside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    with pytest.raises(anchor_scan.IssueAnchorScanError, match="outside repo root"):
        anchor_scan.scan_issue_anchors(repo.resolve(), [str(tmp_path / "elsewhere.py")])


def test_scan_rejects_missing_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "skills" / "public" / "demo").mkdir(parents=True)
    with pytest.raises(anchor_scan.IssueAnchorScanError, match="is missing"):
        anchor_scan.scan_issue_anchors(repo.resolve(), ["skills/public/demo/SKILL.md"])


def test_load_text_quality_lib_missing_raises(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(anchor_scan, "LIB_ROOT", tmp_path)
    with pytest.raises(anchor_scan.IssueAnchorScanError, match="missing skill_text_quality_lib"):
        anchor_scan._load_text_quality_lib()


def test_format_human_covers_ok_and_blocked() -> None:
    ok_report = {"status": "ok", "blocked": [], "findings": [], "checked": [{"path": "a", "findings": 0}]}
    blocked_report = {
        "status": "blocked",
        "blocked": ["a"],
        "findings": [{"path": "a", "line": 2, "excerpt": "x #340"}],
        "checked": [{"path": "a", "findings": 1}],
    }
    assert "skill-issue-anchor-scan: ok" in anchor_scan.format_human(ok_report)
    blocked_text = anchor_scan.format_human(blocked_report)
    assert "BLOCK" in blocked_text
    assert "validate_skill_ergonomics" in blocked_text


def test_scan_cli_blocks_with_exit_one(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    rel = "skills/public/demo/scripts/helper.py"
    _write(repo, rel, "# owner/repo#5 reference\n")
    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_surface_preflight.py", "--repo-root", str(repo), "--scan-issue-anchors", rel],
    )
    assert preflight.main() == 1
    assert "BLOCK" in capsys.readouterr().out


def test_scan_cli_ok_exit_zero_json(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    rel = "skills/public/demo/SKILL.md"
    _write(repo, rel, "# Demo\nclean prose with no anchors\n")
    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_surface_preflight.py", "--repo-root", str(repo), "--scan-issue-anchors", rel, "--json"],
    )
    assert preflight.main() == 0
    assert '"status": "ok"' in capsys.readouterr().out


def test_scan_cli_bad_path_exit_two(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    _write(repo, "docs/note.md", "see #340\n")
    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_surface_preflight.py", "--repo-root", str(repo), "--scan-issue-anchors", "docs/note.md"],
    )
    assert preflight.main() == 2
    assert "issue-anchor scan target" in capsys.readouterr().err
