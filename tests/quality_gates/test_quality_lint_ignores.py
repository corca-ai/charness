from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path

from .support import ROOT

# In-process boundary conversion (testability-dsl-initiative goal 1): load the
# inventory entrypoint by file and drive its `main()` with a captured stdout
# buffer instead of spawning a subprocess. This entrypoint wraps its lib output
# with adapter-derived fields inside main(), so calling main() (not the bare lib
# function) preserves that contract; `--json` mode serializes the same payload.
_SPEC = importlib.util.spec_from_file_location(
    "inventory_lint_ignores",
    ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_lint_ignores.py",
)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def _inventory_json(repo: Path) -> dict:
    buffer = io.StringIO()
    saved_argv = _MODULE.sys.argv
    _MODULE.sys.argv = ["inventory_lint_ignores.py", "--repo-root", str(repo), "--json"]
    try:
        with contextlib.redirect_stdout(buffer):
            assert _MODULE.main() == 0
    finally:
        _MODULE.sys.argv = saved_argv
    return json.loads(buffer.getvalue())


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

    payload = _inventory_json(repo)
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

    payload = _inventory_json(repo)
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

    payload = _inventory_json(repo)
    assert payload["summary"]["ignore_count"] == 0
    assert payload["findings"] == []
