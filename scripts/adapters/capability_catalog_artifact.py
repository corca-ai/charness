"""Canonical current-pointer writer for the capability catalog."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.artifacts.current_pointer_writer_lib import (  # noqa: E402
    write_current_pointer_json,
    write_current_pointer_text,
)

CATALOG_DIR = Path("charness-artifacts/capability-catalog")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def render_markdown(snapshot: dict[str, Any]) -> str:
    inv = snapshot["inventory"]
    lines = ["# Capability Catalog", f"Date: {snapshot['generated_at'][:10]}", f"Updated: {snapshot['generated_at']}", "", "## Summary"]
    for label, key in (("public skills", "public_skills"), ("support skills", "support_skills"), ("support capabilities", "support_capabilities"), ("integrations", "integrations"), ("trusted skills", "trusted_skills")):
        lines.append(f"- {label}: {len(inv.get(key, []))}")
    for title, key in (("Public Skills", "public_skills"), ("Support Skills", "support_skills"), ("Support Capabilities", "support_capabilities"), ("Integrations", "integrations"), ("Trusted Skills", "trusted_skills")):
        lines.extend(["", f"## {title}"])
        entries = inv.get(key, [])
        if not entries:
            lines.append("- none")
        for entry in entries:
            summary = entry.get("summary", "")
            layer = f" ({entry['layer']})" if entry.get("layer") else ""
            lines.append(f"- `{entry.get('id', '')}`{layer}: {summary}")
    return "\n".join(lines) + "\n"


def _load(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) and isinstance(value.get("inventory"), dict) else None


def persist_catalog(repo_root: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    output_dir = repo_root / CATALOG_DIR
    markdown_path, json_path = output_dir / "latest.md", output_dir / "latest.json"
    existing = _load(json_path)
    if existing is not None:
        prior = existing.get("inventory", {})
        for key in ("support_skills", "support_capabilities", "integrations"):
            if isinstance(prior, dict) and prior.get(key) and not inventory.get(key):
                raise ValueError(f"refusing to overwrite capability catalog with empty {key} surface")
    if existing is not None and existing.get("inventory") == inventory and markdown_path.is_file():
        generated_at = existing.get("generated_at") or _now()
        updated = False
    else:
        generated_at = _now()
        snapshot = {"schema_version": 1, "artifact_kind": "capability-catalog", "generated_at": generated_at, "repo": repo_root.name, "inventory": inventory}
        output_dir.mkdir(parents=True, exist_ok=True)
        write_current_pointer_text(markdown_path, render_markdown(snapshot))
        write_current_pointer_json(json_path, snapshot)
        updated = True
    return {"mode": "write", "markdown_path": str(markdown_path.relative_to(repo_root)), "json_path": str(json_path.relative_to(repo_root)), "generated_at": generated_at, "updated": updated}


def read_only_result() -> dict[str, Any]:
    return {"mode": "read-only", "markdown_path": None, "json_path": None, "generated_at": None, "updated": False}
