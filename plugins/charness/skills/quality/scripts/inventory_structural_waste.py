#!/usr/bin/env python3

"""Advisory inventory for duplicate discovery and broad scanner waste."""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_structural_waste = SKILL_RUNTIME.load_local_skill_module(__file__, "structural_waste_lib")
inventory = _structural_waste.inventory


def _print_text(payload: dict) -> None:
    print(
        "Structural waste inventory: "
        f"{payload['command_snippet_count']} command snippet(s), "
        f"{payload['python_source_count']} Python source file(s), "
        f"{len(payload['duplicate_discovery_candidates'])} duplicate-discovery candidate(s), "
        f"{len(payload['broad_scanner_candidates'])} broad-scanner candidate(s)."
    )
    for finding in payload["findings"]:
        print(f"{finding['severity'].upper()} {finding['type']}: {finding['recommended_action']}")
    for candidate in payload["duplicate_discovery_candidates"]:
        print(
            f"  duplicate {candidate['path']}::{candidate['origin']} "
            f"({candidate['type']}): {candidate['recommended_action']}"
        )
    for candidate in payload["broad_scanner_candidates"]:
        print(
            f"  scanner {candidate['path']}:{candidate['line']} "
            f"({candidate['parser_token']}): {candidate['recommended_action']}"
        )
    interpretation = payload["interpretation"]
    print(
        "INTERPRETATION (advisory structural signal, not a refactor mandate): "
        f"measures {interpretation['measures']}; blind spots: "
        f"{interpretation['blind_spots']}. Answer first: "
        f"{interpretation['interpretation_question']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the structural waste inventory")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
    args = parser.parse_args()

    payload = inventory(args.repo_root)
    if args.json:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        _print_text(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
