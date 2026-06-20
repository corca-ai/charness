#!/usr/bin/env python3
"""Run the advisory nose clone-family inventory for quality review."""

from __future__ import annotations

import argparse
import json
import os
import runpy
import shlex
import shutil
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


_SKILL_RUNTIME = _load_skill_runtime_bootstrap()
nose_baseline = _SKILL_RUNTIME.load_local_skill_module(__file__, "nose_baseline_lib")
nose_report = _SKILL_RUNTIME.load_local_skill_module(__file__, "nose_report_lib")
DEFAULT_BASELINE_REL = nose_baseline.DEFAULT_BASELINE_REL

DEFAULT_PATHS = ("scripts", "skills/public", "skills/support")
# nose 0.5 makes --mode REPLACE the default channels (syntax,semantic) rather
# than add to them, so every channel we want must be listed explicitly.
# syntax+semantic+near is a superset of the 0.5 default, so this requests
# strictly more coverage, never less — no silent channel drop under 0.5.
DEFAULT_MODE = "syntax,semantic,near"
# A baseline must record EVERY family; the display `--top` would truncate the
# enumeration and leave the rest to re-flag as drift forever. Enumerate the full
# set when writing (high top=, no nose --baseline), independent of --top.
WRITE_BASELINE_TOP = 1_000_000


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def resolve_nose_bin() -> str | None:
    override = os.environ.get("NOSE_BIN")
    if override:
        return override
    return shutil.which("nose")


# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): this inference-layer proxy self-declares
# its blind spots and the question the consumer must answer before acting.
INTERPRETATION = {
    "measures": "lexical clone families (near-duplicate code spans) at/above the scan threshold",
    "proxy_for": "refactorable duplication debt that a shared helper could remove",
    "blind_spots": (
        "intentional per-skill-package boilerplate (e.g. resolve_adapter.py copied "
        "for portability) counts as duplication and inflates the line total; "
        "lexical, so it misses semantic duplication and over-counts deliberate copies"
    ),
    "interpretation_question": (
        "which of these families are intentional/portability boilerplate versus "
        "genuinely extractable debt for THIS repo?"
    ),
}


def _representative_command(nose_bin: str, roots: list[str], args: argparse.Namespace, excludes: list[str], ignore_file: str | None) -> str:
    """The actual `nose query` command. nose 0.14.0 `--root/-r` takes every scope
    root in one invocation, so this IS the single command the resolver runs."""
    return shlex.join(
        nose_report.build_query_command(
            nose_bin, roots or ["."], mode=args.mode, min_size=args.min_size, top=args.top,
            sort=args.sort, exclude=excludes, ignore_file=ignore_file,
        )
    )


def payload_for_args(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    roots = [str(path) for path in (args.path or DEFAULT_PATHS)]
    excludes = list(args.exclude or [])
    ignore_file = args.ignore_file
    baseline = nose_baseline.resolve_baseline(
        write_baseline=args.write_baseline, baseline=args.baseline, repo_root=repo_root
    )
    nose_bin = resolve_nose_bin()
    if nose_bin is None:
        return {
            "status": "missing",
            "advisory": True,
            "repo_root": str(repo_root),
            "paths": roots,
            "excludes": excludes,
            "ignore_file": ignore_file,
            "baseline": baseline,
            "scope": {},
            "ranking": {},
            "tool_version": "",
            "family_count": 0,
            "families": [],
            "notes": [
                "nose is missing; install per integrations/tools/nose.json to run the clone-family advisory.",
                "nose is now required (>=0.13.3): document near-duplicate review runs through inventory_doc_duplicates.py (Markdown families), not a difflib fallback.",
            ],
        }
    # Writing a baseline enumerates EVERY family (full top); a read uses the
    # display --top for ranking. A truncated write would re-flag the rest forever.
    scan_top = WRITE_BASELINE_TOP if args.write_baseline else args.top
    collected = nose_report.collect_families(
        repo_root, nose_bin, roots, mode=args.mode, min_size=args.min_size,
        top=scan_top, sort=args.sort, exclude=excludes, ignore_file=ignore_file,
    )
    command = _representative_command(nose_bin, roots, args, excludes, ignore_file)
    families = collected["families"]
    if args.write_baseline:
        if collected["status"] == "error":
            return {
                "status": "error", "advisory": True, "repo_root": str(repo_root),
                "paths": roots, "baseline": baseline, "command": command,
                "stderr": collected["stderr"],
                "notes": ["nose query errored; baseline not written. Review manually."],
            }
        ids = {nose_report.family_identity(family) for family in families}
        return nose_baseline.write_baseline_payload(
            repo_root, baseline, {fid for fid in ids if fid}, roots,
            tool_version=collected.get("tool_version", ""),
        )
    if collected["status"] == "error":
        return {
            "status": "error",
            "advisory": True,
            "repo_root": str(repo_root),
            "paths": roots,
            "excludes": excludes,
            "ignore_file": ignore_file,
            "baseline": baseline,
            "scope": collected.get("scope", {}),
            "ranking": {},
            "command": command,
            "exit_code": collected["exit_code"],
            "tool_version": collected.get("tool_version", ""),
            "family_count": 0,
            "families": [],
            "stderr": collected["stderr"],
            "notes": ["nose inventory error; review manually."],
        }
    baseline_ids = nose_baseline.load_baseline_ids(repo_root, baseline)
    if baseline_ids is not None:
        drift = [family for family in families if nose_report.family_identity(family) not in baseline_ids]
    else:
        drift = families
    summaries = [nose_report.family_summary(family) for family in drift]
    # Scanner-version skew: a baseline written under a different nose version makes
    # its accepted ids stale, so today's families read as drift even with zero new
    # duplication. Surface "re-baseline", not a flood of false findings.
    skew = (
        nose_report.tool_version_skew(
            nose_baseline.load_baseline_tool_version(repo_root, baseline),
            collected.get("tool_version", ""),
        )
        if baseline_ids is not None
        else None
    )
    notes = [
        "nose findings are refactoring candidates, not standing quality failures.",
        "Review only extractable non-bootstrap families before changing code; do not chase every reported family.",
        "Map each reviewed family to a structural response (machine-owned consistency for intentional duplication, owned extraction, generated-surface ownership, or design review) per the quality inventory-dispatch reference.",
        "Never treat total_dup_lines as a reduction target or a cross-scanner-version trend; re-baseline per scanner version.",
    ]
    if skew:
        notes.insert(0, f"WARNING: {skew}")
    return {
        "status": "findings" if summaries else "clean",
        "advisory": True,
        "repo_root": str(repo_root),
        "paths": roots,
        "excludes": excludes,
        "ignore_file": ignore_file,
        "baseline": baseline if baseline_ids is not None else None,
        "scope": collected.get("scope", {}),
        "ranking": collected.get("ranking", {}),
        "command": command,
        "exit_code": collected["exit_code"],
        "tool_version": collected.get("tool_version", ""),
        "version_skew": skew,
        "family_count": len(summaries),
        "total_dup_lines": sum(int(summary.get("dup_lines") or 0) for summary in summaries),
        "families": summaries,
        "stderr": collected["stderr"],
        "interpretation": dict(INTERPRETATION),
        "notes": notes,
    }


def print_human(payload: dict[str, Any]) -> None:
    status = payload["status"]
    if status == "missing":
        print("ADVISORY: nose missing; clone-family inventory skipped. Install per integrations/tools/nose.json.")
        return
    if status == "error":
        print(f"ADVISORY: nose inventory error; review manually. {payload.get('stderr', '')}")
        return
    if status == "baseline-written":
        count = payload.get("code_family_count")
        suffix = f" ({count} code family_ids accepted)" if isinstance(count, int) else ""
        print(f"nose baseline written: {payload.get('baseline')}{suffix}.")
        return
    version_label = payload.get("tool_version") or "unknown"
    print(
        f"nose clone advisory (nose {version_label}): {status}; {payload['family_count']} families, "
        f"{payload['total_dup_lines']} duplicated lines in reported families."
    )
    skew = payload.get("version_skew")
    if skew:
        print(f"WARNING: {skew}")
    ranking = payload.get("ranking")
    if isinstance(ranking, dict):
        total_families = ranking.get("total_families")
        shown_families = ranking.get("shown_families")
        if isinstance(total_families, int) and isinstance(shown_families, int) and total_families != shown_families:
            print(f"RANKING: showing {shown_families} of {total_families} ranked families.")
    baseline = payload.get("baseline")
    if baseline:
        print(
            f"BASELINE: active ({baseline}); reporting only new/changed families (drift). "
            "Accepted families are intentional/portability boilerplate; re-baseline per scanner version with --write-baseline."
        )
    excludes = payload.get("excludes")
    ignore_file = payload.get("ignore_file")
    if excludes or ignore_file:
        parts = []
        if excludes:
            parts.append(f"excludes={', '.join(str(pattern) for pattern in excludes)}")
        if ignore_file:
            parts.append(f"ignore_file={ignore_file}")
        print(f"SCOPE: filtered scan ({'; '.join(parts)}). Excluded findings are not resolved.")
    for index, family in enumerate(payload["families"][:5], start=1):
        samples = ", ".join(
            f"{item['file']}:{item['start_line']}-{item['end_line']}"
            for item in family["sample_locations"][:3]
        )
        print(
            f"ADVISORY: nose family #{index}: members={family['members']} "
            f"dup_lines={family['dup_lines']} shared_lines={family['shared_lines']} "
            f"params={family['params']} samples={samples}"
        )
    interpretation = payload.get("interpretation")
    if isinstance(interpretation, dict):
        print(
            "INTERPRETATION (inference-layer proxy, not a verdict): "
            f"measures {interpretation['measures']}; proxy for "
            f"{interpretation['proxy_for']}; blind spots: {interpretation['blind_spots']}. "
            f"Consumer must answer first: {interpretation['interpretation_question']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--path", action="append", default=[], help="Repo-relative path to scan; repeatable")
    parser.add_argument("--mode", default=DEFAULT_MODE)
    parser.add_argument("--min-size", type=int, default=24)
    parser.add_argument("--exclude", action="append", default=[], help="Gitignore-style glob to skip; repeatable")
    parser.add_argument("--ignore-file", help="Structured nose ignore file to apply")
    parser.add_argument("--threshold", type=float, default=0.70, help=argparse.SUPPRESS)
    parser.add_argument("--min-lines", type=int, default=18, help=argparse.SUPPRESS)
    parser.add_argument("--min-tokens", dest="min_size", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--sort", default="extractability", choices=("extractability", "value", "sites"))
    parser.add_argument("--baseline", help=f"Accepted-baseline file (repo-relative) of already-recorded families; only new/changed are reported. Defaults to {DEFAULT_BASELINE_REL} when it exists.")
    parser.add_argument("--write-baseline", action="store_true", help="Write current families to the baseline and exit (accept today's state); re-baseline per scanner version.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = payload_for_args(args)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_human(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
