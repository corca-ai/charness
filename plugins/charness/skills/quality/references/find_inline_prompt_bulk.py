#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from git_inventory_lib import visible_repo_files  # noqa: E402


def multiline_string_findings(path: Path, *, min_chars: int) -> list[dict[str, object]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    findings: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        value = node.value
        if "\n" not in value or len(value) < min_chars:
            continue
        findings.append(
            {
                "path": str(path),
                "line": getattr(node, "lineno", 1),
                "char_count": len(value),
                "preview": value.strip().splitlines()[0][:80],
            }
        )
    return findings


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _load_quality_adapter(repo_root: Path) -> dict[str, object]:
    resolver = Path(__file__).resolve().parents[1] / "scripts" / "resolve_adapter.py"
    namespace = runpy.run_path(str(resolver))
    return namespace["load_adapter"](repo_root)


def _adapter_prompt_policy(repo_root: Path) -> tuple[dict[str, object], dict[str, object]]:
    adapter = _load_quality_adapter(repo_root)
    data = adapter.get("data") if isinstance(adapter, dict) else {}
    policy = data.get("prompt_asset_policy") if isinstance(data, dict) else {}
    return adapter, policy if isinstance(policy, dict) else {}


def _summary_payload(payload: dict[str, object], *, limit: int) -> dict[str, object]:
    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        findings = []
    return {
        key: value
        for key, value in {
            **payload,
            "finding_count": len(findings),
            "findings_sample": findings[:limit],
        }.items()
        if key != "findings"
    }


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [entry for entry in value if isinstance(entry, str)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-glob", action="append", default=[])
    parser.add_argument("--exemption-glob", action="append", default=[])
    parser.add_argument("--min-multiline-chars", type=int)
    parser.add_argument(
        "--from-adapter",
        action="store_true",
        help="Use quality adapter prompt_asset_policy unless explicit CLI policy flags override it.",
    )
    parser.add_argument("--summary", action="store_true", help="Emit compact JSON with a findings sample.")
    parser.add_argument("--summary-limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter_payload: dict[str, object] | None = None
    adapter_policy: dict[str, object] = {}
    if args.from_adapter:
        adapter_payload, adapter_policy = _adapter_prompt_policy(repo_root)

    adapter_source_globs = _string_list(adapter_policy.get("source_globs"))
    adapter_exemption_globs = _string_list(adapter_policy.get("exemption_globs"))
    adapter_min_chars = adapter_policy.get("min_multiline_chars")

    source_globs = (
        args.source_glob
        or adapter_source_globs
        or ([] if args.from_adapter else ["**/*.py"])
    )
    exemptions = args.exemption_glob or adapter_exemption_globs
    min_chars = (
        args.min_multiline_chars
        if args.min_multiline_chars is not None
        else adapter_min_chars
        if args.from_adapter and isinstance(adapter_min_chars, int)
        else 400
    )
    visible_files = visible_repo_files(repo_root)
    findings: list[dict[str, object]] = []
    seen: set[Path] = set()
    for pattern in source_globs:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            if visible_files is not None and path not in visible_files:
                continue
            rendered = str(path.relative_to(repo_root))
            if matches_any(rendered, exemptions):
                continue
            findings.extend(
                {
                    **finding,
                    "path": rendered,
                }
                for finding in multiline_string_findings(path, min_chars=min_chars)
            )

    if args.source_glob:
        scope_classification = "scanned"
        scope_reason = "explicit --source-glob argument(s) supplied"
    elif args.from_adapter and source_globs:
        scope_classification = "scanned_from_adapter"
        scope_reason = "quality adapter prompt_asset_policy.source_globs supplied the scan scope"
    elif args.from_adapter:
        scope_classification = "adapter_policy_no_source_globs"
        scope_reason = "quality adapter prompt_asset_policy.source_globs is empty; scan is intentionally empty"
    else:
        scope_classification = "advisory_only_no_canonical_prompt_asset_roots"
        scope_reason = "default `**/*.py` scan; no canonical prompt_asset_roots were supplied via --source-glob, so findings are advisory-only"
    payload = {
        "repo_root": str(repo_root),
        "source_globs": source_globs,
        "exemption_globs": exemptions,
        "min_multiline_chars": min_chars,
        "scope_classification": scope_classification,
        "scope_reason": scope_reason,
        "findings": findings,
    }
    if adapter_payload is not None:
        payload["adapter"] = {
            "found": adapter_payload.get("found"),
            "valid": adapter_payload.get("valid"),
            "path": adapter_payload.get("path"),
            "errors": adapter_payload.get("errors", []),
            "warnings": adapter_payload.get("warnings", []),
        }
    if args.summary:
        print(json.dumps(_summary_payload(payload, limit=max(args.summary_limit, 0)), ensure_ascii=False, indent=2))
    elif args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if scope_classification.startswith("advisory_only"):
            print(f"scope_classification={scope_classification}: {scope_reason}")
        for finding in findings:
            print(f"{finding['path']}:{finding['line']} chars={finding['char_count']} {finding['preview']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
