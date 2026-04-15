from __future__ import annotations

import json

from .support import ROOT, run_script


def test_narrative_resolve_adapter_reports_brief_template_for_current_repo() -> None:
    result = run_script("skills/public/narrative/scripts/resolve_adapter.py", "--repo-root", str(ROOT))
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
    assert payload["bootstrap_expectations"]["artifact_path"] == "charness-artifacts/narrative/narrative.md"
    assert "narrative alignment output" in payload["bootstrap_expectations"]["artifact_meaning"]
