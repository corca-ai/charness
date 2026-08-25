#!/usr/bin/env python3
"""Check the executable producer-to-final-consumer invariant registry."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


def _load_contract_module(repo_root: Path):
    shared = repo_root / "skills" / "shared" / "scripts"
    if not shared.is_dir():
        shared = repo_root / "shared" / "scripts"
    if str(shared) not in sys.path:
        sys.path.insert(0, str(shared))
    import provenance_contract

    return provenance_contract


def _emit_yaml(payload: dict, repo_root: Path) -> None:
    output_path = repo_root / "scripts" / "yaml_output.py"
    spec = importlib.util.spec_from_file_location("charness_yaml_output", output_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"yaml output helper is not loadable: {output_path}")
    output = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(output)
    output.emit_yaml(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="Repository or packaged tree to validate"
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    module = _load_contract_module(repo_root)
    errors = module.validate_registry(
        repo_root, require_repo_anchors=(repo_root / "skills" / "shared").is_dir()
    )
    fixture_results = []
    authoring_tree = (repo_root / "tests").is_dir()
    # The authoring checkout has the final-consumer tests.  Execute the exact
    # nodes named by the registry so a path/comment marker cannot masquerade as
    # proof.  Exported plugin trees intentionally validate shape and anchors only.
    if not errors and authoring_tree:
        for contract in module.CONTRACTS:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", contract.negative_fixture],
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=60,
                )
            except subprocess.TimeoutExpired as exc:
                fixture_results.append(
                    {
                        "contract_id": contract.contract_id,
                        "fixture": contract.negative_fixture,
                        "returncode": None,
                        "status": "timeout",
                    }
                )
                errors.append(
                    f"{contract.contract_id} fixture timed out ({contract.negative_fixture}): "
                    f"{exc}"
                )
                continue
            fixture_results.append(
                {
                    "contract_id": contract.contract_id,
                    "fixture": contract.negative_fixture,
                    "returncode": result.returncode,
                    "status": "passed" if result.returncode == 0 else "failed",
                }
            )
            if result.returncode:
                errors.append(
                    f"{contract.contract_id} fixture failed ({contract.negative_fixture}): "
                    f"{result.stdout.strip() or result.stderr.strip()}"
                )
    payload = {
        "schema_version": module.SCHEMA_VERSION,
        "contract_count": len(module.CONTRACTS),
        "fixture_results": fixture_results,
        "errors": errors,
        "proof_level": "executable-fixtures" if authoring_tree else "shape-only",
        "non_claims": []
        if authoring_tree
        else ["final-consumer pytest fixtures are not packaged in this plugin layout"],
        "ok": not errors,
    }
    _emit_yaml(payload, repo_root)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
