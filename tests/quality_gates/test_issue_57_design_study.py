from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def _write_inventory(repo: Path) -> None:
    inventory_path = repo / "charness-artifacts" / "find-skills" / "latest.json"
    inventory_path.parent.mkdir(parents=True)
    inventory_path.write_text(
        json.dumps(
            {
                "inventory": {
                    "public_skills": [
                        {
                            "id": "gather",
                            "layer": "public skill",
                            "source": "local-public",
                            "summary": "Gather external context.",
                        }
                    ],
                    "support_skills": [
                        {
                            "id": "cautilus",
                            "layer": "synced support skill",
                            "source": "synced-support",
                            "kind": "external_binary_with_skill",
                            "access_modes": ["binary", "degraded"],
                            "supports_public_skills": ["impl", "quality"],
                            "recommendation_role": "validation",
                            "summary": "Behavior review helper.",
                        }
                    ],
                    "support_capabilities": [
                        {
                            "id": "web-fetch",
                            "layer": "support capability",
                            "source": "local-support-capability",
                            "kind": "support_runtime",
                            "access_modes": ["public", "degraded"],
                            "supports_public_skills": ["gather"],
                        }
                    ],
                    "integrations": [
                        {
                            "id": "gws-cli",
                            "layer": "external integration",
                            "source": "local-integration",
                            "kind": "external_binary",
                            "access_modes": ["binary", "env", "degraded"],
                            "supports_public_skills": ["gather"],
                            "recommendation_role": "runtime",
                        }
                    ],
                }
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_issue_57_renderer_writes_capability_spectrum_markdown(tmp_path: Path) -> None:
    _write_inventory(tmp_path)

    result = run_script(
        "scripts/render_issue_57_design_study.py",
        "--repo-root",
        str(tmp_path),
        "--write",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["output_path"] == "charness-artifacts/design-studies/issue-57/capability-spectrum.md"
    assert payload["totals"]["items"] == 4
    assert payload["totals"]["boundaries"] == {
        "runtime/external": 1,
        "runtime/native": 1,
        "tool/synced-external": 1,
        "workflow/native": 1,
    }

    artifact = tmp_path / payload["output_path"]
    rendered = artifact.read_text(encoding="utf-8")
    assert rendered.startswith("# Issue 57 Capability Spectrum\nDate: ")
    assert "Source: `charness-artifacts/find-skills/latest.json`." in rendered
    assert "| gather | workflow/native | public skill | local-public | - | - | - |" in rendered
    assert "| web-fetch | runtime/native | support capability | local-support-capability | public, degraded | gather | - |" in rendered
    assert "| cautilus | tool/synced-external | synced support skill | synced-support | binary, degraded | impl, quality | validation |" in rendered
    assert "| gws-cli | runtime/external | external integration | local-integration | binary, env, degraded | gather | runtime |" in rendered
    assert "live doctor payload ingestion" in rendered


def test_issue_57_renderer_prints_markdown_without_writing_by_default(tmp_path: Path) -> None:
    _write_inventory(tmp_path)

    result = run_script(
        "scripts/render_issue_57_design_study.py",
        "--repo-root",
        str(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    assert "# Issue 57 Capability Spectrum" in result.stdout
    assert not (tmp_path / "charness-artifacts" / "design-studies").exists()
