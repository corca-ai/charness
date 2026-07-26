"""The fresh-eye contract owns reviewer result delivery, not just reviewer conduct.

Regression guard for #454: bounded reviewers ran correctly, kept a clean rail-1
boundary, and wrote complete final messages that never reached the parent,
because a named spawn selected a mailbox channel the parent had no tool to read.
The same differential was observed on 2026-06-20 and lost to lesson decay before
it reached a contract, so the rule is pinned here rather than left to prose that
ages out.

Delivery itself is a per-host live claim and is intentionally not asserted here;
these tests pin that the contract *states* the rule and keeps delivery separable
from boundary state.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SHARED_REVIEW = REPO_ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
ENVELOPE = REPO_ROOT / ".claude" / "agents" / "bounded-reviewer.md"


def _unwrapped(path: Path) -> str:
    """Read a prose surface with line wrapping and markdown emphasis collapsed.

    These guards pin what the contract *says*. A reflow that moves a phrase
    across a line break, or a change in which words carry bold, must not read as
    the clause going missing — that is maintenance tax with no safety gain.
    """
    text = path.read_text(encoding="utf-8").replace("*", "").replace("_", "")
    return re.sub(r"\s+", " ", text)


def _shared_review() -> str:
    return _unwrapped(SHARED_REVIEW)


def test_shared_reference_owns_a_result_delivery_section() -> None:
    assert "## Result Delivery" in _shared_review(), (
        "the shared fresh-eye reference is the canonical owner of the delivery rule; "
        "skills cite this section instead of restating it"
    )


def test_delivery_rule_names_the_unnamed_spawn_shape() -> None:
    text = _shared_review()
    assert "without a host addressing or team name" in text, (
        "the contract must state the one-shot spawn shape that returns findings to the caller"
    )


def test_spawn_acceptance_is_not_delivery_proof() -> None:
    text = _shared_review()
    assert "A spawned reviewer is not a received review." in text
    assert "spawn-accepted-no-delivery" in text, (
        "closeout must be able to record delivery failure as a typed state"
    )
    assert "findings-received" in text


def test_delivery_state_stays_separable_from_boundary_state() -> None:
    text = _shared_review()
    assert "Boundary clean and findings received are independent claims" in text, (
        "rail-1 boundary cleanliness and findings delivery must stay separable claims; "
        "collapsing them is the false-confidence failure this guard exists to stop"
    )


def test_blocked_path_probe_requires_findings_not_just_a_spawn() -> None:
    text = _shared_review()
    assert "The probe passes only when the reviewer's findings text reaches you." in text, (
        "an accepted-but-undelivered spawn must fail the availability probe"
    )


def test_do_not_list_forbids_named_one_shot_reviewer_spawns() -> None:
    text = _shared_review()
    tail = text.split("## Do Not", 1)
    assert len(tail) == 2, "the shared reference must keep its Do Not list"
    assert "host addressing or team name to a one-shot bounded reviewer" in tail[1]


def test_envelope_points_reviewers_at_the_delivery_owner() -> None:
    text = _unwrapped(ENVELOPE)
    assert "Result Delivery" in text, (
        "the reviewer envelope must cite the delivery owner rather than restating it"
    )
    assert "final assistant message" in text


# --- #458: the rule must bind for EVERY spawn, not only the review path -------

AGENTS_DOC = REPO_ROOT / "AGENTS.md"
AGENT_DOCS_POLICY = (
    REPO_ROOT / "skills" / "public" / "setup" / "references" / "agent-docs-policy.md"
)


def test_always_loaded_contract_states_the_spawn_shape_rule() -> None:
    """#458: the rule lived only on a review-scoped reference, so it never bound.

    A parent spawning for a non-review reason never opens the fresh-eye reference,
    and the defect's signature is that the spawn SUCCEEDS — so there is no blocked
    signal to send it looking. The rule therefore has to sit on a surface already
    loaded before any spawn. This test is the pin: the #458 fix is otherwise pure
    prose placement, and its own root cause is a rule decaying out of reach.
    """
    text = _unwrapped(AGENTS_DOC)
    assert "Spawn shape" in text, "AGENTS.md must state the spawn-shape rule"
    assert "EVERY spawn" in text, (
        "the rule must be scoped to every spawn; scoping it to reviews is exactly "
        "the #458 defect"
    )
    # Phrase stops before "name" because AGENTS.md renders it as inline code and
    # `_unwrapped` deliberately does not strip backticks.
    assert "without a host addressing or team" in text
    assert "idle notification" in text, (
        "an idle notification reading like success is the signal that misleads a parent"
    )


def test_always_loaded_contract_forbids_a_same_agent_substitute_for_lost_findings() -> None:
    """Lost findings are a delivery failure, never a subagent that returned nothing."""
    text = _unwrapped(AGENTS_DOC)
    assert "delivery failure" in text
    assert "never grounds for a same-agent substitute" in text


def test_consuming_repo_template_carries_the_spawn_shape_rule() -> None:
    """#458 was filed FROM a consuming repo, so charness's own AGENTS.md is not enough.

    `setup` seeds a managed repo's `## Subagent Delegation` from the copy-verbatim
    template here. Without the rule in the template, every setup-normalized repo
    keeps stranding non-review spawns while `setup` reports its AGENTS.md
    conformant — the same scope mismatch #458 names, one level out.
    """
    text = _unwrapped(AGENT_DOCS_POLICY)
    assert "Spawn shape, for every spawn" in text
    assert "without a host addressing or team name" in text  # template has no backticks
    assert "A spawned agent is not a received result" in text


def test_compact_contract_inspector_requires_the_spawn_shape_snippet() -> None:
    """A pre-#458 compact AGENTS.md must read as STALE, not as conformant.

    Without this the inspector silently accepts an older body, which is how the
    rule fails to reach the repos that need it.
    """
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import setup_agent_docs_fresh_eye_lib as lib

    conformant = (
        "## Subagent Delegation\n\n"
        "- standing delegation request for the canonical scopes; a host block is "
        "reported, and no same-agent substitutes are forbidden path is taken\n"
        "- reviewer tier and concrete spawn fields are applied\n"
        "- spawn shape: spawn one-shot subagents without a host addressing or team name\n"
    )
    assert lib.fresh_eye_compact_contract_present(conformant)

    stale = conformant.replace(
        "- spawn shape: spawn one-shot subagents without a host addressing or team name\n",
        "",
    )
    assert not lib.fresh_eye_compact_contract_present(stale), (
        "a compact contract missing the spawn-shape rule must be flagged stale"
    )
