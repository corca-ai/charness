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
_summary_output = SKILL_RUNTIME.load_local_skill_module(__file__, "summary_output_lib")
inventory = _standing_test_economics.inventory
dump_yaml = _summary_output.dump_yaml
emit_summary = _summary_output.emit_summary

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): the test-economics trend is an
# inference-layer proxy, so the inventory self-declares blind spots and the
# question the `quality` consumer must answer before acting on the growth.
INTERPRETATION = {
    "measures": "the test surface relevant to standing economics — test-file count, nested-CLI fan-out split into likely standing/mixed vs module-level release_only buckets, transpiler/loader and node-isolation snippets, and the pytest temp footprint",
    "proxy_for": "standing suite cost dominated by per-file runner startup, isolation, and fixture materialization rather than by test value",
    "blind_spots": "counts files and process-spawn call sites, not coverage or value — a high test-file count can be honest behavior coverage, and an intentional real-binary smoke that spawns a subprocess counts as nested-CLI fan-out; the release_only split is conservative and only separates module-level pytestmark files, so mixed or non-standard markers stay in standing/mixed; it cannot see whether a given test earns its isolation cost",
    "interpretation_question": "is this test-file / nested-CLI growth paying for real isolation and coverage value, or is it startup-cost waste THIS repo should consolidate?",
}

SUMMARY_FIELDS = (
    "repo_root",
    "summary_note",
    "test_file_count",
    "test_files_by_extension",
    "runner_snippets",
    "nested_cli_file_count",
    "nested_cli_files_sample",
    "nested_cli_release_only_file_count",
    "nested_cli_release_only_files_sample",
    "nested_cli_standing_or_mixed_file_count",
    "nested_cli_standing_or_mixed_files_sample",
    "pytest_temp_footprint",
    "findings",
    "interpretation",
)
SUMMARY_NESTED_CLI_SAMPLE_SIZE = 10
SUMMARY_NOTE = "summary is triage output; use --json for full nested_cli_files attribution"


def summarize_payload(payload: dict[str, object]) -> dict[str, object]:
    payload_with_sample = dict(payload)
    payload_with_sample["summary_note"] = SUMMARY_NOTE
    for key in (
        "nested_cli_files",
        "nested_cli_release_only_files",
        "nested_cli_standing_or_mixed_files",
    ):
        value = payload.get(key, [])
        sample = value[:SUMMARY_NESTED_CLI_SAMPLE_SIZE] if isinstance(value, list) else []
        payload_with_sample[f"{key}_sample"] = sample
    return {field: payload_with_sample.get(field) for field in SUMMARY_FIELDS}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the standing-test economics inventory")
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
    parser.add_argument("--summary", action="store_true", help="Emit compact JSON for agent review instead of every nested-CLI path")
    parser.add_argument("--summary-yaml", action="store_true", help="Emit compact YAML for agent review instead of compact JSON")
    args = parser.parse_args()

    payload = inventory(args.repo_root.resolve())
    payload["interpretation"] = dict(INTERPRETATION)
    if args.summary or args.summary_yaml:
        emit_summary(summarize_payload(payload), as_yaml=args.summary_yaml)
        return 0
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
