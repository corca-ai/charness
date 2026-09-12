#!/usr/bin/env python3
"""Require every detected temporary-output producer to have one disposition."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Iterable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_adapter = import_repo_module(__file__, "scripts.adapter_lib")
_lib = import_repo_module(__file__, "scripts.gates.temp_producer_inventory_lib")
load_yaml_file = _adapter.load_yaml_file
emit_yaml = import_repo_module(__file__, "scripts.yaml_output").emit_yaml
Producer = _lib.Producer
discover_producers = _lib.discover_producers

SCHEMA = "charness/temp-producers/v1"
DEFAULT_MANIFEST = Path(".agents") / "temp-producers.yaml"
DISPOSITIONS = frozenset(
    {
        "owned-scratch",
        "atomic-sibling",
        "anonymous-auto-delete-file",
        "bounded-runtime-cache",
        "durable-output",
        "test-compatibility-only",
    }
)


def load_manifest(repo_root: Path, path: Path = DEFAULT_MANIFEST) -> tuple[list[dict[str, Any]], list[str]]:
    manifest_path = path if path.is_absolute() else repo_root / path
    try:
        payload = load_yaml_file(manifest_path)
    except (OSError, ValueError) as exc:
        return [], [f"cannot read manifest {manifest_path}: {exc}"]
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        return [], [f"manifest schema must be {SCHEMA!r}: {manifest_path}"]
    rows = payload.get("producers")
    if not isinstance(rows, list):
        return [], ["manifest.producers must be a list"]
    errors: list[str] = []
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"manifest.producers[{index}] must be a mapping")
            continue
        identity = row.get("identity")
        if not isinstance(identity, str) or not identity:
            errors.append(f"manifest.producers[{index}].identity must be non-empty")
            continue
        if identity in seen:
            errors.append(f"manifest has duplicate identity {identity!r}")
        seen.add(identity)
        disposition = row.get("disposition")
        if disposition not in DISPOSITIONS:
            errors.append(f"manifest.producers[{index}] {identity!r} has invalid disposition {disposition!r}")
        for field in ("path", "symbol", "rationale"):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"manifest.producers[{index}] {identity!r} must name {field}")
        result.append(row)
    return result, errors


def validate_inventory(
    repo_root: Path,
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    require_git: bool = False,
    producers: Iterable[Producer] | None = None,
) -> dict[str, Any]:
    detected = list(discover_producers(repo_root, require_git=require_git) if producers is None else producers)
    rows, errors = load_manifest(repo_root, manifest_path)
    detected_by_id: dict[str, list[Producer]] = {}
    for producer in detected:
        detected_by_id.setdefault(producer.identity, []).append(producer)
    declared = {
        row["identity"]: row
        for row in rows
        if isinstance(row.get("identity"), str)
    }
    missing = sorted(set(detected_by_id) - set(declared))
    stale = sorted(set(declared) - set(detected_by_id))
    raw_directories = sorted(
        producer.identity
        for producer in detected
        if producer.kind == "directory"
        and declared.get(producer.identity, {}).get("disposition") != "test-compatibility-only"
    )
    parse_errors = [producer.as_dict() for producer in detected if producer.kind == "parse-error"]
    failures = list(errors)
    if missing:
        failures.append("detected producers missing from manifest: " + ", ".join(missing))
    if stale:
        failures.append("manifest entries no longer detected (stale): " + ", ".join(stale))
    if raw_directories:
        failures.append("unowned directory creators remain: " + ", ".join(raw_directories))
    if parse_errors:
        failures.append("one or more producer files could not be parsed")
    for identity, found in detected_by_id.items():
        row = declared.get(identity)
        if row is None or len(found) != 1:
            continue
        producer = found[0]
        if row.get("path") != producer.path:
            failures.append(f"manifest producer {identity!r} path does not match detected path {producer.path!r}")
        if row.get("symbol") != producer.symbol:
            failures.append(f"manifest producer {identity!r} symbol does not match detected symbol {producer.symbol!r}")
        if producer.kind == "owned-directory" and row.get("disposition") != "owned-scratch":
            failures.append(f"owned directory producer {identity!r} must use disposition 'owned-scratch'")
    return {
        "schema": SCHEMA,
        "manifest": str((manifest_path if manifest_path.is_absolute() else repo_root / manifest_path).resolve()),
        "detected": [producer.as_dict() for producer in detected],
        "declared_count": len(declared),
        "detected_count": len(detected_by_id),
        "missing": missing,
        "stale": stale,
        "unowned_directory_creators": raw_directories,
        "errors": failures,
        "ok": not failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args(argv)
    report = validate_inventory(
        args.repo_root.resolve(),
        manifest_path=args.manifest,
        require_git=args.require_git_file_listing,
    )
    emit_yaml(report)
    if report["ok"]:
        print(
            f"Validated temporary-output inventory: {report['detected_count']} producer identity(ies), "
            f"{report['declared_count']} manifest row(s).",
            file=sys.stderr,
        )
        return 0
    for error in report["errors"]:
        print(f"check-temp-producer-inventory: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover - main is unit-tested
    raise SystemExit(main())
