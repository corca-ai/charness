#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from cli_side_effect_probe_lib import build_inventory


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
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the CLI side-effect probe inventory")
    parser.add_argument("--contract-file", action="append", default=[], help="Path to a side-effect probe contract file (repeatable)")
    parser.add_argument("--execute-probes", action="store_true", help="Actually execute declared probe commands rather than only inventorying them")
    parser.add_argument("--fail-on-findings", action="store_true", help="Exit non-zero when any findings are surfaced")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    contract_paths = [(repo_root / path).resolve() for path in args.contract_file]
    adapter = _quality_adapter_lib.load_quality_adapter_permissive(repo_root)
    vendored = _adapter_vendored_prefixes(adapter)
    vendored_filter = (lambda root, path: _vendored_path_lib.is_vendored(root, path, vendored)) if vendored else None
    payload = build_inventory(
        repo_root,
        contract_paths=contract_paths,
        execute_probes=args.execute_probes,
        vendored_filter=vendored_filter,
    )
    payload["adapter_path"] = adapter.get("path")
    payload["adapter_valid"] = adapter.get("valid", True)
    payload["adapter_errors"] = adapter.get("errors", [])
    payload["adapter_warnings"] = adapter.get("warnings", [])
    payload["adapter_load_mode"] = adapter.get("load_mode", "permissive")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["status"] == "unconfigured":
            print(f"status=unconfigured: {payload.get('reason', '')}")
        if payload["adapter_valid"] is False:
            print("adapter=invalid: advisory inventory is best-effort until adapter errors are repaired.")
        for finding in payload["findings"]:
            command = finding.get("command", "")
            path = finding.get("path", "<none>")
            print(f"{finding['type']}: {path} {command}")
    return 1 if args.fail_on_findings and payload["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
