#!/usr/bin/env python3
"""Keep the packaged consumer-validator inventory explicit and discoverable.

The package contains two different kinds of validator-like scripts: validators a
consuming repository can run against its authored artifacts, and Charness's own
development/packaging gates.  A filename scan alone cannot tell those classes
apart, while a hand-maintained list of only the public class silently misses a
new candidate.  This gate therefore requires a decision for every packaged
candidate and exposes the consumer-facing subset through the catalog itself.

The scan boundary is deliberately owned by this checker, not by the catalog.
Allowing the data file to narrow its own candidate set would recreate the
under-enumeration defect this gate is meant to prevent.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
DEFAULT_CATALOG_REL = Path("skills/public/quality/references/consumer-validator-catalog.yaml")
DEFAULT_PACKAGE_ROOT_REL = Path("plugins/charness")
DEFAULT_ADOPTION_REL = Path(".agents/consumer-validator-adoption.yaml")
CATALOG_ID = "consumer-validator-catalog"
ADOPTION_POLICY = "wire-or-opt-out"
EXPECTED_CANDIDATE_PATTERNS = ("**/check_*.py", "**/validate_*.py")
EXPECTED_SCANNER_EXCLUSIONS = ("scripts/check_consumer_validator_catalog.py",)
DECISIONS = frozenset({"publish", "exclude"})
STABLE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib.load_yaml_file
_yaml_output = import_repo_module(__file__, "scripts.yaml_output")
emit_yaml = _yaml_output.emit_yaml


class CatalogError(ValueError):
    """The catalog or the package inventory cannot support a trustworthy report."""


def _layout_relative(repo_root: Path, source_relative: Path, installed_relative: Path) -> Path:
    """Select one source-vs-installed relative path without duplicating the probe."""

    return source_relative if (repo_root / "skills" / "public").is_dir() else installed_relative


def _default_catalog_rel(repo_root: Path) -> Path:
    """Select the catalog layout belonging to this source or installed package root."""

    return _layout_relative(
        repo_root,
        DEFAULT_CATALOG_REL,
        Path("skills/quality/references/consumer-validator-catalog.yaml"),
    )


def _default_package_root_rel(repo_root: Path) -> Path:
    """Select the packaged validator root in the source or installed layout."""

    return _layout_relative(repo_root, DEFAULT_PACKAGE_ROOT_REL, Path("."))


def discover_packaged_validators(package_root: Path) -> list[str]:
    """Return every packaged ``check_*.py`` or ``validate_*.py`` path."""

    if not package_root.is_dir():
        raise CatalogError(f"{package_root}: packaged plugin root is missing")
    return sorted(
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*.py")
        if path.is_file()
        and path.name.startswith(("check_", "validate_"))
        and path.relative_to(package_root).as_posix() not in EXPECTED_SCANNER_EXCLUSIONS
    )


def _required_text(value: Any, *, field: str, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{where}: `{field}` must be a non-empty string")
    return value.strip()


def _relative_catalog_path(value: Any, *, where: str) -> str:
    path = _required_text(value, field="path", where=where)
    parsed = PurePosixPath(path)
    if (
        parsed.is_absolute()
        or ".." in parsed.parts
        or "\\" in path
        or parsed.as_posix() != path
    ):
        raise CatalogError(f"{where}: `path` must be a normalized relative POSIX path")
    return path


def _load_catalog(catalog_path: Path) -> dict[str, Any]:
    if not catalog_path.is_file():
        raise CatalogError(f"{catalog_path}: consumer-validator catalog is missing")
    try:
        catalog = load_yaml_file(catalog_path)
    except (OSError, ValueError, TypeError) as exc:
        raise CatalogError(f"{catalog_path}: could not read catalog: {exc}") from exc
    if not isinstance(catalog, dict):
        raise CatalogError(f"{catalog_path}: top level must be a mapping")
    return catalog


def _validate_catalog_header(
    catalog: dict[str, Any], catalog_path: Path, package_rel: str
) -> list[dict[str, Any]]:
    if catalog.get("schema_version") != 1:
        raise CatalogError(f"{catalog_path}: `schema_version` must be integer 1")
    if catalog.get("catalog_id") != CATALOG_ID:
        raise CatalogError(f"{catalog_path}: `catalog_id` must be `{CATALOG_ID}`")
    if catalog.get("package_root") != package_rel:
        raise CatalogError(f"{catalog_path}: `package_root` must be `{package_rel}`")
    patterns = catalog.get("candidate_patterns")
    if patterns != list(EXPECTED_CANDIDATE_PATTERNS):
        raise CatalogError(
            f"{catalog_path}: `candidate_patterns` must be the fixed scanner scope "
            f"{list(EXPECTED_CANDIDATE_PATTERNS)!r}"
        )
    exclusions = catalog.get("scanner_exclusions")
    if not isinstance(exclusions, list) or [
        item.get("path") for item in exclusions if isinstance(item, dict)
    ] != list(EXPECTED_SCANNER_EXCLUSIONS):
        raise CatalogError(
            f"{catalog_path}: `scanner_exclusions` must explicitly name "
            f"{list(EXPECTED_SCANNER_EXCLUSIONS)!r}"
        )
    for index, item in enumerate(exclusions, start=1):
        if not isinstance(item, dict):
            raise CatalogError(f"{catalog_path}: scanner_exclusions[{index}] must be a mapping")
        _required_text(
            item.get("reason"),
            field="reason",
            where=f"{catalog_path}: scanner_exclusions[{index}]",
        )
    contract = catalog.get("consumer_contract")
    if not isinstance(contract, dict):
        raise CatalogError(f"{catalog_path}: `consumer_contract` must be a mapping")
    if contract.get("source") != "packaged":
        raise CatalogError(f"{catalog_path}: consumer contract `source` must be `packaged`")
    for field in ("selection_field", "no_substitute"):
        _required_text(contract.get(field), field=field, where=f"{catalog_path}: consumer_contract")
    policy = catalog.get("adoption_policy")
    if not isinstance(policy, dict):
        raise CatalogError(f"{catalog_path}: `adoption_policy` must be a mapping")
    if policy.get("declaration_path") != DEFAULT_ADOPTION_REL.as_posix():
        raise CatalogError(
            f"{catalog_path}: adoption declaration path must be `{DEFAULT_ADOPTION_REL.as_posix()}`"
        )
    if policy.get("exactly_one_of") != ["wired", "opt_out_reason"]:
        raise CatalogError(
            f"{catalog_path}: adoption policy must require exactly one of `wired` and `opt_out_reason`"
        )
    entries = catalog.get("validators")
    if not isinstance(entries, list):
        raise CatalogError(f"{catalog_path}: `validators` must be a list")
    return entries


def _validate_entry(
    entry: Any,
    *,
    index: int,
    catalog_path: Path,
    discovered: set[str],
    declared: dict[str, dict[str, Any]],
) -> None:
    where = f"{catalog_path}: validators[{index}]"
    if not isinstance(entry, dict):
        raise CatalogError(f"{where} must be a mapping")
    path = _relative_catalog_path(entry.get("path"), where=where)
    if path in declared:
        raise CatalogError(f"{where}: duplicate validator path `{path}`")
    if path not in discovered:
        raise CatalogError(f"{where}: `{path}` is not a packaged check_/validate_ script")
    consumer_facing = entry.get("consumer_facing")
    if type(consumer_facing) is not bool:
        raise CatalogError(f"{where} ({path}): `consumer_facing` must be an explicit boolean")
    decision = entry.get("decision")
    if decision not in DECISIONS:
        raise CatalogError(
            f"{where} ({path}): `decision` must be one of {sorted(DECISIONS)}"
        )
    expected_decision = "publish" if consumer_facing else "exclude"
    if decision != expected_decision:
        raise CatalogError(
            f"{where} ({path}): decision `{decision}` disagrees with "
            f"consumer_facing={consumer_facing!r}"
        )
    entry_where = f"{where} ({path})"
    _required_text(entry.get("reason"), field="reason", where=entry_where)
    if consumer_facing:
        validator_id = _required_text(entry.get("id"), field="id", where=entry_where)
        if not STABLE_ID_RE.fullmatch(validator_id):
            raise CatalogError(
                f"{entry_where}: `id` must be a stable lower-kebab-case identifier"
            )
        if any(item.get("id") == validator_id for item in declared.values()):
            raise CatalogError(f"{entry_where}: duplicate validator id `{validator_id}`")
        _required_text(entry.get("artifact_type"), field="artifact_type", where=entry_where)
        if entry.get("adoption_policy") != ADOPTION_POLICY:
            raise CatalogError(
                f"{entry_where}: `adoption_policy` must be `{ADOPTION_POLICY}`"
            )
        _required_text(entry.get("purpose"), field="purpose", where=entry_where)
        invocation = _required_text(entry.get("invocation"), field="invocation", where=entry_where)
        expected_command = f"<plugin-root>/{path}"
        try:
            invocation_tokens = shlex.split(invocation)
        except ValueError as exc:
            raise CatalogError(f"{entry_where}: `invocation` must be shell-tokenizable") from exc
        if len(invocation_tokens) < 2 or invocation_tokens[:2] != ["python3", expected_command]:
            raise CatalogError(
                f"{entry_where}: `invocation` must name the packaged path "
                f"as the command `python3 {expected_command}`"
            )
    declared[path] = entry


def _validate_adoption_entry(
    entry: Any,
    *,
    index: int,
    path: Path,
    expected_ids: set[str],
    seen: set[str],
) -> None:
    where = f"{path}: validators[{index}]"
    if not isinstance(entry, dict):
        raise CatalogError(f"{where} must be a mapping")
    validator_id = _required_text(entry.get("id"), field="id", where=where)
    if validator_id in seen:
        raise CatalogError(f"{where}: duplicate validator id `{validator_id}`")
    if validator_id not in expected_ids:
        raise CatalogError(f"{where}: `{validator_id}` is not a consumer-facing catalog id")
    seen.add(validator_id)
    has_wired = "wired" in entry
    has_opt_out = "opt_out_reason" in entry
    if has_wired == has_opt_out:
        raise CatalogError(
            f"{where} ({validator_id}): declare exactly one of `wired` or `opt_out_reason`"
        )
    if has_wired and entry.get("wired") is not True:
        raise CatalogError(f"{where} ({validator_id}): `wired` must be true when declared")
    if has_opt_out:
        _required_text(
            entry.get("opt_out_reason"),
            field="opt_out_reason",
            where=f"{where} ({validator_id})",
        )


def _require_staged_adoption(repo_root: Path, path: Path) -> None:
    """Require the declaration to be present in the index for commit-time checks."""

    try:
        relative = path.relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise CatalogError(f"{path}: adoption declaration must be inside the repo root") from exc
    try:
        staged = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "--cached", "--error-unmatch", "--", relative],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise CatalogError(f"{path}: could not verify staged adoption declaration: {exc}") from exc
    if staged.returncode != 0:
        raise CatalogError(f"{path}: adoption declaration must be staged with the catalog contract")


def _adoption_decisions(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    for entry in sorted(entries, key=lambda item: item["id"]):
        if entry.get("wired") is True:
            decisions.append({"id": entry["id"], "wired": True})
        else:
            decisions.append({"id": entry["id"], "opt_out_reason": entry["opt_out_reason"]})
    return decisions


def validate_adoption(
    repo_root: Path,
    *,
    declared: dict[str, dict[str, Any]],
    adoption_path: Path,
    required: bool,
    require_staged: bool = False,
) -> dict[str, Any]:
    """Validate one consuming repo's explicit adoption decisions."""

    root = repo_root.resolve()
    if not adoption_path.is_absolute():
        raw = PurePosixPath(adoption_path.as_posix())
        if raw.as_posix() != DEFAULT_ADOPTION_REL.as_posix() or ".." in raw.parts:
            raise CatalogError(
                f"{adoption_path}: adoption path must be `{DEFAULT_ADOPTION_REL.as_posix()}`"
            )
    path = (adoption_path if adoption_path.is_absolute() else root / adoption_path).resolve()
    expected_parts = DEFAULT_ADOPTION_REL.parts
    if path.parts[-len(expected_parts) :] != expected_parts:
        raise CatalogError(
            f"{path}: adoption path must end with `{DEFAULT_ADOPTION_REL.as_posix()}`"
        )
    try:
        display_path = path.relative_to(root).as_posix()
    except ValueError:
        # The catalog owner and the consuming repo are different roots in an
        # installed invocation. The declaration contract is intentionally a
        # stable repo-relative name even when the caller passed an absolute path.
        display_path = DEFAULT_ADOPTION_REL.as_posix()
    if not path.is_file():
        if required:
            raise CatalogError(f"{path}: consumer-validator adoption declaration is missing")
        return {
            "status": "not_configured",
            "adoption_path": display_path,
            "reason": "consumer has not declared wired validators or explicit opt-outs",
        }
    if require_staged:
        _require_staged_adoption(root, path)
    adoption = _load_catalog(path)
    if adoption.get("schema_version") != 1:
        raise CatalogError(f"{path}: `schema_version` must be integer 1")
    if adoption.get("catalog_id") != CATALOG_ID:
        raise CatalogError(f"{path}: `catalog_id` must be `{CATALOG_ID}`")
    entries = adoption.get("validators")
    if not isinstance(entries, list):
        raise CatalogError(f"{path}: `validators` must be a list")

    expected_ids = {
        entry["id"] for entry in declared.values() if entry.get("consumer_facing") is True
    }
    seen: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        _validate_adoption_entry(
            entry,
            index=index,
            path=path,
            expected_ids=expected_ids,
            seen=seen,
        )
    missing = sorted(expected_ids - seen)
    if missing:
        raise CatalogError(
            f"{path}: consumer-facing validator(s) missing an adoption decision: {', '.join(missing)}"
        )
    wired = sorted(entry["id"] for entry in entries if entry.get("wired") is True)
    opted_out = sorted(entry["id"] for entry in entries if "opt_out_reason" in entry)
    return {
        "status": "pass",
        "adoption_path": display_path,
        "declared_count": len(entries),
        "wired_count": len(wired),
        "opt_out_count": len(opted_out),
        "wired": wired,
        "opted_out": opted_out,
        "decisions": _adoption_decisions(entries),
    }


def validate_catalog(
    repo_root: Path,
    *,
    catalog_path: Path | None = None,
    package_root: Path | None = None,
    adoption_path: Path | None = None,
    require_adoption: bool = False,
    require_staged_adoption: bool = False,
) -> dict[str, Any]:
    """Validate completeness and return the report consumed by the CLI/tests."""

    root = repo_root.resolve()
    default_catalog = _default_catalog_rel(root)
    default_package_root = _default_package_root_rel(root)
    catalog = _load_catalog((catalog_path or (root / default_catalog)).resolve())
    package_dir = (package_root or (root / default_package_root)).resolve()
    package_rel = package_dir.relative_to(root).as_posix()
    catalog_path_value = (catalog_path or (root / default_catalog)).resolve()
    entries = _validate_catalog_header(catalog, catalog_path_value, package_rel)

    discovered = discover_packaged_validators(package_dir)
    discovered_set = set(discovered)
    declared: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries, start=1):
        _validate_entry(
            entry,
            index=index,
            catalog_path=catalog_path_value,
            discovered=discovered_set,
            declared=declared,
        )

    missing = sorted(discovered_set - set(declared))
    if missing:
        raise CatalogError(
            f"{catalog_path_value}: packaged validator(s) missing an explicit catalog "
            f"decision: {', '.join(missing)}"
        )
    consumer_paths = sorted(
        path for path, entry in declared.items() if entry["consumer_facing"] is True
    )
    consumer_entries = [
        {
            field: entry[field]
            for field in (
                "id",
                "path",
                "purpose",
                "artifact_type",
                "invocation",
                "adoption_policy",
            )
        }
        for path, entry in sorted(declared.items())
        if entry["consumer_facing"] is True
    ]
    report: dict[str, Any] = {
        "status": "pass",
        "catalog_id": catalog.get("catalog_id"),
        "catalog_path": catalog_path_value.relative_to(root).as_posix(),
        "package_root": package_rel,
        "packaged_validator_count": len(discovered),
        "decision_count": len(declared),
        "consumer_facing_count": len(consumer_paths),
        "excluded_count": len(declared) - len(consumer_paths),
        "consumer_facing_validators": consumer_paths,
        "consumer_validator_entries": consumer_entries,
        "consumer_validator_ids": sorted(
            entry["id"] for entry in declared.values() if entry["consumer_facing"] is True
        ),
    }
    if adoption_path is not None:
        report["adoption"] = validate_adoption(
            root,
            declared=declared,
            adoption_path=adoption_path,
            required=require_adoption,
            require_staged=require_staged_adoption,
        )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--catalog-path", type=Path, default=None)
    parser.add_argument("--package-root", type=Path, default=None)
    parser.add_argument("--adoption-path", type=Path, default=None)
    parser.add_argument("--require-adoption", action="store_true")
    parser.add_argument("--require-staged-adoption", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = validate_catalog(
            args.repo_root,
            catalog_path=args.catalog_path,
            package_root=args.package_root,
            adoption_path=args.adoption_path,
            require_adoption=args.require_adoption,
            require_staged_adoption=args.require_staged_adoption,
        )
    except (CatalogError, ValueError) as exc:
        print(f"status: fail\nerror: {exc}", file=sys.stderr)
        return 1
    emit_yaml(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
