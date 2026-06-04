from __future__ import annotations

import json
import os
from pathlib import Path

from tests.quality_gates.support import run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def test_non_gh_backend_without_command_templates_is_not_ready(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "ceal"
    fake.write_text("#!/usr/bin/env sh\n[ \"$1\" = --version ] && echo 'ceal 0.0.1'\n", encoding="utf-8")
    fake.chmod(0o755)
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "issue-adapter.yaml").write_text(
        "\n".join([
            "version: 1",
            "default_org: corca-ai",
            "issue_backend:",
            "  id: ceal-github",
            "  binary: ceal",
            "  commands: null",
            "",
        ]),
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "preflight",
        "--json",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["backend_ops_available"] is False
    assert payload["selected_backend"]["id"] == "ceal-github"
    assert payload["selected_backend"]["found"] is True
    assert "no synchronous issue backend command templates" in payload["error"]
