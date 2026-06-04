from __future__ import annotations

import re
import runpy
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_retro_auto_trigger = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "skills.public.retro.scripts.check_auto_trigger"
)
_retro_persistence = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.retro_persistence_lib"
)

build_retro_trigger_payload = _retro_auto_trigger.build_payload
load_retro_adapter = _retro_auto_trigger.load_adapter
persist_retro_artifact = _retro_persistence.persist_retro_artifact


def _retro_artifact_name(tag_name: str) -> str:
    safe_tag = re.sub(r"[^0-9A-Za-z]+", "-", tag_name).strip("-").lower()
    today = datetime.now(timezone.utc).date().isoformat()
    return f"{today}-{safe_tag}-release-auto-retro.md"


def _retro_trigger_markdown(
    *,
    tag_name: str,
    payload: dict[str, Any],
    artifact_path: str,
) -> str:
    surface_hits = payload.get("surface_hits", [])
    path_hits = payload.get("path_hits", [])
    changed_paths = payload.get("changed_paths", [])
    lines = [
        f"# Retro: Release Auto-Retro Trigger {tag_name}",
        f"Date: {datetime.now(timezone.utc).date().isoformat()}",
        "Mode: session",
        "",
        "## Context",
        "",
        f"Release publish triggered a configured automatic session retro for `{tag_name}`.",
        "The release helper persisted this bounded retro before committing the release artifacts so clean-tree post-publish state cannot erase the trigger evidence.",
        "",
        "## Evidence Summary",
        "",
        f"- Triggered: `{payload.get('triggered')}`.",
        f"- Surface hits: {', '.join(f'`{item}`' for item in surface_hits) if surface_hits else 'none'}.",
        f"- Path hits: {', '.join(f'`{item}`' for item in path_hits) if path_hits else 'none'}.",
        f"- Evaluated changed paths: {len(changed_paths)}.",
        "",
        "## Waste",
        "",
        "- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact.",
        "",
        "## Critical Decisions",
        "",
        "- The release helper treats a configured trigger hit as a bounded session-retro obligation and writes the artifact in the release commit instead of leaving a chat-only reminder.",
        "",
        "## Expert Counterfactuals",
        "",
        "- Jef Raskin would make the system mode visible: a triggered detector must show whether it wrote the follow-up artifact or intentionally skipped it.",
        "",
        "## Next Improvements",
        "",
        "- workflow: Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance.",
        "",
        "## Sibling Search",
        "",
        "- Checked the release helper clean-tree path and the retro trigger detector path; this artifact covers the release-publish sibling where helper-generated changed paths would otherwise be lost.",
        "",
        "## Persisted",
        "",
        f"Persisted: yes `{artifact_path}`",
    ]
    return "\n".join(lines)


def persist_retro_trigger_closeout(
    repo_root: Path,
    *,
    tag_name: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    if not payload.get("triggered"):
        return {
            "status": "skipped",
            "reason": "retro trigger did not match the evaluated release paths",
        }
    adapter = load_retro_adapter(repo_root)
    if not adapter["valid"]:
        return {
            "status": "blocked",
            "reason": "retro adapter invalid",
            "errors": adapter.get("errors", []),
        }
    artifact_name = _retro_artifact_name(tag_name)
    output_dir = repo_root / adapter["data"]["output_dir"]
    artifact_rel = str((output_dir / artifact_name).relative_to(repo_root))
    summary_rel = adapter["data"].get("summary_path")
    result = persist_retro_artifact(
        repo_root=repo_root,
        output_dir=output_dir,
        artifact_name=artifact_name,
        markdown_text=_retro_trigger_markdown(
            tag_name=tag_name,
            payload=payload,
            artifact_path=artifact_rel,
        ),
        summary_path=(repo_root / summary_rel) if isinstance(summary_rel, str) else None,
    )
    return {
        "status": "written",
        "artifact_path": result["artifact_path"],
        "summary_path": result.get("summary_path"),
        "lesson_selection_index_path": result.get("lesson_selection_index_path"),
    }


def build_retro_trigger_evaluation(
    repo_root: Path,
    release_content_paths: list[str],
    *,
    evaluated_at: str,
    tag_name: str,
    execute: bool,
) -> dict[str, Any]:
    payload = build_retro_trigger_payload(repo_root, paths=release_content_paths)
    payload["evaluated_at"] = evaluated_at
    if execute:
        payload["closeout"] = persist_retro_trigger_closeout(
            repo_root, tag_name=tag_name, payload=payload
        )
        if payload["closeout"].get("status") == "blocked":
            raise SystemExit(
                "retro trigger closeout blocked release publish:\n"
                + "\n".join(payload["closeout"].get("errors", []))
            )
    else:
        payload["closeout"] = {
            "status": "would_write" if payload.get("triggered") else "skipped",
            "reason": (
                "dry run: retro artifact would be written during --execute"
                if payload.get("triggered")
                else "retro trigger did not match the evaluated release paths"
            ),
        }
    return payload
