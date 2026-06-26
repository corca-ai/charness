#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import public_spec_quality_lib as qlib  # noqa: E402
from public_spec_inventory_lib import inventory  # noqa: E402


def summarize_payload(payload: dict[str, object], *, sample_limit: int = 10) -> dict[str, object]:
    specs = payload.get("public_specs", [])
    spec_items = specs if isinstance(specs, list) else []
    flagged_specs = [
        {
            "spec_path": spec.get("spec_path"),
            "total_line_count": spec.get("total_line_count"),
            "source_guard_row_count": spec.get("source_guard_row_count"),
            "implementation_path_ref_count": spec.get("implementation_path_ref_count"),
            "heuristics": spec.get("heuristics", []),
        }
        for spec in spec_items
        if isinstance(spec, dict) and spec.get("heuristics")
    ]
    layering = payload.get("layering", {})
    layering_dict = layering if isinstance(layering, dict) else {}
    return {
        "summary_note": "summary is triage output; use --json for full public-spec attribution",
        "repo_root": payload["repo_root"],
        "summary": payload["summary"],
        "layering": {
            "heuristics": layering_dict.get("heuristics", []),
            "delegated_runner_specs": layering_dict.get("delegated_runner_specs", []),
            "duplicate_command_examples_sample": layering_dict.get("duplicate_command_examples", [])[:sample_limit],
            "top_source_guard_specs_sample": layering_dict.get("top_source_guard_specs", [])[:sample_limit],
            "recommendations": layering_dict.get("recommendations", []),
            "review_prompts": layering_dict.get("review_prompts", []),
        },
        "flagged_specs_sample": flagged_specs[:sample_limit],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the public-skill spec quality inventory")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
    parser.add_argument("--summary", action="store_true", help="Emit compact JSON rollups and samples instead of full spec attribution")
    args = parser.parse_args()
    try:
        payload = inventory(args.repo_root.resolve())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.summary:
        print(json.dumps(summarize_payload(payload), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("\n".join(qlib.render_text_summary(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
