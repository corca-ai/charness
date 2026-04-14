from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .support import ROOT


def test_quality_tool_recommendations_emit_blocking_validation_routes(tmp_path: Path) -> None:
    (tmp_path / "integrations" / "tools").mkdir(parents=True)
    (tmp_path / "integrations" / "tools" / "cautilus.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "cautilus",
                "kind": "external_binary_with_skill",
                "display_name": "cautilus",
                "summary": "Standalone evaluator.",
                "upstream_repo": "corca-ai/cautilus",
                "homepage": "https://github.com/corca-ai/cautilus",
                "lifecycle": {
                    "install": {
                        "mode": "manual",
                        "docs_url": "https://github.com/corca-ai/cautilus",
                        "install_url": "https://github.com/corca-ai/cautilus/blob/main/install.md",
                        "notes": ["Install cautilus."],
                    },
                    "update": {"mode": "manual", "docs_url": "https://github.com/corca-ai/cautilus/releases", "notes": ["Update cautilus."]},
                },
                "checks": {
                    "detect": {"commands": ["cautilus --version"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["cautilus doctor --help"], "success_criteria": ["exit_code:0", "stdout_contains:doctor"]},
                },
                "access_modes": ["binary", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "latest", "detected_by": "stdout"},
                "supports_public_skills": ["spec", "quality"],
                "recommendation_role": "validation",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    import shutil
    import sys

    isolated_path_parts: list[str] = [str(Path(sys.executable).resolve().parent)]
    git_binary = shutil.which("git")
    if git_binary is not None:
        isolated_path_parts.append(str(Path(git_binary).resolve().parent))
    isolated_path = os.pathsep.join(dict.fromkeys(isolated_path_parts))

    result = subprocess.run(
        [
            "python3",
            "skills/public/quality/scripts/list_tool_recommendations.py",
            "--repo-root",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": isolated_path},
    )

    payload = json.loads(result.stdout)
    assert payload == {
        "recommendation_role": "validation",
        "next_skill_id": "quality",
        "tool_recommendations": [
            {
                "tool_id": "cautilus",
                "display_name": "cautilus",
                "kind": "external_binary_with_skill",
                "summary": "Standalone evaluator.",
                "why_recommended": "Recommended because `quality` can use this tool for stronger validation when repo-native deterministic proof is not enough.",
                "supports_public_skills": ["spec", "quality"],
                "recommendation_role": "validation",
                "recommendation_status": "install-needed",
                "doctor_status": "missing",
                "support_state": "integration-only",
                "support_sync_status": "not-tracked",
                "detect_ok": False,
                "healthcheck_ok": False,
                "readiness_ok": True,
                "install": {
                    "mode": "manual",
                    "commands": [],
                    "docs_url": "https://github.com/corca-ai/cautilus",
                    "install_url": "https://github.com/corca-ai/cautilus/blob/main/install.md",
                    "notes": ["Install cautilus."],
                },
                "verify_command": "python3 scripts/doctor.py --repo-root . --json --tool-id cautilus",
                "next_skill_id": "quality",
            }
        ],
    }
