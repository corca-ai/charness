from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


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
