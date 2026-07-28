#!/usr/bin/env python3
"""Seed/refresh the reviewed-fixable duplicate overlay (dup-review.json).

Reads the two nose advisories (code: ``inventory_nose_clones.py``; doc:
``inventory_doc_duplicates.py``), auto-seeds ``intentional`` for portable
per-skill copies, leaves everything else ``unreviewed`` (implicit), and writes
the overlay with ``fixable_ceiling``. No gating — this is slice 1 of item 5 (the
boy-scout dup ratchet); the slice-2 gate consumes this overlay. See the item-5
boy-scout dup-ratchet spec for the full contract.

The classification logic lives in ``dup_review_lib`` (pure, unit-tested);
this CLI is the integration seam that collects inventories and persists the
overlay. Pass ``--code-inventory`` / ``--doc-inventory`` to inject a
pre-collected ``--json`` payload (the portable/testable path); without them the
sibling inventory scripts are run with their default baseline behavior.
"""

from __future__ import annotations

import argparse
import datetime
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


_SKILL_RUNTIME = _load_skill_runtime_bootstrap()
dup_review = _SKILL_RUNTIME.load_local_skill_module(__file__, "dup_review_lib")

DEFAULT_OUTPUT_REL = "charness-artifacts/quality/dup-review.json"
_SCRIPTS_DIR = Path(__file__).resolve().parent
CODE_INVENTORY = _SCRIPTS_DIR / "inventory_nose_clones.py"
DOC_INVENTORY = _SCRIPTS_DIR / "inventory_doc_duplicates.py"


NON_SCAN_STATUSES = frozenset({"missing", "version-too-old", "error", "baseline-written"})


def _families_from_payload(text: str, source: str) -> tuple[list[dict], str | None]:
    """``(families, reason)``. ``reason`` is set when the payload did not ESTABLISH a
    family list, which is not the same as declaring an empty one: blank text (a crashed
    producer), unparseable text, a missing `families` list, and a self-reported non-scan
    status all used to read as "zero families found" and rendered a confident seed over a
    corpus that was never read (the twin of dup_ratchet_scan's triage sweep S29 fix)."""
    if not text or not text.strip():
        return [], f"{source} produced no output; the inventory produced nothing to read"
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], f"{source} did not emit JSON: {exc}"
    if not isinstance(payload, dict):
        return [], f"{source} payload is not a report object"
    status = payload.get("status")
    if status in NON_SCAN_STATUSES:
        return [], f"{source} degraded (status={status}); it established no family set"
    families = payload.get("families")
    if not isinstance(families, list):
        return [], f"{source} payload declares no families list"
    return [fam for fam in families if isinstance(fam, dict)], None


def _run_inventory(script: Path, repo_root: Path) -> tuple[list[dict], str | None]:
    completed = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(repo_root), "--json"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    families, reason = _families_from_payload(completed.stdout, script.name)
    # The return code was read by nothing: a producer that died mid-run still seeded.
    if reason is None and completed.returncode != 0:
        return [], f"{script.name} exited {completed.returncode}: {completed.stderr.strip()[:160]}"
    return families, reason


def _families(inventory_json: Path | None, script: Path, repo_root: Path) -> tuple[list[dict], str | None]:
    if inventory_json is not None:
        try:
            text = inventory_json.read_text(encoding="utf-8")
        except OSError as exc:
            return [], f"cannot read {inventory_json}: {exc}"
        return _families_from_payload(text, str(inventory_json))
    return _run_inventory(script, repo_root)


def _load_existing(output_path: Path) -> tuple[dict, str | None]:
    """``(overlay, reason)``. A CORRUPT existing overlay used to read as "no prior review",
    so ``--write`` rebuilt it from scratch and dropped every operator classification (and
    reset the one-way ``fixable_ceiling``) while reporting success.

    Unparseable is not the only unreadable: `dup_review_lib.build_review` does
    ``(existing or {}).get("entries") or []``, so a payload that is a list, a scalar, or a
    dict whose `entries` key was renamed or lost in a partial hand-edit ALSO yields zero
    prior entries — the same silent wipe through a parse that succeeded. This mirrors
    `migrate_dup_fingerprints._load_review_data`, which the same repair round gave the
    stronger check; the two overlay readers must not disagree about what "readable" means."""
    if not output_path.is_file():
        return {}, None
    unreadable = f"{output_path} is present but unreadable"
    refusal = "; refusing to reseed rather than rebuilding the reviewed overlay from scratch."
    try:
        data = json.loads(output_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {}, f"{unreadable} ({exc}){refusal}"
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return {}, f"{unreadable} (no `entries` list){refusal}"
    return data, None


def build_result(args: argparse.Namespace) -> dict:
    repo_root = args.repo_root.resolve()
    output_path = repo_root / args.output
    code_families, code_reason = _families(args.code_inventory, CODE_INVENTORY, repo_root)
    doc_families, doc_reason = _families(args.doc_inventory, DOC_INVENTORY, repo_root)
    existing, existing_reason = _load_existing(output_path)
    unestablished = [reason for reason in (code_reason, doc_reason, existing_reason) if reason]
    if unestablished:
        return {
            "ok": False,
            "review": None,
            "output": args.output,
            "output_path": str(output_path),
            "code_family_count": len(code_families),
            "doc_family_count": len(doc_families),
            "unestablished_reasons": unestablished,
        }
    review = dup_review.build_review(existing, code_families, doc_families, reviewed_at=args.reviewed_at)
    return {
        "ok": True,
        "review": review,
        "output": args.output,
        "output_path": str(output_path),
        "code_family_count": len(code_families),
        "doc_family_count": len(doc_families),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True, help="Repository root whose duplicate inventories and overlay should be managed")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_REL, help=f"Overlay path (repo-relative; default {DEFAULT_OUTPUT_REL}).")
    parser.add_argument("--code-inventory", type=Path, help="Pre-collected inventory_nose_clones --json file (else the script is run).")
    parser.add_argument("--doc-inventory", type=Path, help="Pre-collected inventory_doc_duplicates --json file (else the script is run).")
    parser.add_argument("--reviewed-at", default=datetime.date.today().isoformat(), help="ISO date stamp for newly auto-seeded entries (default today).")
    parser.add_argument("--write", action="store_true", help="Write the overlay to --output (else dry-run preview).")
    parser.add_argument("--json", action="store_true", help="Emit the seed result as JSON")
    args = parser.parse_args()

    result = build_result(args)
    if not result["ok"]:
        sys.stderr.write("dup-review seed refused: an input established no family set:\n")
        for reason in result["unestablished_reasons"]:
            sys.stderr.write(f"  - {reason}\n")
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 1
    review = result["review"]
    errors = dup_review.validate_review(review)
    if errors:
        sys.stderr.write("dup-review seed produced an invalid overlay:\n")
        for err in errors:
            sys.stderr.write(f"  - {err}\n")
        return 1
    if args.write:
        out = Path(result["output_path"])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        action = "wrote" if args.write else "previewed (dry-run; pass --write to persist)"
        print(
            f"dup-review {action}: {len(review['entries'])} classified entries "
            f"(fixable_ceiling={review['fixable_ceiling']}) from {result['code_family_count']} code + "
            f"{result['doc_family_count']} doc families -> {result['output']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
