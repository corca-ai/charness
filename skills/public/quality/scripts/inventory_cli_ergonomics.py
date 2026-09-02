#!/usr/bin/env python3

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cli_ergonomics_lib as celib  # noqa: E402
from git_inventory_lib import (  # noqa: E402
    VisibleRepoFilesSnapshot,
    capture_visible_repo_files,
    visible_repo_files,
)
from summary_output_lib import add_output_args, emit_selected  # noqa: E402


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


_SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_quality_adapter_lib = _SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapters.quality_adapter_lib")
_vendored_path_lib = _SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.vendored_path_lib")


def _adapter_vendored_prefixes(adapter: dict[str, object]) -> list[str]:
    data = adapter.get("data", {}) if isinstance(adapter, dict) else {}
    values = data.get("vendored_paths", []) if isinstance(data, dict) else []
    if not isinstance(values, list):
        return []
    return _vendored_path_lib.vendored_prefixes(values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the CLI ergonomics inventory scan")
    parser.add_argument("--registry-file", action="append", default=[], help="Path to a command-registry JSON file (repeatable; defaults auto-discover under the repo)")
    parser.add_argument("--archetype-contract-file", action="append", default=[], help="Path to a command-archetype contract JSON file (repeatable; defaults auto-discover under the repo)")
    parser.add_argument("--flat-help-threshold", type=int, default=10, help="Number of subcommands above which a flat help surface is flagged")
    add_output_args(
        parser,
        summary_help="Emit compact YAML counts and finding samples for triage",
        detail_help="Emit the full CLI-ergonomics inventory as YAML",
    )
    return parser.parse_args()


def _default_paths(
    repo_root: Path,
    patterns: list[str],
    vendored: list[str],
    *,
    snapshot: VisibleRepoFilesSnapshot | None = None,
) -> list[Path]:
    visible_files = visible_repo_files(repo_root, snapshot=snapshot)
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


def summarize(payload: dict[str, object], *, sample_limit: int = 10) -> dict[str, object]:
    findings = payload.get("findings", [])
    sample = findings[:sample_limit] if isinstance(findings, list) else []
    return {
        "summary_note": "summary is triage output; use --detail for full registry and archetype records",
        "repo_root": payload["repo_root"],
        "status": payload["status"],
        "scope_classification": payload.get("scope_classification"),
        "reason": payload.get("reason"),
        "registry_count": len(payload.get("registries", [])),
        "archetype_contract_count": len(payload.get("archetype_contracts", [])),
        "finding_count": len(findings) if isinstance(findings, list) else 0,
        "findings_sample": sample,
        "adapter_path": payload.get("adapter_path"),
        "adapter_valid": payload.get("adapter_valid", True),
        "adapter_errors": payload.get("adapter_errors", []),
        "adapter_warnings": payload.get("adapter_warnings", []),
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    snapshot = capture_visible_repo_files(repo_root)
    adapter = _quality_adapter_lib.load_quality_adapter_permissive(repo_root)
    vendored = _adapter_vendored_prefixes(adapter)
    registry_paths = (
        [(repo_root / path).resolve() for path in args.registry_file]
        if args.registry_file
        else _default_paths(
            repo_root,
            ["**/command-registry.json", "**/*command-registry*.json"],
            vendored,
            snapshot=snapshot,
        )
    )
    archetype_contract_paths = (
        [(repo_root / path).resolve() for path in args.archetype_contract_file]
        if args.archetype_contract_file
        else _default_paths(
            repo_root,
            ["**/command-archetypes.json", "**/*archetype-contract*.json"],
            vendored,
            snapshot=snapshot,
        )
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
    if not emit_selected(payload, args, summarize=summarize):
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
