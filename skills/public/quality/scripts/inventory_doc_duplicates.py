#!/usr/bin/env python3
"""Advisory nose Markdown near-duplicate inventory for quality doc review.

Replaces the bespoke difflib whole-file `check_doc_near_duplicates.py` gate with
nose's first-class Markdown duplication engine (char-n-gram MinHash + witnesses,
nose >= 0.13.0). Advisory posture, mirroring `inventory_nose_clones.py` for code:
nose detects + witnesses near-duplicate prose families; the maintainer judges
which are intentional shared template versus single-sourceable duplication.

nose's native `--baseline` filters only the code-clone view, not the top-level
`markdown` array, so this script keeps its own signature baseline (sorted member
`path#heading` tuples) under `charness-artifacts/quality/doc-nose-baseline.json`
so the advisory reports only NEW/changed doc families (drift) rather than
re-flagging the accepted intentional mass every run.
"""

from __future__ import annotations

import argparse
import json
import runpy
import shlex
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_output_lib import add_output_args, emit_selected  # noqa: E402


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
_scan = SKILL_RUNTIME.load_local_skill_module(__file__, "doc_duplicate_scan")
nose_tool = _scan.nose_tool
DEFAULT_SCAN_PATH = _scan.DEFAULT_SCAN_PATH
DEFAULT_BASELINE_REL = _scan.DEFAULT_BASELINE_REL
MIN_NOSE_VERSION = _scan.MIN_NOSE_VERSION
NOSE_TIMEOUT_SECONDS = _scan.NOSE_TIMEOUT_SECONDS

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): this inference-layer proxy self-declares
# its blind spots and the question the consumer must answer before acting.
INTERPRETATION = {
    "measures": "near-duplicate Markdown prose families (same-language char-n-gram similarity) across checked-in docs and skill text",
    "proxy_for": "single-sourceable doc duplication a shared canonical section or include could remove",
    "blind_spots": (
        "intentional per-skill template/boilerplate (adapter-contract sections, "
        "preset scaffolds, shared reference shapes) scores as duplication; it is "
        "lexical/structural, so it cannot tell a deliberate shared shape from "
        "copy-paste drift"
    ),
    "interpretation_question": (
        "which of these doc families are intentional shared template versus "
        "genuinely single-sourceable duplication for THIS repo?"
    ),
}


def resolve_nose_bin() -> str | None:
    return nose_tool.resolve_nose_bin()


def parse_nose_version(text: str) -> tuple[int, int, int] | None:
    return nose_tool.parse_nose_version(text)


def nose_version(nose_bin: str) -> tuple[int, int, int] | None:
    return nose_tool.probe_nose_version(nose_bin).get("version")


family_signature = _scan.family_signature
build_command = _scan.build_command


run_query = _scan.run_query


load_baseline = _scan.load_baseline
write_baseline = _scan.write_baseline


family_view = _scan.family_view


def payload_for_args(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    scope = _scan.resolve_doc_scope(repo_root, args.path)
    scan_path = scope["scan_path"]
    universe_files = scope["universe_files"]
    scope_refusal = scope["scope_refusal"]
    excludes = list(args.exclude)
    baseline_rel = args.baseline or DEFAULT_BASELINE_REL
    if scope_refusal:
        return {
            "status": "scope-refused",
            "advisory": True,
            "repo_root": str(repo_root),
            "scan_path": scan_path,
            "excludes": excludes,
            "family_count": 0,
            "families": [],
            "notes": [scope_refusal],
        }
    discovered_empty = universe_files is not None and not universe_files
    empty_scope_note = scope["empty_scope_note"] if discovered_empty else None
    nose_bin = resolve_nose_bin()
    if nose_bin is None:
        notes = [
            "nose is REQUIRED (>=0.13.0) for doc near-duplicate review; install per integrations/tools/nose.json.",
            "The run-quality `nose` phase fails closed when the binary is absent; this advisory only reports.",
        ]
        if empty_scope_note:
            notes.append(empty_scope_note)
        return {
            "status": "missing",
            "advisory": True,
            "repo_root": str(repo_root),
            "scan_path": scan_path,
            "excludes": excludes,
            "family_count": 0,
            "families": [],
            "notes": notes,
        }
    version = nose_version(nose_bin)
    if version is not None and version < MIN_NOSE_VERSION:
        want = ".".join(str(part) for part in MIN_NOSE_VERSION)
        have = ".".join(str(part) for part in version)
        notes = [
            f"nose {have} cannot detect Markdown families; doc near-duplicate review needs >= {want}.",
            "Update per integrations/tools/nose.json; an old nose silently reports zero doc families.",
        ]
        if empty_scope_note:
            notes.append(empty_scope_note)
        return {
            "status": "version-too-old",
            "advisory": True,
            "repo_root": str(repo_root),
            "scan_path": scan_path,
            "excludes": excludes,
            "tool_version": have,
            "family_count": 0,
            "families": [],
            "notes": notes,
        }
    if empty_scope_note:
        return {
            "status": "empty-scope",
            "advisory": True,
            "repo_root": str(repo_root),
            "scan_path": scan_path,
            "excludes": excludes,
            "family_count": 0,
            "families": [],
            "notes": [empty_scope_note],
        }
    command = build_command(nose_bin, scan_path, excludes)
    result = run_query(repo_root, command)
    if result["status"] != "ok":
        return {
            "status": "error",
            "advisory": True,
            "repo_root": str(repo_root),
            "scan_path": scan_path,
            "excludes": excludes,
            "command": shlex.join(command),
            "family_count": 0,
            "families": [],
            "stderr": result.get("stderr", ""),
            "notes": ["nose doc inventory error; review manually."],
        }
    if args.write_baseline:
        write_baseline(repo_root, baseline_rel, result["families"])
        return {
            "status": "baseline-written",
            "advisory": True,
            "repo_root": str(repo_root),
            "scan_path": scan_path,
            "baseline": baseline_rel,
            "command": shlex.join(command),
            "family_count": len(result["families"]),
            "families": [],
            "notes": [
                "Baseline accepts today's intentional/shared-template doc families so the advisory reports only new/changed drift.",
                "Re-baseline per scanner version; never treat the accepted count as a reduction target.",
            ],
        }
    accepted = load_baseline(repo_root, baseline_rel)
    new_families = [fam for fam in result["families"] if family_signature(fam) not in accepted]
    return {
        "status": "ok",
        "advisory": True,
        "repo_root": str(repo_root),
        "scan_path": scan_path,
        "excludes": excludes,
        "command": shlex.join(command),
        "schema_version": result.get("schema_version"),
        "baseline": baseline_rel if accepted else None,
        "accepted_count": len(accepted),
        "total_family_count": len(result["families"]),
        "family_count": len(new_families),
        "families": [family_view(fam) for fam in new_families],
        "interpretation": dict(INTERPRETATION),
        "notes": [
            "nose Markdown findings are review candidates, not standing quality failures.",
            "Review which families are intentional shared template versus single-sourceable; do not chase every family.",
            "Accepted families live in the doc baseline; only new/changed drift is reported here.",
            "Never treat the family count as a reduction target without the item-5 reviewed-candidate classification.",
        ],
    }


def print_human(payload: dict[str, Any]) -> None:
    status = payload["status"]
    if status == "scope-refused":
        print(f"REFUSED: {payload['notes'][0]}")
        return
    if status == "empty-scope":
        print(payload["notes"][0])
        return
    if status == "missing":
        print(
            "ADVISORY: nose missing; doc near-duplicate inventory skipped. nose >=0.13.0 is required (integrations/tools/nose.json)."
        )
        return
    if status == "version-too-old":
        print(
            f"ADVISORY: nose {payload.get('tool_version')} too old for Markdown families; need >=0.13.0 (integrations/tools/nose.json)."
        )
        return
    if status == "error":
        print(f"ADVISORY: nose doc inventory error; review manually. {payload.get('stderr', '')}")
        return
    if status == "baseline-written":
        print(
            f"doc baseline written: {payload.get('baseline')} ({payload.get('family_count')} families accepted)."
        )
        return
    total = payload.get("total_family_count", 0)
    new = payload["family_count"]
    accepted = payload.get("accepted_count", 0)
    print(
        f"nose doc-duplicate advisory: {new} new/changed Markdown family(ies) ({total} total, {accepted} accepted in baseline)."
    )
    if payload.get("baseline"):
        print(
            f"BASELINE: active ({payload['baseline']}); reporting only new/changed doc families (drift)."
        )
    for index, family in enumerate(payload["families"][:5], start=1):
        witness = family["witness"]
        print(
            f"ADVISORY: doc family #{index} (tier={family['tier']} score={family['score']} "
            f"files={family['files']} removable={family['removable']}): {witness['a']} <-> {witness['b']}"
        )
    interpretation = payload.get("interpretation")
    if isinstance(interpretation, dict):
        print(
            "INTERPRETATION (inference-layer proxy, not a verdict): "
            f"measures {interpretation['measures']}; proxy for "
            f"{interpretation['proxy_for']}; blind spots: {interpretation['blind_spots']}. "
            f"Consumer must answer first: {interpretation['interpretation_question']}"
        )


def summarize(payload: dict[str, Any], *, sample_limit: int = 5) -> dict[str, Any]:
    """Return the advisory status and a bounded family sample for triage."""
    families = payload.get("families", [])
    return {
        "summary_note": "summary is triage output; use --detail for full Markdown family evidence",
        "status": payload.get("status"),
        "advisory": payload.get("advisory"),
        "family_count": payload.get("family_count", 0),
        "total_family_count": payload.get("total_family_count", 0),
        "accepted_count": payload.get("accepted_count", 0),
        "families_sample": families[:sample_limit] if isinstance(families, list) else [],
        "notes": payload.get("notes", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repository root to scan and use for baseline paths",
    )
    parser.add_argument(
        "--path",
        help=(
            "Explicit repo-relative scan root (legacy default is "
            f"{DEFAULT_SCAN_PATH}); when omitted, scan the adapter's doc_surfaces."
        ),
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help=(
            "Gitignore-style glob to skip; repeatable. The default scan uses the "
            "adapter's doc_surfaces roots and adds no exclusions."
        ),
    )
    parser.add_argument(
        "--baseline",
        help=f"Accepted doc-family baseline (repo-relative). Defaults to {DEFAULT_BASELINE_REL} when it exists.",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write current doc families to the baseline and exit (accept today's state).",
    )
    parser.add_argument(
        "--require-nose",
        action="store_true",
        help=(
            "Fail closed (exit 1) when nose is missing, older than the required "
            ">=0.13.0 Markdown engine, or errors out (crash/timeout/invalid JSON). "
            "Findings themselves never block (advisory); this only enforces a "
            "healthy required tool so an absent or broken nose is not a silent "
            "all-clear. Used by the run-quality `doc-duplicates` phase."
        ),
    )
    add_output_args(
        parser,
        summary_help="Emit compact YAML advisory counts and bounded family samples",
        detail_help="Emit the full Markdown near-duplicate inventory as YAML",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    payload = payload_for_args(args)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if not emit_selected(payload, args, summarize=summarize):
        print_human(payload)
    if payload["status"] == "scope-refused":
        return 1
    if args.require_nose and payload["status"] in ("missing", "version-too-old", "error"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
