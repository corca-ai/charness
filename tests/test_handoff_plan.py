from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "skills/public/handoff/scripts/plan_handoff_run.py"
SCRIPT_PATH = ROOT / SCRIPT
CHUNKED_ROUTING_TEXT = (ROOT / "skills/public/handoff/references/chunked-routing.md").read_text(encoding="utf-8")
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
            "--intent": "Declare the routing decision you judged from the user request",
            "--invoked-directly": "Declare that the skill was launched bare with no task",
        },
    )
    assert "--json" not in result.stdout
    # The text-classification interface is DELETED, not merely unused: while it
    # existed, the model retyped the user's message into it and a regex classified
    # the paraphrase.
    assert "--invocation-text" not in result.stdout
    # Deleted with the pickup-ambiguity heuristic it fed (operator ruling 2026-08-11).
    assert "--pickup-target" not in result.stdout


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
    assert [read for read in plan["required_reads"] if read.get("kind") == "preflight"] == [], (
        "chunked routing reads the handoff but must not be briefed to author it"
    )
    assert "draft_goal_from_chunk.py" in CHUNKED_ROUTING_TEXT
    assert "must **never** rewrite `handoff.md`" in CHUNKED_ROUTING_TEXT.replace("\n", " ")


def test_handoff_plan_routes_declared_chunked_routing_intent() -> None:
    # `chunked_routing` is a declarable intent, so an agent that judged the rule
    # from the user's actual message can say so without a bare-launch flag.
    plan = run_plan("--repo-root", ".", "--intent", "chunked_routing")

    assert plan["intent"]["resolved"] == "chunked_routing"
    assert plan["intent"]["reason"] == "explicit --intent"
    assert plan["intent"]["chunked_routing"]["should_run"] is True
    assert plan["next_action"]["kind"] == "run_chunked_routing"


def test_handoff_plan_refuses_to_guess_intent_without_a_declaration(tmp_path: Path) -> None:
    # The routing floor's whole repair: with no declaration and no structural
    # signal, the planner hands the decision BACK to the judge instead of
    # inferring it from prose. It must not silently pick pickup or refresh.
    repo = seed_repo(tmp_path, handoff_body())
    plan = run_plan("--repo-root", str(repo))

    assert plan["intent"]["resolved"] == "judge_from_user_request"
    assert plan["intent"]["chunked_routing"]["should_run"] is False
    # And it must not be steered anywhere either: an undeclared run that fell
    # through to `refresh_handoff` would be guessing again, unconditionally and
    # on the writing side. The next action is to decide and re-run.
    assert plan["next_action"]["kind"] == "judge_the_user_request"
    assert "--intent" in plan["next_action"]["command"]
    # Nor is it briefed on writing a surface it has not decided to write.
    assert [r for r in plan["required_reads"] if r.get("kind") == "preflight"] == []


def test_handoff_plan_takes_declared_intent_over_direct_invocation_shape(tmp_path: Path) -> None:
    # A bare launch that nonetheless carries a task ("/handoff fix #396") is the
    # case the deleted regex handled by re-reading the message. The agent read it
    # already, so its declaration wins over the structural default.
    repo = seed_repo(tmp_path, handoff_body())
    plan = run_plan("--repo-root", str(repo), "--intent", "pickup", "--invoked-directly")

    assert plan["intent"]["resolved"] == "pickup"
    assert plan["intent"]["chunked_routing"]["should_run"] is False
    assert plan["next_action"]["kind"] == "follow_workflow_trigger"


def test_handoff_plan_honors_declared_refresh_and_pickup(tmp_path: Path) -> None:
    # Seeded ("ok"-status) repo, not the live repo root: intent/next_action here
    # must not depend on the live handoff's line count (#10 handoff test brittleness).
    repo = seed_repo(tmp_path, handoff_body())
    refresh = run_plan("--repo-root", str(repo), "--intent", "refresh")
    pickup = run_plan("--repo-root", str(repo), "--intent", "pickup")

    assert refresh["intent"]["resolved"] == "refresh"
    assert refresh["intent"]["reason"] == "explicit --intent"
    assert pickup["intent"]["resolved"] == "pickup"
    assert pickup["intent"]["reason"] == "explicit --intent"
    assert pickup["next_action"]["kind"] == "follow_workflow_trigger"


def test_handoff_plan_carries_authoring_rules_as_a_read_before_writing(tmp_path: Path) -> None:
    # The constraint forecast moved from `gate_packets` (evidence to run against
    # something already written) into `required_reads` (open before acting), and
    # carries the rules-mode command, which answers with NO target.
    # The live repo root, which is where `scripts/` is actually vendored.
    refresh = run_plan("--repo-root", ".", "--intent", "refresh")

    rules = [r for r in refresh["required_reads"] if r.get("kind") == "preflight"]
    assert len(rules) == 1
    assert rules[0]["path"] == "scripts/check_doc_authoring_preflight.py"
    assert "--as-surface handoff" in rules[0]["command"]
    assert "--path" not in rules[0]["command"]


def test_the_authoring_read_is_keyed_on_the_ACTION_not_the_intent(tmp_path: Path) -> None:
    """A pickup gets the rules only when its next action actually authors.

    This used to assert that a pickup NEVER carries the read, which contradicted
    the rule the planner deliberately moved to: a pickup against a bloated or
    mis-shaped handoff is sent to PRUNE it, and keying on the intent left exactly
    that case briefed by nothing. The old assertion also ran against the LIVE
    repo, so whether it passed depended on the checked-in handoff's current shape
    rather than on the contract — it was already failing on `origin/main` for
    that reason. Seeded fixtures pin both directions instead.
    """
    ordinary = run_plan("--repo-root", str(seed_repo(tmp_path / "a", handoff_body())), "--intent", "pickup")
    assert ordinary["next_action"]["kind"] not in ("refresh_handoff", "repair_or_prune_handoff")
    assert [r for r in ordinary["required_reads"] if r.get("kind") == "preflight"] == []

    bloated = run_plan(
        "--repo-root",
        str(seed_repo(tmp_path / "b", handoff_body(current_lines=4000))),
        "--intent",
        "pickup",
    )
    if bloated["next_action"]["kind"] in ("refresh_handoff", "repair_or_prune_handoff"):
        # The seeded repo has no vendored `scripts/`, so the read is correctly
        # dropped rather than pointing at a command that cannot run; the sibling
        # test below owns that half. What this pins is the KEY: an authoring
        # action, reached from a pickup intent, is what the planner asks about.
        assert bloated["intent"]["resolved"] == "pickup"


def test_handoff_plan_omits_authoring_rules_when_the_script_is_not_vendored(tmp_path: Path) -> None:
    # Portable install without `scripts/`: the read is dropped rather than
    # pointing an author at a command that cannot run.
    repo = seed_repo(tmp_path, handoff_body())
    plan = run_plan("--repo-root", str(repo), "--intent", "refresh")

    assert [r for r in plan["required_reads"] if r.get("kind") == "preflight"] == []


def test_handoff_plan_constants_single_sourced_from_validator() -> None:
    # Drift-guard: the planner's MAX_CONTENT_LINES/REQUIRED_SECTIONS must never
    # silently diverge from what scripts/validate_handoff_artifact.py enforces.
    module = load_plan_module()
    assert module.MAX_CONTENT_LINES == _handoff_validator.MAX_CONTENT_LINES
    # The COUNT must not drift either: a planner that agrees on the ceiling but
    # counts different lines reports a status the gate contradicts.
    sample = ["# H", "", "## Current State", "", "- a", "## References", "- [x](y.md)"]
    assert module.content_lines(sample) == _handoff_validator.content_lines(sample)
    assert module.REQUIRED_SECTIONS == tuple(_handoff_validator.REQUIRED_SECTIONS)


def test_handoff_plan_degrades_to_default_constants_when_validator_import_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    # The module-level try/except degrades to a fixed default (never a crash at
    # import time) when scripts.validate_handoff_artifact cannot load -- e.g. a
    # portable install without scripts/ vendored. load_repo_module_from_skill_script
    # reaches this via `importlib.import_module`, so forcing THAT call to fail for
    # only this one module name (not resolve_adapter, which uses
    # a different loader) exercises the except branch on a fresh import of the
    # real file.
    real_import_module = importlib.import_module

    def fake_import_module(name, *args, **kwargs):
        if name == "scripts.validate_handoff_artifact":
            raise ModuleNotFoundError(name)
        return real_import_module(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    module = load_plan_module()
    assert module.MAX_CONTENT_LINES == 58
    # The local counting fallback must still be used, not left as None.
    assert module.content_lines(["# H", "", "## Discuss", "- a"]) == ["# H", "- a"]
    assert module.REQUIRED_SECTIONS == (
        "## Workflow Trigger", "## Current State", "## Next Session", "## Discuss", "## References",
    )


def test_handoff_plan_reports_artifact_statuses_that_require_repair(tmp_path: Path) -> None:
    cases = [
        ("over_limit", handoff_body(current_lines=60)),
        ("diary_smell", handoff_body(dated_session=True)),
        ("shape_issue", handoff_body(omit_references=True)),
        ("near_limit", handoff_body(current_lines=48)),
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


def _pickup_reads(repo: Path, *extra: str) -> set[str]:
    plan = run_plan("--repo-root", str(repo), "--intent", "pickup", *extra)
    return {read["path"] for read in plan["required_reads"]}


def test_handoff_plan_pickup_forces_no_reference_read_whatever_the_entry_count(tmp_path: Path) -> None:
    # A pickup's forced reads are the ARTIFACT and nothing else. The planner used to
    # decide between one and several plausible pickups by COUNTING `## Next Session`
    # entries and forcing continuation-sequence.md on the "ambiguous" arm -- a prose
    # parser rendering a verdict about the operator's intent, which renumbering the
    # handoff or splitting one item in two could flip. Deleted by operator ruling
    # 2026-08-11; ordering plausible pickups is SKILL.md prose the agent opens by
    # judgment. Falsifiable both ways: the entry count must not change the answer.
    for entry_count in (1, 3):
        reads = _pickup_reads(seed_repo(tmp_path / f"repo{entry_count}", _pickup_body(entry_count)))
        assert not {read for read in reads if read.startswith("references/")}, entry_count
        assert "docs/handoff.md" in reads, entry_count


def test_handoff_plan_pickup_target_flag_is_gone(tmp_path: Path) -> None:
    # The flag existed only to feed the deleted ambiguity predicate. Argparse must
    # REJECT it rather than silently accept and ignore it, so a caller still passing
    # it learns the mechanism is gone instead of getting the same plan either way.
    repo = seed_repo(tmp_path, _pickup_body(3))
    result = subprocess.run(
        ["python3", SCRIPT, "--repo-root", str(repo), "--intent", "pickup", "--pickup-target", "Task 2"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "--pickup-target" in result.stderr


def test_artifact_summary_carries_no_next_session_entry_count(tmp_path: Path) -> None:
    # The count was computed for one consumer -- the deleted ambiguity predicate --
    # and reported in the plan envelope, where a reader could mistake it for a fact
    # the planner acts on. It is gone from the summary, not merely unread.
    module = load_plan_module()
    artifact = tmp_path / "handoff.md"
    artifact.write_text("# H\n\n## Next Session\n\n- one\n- two\n", encoding="utf-8")
    summary = module._artifact_summary(tmp_path, {"artifact_path": "handoff.md"})
    assert summary["exists"] is True
    assert "next_session_entry_count" not in summary


def test_handoff_plan_briefs_the_rules_whenever_the_next_action_writes(tmp_path: Path) -> None:
    # Keying the authoring-rules read on the INTENT left one case briefed by
    # nothing: a pickup against a bloated artifact is sent to prune it, which is
    # authoring. The next action is what says whether the run writes.
    repo = seed_repo(tmp_path, handoff_body(current_lines=60))
    (repo / "scripts").mkdir()
    # Seed BOTH files the emitted command needs. The rules mode imports
    # `doc_authoring_rules` at runtime, so a repo carrying only the entrypoint
    # gets a command that dies on import.
    for name in ("check_doc_authoring_preflight.py", "doc_authoring_rules.py"):
        shutil.copy(ROOT / "scripts" / name, repo / "scripts")
    plan = run_plan("--repo-root", str(repo), "--intent", "pickup")

    assert plan["next_action"]["kind"] == "repair_or_prune_handoff"
    assert [r for r in plan["required_reads"] if r.get("kind") == "preflight"]

    # The probe must cover every file the emitted command needs, not just the
    # entrypoint. Deleting the runtime-imported half must SUPPRESS the read;
    # while the probe checked one file, this repo state still advertised it.
    (repo / "scripts" / "doc_authoring_rules.py").unlink()
    degraded = run_plan("--repo-root", str(repo), "--intent", "pickup")
    assert [r for r in degraded["required_reads"] if r.get("kind") == "preflight"] == []
