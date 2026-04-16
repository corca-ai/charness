from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_inventory_brittle_source_guards_flags_wrapped_fixed_pattern(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "README.md").write_text(
        "\n".join(
            [
                "# Demo",
                "",
                "The repo keeps behavior honest while prompts keep changing across",
                "several daily workflow edits and release checks.",
                "This prose is still written with ordinary column wrapping that",
                "can split fixed string assertions without changing rendered text.",
                "Another wrapped line keeps the heuristic honest for this target.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "docs" / "specs" / "current-product.spec.md").write_text(
        "\n".join(
            [
                "# Current Product",
                "",
                "| file | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | behavior honest while prompts keep changing across several daily workflow edits |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_brittle_source_guards.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["brittle_count"] == 1
    finding = payload["findings"][0]
    assert finding["status"] == "brittle"
    assert finding["hard_wrapped"] is True
    assert finding["exact_found"] is False
    assert finding["normalized_found"] is True


def test_inventory_brittle_source_guards_reports_policy_without_tool(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Agents\n\nUse semantic line breaks for prose markdown.\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_brittle_source_guards.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["policy"] == {
        "policy_declared": True,
        "enforcement_tools": [],
        "policy_without_tool": True,
    }
