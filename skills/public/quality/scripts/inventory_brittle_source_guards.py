#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_MIN_PATTERN_CHARS = 40


def _load_source_guard_scan_lib():
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "scripts" / "source_guard_scan_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("source_guard_scan_lib", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/source_guard_scan_lib.py not found")


_source_guard_scan_lib = _load_source_guard_scan_lib()
DEFAULT_SOURCE_GUARD_SCAN_ROOTS = _source_guard_scan_lib.DEFAULT_SOURCE_GUARD_SCAN_ROOTS
fixed_source_guard_rows = _source_guard_scan_lib.fixed_source_guard_rows


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def _looks_like_prose_line(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith(("#", "-", "*", "|", "```", ">", "<", "{", "}"))


def _hard_wrap_score(text: str) -> dict[str, int]:
    prose_lines = [line.rstrip() for line in text.splitlines() if _looks_like_prose_line(line)]
    wrapped_lines = [line for line in prose_lines if 60 <= len(line) <= 90]
    return {
        "prose_lines": len(prose_lines),
        "wrapped_lines": len(wrapped_lines),
    }


def _is_hard_wrapped(score: dict[str, int]) -> bool:
    if score["prose_lines"] < 3:
        return False
    return score["wrapped_lines"] >= 3 and score["wrapped_lines"] / score["prose_lines"] >= 0.4


def _source_guard_scan(repo_root: Path, scan_roots: list[Path]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    return fixed_source_guard_rows(repo_root, scan_roots)


def _policy_state(repo_root: Path) -> dict[str, Any]:
    agents = repo_root / "AGENTS.md"
    text = agents.read_text(encoding="utf-8", errors="replace") if agents.is_file() else ""
    has_policy = bool(re.search(r"semantic line|semantic-line|prose wrap|prose-wrap", text, re.IGNORECASE))
    enforcement_tools = sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / "scripts").glob("*prose*")
        if path.is_file()
    )
    return {
        "policy_declared": has_policy,
        "enforcement_tools": enforcement_tools,
        "policy_without_tool": has_policy and not enforcement_tools,
    }


def _finding_for_guard(repo_root: Path, guard: dict[str, str], min_pattern_chars: int) -> dict[str, Any]:
    target = repo_root / guard["target_path"]
    pattern = guard["pattern"]
    finding: dict[str, Any] = {
        **guard,
        "pattern_chars": len(pattern),
        "status": "ok",
        "hard_wrapped": False,
        "exact_found": False,
        "normalized_found": False,
        "recommendation": "",
    }
    if len(pattern) < min_pattern_chars:
        return finding
    if not target.is_file():
        finding["status"] = "missing_target"
        finding["recommendation"] = "Fix the source_guard target path before judging wrap fragility."
        return finding

    text = target.read_text(encoding="utf-8", errors="replace")
    score = _hard_wrap_score(text)
    hard_wrapped = _is_hard_wrapped(score)
    exact_found = pattern in text
    normalized_found = _normalize_whitespace(pattern) in _normalize_whitespace(text)
    finding.update(
        {
            "hard_wrapped": hard_wrapped,
            "exact_found": exact_found,
            "normalized_found": normalized_found,
            "wrap_score": score,
        }
    )
    if hard_wrapped and not exact_found and normalized_found:
        finding["status"] = "brittle"
        finding["recommendation"] = (
            "Prefer semantic line breaks in the target file, or make the matcher normalize whitespace."
        )
    elif hard_wrapped and exact_found:
        finding["status"] = "at_risk"
        finding["recommendation"] = (
            "The fixed pattern is currently intact but can break under column wrapping; prefer semantic line breaks."
        )
    elif not exact_found and normalized_found:
        finding["status"] = "normalization_needed"
        finding["recommendation"] = "The matcher must normalize whitespace or the target prose should be reformatted."
    return finding


def inventory(
    repo_root: Path,
    *,
    min_pattern_chars: int = DEFAULT_MIN_PATTERN_CHARS,
    scan_roots: list[Path] | None = None,
) -> dict[str, Any]:
    resolved_scan_roots = scan_roots if scan_roots is not None else list(DEFAULT_SOURCE_GUARD_SCAN_ROOTS)
    guards, warnings = _source_guard_scan(repo_root, resolved_scan_roots)
    findings = [_finding_for_guard(repo_root, guard, min_pattern_chars) for guard in guards]
    fragile = [finding for finding in findings if finding["status"] in {"brittle", "at_risk", "normalization_needed"}]
    return {
        "repo_root": str(repo_root),
        "min_pattern_chars": min_pattern_chars,
        "scan_roots": [root.as_posix() for root in resolved_scan_roots],
        "warnings": warnings,
        "summary": {
            "source_guard_count": len(findings),
            "fragile_count": len(fragile),
            "brittle_count": sum(1 for finding in findings if finding["status"] == "brittle"),
            "at_risk_count": sum(1 for finding in findings if finding["status"] == "at_risk"),
        },
        "policy": _policy_state(repo_root),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--min-pattern-chars", type=int, default=DEFAULT_MIN_PATTERN_CHARS)
    parser.add_argument(
        "--scan-root",
        action="append",
        type=Path,
        dest="scan_roots",
        help="Markdown file or directory to scan for source guards. Repeat to override the default bounded roots.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = inventory(
        args.repo_root.resolve(),
        min_pattern_chars=args.min_pattern_chars,
        scan_roots=args.scan_roots,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for finding in payload["findings"]:
            if finding["status"] != "ok":
                print(f"{finding['status']}: {finding['spec_path']}:{finding['line']} -> {finding['target_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
