#!/usr/bin/env python3
"""Run the advisory nose clone-family inventory for quality review."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_output_lib import add_output_args, emit_selected  # noqa: E402


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


_SKILL_RUNTIME = _load_skill_runtime_bootstrap()
nose_baseline = _SKILL_RUNTIME.load_local_skill_module(__file__, "nose_baseline_lib")
nose_report = _SKILL_RUNTIME.load_local_skill_module(__file__, "nose_report_lib")
nose_fingerprint = _SKILL_RUNTIME.load_local_skill_module(__file__, "nose_fingerprint_lib")
nose_tool = _SKILL_RUNTIME.load_local_skill_module(__file__, "nose_tool_lib")
nose_scope = _SKILL_RUNTIME.load_local_skill_module(__file__, "nose_inventory_scope_lib")

DEFAULT_BASELINE_REL = nose_baseline.DEFAULT_BASELINE_REL
DEFAULT_PATHS = nose_scope.DEFAULT_PATHS
DEFAULT_MODE = "syntax,semantic,near"
WRITE_BASELINE_TOP = nose_scope.WRITE_BASELINE_TOP
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


def resolve_nose_bin() -> str | None:
    return nose_tool.resolve_nose_bin()


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def payload_for_args(args: argparse.Namespace) -> dict[str, Any]:
    return nose_scope.payload_for_args(
        args,
        baseline=nose_baseline,
        report=nose_report,
        fingerprint=nose_fingerprint,
        load_repo_module=_SKILL_RUNTIME.load_repo_module_from_skill_script,
        script_path=__file__,
        resolve_nose_bin=resolve_nose_bin,
        interpretation=INTERPRETATION,
    )


cli_exit_code_for_payload = nose_scope.cli_exit_code_for_payload


def _print_non_scan(payload: dict[str, Any]) -> bool:
    status = payload["status"]
    if status == "missing":
        print("ADVISORY: nose missing; clone-family inventory skipped. Install per integrations/tools/nose.json.")
        if payload.get("missing_paths"):
            print(f"SCOPE: missing requested roots ({', '.join(payload['missing_paths'])}).")
        return True
    if status == "inapplicable":
        missing = ", ".join(str(path) for path in payload.get("missing_paths", [])) or "none"
        print(
            "ADVISORY: nose clone inventory inapplicable; no requested scan root exists. "
            f"missing_paths={missing}"
        )
        return True
    if status == "error":
        print(f"ADVISORY: nose inventory error; review manually. {payload.get('stderr', '')}")
        return True
    if status == "baseline-written":
        count = payload.get("code_family_count")
        suffix = f" ({count} code family_ids accepted)" if isinstance(count, int) else ""
        print(f"nose baseline written: {payload.get('baseline')}{suffix}.")
        return True
    return False


def print_human(payload: dict[str, Any]) -> None:
    if _print_non_scan(payload):
        return
    version_label = payload.get("tool_version") or "unknown"
    print(
        f"nose clone advisory (nose {version_label}): {payload['status']}; {payload['family_count']} families, "
        f"{payload['total_dup_lines']} duplicated lines in reported families."
    )
    if payload.get("version_skew"):
        print(f"WARNING: {payload['version_skew']}")
    ranking = payload.get("ranking")
    if isinstance(ranking, dict):
        total = ranking.get("total_families")
        shown = ranking.get("shown_families")
        if isinstance(total, int) and isinstance(shown, int) and total != shown:
            print(f"RANKING: showing {shown} of {total} ranked families.")
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
    if payload.get("scope_status") == "partial":
        print(
            "SCOPE: partial scan; missing requested roots are not covered. "
            f"scanned={', '.join(payload.get('scanned_paths', []))}; "
            f"missing={', '.join(payload.get('missing_paths', []))}"
        )
    for index, family in enumerate(payload["families"][:5], start=1):
        samples = ", ".join(
            f"{item['file']}:{item['start_line']}-{item['end_line']}" for item in family["sample_locations"][:3]
        )
        print(
            f"ADVISORY: nose family #{index}: members={family['members']} dup_lines={family['dup_lines']} "
            f"shared_lines={family['shared_lines']} params={family['params']} samples={samples}"
        )
    interpretation = payload.get("interpretation")
    if isinstance(interpretation, dict):
        print(
            "INTERPRETATION (inference-layer proxy, not a verdict): "
            f"measures {interpretation['measures']}; proxy for {interpretation['proxy_for']}; "
            f"blind spots: {interpretation['blind_spots']}. Consumer must answer first: "
            f"{interpretation['interpretation_question']}"
        )


def summarize(payload: dict[str, Any], *, sample_limit: int = 5) -> dict[str, Any]:
    families = payload.get("families", [])
    return {
        "summary_note": "summary is triage output; use --detail for all clone-family evidence",
        "status": payload["status"],
        "advisory": payload.get("advisory", True),
        "repo_root": payload.get("repo_root"),
        "paths": payload.get("paths", []),
        "requested_paths": payload.get("requested_paths", []),
        "scanned_paths": payload.get("scanned_paths", []),
        "missing_paths": payload.get("missing_paths", []),
        "scope_status": payload.get("scope_status"),
        "scope": payload.get("scope", {}),
        "baseline": payload.get("baseline"),
        "command": payload.get("command", ""),
        "exit_code": payload.get("exit_code", 0),
        "cli_exit_code": payload.get("cli_exit_code", 0),
        "stderr": payload.get("stderr", ""),
        "tool_version": payload.get("tool_version", ""),
        "family_count": payload.get("family_count", payload.get("code_family_count", 0)),
        "total_dup_lines": payload.get("total_dup_lines", 0),
        "version_skew": payload.get("version_skew"),
        "families_sample": families[:sample_limit] if isinstance(families, list) else [],
        "notes": payload.get("notes", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True, help="Repository root to scan and use for baseline paths")
    parser.add_argument("--path", action="append", default=[], help="Repo-relative path to scan; repeatable")
    parser.add_argument("--mode", default=DEFAULT_MODE, help="Comma-separated nose query channels to scan (default: syntax,semantic,near)")
    parser.add_argument("--min-size", type=int, default=24, help="Minimum token count for a clone family (default: 24)")
    parser.add_argument("--exclude", action="append", default=[], help="Gitignore-style glob to skip; repeatable")
    parser.add_argument("--ignore-file", help="Structured nose ignore file to apply")
    parser.add_argument("--threshold", type=float, default=0.70, help=argparse.SUPPRESS)
    parser.add_argument("--min-lines", type=int, default=18, help=argparse.SUPPRESS)
    parser.add_argument("--min-tokens", dest="min_size", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--top", type=int, default=20, help="Maximum ranked families to report normally (default: 20); --write-baseline ignores this limit and scans all families")
    parser.add_argument("--sort", default="extractability", choices=("extractability", "value", "sites"), help="Ranking field for reported families (extractability, value, or sites; default: extractability)")
    parser.add_argument("--baseline", help=f"Accepted-baseline file (repo-relative) of already-recorded families; only new/changed are reported. Defaults to {DEFAULT_BASELINE_REL} when it exists.")
    parser.add_argument("--write-baseline", action="store_true", help="Write current families to the baseline and exit (accept today's state); re-baseline per scanner version.")
    add_output_args(parser, summary_help="Emit compact YAML clone-family counts and samples for triage", detail_help="Emit the full clone-family advisory payload as YAML")
    args = parser.parse_args()
    payload = payload_for_args(args)
    cli_exit_code = cli_exit_code_for_payload(payload)
    payload["cli_exit_code"] = cli_exit_code
    if not emit_selected(payload, args, summarize=summarize):
        print_human(payload)
    return cli_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
