from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.final_bundle_preflight_evidence import (
    _classify_artifact,
    behavior_inventory,
    critique_inventory,
)
from scripts.final_bundle_preflight_lib import (
    _safe_relative,
    build_plan,
    packaging_mirror_inventory,
)

from .support import ROOT, run_script

MANIFEST = "charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json"
CRITIQUE = "charness-artifacts/critique/2026-08-06-slice-3-final-bundle-implementation-review.md"


def test_full_plan_is_ready_and_has_provenance_and_closeout_command() -> None:
    result = run_script(
        "scripts/final_bundle_preflight.py",
        "--repo-root",
        str(ROOT),
        "--manifest",
        MANIFEST,
        "--critique-path",
        CRITIQUE,
        "--behavior-channel",
        "behavior=python3 -m pytest -q tests/quality_gates/test_final_bundle_preflight.py",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ready"
    assert payload["mirror_inventory"]["status"] == "matched"
    assert payload["critique_inventory"][0]["status"] == "current"
    assert payload["artifact_inventory"]
    assert payload["candidate_snapshot"]["head_sha"]
    assert any(item["phase"] == "closeout" for item in payload["planned_commands"])
    assert all("reason_surface_ids" in item for item in payload["planned_commands"])


def test_explicit_paths_are_diagnostic_only() -> None:
    result = run_script(
        "scripts/final_bundle_preflight.py",
        "--repo-root",
        str(ROOT),
        "--manifest",
        MANIFEST,
        "--critique-path",
        CRITIQUE,
        "--behavior-channel",
        "behavior=python3 -m pytest -q",
        "--paths",
        "scripts/slice_manifest_lib.py",
        "--json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "diagnostic"
    assert {item["code"] for item in payload["blockers"]} >= {"diagnostic_scope"}
    assert not any(item["phase"] == "closeout" for item in payload["planned_commands"])


def test_behavior_channels_reject_duplicates_controls_and_validator_rebranding() -> None:
    rows, blockers = behavior_inventory(
        ["bad id=echo one", "safe=echo\nno", "same=python3 scripts/check_doc_links.py --repo-root .", "same=echo two"],
        ["python3 scripts/check_doc_links.py --repo-root ."],
    )
    assert rows == [{"id": "same", "command": "python3 scripts/check_doc_links.py --repo-root .", "claim": "operator-declared behavior proof"}]
    assert {item["code"] for item in blockers} == {
        "invalid_behavior_channel",
        "behavior_is_validator",
        "duplicate_behavior_channel",
    }


def test_missing_behavior_channel_refuses() -> None:
    rows, blockers = behavior_inventory([], ["python3 -m pytest -q"])
    assert rows == []
    assert blockers[0]["code"] == "missing_behavior_channel"


def test_fixture_artifacts_are_not_classified_as_goals() -> None:
    assert _classify_artifact("charness-artifacts/goals/fixtures/example.json") == "fixture"


def test_unmatched_diagnostic_path_has_stable_refusal_and_no_closeout() -> None:
    payload = build_plan(
        ROOT,
        manifest_path=ROOT / MANIFEST,
        critique_paths=[CRITIQUE],
        behavior_channels=["behavior=python3 -m pytest -q"],
        explicit_paths=["notes/not-covered.txt"],
    )
    assert payload["status"] == "diagnostic"
    assert {item["code"] for item in payload["blockers"]} >= {
        "diagnostic_scope",
        "unmatched_surface_path",
    }
    assert not any(item["phase"] == "closeout" for item in payload["planned_commands"])


def test_manifest_refusal_is_aggregated_without_closeout(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import final_bundle_preflight_lib as lib

    monkeypatch.setattr(
        lib._manifest,
        "validate_manifest",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            lib._manifest.ManifestError("identity_mismatch", "carrier.sha", "carrier mismatch")
        ),
    )
    payload = build_plan(
        ROOT,
        manifest_path=ROOT / MANIFEST,
        critique_paths=[CRITIQUE],
        behavior_channels=["behavior=python3 -m pytest -q"],
        explicit_paths=["scripts/slice_manifest_lib.py"],
    )
    assert any(item["code"] == "invalid_manifest" for item in payload["blockers"])
    assert not any(item["phase"] == "closeout" for item in payload["planned_commands"])


def test_manifest_outside_repo_refuses_with_structured_blocker() -> None:
    payload = build_plan(
        ROOT,
        manifest_path=Path("/tmp/final-bundle-outside.json"),
        critique_paths=[CRITIQUE],
        behavior_channels=["behavior=python3 -m pytest -q"],
        explicit_paths=["scripts/slice_manifest_lib.py"],
    )
    assert payload["status"] == "diagnostic"
    assert any(item["code"] == "invalid_manifest" for item in payload["blockers"])


def test_generated_critique_command_quotes_hostile_path_and_does_not_execute() -> None:
    hostile = "charness-artifacts/critique/space name;touch.md"
    payload = build_plan(
        ROOT,
        manifest_path=ROOT / MANIFEST,
        critique_paths=[hostile],
        behavior_channels=["behavior=python3 -m pytest -q"],
        explicit_paths=["scripts/slice_manifest_lib.py"],
    )
    command = next(item["command"] for item in payload["planned_commands"] if item["phase"] == "verify")
    assert "'charness-artifacts/critique/space name;touch.md'" in command
    assert not (ROOT / "touch.md").exists()


def test_critique_input_requires_durable_review_and_packet_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*_args, **_kwargs):
        raise ValueError("stale packet")

    monkeypatch.setattr("scripts.critique_reviewed_input_binding.validate_reviewed_input_binding", refuse)
    rows, blockers = critique_inventory(ROOT, [CRITIQUE], _safe_relative)
    assert rows[0]["status"] == "invalid"
    assert blockers[0]["code"] == "unbound_critique"


def test_packaging_owner_mirror_is_current() -> None:
    inventory, blockers = packaging_mirror_inventory(ROOT)
    assert inventory["owner"] == "scripts/packaging_lib.py#export_plugin_tree"
    assert inventory["status"] == "matched"
    assert blockers == []


def test_source_and_plugin_cli_copies_are_byte_identical() -> None:
    for relative in ("final_bundle_preflight.py", "final_bundle_preflight_lib.py"):
        assert (ROOT / "scripts" / relative).read_bytes() == (
            ROOT / "plugins/charness/scripts" / relative
        ).read_bytes()
