#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cli_ergonomics_lib as celib  # noqa: E402


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


_SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_quality_adapter_lib = _SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")
_vendored_path_lib = _SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.vendored_path_lib")


def _adapter_vendored_prefixes(adapter: dict[str, object]) -> list[str]:
    data = adapter.get("data", {}) if isinstance(adapter, dict) else {}
    values = data.get("vendored_paths", []) if isinstance(data, dict) else []
    if not isinstance(values, list):
        return []
    return _vendored_path_lib.vendored_prefixes(values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--registry-file", action="append", default=[])
    parser.add_argument("--archetype-contract-file", action="append", default=[])
    parser.add_argument("--flat-help-threshold", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _git_visible_repo_files(repo_root: Path) -> set[Path] | None:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return {repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel}


def _default_paths(repo_root: Path, patterns: list[str], vendored: list[str]) -> list[Path]:
    visible_files = _git_visible_repo_files(repo_root)
    seen: set[Path] = set()
    found: list[Path] = []
    for pattern in patterns:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            if visible_files is not None and path not in visible_files:
                continue
            if _vendored_path_lib.is_vendored(repo_root, path, vendored):
                continue
            seen.add(path)
            found.append(path)
    return found


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = _quality_adapter_lib.load_quality_adapter_permissive(repo_root)
    vendored = _adapter_vendored_prefixes(adapter)
    registry_paths = (
        [(repo_root / path).resolve() for path in args.registry_file]
        if args.registry_file
        else _default_paths(repo_root, ["**/command-registry.json", "**/*command-registry*.json"], vendored)
    )
    archetype_contract_paths = (
        [(repo_root / path).resolve() for path in args.archetype_contract_file]
        if args.archetype_contract_file
        else _default_paths(repo_root, ["**/command-archetypes.json", "**/*archetype-contract*.json"], vendored)
    )
    registries = [celib.inventory_registry(repo_root, path, threshold=args.flat_help_threshold) for path in registry_paths]
    archetype_contracts = [celib.inventory_archetype_contract(repo_root, path) for path in archetype_contract_paths]
    findings = [finding for section in [*registries, *archetype_contracts] for finding in section["findings"]]
    status = celib.scope_status(len(registry_paths) + len(archetype_contract_paths), bool(args.registry_file or args.archetype_contract_file))
    payload = {
        "repo_root": str(repo_root),
        "flat_help_threshold": args.flat_help_threshold,
        "adapter_path": adapter.get("path"),
        "adapter_valid": adapter.get("valid", True),
        "adapter_errors": adapter.get("errors", []),
        "adapter_warnings": adapter.get("warnings", []),
        "adapter_load_mode": adapter.get("load_mode", "permissive"),
        **status,
        "registries": registries,
        "archetype_contracts": archetype_contracts,
        "findings": findings,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["status"] == "unconfigured":
            print(f"status=unconfigured: {payload.get('reason', '')}")
        if payload.get("scope_classification", "scanned").startswith("advisory_only"):
            print(f"scope_classification={payload['scope_classification']}: enforcement is advisory-only.")
        if payload["adapter_valid"] is False:
            print("adapter=invalid: advisory inventory is best-effort until adapter errors are repaired.")
        for finding in findings:
            print(f"{finding['type']}: {finding['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
