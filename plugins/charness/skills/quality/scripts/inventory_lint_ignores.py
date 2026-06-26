#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def summarize(payload: dict[str, object], *, sample_limit: int = 10) -> dict[str, object]:
    findings = payload.get("findings", [])
    finding_items = [finding for finding in findings if isinstance(finding, dict)]
    priority_sample = sorted(
        finding_items,
        key=lambda finding: (
            0 if finding.get("blanket") else 1,
            0 if finding.get("scope") == "file" else 1,
            str(finding.get("path", "")),
            int(finding.get("line", 0)),
        ),
    )[:sample_limit]
    return {
        "summary_note": "summary is triage output; use --json for full lint-ignore findings",
        "repo_root": payload["repo_root"],
        "summary": payload["summary"],
        "priority_findings_sample": priority_sample,
        "review_prompts": payload["review_prompts"],
        "interpretation": payload["interpretation"],
        "adapter_path": payload.get("adapter_path"),
        "adapter_valid": payload.get("adapter_valid", True),
        "adapter_errors": payload.get("adapter_errors", []),
        "adapter_warnings": payload.get("adapter_warnings", []),
        "adapter_load_mode": payload.get("adapter_load_mode", "permissive"),
    }


def main() -> int:
    repo_root = next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "lint_ignore_inventory_lib.py").is_file())
    sys.path.insert(0, str(repo_root))
    from scripts.lint_ignore_inventory_lib import inventory_lint_ignores
    from scripts.quality_adapter_lib import load_quality_adapter_permissive

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the lint-ignore inventory")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
    parser.add_argument("--summary", action="store_true", help="Emit compact JSON counts and priority samples instead of full findings")
    args = parser.parse_args()
    target_root = args.repo_root.resolve()
    adapter = load_quality_adapter_permissive(target_root)
    data = adapter.get("data", {}) if isinstance(adapter, dict) else {}
    vendored_paths = data.get("vendored_paths", []) if isinstance(data, dict) else []
    payload = inventory_lint_ignores(target_root, vendored_paths if isinstance(vendored_paths, list) else [])
    payload["adapter_path"] = adapter.get("path")
    payload["adapter_valid"] = adapter.get("valid", True)
    payload["adapter_errors"] = adapter.get("errors", [])
    payload["adapter_warnings"] = adapter.get("warnings", [])
    payload["adapter_load_mode"] = adapter.get("load_mode", "permissive")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.summary:
        print(json.dumps(summarize(payload), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for finding in payload["findings"]:
            codes = ",".join(finding["codes"]) or "*"
            print(f"{finding['tool']}:{finding['scope']}:{codes} {finding['path']}:{finding['line']}")
        interpretation = payload.get("interpretation")
        if isinstance(interpretation, dict):
            print(
                "INTERPRETATION (inference-layer trend, not a verdict): "
                f"measures {interpretation['measures']}; proxy for "
                f"{interpretation['proxy_for']}; blind spots: {interpretation['blind_spots']}. "
                f"Consumer must answer first: {interpretation['interpretation_question']}"
            )
        if payload["adapter_valid"] is False:
            print("adapter=invalid: advisory inventory is best-effort until adapter errors are repaired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
