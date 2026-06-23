from __future__ import annotations

from .support import ROOT

SKILL = ROOT / "skills" / "public" / "issue" / "SKILL.md"
CLOSEOUT = ROOT / "skills" / "public" / "issue" / "references" / "closeout-discipline.md"
SHAPING = ROOT / "skills" / "public" / "issue" / "references" / "issue-shaping.md"
RESOLVE_FLOW = ROOT / "skills" / "public" / "issue" / "references" / "resolve-flow.md"


def _read(path) -> str:
    return path.read_text(encoding="utf-8")


def test_issue_skill_pins_verified_ledger_for_new_closeout() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)

    assert "verified" in skill
    assert "{repo, number, url}" in skill
    assert "ledger" in skill
    assert "Created-Issue Ledger" in closeout
    assert "never report a number, repo, or status not present in the" in closeout


def test_issue_skill_pins_target_durability_on_retry() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)
    resolve_flow = _read(RESOLVE_FLOW)

    assert "durable workflow state" in skill
    assert "target_unavailable" in skill
    assert "silently switching to" in skill
    assert "Target Durability" in closeout
    assert "do not re-walk the fallback ladder" in closeout
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
    assert "preserved original context" in skill


def test_issue_skill_guardrails_block_silent_retarget_and_chat_memory_closeout() -> None:
    skill = _read(SKILL)

    assert "Do not silently retarget on retry" in skill
    assert "Render `issue new` closeout only from the verified" in skill
    assert "external source" in skill


def test_issue_skill_cites_closeout_discipline_at_each_anchor() -> None:
    skill = _read(SKILL)

    citations = [
        line for line in skill.splitlines()
        if "references/closeout-discipline.md" in line
    ]
    assert len(citations) >= 3, (
        f"expected closeout-discipline.md cited from step 3, Target Rules, "
        f"and step 6 anchors plus References list; found: {citations}"
    )


def test_issue_resolve_prefers_autoclose_carriers_before_manual_close() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)
    resolve_flow = _read(RESOLVE_FLOW)
    brief = _read(ROOT / "skills" / "public" / "issue" / "references" / "resolution-brief.md")

    assert "prefer GitHub auto-close via explicit close keywords" in skill
    assert "manual close is" in skill
    assert "the fallback, not the default success path" in skill
    assert "Resolve Auto-Close Linkage" in closeout
    assert "PR body" in closeout
    assert "commit body" in closeout
    assert "auto-close the normal closeout path" in resolve_flow
    assert "PR body or direct-to-default commit body" in brief
    assert "preferred closeout carrier" in brief
    assert "re-read GitHub state after comment plus close" in closeout
    assert "command success alone is not closeout" in closeout


def test_issue_closeout_draft_validation_runs_before_mutation() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)

    assert "validate-closeout-draft" in skill
    assert "Before a PR body, direct commit body, or manual close comment is published" in closeout
    assert "fails before any GitHub mutation" in closeout


def test_issue_closeout_covers_release_helper_issue_verification() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)
    resolve_flow = _read(RESOLVE_FLOW)
    release_cli = _read(ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_cli.py")
    publication_boundary = _read(ROOT / "skills" / "public" / "release" / "references" / "publication-boundary.md")

    assert "--close-issue <number>" in skill
    assert "issue_closeout.status: verified" in skill
    assert "Release-driven direct-to-default work follows the same linkage" in closeout
    assert "post-push issue verification payload" in resolve_flow
    assert "--close-issue" in release_cli
    assert "payload.distinct_channel_verification" in publication_boundary


def test_issue_closeout_separates_carrier_from_lifecycle_publication() -> None:
    closeout = _read(CLOSEOUT)
    achieve_lifecycle = _read(
        ROOT / "skills" / "public" / "achieve" / "references" / "lifecycle.md"
    )

    assert "Issue-resolution carrier publication" in closeout
    assert "separate publication surfaces" in closeout
    assert "second docs-only issue-closeout push" in achieve_lifecycle
