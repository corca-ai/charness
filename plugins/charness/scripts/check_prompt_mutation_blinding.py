#!/usr/bin/env python3
"""Read-only prompt-mutation post-capture blinding scan.

Scans captured prompt-mutation bundles for identity-relevant git history/ref
probes in ``trace-digest.jsonl`` and ``stream.jsonl``. Advisory only: it
reports taint, but never blocks a run.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from prompt_mutation_bundle_lib import iter_jsonl_dicts, tool_input_strings

GIT_PREFIX = r"\bgit\b(?:\s+(?:-[Cc]\s+\S+|--no-pager|-c\s+\S+))*\s+"

IDENTITY_PROBE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("git log", re.compile(GIT_PREFIX + r"log\b", re.IGNORECASE)),
    ("git show", re.compile(GIT_PREFIX + r"show\b", re.IGNORECASE)),
    ("git rev-parse", re.compile(GIT_PREFIX + r"rev-parse\b", re.IGNORECASE)),
    ("git reflog", re.compile(GIT_PREFIX + r"reflog\b", re.IGNORECASE)),
    ("git for-each-ref", re.compile(GIT_PREFIX + r"for-each-ref\b", re.IGNORECASE)),
    ("git show-ref", re.compile(GIT_PREFIX + r"show-ref\b", re.IGNORECASE)),
    ("git merge-base", re.compile(GIT_PREFIX + r"merge-base\b", re.IGNORECASE)),
    (
        "git diff",
        re.compile(
            GIT_PREFIX + r"diff\b.*(?:\bHEAD\b|\borigin/|\brefs/|\.\.|[0-9a-f]{7,40}\b)",
            re.IGNORECASE,
        ),
    ),
    ("git status --branch", re.compile(GIT_PREFIX + r"status\b.*(?:--branch|\s-b\b)", re.IGNORECASE)),
)


def _candidate_commands(record: dict) -> list[str]:
    commands: list[str] = []
    args = record.get("args")
    if isinstance(args, str):
        commands.append(args)
    commands.extend(tool_input_strings(record))
    return commands


def _classify_identity_probe(command: str) -> str | None:
    normalized = " ".join(command.split())
    for label, pattern in IDENTITY_PROBE_PATTERNS:
        if pattern.search(normalized):
            return label
    return None


def _scan_jsonl(path: Path, *, source: str, seen_commands: set[str]) -> list[dict]:
    hits: list[dict] = []
    for record in iter_jsonl_dicts(path) or []:
        for command in _candidate_commands(record):
            command = " ".join(command.split())
            if not command or command in seen_commands:
                continue
            seen_commands.add(command)
            risk = _classify_identity_probe(command)
            if risk is None:
                continue
            hit = {"source": source, "risk": "identity_probe", "command": command}
            for key in ("step", "track", "name"):
                value = record.get(key)
                if value is not None:
                    hit[key] = value
            hits.append(hit)
    return hits


def scan_bundle(bundle_dir: Path) -> dict[str, object]:
    """Scan one preserved run bundle for identity-relevant git history/ref probes."""
    trace_path = bundle_dir / "trace-digest.jsonl"
    stream_path = bundle_dir / "stream.jsonl"
    seen_commands: set[str] = set()
    hits = []
    if trace_path.is_file():
        hits.extend(_scan_jsonl(trace_path, source="trace-digest", seen_commands=seen_commands))
    if stream_path.is_file():
        hits.extend(_scan_jsonl(stream_path, source="stream.jsonl", seen_commands=seen_commands))
    return {
        "scope": "bundle",
        "bundle": str(bundle_dir),
        "tainted": bool(hits),
        "probe_count": len(hits),
        "evidence_files": [str(path.name) for path in (trace_path, stream_path) if path.is_file()],
        "hits": hits,
        "interpretation": (
            "Identity-relevant git history/ref probes were observed in this bundle; "
            "treat the run as tainted for the blinding claim."
            if hits
            else "No identity-relevant git history/ref probes were observed in this bundle."
        ),
    }


def _bundle_dirs_from_ab_dir(ab_dir: Path) -> list[Path]:
    results_path = ab_dir / "results.json"
    if results_path.is_file():
        try:
            payload = json.loads(results_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        runs = payload.get("runs", []) if isinstance(payload, dict) else []
        bundle_dirs = []
        for record in runs:
            if not isinstance(record, dict):
                continue
            arm = record.get("arm")
            run = record.get("run")
            if isinstance(arm, str) and isinstance(run, int):
                bundle_dirs.append(ab_dir / "preserved" / f"{arm}__{run}")
        if bundle_dirs:
            return bundle_dirs
    preserved = ab_dir / "preserved"
    if not preserved.is_dir():
        return []
    return sorted(path for path in preserved.iterdir() if path.is_dir())


def scan_ab_dir(ab_dir: Path) -> dict[str, object]:
    """Scan every preserved bundle in one prompt-mutation A/B output dir."""
    bundle_reports = [scan_bundle(bundle_dir) for bundle_dir in _bundle_dirs_from_ab_dir(ab_dir)]
    tainted = [report for report in bundle_reports if report["tainted"]]
    return {
        "scope": "ab-dir",
        "ab_dir": str(ab_dir),
        "bundles": bundle_reports,
        "summary": {
            "runs": len(bundle_reports),
            "tainted_runs": len(tainted),
            "tainted_bundles": [report["bundle"] for report in tainted],
            "interpretation": (
                "Identity-relevant git history/ref probes were observed in one or more preserved runs; "
                "treat the capture set as tainted for the blinding claim."
                if tainted
                else "No identity-relevant git history/ref probes were observed in the preserved runs."
            ),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Advisory prompt-mutation post-capture blinding scan: scan captured bundles for identity-relevant "
            "git history/ref probes. Never blocks a run."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bundle-dir", type=Path, help="Scan one preserved run bundle.")
    group.add_argument("--ab-dir", type=Path, help="Scan every preserved bundle under one A/B results dir.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.bundle_dir is not None:
        report = scan_bundle(args.bundle_dir.resolve())
    else:
        report = scan_ab_dir(args.ab_dir.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
