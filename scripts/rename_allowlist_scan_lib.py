from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Pattern

SCAN_SUFFIXES = {
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
    ".sh",
    ".toml",
    ".cfg",
    ".ini",
}


@dataclass
class Allowlist:
    file_paths: set[str] = field(default_factory=set)
    dir_prefixes: tuple[str, ...] = ()
    reasons: dict[str, str] = field(default_factory=dict)

    def covers(self, rel: str) -> bool:
        if rel in self.file_paths:
            return True
        return any(rel.startswith(prefix) for prefix in self.dir_prefixes)


def parse_allowlist(path: Path) -> Allowlist:
    files: set[str] = set()
    dirs: list[str] = []
    reasons: dict[str, str] = {}
    if not path.is_file():
        return Allowlist(set(), tuple(), {})
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise SystemExit(f"allowlist line missing tab-separated reason: {raw!r}")
        target, reason = line.split("\t", 1)
        target = target.strip()
        reason = reason.strip()
        if not target or not reason:
            raise SystemExit(f"allowlist entry malformed: {raw!r}")
        reasons[target] = reason
        if target.endswith("/"):
            dirs.append(target)
        else:
            files.add(target)
    return Allowlist(files, tuple(dirs), reasons)


def tracked_files(repo_root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"],
        cwd=str(repo_root),
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return out.splitlines()


def scan(repo_root: Path, allowlist: Allowlist, pattern: Pattern[str]) -> tuple[list[dict], list[dict]]:
    inside: list[dict] = []
    outside: list[dict] = []
    for rel in tracked_files(repo_root):
        path = repo_root / rel
        if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        hits: list[dict] = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in pattern.finditer(line):
                hits.append(
                    {
                        "line": line_no,
                        "match": match.group(0),
                        "snippet": line.strip(),
                    }
                )
        if not hits:
            continue
        record = {"path": rel, "count": len(hits), "hits": hits}
        if allowlist.covers(rel):
            inside.append(record)
        else:
            outside.append(record)
    return inside, outside


def render_text_report(validator_name: str, inside: list[dict], outside: list[dict], allowlist_path: Path) -> str:
    lines: list[str] = []
    lines.append(f"{validator_name} validator (allowlist: {allowlist_path})")
    lines.append(f"  inside-allowlist files: {len(inside)} ({sum(r['count'] for r in inside)} cites)")
    lines.append(f"  OUTSIDE-allowlist files: {len(outside)} ({sum(r['count'] for r in outside)} cites)")
    if outside:
        lines.append("")
        lines.append("Outside allowlist:")
        for record in outside:
            lines.append(f"  - {record['path']} ({record['count']} cites)")
            for hit in record["hits"][:3]:
                lines.append(f"      L{hit['line']}: {hit['snippet']}")
            if record["count"] > 3:
                lines.append(f"      ... ({record['count'] - 3} more)")
    return "\n".join(lines)


def render_json_report(allowlist_path: Path, inside: list[dict], outside: list[dict]) -> str:
    report = {
        "allowlist": str(allowlist_path),
        "inside_allowlist_files": len(inside),
        "outside_allowlist_files": len(outside),
        "inside_allowlist_cite_total": sum(r["count"] for r in inside),
        "outside_allowlist_cite_total": sum(r["count"] for r in outside),
        "outside_allowlist": outside,
        "status": "pass" if not outside else "fail",
    }
    return json.dumps(report, indent=2)


def run_validator(
    *,
    description: str,
    argv: Iterable[str] | None,
    pattern: Pattern[str],
    allowlist_default: str,
    validator_name: str,
) -> int:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="repository root to scan (default: cwd)",
    )
    parser.add_argument(
        "--allowlist",
        default=None,
        help=f"allowlist path (default: <repo-root>/{allowlist_default})",
    )
    parser.add_argument(
        "--json",
        dest="emit_json",
        action="store_true",
        help="emit JSON report instead of text",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo_root = Path(args.repo_root).resolve()
    allowlist_path = (
        Path(args.allowlist).resolve()
        if args.allowlist
        else (repo_root / allowlist_default)
    )
    allowlist = parse_allowlist(allowlist_path)
    inside, outside = scan(repo_root, allowlist, pattern)

    if args.emit_json:
        print(render_json_report(allowlist_path, inside, outside))
    else:
        print(render_text_report(validator_name, inside, outside, allowlist_path))

    return 0 if not outside else 1
