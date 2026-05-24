from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.mutation_sampling_lib import (  # noqa: E402
    _covered_statement_spans,
    _mutation_line_is_covered,
)


def test_mutation_line_coverage_counts_executed_multiline_statement_continuations(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.py"
    target.write_text(
        dedent(
            """\
            def build() -> dict[str, object]:
                record = {
                    "schema_version": 1,
                    "converted": True,
                }
                return record
            """
        ),
        encoding="utf-8",
    )
    spans = _covered_statement_spans(target, {2, 6})

    assert _mutation_line_is_covered(3, set(), spans)
    assert _mutation_line_is_covered(4, set(), spans)
    assert not _mutation_line_is_covered(10, set(), spans)


def test_mutation_line_coverage_does_not_propagate_across_function_body(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.py"
    target.write_text(
        dedent(
            """\
            def build() -> dict[str, object]:
                covered = 1
                if covered:
                    nested = 2
                unrelated = 3
                return {"covered": covered, "unrelated": unrelated}
            """
        ),
        encoding="utf-8",
    )
    spans = _covered_statement_spans(target, {2})

    assert _mutation_line_is_covered(2, {2}, spans)
    assert not _mutation_line_is_covered(4, {2}, spans)
    assert not _mutation_line_is_covered(5, {2}, spans)
