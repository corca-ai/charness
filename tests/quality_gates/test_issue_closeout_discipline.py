from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, fake_gh_env, run_script

SKILL = ROOT / "skills" / "public" / "issue" / "SKILL.md"
CLOSEOUT = ROOT / "skills" / "public" / "issue" / "references" / "closeout-discipline.md"
SHAPING = ROOT / "skills" / "public" / "issue" / "references" / "issue-shaping.md"
RESOLVE_FLOW = ROOT / "skills" / "public" / "issue" / "references" / "resolve-flow.md"
SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def _read(path) -> str:
    return path.read_text(encoding="utf-8")


def _issue_plan(tmp_path: Path, *args: str) -> dict:
    result = run_script(
        SCRIPT,
        "plan",
        "--repo-root",
        str(tmp_path),
        *args,
        env=fake_gh_env(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_issue_skill_pins_verified_ledger_for_new_closeout() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)

    assert "verified" in skill
    assert "{repo, number, url}" in skill
    assert "ledger" in skill
    assert "Created-Issue Ledger" in closeout
    assert "never report a number, repo, or status not present in the" in closeout


def test_issue_new_closeout_requires_title_body_preview_and_warning() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)

    assert "helper-returned title" in skill
    assert "body_preview" in skill
    assert "body_verified" in skill
    assert "Created <repo>#<number>: <title> (<url>)" in closeout
    assert "Body summary: <one to three sentences from body_preview>" in closeout
    assert "warning: body was not verified" in closeout


def test_issue_skill_pins_target_durability_on_retry() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)
    resolve_flow = _read(RESOLVE_FLOW)

    assert "durable workflow state" in skill
    assert "target_unavailable" in skill
    assert "Target Durability" in closeout
    assert "do not re-walk the fallback ladder" in closeout
    assert "never silently fall through" in closeout
    assert "durable workflow state" in resolve_flow


def test_issue_shaping_requires_external_source_identity() -> None:
    shaping = _read(SHAPING)
    closeout = _read(CLOSEOUT)
    skill = _read(SKILL)

    assert "source identity" in shaping
    assert "Slack thread" in shaping
    assert "preserve the original user context" in shaping
    assert "External-Source Identity" in closeout
    assert "gathered" in closeout
    # #324: the Source block must mark an external origin and require one
    # auditable preservation form (Source text / Re-read obligation / degraded).
    assert "Source origin:" in closeout
    assert "Re-read obligation:" in closeout
    assert "source identity/preservation" in skill


def test_issue_skill_guardrails_block_silent_retarget_and_chat_memory_closeout() -> None:
    skill = _read(SKILL)

    assert "Target repo is durable workflow state" in skill
    assert "target_unavailable" in skill
    assert "stale local note" in skill
    assert "source identity/preservation" in skill


def test_issue_planner_requires_closeout_discipline_for_new_and_resolve(tmp_path: Path) -> None:
    new_plan = _issue_plan(tmp_path, "--intent", "new")
    resolve_plan = _issue_plan(tmp_path, "--intent", "resolve", "--", "42")

    assert "references/closeout-discipline.md" in {ref["path"] for ref in new_plan["required_reads"]}
    assert "references/closeout-discipline.md" in {ref["path"] for ref in resolve_plan["required_reads"]}


def test_issue_resolve_prefers_autoclose_carriers_before_manual_close() -> None:
    skill = _read(SKILL)
    skill_flat = " ".join(skill.split())
    closeout = _read(CLOSEOUT)
    resolve_flow = _read(RESOLVE_FLOW)
    brief = _read(ROOT / "skills" / "public" / "issue" / "references" / "resolution-brief.md")

    assert "explicit close keywords when auto-close is available" in skill_flat
    assert "Resolve Auto-Close Linkage" in closeout
    assert "PR body" in closeout
    assert "commit body" in closeout
    assert "auto-close the normal closeout path" in resolve_flow
    assert "PR body or direct-to-default commit body" in brief
    assert "preferred closeout carrier" in brief
    assert "re-read GitHub state after comment plus close" in closeout
    assert "command success alone is not closeout" in closeout


def test_issue_closeout_draft_validation_runs_before_mutation(tmp_path: Path) -> None:
    plan = _issue_plan(tmp_path, "--intent", "resolve", "--", "42")
    closeout = _read(CLOSEOUT)

    gate_commands = {gate.get("id"): gate.get("command") for gate in plan["gate_packets"]}
    assert "validate-closeout-draft" in gate_commands["closeout-draft"]
    assert "Before a PR body, direct commit body, or manual close comment is published" in closeout
    assert "fails before any GitHub mutation" in closeout


def test_issue_closeout_draft_gate_names_the_stub_producer_not_only_the_validator(tmp_path: Path) -> None:
    """The closeout shape must be HANDED to the author at the gate, not discovered
    by failing the validator. The `closeout-draft` packet names its validator; it
    must also name `describe_closeout_draft_shape.py` (+ `--stub`), the producer
    that renders the enforced shape live from the verifier constants."""
    plan = _issue_plan(tmp_path, "--intent", "resolve", "--", "42")

    packet = next(gate for gate in plan["gate_packets"] if gate["id"] == "closeout-draft")
    assert "describe_closeout_draft_shape.py" in packet["shape_command"]
    assert packet["stub_command"].endswith("--stub")
    assert "describe_closeout_draft_shape.py" in packet["stub_command"]
    assert "before drafting" in packet["shape_run_when"]
    assert (ROOT / "skills/public/issue/scripts/describe_closeout_draft_shape.py").is_file()


def test_issue_closeout_covers_release_helper_issue_verification() -> None:
    closeout = _read(CLOSEOUT)
    resolve_flow = _read(RESOLVE_FLOW)
    release_cli = _read(ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_cli.py")
    publication_boundary = _read(ROOT / "skills" / "public" / "release" / "references" / "publication-boundary.md")

    assert "Release-driven direct-to-default work follows the same linkage" in closeout
    assert "post-push issue verification payload" in resolve_flow
    assert "--close-issue" in release_cli
    assert "payload.distinct_channel_verification" in publication_boundary


def test_issue_closeout_separates_carrier_from_lifecycle_publication() -> None:
    closeout = _read(CLOSEOUT)
    # Issue-resolution carrier vs. lifecycle-artifact publication lives in the
    # After-phase file (lifecycle.md was split by phase).
    achieve_lifecycle = _read(
        ROOT / "skills" / "public" / "achieve" / "references" / "lifecycle-after.md"
    )

    assert "Issue-resolution carrier publication" in closeout
    assert "separate publication surfaces" in closeout
    assert "second docs-only issue-closeout push" in achieve_lifecycle
