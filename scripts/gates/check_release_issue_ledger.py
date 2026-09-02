#!/usr/bin/env python3
"""CLI for the activation-time release issue ledger contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.yaml_output import emit_yaml  # noqa: E402

try:
    from scripts.release_issue_ledger_contract import (
        REPOSITORY,  # noqa: F401
        summary,
        validate_ledger,
    )
    from scripts.release_issue_ledger_contract import (
        SCHEMA_VERSION as _SCHEMA_VERSION,
    )
except ImportError:  # pragma: no cover - direct execution from scripts/
    from release_issue_ledger_contract import (  # type: ignore[no-redef]
        REPOSITORY,  # type: ignore[no-redef]  # noqa: F401
        summary,
        validate_ledger,
    )
    from release_issue_ledger_contract import (
        SCHEMA_VERSION as _SCHEMA_VERSION,
    )

SCHEMA_VERSION = _SCHEMA_VERSION


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    ledger_path = args.ledger if args.ledger.is_absolute() else repo_root / args.ledger
    try:
        payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        emit_yaml({"status": "fail", "errors": [f"cannot read ledger: {exc}"]})
        return 1
    errors = validate_ledger(payload, repo_root)
    if errors:
        emit_yaml({"status": "fail", "errors": errors})
        return 1
    emit_yaml(summary(payload))
    return 0


if __name__ == "__main__":  # pragma: no cover - main is unit-tested
    raise SystemExit(main())
