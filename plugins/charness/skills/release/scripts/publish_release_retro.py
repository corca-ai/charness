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


def _load_public_skill_module(dotted_suffix: str):
    # The repo layout exposes public skills under `skills.public.<skill>...`; the
    # exported plugin cache drops the `public` segment (`skills.<skill>...`). Try
    # both so publish_release runs from the installed plugin cache without a
    # `ModuleNotFoundError: No module named 'skills.public'`. Only the
    # layout-resolution miss (a missing `skills`/`skills.public` package) is
    # tolerated; a genuine missing dependency inside the target module re-raises
    # immediately instead of being relabeled as a layout miss.
    last_error: ModuleNotFoundError | None = None
    for module_name in (f"skills.public.{dotted_suffix}", f"skills.{dotted_suffix}"):
        try:
            return SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, module_name)
        except ModuleNotFoundError as exc:
            missing = exc.name or ""
            if not (missing == "skills" or missing.startswith("skills.")):
                raise
            last_error = exc
    raise ModuleNotFoundError(
        f"could not resolve `skills(.public).{dotted_suffix}` in the repo or exported plugin layout"
    ) from last_error


_retro_auto_trigger = _load_public_skill_module("retro.scripts.check_auto_trigger")
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
        # This is release-delta evidence, not lesson-memory state: it has no
        # ledger fields to reconcile.
        "Mode: release-trigger",
        "",
        "## Context",
        "",
        f"Release publish triggered a configured automatic release-delta retro for `{tag_name}`.",
        "The release helper persisted this bounded release-delta evidence before committing the release artifacts so clean-tree post-publish state cannot erase the trigger evidence.",
        "",
        "**Scope: this artifact covers the release delta only.** It is derived from the",
        "release delta's surface hits and makes no claim about session-level waste,",
        "decisions, counterfactuals, or lesson dispositions.",
        "",
        "## Evidence Summary",
        "",
        f"- Triggered: `{payload.get('triggered')}`.",
        f"- Surface hits: {', '.join(f'`{item}`' for item in surface_hits) if surface_hits else 'none'}.",
        f"- Path hits: {len(path_hits)}.",
        f"- Evaluated changed paths: {len(changed_paths)}.",
        "",
        "## Waste",
        "",
        "- Without the release-helper persistence step, a successful publish can leave a clean tree and make the release trigger evidence disappear after the fact.",
        "- NOT MEASURED HERE: work outside the release delta. This helper is not a session receipt or a lesson evaluator.",
        "",
        "## Critical Decisions",
        "",
        "- The release helper treats a configured trigger hit as bounded release-delta evidence and writes the artifact in the release commit instead of leaving a chat-only reminder. The structured payload retains the exact path set; this Markdown summary records counts so deleted or ignored paths are not mistaken for durable proof citations.",
        "",
        "## Expert Counterfactuals",
        "",
        "- Jef Raskin would make the system mode visible: a triggered detector must show whether it wrote the follow-up artifact or intentionally skipped it -- and must not let a bounded record look like the unbounded one.",
        "",
        "## Next Improvements",
        "",
        "- workflow: the release-trigger artifact covers the release delta only. A broader retro is an explicit operator choice and is not represented by this artifact.",
        "",
        "## Sibling Search",
        "",
        "- Checked the release helper clean-tree path and the retro trigger detector path; this artifact covers the release-publish sibling where helper-generated changed paths would otherwise be lost.",
        "",
        # Required of EVERY retro artifact by `validate_retro_artifact.py`. Its absence
        # here made the release helper generate an artifact that failed the repo's own
        # retro validator, which failed the release quality gate, which rolled the
        # publish back -- a helper blocking every release on a section its own template
        # never learned about. What this bounded artifact can honestly say about the
        # north star is narrow, and it says exactly that rather than padding.
        "## North Star Alignment",
        "",
        "- P4 (an irreversible boundary is confirmed by a different observer AND channel) is the facet this release path is built around: the helper's own exit code is not the release verdict, and tag push, workflow completion and helper green are each explicitly non-terminal per `references/publication-boundary.md`.",
        "- SCOPE, stated rather than implied: this is RELEASE-DELTA evidence written by a helper. It can see which surfaces the delta touched; it cannot see broader reasoning, rework, or lesson dispositions. Treating this bounded record as a complete work review would be the failure signature it is meant to avoid.",
        "",
        "## Persisted",
        "",
        f"Persisted: yes: {artifact_path}",
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
