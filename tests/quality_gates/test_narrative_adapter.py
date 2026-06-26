from __future__ import annotations

import json
import sys
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

from .support import ROOT

RESOLVE_SCRIPT = "skills/public/narrative/scripts/resolve_adapter.py"
_resolve_adapter = import_repo_module(ROOT / RESOLVE_SCRIPT, "skills.public.narrative.scripts.resolve_adapter")


def run_narrative_resolve_adapter(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [RESOLVE_SCRIPT, *args])
    code = _resolve_adapter.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def test_narrative_resolve_adapter_reports_brief_template_for_current_repo(monkeypatch, capsys) -> None:
    result = run_narrative_resolve_adapter(monkeypatch, capsys, "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["data"]["brief_template"] == [
        "One-Line Summary",
        "Current Contract",
        "What Changed",
        "Open Questions",
    ]
    assert payload["data"]["scenario_surfaces"] == []
    assert payload["data"]["scenario_block_template"] == [
        "What You Bring",
        "Input (CLI)",
        "Input (For Agent)",
        "What Happens",
        "What Comes Back",
        "Next Action",
    ]
    assert "docs/control-plane.md" in payload["data"]["source_documents"]
    assert payload["bootstrap_expectations"]["artifact_path"] == "charness-artifacts/narrative/latest.md"
    assert "narrative alignment output" in payload["bootstrap_expectations"]["artifact_meaning"]
