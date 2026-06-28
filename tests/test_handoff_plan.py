from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "skills/public/handoff/scripts/plan_handoff_run.py"
SCRIPT_PATH = ROOT / SCRIPT


def load_plan_module():
    spec = importlib.util.spec_from_file_location("handoff_plan_test_module", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def handoff_body(*, current_lines: int = 1, omit_references: bool = False, dated_session: bool = False) -> str:
    lines = [
        "# Demo Handoff",
        "",
        "## Workflow Trigger",
        "",
        "- trigger",
        "",
        "## Current State",
        "",
    ]
    lines.extend(f"- state {index}" for index in range(current_lines))
    lines.extend(
        [
            "",
            "## Next Session",
            "",
            "- next",
            "",
            "## Discuss",
            "",
            "- discuss",
            "",
        ]
    )
    if dated_session:
        lines.extend(["## This Session (2026-06-24)", "", "- stale diary", ""])
    if not omit_references:
        lines.extend(["## References", "", "- [guide](docs/guide.md)", ""])
    return "\n".join(lines)


def seed_repo(tmp_path: Path, body: str, *, adapter: bool = True) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir()
    if adapter:
        (repo / ".agents" / "handoff-adapter.yaml").write_text(
            "\n".join(
                [
                    "version: 1",
                    "repo: demo",
                    "language: en",
                    "output_dir: docs",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    (repo / "docs" / "handoff.md").write_text(body, encoding="utf-8")
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    return repo


def run_plan(*args: str, cwd: Path | None = None) -> dict[str, object]:
    result = subprocess.run(
        ["python3", SCRIPT, "--json", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_handoff_plan_bootstrap_reports_missing_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_plan_module()

    class MissingCandidate:
        def is_file(self) -> bool:
            return False

    class Ancestor:
        def __truediv__(self, _name: str) -> MissingCandidate:
            return MissingCandidate()

    class FakePath:
        def __init__(self, _value: str) -> None:
            pass

        def resolve(self) -> "FakePath":
            return self

        @property
        def parents(self) -> list[Ancestor]:
            return [Ancestor()]

    monkeypatch.setattr(module, "Path", FakePath)
    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        module._load_skill_runtime_bootstrap()


def test_handoff_plan_reports_artifact_gates_and_required_reads() -> None:
    plan = run_plan("--repo-root", ".", "--intent", "refresh")

    assert plan["schema_version"] == "handoff.run_plan.v1"
    assert plan["adapter"]["artifact_path"] == "docs/handoff.md"
    assert plan["artifact"]["exists"] is True
    assert plan["intent"]["resolved"] == "refresh"
    assert plan["next_action"]["kind"] in {
        "refresh_handoff",
        "repair_or_prune_handoff",
    }

    read_paths = {read["path"] for read in plan["required_reads"]}
    assert "docs/handoff.md" in read_paths
    assert "references/state-selection.md" in read_paths
    assert "references/spill-targets.md" in read_paths

    gates = {packet["id"]: packet for packet in plan["gate_packets"]}
    assert gates["handoff-artifact-shape"]["available"] is True
    assert gates["current-pointer-freshness"]["available"] is True
    assert "deterministic shape" in gates["handoff-artifact-shape"]["trust_model"]


def test_handoff_plan_routes_direct_invocation_to_chunked_routing() -> None:
    plan = run_plan("--repo-root", ".", "--invoked-directly")

    assert plan["intent"]["resolved"] == "chunked_routing"
    assert plan["intent"]["chunked_routing"]["should_run"] is True
    assert plan["next_action"]["kind"] == "run_chunked_routing"
    assert plan["next_action"]["command"].endswith("--repo-root . --with-issues")
    assert {
        "path": "references/chunked-routing.md",
        "kind": "reference",
        "base": "skill",
        "why": "deterministic trigger says route backlog before pickup",
    } in plan["required_reads"]


def test_handoff_plan_routes_documented_slash_invocation_to_chunked_routing() -> None:
    plan = run_plan("--repo-root", ".", "--invocation-text", "/handoff")

    assert plan["intent"]["resolved"] == "chunked_routing"
    assert plan["next_action"]["kind"] == "run_chunked_routing"


def test_handoff_plan_routes_namespaced_slash_invocation_to_chunked_routing() -> None:
    # The plugin-namespaced `/charness:handoff` IS the handoff command, not "another
    # slash command": a bare namespaced invocation (no --invoked-directly) must
    # resolve to chunked_routing. The default claim-fidelity scenario relies on this
    # production path, so guard it at the planner layer, not only in the chunker fixture.
    plan = run_plan("--repo-root", ".", "--invocation-text", "/charness:handoff")

    assert plan["intent"]["resolved"] == "chunked_routing"
    assert plan["next_action"]["kind"] == "run_chunked_routing"


def test_handoff_plan_does_not_chunk_explicit_task_directive() -> None:
    plan = run_plan(
        "--repo-root",
        ".",
        "--invocation-text",
        "/handoff fix #396",
        "--invoked-directly",
    )

    assert plan["intent"]["chunked_routing"]["should_run"] is False
    assert plan["intent"]["resolved"] == "judge_from_user_request"
    assert plan["next_action"]["kind"] != "run_chunked_routing"


def test_handoff_plan_derives_refresh_and_pickup_from_invocation_text() -> None:
    refresh = run_plan("--repo-root", ".", "--invocation-text", "update the handoff")
    pickup = run_plan("--repo-root", ".", "--invocation-text", "resume from handoff after reading trigger")

    assert refresh["intent"]["resolved"] == "refresh"
    assert refresh["intent"]["reason"] == "refresh/update wording in invocation"
    assert pickup["intent"]["resolved"] == "pickup"
    assert pickup["intent"]["reason"] == "pickup/resume wording in invocation"
    assert pickup["next_action"]["kind"] == "follow_workflow_trigger"


def test_handoff_plan_reports_artifact_statuses_that_require_repair(tmp_path: Path) -> None:
    cases = [
        ("over_limit", handoff_body(current_lines=65)),
        ("diary_smell", handoff_body(dated_session=True)),
        ("shape_issue", handoff_body(omit_references=True)),
        ("near_limit", handoff_body(current_lines=43)),
    ]
    for status, body in cases:
        repo = seed_repo(tmp_path / status, body)
        plan = run_plan("--repo-root", str(repo), "--intent", "refresh")
        assert plan["artifact"]["status"] == status
        assert plan["next_action"]["kind"] == "repair_or_prune_handoff"


def test_handoff_plan_marks_missing_adapter_reads_as_skill_relative(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, handoff_body(), adapter=False)

    plan = run_plan("--repo-root", str(repo), "--intent", "refresh")

    assert plan["adapter"]["found"] is False
    assert {
        "path": "references/adapter-contract.md",
        "kind": "reference",
        "base": "skill",
        "why": "adapter was missing, warned, or invalid",
    } in plan["required_reads"]


def test_handoff_plan_scaffolds_missing_artifact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / ".agents" / "handoff-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: docs",
                "",
            ]
        ),
        encoding="utf-8",
    )

    plan = run_plan("--repo-root", str(repo), "--intent", "refresh")

    assert plan["artifact"]["status"] == "missing"
    assert plan["next_action"]["kind"] == "scaffold_missing_artifact"
    assert plan["required_reads"][0]["base"] == "skill"
    assert plan["gate_packets"][0]["id"] == "handoff-artifact-shape"
    assert plan["gate_packets"][0]["available"] is False
