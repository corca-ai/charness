from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

SCRIPT = "skills/public/quality/scripts/inventory_entrypoint_docs_ergonomics.py"
_inventory_entrypoint_docs = import_repo_module(
    Path(__file__).resolve().parents[2] / SCRIPT,
    "skills.public.quality.scripts.inventory_entrypoint_docs_ergonomics",
)


def run_entrypoint_docs(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["inventory_entrypoint_docs_ergonomics.py", *args])
    returncode = _inventory_entrypoint_docs.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_inventory_entrypoint_docs_ergonomics_reports_advisory_flags(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_entrypoint_docs(
        monkeypatch,
        capsys,
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


def test_inventory_entrypoint_docs_ergonomics_summary_omits_full_doc_rows(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    lines = [
        "# Agents",
        "",
        "Mode choice matters in this mode-heavy workflow.",
        "Another mode note keeps the mode pressure explicit.",
        "This option should probably be inference instead of an option.",
        "A second flag mention keeps flag pressure visible.",
    ]
    lines.extend(f"Use `{index}` as the inline command detail." for index in range(18))
    lines.extend(f"filler line {index}" for index in range(40))
    (repo / "AGENTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_entrypoint_docs(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--max-core-lines",
        "20",
        "--summary",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary_note"].startswith("summary is triage output")
    assert payload["document_count"] == 1
    assert payload["documents_with_heuristics_count"] == 1
    doc = payload["documents_with_heuristics_sample"][0]
    assert doc["doc_path"] == "AGENTS.md"
    assert "review_prompts" not in doc
    assert "inbound_internal_doc_links" not in doc
    assert payload["heuristic_counts"]["long_entrypoint"] == 1
    assert payload["review_prompts"]


def test_inventory_entrypoint_docs_ergonomics_summary_skips_non_dict_rows() -> None:
    payload = _inventory_entrypoint_docs.summarize_payload(
        {
            "repo_root": "/tmp/repo",
            "max_core_lines": 20,
            "documents": [
                "not-a-document-row",
                {
                    "doc_path": "AGENTS.md",
                    "core_nonempty_lines": 30,
                    "internal_doc_link_count": 0,
                    "inbound_internal_doc_link_count": 0,
                    "inline_code_count": 0,
                    "code_fence_count": 0,
                    "numbered_procedure_count": 0,
                    "heuristics": ["long_entrypoint"],
                },
            ],
        }
    )

    assert payload["document_count"] == 2
    assert payload["documents_with_heuristics_count"] == 1
    assert payload["documents_with_heuristics_sample"][0]["doc_path"] == "AGENTS.md"


def test_inventory_entrypoint_docs_ergonomics_flags_agents_runbook_pressure(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_entrypoint_docs(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    doc = payload["documents"][0]
    assert doc["numbered_procedure_count"] == 4
    assert "host_instruction_runbook_pressure" in doc["heuristics"]


def test_inventory_entrypoint_docs_ergonomics_reports_inbound_and_audience_signals(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (repo / "README.md").write_text(
        "# Project\n\nSee [guide](./docs/guide.md).\n",
        encoding="utf-8",
    )
    (docs / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (docs / "token-efficiency.md").write_text("# Token Efficiency\n", encoding="utf-8")

    result = run_entrypoint_docs(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    docs_by_path = {item["doc_path"]: item for item in payload["documents"]}
    assert docs_by_path["docs/guide.md"]["inbound_internal_doc_links"] == ["README.md"]
    assert "top_level_doc_audience_folder_review" in docs_by_path["docs/guide.md"]["heuristics"]
    orphan = docs_by_path["docs/token-efficiency.md"]
    assert orphan["inbound_internal_doc_link_count"] == 0
    assert "top_level_doc_without_inbound_link" in orphan["heuristics"]
