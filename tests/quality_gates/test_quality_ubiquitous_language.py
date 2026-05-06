from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_inventory_ubiquitous_language_is_unconfigured_without_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text("version: 1\n", encoding="utf-8")

    result = run_script(
        "skills/public/quality/scripts/inventory_ubiquitous_language.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "unconfigured"


def test_inventory_ubiquitous_language_flags_deprecated_alias(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / "docs" / "tools.md").write_text("Use charness install <tool> for setup.\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "domain_language_contract:",
                "  surface_globs:",
                "    - docs/**/*.md",
                "  terms:",
                "    - id: external-tool-cli",
                '      canonical: "charness tool"',
                "      deprecated_aliases:",
                '        - "charness install <tool>"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_ubiquitous_language.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert "external-tool-cli: docs/tools.md uses deprecated alias `charness install <tool>`" in payload["findings"][0]


def test_inventory_ubiquitous_language_default_scope_does_not_scan_adapter_declarations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "domain_language_contract:",
                "  terms:",
                "    - id: external-tool-cli",
                '      canonical: "charness tool"',
                "      deprecated_aliases:",
                '        - "charness install <tool>"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_ubiquitous_language.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["terms"][0]["deprecated_alias_total"] == 0


def test_inventory_ubiquitous_language_honors_exemption_globs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "skills" / "public" / "quality" / "references").mkdir(parents=True)
    (repo / "skills" / "public" / "quality" / "references" / "adapter-contract.md").write_text(
        "Example: charness install <tool>\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "domain_language_contract:",
                "  surface_globs:",
                "    - skills/public/**/*.md",
                "  exemption_globs:",
                "    - skills/public/quality/references/adapter-contract.md",
                "  terms:",
                "    - id: external-tool-cli",
                '      canonical: "charness tool"',
                "      deprecated_aliases:",
                '        - "charness install <tool>"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_ubiquitous_language.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["terms"][0]["files_with_terms"] == []


def test_inventory_ubiquitous_language_passes_current_repo_contract() -> None:
    result = run_script(
        "skills/public/quality/scripts/inventory_ubiquitous_language.py",
        "--repo-root",
        str(ROOT),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert [term["id"] for term in payload["terms"]]
