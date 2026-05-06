from __future__ import annotations

import json

from .support import ROOT


def test_exported_markdown_preview_healthcheck_uses_plugin_support_path() -> None:
    source = json.loads(
        (ROOT / "skills" / "support" / "markdown-preview" / "capability.json").read_text(encoding="utf-8")
    )
    exported_path = ROOT / "plugins" / "charness" / "support" / "markdown-preview" / "capability.json"
    if not exported_path.exists():
        return
    exported = json.loads(exported_path.read_text(encoding="utf-8"))

    source_command = source["readiness_checks"][1]["commands"][0]
    exported_command = exported["readiness_checks"][1]["commands"][0]
    assert "skills/support/markdown-preview/scripts/check_glow_backend.py" in source_command
    assert "support/markdown-preview/scripts/check_glow_backend.py" in exported_command
