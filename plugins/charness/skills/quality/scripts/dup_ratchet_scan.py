#!/usr/bin/env python3
"""Boy-scout dup-ratchet — live fingerprint / drift-signature collection seam.

Extracted from ``check_dup_ratchet.py`` (module-length split, item 5). This is the
leaf that turns the world into identity sets: it derives the current code
content-fingerprint set (from a full ``nose query`` scan or an injected ``--json``
inventory) and the doc drift-signature set (from ``inventory_doc_duplicates`` or an
injected file). The gate CLI (``check_dup_ratchet.py``) and its baseline maintenance
commands both consume this; it depends only on the nose scan/report/fingerprint
helpers, so the dependency direction stays one-way (scan <- check, never a cycle).

Test seams mirror the CLI: ``code_fingerprints`` / ``doc_drift_signatures`` honor an
injected ``--code-inventory`` / ``--doc-inventory`` payload so no nose binary is
needed. An injected family carries ``family_fingerprint`` directly, or the fingerprint
is computed from injected raw ``locations``.
"""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_inventory = SKILL_RUNTIME.load_local_skill_module(__file__, "inventory_nose_clones")
_nose_report = SKILL_RUNTIME.load_local_skill_module(__file__, "nose_report_lib")
_fingerprint = SKILL_RUNTIME.load_local_skill_module(__file__, "nose_fingerprint_lib")

DOC_INVENTORY = Path(__file__).resolve().parent / "inventory_doc_duplicates.py"
# Full enumeration: high --top, no nose --baseline (the gate baseline seed must
# carry EVERY family_id, or unenumerated families false-block later).
FULL_SCAN_TOP = 1_000_000
FULL_SCAN_MIN_SIZE = 24


def safe_read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def load_json(path: Path):
    text = safe_read(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def families_from_text(text: str | None) -> list | None:
    if text is None:
        return None
    try:
        payload = json.loads(text) if text.strip() else {}
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    families = payload.get("families")
    return families if isinstance(families, list) else []


def scan_code_fingerprints(repo_root: Path, scope_paths: list[str]) -> tuple[set[str], str | None, str]:
    nose_bin = _inventory.resolve_nose_bin()
    if nose_bin is None:
        return set(), "nose binary not found; code clone scan skipped", ""
    paths = [str(path) for path in (scope_paths or _inventory.DEFAULT_PATHS)]
    # Full enumeration via the pinned `nose query` resolver: one nose `--root` multi-root
    # query over the whole scope (a cross-root clone is grouped, not split per root), high
    # top= so every family is recorded. `collect_families` stamps each family's offset/path-
    # independent content fingerprint (slice 4); the gate keys newness on that, not the
    # offset/path-folding family_id (resolves D30).
    result = _nose_report.collect_families(
        repo_root, nose_bin, paths, mode=_inventory.DEFAULT_MODE,
        min_size=FULL_SCAN_MIN_SIZE, top=FULL_SCAN_TOP, sort="extractability",
    )
    live_version = result.get("tool_version", "")
    if result.get("status") == "error":
        return set(), f"nose code scan error: {result.get('stderr', '')[:160]}", live_version
    families = [fam for fam in result.get("families", []) if isinstance(fam, dict)]
    # A family with no stamped fingerprint had an unreadable member span (file changed
    # between scan and read, etc.). Degrade the WHOLE gate to advisory (FD8) — never a
    # false block, never a silently dropped family that would read as "removed".
    missing = [fam for fam in families if not fam.get("family_fingerprint")]
    if missing:
        return (
            set(),
            f"{len(missing)} clone family(ies) had an unreadable member span; "
            "content fingerprint degraded (whole gate advisory)",
            live_version,
        )
    fingerprints = {str(fam["family_fingerprint"]) for fam in families}
    return {fp for fp in fingerprints if fp}, None, live_version


def payload_tool_version(text: str | None) -> str:
    """Top-level nose tool_version stamped into an injected inventory --json payload,
    or ``""`` when absent/unreadable. The injected scan's version is the live scanner
    version for skew detection against the gate baseline's stamped version."""
    try:
        payload = json.loads(text) if text and text.strip() else {}
    except json.JSONDecodeError:
        return ""
    version = payload.get("tool_version") if isinstance(payload, dict) else None
    return version if isinstance(version, str) else ""


def code_fingerprints(args, repo_root: Path, scope_paths: list[str]) -> tuple[set[str], str | None, str]:
    if args.code_inventory is not None:
        text = safe_read(args.code_inventory)
        families = families_from_text(text)
        if families is None:
            return set(), f"injected code inventory unreadable ({args.code_inventory})", ""
        # Test seam: an injected family carries `family_fingerprint` directly (symmetric
        # with the pre-slice-4 injected `family_id`); else compute it from injected raw
        # `locations` so an injected nose-shaped inventory also works.
        fingerprints: set[str] = set()
        for fam in families:
            if not isinstance(fam, dict):
                continue
            fingerprint = fam.get("family_fingerprint")
            if not fingerprint and fam.get("locations"):
                fingerprint = _fingerprint.family_content_fingerprint(fam, repo_root)
            if fingerprint:
                fingerprints.add(str(fingerprint))
        return fingerprints, None, payload_tool_version(text)
    return scan_code_fingerprints(repo_root, scope_paths)


def run_doc_inventory(repo_root: Path) -> str:
    completed = subprocess.run(
        [sys.executable, str(DOC_INVENTORY), "--repo-root", str(repo_root), "--json"],
        cwd=repo_root, check=False, capture_output=True, text=True,
    )
    return completed.stdout


def doc_drift_signatures(args, repo_root: Path) -> tuple[set[str], str | None]:
    if args.doc_inventory is not None:
        text = safe_read(args.doc_inventory)
        if text is None:
            return set(), f"injected doc inventory missing ({args.doc_inventory})"
    else:
        text = run_doc_inventory(repo_root)
    try:
        payload = json.loads(text) if text and text.strip() else {}
    except json.JSONDecodeError:
        return set(), "doc inventory JSON unreadable"
    if not isinstance(payload, dict):
        return set(), "doc inventory payload malformed"
    if payload.get("status") in {"missing", "version-too-old", "error"}:
        return set(), f"doc inventory degraded (status={payload.get('status')})"
    families = payload.get("families")
    if not isinstance(families, list):
        return set(), None
    signatures = {
        fam["signature"] for fam in families
        if isinstance(fam, dict) and isinstance(fam.get("signature"), str) and fam.get("signature")
    }
    return signatures, None
