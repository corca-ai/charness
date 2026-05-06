#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


def _load_adapter_lib():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "scripts" / "adapter_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("adapter_lib", candidate)
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/adapter_lib.py not found")


def _default_repo_root() -> Path:
    return next(
        (ancestor for ancestor in Path(__file__).resolve().parents if (ancestor / "packaging" / "charness.json").is_file()),
        Path.cwd(),
    )


REPO_ROOT = _default_repo_root()
load_yaml_file = _load_adapter_lib().load_yaml_file

DEFAULT_CONTRACT_PATH = Path(".agents/quality-adapter.yaml")
SKIP_DIRS = {".git", ".charness", ".pytest_cache", "node_modules"}


class InventoryError(Exception):
    pass

def _string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    raise InventoryError(f"{field} must be a list of strings")


def _load_contract(repo_root: Path, adapter_path: Path) -> dict[str, Any] | None:
    path = adapter_path if adapter_path.is_absolute() else repo_root / adapter_path
    if not path.is_file():
        return None
    raw = load_yaml_file(path)
    if not isinstance(raw, dict) or raw.get("domain_language_contract") is None:
        return None
    contract = raw.get("domain_language_contract")
    if not isinstance(contract, dict):
        raise InventoryError("domain_language_contract must be a mapping")
    return contract


def _matches_pattern(rel: str, pattern: str) -> bool:
    return fnmatch.fnmatch(rel, pattern) or ("/**/" in pattern and fnmatch.fnmatch(rel, pattern.replace("/**/", "/")))


def _iter_files(repo_root: Path, globs: list[str], exemption_globs: list[str]) -> list[Path]:
    matched: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if any(part in SKIP_DIRS for part in path.relative_to(repo_root).parts):
            continue
        if not any(_matches_pattern(rel, pattern) for pattern in exemption_globs) and any(
            _matches_pattern(rel, pattern) for pattern in globs
        ):
            matched.append(path)
    return sorted(set(matched))


def _count_term(text: str, term: str) -> int:
    if not term:
        return 0
    return len(re.findall(re.escape(term), text, flags=re.IGNORECASE))


def _scan_term(
    repo_root: Path,
    term: dict[str, Any],
    default_globs: list[str],
    default_exemption_globs: list[str],
) -> dict[str, Any]:
    term_id = term.get("id")
    canonical = term.get("canonical")
    if not isinstance(term_id, str) or not term_id:
        raise InventoryError("domain_language_contract.terms[].id must be a non-empty string")
    if not isinstance(canonical, str) or not canonical:
        raise InventoryError(f"domain_language_contract term `{term_id}` must declare non-empty canonical")

    allowed_aliases = _string_list(term.get("allowed_aliases"), f"domain_language_contract.{term_id}.allowed_aliases")
    deprecated_aliases = _string_list(
        term.get("deprecated_aliases"), f"domain_language_contract.{term_id}.deprecated_aliases"
    )
    surface_globs = _string_list(term.get("surface_globs"), f"domain_language_contract.{term_id}.surface_globs")
    exemption_globs = default_exemption_globs + _string_list(
        term.get("exemption_globs"), f"domain_language_contract.{term_id}.exemption_globs"
    )
    files = _iter_files(repo_root, surface_globs or default_globs, exemption_globs)

    file_rows: list[dict[str, Any]] = []
    deprecated_hits: list[dict[str, Any]] = []
    alias_only_hits: list[dict[str, Any]] = []
    canonical_total = 0
    allowed_total = 0
    deprecated_total = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        canonical_count = _count_term(text, canonical)
        allowed_counts = {alias: _count_term(text, alias) for alias in allowed_aliases}
        deprecated_counts = {alias: _count_term(text, alias) for alias in deprecated_aliases}
        canonical_total += canonical_count
        allowed_total += sum(allowed_counts.values())
        deprecated_total += sum(deprecated_counts.values())
        rel = path.relative_to(repo_root).as_posix()
        row = {
            "path": rel,
            "canonical_count": canonical_count,
            "allowed_alias_counts": allowed_counts,
            "deprecated_alias_counts": deprecated_counts,
        }
        if canonical_count or any(allowed_counts.values()) or any(deprecated_counts.values()):
            file_rows.append(row)
        for alias, count in deprecated_counts.items():
            if count:
                deprecated_hits.append({"path": rel, "alias": alias, "count": count})
        if canonical_count == 0 and any(allowed_counts.values()):
            alias_only_hits.append({"path": rel, "aliases": {alias: count for alias, count in allowed_counts.items() if count}})

    return {
        "id": term_id,
        "canonical": canonical,
        "surface_globs": surface_globs or default_globs,
        "canonical_total": canonical_total,
        "allowed_alias_total": allowed_total,
        "deprecated_alias_total": deprecated_total,
        "files_with_terms": file_rows,
        "deprecated_hits": deprecated_hits,
        "alias_only_hits": alias_only_hits,
    }


def build_inventory(repo_root: Path, adapter_path: Path) -> dict[str, Any]:
    contract = _load_contract(repo_root, adapter_path)
    if contract is None:
        return {"status": "unconfigured", "reason": "quality adapter does not declare domain_language_contract", "terms": [], "findings": []}
    terms = contract.get("terms")
    if not isinstance(terms, list):
        raise InventoryError("domain_language_contract.terms must be a list")
    default_globs = _string_list(contract.get("surface_globs"), "domain_language_contract.surface_globs")
    if not default_globs:
        default_globs = ["README.md", "docs/**/*.md", "skills/public/**/*.md"]
    default_exemption_globs = _string_list(contract.get("exemption_globs"), "domain_language_contract.exemption_globs")
    scanned_terms = [
        _scan_term(repo_root, term, default_globs, default_exemption_globs)
        for term in terms
        if isinstance(term, dict)
    ]
    if len(scanned_terms) != len(terms):
        raise InventoryError("domain_language_contract.terms must contain only mappings")

    findings: list[str] = []
    for scanned in scanned_terms:
        for hit in scanned["deprecated_hits"]:
            findings.append(
                f"{scanned['id']}: {hit['path']} uses deprecated alias `{hit['alias']}` ({hit['count']})"
            )
    return {
        "status": "fail" if findings else "ok",
        "contract_path": str(adapter_path),
        "terms": scanned_terms,
        "findings": findings,
    }


def render_report(report: dict[str, Any]) -> str:
    if report["status"] == "unconfigured":
        return "Ubiquitous-language inventory unconfigured; skipping advisory terminology scan."
    lines = [f"Ubiquitous-language inventory: {report['status']} ({len(report['terms'])} terms)."]
    if report["findings"]:
        lines.append("Deprecated terminology found:")
        lines.extend(f"- {finding}" for finding in report["findings"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = build_inventory(args.repo_root.resolve(), args.adapter)
    except InventoryError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        stream = sys.stderr if report["findings"] else sys.stdout
        stream.write(render_report(report) + "\n")
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
