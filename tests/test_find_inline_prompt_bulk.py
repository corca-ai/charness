from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def init_git_repo(repo: Path, *tracked_paths: str) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    if tracked_paths:
        subprocess.run(
            ["git", "add", *tracked_paths],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )


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
    result = subprocess.run(
        [
            "python3",
            "skills/public/quality/references/find_inline_prompt_bulk.py",
            "--repo-root",
            str(repo),
            "--source-glob",
            "src/**/*.py",
            "--min-multiline-chars",
            "400",
            "--json",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
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


def test_find_inline_prompt_bulk_ignores_gitignored_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / ".artifacts").mkdir(parents=True)
    (repo / ".gitignore").write_text(".artifacts/**\n", encoding="utf-8")
    (repo / "src" / "kept.py").write_text(
        'PROMPT = """line one\\n' + ("x" * 450) + '"""\n',
        encoding="utf-8",
    )
    (repo / ".artifacts" / "generated.py").write_text(
        'PROMPT = """line one\\n' + ("x" * 450) + '"""\n',
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "src/kept.py")

    result = subprocess.run(
        [
            "python3",
            "skills/public/quality/references/find_inline_prompt_bulk.py",
            "--repo-root",
            str(repo),
            "--json",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["exemption_globs"] == []
    assert [finding["path"] for finding in payload["findings"]] == ["src/kept.py"]
