from __future__ import annotations

from pathlib import Path

from runtime_bootstrap import import_repo_module

from .support import ROOT

_scan = import_repo_module(ROOT / "scripts/core/markdown_doc_scan.py", "scripts.core.markdown_doc_scan")


def _write(tmp_path: Path, *lines: str) -> Path:
    doc = tmp_path / "doc.md"
    doc.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return doc


def test_iter_doc_lines_marks_fenced_lines_and_drops_the_delimiters(tmp_path: Path) -> None:
    doc = _write(tmp_path, "prose", "```bash", "run me", "```", "more prose")

    assert list(_scan.iter_doc_lines(doc)) == [
        (1, "prose", False),
        (3, "run me", True),
        (5, "more prose", False),
    ]


def test_iter_doc_lines_drops_multi_line_html_comments(tmp_path: Path) -> None:
    doc = _write(tmp_path, "before", "<!--", "hidden", "-->", "after")

    assert [line for _, line, _ in _scan.iter_doc_lines(doc)] == ["before", "after"]


def test_iter_doc_lines_drops_a_single_line_html_comment(tmp_path: Path) -> None:
    # The rule the two doc gates disagreed on before they shared this walk: a
    # fully commented line is not live content for either of them.
    doc = _write(tmp_path, "before", "<!-- [cite](./gone.md) -->", "after")

    assert [line for _, line, _ in _scan.iter_doc_lines(doc)] == ["before", "after"]


def test_iter_doc_lines_keeps_a_trailing_comment_on_a_content_line(tmp_path: Path) -> None:
    doc = _write(tmp_path, "- [cite](./x.md) <!-- reproduction-source -->")

    assert [line for _, line, _ in _scan.iter_doc_lines(doc)] == [
        "- [cite](./x.md) <!-- reproduction-source -->"
    ]


def test_iter_doc_lines_does_not_reopen_a_fence_inside_an_html_comment(tmp_path: Path) -> None:
    doc = _write(tmp_path, "<!--", "```", "-->", "prose")

    assert list(_scan.iter_doc_lines(doc)) == [(4, "prose", False)]


def test_iter_doc_lines_keeps_live_content_beside_a_leading_comment(tmp_path: Path) -> None:
    # Dropping the whole line here is fail-open: the citation after the comment
    # renders, so it is live content the caller must still see.
    doc = _write(tmp_path, "<!-- keep --> Evidence: [log](./run.log)")

    assert [line for _, line, _ in _scan.iter_doc_lines(doc)] == [
        "<!-- keep --> Evidence: [log](./run.log)"
    ]


def test_iter_doc_lines_treats_an_unclosed_comment_inside_a_fence_as_literal(tmp_path: Path) -> None:
    # Inside a fence `<!--` is code, not markup. Opening a comment there would
    # swallow the closing delimiter and mark the rest of the document fenced.
    doc = _write(tmp_path, "```html", "<!-- template start", "```", "after the fence")

    assert list(_scan.iter_doc_lines(doc)) == [
        (2, "<!-- template start", True),
        (4, "after the fence", False),
    ]


def test_iter_doc_lines_with_language_reports_the_fence_info_string(tmp_path: Path) -> None:
    # `check_documented_subcommands.py` scans shell fences and skips the rest:
    # `text` fences in this repo carry sample OUTPUT, and reading one as a
    # command line makes the CLI reference argue with itself.
    doc = _write(tmp_path, "prose", "```BASH  ", "run me", "```", "```text", "sample", "```")

    assert list(_scan.iter_doc_lines_with_language(doc)) == [
        (1, "prose", None),
        (3, "run me", "bash"),
        (6, "sample", "text"),
    ]


def test_iter_doc_lines_with_language_reports_an_undeclared_fence_as_empty(tmp_path: Path) -> None:
    # `""` and `None` are different states: "a fence that declared no language"
    # is not "prose", and a caller keying on truthiness would merge them.
    doc = _write(tmp_path, "```", "body", "```")

    assert list(_scan.iter_doc_lines_with_language(doc)) == [(2, "body", "")]
