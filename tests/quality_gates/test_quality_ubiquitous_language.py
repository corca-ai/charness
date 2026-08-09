from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

from .support import ROOT, run_script

SCRIPT = "skills/public/quality/scripts/inventory_ubiquitous_language.py"
_inventory_ubiquitous_language = import_repo_module(
    ROOT / SCRIPT,
    "skills.public.quality.scripts.inventory_ubiquitous_language",
)


def run_ubiquitous_language(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["inventory_ubiquitous_language.py", *args])
    returncode = _inventory_ubiquitous_language.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


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


def test_inventory_ubiquitous_language_treats_a_non_mapping_adapter_as_unconfigured(
    tmp_path: Path,
) -> None:
    """A YAML file that parses to a list declares no `version` and no contract, so it is
    absent-shaped. Sending it through the version refusal would fail a repo for a file
    that asserts nothing."""
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text("- not\n- a mapping\n", encoding="utf-8")

    result = run_script(
        "skills/public/quality/scripts/inventory_ubiquitous_language.py",
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "unconfigured"


def test_inventory_ubiquitous_language_refuses_an_adapter_version_it_does_not_speak(
    tmp_path: Path,
) -> None:
    """The contract selects this inventory's scan scope AND its exemptions, so reading it
    from an unreconciled schema version lets a declaration this reader never validated
    decide what gets looked at. `unconfigured` would be the wrong refusal: it renders the
    same as a repo that simply declared nothing.
    """
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / "docs" / "tools.md").write_text("Use charness install <tool> for setup.\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 7",
                "domain_language_contract:",
                "  surface_globs:",
                "    - attacker/**/*.md",
                "  terms: []",
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

    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "version must be 1" in combined
    assert "domain_language_contract was not read" in combined
    assert "attacker" not in combined


def test_inventory_ubiquitous_language_flags_deprecated_alias(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_ubiquitous_language(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert "external-tool-cli: docs/tools.md uses deprecated alias `charness install <tool>`" in payload["findings"][0]


def test_inventory_ubiquitous_language_summary_omits_full_per_file_counts(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / "docs" / "tools.md").write_text(
        "Use charness tool for setup. Do not write charness install <tool>.\n",
        encoding="utf-8",
    )
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

    result = run_ubiquitous_language(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--summary",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["summary_note"].startswith("summary is triage output")
    assert payload["finding_count"] == 1
    assert payload["terms"][0]["canonical_total"] == 1
    assert payload["terms"][0]["deprecated_alias_total"] == 1
    assert payload["terms"][0]["files_with_terms_count"] == 1
    assert "files_with_terms" not in payload["terms"][0]
    assert payload["terms"][0]["deprecated_hits_sample"] == [
        {"path": "docs/tools.md", "alias": "charness install <tool>", "count": 1}
    ]


def test_inventory_ubiquitous_language_default_scope_does_not_scan_adapter_declarations(
    tmp_path: Path, monkeypatch, capsys
) -> None:
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

    result = run_ubiquitous_language(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["terms"][0]["deprecated_alias_total"] == 0


def test_inventory_ubiquitous_language_honors_exemption_globs(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_ubiquitous_language(
        monkeypatch,
        capsys,
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
