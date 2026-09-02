"""Adapter-scoped Markdown duplicate scan primitives."""

from __future__ import annotations

import hashlib
import json
import runpy
import sys
from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nose_tool_lib as nose_tool  # noqa: E402


def _load_skill_runtime_bootstrap():
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_quality_adapter = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.quality_adapter_lib"
)
load_quality_adapter = _quality_adapter.load_quality_adapter
_quality_universes = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.quality_universes_lib"
)
DEFAULT_UNIVERSES = _quality_universes.DEFAULT_UNIVERSES
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe
DEFAULT_SCAN_PATH = "."
DEFAULT_BASELINE_REL = "charness-artifacts/quality/doc-nose-baseline.json"
MIN_NOSE_VERSION = (0, 13, 0)
NOSE_TIMEOUT_SECONDS = nose_tool.NOSE_TIMEOUT_SECONDS


def resolve_doc_scope(repo_root: Path, explicit_path: str | None) -> dict[str, Any]:
    if explicit_path:
        return {
            "scan_path": explicit_path,
            "universe_files": None,
            "scope_refusal": None,
            "empty_scope_note": None,
        }
    universe = resolve_universe(
        load_quality_adapter(repo_root),
        "doc_surfaces",
        default=DEFAULT_UNIVERSES["doc_surfaces"],
    )
    files = [path for path in matching_files(repo_root, universe) if path.suffix.lower() == ".md"]
    refusal = refuse_if_declared_and_empty(universe, files, "doc-duplicates")
    return {
        "scan_path": [path.relative_to(repo_root).as_posix() for path in files],
        "universe_files": files,
        "scope_refusal": refusal,
        "empty_scope_note": (
            "doc-duplicates: discovered empty doc_surfaces universe; no Markdown families were scanned."
            if not files and not refusal
            else None
        ),
    }


def build_command(nose_bin: str, scan_path: str | Sequence[str], excludes: list[str]) -> list[str]:
    command = [nose_bin, "query", scan_path] if isinstance(scan_path, str) else [nose_bin, "query"]
    if not isinstance(scan_path, str):
        for path in scan_path:
            command.extend(["--root", path])
    for pattern in excludes:
        command.extend(["--exclude", pattern])
    command.extend(["--format", "json"])
    return command


def run_query(repo_root: Path, command: list[str]) -> dict[str, Any]:
    result = nose_tool.run_json_query(repo_root, command)
    if result.get("error_kind") == "timeout":
        return {
            "status": "error",
            "families": [],
            "stderr": f"nose timed out after {NOSE_TIMEOUT_SECONDS}s",
        }
    if result.get("error_kind") == "oserror":
        return {
            "status": "error",
            "families": [],
            "stderr": f"nose could not be executed: {result.get('error', '')}",
        }
    if result.get("error_kind") in {"invalid-json", "empty-output"}:
        stderr = (
            "nose emitted no output; the scan produced nothing to read"
            if result.get("error_kind") == "empty-output"
            else f"nose returned invalid JSON: {result.get('error', 'unparseable stdout')}"
        )
        if result.get("stderr"):
            stderr = f"{stderr}; {result['stderr']}"
        return {"status": "error", "families": [], "stderr": stderr}
    if result["status"] == "error":
        return {"status": "error", "families": [], "stderr": result["stderr"]}
    payload = result["payload"]
    families = payload.get("markdown") if isinstance(payload, dict) else None
    if not isinstance(families, list):
        keys = (
            ", ".join(sorted(str(key) for key in payload)[:8])
            if isinstance(payload, dict)
            else "<not an object>"
        )
        return {
            "status": "error",
            "families": [],
            "stderr": f"nose report declares no `markdown` family list (keys: {keys}); "
            "the Markdown family set is unestablished",
        }
    return {
        "status": "ok",
        "families": families,
        "schema_version": payload.get("schema_version"),
        "stderr": result["stderr"],
    }


def family_signature(family: dict[str, Any]) -> str:
    parts = [
        f"{str(member.get('path', '')).lstrip('./')}#{member.get('heading', '')}"
        for member in family.get("members") or []
        if isinstance(member, dict)
    ]
    digest = hashlib.sha256("|".join(sorted(parts)).encode("utf-8")).hexdigest()
    return digest[:16]


def load_baseline(repo_root: Path, baseline_rel: str) -> set[str]:
    path = repo_root / baseline_rel
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    signatures = data.get("signatures") if isinstance(data, dict) else data
    return {str(sig) for sig in signatures} if isinstance(signatures, list) else set()


def write_baseline(repo_root: Path, baseline_rel: str, families: list[dict[str, Any]]) -> None:
    path = repo_root / baseline_rel
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": 1,
        "tool": "nose-markdown",
        "note": (
            "Accepted (intentional/shared-template) Markdown duplicate families so "
            "the advisory reports only new/changed drift. Signature = sorted member "
            "path#heading tuples. Re-baseline per scanner version with --write-baseline; "
            "never treat the accepted count as a reduction target (see item 5 review)."
        ),
        "signatures": sorted({family_signature(family) for family in families}),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def family_view(family: dict[str, Any]) -> dict[str, Any]:
    witness = family.get("witness") or {}
    return {
        "signature": family_signature(family),
        "tier": family.get("tier"),
        "score": family.get("score"),
        "files": family.get("files"),
        "removable": family.get("removable"),
        "commonness": family.get("commonness"),
        "witness": {
            "a": f"{witness.get('a_path', '')}:{witness.get('a_start', '')}-{witness.get('a_end', '')}",
            "b": f"{witness.get('b_path', '')}:{witness.get('b_start', '')}-{witness.get('b_end', '')}",
            "matched_lines": witness.get("matched_lines"),
        },
    }
