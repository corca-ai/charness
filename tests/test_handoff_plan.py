from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "skills/public/handoff/scripts/plan_handoff_run.py"
SCRIPT_PATH = ROOT / SCRIPT
_handoff_validator = import_repo_module(ROOT / "scripts" / "validate_handoff_artifact.py", "scripts.validate_handoff_artifact")


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
        ["python3", SCRIPT, *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each option's wrapped argparse block contains its own help text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_handoff_plan_help_describes_all_options() -> None:
    result = subprocess.run(
        ["python3", SCRIPT, "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    _assert_help_pairs(
        result.stdout,
        {
            "--repo-root": "Repository root used to resolve handoff adapter and artifact state.",
            "--intent": "Operator intent when known; auto derives only deterministic cases.",
            "--invocation-text": "Original invocation text used to derive handoff intent and routing.",
            "--invoked-directly": "Mark that the handoff skill was invoked directly for chunked routing.",
        },
    )
    assert "--json" not in result.stdout


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
    # state-selection.md is retired from the forced refresh reads (census INLINE
    # MOVE): its Compression Rule gist is inlined in SKILL.md, so the run keeps
    # only next-action state from core and the eval floors on the emitted
    # closeout tokens instead of a redundant re-read. spill-targets.md stays a
    # forced read (its owning-path routing table is genuine depth absent from
    # SKILL.md).
    assert "references/state-selection.md" not in read_paths
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


def test_handoff_plan_derives_refresh_and_pickup_from_invocation_text(tmp_path: Path) -> None:
    # Seeded ("ok"-status) repo, not the live repo root: intent/next_action here
    # must not depend on the live handoff's line count (#10 handoff test brittleness).
    repo = seed_repo(tmp_path, handoff_body())
    refresh = run_plan("--repo-root", str(repo), "--invocation-text", "update the handoff")
    pickup = run_plan("--repo-root", str(repo), "--invocation-text", "resume from handoff after reading trigger")

    assert refresh["intent"]["resolved"] == "refresh"
    assert refresh["intent"]["reason"] == "refresh/update wording in invocation"
    assert pickup["intent"]["resolved"] == "pickup"
    assert pickup["intent"]["reason"] == "pickup/resume wording in invocation"
    assert pickup["next_action"]["kind"] == "follow_workflow_trigger"


def test_handoff_plan_constants_single_sourced_from_validator() -> None:
    # Drift-guard: the planner's MAX_ARTIFACT_LINES/REQUIRED_SECTIONS must never
    # silently diverge from what scripts/validate_handoff_artifact.py enforces.
    module = load_plan_module()
    assert module.MAX_ARTIFACT_LINES == _handoff_validator.MAX_ARTIFACT_LINES
    assert module.REQUIRED_SECTIONS == tuple(_handoff_validator.REQUIRED_SECTIONS)


def test_handoff_plan_degrades_to_default_constants_when_validator_import_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    # The module-level try/except degrades to a fixed default (never a crash at
    # import time) when scripts.validate_handoff_artifact cannot load -- e.g. a
    # portable install without scripts/ vendored. load_repo_module_from_skill_script
    # reaches this via `importlib.import_module`, so forcing THAT call to fail for
    # only this one module name (not resolve_adapter/chunked_routing_lib, which use
    # a different loader) exercises the except branch on a fresh import of the
    # real file.
    real_import_module = importlib.import_module

    def fake_import_module(name, *args, **kwargs):
        if name == "scripts.validate_handoff_artifact":
            raise ModuleNotFoundError(name)
        return real_import_module(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    module = load_plan_module()
    assert module.MAX_ARTIFACT_LINES == 70
    assert module.REQUIRED_SECTIONS == (
        "## Workflow Trigger", "## Current State", "## Next Session", "## Discuss", "## References",
    )


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


def _pickup_body(next_entries: int) -> str:
    lines = [
        "# Demo Handoff",
        "",
        "## Workflow Trigger",
        "",
        "- trigger",
        "",
        "## Current State",
        "",
        "- state",
        "",
        "## Next Session",
        "",
    ]
    lines.extend(f"{index}. Task {index} to do." for index in range(1, next_entries + 1))
    lines.extend(
        [
            "",
            "## Discuss",
            "",
            "- discuss",
            "",
            "## References",
            "",
            "- [guide](docs/guide.md)",
            "",
        ]
    )
    return "\n".join(lines)


def _pickup_reads(repo: Path, invocation_text: str) -> set[str]:
    plan = run_plan(
        "--repo-root",
        str(repo),
        "--intent",
        "pickup",
        "--invocation-text",
        invocation_text,
    )
    return {read["path"] for read in plan["required_reads"]}


def test_handoff_plan_pickup_requires_continuation_when_ambiguous(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _pickup_body(3))
    reads = _pickup_reads(repo, "resume from the current state")
    # Several plausible pickups + no pinned task -> continuation-sequence.md orders them.
    assert "references/continuation-sequence.md" in reads
    assert "references/workflow-trigger.md" not in reads  # retired from forced pickup reads (#410 Slice 9): gist inlined, artifact carries the trigger


def test_handoff_plan_pickup_skips_continuation_when_single_plausible_pickup(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _pickup_body(1))
    reads = _pickup_reads(repo, "resume from the current state")
    # Only one plausible pickup -> no sequencing choice, so the planner does not force it.
    assert "references/continuation-sequence.md" not in reads
    assert "references/workflow-trigger.md" not in reads


def test_handoff_plan_pickup_skips_continuation_when_task_pinned(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _pickup_body(3))
    # A clearly-pinned task overrides state ambiguity (mirrors the pickup spec prompt).
    reads = _pickup_reads(repo, "resume the pinned task and start the named workflow")
    assert "references/continuation-sequence.md" not in reads


def test_handoff_plan_pickup_skips_continuation_when_issue_pinned(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _pickup_body(3))
    reads = _pickup_reads(repo, "resume and work on #412")
    assert "references/continuation-sequence.md" not in reads


def test_handoff_plan_pickup_keeps_continuation_when_unpinned(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _pickup_body(3))
    # "unpinned" must NOT read as a pinned task: several plausible pickups remain.
    reads = _pickup_reads(repo, "the next pickup is unpinned, resume from the current state")
    assert "references/continuation-sequence.md" in reads


def test_handoff_plan_pickup_skips_continuation_when_file_path_pinned(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _pickup_body(3))
    # A concrete non-handoff file path names one target, so no sequencing remains
    # among the plausible pickups -> continuation-sequence.md is not forced.
    reads = _pickup_reads(repo, "resume work on skills/public/impl/SKILL.md")
    assert "references/continuation-sequence.md" not in reads
    assert "references/workflow-trigger.md" not in reads


def test_artifact_summary_counts_zero_when_entry_parse_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The `## Next Session` entry count is defensive: if the shared entry parser
    # raises, the planner degrades to zero plausible pickups instead of crashing.
    module = load_plan_module()
    artifact = tmp_path / "handoff.md"
    artifact.write_text("# H\n\n## Next Session\n\n- one\n", encoding="utf-8")

    def _raise(_raw: str):
        raise ValueError("unparseable handoff entries")

    monkeypatch.setattr(module.chunked_routing_lib, "parse_handoff_entries", _raise)
    summary = module._artifact_summary(tmp_path, {"artifact_path": "handoff.md"})
    assert summary["exists"] is True
    assert summary["next_session_entry_count"] == 0
