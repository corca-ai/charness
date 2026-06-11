from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.quality_gates.support import ROOT, run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
sys.path.insert(0, str(ROOT / "skills" / "public" / "issue" / "scripts"))
import issue_read  # noqa: E402


def test_issue_read_fails_when_backend_omits_comments(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "print(json.dumps({'number': 42, 'title': 'Demo', 'body': 'Body', 'state': 'OPEN'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)

    result = run_script(
        SCRIPT,
        "read",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "comments list" in payload["error"]


def test_issue_read_reports_backend_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        issue_read,
        "_run_backend",
        lambda _argv: subprocess.CompletedProcess(["gh"], 2, "", "boom"),
    )

    with pytest.raises(RuntimeError, match="issue read failed"):
        issue_read.read_issue_with_comments("corca-ai/charness", 42)


def test_issue_read_reports_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        issue_read,
        "_run_backend",
        lambda _argv: subprocess.CompletedProcess(["gh"], 0, "{", ""),
    )

    with pytest.raises(RuntimeError, match="invalid JSON"):
        issue_read.read_issue_with_comments("corca-ai/charness", 42)


def test_issue_read_load_local_missing_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(issue_read.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None)

    with pytest.raises(ImportError, match="Unable to load"):
        issue_read._load_local("missing")


def test_issue_read_command_stops_on_invalid_adapter(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "issue-adapter.yaml").write_text("version: 1\nissue_backend: broken\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "read",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
