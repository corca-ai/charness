from __future__ import annotations

from pathlib import Path

from scripts import check_artifact_citations as checker


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts").mkdir(parents=True)
    (repo / "scripts").mkdir()
    return repo


def _write(repo: Path, relative: str, text: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _check(repo: Path, *artifacts: str) -> dict[str, object]:
    return checker.check_artifact_citations(repo, artifacts)


def test_valid_code_citation_checks_path_range_and_nearby_identifier(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo, "scripts/sample.py", "def first():\n    return 1\n\ndef second():\n    return 2\n")
    _write(
        repo,
        "charness-artifacts/current.md",
        "The `second` helper is at `scripts/sample.py:4-5`.\n",
    )

    report = _check(repo, "charness-artifacts/current.md")

    assert report["ok"] is True
    assert report["status"] == "checked"
    assert len(report["citations_checked"]) == 1
    assert report["issues"] == []


def test_moved_identifier_is_a_structural_failure_not_a_semantic_judgment(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo, "scripts/sample.py", "# moved\ndef second():\n    return 2\n")
    _write(repo, "charness-artifacts/current.md", "The `second` helper is at `scripts/sample.py:1`.\n")

    report = _check(repo, "charness-artifacts/current.md")

    assert report["ok"] is False
    assert "nearby identifier" in report["issues"][0]["reason"]
    assert report["semantic_scope"] == "syntactic-only"


def test_missing_path_and_out_of_range_line_are_reported(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo, "scripts/sample.py", "def present():\n    pass\n")
    _write(
        repo,
        "charness-artifacts/current.md",
        "- `scripts/missing.py:2`\n- `scripts/sample.py:9`\n",
    )

    report = _check(repo, "charness-artifacts/current.md")

    assert report["ok"] is False
    reasons = [issue["reason"] for issue in report["issues"]]
    assert any("does not exist" in reason for reason in reasons)
    assert any("exceeds target length" in reason for reason in reasons)


def test_non_code_citation_requires_explicit_disposition(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo, "docs/record.md", "## Evidence\nline one\n")
    _write(repo, "charness-artifacts/current.md", "The record is `docs/record.md:2`.\n")

    report = _check(repo, "charness-artifacts/current.md")

    assert report["ok"] is False
    assert "explicit" in report["issues"][0]["reason"]


def test_non_code_and_external_intentional_citations_are_dispositioned(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo, "docs/record.md", "## Evidence\nline one\n")
    _write(
        repo,
        "charness-artifacts/current.md",
        "The record is `docs/record.md:2`. Citation disposition: non-code — prose record.\n"
        "The old source is `old/source.py:8`. Citation disposition: historical — prior tree.\n"
        "The upstream source is `vendor/source.py:3`. Citation disposition: external — upstream.\n",
    )

    report = _check(repo, "charness-artifacts/current.md")

    assert report["ok"] is True
    assert [citation["disposition"] for citation in report["citations_checked"]] == [
        "non-code",
        "historical",
        "external",
    ]


def test_code_fences_prose_numbers_and_urls_are_not_citations(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo, "scripts/sample.py", "def present():\n    pass\n")
    _write(
        repo,
        "charness-artifacts/current.md",
        "Release date 2026-08-20 and ratio 5:30; see https://example.test/a.py:999.\n"
        "```text\nThis example cites `scripts/missing.py:9`.\n```\n",
    )

    report = _check(repo, "charness-artifacts/current.md")

    assert report["ok"] is True
    assert report["citations_checked"] == []


def test_semantically_false_but_current_citation_passes_syntactic_check(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo, "scripts/sample.py", "def present():\n    pass\n")
    _write(
        repo,
        "charness-artifacts/current.md",
        "The system has five consumers (a semantic claim not checked here); `scripts/sample.py:1`.\n",
    )

    report = _check(repo, "charness-artifacts/current.md")

    assert report["ok"] is True
    assert report["semantic_blind_spots"]


def test_only_selected_artifacts_are_scanned_historical_corpus_is_grandfathered(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo, "scripts/sample.py", "def present():\n    pass\n")
    _write(repo, "charness-artifacts/old.md", "`scripts/missing.py:9`\n")
    _write(repo, "charness-artifacts/current.md", "`scripts/sample.py:1`\n")

    report = _check(repo, "charness-artifacts/current.md")

    assert report["ok"] is True
    assert report["artifacts_checked"] == ["charness-artifacts/current.md"]


def test_non_artifact_changed_paths_have_an_explicit_no_scope_status(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = _check(repo, "scripts/sample.py", "docs/readme.md")

    assert report["ok"] is True
    assert report["status"] == "no-scope"
    assert report["artifacts_checked"] == []


def test_main_returns_nonzero_and_emits_structured_findings(tmp_path: Path, capsys) -> None:
    repo = _repo(tmp_path)
    _write(repo, "charness-artifacts/current.md", "`scripts/missing.py:9`\n")

    code = checker.main(["--repo-root", str(repo), "--paths", "charness-artifacts/current.md"])
    output = capsys.readouterr().out

    assert code == 1
    assert "semantic_scope: syntactic-only" in output
    assert "does not exist" in output
