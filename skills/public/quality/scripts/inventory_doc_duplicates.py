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
import hashlib
import json
import shlex
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nose_tool_lib as nose_tool  # noqa: E402
from summary_output_lib import add_output_args, emit_selected  # noqa: E402

DEFAULT_SCAN_PATH = "."
# Exclude the export mirror (every source doc would otherwise pair 1:1 with its
# plugin copy), durable artifacts, and the mutation scratch tree. nose already
# honors .gitignore on top of these.
DEFAULT_EXCLUDES = ("plugins/**", "charness-artifacts/**", "mutants/**")
DEFAULT_BASELINE_REL = "charness-artifacts/quality/doc-nose-baseline.json"
MIN_NOSE_VERSION = (0, 13, 0)
NOSE_TIMEOUT_SECONDS = nose_tool.NOSE_TIMEOUT_SECONDS

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


def family_signature(family: dict[str, Any]) -> str:
    """Stable identity for a Markdown family: sorted member ``path#heading``
    tuples. Headings survive line-number churn far better than spans, so a doc
    edit that shifts lines does not re-flag an already-accepted family.
    """
    parts: list[str] = []
    for member in family.get("members") or []:
        if isinstance(member, dict):
            path = str(member.get("path", "")).lstrip("./")
            heading = str(member.get("heading", ""))
            parts.append(f"{path}#{heading}")
    parts.sort()
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return digest[:16]


def build_command(nose_bin: str, scan_path: str, excludes: list[str]) -> list[str]:
    command = [nose_bin, "query", scan_path]
    for pattern in excludes:
        command.extend(["--exclude", pattern])
    command.extend(["--format", "json"])
    return command


def run_query(repo_root: Path, command: list[str]) -> dict[str, Any]:
    result = nose_tool.run_json_query(repo_root, command)
    if result.get("error_kind") == "timeout":
        return {"status": "error", "families": [], "stderr": f"nose timed out after {NOSE_TIMEOUT_SECONDS}s"}
    if result.get("error_kind") == "oserror":
        return {"status": "error", "families": [], "stderr": f"nose could not be executed: {result.get('error', '')}"}
    if result.get("error_kind") in {"invalid-json", "empty-output"}:
        # Name the actual kind: an empty stdout is a producer that printed nothing, which is
        # a different diagnosis from output that failed to parse.
        stderr = (
            "nose emitted no output; the scan produced nothing to read"
            if result.get("error_kind") == "empty-output"
            else f"nose returned invalid JSON: {result.get('error', 'unparseable stdout')}"
        )
        # Keep nose's own stderr: a nonzero exit with blank stdout reaches this branch, and
        # the diagnosis the operator needs is what nose printed, not just "no JSON".
        if result.get("stderr"):
            stderr = f"{stderr}; {result['stderr']}"
        return {"status": "error", "families": [], "stderr": stderr}
    if result["status"] == "error":
        return {"status": "error", "families": [], "stderr": result["stderr"]}
    payload = result["payload"]
    families = payload.get("markdown") if isinstance(payload, dict) else None
    if not isinstance(families, list):
        # Shape parity with the code arm's `nose_report_lib.report_shape_error`: a payload
        # whose Markdown family list the reader cannot key (renamed/future key, a
        # non-object report) establishes NO family set, so it is an error rather than zero
        # doc drift. Reading it as `[]` made a bumped nose render a clean doc advisory AND
        # a vacuously clean dup-ratchet doc arm — the doc-side twin of triage sweep S34.
        keys = ", ".join(sorted(str(key) for key in payload)[:8]) if isinstance(payload, dict) else "<not an object>"
        return {
            "status": "error", "families": [],
            "stderr": f"nose report declares no `markdown` family list (keys: {keys}); "
                      "the Markdown family set is unestablished",
        }
    return {
        "status": "ok",
        "families": families,
        "schema_version": payload.get("schema_version"),
        "stderr": result["stderr"],
    }


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
    signatures = sorted({family_signature(fam) for fam in families})
    payload = {
        "schema": 1,
        "tool": "nose-markdown",
        "note": (
            "Accepted (intentional/shared-template) Markdown duplicate families so "
            "the advisory reports only new/changed drift. Signature = sorted member "
            "path#heading tuples. Re-baseline per scanner version with --write-baseline; "
            "never treat the accepted count as a reduction target (see item 5 review)."
        ),
        "signatures": signatures,
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


def payload_for_args(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    scan_path = args.path or DEFAULT_SCAN_PATH
    excludes = list(args.exclude) if args.exclude else list(DEFAULT_EXCLUDES)
    baseline_rel = args.baseline or DEFAULT_BASELINE_REL
    nose_bin = resolve_nose_bin()
    if nose_bin is None:
        return {
            "status": "missing",
            "advisory": True,
            "repo_root": str(repo_root),
            "scan_path": scan_path,
            "excludes": excludes,
            "family_count": 0,
            "families": [],
            "notes": [
                "nose is REQUIRED (>=0.13.0) for doc near-duplicate review; install per integrations/tools/nose.json.",
                "The run-quality `nose` phase fails closed when the binary is absent; this advisory only reports.",
            ],
        }
    version = nose_version(nose_bin)
    if version is not None and version < MIN_NOSE_VERSION:
        want = ".".join(str(part) for part in MIN_NOSE_VERSION)
        have = ".".join(str(part) for part in version)
        return {
            "status": "version-too-old",
            "advisory": True,
            "repo_root": str(repo_root),
            "scan_path": scan_path,
            "excludes": excludes,
            "tool_version": have,
            "family_count": 0,
            "families": [],
            "notes": [
                f"nose {have} cannot detect Markdown families; doc near-duplicate review needs >= {want}.",
                "Update per integrations/tools/nose.json; an old nose silently reports zero doc families.",
            ],
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
    if status == "missing":
        print("ADVISORY: nose missing; doc near-duplicate inventory skipped. nose >=0.13.0 is required (integrations/tools/nose.json).")
        return
    if status == "version-too-old":
        print(f"ADVISORY: nose {payload.get('tool_version')} too old for Markdown families; need >=0.13.0 (integrations/tools/nose.json).")
        return
    if status == "error":
        print(f"ADVISORY: nose doc inventory error; review manually. {payload.get('stderr', '')}")
        return
    if status == "baseline-written":
        print(f"doc baseline written: {payload.get('baseline')} ({payload.get('family_count')} families accepted).")
        return
    total = payload.get("total_family_count", 0)
    new = payload["family_count"]
    accepted = payload.get("accepted_count", 0)
    print(f"nose doc-duplicate advisory: {new} new/changed Markdown family(ies) ({total} total, {accepted} accepted in baseline).")
    if payload.get("baseline"):
        print(f"BASELINE: active ({payload['baseline']}); reporting only new/changed doc families (drift).")
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
    parser.add_argument("--path", help=f"Repo-relative scan root (default {DEFAULT_SCAN_PATH}).")
    parser.add_argument("--exclude", action="append", default=[], help="Gitignore-style glob to skip; repeatable. Defaults to mirror/artifact/mutant excludes.")
    parser.add_argument("--baseline", help=f"Accepted doc-family baseline (repo-relative). Defaults to {DEFAULT_BASELINE_REL} when it exists.")
    parser.add_argument("--write-baseline", action="store_true", help="Write current doc families to the baseline and exit (accept today's state).")
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
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if not emit_selected(payload, args, summarize=summarize):
        print_human(payload)
    if args.require_nose and payload["status"] in ("missing", "version-too-old", "error"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
