from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from .support import ROOT


def _write_manifest(tmp_path: Path, name: str, payload: dict[str, object]) -> None:
    (tmp_path / "integrations" / "tools").mkdir(parents=True)
    (tmp_path / "integrations" / "tools" / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _isolated_path() -> str:
    import shutil

    isolated_path_parts: list[str] = [str(Path(sys.executable).resolve().parent)]
    git_binary = shutil.which("git")
    if git_binary is not None:
        isolated_path_parts.append(str(Path(git_binary).resolve().parent))
    return os.pathsep.join(dict.fromkeys(isolated_path_parts))


def _run_recommendations(
    script_relpath: str,
    tmp_path: Path,
    *,
    recommendation_role: str | None = None,
    next_skill_id: str | None = None,
) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, script_relpath, "--repo-root", str(tmp_path)]
        + (
            ["--recommendation-role", recommendation_role]
            if recommendation_role is not None
            else []
        )
        + (["--next-skill-id", next_skill_id] if next_skill_id is not None else []),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": _isolated_path()},
    )
    return json.loads(result.stdout)


def test_quality_tool_recommendations_emit_blocking_validation_routes(tmp_path: Path) -> None:
    _write_manifest(
        tmp_path,
        "cautilus.json",
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
                    "install_url": "https://github.com/corca-ai/cautilus/blob/main/install.sh",
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
    )

    payload = _run_recommendations(
        "skills/public/quality/scripts/list_tool_recommendations.py",
        tmp_path,
    )
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
                    "install_url": "https://github.com/corca-ai/cautilus/blob/main/install.sh",
                    "notes": ["Install cautilus."],
                },
                "verify_command": "python3 scripts/doctor.py --repo-root . --json --tool-id cautilus",
                "next_skill_id": "quality",
            }
        ],
    }


def test_quality_tool_recommendations_filter_role_by_next_skill(tmp_path: Path) -> None:
    _write_manifest(
        tmp_path,
        "impl-only.json",
        {
            "schema_version": "1",
            "tool_id": "impl-only",
            "kind": "external_binary",
            "display_name": "impl-only",
            "summary": "Impl-only validation.",
            "upstream_repo": "example/impl-only",
            "homepage": "https://example.com/impl-only",
            "lifecycle": {
                "install": {"mode": "manual", "docs_url": "https://example.com", "notes": []},
                "update": {"mode": "manual", "docs_url": "https://example.com", "notes": []},
            },
            "checks": {
                "detect": {"commands": ["impl-only --version"], "success_criteria": ["exit_code:0"]},
                "healthcheck": {"commands": ["impl-only --help"], "success_criteria": ["exit_code:0"]},
            },
            "access_modes": ["binary"],
            "version_expectation": {"policy": "advisory", "constraint": "latest", "detected_by": "stdout"},
            "supports_public_skills": ["impl"],
            "recommendation_role": "validation",
        },
    )

    payload = _run_recommendations(
        "skills/public/quality/scripts/list_tool_recommendations.py",
        tmp_path,
        recommendation_role="validation",
        next_skill_id="quality",
    )

    assert payload["tool_recommendations"] == []


def test_quality_tool_recommendations_emit_blocking_runtime_routes(tmp_path: Path) -> None:
    _write_manifest(
        tmp_path,
        "glow.json",
        {
            "schema_version": "1",
            "tool_id": "glow",
            "kind": "external_binary",
            "display_name": "glow",
            "summary": "Markdown renderer.",
            "upstream_repo": "charmbracelet/glow",
            "homepage": "https://github.com/charmbracelet/glow",
            "lifecycle": {
                "install": {
                    "mode": "manual",
                    "docs_url": "https://github.com/charmbracelet/glow",
                    "install_url": "https://github.com/charmbracelet/glow#installation",
                    "notes": ["Install glow."],
                },
                "update": {"mode": "manual", "docs_url": "https://github.com/charmbracelet/glow/releases", "notes": ["Update glow."]},
            },
            "checks": {
                "detect": {"commands": ["glow --version"], "success_criteria": ["exit_code:0"]},
                "healthcheck": {"commands": ["glow --help"], "success_criteria": ["exit_code:0"]},
            },
            "access_modes": ["binary", "degraded"],
            "version_expectation": {"policy": "advisory", "constraint": "latest", "detected_by": "stdout"},
            "supports_public_skills": ["narrative", "quality"],
            "recommendation_role": "runtime",
        },
    )

    payload = _run_recommendations(
        "skills/public/quality/scripts/list_tool_recommendations.py",
        tmp_path,
        recommendation_role="runtime",
        next_skill_id="quality",
    )
    assert payload == {
        "recommendation_role": "runtime",
        "next_skill_id": "quality",
        "tool_recommendations": [
            {
                "tool_id": "glow",
                "display_name": "glow",
                "kind": "external_binary",
                "summary": "Markdown renderer.",
                "why_recommended": "Recommended because `quality` can use this tool as a supported runtime path.",
                "supports_public_skills": ["narrative", "quality"],
                "recommendation_role": "runtime",
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
                    "docs_url": "https://github.com/charmbracelet/glow",
                    "install_url": "https://github.com/charmbracelet/glow#installation",
                    "notes": ["Install glow."],
                },
                "verify_command": "python3 scripts/doctor.py --repo-root . --json --tool-id glow",
                "next_skill_id": "quality",
            }
        ],
    }


def test_narrative_tool_recommendations_emit_blocking_runtime_routes(tmp_path: Path) -> None:
    _write_manifest(
        tmp_path,
        "glow.json",
        {
            "schema_version": "1",
            "tool_id": "glow",
            "kind": "external_binary",
            "display_name": "glow",
            "summary": "Markdown renderer.",
            "upstream_repo": "charmbracelet/glow",
            "homepage": "https://github.com/charmbracelet/glow",
            "lifecycle": {
                "install": {
                    "mode": "manual",
                    "docs_url": "https://github.com/charmbracelet/glow",
                    "install_url": "https://github.com/charmbracelet/glow#installation",
                    "notes": ["Install glow."],
                },
                "update": {"mode": "manual", "docs_url": "https://github.com/charmbracelet/glow/releases", "notes": ["Update glow."]},
            },
            "checks": {
                "detect": {"commands": ["glow --version"], "success_criteria": ["exit_code:0"]},
                "healthcheck": {"commands": ["glow --help"], "success_criteria": ["exit_code:0"]},
            },
            "access_modes": ["binary", "degraded"],
            "version_expectation": {"policy": "advisory", "constraint": "latest", "detected_by": "stdout"},
            "supports_public_skills": ["narrative", "quality"],
            "recommendation_role": "runtime",
        },
    )

    payload = _run_recommendations(
        "skills/public/narrative/scripts/list_tool_recommendations.py",
        tmp_path,
    )
    assert payload == {
        "recommendation_role": "runtime",
        "next_skill_id": "narrative",
        "tool_recommendations": [
            {
                "tool_id": "glow",
                "display_name": "glow",
                "kind": "external_binary",
                "summary": "Markdown renderer.",
                "why_recommended": "Recommended because `narrative` can use this tool as a supported runtime path.",
                "supports_public_skills": ["narrative", "quality"],
                "recommendation_role": "runtime",
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
                    "docs_url": "https://github.com/charmbracelet/glow",
                    "install_url": "https://github.com/charmbracelet/glow#installation",
                    "notes": ["Install glow."],
                },
                "verify_command": "python3 scripts/doctor.py --repo-root . --json --tool-id glow",
                "next_skill_id": "narrative",
            }
        ],
    }
