from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

QUALITY_SCRIPT = "skills/public/quality/scripts/list_tool_recommendations.py"
_quality_tool_recommendations = load_script_module(
    "tests.quality_gates.quality_list_tool_recommendations",
    ROOT / QUALITY_SCRIPT,
)


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


def _run_quality_recommendations(
    monkeypatch, capsys, tmp_path: Path, *args: str
) -> dict[str, object]:
    monkeypatch.setenv("PATH", _isolated_path())
    monkeypatch.setattr(
        sys,
        "argv",
        [QUALITY_SCRIPT, "--repo-root", str(tmp_path), *args],
    )
    result = run_loaded_script_main(QUALITY_SCRIPT, _quality_tool_recommendations, *sys.argv[1:])
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


def _run_recommendations(
    script_relpath: str,
    tmp_path: Path,
    *,
    recommendation_role: str | None = None,
    next_skill_id: str | None = None,
) -> dict[str, object]:
    args = ["--repo-root", str(tmp_path)]
    if recommendation_role is not None:
        args.extend(["--recommendation-role", recommendation_role])
    if next_skill_id is not None:
        args.extend(["--next-skill-id", next_skill_id])
    module_name = "recommendations_" + script_relpath.replace("/", "_").replace(".", "_")
    result = run_loaded_script_main(
        script_relpath,
        load_script_module(module_name, ROOT / script_relpath),
        *args,
        env={**os.environ, "PATH": _isolated_path()},
    )
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


def test_quality_tool_recommendations_filter_role_by_next_skill(
    tmp_path: Path, monkeypatch, capsys
) -> None:
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
                "detect": {
                    "commands": ["impl-only --version"],
                    "success_criteria": ["exit_code:0"],
                },
                "healthcheck": {
                    "commands": ["impl-only --help"],
                    "success_criteria": ["exit_code:0"],
                },
            },
            "access_modes": ["binary"],
            "version_expectation": {
                "policy": "advisory",
                "constraint": "latest",
                "detected_by": "stdout",
            },
            "supports_public_skills": ["impl"],
            "recommendation_role": "validation",
        },
    )

    payload = _run_quality_recommendations(
        monkeypatch,
        capsys,
        tmp_path,
        "--recommendation-role",
        "validation",
        "--next-skill-id",
        "quality",
    )

    assert payload["tool_recommendations"] == []


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
                "update": {
                    "mode": "manual",
                    "docs_url": "https://github.com/charmbracelet/glow/releases",
                    "notes": ["Update glow."],
                },
            },
            "checks": {
                "detect": {"commands": ["glow --version"], "success_criteria": ["exit_code:0"]},
                "healthcheck": {"commands": ["glow --help"], "success_criteria": ["exit_code:0"]},
            },
            "access_modes": ["binary", "degraded"],
            "version_expectation": {
                "policy": "advisory",
                "constraint": "latest",
                "detected_by": "stdout",
            },
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
                "verify_command": "python3 scripts/doctor.py --repo-root . --tool-id glow",
                "next_skill_id": "narrative",
                "manifest_origin": "user-repo",
                "staged": None,
            }
        ],
    }
