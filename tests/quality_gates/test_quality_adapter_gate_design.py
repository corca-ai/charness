from __future__ import annotations

import json
from pathlib import Path

from .quality_bootstrap_support import _run_adapter_gate_design, seed_quality_repo


def test_quality_inventory_adapter_gate_design_emits_required_classes(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "acknowledged_recommendations:",
                "- demo.ack",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "review_policy.py").write_text(
        "FRESH_EYE_MARKERS = ('critique',)\nrecommendations = [{'enforcement_tier': 'NON_AUTOMATABLE'}]\n",
        encoding="utf-8",
    )

    result = _run_adapter_gate_design("--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert set(payload["finding_classes"]) == {
        "structural_fact",
        "contextual_recommendation",
        "acknowledgement_gap",
        "migration_gap",
        "brittle_hard_gate_smell",
    }
    assert set(payload["enforcement_tiers"]) == {"AUTO_EXISTING", "AUTO_CANDIDATE", "NON_AUTOMATABLE"}
    classes = {finding["finding_class"] for finding in payload["findings"]}
    assert "migration_gap" in classes
    assert "acknowledgement_gap" in classes
    assert "brittle_hard_gate_smell" in classes
    assert "contextual_recommendation" in classes


def test_quality_inventory_adapter_gate_design_uses_configured_review_scope(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    (repo / "custom").mkdir()
    (repo / "custom" / "review_policy.py").write_text(
        "FRESH_EYE_MARKERS = ('critique',)\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "ignored_policy.py").write_text(
        "FRESH_EYE_MARKERS = ('critique',)\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "adapter_review_sources:",
                "- .agents/quality-adapter.yaml",
                "gate_design_review_globs:",
                "- custom/*.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run_adapter_gate_design("--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["review_scope_source"].endswith(".agents/quality-adapter.yaml")
    assert "custom/review_policy.py" in payload["reviewed_paths"]
    assert "scripts/ignored_policy.py" not in payload["reviewed_paths"]
