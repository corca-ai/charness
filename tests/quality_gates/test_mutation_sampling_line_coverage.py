from __future__ import annotations

import subprocess
import sys
import types
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import scripts.mutation_sampling_lib as mutation_sampling_lib  # noqa: E402
from scripts.mutation_sampling_lib import (  # noqa: E402
    _covered_statement_spans,
    _mutation_line_is_covered,
    build_mutation_line_coverage,
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


def test_covered_statement_spans_tolerates_syntax_error(tmp_path: Path) -> None:
    target = tmp_path / "broken.py"
    target.write_text("def broken(:\n", encoding="utf-8")

    assert _covered_statement_spans(target, {1}) == []


def test_build_mutation_line_coverage_uses_statement_spans(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (script_dir / "demo.py").write_text(
        dedent(
            """\
            def build() -> dict[str, object]:
                record = {
                    "converted": True,
                }
                return record
            """
        ),
        encoding="utf-8",
    )
    config = repo / "cosmic-ray.toml"
    config.write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["scripts/demo.py"]
            test-command = "python3 -m pytest"
            """
        ),
        encoding="utf-8",
    )

    class Mutation:
        module_path = Path("scripts/demo.py")
        start_pos = (3, 0)
        operator_name = "core/ReplaceTrueWithFalse"

    class Item:
        mutations = [Mutation()]

    class Db:
        work_items = [Item()]

    @contextmanager
    def fake_use_db(_path: Path):
        yield Db()

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command[0:2] == ["cosmic-ray", "init"]
        return subprocess.CompletedProcess(command, 0, "", "")

    cosmic_ray = types.ModuleType("cosmic_ray")
    work_db = types.ModuleType("cosmic_ray.work_db")
    work_db.use_db = fake_use_db
    monkeypatch.setitem(sys.modules, "cosmic_ray", cosmic_ray)
    monkeypatch.setitem(sys.modules, "cosmic_ray.work_db", work_db)
    monkeypatch.setattr(mutation_sampling_lib.subprocess, "run", fake_run)

    coverage = build_mutation_line_coverage(
        repo,
        config,
        ["scripts/demo.py"],
        {"scripts/demo.py": {2}},
    )

    assert coverage["scripts/demo.py"] == {"mutable": 1, "covered": 1, "uncovered": 0}
