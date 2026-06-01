#!/usr/bin/env python3
"""Advisory scan for stale docs after deleting a public symbol (#259)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SYMBOL_RE = re.compile(r"^\s*(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)\b")
CONSTANT_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]{2,})\s*(?::[^=]+)?=")
DEFAULT_SCAN_ROOTS = ("docs", "skills")


@dataclass(frozen=True)
class Finding:
    symbol: str
    variant: str
    path: str
    line: int
    text: str

    def to_dict(self) -> dict[str, object]:
        return {
            "symbol": self.symbol,
            "variant": self.variant,
            "path": self.path,
            "line": self.line,
            "text": self.text,
        }


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def deleted_symbols(repo_root: Path) -> list[str]:
    proc = _git(repo_root, "diff", "--unified=0", "HEAD", "--", ":(glob)**/*.py", "*.py")
    if proc.returncode != 0:
        return []
    symbols: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.startswith("-") or line.startswith("---"):
            continue
        text = line[1:]
        for pattern in (SYMBOL_RE, CONSTANT_RE):
            match = pattern.match(text)
            if match:
                symbols.add(match.group(1))
    return sorted(symbols)


def symbol_variants(symbol: str) -> list[str]:
    stripped = symbol.strip("_")
    variants = {symbol, stripped}
    words = [part.lower() for part in stripped.split("_") if part]
    if words[:1] in (["is"], ["has"], ["should"]) and len(words) > 2:
        words = words[1:]
    if len(words) >= 2:
        variants.add(" ".join(words))
        variants.add("-".join(words))
        variants.add(" ".join(word.capitalize() for word in words))
        variants.add("-".join(word.capitalize() for word in words))
        if words[0] in {"non", "pre", "post"} and len(words) > 2:
            variants.add(f"{words[0]}-{ ' '.join(words[1:]) }")
            variants.add(f"{words[0].capitalize()}-{ ' '.join(word.capitalize() for word in words[1:]) }")
    return sorted(variant for variant in variants if variant)


def _tracked_scan_paths(repo_root: Path, scan_roots: list[str]) -> list[Path]:
    proc = _git(repo_root, "ls-files", "--", *scan_roots)
    if proc.returncode != 0:
        return []
    return [
        repo_root / line
        for line in proc.stdout.splitlines()
        if line.endswith((".md", ".txt", ".json", ".yaml", ".yml"))
    ]


def concept_variants(concept: str) -> list[str]:
    normalized = " ".join(concept.replace("_", " ").replace("-", " ").split())
    if not normalized:
        return []
    lower = normalized.lower()
    return sorted(
        {
            concept,
            normalized,
            lower,
            "-".join(lower.split()),
            " ".join(word.capitalize() for word in lower.split()),
            "-".join(word.capitalize() for word in lower.split()),
        }
    )


def find_residue(
    repo_root: Path,
    scan_roots: list[str] | None = None,
    *,
    symbols: list[str] | None = None,
    concepts: list[str] | None = None,
) -> list[Finding]:
    variants_by_symbol = {
        symbol: symbol_variants(symbol) for symbol in deleted_symbols(repo_root)
    }
    for symbol in symbols or []:
        variants_by_symbol[symbol] = symbol_variants(symbol)
    for concept in concepts or []:
        variants = concept_variants(concept)
        if variants:
            variants_by_symbol[concept] = variants
    findings: list[Finding] = []
    seen: set[tuple[str, str, int]] = set()
    for path in _tracked_scan_paths(repo_root, list(scan_roots or DEFAULT_SCAN_ROOTS)):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        relpath = path.relative_to(repo_root).as_posix()
        for number, line in enumerate(lines, start=1):
            lowered = line.lower()
            for symbol, variants in variants_by_symbol.items():
                for variant in variants:
                    haystack = lowered if variant.lower() == variant else line
                    needle = variant if haystack is line else variant.lower()
                    key = (symbol, relpath, number)
                    if needle in haystack and key not in seen:
                        findings.append(Finding(symbol, variant, relpath, number, line.strip()))
                        seen.add(key)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Warn when deleted public symbols still appear in docs/skills prose."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--scan-root", action="append", default=[])
    parser.add_argument("--symbol", action="append", default=[], help="Also scan for an explicitly named deleted symbol.")
    parser.add_argument("--concept", action="append", default=[], help="Also scan for an explicitly named deleted concept.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    findings = find_residue(
        args.repo_root.resolve(),
        args.scan_root or None,
        symbols=args.symbol,
        concepts=args.concept,
    )
    if args.json:
        print(json.dumps({"finding_count": len(findings), "findings": [f.to_dict() for f in findings]}, indent=2))
        return 0
    if not findings:
        print("symbol-residue advisory: clean")
        return 0
    print(f"symbol-residue advisory: {len(findings)} possible stale reference(s)")
    for finding in findings:
        print(f"- {finding.path}:{finding.line}: {finding.symbol} via {finding.variant!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
