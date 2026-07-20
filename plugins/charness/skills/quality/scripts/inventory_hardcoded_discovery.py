#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import discovery_filter_scan_lib as _scan_lib  # noqa: E402
from summary_output_lib import add_output_args, emit_selected  # noqa: E402

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): this is a lexical structural signal, so
# the inventory self-declares what it measures, its proxy, its blind spots, and
# the question the consumer must answer before acting.
INTERPRETATION = {
    "measures": "portable skill/script constants that hardcode a multi-language (2+ code-language-family) test/source-file discovery list, split into adapter-owned-or-marked boundaries and unmarked candidates",
    "proxy_for": "measurement-contract divergence risk: a polyglot discovery list baked into the portable body can omit a language the consuming repo actually uses, so the repo's real surface silently undercounts",
    "blind_spots": "lexical and name-based — it only sees Tuple/List/Set constants whose NAME advertises discovery (EXTENSION/SUFFIX/PATTERN/GLOB), so it misses discovery via inline literals, git ls-files pathspecs, dict or dynamic construction, or a differently-named constant; it flags only lists spanning 2+ of a FIXED code-language-family map, so a single-family list that omits a sibling extension (a JS-only list missing `.mjs` — the founding-bug shape at finer grain) and any extension outside the map (php/cs/swift/scala/…) read as non-polyglot and are NOT flagged; and it cannot tell an intentional language-scope from a real undercount — a `# discovery-boundary:` marker is trusted, never verified",
    "interpretation_question": "for each unmarked polyglot discovery list: should THIS surface be adapter-owned (the consuming repo declares its real test/source surface) or is a language-scoped boundary genuinely intentional and worth marking?",
}

SUMMARY_FIELDS = (
    "repo_root",
    "summary_note",
    "scan_roots",
    "summary",
    "unmarked_findings",
    "marked_findings_sample",
    "interpretation",
)
SUMMARY_SAMPLE_SIZE = 10
SUMMARY_NOTE = "summary is triage output; use --detail for every marked boundary site"


def inventory(repo_root: Path, scan_roots: list[str] | None = None) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    findings = _scan_lib.scan(repo_root, scan_roots)
    unmarked = [finding for finding in findings if not finding["marked_boundary"]]
    marked = [finding for finding in findings if finding["marked_boundary"]]
    advisory_findings = [
        {
            "type": "unowned_polyglot_discovery",
            "severity": "advisory",
            "path": finding["path"],
            "line": finding["line"],
            "constant": finding["constant"],
            "code_families": finding["code_families"],
            "message": (
                f"`{finding['constant']}` hardcodes a polyglot ({'+'.join(finding['code_families'])}) "
                "discovery list in a portable body."
            ),
            "recommended_action": (
                "Make this surface adapter-owned (let the consuming repo declare its real test/source "
                "surface) or add an inline `# discovery-boundary: <reason>` marker stating why the "
                "language scope is intentional."
            ),
        }
        for finding in unmarked
    ]
    return {
        "repo_root": str(repo_root),
        "scan_roots": list(scan_roots) if scan_roots is not None else list(_scan_lib.DEFAULT_SCAN_ROOTS),
        "summary": {
            "polyglot_discovery_sites": len(findings),
            "unmarked_count": len(unmarked),
            "marked_boundary_count": len(marked),
        },
        "unmarked_findings": advisory_findings,
        "marked_findings": marked,
        "findings": advisory_findings,
    }


def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    marked = payload.get("marked_findings", [])
    return {
        "repo_root": payload["repo_root"],
        "summary_note": SUMMARY_NOTE,
        "scan_roots": payload["scan_roots"],
        "summary": payload["summary"],
        "unmarked_findings": payload["unmarked_findings"],
        "marked_findings_sample": marked[:SUMMARY_SAMPLE_SIZE] if isinstance(marked, list) else [],
        "interpretation": payload.get("interpretation"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the hardcoded-discovery inventory")
    parser.add_argument(
        "--scan-root",
        action="append",
        type=str,
        dest="scan_roots",
        help="Repo-relative directory to scan. Repeat to override the default roots (skills/public, scripts).",
    )
    add_output_args(
        parser,
        summary_help="Emit compact YAML counts and unmarked candidates for triage",
        detail_help="Emit the full hardcoded-discovery inventory as YAML",
    )
    args = parser.parse_args()
    payload = inventory(args.repo_root.resolve(), args.scan_roots)
    payload["interpretation"] = dict(INTERPRETATION)
    if emit_selected(payload, args, summarize=summarize):
        return 0
    print(f"polyglot discovery sites: {payload['summary']['polyglot_discovery_sites']}")
    print(f"  unmarked (advisory): {payload['summary']['unmarked_count']}")
    print(f"  marked boundary: {payload['summary']['marked_boundary_count']}")
    for finding in payload["unmarked_findings"]:
        print(f"ADVISORY {finding['type']}: {finding['path']}:{finding['line']} {finding['constant']} -> {finding['recommended_action']}")
    interpretation = payload.get("interpretation")
    if isinstance(interpretation, dict):
        print(
            "INTERPRETATION (structural lexical signal, not a verdict): "
            f"measures {interpretation['measures']}; proxy for {interpretation['proxy_for']}; "
            f"blind spots: {interpretation['blind_spots']}. "
            f"Consumer must answer first: {interpretation['interpretation_question']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
