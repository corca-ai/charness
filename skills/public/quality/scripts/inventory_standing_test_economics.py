#!/usr/bin/env python3

from __future__ import annotations

import argparse
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
_standing_test_economics = SKILL_RUNTIME.load_local_skill_module(__file__, "standing_test_economics_lib")
_summary_output = SKILL_RUNTIME.load_local_skill_module(__file__, "summary_output_lib")
inventory = _standing_test_economics.inventory
dump_yaml = _summary_output.dump_yaml


def _load_quality_adapter_permissive(repo_root: Path) -> dict[str, object]:
    lib_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "adapters" / "quality_adapter_lib.py").is_file()
        ),
        None,
    )
    if lib_root is None:
        return {"data": {}, "path": None, "valid": True, "errors": [], "warnings": [], "load_mode": "permissive"}
    if str(lib_root) not in sys.path:
        sys.path.insert(0, str(lib_root))
    from scripts.adapters.quality_adapter_lib import load_quality_adapter_permissive

    return load_quality_adapter_permissive(repo_root)

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): the test-economics trend is an
# inference-layer proxy, so the inventory self-declares blind spots and the
# question the `quality` consumer must answer before acting on the growth.
INTERPRETATION = {
    "measures": "the test surface relevant to standing economics — test-file count, nested-CLI fan-out split into standing-only, mixed release_only/standing, and all-release-only buckets, conservative static subprocess-settlement signals, transpiler/loader and node-isolation snippets, the pytest temp footprint, and a proof-preserving comparison card when acceleration candidates exist",
    "proxy_for": "standing suite cost dominated by per-file runner startup, isolation, and fixture materialization rather than by test value",
    "blind_spots": "counts files and process-spawn call sites, not coverage or value — a high test-file count can be honest behavior coverage, and an intentional real-binary smoke that spawns a subprocess counts as nested-CLI fan-out; settlement fields only classify visible literal syntax and never prove child lifecycle or process-tree ownership; the release_only split is structural and only sees pytest markers, so the file buckets still cannot tell whether a given test earns its isolation cost",
    "interpretation_question": "is this test-file / nested-CLI growth paying for real isolation and coverage value, or is it startup-cost waste THIS repo should consolidate?",
}

SUMMARY_FIELDS = (
    "repo_root",
    "summary_note",
    "test_discovery",
    "test_file_count",
    "test_files_by_extension",
    "runner_snippets",
    "nested_cli_file_count",
    "nested_cli_files_sample",
    "nested_cli_all_release_only_file_count",
    "nested_cli_all_release_only_files_sample",
    "nested_cli_mixed_release_only_file_count",
    "nested_cli_mixed_release_only_files_sample",
    "nested_cli_standing_file_count",
    "nested_cli_standing_files_sample",
    "nested_cli_release_only_file_count",
    "nested_cli_release_only_files_sample",
    "nested_cli_standing_or_mixed_file_count",
    "nested_cli_standing_or_mixed_files_sample",
    "subprocess_settlement",
    "pytest_temp_footprint",
    "proof_path_review",
    "findings",
    "interpretation",
    "adapter_path",
    "adapter_valid",
    "adapter_errors",
    "adapter_warnings",
    "adapter_load_mode",
)
SUMMARY_NESTED_CLI_SAMPLE_SIZE = 10
SUMMARY_NOTE = "summary is triage output; use --detail for full nested-CLI and subprocess-settlement callsite attribution"


def summarize_payload(payload: dict[str, object]) -> dict[str, object]:
    payload_with_sample = dict(payload)
    payload_with_sample["summary_note"] = SUMMARY_NOTE
    for key in (
        "nested_cli_files",
        "nested_cli_all_release_only_files",
        "nested_cli_mixed_release_only_files",
        "nested_cli_standing_files",
        "nested_cli_release_only_files",
        "nested_cli_standing_or_mixed_files",
    ):
        value = payload.get(key, [])
        sample = value[:SUMMARY_NESTED_CLI_SAMPLE_SIZE] if isinstance(value, list) else []
        payload_with_sample[f"{key}_sample"] = sample
    settlement = payload.get("subprocess_settlement")
    if isinstance(settlement, dict):
        payload_with_sample["subprocess_settlement"] = {
            key: value for key, value in settlement.items() if key != "seams"
        }
    return {field: payload_with_sample.get(field) for field in SUMMARY_FIELDS}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the standing-test economics inventory")
    _summary_output.add_output_args(
        parser,
        summary_help="Emit compact YAML for agent review instead of every nested-CLI path",
        detail_help="Emit the full inventory payload as YAML",
    )
    args = parser.parse_args()

    target_root = args.repo_root.resolve()
    adapter = _load_quality_adapter_permissive(target_root)
    adapter_data = adapter.get("data", {}) if isinstance(adapter, dict) else {}
    discovery = adapter_data.get("test_file_discovery") if isinstance(adapter_data, dict) else None
    payload = inventory(target_root, discovery=discovery)
    payload["interpretation"] = dict(INTERPRETATION)
    payload["adapter_path"] = adapter.get("path")
    payload["adapter_valid"] = adapter.get("valid", True)
    payload["adapter_errors"] = adapter.get("errors", [])
    payload["adapter_warnings"] = adapter.get("warnings", [])
    payload["adapter_load_mode"] = adapter.get("load_mode", "permissive")
    if _summary_output.emit_selected(payload, args, summarize=summarize_payload):
        return 0
    print(f"test files: {payload['test_file_count']}")
    discovery_provenance = payload.get("test_discovery") or {}
    if discovery_provenance.get("source") != "default":
        print(f"test discovery source: {discovery_provenance.get('source')}")
    if discovery_provenance.get("degraded"):
        print(
            f"test discovery DEGRADED (command_status={discovery_provenance.get('command_status')}, "
            f"source={discovery_provenance.get('source')}): {discovery_provenance.get('error')}"
        )
    print(f"nested CLI files: {payload['nested_cli_file_count']}")
    print(
        "nested CLI buckets: "
        f"standing={payload['nested_cli_standing_file_count']} "
        f"mixed={payload['nested_cli_mixed_release_only_file_count']} "
        f"all-release-only={payload['nested_cli_all_release_only_file_count']}"
    )
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
    if payload.get("adapter_valid") is False:
        print("adapter=invalid: advisory inventory is best-effort until adapter errors are repaired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
