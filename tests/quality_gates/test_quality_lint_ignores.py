from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_inventory_lint_ignores_reports_file_level_and_inline_suppressions(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "web").mkdir(parents=True)
    (repo / "scripts" / "demo.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "# ruff: noqa: E402, I001",
                "import sys  # noqa: F401",
                "VALUE = 1  # noqa",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "web" / "demo.ts").write_text(
        "\n".join(
            [
                "/* eslint-disable no-console */",
                "console.log('demo')",
                "// eslint-disable-next-line no-alert",
                "alert('demo')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_lint_ignores.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"] == {
        "ignore_count": 5,
        "files_with_ignores": 2,
        "blanket_count": 1,
        "file_level_count": 2,
        "inline_count": 3,
        "by_tool": {"eslint": 2, "noqa": 2, "ruff": 1},
    }
    findings = {
        (item["path"], item["tool"], item["scope"], tuple(item["codes"]), item["blanket"])
        for item in payload["findings"]
    }
    assert ("scripts/demo.py", "ruff", "file", ("E402", "I001"), False) in findings
    assert ("scripts/demo.py", "noqa", "inline", ("F401",), False) in findings
    assert ("scripts/demo.py", "noqa", "inline", (), True) in findings
    assert ("web/demo.ts", "eslint", "file", ("no-console",), False) in findings
    assert ("web/demo.ts", "eslint", "inline", ("no-alert",), False) in findings
    assert any("structural seam" in item for item in payload["review_prompts"])


def test_inventory_lint_ignores_skips_vendored_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    own_dir = repo / "scripts"
    vendored_dir = repo / "packages" / "official-skills" / "charness-public" / "scripts"
    own_dir.mkdir(parents=True)
    vendored_dir.mkdir(parents=True)
    (own_dir / "demo.py").write_text("# noqa: F401\nimport sys\n", encoding="utf-8")
    (vendored_dir / "vendored.py").write_text(
        "# ruff: noqa: E402\nimport sys\n", encoding="utf-8"
    )
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "output_dir: charness-artifacts/quality",
                "vendored_paths:",
                "  - packages/official-skills/charness-public",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_lint_ignores.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    paths = {finding["path"] for finding in payload["findings"]}
    assert paths == {"scripts/demo.py"}


def test_inventory_lint_ignores_skips_python_string_literals(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "demo.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                'PATTERN = r"# noqa(?:: (?P<codes>.*))?"',
                'TEXT = "import sys  # noqa: F401"',
                'COMMENT = "/* eslint-disable no-console */"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_lint_ignores.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["ignore_count"] == 0
    assert payload["findings"] == []
