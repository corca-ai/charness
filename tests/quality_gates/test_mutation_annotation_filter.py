"""Annotation-union equivalence detection for the Cosmic Ray mutant filter.

Covers `should_skip_mutation` / `annotation_union_operator_positions`: PEP 604
union `|` mutants inside annotations are equivalent under `from __future__
import annotations`, so they are skipped wherever they land, while real `|`
expressions stay killable.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from scripts.filter_cosmic_ray_mutants import (
    _annotation_union_positions,
    _pipe_position,
    annotation_union_operator_positions,
    should_skip_mutation,
)


def _write_module(tmp_path: Path, name: str, source: str) -> Path:
    path = tmp_path / name
    path.write_text(dedent(source), encoding="utf-8")
    return path


class _Mutation:
    def __init__(self, module_path: Path, start_pos: tuple[int, int], operator: str) -> None:
        self.module_path = module_path
        self.start_pos = start_pos
        self.operator_name = operator


def test_annotation_union_positions_cover_multiline_signatures_and_variables(tmp_path: Path) -> None:
    _write_module(
        tmp_path,
        "demo.py",
        """\
        from __future__ import annotations

        total: int | None = None


        def demo(
            *,
            first: str,
            second: str | None = None,
        ) -> dict[str, int] | None:
            local: list[int] | None = first | None  # annotation union, real default expr
            return local
        """,
    )
    positions = annotation_union_operator_positions(tmp_path, Path("demo.py"))
    # line 3 `total: int | None`, line 9 `second: str | None`,
    # line 10 `-> dict[str, int] | None`, line 11 the `list[int] | None` annotation
    # (the real `first | None` default expression on the same line is excluded).
    assert positions == frozenset({(3, 11), (9, 16), (10, 20), (11, 21)})


def test_annotation_union_positions_ignore_real_expressions(tmp_path: Path) -> None:
    _write_module(
        tmp_path,
        "expr.py",
        """\
        from __future__ import annotations

        flags = 1 | 2
        result = flags | 4
        """,
    )
    assert annotation_union_operator_positions(tmp_path, Path("expr.py")) == frozenset()


def test_annotation_union_positions_require_future_annotations(tmp_path: Path) -> None:
    # Without PEP 563 the annotation is evaluated, so the `|` mutant is not
    # provably equivalent and must not be skipped.
    _write_module(
        tmp_path,
        "no_future.py",
        """\
        data: int | None = None


        def fn(value: str | None = None) -> None:
            return None
        """,
    )
    assert annotation_union_operator_positions(tmp_path, Path("no_future.py")) == frozenset()


def test_should_skip_mutation_skips_annotation_union_not_default_expression(tmp_path: Path) -> None:
    _write_module(
        tmp_path,
        "mixed.py",
        """\
        from __future__ import annotations

        A = 1
        B = 2


        def fn(value: int | None = A | B) -> None:
            return value
        """,
    )
    module = Path("mixed.py")
    # The annotation `int | None` pipe is at line 7 col 18; the default `A | B`
    # pipe at col 29 is a real, killable expression that must not be skipped.
    annotation_pipe = _Mutation(module, (7, 18), "core/ReplaceBinaryOperator_BitOr_Add")
    default_expr_pipe = _Mutation(module, (7, 29), "core/ReplaceBinaryOperator_BitOr_Add")
    non_bitor = _Mutation(module, (7, 18), "core/NumberReplacer")

    assert should_skip_mutation(tmp_path, annotation_pipe) is True
    assert should_skip_mutation(tmp_path, default_expr_pipe) is False
    assert should_skip_mutation(tmp_path, non_bitor) is False


def test_annotation_union_positions_cover_vararg_kwarg_and_split_lines(tmp_path: Path) -> None:
    _write_module(
        tmp_path,
        "edges.py",
        """\
        from __future__ import annotations


        def fn(
            *args: int | None,
            **kwargs: str | None,
        ) -> (
            dict[str, int]
            | None
        ):
            return None
        """,
    )
    positions = annotation_union_operator_positions(tmp_path, Path("edges.py"))
    # vararg union (line 5), kwarg union (line 6), and a return annotation whose
    # `|` sits on a continuation line (line 9).
    assert positions == frozenset({(5, 15), (6, 18), (9, 4)})


def test_pipe_position_returns_none_when_no_operator_between_operands() -> None:
    # Defensive branch: a malformed span with no `|` yields None instead of a
    # bogus position.
    assert _pipe_position(["left   right"], (1, 4), (1, 7)) is None


def test_annotation_union_positions_tolerate_unreadable_or_invalid_source(tmp_path: Path) -> None:
    assert annotation_union_operator_positions(tmp_path, Path("missing.py")) == frozenset()
    broken = tmp_path / "broken.py"
    broken.write_text("from __future__ import annotations\ndef oops(\n", encoding="utf-8")
    assert _annotation_union_positions(str(broken)) == frozenset()


def test_annotation_union_positions_known_limitation_annotated_metadata(tmp_path: Path) -> None:
    # Known, deferred limitation: a `|` inside `Annotated[...]` metadata is
    # runtime-observable (typing.get_type_hints(include_extras=True)), so it is
    # NOT a provably equivalent mutant and should not be skipped. The detector
    # currently records it anyway because it walks the whole annotation subtree.
    # The repo has no `Annotated` usage today, so nothing is masked; tighten the
    # detector to exclude Annotated metadata before adopting that pattern.
    _write_module(
        tmp_path,
        "anno.py",
        """\
        from __future__ import annotations

        from typing import Annotated

        FLAG_A = 1
        FLAG_B = 2


        def fn(value: Annotated[int, FLAG_A | FLAG_B]) -> None:
            return value
        """,
    )
    assert annotation_union_operator_positions(tmp_path, Path("anno.py")) == frozenset({(9, 36)})
