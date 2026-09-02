"""Release changed-line regression coverage for release and CLI boundaries.

This module is split from the evidence/boundary regression module so each test
file remains below the repository's hard Python length limit.  The literal
source paths are consumed by the focused mutation mapper.
"""

from __future__ import annotations

import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]

_MUTATION_SOURCES = (
    "charness",
    "scripts/review/adversarial_evidence.py",
    "scripts/adapters/capability_catalog_resolver.py",
    "scripts/review/critique_packet_lib.py",
    "scripts/review/reviewed_input_identity.py",
    "scripts/staged_commit_gate_plan_helpers.py",
    "skills/public/critique/scripts/prepare_packet.py",
    "skills/public/debug/scripts/persist_debug_artifact.py",
    "skills/public/quality/scripts/check_dup_ratchet.py",
    "skills/public/quality/scripts/dup_family_lineage.py",
    "skills/public/quality/scripts/dup_ratchet_baseline_lib.py",
    "skills/public/quality/scripts/check_provenance_contract.py",
    "skills/public/setup/scripts/inspect_repo.py",
)


def _load_script(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dup_check = _load_script(
    "skills/public/quality/scripts/check_dup_ratchet.py",
    "release_dup_check_split_under_test",
)
dup_lineage = _load_script(
    "skills/public/quality/scripts/dup_family_lineage.py",
    "release_dup_lineage_split_under_test",
)
dup_baseline = _load_script(
    "skills/public/quality/scripts/dup_ratchet_baseline_lib.py",
    "release_dup_baseline_split_under_test",
)
provenance_check = _load_script(
    "skills/public/quality/scripts/check_provenance_contract.py",
    "release_provenance_check_split_under_test",
)
setup_inspect = import_repo_module(
    ROOT / "skills/public/setup/scripts/inspect_repo.py",
    "skills.public.setup.scripts.inspect_repo",
)
debug_persist = import_repo_module(
    ROOT / "skills/public/debug/scripts/persist_debug_artifact.py",
    "skills.public.debug.scripts.persist_debug_artifact",
)


def test_dup_baseline_and_lineage_reject_untypeable_rows() -> None:
    assert dup_baseline.load_gate_baseline_families(
        {"code_families": [{"fingerprint": "x", "member_hashes": [], "member_paths": [1]}]}
    ) is None
    assert dup_lineage.readiness(
        ["not-a-row", {"fingerprint": "x", "member_paths": ["x.py"]}], reviewed_ids={"x"}
    )["status"] == "ready"
    assert dup_lineage.family_members({"locations": ["not-a-row", {"file": "src/a.py"}]})[1] == {"src/a.py"}


def test_dup_consumer_renders_lineage_proposal_advisory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    (repo / "q").mkdir()
    (repo / "q/dup-review.json").write_text(
        json.dumps(
            {
                "schemaVersion": "charness.quality.dup_review.v1",
                "fixable_ceiling": 0,
                "entries": [{"id": "OLD", "surface": "code", "class": "fixable", "note": "reviewed", "reviewed_at": "2026-08-25"}],
            }
        ),
        encoding="utf-8",
    )
    baseline = dup_baseline.build_gate_baseline(
        {"OLD": ["old-a", "old-b"]},
        member_paths={"OLD": ["src/a.py", "src/b.py"]},
        tool_version="0.20.0",
        algo_version=dup_check._fingerprint.FINGERPRINT_ALGO_VERSION,
    )
    (repo / "q/dup-ratchet-baseline.json").write_text(json.dumps(baseline), encoding="utf-8")
    (repo / ".agents/quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: consumer",
                "dup_ratchet:",
                "  enabled: true",
                "  floor_F: 0",
                "  escalation_K: 10",
                "  scope_paths:",
                "    - src",
                "  review_artifact_path: q/dup-review.json",
                "  gate_baseline_path: q/dup-ratchet-baseline.json",
                "",
            ]
        ),
        encoding="utf-8",
    )
    code = tmp_path / "code.json"
    code.write_text(
        json.dumps(
            {
                "status": "findings",
                "tool_version": "0.20.0",
                "families": [
                    {
                        "family_fingerprint": "NEW",
                        "family_member_hashes": ["new-a", "new-b"],
                        "locations": [
                            {"file": "src/a.py", "start": 1, "end": 2},
                            {"file": "src/b.py", "start": 3, "end": 4},
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    doc = tmp_path / "doc.json"
    doc.write_text(json.dumps({"status": "ok", "families": []}), encoding="utf-8")
    args = dup_check.parse_args(
        [
            "--repo-root",
            str(repo),
            "--code-inventory",
            str(code),
            "--doc-inventory",
            str(doc),
            "--stagnation",
            "0",
        ]
    )
    monkeypatch.setattr(
        dup_check._lineage,
        "propose",
        lambda **_kwargs: [{"new_fingerprint": "NEW", "old_fingerprints": ["OLD"], "relation": "rotation-proposal"}],
    )
    report = dup_check.run(repo, args)
    assert report["lineage_proposals"]
    assert any("ADVISORY (lineage)" in message for message in report["messages"])


def test_provenance_checker_reads_failure_error_and_anchor_mismatch(tmp_path: Path) -> None:
    failure = tmp_path / "failure.xml"
    failure.write_text("<testsuite><testcase><failure /></testcase></testsuite>", encoding="utf-8")
    error = tmp_path / "error.xml"
    error.write_text("<testsuite><testcase><error /></testcase></testsuite>", encoding="utf-8")
    assert provenance_check._junit_fixture_status(failure, "")[0] == "failed"
    assert provenance_check._junit_fixture_status(error, "")[0] == "errored"
    contract = SimpleNamespace(contract_id="contract-x", consumer_path="skills/shared/scripts/consumer.py")
    consumer = tmp_path / "shared/scripts/consumer.py"
    consumer.parent.mkdir(parents=True)
    consumer.write_text("# no anchor\n", encoding="utf-8")
    errors = provenance_check._validate_plugin_anchors(tmp_path, [contract])
    assert any("not anchored" in item for item in errors)


def test_setup_inspect_refuses_changed_plan_identity(tmp_path: Path) -> None:
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(
            sys,
            "argv",
            ["inspect_repo.py", "--repo-root", str(tmp_path), "--expect-plan-identity", "sha256:" + "0" * 64],
        )
        assert setup_inspect.main() == 2
    finally:
        monkeypatch.undo()


def _persist_args(repo: Path, artifact_path: str, markdown: Path) -> SimpleNamespace:
    return SimpleNamespace(
        repo_root=repo,
        artifact_path=artifact_path,
        title=None,
        subject=None,
        markdown_file=markdown,
    )


def test_debug_persistence_refuses_adapter_and_path_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class MissingBootstrapPath:
        def __init__(self, *_args: object) -> None:
            pass

        def resolve(self) -> "MissingBootstrapPath":
            return self

        @property
        def parents(self) -> list[Path]:
            return []

    monkeypatch.setattr(debug_persist, "Path", MissingBootstrapPath)
    with pytest.raises(ImportError, match="not found"):
        debug_persist._load_skill_runtime_bootstrap()
    monkeypatch.setattr(debug_persist, "Path", Path)
    markdown = tmp_path / "debug.md"
    markdown.write_text("debug", encoding="utf-8")
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "out/good.md", markdown))
    monkeypatch.setattr(debug_persist, "load_adapter", lambda _repo: {"errors": ["unhonored"], "data": {}})
    monkeypatch.setattr(debug_persist._version_verdict, "declarations_unhonored", lambda _errors: True)
    assert debug_persist.main() == 1

    monkeypatch.setattr(debug_persist, "load_adapter", lambda _repo: {"errors": [], "data": {"output_dir": "out"}})
    monkeypatch.setattr(debug_persist._version_verdict, "declarations_unhonored", lambda _errors: False)
    monkeypatch.setattr(
        debug_persist._scaffold,
        "payload_for",
        lambda *_args, **_kwargs: {"write_artifact_path": "out/good.md", "artifact_path": "out/good.md"},
    )
    monkeypatch.setattr(debug_persist._scaffold, "validator_command", lambda *_args: "validate")
    monkeypatch.setattr(debug_persist._persistence, "persist_debug_artifact", lambda **_kwargs: {"validated": True})
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "/absolute.md", markdown))
    assert debug_persist.main() == 1
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "out/other.md", markdown))
    assert debug_persist.main() == 1

    outside = tmp_path.parent / "debug-outside"
    outside.mkdir()
    (tmp_path / "out").mkdir()
    (tmp_path / "out/link.md").symlink_to(outside / "link.md")
    monkeypatch.setattr(debug_persist._scaffold, "payload_for", lambda *_args, **_kwargs: {"write_artifact_path": "out/link.md", "artifact_path": "out/link.md"})
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "out/link.md", markdown))
    assert debug_persist.main() == 1
    monkeypatch.setattr(debug_persist._scaffold, "payload_for", lambda *_args, **_kwargs: {"write_artifact_path": "other/good.md", "artifact_path": "other/good.md"})
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "other/good.md", markdown))
    assert debug_persist.main() == 1


def test_debug_persistence_script_entrypoint_runs_the_main_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    markdown = tmp_path / "debug.md"
    markdown.write_text("debug", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "persist_debug_artifact.py",
            "--repo-root",
            str(tmp_path),
            "--artifact-path",
            "../bad.md",
            "--markdown-file",
            str(markdown),
        ],
    )
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(
            str(ROOT / "skills/public/debug/scripts/persist_debug_artifact.py"),
            run_name="__main__",
        )
    assert raised.value.code == 1
