#!/usr/bin/env python3
"""Boy-scout dup-ratchet — live fingerprint / drift-signature collection seam.

Extracted from ``check_dup_ratchet.py`` (module-length split, item 5). This is the
leaf that turns the world into identity sets: it derives the current code
content-fingerprint set (from a full ``nose query`` scan or an injected structured
inventory) and the doc drift-signature set (from ``inventory_doc_duplicates`` or an
injected file). The gate CLI (``check_dup_ratchet.py``) and its baseline maintenance
commands both consume this; it depends only on the nose scan/report/fingerprint
helpers, so the dependency direction stays one-way (scan <- check, never a cycle).

Test seams mirror the CLI: ``code_family_members`` / ``doc_drift_signatures`` honor an
injected ``--code-inventory`` / ``--doc-inventory`` payload so no nose binary is
needed. An injected family carries ``family_fingerprint`` / ``family_member_hashes``
directly, or they are computed from injected raw ``locations``.
"""

from __future__ import annotations

import contextlib
import io
import json
import runpy
import sys
import traceback
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import yaml


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
# An inventory payload carrying one of these statuses established no family set: it
# reports a missing/old/broken scanner, or (baseline-written) what was accepted rather
# than what drifted. Shared by the code and doc readers so the two arms of the gate
# cannot disagree about which statuses count as a scan.
UNESTABLISHED_DOC_STATUSES = frozenset({"missing", "version-too-old", "error", "baseline-written"})
UNESTABLISHED_CODE_STATUSES = UNESTABLISHED_DOC_STATUSES


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


def load_review_overlay(
    repo_root: Path,
    review_rel: str,
    validator: Callable[[object], list[str]],
) -> tuple[dict | None, str | None]:
    overlay = load_json(repo_root / review_rel)
    if overlay is None:
        return None, f"overlay missing/unreadable ({review_rel})"
    errors = validator(overlay)
    if errors:
        return None, f"overlay integrity ({review_rel}): " + "; ".join(errors)
    return overlay, None


def families_from_text(text: str | None) -> list | None:
    """The injected inventory's DECLARED family list, or ``None`` when the payload does
    not establish one. A zero-byte/blank file, a non-object payload, and an object with
    no `families` list all used to read as `[]` — indistinguishable from an inventory
    that declared zero families, so a crashed or truncated producer rendered a clean
    gate over a scan that never ran (triage sweep S29). `[]` now means the payload said
    zero; anything else is a reason the caller degrades on."""
    if text is None or not text.strip():
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    families = payload.get("families")
    return families if isinstance(families, list) else None


def scan_families(
    repo_root: Path, scope_paths: list[str]
) -> tuple[list[dict] | None, str | None, str]:
    """Shared leaf: one full ``nose query`` scan over ``scope_paths``, returning the
    raw family dicts (each already carrying nose_report_lib's stamped
    ``family_fingerprint`` / ``family_member_hashes``, plus ``locations`` for a
    caller that needs the raw member spans), or ``None`` with a reason on a missing
    nose binary or a scan error. `scan_code_members` builds on this (one nose
    invocation per caller, never a double-scan for the perf budget)."""
    nose_bin = _inventory.resolve_nose_bin()
    if nose_bin is None:
        return None, "nose binary not found; code clone scan skipped", ""
    paths = [str(path) for path in (scope_paths or _inventory.DEFAULT_PATHS)]
    # Full enumeration via the pinned `nose query` resolver: one nose `--root` multi-root
    # query over the whole scope (a cross-root clone is grouped, not split per root), high
    # top= so every family is recorded. `collect_families` stamps each family's offset/path-
    # independent content fingerprint (slice 4); the gate keys newness on that, not the
    # offset/path-folding family_id (resolves D30).
    result = _nose_report.collect_families(
        repo_root,
        nose_bin,
        paths,
        mode=_inventory.DEFAULT_MODE,
        min_size=FULL_SCAN_MIN_SIZE,
        top=FULL_SCAN_TOP,
        sort="extractability",
    )
    live_version = result.get("tool_version", "")
    if result.get("status") == "error":
        return None, f"nose code scan error: {result.get('stderr', '')[:160]}", live_version
    families = [fam for fam in result.get("families", []) if isinstance(fam, dict)]
    return families, None, live_version


def family_member_spans(family: dict) -> list[dict]:
    """Well-formed ``{file, start, end}`` member spans from one raw family's
    ``locations`` list (nose stamps repo-relative ``file`` and 1-based inclusive
    ``start``/``end``). Malformed entries are dropped rather than degrading: spans
    are hard-block *evidence* for the human/JSON report, never gate identity, so a
    partial list still beats an opaque fingerprint."""
    spans: list[dict] = []
    for location in family.get("locations") or []:
        if not isinstance(location, dict):
            continue
        file, start, end = location.get("file"), location.get("start"), location.get("end")
        if (
            isinstance(file, str)
            and file
            and isinstance(start, int)
            and isinstance(end, int)
            and not isinstance(start, bool)
            and not isinstance(end, bool)
        ):
            spans.append({"file": file, "start": start, "end": end})
    return spans


def scan_code_members(
    repo_root: Path, scope_paths: list[str]
) -> tuple[dict[str, list[str]], dict[str, list[dict]], str | None, str]:
    """Real (non-injected) code-family scan, returning ``({fingerprint: member_hashes},
    {fingerprint: member_spans}, reason, live_version)``. Schema v3 stores the
    per-family member hashes in the gate baseline; the CLI's reduction pre-pass diffs
    them as multisets, and the member spans feed the hard-block evidence report so a
    blocked new family names its file/line members instead of only an opaque
    fingerprint. Shares the FD8 whole-gate-degrade discipline: any family missing
    either stamped identity field degrades the WHOLE map to a reason, never a
    silently dropped family."""
    families, reason, live_version = scan_families(repo_root, scope_paths)
    if reason:
        return {}, {}, reason, live_version
    missing = [
        fam
        for fam in families
        if not fam.get("family_fingerprint")
        or not isinstance(fam.get("family_member_hashes"), list)
    ]
    if missing:
        return (
            {},
            {},
            f"{len(missing)} clone family(ies) had an unreadable member span; "
            "content fingerprint degraded (whole gate advisory)",
            live_version,
        )
    members = {
        str(fam["family_fingerprint"]): [str(h) for h in fam["family_member_hashes"]]
        for fam in families
        if fam.get("family_fingerprint")
    }
    spans = {
        str(fam["family_fingerprint"]): family_member_spans(fam)
        for fam in families
        if fam.get("family_fingerprint")
    }
    return members, spans, None, live_version


def payload_string_field(text: str | None, field: str) -> str:
    """One top-level string field of an injected structured payload, or ``""`` when
    the payload is absent/unreadable or the field is missing or not a string.

    Two fields are read this way and neither gets its own wrapper: ``status`` (read ONLY to
    refuse a self-reported non-scan payload — the family set itself always comes from the
    declared list) and ``tool_version`` (the injected scan's scanner version, for skew
    detection against the gate baseline's stamp)."""
    try:
        payload = json.loads(text) if text and text.strip() else {}
    except json.JSONDecodeError:
        return ""
    value = payload.get(field) if isinstance(payload, dict) else None
    return value if isinstance(value, str) else ""


def code_family_members(
    args, repo_root: Path, scope_paths: list[str]
) -> tuple[dict[str, list[str]], dict[str, list[dict]], str | None, str]:
    """The injected-inventory test seam (``--code-inventory``) mirrors the CLI:
    an injected family carries `family_member_hashes` directly, else it is computed
    from injected raw `locations`. A family missing both stays unrepresented — the
    CLI's own missing-fingerprint checks already degrade the whole gate on that
    shape. Without an injected inventory, delegates to a real ``scan_code_members``.
    Returns the same 4-tuple shape: member spans (second element) come from each
    family's raw ``locations`` and may be empty for a synthetic injected family —
    evidence-only, never identity."""
    if args.code_inventory is not None:
        text = safe_read(args.code_inventory)
        # The doc reader has always degraded on a self-reported non-scan status; the code
        # reader checked shape only, so an injected payload minted when nose was absent
        # or erroring (`families: []` by construction) read as a declared-empty scan and
        # rendered a clean gate — the S29 class, in the sibling arm of the same function.
        status = payload_string_field(text, "status")
        if status in UNESTABLISHED_CODE_STATUSES:
            return {}, {}, f"injected code inventory degraded (status={status})", ""
        families = families_from_text(text)
        if families is None:
            return {}, {}, f"injected code inventory unreadable ({args.code_inventory})", ""
        members: dict[str, list[str]] = {}
        spans: dict[str, list[dict]] = {}
        for fam in families:
            if not isinstance(fam, dict):
                continue
            fingerprint = fam.get("family_fingerprint")
            hashes = fam.get("family_member_hashes")
            if not fingerprint and fam.get("locations"):
                fingerprint = _fingerprint.family_content_fingerprint(fam, repo_root)
            if not isinstance(hashes, list) and fam.get("locations"):
                hashes = _fingerprint.family_member_hashes(fam, repo_root)
            if fingerprint and isinstance(hashes, list):
                members[str(fingerprint)] = [str(h) for h in hashes]
                spans[str(fingerprint)] = family_member_spans(fam)
        return members, spans, None, payload_string_field(text, "tool_version")
    return scan_code_members(repo_root, scope_paths)


def run_doc_inventory(repo_root: Path) -> str:
    module = SKILL_RUNTIME.load_local_skill_module(__file__, "inventory_doc_duplicates")
    stdout = io.StringIO()
    stderr = io.StringIO()
    previous_argv = sys.argv
    try:
        sys.argv = [str(DOC_INVENTORY), "--repo-root", str(repo_root), "--detail"]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                module.main()
            except SystemExit:
                pass
            except Exception:
                traceback.print_exc()
    finally:
        sys.argv = previous_argv
    return stdout.getvalue()


def doc_drift_signatures(args, repo_root: Path) -> tuple[set[str], str | None]:
    if args.doc_inventory is not None:
        text = safe_read(args.doc_inventory)
        if text is None:
            return set(), f"injected doc inventory missing ({args.doc_inventory})"
    else:
        text = run_doc_inventory(repo_root)
    # An empty payload is a producer that died (a crashed/nonzero-exit
    # `inventory_doc_duplicates` prints nothing), NOT a doc corpus with no drift; it
    # used to parse as `{}` and return no signatures with no reason (S29).
    if not text or not text.strip():
        return set(), "doc inventory produced no output; the doc scan produced nothing to read"
    try:
        payload = yaml.safe_load(text)
    except yaml.YAMLError:
        return set(), "doc inventory YAML unreadable"
    if not isinstance(payload, dict):
        return set(), "doc inventory payload malformed"
    # `baseline-written` belongs here with the other non-drift statuses: that payload
    # reports what was ACCEPTED and always carries `families: []`, so reading it as a
    # drift scan is a clean verdict over a scan that answered a different question.
    if payload.get("status") in UNESTABLISHED_DOC_STATUSES:
        return set(), f"doc inventory degraded (status={payload.get('status')})"
    families = payload.get("families")
    if not isinstance(families, list):
        # Covers a renamed key and the `--summary` view (which emits `families_sample`),
        # the doc-side twin of the S27 truncated-view trap.
        return set(), "doc inventory payload declares no families list"
    signatures = {
        fam["signature"]
        for fam in families
        if isinstance(fam, dict) and isinstance(fam.get("signature"), str) and fam.get("signature")
    }
    return signatures, None


def live_scan_for_rebaseline(
    repo_root: Path,
    config: dict,
    args,
    *,
    default_baseline_rel: str,
    fail_status: str,
    fail_prefix: str,
) -> tuple[str, dict, str, dict | None]:
    """Shared preamble of the gate's --write-baseline and scoped-accept paths:
    resolve the adapter paths, run the live scan, and typed-fail on a scan reason."""
    scope_paths = list(config.get("scope_paths") or [])
    baseline_rel = config.get("gate_baseline_path") or default_baseline_rel
    members, spans, reason, live_version = code_family_members(args, repo_root, scope_paths)
    # Preserve the path evidence alongside the historical tuple return shape so
    # callers and consumer fixtures remain compatible while new baselines can
    # carry stable lineage bindings.
    setattr(
        args,
        "_live_member_paths",
        {
            fingerprint: sorted(
                {
                    str(span["file"]).replace("\\", "/")
                    for span in family_spans
                    if isinstance(span, dict)
                    and isinstance(span.get("file"), str)
                    and span.get("file")
                }
            )
            for fingerprint, family_spans in spans.items()
        },
    )
    error = None
    if reason:
        error = {
            "ok": False,
            "inert": False,
            "status": fail_status,
            "messages": [f"{fail_prefix}: {reason}"],
        }
    return baseline_rel, members, live_version, error
