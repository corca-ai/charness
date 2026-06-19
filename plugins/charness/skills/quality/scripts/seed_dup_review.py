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


def _families_from_payload(text: str) -> list[dict]:
    try:
        payload = json.loads(text) if text.strip() else {}
    except json.JSONDecodeError:
        return []
    families = payload.get("families")
    return families if isinstance(families, list) else []


def _run_inventory(script: Path, repo_root: Path) -> list[dict]:
    completed = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(repo_root), "--json"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return _families_from_payload(completed.stdout)


def _families(inventory_json: Path | None, script: Path, repo_root: Path) -> list[dict]:
    if inventory_json is not None:
        return _families_from_payload(inventory_json.read_text(encoding="utf-8"))
    return _run_inventory(script, repo_root)


def _load_existing(output_path: Path) -> dict:
    if not output_path.is_file():
        return {}
    try:
        return json.loads(output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_result(args: argparse.Namespace) -> dict:
    repo_root = args.repo_root.resolve()
    output_path = repo_root / args.output
    code_families = _families(args.code_inventory, CODE_INVENTORY, repo_root)
    doc_families = _families(args.doc_inventory, DOC_INVENTORY, repo_root)
    review = dup_review.build_review(
        _load_existing(output_path), code_families, doc_families, reviewed_at=args.reviewed_at
    )
    return {
        "review": review,
        "output": args.output,
        "output_path": str(output_path),
        "code_family_count": len(code_families),
        "doc_family_count": len(doc_families),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_REL, help=f"Overlay path (repo-relative; default {DEFAULT_OUTPUT_REL}).")
    parser.add_argument("--code-inventory", type=Path, help="Pre-collected inventory_nose_clones --json file (else the script is run).")
    parser.add_argument("--doc-inventory", type=Path, help="Pre-collected inventory_doc_duplicates --json file (else the script is run).")
    parser.add_argument("--reviewed-at", default=datetime.date.today().isoformat(), help="ISO date stamp for newly auto-seeded entries (default today).")
    parser.add_argument("--write", action="store_true", help="Write the overlay to --output (else dry-run preview).")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = build_result(args)
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
