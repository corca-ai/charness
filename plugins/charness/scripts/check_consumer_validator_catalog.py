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
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
DEFAULT_CATALOG_REL = Path("skills/public/quality/references/consumer-validator-catalog.yaml")
DEFAULT_PACKAGE_ROOT_REL = Path("plugins/charness")
EXPECTED_CANDIDATE_PATTERNS = ("**/check_*.py", "**/validate_*.py")
EXPECTED_SCANNER_EXCLUSIONS = ("scripts/check_consumer_validator_catalog.py",)
DECISIONS = frozenset({"publish", "exclude"})

_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib.load_yaml_file
_yaml_output = import_repo_module(__file__, "scripts.yaml_output")
emit_yaml = _yaml_output.emit_yaml


class CatalogError(ValueError):
    """The catalog or the package inventory cannot support a trustworthy report."""


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
        _required_text(entry.get("purpose"), field="purpose", where=entry_where)
        invocation = _required_text(entry.get("invocation"), field="invocation", where=entry_where)
        expected_fragment = f"<plugin-root>/{path}"
        if expected_fragment not in invocation:
            raise CatalogError(
                f"{entry_where}: `invocation` must name the packaged path "
                f"`{expected_fragment}`"
            )
    declared[path] = entry


def validate_catalog(
    repo_root: Path,
    *,
    catalog_path: Path | None = None,
    package_root: Path | None = None,
) -> dict[str, Any]:
    """Validate completeness and return the report consumed by the CLI/tests."""

    root = repo_root.resolve()
    catalog = _load_catalog((catalog_path or (root / DEFAULT_CATALOG_REL)).resolve())
    package_dir = (package_root or (root / DEFAULT_PACKAGE_ROOT_REL)).resolve()
    package_rel = package_dir.relative_to(root).as_posix()
    catalog_path_value = (catalog_path or (root / DEFAULT_CATALOG_REL)).resolve()
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
    extra = sorted(set(declared) - discovered_set)
    if extra:
        raise CatalogError(
            f"{catalog_path_value}: catalog names non-packaged validator(s): "
            f"{', '.join(extra)}"
        )

    consumer_paths = sorted(
        path for path, entry in declared.items() if entry["consumer_facing"] is True
    )
    return {
        "status": "pass",
        "catalog_path": catalog_path_value.relative_to(root).as_posix(),
        "package_root": package_rel,
        "packaged_validator_count": len(discovered),
        "decision_count": len(declared),
        "consumer_facing_count": len(consumer_paths),
        "excluded_count": len(declared) - len(consumer_paths),
        "consumer_facing_validators": consumer_paths,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--catalog-path", type=Path, default=None)
    parser.add_argument("--package-root", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        report = validate_catalog(
            args.repo_root,
            catalog_path=args.catalog_path,
            package_root=args.package_root,
        )
    except (CatalogError, ValueError) as exc:
        print(f"status: fail\nerror: {exc}", file=sys.stderr)
        return 1
    emit_yaml(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
