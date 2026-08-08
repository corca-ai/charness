from __future__ import annotations

import hashlib
import json
import subprocess
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

from .support import ROOT, bundle_blocker_report, bundle_payload_or_report, run_script

MANIFEST = "charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json"
CRITIQUE = "charness-artifacts/critique/2026-08-06-slice-3-final-bundle-contract.md"


def test_full_plan_has_provenance_and_inventories() -> None:
    """Renamed off `is_ready`, because that was the coupling #537 is about.

    The build found one place the issue's own analysis was too generous: it says every
    assertion other than `status == "ready"` survives a blocked repo, and `planned_commands` does
    NOT — the plan omits them entirely when blocked. Those two assertions moved to the readiness
    test, where the precondition they need is the subject rather than a side effect.
    """
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
    # Parsed from stdout regardless of exit code, and NOT asserting `ready`. #537: this test's
    # name and every other assertion in it are about plan SHAPE, which survives a blocked repo
    # intact. Only the `ready` line tied it to the repo being currently clean, and that one line
    # made a correct preflight refusal surface as five failing tests instead of one finding.
    # `test_this_repo_is_currently_bundle_ready` below is the single test that owns that question.
    payload = bundle_payload_or_report(result, "final_bundle_preflight")
    assert payload["status"] in {"ready", "blocked"}, payload.get("status")
    # SHAPE only, and that means shape of the live-state fields too — not their verdicts. A
    # round-2 measurement showed the first repair fixed only the `unmatched_surface_path`
    # class: a drifted plugin mirror still fanned out to five failures, three of them named
    # for subjects that were not the cause, because `mirror_inventory["status"] == "matched"`
    # and `critique_inventory[0]["status"] == "current"` are the same live-repo coupling as
    # `status == "ready"` was. Those verdicts have their own owners —
    # `test_packaging_owner_mirror_is_current` and the critique-inventory tests below — so this
    # test asserts the keys are populated and leaves the verdicts to them.
    assert payload["mirror_inventory"]["owner"]
    assert payload["mirror_inventory"]["status"]
    assert payload["critique_inventory"][0]["path"]
    assert isinstance(payload["artifact_inventory"], list)
    assert payload["candidate_snapshot"]["head_sha"]


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
    assert result.returncode == 1, result.stdout[:400] or result.stderr[:400]
    payload = bundle_payload_or_report(result, "final_bundle_preflight")
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


def test_final_bundle_cli_human_renderer_is_available() -> None:
    result = run_script(
        "scripts/final_bundle_preflight.py",
        "--repo-root", str(ROOT), "--manifest", MANIFEST,
        "--critique-path", CRITIQUE,
        "--behavior-channel", "behavior=python3 -m pytest -q tests/quality_gates/test_final_bundle_preflight.py",
    )
    # The subject is that the human renderer EXISTS and renders the verdict it actually has.
    # A first version accepted either verdict and then asserted `"Blockers:" in stdout`, which a
    # bounded round showed was vacuous: the ready branch prints "Blockers: none", which CONTAINS
    # that substring, so the assertion could not distinguish the branches. Now the blocker line
    # asserted is the one the status implies.
    # The message names returncode and stderr too: `stdout[:120]` is EMPTY precisely when the
    # renderer crashed, which is the one case this assertion trips.
    assert result.stdout.startswith("Final-bundle preflight: "), (
        f"returncode={result.returncode}, stdout={result.stdout[:200]!r}, "
        f"stderr={result.stderr.strip()!r}"
    )
    verdict_line = result.stdout.splitlines()[0]
    if verdict_line == "Final-bundle preflight: ready":
        assert "Blockers: none" in result.stdout
    else:
        assert verdict_line == "Final-bundle preflight: blocked", verdict_line
        # A blocked render must carry the blocker DETAIL, not just the heading — that detail is
        # the whole point of #537, and nothing pinned it before. `Remediation:` only appears on
        # the per-blocker line, so it is the one that proves the detail rendered.
        assert "Remediation:" in result.stdout, result.stdout[:600]


def test_critique_inventory_refusal_matrix(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from scripts import final_bundle_preflight_evidence as evidence

    rows, blockers = evidence.critique_inventory(tmp_path, [], _safe_relative)
    assert rows == [] and blockers[0]["code"] == "missing_critique"

    def unsafe(_: str) -> str:
        raise ValueError("unsafe")

    _, blockers = evidence.critique_inventory(tmp_path, ["../bad"], unsafe)
    assert blockers[0]["code"] == "unsafe_critique_path"
    _, blockers = evidence.critique_inventory(tmp_path, ["missing.txt"], _safe_relative)
    assert blockers[0]["code"] == "invalid_critique_artifact"

    review = tmp_path / "review.md"
    review.write_text("review\n", encoding="utf-8")
    packet = tmp_path / "packet.json"
    packet_md = tmp_path / "packet.md"
    identity_sha = "a" * 64
    fields = {"packet path": "packet.json", "packet sha256": "0" * 64, "identity sha256": identity_sha}
    monkeypatch.setattr(evidence._binding, "_binding_fields", lambda _: fields)
    monkeypatch.setattr(evidence._binding, "validate_reviewed_input_binding", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(evidence._packet, "render_markdown", lambda _: "rendered")

    _, blockers = evidence.critique_inventory(tmp_path, ["review.md"], _safe_relative)
    assert blockers[0]["code"] == "unbound_critique"
    packet.write_text(json.dumps({"reviewed_input_identity": {"identity_sha256": identity_sha}}), encoding="utf-8")
    packet_md.write_text("rendered", encoding="utf-8")
    _, blockers = evidence.critique_inventory(tmp_path, ["review.md"], _safe_relative)
    assert blockers[0]["code"] == "unbound_critique"

    fields["packet sha256"] = hashlib.sha256(packet.read_bytes()).hexdigest()
    packet.write_text(json.dumps({}), encoding="utf-8")
    fields["packet sha256"] = hashlib.sha256(packet.read_bytes()).hexdigest()
    _, blockers = evidence.critique_inventory(tmp_path, ["review.md"], _safe_relative)
    assert blockers[0]["code"] == "unbound_critique"

    packet.write_text(json.dumps({"reviewed_input_identity": {"identity_sha256": identity_sha}}), encoding="utf-8")
    fields["packet sha256"] = hashlib.sha256(packet.read_bytes()).hexdigest()
    packet_md.write_text("wrong", encoding="utf-8")
    _, blockers = evidence.critique_inventory(tmp_path, ["review.md"], _safe_relative)
    assert blockers[0]["code"] == "unbound_critique"

    packet_md.write_text("rendered", encoding="utf-8")
    fields["packet markdown sha256"] = "0" * 64
    _, blockers = evidence.critique_inventory(tmp_path, ["review.md"], _safe_relative)
    assert blockers[0]["code"] == "unbound_critique"


def test_final_bundle_private_error_and_render_branches(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from scripts import final_bundle_preflight_lib as lib

    monkeypatch.setattr(lib, "_git", lambda *_args, **_kwargs: subprocess.CompletedProcess([], 1, stdout="", stderr="failed"))
    with pytest.raises(lib.BundleError):
        lib._git_text(tmp_path, "status")
    monkeypatch.setattr(lib, "_git", lambda *_args, **_kwargs: subprocess.CompletedProcess([], 1, stdout=b"", stderr=b"failed"))
    with pytest.raises(lib.BundleError):
        lib._git_bytes(tmp_path, "status")
    with pytest.raises(lib.BundleError):
        _safe_relative("a\\b")
    with pytest.raises(lib.BundleError):
        _safe_relative("../bad")

    manifest = ROOT / MANIFEST
    def drift_git(_repo: Path, *args: str, **_kwargs: object) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess([], 0 if args and args[0] == "ls-files" else 1, stdout="", stderr="drift")

    monkeypatch.setattr(lib, "_git", drift_git)
    blockers = lib._current_manifest_blockers(ROOT, manifest)
    assert {item["code"] for item in blockers} == {"manifest_worktree_drift", "manifest_index_drift"}
    missing_manifest = tmp_path / "missing-manifest.json"
    blockers = lib._current_manifest_blockers(tmp_path, missing_manifest)
    assert {item["code"] for item in blockers} == {"manifest_not_regular"}
    untracked_manifest = tmp_path / "untracked.json"
    untracked_manifest.write_text("{}", encoding="utf-8")
    def untracked_git(_repo: Path, *args: str, **_kwargs: object) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess([], 1 if args and args[0] == "ls-files" else 0, stdout="", stderr="not tracked")

    monkeypatch.setattr(lib, "_git", untracked_git)
    blockers = lib._current_manifest_blockers(tmp_path, untracked_manifest)
    assert {item["code"] for item in blockers} == {"manifest_not_tracked"}
    assert lib._tree_files(tmp_path / "not-a-directory") == set()

    checked = tmp_path / "checked"
    checked.mkdir()
    (checked / "only-checked.txt").write_text("checked", encoding="utf-8")
    (checked / "same.txt").write_text("old", encoding="utf-8")
    monkeypatch.setattr(lib._packaging, "load_manifest", lambda *_args: {})
    monkeypatch.setattr(lib._packaging, "checked_in_plugin_root", lambda *_args: "checked")

    def render(_: Path, expected: Path, __: object) -> None:
        expected.mkdir(parents=True, exist_ok=True)
        (expected / "only-expected.txt").write_text("expected", encoding="utf-8")
        (expected / "same.txt").write_text("new", encoding="utf-8")

    monkeypatch.setattr(lib._packaging, "export_plugin_tree", render)
    inventory, blockers = packaging_mirror_inventory(tmp_path)
    assert inventory["status"] == "needs_sync"
    assert blockers[0]["code"] == "needs_sync"
    monkeypatch.setattr(lib._packaging, "load_manifest", lambda *_args: (_ for _ in ()).throw(RuntimeError("renderer")))
    inventory, blockers = packaging_mirror_inventory(tmp_path)
    assert inventory["status"] == "unavailable"
    assert blockers[0]["code"] == "packaging_owner_unavailable"

    monkeypatch.setattr(lib, "_current_manifest_blockers", lambda *_args: [])
    monkeypatch.setattr(lib._manifest, "validate_manifest", lambda *_args, **_kwargs: {
        "target_sha": "a" * 40, "carrier_sha": "a" * 40, "ci_run_id": 1, "captured_open_issue_count": 0,
    })
    monkeypatch.setattr(lib, "_git", lambda *_args, **_kwargs: subprocess.CompletedProcess([], 1, stdout="", stderr="not ancestor"))
    monkeypatch.setattr(lib._surfaces, "collect_changed_paths_since_resolved_base", lambda *_args: (_ for _ in ()).throw(lib._surfaces.SurfaceError("bad paths")))
    monkeypatch.setattr(lib, "_candidate_snapshot", lambda *_args: (_ for _ in ()).throw(lib.BundleError("bad snapshot")))
    monkeypatch.setattr(lib._surfaces, "load_surfaces", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("bad surfaces")))
    monkeypatch.setattr(lib, "packaging_mirror_inventory", lambda *_args: ({"status": "matched"}, []))
    payload = build_plan(ROOT, manifest_path=manifest, critique_paths=[], behavior_channels=[])
    assert payload["status"] == "blocked"
    codes = {item["code"] for item in payload["blockers"]}
    assert {"candidate_base_not_ancestor", "changed_path_collection_failed", "candidate_snapshot_failed", "surface_inventory_failed"} <= codes

    monkeypatch.undo()
    # The subject here is that undoing the patches restores a REAL build that still produces a
    # well-formed plan — not that this repo happens to be bundle-ready, which is a different
    # question owned by one test below.
    restored = build_plan(
        ROOT,
        manifest_path=manifest,
        critique_paths=[CRITIQUE],
        behavior_channels=["behavior=python3 -m pytest -q tests/quality_gates/test_final_bundle_preflight.py"],
    )
    assert restored["status"] in {"ready", "blocked"}
    # Same reason as above: this test is about monkeypatched error branches, so it must not
    # redden because the live mirror drifted.
    assert restored["mirror_inventory"]["status"]
    assert restored["candidate_snapshot"]["head_sha"]

    rich = {
        "status": "ready", "changed_paths": ["x"],
        "surface_inventory": [{"surface_id": "surface"}], "artifact_inventory": [{"path": "x"}],
        "critique_inventory": [{"path": "review.md"}], "behavior_channels": [{"id": "behavior", "command": "echo"}],
        "planned_commands": [{"phase": "verify", "command": "echo", "reason_surface_ids": []}],
        "blockers": [{"code": "blocked", "subject": "x", "message": "no", "remediation": "fix"}],
    }
    rendered = lib.render_text(rich)
    assert "Surfaces: surface" in rendered and "Blockers:" in rendered
    rich["blockers"] = []
    assert "Blockers: none" in lib.render_text(rich)


def test_this_repo_is_currently_bundle_ready() -> None:
    """The single test that answers "is this repo bundle-ready right now".

    #537: five tests used to answer it as a side effect, so one correct refusal — ten artifacts
    with no owning surface — arrived as five failures whose only diagnostic was a truncated
    subprocess repr, and stayed unread for six commits among thirty other reds. The gate keeps
    its teeth; what changes is that exactly one test fails and it PRINTS the blocker payload the
    preflight already produced, including the remediation and the offending paths.
    """
    result = run_script(
        "scripts/final_bundle_preflight.py",
        "--repo-root", str(ROOT), "--manifest", MANIFEST,
        "--critique-path", CRITIQUE,
        "--behavior-channel", "behavior=python3 -m pytest -q tests/quality_gates/test_final_bundle_preflight.py",
        "--json",
    )
    payload = bundle_payload_or_report(result, "final_bundle_preflight")
    assert payload["status"] == "ready", bundle_blocker_report(payload, "final_bundle_preflight")
    # `result.stdout`, not `result.stderr`: these scripts report on stdout, so passing stderr
    # here is the empty-message idiom this slice exists to stop repeating.
    assert result.returncode == 0, result.stdout[:400]
    # These live here rather than in the shape test because a blocked plan carries NO
    # planned_commands, so asserting them anywhere else re-creates the coupling this slice removed.
    assert any(item["phase"] == "closeout" for item in payload["planned_commands"])
    assert all("reason_surface_ids" in item for item in payload["planned_commands"])
