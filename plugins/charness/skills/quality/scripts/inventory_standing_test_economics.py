#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_standing_test_economics = SKILL_RUNTIME.load_local_skill_module(__file__, "standing_test_economics_lib")
inventory = _standing_test_economics.inventory

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): the test-economics trend is an
# inference-layer proxy, so the inventory self-declares blind spots and the
# question the `quality` consumer must answer before acting on the growth.
INTERPRETATION = {
    "measures": "the standing test surface — test-file count, nested-CLI fan-out count, transpiler/loader and node-isolation snippets, and the pytest temp footprint",
    "proxy_for": "standing suite cost dominated by per-file runner startup, isolation, and fixture materialization rather than by test value",
    "blind_spots": "counts files and process-spawn call sites, not coverage or value — a high test-file count can be honest behavior coverage, and an intentional real-binary smoke that spawns a subprocess counts as nested-CLI fan-out; it cannot see whether a given test earns its isolation cost",
    "interpretation_question": "is this test-file / nested-CLI growth paying for real isolation and coverage value, or is it startup-cost waste THIS repo should consolidate?",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the standing-test economics inventory")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
    args = parser.parse_args()

    payload = inventory(args.repo_root.resolve())
    payload["interpretation"] = dict(INTERPRETATION)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print(f"test files: {payload['test_file_count']}")
    print(f"nested CLI files: {payload['nested_cli_file_count']}")
    for finding in payload["findings"]:
        print(f"{finding['severity'].upper()} {finding['type']}: {finding['recommended_action']}")
    interpretation = payload.get("interpretation")
    if isinstance(interpretation, dict):
        print(
            "INTERPRETATION (inference-layer trend, not a verdict): "
            f"measures {interpretation['measures']}; proxy for "
            f"{interpretation['proxy_for']}; blind spots: {interpretation['blind_spots']}. "
            f"Consumer must answer first: {interpretation['interpretation_question']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
