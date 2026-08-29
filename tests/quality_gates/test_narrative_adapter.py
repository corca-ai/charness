from __future__ import annotations

import sys
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module

from .support import ROOT

RESOLVE_SCRIPT = "skills/public/narrative/scripts/resolve_adapter.py"
_resolve_adapter = import_repo_module(ROOT / RESOLVE_SCRIPT, "skills.public.narrative.scripts.resolve_adapter")


def run_narrative_resolve_adapter(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [RESOLVE_SCRIPT, *args])
    code = _resolve_adapter.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def test_narrative_resolve_adapter_answers_the_live_repo_with_a_well_shaped_payload(
    monkeypatch, capsys
) -> None:
    """A smoke check against this repo's real adapter, not a pin on its wording.

    This used to assert the exact contents of `brief_template`,
    `scenario_block_template`, and `source_documents` as read from the live
    `.agents/narrative-adapter.yaml`. That made an intentional wording edit to
    the repo's own config a test failure with no code-defect signal behind it,
    which is why the #753 JTBD audit classified the file `convert-pin` and named
    this conversion.

    What survives is the part that can actually fail for a code reason: the
    resolver runs against a real adapter, exits clean, and produces every key
    its consumers read. The parsing behaviour underneath is covered against
    synthetic fixtures in
    `test_narrative_scenario_blocks.py::test_narrative_resolve_adapter_preserves_scenario_surface_fields`,
    where a changed expectation means a changed contract rather than changed prose.
    """
    result = run_narrative_resolve_adapter(monkeypatch, capsys, "--repo-root", str(ROOT))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["valid"] is True
    data = payload["data"]
    for key in ("brief_template", "scenario_block_template", "source_documents", "scenario_surfaces"):
        assert key in data, f"resolved adapter payload is missing `{key}`"
    assert data["source_documents"], "source_documents resolved empty for the live repo"
    assert payload["bootstrap_expectations"]["artifact_path"]
