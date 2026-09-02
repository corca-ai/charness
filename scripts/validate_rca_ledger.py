#!/usr/bin/env python3
"""Schema + closed-enum validation over the RCA conversion ledger.

Blocks only on malformed lines (changed-surface scope). The conversion rate is
advisory and is never evaluated here; this validator must not become a
whole-artifact gate on the metric value.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.yaml_output import emit_yaml  # noqa: E402

try:
    from scripts import rca_ledger_lib as lib
except ImportError:
    import rca_ledger_lib as lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate every line of the RCA ledger.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--ledger", default=None, help="Override ledger path (defaults to canonical)."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    ledger_path = lib.resolve_ledger_path(repo_root, Path(args.ledger) if args.ledger else None)
    errors = lib.validate_ledger(ledger_path, lib.load_schema())

    result = {
        "status": "valid" if not errors else "invalid",
        "ledger_path": lib.portable_path(repo_root, ledger_path),
        "error_count": len(errors),
        "errors": errors,
    }
    # Unconditional YAML. The retired human lines carried only `status`,
    # `error_count`, `ledger_path`, and each error's `line`/`error` -- all already
    # in the payload below.
    emit_yaml(result)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
