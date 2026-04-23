from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def seed_repo(tmp_path: Path, *artifacts: tuple[str, str]) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/debug",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for filename, body in artifacts:
        (debug_dir / filename).write_text(body, encoding="utf-8")
    return repo


def debug_artifact(
    *,
    interrupt_id: str = "host-seam",
    risk_class: str = "external-seam",
    seam: str = "host-api",
    generalization_pressure: str = "factor-now",
) -> str:
    return (
        "\n".join(
            [
                "# Debug Review",
                "Date: 2026-04-22",
                "",
                "## Problem",
                "",
                "problem",
                "",
                "## Correct Behavior",
                "",
                "correct",
                "",
                "## Observed Facts",
                "",
                "- fact",
                "",
                "## Reproduction",
                "",
                "repro",
                "",
                "## Candidate Causes",
                "",
                "- one",
                "- two",
                "- three",
                "",
                "## Hypothesis",
                "",
                "hypothesis",
                "",
                "## Verification",
                "",
                "verification",
                "",
                "## Root Cause",
                "",
                "root cause",
                "",
                "## Seam Risk",
                "",
                f"- Interrupt ID: {interrupt_id}",
                f"- Risk Class: {risk_class}",
                f"- Seam: {seam}",
                "- Disproving Observation: host behavior disproves local reasoning",
                "- What Local Reasoning Cannot Prove: live host semantics",
                f"- Generalization Pressure: {generalization_pressure}",
                "",
                "## Interrupt Decision",
                "",
                "- Premortem Required: yes",
                "- Next Step: spec",
                "- Handoff Artifact: charness-artifacts/spec/host-seam.md",
                "",
                "## Prevention",
                "",
                "prevention",
                "",
            ]
        )
        + "\n"
    )


def legacy_debug_artifact() -> str:
    return (
        "\n".join(
            [
                "# Legacy Debug Review",
                "Date: 2026-04-10",
                "",
                "## Problem",
                "",
                "legacy",
                "",
            ]
        )
        + "\n"
    )


def test_build_debug_seam_risk_index_writes_source_linked_entries(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        ("2026-04-22-host-seam.md", debug_artifact()),
        ("2026-04-10-legacy.md", legacy_debug_artifact()),
    )
    result = run_script("scripts/build_debug_seam_risk_index.py", "--repo-root", str(repo), "--write", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["index_path"] == "charness-artifacts/debug/seam-risk-index.json"

    index = json.loads((repo / payload["index_path"]).read_text(encoding="utf-8"))
    assert index["score_policy"].startswith("none:")
    assert index["source_artifact_count"] == 2
    assert index["indexed_artifact_count"] == 1
    assert index["risk_class_counts"] == {"external-seam": 1}
    assert index["generalization_pressure_counts"] == {"factor-now": 1}
    assert index["entries"][0]["artifact_path"] == "charness-artifacts/debug/2026-04-22-host-seam.md"
    assert index["entries"][0]["forced"] is True
    assert index["skipped_artifacts"] == [
        {
            "artifact_path": "charness-artifacts/debug/2026-04-10-legacy.md",
            "reason": "debug artifact has no risk interrupt sections yet",
        }
    ]


def test_build_debug_seam_risk_index_check_rejects_stale_index(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, ("2026-04-22-host-seam.md", debug_artifact()))
    stale = repo / "charness-artifacts" / "debug" / "seam-risk-index.json"
    stale.write_text("{}\n", encoding="utf-8")
    result = run_script("scripts/build_debug_seam_risk_index.py", "--repo-root", str(repo), "--check")
    assert result.returncode == 1
    assert "debug seam-risk index" in result.stderr
    assert "--write" in result.stderr
