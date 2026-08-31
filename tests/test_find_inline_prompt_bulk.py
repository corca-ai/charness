from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.repo_shapes import install_committed_repo

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "skills/public/quality/references/find_inline_prompt_bulk.py"
SPEC = importlib.util.spec_from_file_location("find_inline_prompt_bulk", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
find_inline_prompt_bulk = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(find_inline_prompt_bulk)


def run_prompt_bulk(*args: str) -> dict[str, object]:
    old_argv = sys.argv[:]
    stdout = io.StringIO()
    try:
        sys.argv = [str(SCRIPT), *args]
        with contextlib.redirect_stdout(stdout):
            assert find_inline_prompt_bulk.main() == 0
    finally:
        sys.argv = old_argv
    # Stdout is unconditionally YAML since the `--json` removal; `render_yaml` is
    # allowed to fall back to JSON syntax when PyYAML is missing, and `safe_load`
    # reads either.
    return yaml.safe_load(stdout.getvalue())


def test_find_inline_prompt_bulk_reports_large_multiline_strings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "prompts.py").write_text(
        'PROMPT = """line one\\n'
        + ("x" * 450)
        + '"""\n'
        'SMALL = """short\\ntext"""\n',
        encoding="utf-8",
    )
    payload = run_prompt_bulk(
        "--repo-root",
        str(repo),
        "--source-glob",
        "src/**/*.py",
        "--min-multiline-chars",
        "400",
    )
    assert payload["source_globs"] == ["src/**/*.py"]
    assert payload["min_multiline_chars"] == 400
    assert payload["findings"] == [
        {
            "path": "src/prompts.py",
            "line": 1,
            "char_count": 459,
            "preview": "line one",
        }
    ]


def test_find_inline_prompt_bulk_ignores_docstrings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "docs.py").write_text(
        '"""module docs\\n' + ("x" * 450) + '"""\n'
        "def helper():\n"
        '    """function docs\\n' + ("y" * 450) + '"""\n'
        '    return """line one\\n' + ("z" * 450) + '"""\n',
        encoding="utf-8",
    )

    payload = run_prompt_bulk(
        "--repo-root",
        str(repo),
        "--source-glob",
        "src/**/*.py",
        "--min-multiline-chars",
        "400",
    )

    assert payload["findings"] == [
        {
            "path": "src/docs.py",
            "line": 4,
            "char_count": 459,
            "preview": "line one",
        }
    ]


def test_find_inline_prompt_bulk_keeps_control_flow_string_expressions(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "control_flow.py").write_text(
        "if True:\n"
        '    """line one\\n' + ("x" * 450) + '"""\n',
        encoding="utf-8",
    )

    payload = run_prompt_bulk(
        "--repo-root",
        str(repo),
        "--source-glob",
        "src/**/*.py",
        "--min-multiline-chars",
        "400",
    )

    assert payload["findings"] == [
        {
            "path": "src/control_flow.py",
            "line": 2,
            "char_count": 459,
            "preview": "line one",
        }
    ]


def test_find_inline_prompt_bulk_ignores_gitignored_files(tmp_path: Path) -> None:
    bulky = 'PROMPT = """line one\\n' + ("x" * 450) + '"""\n'
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": ".artifacts/**\n",
            "src/kept.py": bulky,
        },
    )
    generated = repo / ".artifacts" / "generated.py"
    generated.parent.mkdir(parents=True)
    generated.write_text(bulky, encoding="utf-8")

    payload = run_prompt_bulk(
        "--repo-root",
        str(repo),
    )
    assert payload["exemption_globs"] == []
    assert [finding["path"] for finding in payload["findings"]] == ["src/kept.py"]
    # The retired text path printed `scope_classification=...: <reason>` ahead of the
    # findings for a default scan. That advisory statement now rides in the payload.
    assert payload["scope_classification"] == "advisory_only_no_canonical_prompt_asset_roots"
    assert "advisory-only" in payload["scope_reason"]


def test_find_inline_prompt_bulk_uses_quality_adapter_policy(tmp_path: Path) -> None:
    bulky = 'PROMPT = """line one\\n' + ("x" * 320) + '"""\n'
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".agents/quality-adapter.yaml": "\n".join(
                [
                    "version: 1",
                    "repo: demo",
                    "prompt_asset_policy:",
                    "  source_globs:",
                    "    - src/**/*.py",
                    "  min_multiline_chars: 300",
                    "  exemption_globs:",
                    "    - src/exempt_*.py",
                    "",
                ]
            )
            + "\n",
            "src/kept.py": bulky,
            "src/exempt_prompt.py": bulky,
            "plugins/mirror/ignored.py": bulky,
        },
    )

    payload = run_prompt_bulk(
        "--repo-root",
        str(repo),
        "--from-adapter",
        "--summary",
        "--summary-limit",
        "1",
    )

    assert payload["scope_classification"] == "scanned_from_adapter"
    assert payload["source_globs"] == ["src/**/*.py"]
    assert payload["exemption_globs"] == ["src/exempt_*.py"]
    assert payload["min_multiline_chars"] == 300
    assert payload["adapter"]["found"] is True
    assert payload["adapter"]["valid"] is True
    assert payload["finding_count"] == 1
    assert [finding["path"] for finding in payload["findings_sample"]] == ["src/kept.py"]
    assert "findings" not in payload


def test_find_inline_prompt_bulk_summary_limits_findings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    for index in range(3):
        (repo / "src" / f"prompt_{index}.py").write_text(
            'PROMPT = """line one\\n' + ("x" * 450) + '"""\n',
            encoding="utf-8",
        )

    payload = run_prompt_bulk(
        "--repo-root",
        str(repo),
        "--source-glob",
        "src/**/*.py",
        "--summary",
        "--summary-limit",
        "2",
    )

    assert payload["finding_count"] == 3
    assert len(payload["findings_sample"]) == 2
    assert "findings" not in payload
    # `--summary` selects payload depth, never format: the scope statement both the
    # retired text path and the full payload carried survives at summary depth too.
    assert payload["scope_classification"] == "scanned"
    assert payload["scope_reason"]


def test_find_inline_prompt_bulk_rejects_removed_json_flag(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    old_argv = sys.argv[:]
    stderr = io.StringIO()
    try:
        sys.argv = [str(SCRIPT), "--repo-root", str(repo), "--json"]
        with contextlib.redirect_stderr(stderr), pytest.raises(SystemExit) as excinfo:
            find_inline_prompt_bulk.main()
    finally:
        sys.argv = old_argv

    assert excinfo.value.code == 2
    assert "--json" in stderr.getvalue()
