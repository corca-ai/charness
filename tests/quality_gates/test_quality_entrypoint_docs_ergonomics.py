from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_inventory_entrypoint_docs_ergonomics_reports_advisory_flags(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    lines = [
        "# Agents",
        "",
        "Mode choice matters in this mode-heavy workflow.",
        "Another mode note keeps the mode pressure explicit.",
        "This option should probably be inference instead of an option.",
        "A second flag mention keeps flag pressure visible.",
        "",
    ]
    lines.extend(f"Use `{index}` as the inline command detail." for index in range(18))
    lines.extend(
        [
            "",
            "```bash",
            "echo first",
            "```",
            "",
            "```bash",
            "echo second",
            "```",
            "",
        ]
    )
    lines.extend(f"filler line {index}" for index in range(40))
    (repo / "AGENTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_script(
        "skills/public/quality/scripts/inventory_entrypoint_docs_ergonomics.py",
        "--repo-root",
        str(repo),
        "--max-core-lines",
        "20",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    doc = payload["documents"][0]
    assert doc["doc_path"] == "AGENTS.md"
    assert set(doc["heuristics"]) == {
        "long_entrypoint",
        "progressive_disclosure_risk",
        "code_fence_without_deeper_doc_link",
        "mode_pressure_terms_present",
        "option_pressure_terms_present",
        "inline_code_density_without_deeper_doc_link",
    }
    assert doc["review_prompts"]


def test_inventory_entrypoint_docs_ergonomics_flags_agents_runbook_pressure(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "When a recovery path is needed, follow every step here:",
                "",
                "1. Start the local service.",
                "2. Mint the temporary token.",
                "3. Export the environment variable.",
                "4. Run the gated command.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_entrypoint_docs_ergonomics.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    doc = payload["documents"][0]
    assert doc["numbered_procedure_count"] == 4
    assert "host_instruction_runbook_pressure" in doc["heuristics"]
