"""The irreversible close carrier must prove the target before mutation."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from tests.quality_gates.support import run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
BODY = "closeout body.\n\nAI-provenance: authored by an agent session.\n"


def _run_with_view_fixture(tmp_path: Path, view_body: str, exit_code: int) -> object:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "if 'view' in sys.argv:",
                f"    print({view_body!r})",
                f"    raise SystemExit({exit_code})",
                "print('unexpected mutation')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    body = tmp_path / "body.md"
    body.write_text(BODY, encoding="utf-8")
    return run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "question",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )


def test_issue_close_refuses_failed_preflight_before_mutation(tmp_path: Path) -> None:
    result = _run_with_view_fixture(tmp_path, "preflight unavailable", 7)
    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "pre-mutation issue readback failed" in payload["error"]
    assert "no comment or close was attempted" in payload["error"]


def test_issue_close_refuses_invalid_preflight_json(tmp_path: Path) -> None:
    result = _run_with_view_fixture(tmp_path, "not-json", 0)
    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "pre-mutation issue readback returned invalid JSON" in payload["error"]
