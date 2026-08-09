#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_summary_output = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).with_name("summary_output_lib.py")))
)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_inventory_lib import visible_repo_files  # noqa: E402


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
_ADAPTER_LIB = _load_adapter_lib()
load_yaml_file = _ADAPTER_LIB.load_yaml_file
validate_adapter_version = _ADAPTER_LIB.validate_adapter_version

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
    # The shared loader always returns a mapping; a list- or scalar-shaped file reads as
    # empty, which falls through the version check and the contract check below.
    raw = load_yaml_file(path)
    # The contract selects the scan scope and its exemptions, so honoring it from a schema
    # version this reader never reconciled is the fail-open shape every adapter reader
    # here owes a verdict on. Refuse loudly rather than silently inventorying an
    # attacker- or typo-selected scope.
    version_errors: list[str] = []
    validate_adapter_version(raw, {}, version_errors)
    if version_errors:
        raise InventoryError(
            f"{adapter_path}: " + "; ".join(version_errors) + "; domain_language_contract was not read"
        )
    if raw.get("domain_language_contract") is None:
        return None
    contract = raw.get("domain_language_contract")
    if not isinstance(contract, dict):
        raise InventoryError("domain_language_contract must be a mapping")
    return contract


def _matches_pattern(rel: str, pattern: str) -> bool:
    return fnmatch.fnmatch(rel, pattern) or ("/**/" in pattern and fnmatch.fnmatch(rel, pattern.replace("/**/", "/")))


def _iter_files_with_scope(
    repo_root: Path, globs: list[str], exemption_globs: list[str]
) -> tuple[list[Path], int, dict[str, int]]:
    """Files to scan, how many the globs matched BEFORE exemptions, and per pattern.

    The second number is what separates "this glob is wrong" from "everything it
    matched was deliberately exempted". Without it, an exemption that legitimately
    empties a term's scope reads identically to a typo'd glob, and the S32 repair
    would have refused on the repo's own `adapter-contract.md` exemption.

    The third is per-PATTERN, because the aggregate hides the likelier real-world
    shape: this repo declares six globs, and one typo among them leaves the total
    nonzero while that surface silently stops being read (round 1, MINOR 4).
    """
    matched: list[Path] = []
    matched_before_exemption = 0
    # Deduped: `per_pattern` is keyed by pattern string, so a list repeating a glob
    # counted its files once per occurrence in the raw list.
    globs = list(dict.fromkeys(globs))
    per_pattern = {pattern: 0 for pattern in globs}
    # Same owner as the sibling inventories: `visible_repo_files` answers "which
    # files does git list", and hand-rolling it here was a duplicate family.
    visible = visible_repo_files(repo_root, context="ubiquitous-language file listing")
    candidates = sorted(visible) if visible is not None else list(repo_root.rglob("*"))
    for path in candidates:
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if any(part in SKIP_DIRS for part in path.relative_to(repo_root).parts):
            continue
        hit = [pattern for pattern in globs if _matches_pattern(rel, pattern)]
        if not hit:
            continue
        for pattern in hit:
            per_pattern[pattern] += 1
        matched_before_exemption += 1
        if not any(_matches_pattern(rel, pattern) for pattern in exemption_globs):
            matched.append(path)
    return sorted(set(matched)), matched_before_exemption, per_pattern


def _count_term(text: str, term: str) -> int:
    if not term:
        return 0
    return len(re.findall(re.escape(term), text, flags=re.IGNORECASE))


def _scan_term(
    repo_root: Path,
    term: dict[str, Any],
    default_globs: list[str],
    default_exemption_globs: list[str],
    default_files: list[Path],
    default_matched_before_exemption: int,
    default_per_pattern: dict[str, int],
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
    # `key: []` is a DECLARED empty scope; `key absent` is no declaration at all.
    # Collapsing them silently handed the term the contract-level or built-in
    # scope and then reported `surface_globs` it never declared (round 1, MINOR 7).
    surface_globs_declared_empty = "surface_globs" in term and not surface_globs
    exemption_globs = default_exemption_globs + _string_list(
        term.get("exemption_globs"), f"domain_language_contract.{term_id}.exemption_globs"
    )
    if not surface_globs and exemption_globs == default_exemption_globs:
        files = default_files
        matched_before_exemption = default_matched_before_exemption
        per_pattern = dict(default_per_pattern)
    else:
        files, matched_before_exemption, per_pattern = _iter_files_with_scope(
            repo_root, surface_globs or default_globs, exemption_globs
        )

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
        # The denominator, kept as a value. A typo'd glob (`doc/**/*.md` for
        # `docs/**/*.md`) scanned zero files and the term reported clean — a
        # deprecated alias sitting three times in a real doc was invisible, and
        # nothing in the output distinguished "no hits" from "nothing read" (S32).
        "files_scanned": len(files),
        # Zero here with a nonzero `files_matched_before_exemption` means the
        # exemptions emptied the scope deliberately; zero on BOTH means the globs
        # read nothing at all, which is the S32 defect.
        "files_matched_before_exemption": matched_before_exemption,
        "matches_per_glob": per_pattern,
        "globs_matching_nothing": sorted(
            pattern for pattern, count in per_pattern.items() if not count
        ),
        "scope_declared": bool(surface_globs),
        "scope_declared_empty": surface_globs_declared_empty,
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
        # Every status carries every list key: `--detail` emits the raw payload, so
        # a consumer reading `report["scope_findings"]` must not KeyError on exactly
        # one status (round 1, MINOR 8).
        return {
            "status": "unconfigured",
            "reason": "quality adapter does not declare domain_language_contract",
            "terms": [],
            "findings": [],
            "scope_findings": [],
            "scope_advisories": [],
        }
    terms = contract.get("terms")
    if not isinstance(terms, list):
        raise InventoryError("domain_language_contract.terms must be a list")
    default_globs = _string_list(contract.get("surface_globs"), "domain_language_contract.surface_globs")
    # A contract that DECLARES its surfaces asserted a scope; the built-in fallback
    # is discovery. The two must not answer an empty scan the same way.
    default_scope_declared = bool(default_globs)
    if not default_globs:
        default_globs = ["README.md", "docs/**/*.md", "skills/public/**/*.md"]
    default_exemption_globs = _string_list(contract.get("exemption_globs"), "domain_language_contract.exemption_globs")
    default_files, default_matched_before_exemption, default_per_pattern = _iter_files_with_scope(
        repo_root, default_globs, default_exemption_globs
    )
    scanned_terms = [
        _scan_term(
            repo_root,
            term,
            default_globs,
            default_exemption_globs,
            default_files,
            default_matched_before_exemption,
            default_per_pattern,
        )
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
    # A term whose DECLARED globs read nothing is an unestablished verdict, not a
    # clean one. Kept in its own list because it is a different defect from a
    # deprecated alias: the contract is wrong, not the prose.
    scope_findings: list[str] = []
    # Statements, not refusals: a scope emptied by a deliberate exemption, and a
    # partially-dead glob list, are both honest configurations. They must still be
    # SAID — round 1 caught the exemption-emptied pass being wholly silent, which
    # is the same "green that names no scope" this repair exists to remove.
    scope_advisories: list[str] = []
    for scanned in scanned_terms:
        # Which key is actually wrong: a term that declared nothing inherits the
        # contract-level globs, and blaming the term sends the operator to the
        # wrong line (round 1, MINOR 6).
        owner = (
            f"domain_language_contract.{scanned['id']}.surface_globs"
            if scanned["scope_declared"]
            else "domain_language_contract.surface_globs"
        )
        globs_text = ", ".join(str(glob) for glob in scanned["surface_globs"])
        if scanned["scope_declared_empty"]:
            # NOT `owner`: `scope_declared` is False for exactly this case (the list
            # is empty, so `bool(surface_globs)` is False), so `owner` would name the
            # CONTRACT-level key — a false statement, with a remedy that does not
            # clear the failure and silently drops every other term to the built-in
            # fallback. Round 2 caught these two round-1 repairs colliding.
            scope_findings.append(
                f"{scanned['id']}: domain_language_contract.{scanned['id']}.surface_globs "
                "is declared EMPTY, so this term names no surface at all and was scanned "
                "against the inherited scope instead. Remedy: declare the globs this term "
                "governs, or delete the key so the inheritance is explicit."
            )
            continue
        if not scanned["files_matched_before_exemption"] and (
            scanned["scope_declared"] or default_scope_declared
        ):
            scope_findings.append(
                f"{scanned['id']}: declared surface_globs {globs_text} matched no file; "
                "this term was never scanned, so its clean result establishes nothing. "
                f"Remedy: correct {owner} to name a path that exists, or remove the term."
            )
            continue
        if not scanned["files_scanned"] and scanned["files_matched_before_exemption"]:
            scope_advisories.append(
                f"{scanned['id']}: 0 file(s) read — "
                f"{scanned['files_matched_before_exemption']} matched {globs_text} and all "
                "were removed by exemption_globs. That is a deliberate configuration and "
                "stays a pass, but this term's clean result establishes nothing."
            )
        elif not scanned["files_scanned"]:
            # Nothing matched AND nothing was exempted. Round 2 caught the first cut
            # telling this operator that files "were removed by exemption_globs" when
            # none were configured — a fabricated cause on the built-in discovery
            # fallback, which is the shape an unconfigured consumer repo hits.
            scope_advisories.append(
                f"{scanned['id']}: 0 file(s) read — the built-in discovery scope "
                f"({globs_text}) matched no file in this repo, and no exemption was "
                "involved. Declare surface_globs if this term governs a real surface; "
                "until then its clean result establishes nothing."
            )
        elif scanned["globs_matching_nothing"]:
            scope_advisories.append(
                f"{scanned['id']}: glob(s) "
                f"{', '.join(scanned['globs_matching_nothing'])} in {owner} matched no file, "
                f"while others did ({scanned['files_scanned']} file(s) read). That surface is "
                "silently unread."
            )
    return {
        "status": "fail" if findings or scope_findings else "ok",
        "contract_path": str(adapter_path),
        "terms": scanned_terms,
        "findings": findings,
        "scope_findings": scope_findings,
        "scope_advisories": scope_advisories,
    }


def summarize_report(report: dict[str, Any], *, sample_limit: int = 10) -> dict[str, Any]:
    terms = report.get("terms", [])
    term_items = terms if isinstance(terms, list) else []
    return {
        "summary_note": "summary is triage output; use --detail for full per-file terminology counts",
        "status": report["status"],
        "contract_path": report.get("contract_path"),
        "reason": report.get("reason"),
        "term_count": len(term_items),
        "finding_count": len(report.get("findings", [])),
        "findings_sample": report.get("findings", [])[:sample_limit],
        "scope_finding_count": len(report.get("scope_findings", [])),
        "scope_findings_sample": report.get("scope_findings", [])[:sample_limit],
        "scope_advisory_count": len(report.get("scope_advisories", [])),
        "scope_advisories_sample": report.get("scope_advisories", [])[:sample_limit],
        "terms": [
            {
                "id": term.get("id"),
                "canonical": term.get("canonical"),
                "surface_globs": term.get("surface_globs", []),
                "canonical_total": term.get("canonical_total", 0),
                "allowed_alias_total": term.get("allowed_alias_total", 0),
                "deprecated_alias_total": term.get("deprecated_alias_total", 0),
                # The denominator, in the mode an operator actually reads. Without
                # it, `--summary` showed status ok / 0 findings for a scope that
                # read nothing at all (round 1, MINOR 3).
                "files_scanned": term.get("files_scanned"),
                "files_matched_before_exemption": term.get("files_matched_before_exemption"),
                "files_with_terms_count": len(term.get("files_with_terms", [])),
                "deprecated_hits_sample": term.get("deprecated_hits", [])[:sample_limit],
                "alias_only_hits_sample": term.get("alias_only_hits", [])[:sample_limit],
            }
            for term in term_items
            if isinstance(term, dict)
        ],
    }


def render_report(report: dict[str, Any]) -> str:
    if report["status"] == "unconfigured":
        return "Ubiquitous-language inventory unconfigured; skipping advisory terminology scan."
    lines = [f"Ubiquitous-language inventory: {report['status']} ({len(report['terms'])} terms)."]
    if report["findings"]:
        lines.append("Deprecated terminology found:")
        lines.extend(f"- {finding}" for finding in report["findings"])
    if report.get("scope_findings"):
        lines.append("Declared scope matched nothing (fix the contract, not the prose):")
        lines.extend(f"- {finding}" for finding in report["scope_findings"])
    if report.get("scope_advisories"):
        lines.append("Scope read less than it declared (not a failure, but not a full scan):")
        lines.extend(f"- {advisory}" for advisory in report["scope_advisories"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root for the ubiquitous-language terminology inventory")
    parser.add_argument("--adapter", type=Path, default=DEFAULT_CONTRACT_PATH, help="Quality adapter file declaring the domain_language_contract")
    _summary_output.add_output_args(
        parser,
        summary_help="Emit compact YAML totals and samples instead of full per-file counts",
        detail_help="Emit full per-file terminology counts as YAML",
    )
    args = parser.parse_args()

    try:
        report = build_inventory(args.repo_root.resolve(), args.adapter)
    except InventoryError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if not _summary_output.emit_selected(report, args, summarize=summarize_report):
        failed = bool(report["findings"] or report.get("scope_findings"))
        stream = sys.stderr if failed else sys.stdout
        stream.write(render_report(report) + "\n")
    return 1 if report["findings"] or report.get("scope_findings") else 0


if __name__ == "__main__":
    raise SystemExit(main())
