from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module
from scripts.setup_agent_docs_lib import _detect_charness_subagent_policy
from scripts.setup_skill_routing_lib import (
    skill_routing_declares_charness_management,
    skill_routing_semantically_complete,
)

from .support import ROOT

_render_skill_routing = import_repo_module(
    ROOT / "skills/public/setup/scripts/render_skill_routing.py",
    "skills.public.setup.scripts.render_skill_routing",
)


def run_render_skill_routing(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["render_skill_routing.py", *args])
    returncode = _render_skill_routing.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_setup_render_skill_routing_defaults_to_compact_mode(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["recommended_action"] == "create_agents_with_skill_routing"
    assert payload["skill_routing_mode"] == "compact"
    assert payload["skill_routing_mode_source"] == "default"
    assert payload["listed_skill_ids"] == []
    # 2026-07-04 revision: session start routes directly instead of always
    # The hook/context path no longer invokes a public semantic router.
    # discovery or a missing/stale/unclear route.
    assert "At session start, a pickup follows docs/handoff.md" in payload["markdown"]
    assert "charness catalog list --repo-root <repo>" in payload["markdown"]
    assert "installed skill metadata and model judgment" in payload["markdown"]
    assert "choose the durable workflow directly" in payload["markdown"]
    assert "if the command returns nonzero" in payload["markdown"]
    assert "SessionStart hook" in payload["markdown"]
    assert "release-note style summary or chat-ready human update" not in payload["markdown"]


def test_setup_render_skill_routing_suggests_add_block_for_mature_agents(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")

    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["agents_has_skill_routing"] is False
    assert payload["recommended_action"] == "add_skill_routing_block"


def test_setup_render_skill_routing_reviews_drifted_existing_block(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Agents\n\n## Skill Routing\n\nFor task-oriented sessions, use local judgment.\n",
        encoding="utf-8",
    )

    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["agents_has_skill_routing"] is True
    assert payload["skill_routing_matches_compact_block"] is False
    assert payload["recommended_action"] == "review_existing_skill_routing"
    assert any("charness catalog list --repo-root <repo>" in item for item in payload["missing_expected_snippets"])


def test_setup_render_skill_routing_leaves_semantically_complete_block(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly.",
                "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
                "If the command returns nonzero, report the command failure rather than concluding skills are unavailable.",
                "External URLs and source links route through `gather` before deciding.",
                "Validation closeout and operator reading tests route through `quality`.",
                "The SessionStart hook may inject this context; it remains context-only.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_matches_compact_block"] is False
    assert payload["skill_routing_semantically_complete"] is True
    assert payload["recommended_action"] == "leave_as_is"
    assert payload["missing_expected_snippets"] == []


def test_setup_render_skill_routing_reviews_block_without_direct_or_failure_actions(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment.",
                "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
                "External URLs and source links route through `gather` before deciding.",
                "Validation closeout and operator reading tests route through `quality`.",
                "The SessionStart hook may inject this context; it remains context-only.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_semantically_complete"] is False
    assert payload["recommended_action"] == "review_existing_skill_routing"


def _shipped_routing_section_body() -> str:
    """The REAL block `setup` tells an operator to write, split at its own heading.

    Deliberately not a fixture. Every pre-#552 fixture for this predicate — the five
    above and the routing preamble inside
    `test_subagent_delegation_ladder.py::test_the_shipped_setup_template_satisfies_BOTH_readers_of_the_contract`
    — hand-wrote `context-only`, so all of them passed while the surface `setup`
    actually writes failed. A fixture spells the contract the way whichever matcher the
    author had in mind wants; that is how this hid for the life of the check.
    """
    markdown, _ = _render_skill_routing._render_skill_routing([])
    heading, _, body = markdown.partition("## Skill Routing")
    assert heading == "", "renderer no longer leads with its own heading"
    return body


def test_the_shipped_renderer_output_satisfies_BOTH_readers_of_the_routing_contract(
    tmp_path: Path,
) -> None:
    """#552: the routing block `setup` writes must be recognized by everything reading it.

    `skill_routing_declares_charness_management` required the literal `context-only`;
    the renderer emits "may inject this context when installed; this block is the
    fallback when it is absent". Five of its six signals matched the renderer's real
    text — only that one word did not — and because the signals are combined with
    `all(...)`, a repo seeded by `charness setup` read as NOT charness-managed.
    """
    body = _shipped_routing_section_body()

    assert skill_routing_declares_charness_management(body) is True, (
        "a repo seeded by `charness setup` would read as not charness-managed"
    )
    assert skill_routing_semantically_complete(body) is True, (
        "the block `setup` writes would read as an incomplete routing contract"
    )

    # THIRD call site of the predicate family, distinct from the two in
    # `setup_agent_docs_lib.py`: the renderer reads its own output back through
    # `agents_skill_routing_semantically_complete` to decide `leave_as_is`. Exercised with
    # renderer-derived text rather than a fixture, for the same reason as the pin above.
    # Written with the heading, because this call site reads the section back out of a
    # whole AGENTS.md via `extract_section` rather than taking a section body.
    markdown, _ = _render_skill_routing._render_skill_routing([])
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\n" + markdown, encoding="utf-8")

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_semantically_complete"] is True
    assert payload["recommended_action"] == "leave_as_is"


def test_a_setup_seeded_repo_can_produce_both_gated_agents_policy_findings() -> None:
    """#552, second half: two AGENTS.md policy checks could never fire where they were written for.

    `agents_missing_charness_dynamic_workflow_policy` and
    `agents_missing_subagent_model_policy` are both guarded by `if charness_managed`, so
    a permanently-False recognizer made both unreachable for every setup-seeded repo.
    Their only live subject was this repo's own AGENTS.md, from which their match tokens
    were copied — a tautology the setup path's silent exclusion hid.

    Constructs the seeded surface rather than inferring the refusal from a green suite:
    the routing block alone (no `## Dynamic Workflows`, no `## Subagent Delegation`) must
    produce BOTH findings, and the real shipped delegation template must clear both.
    """
    seeded_agents = "# Agents\n\n" + _render_skill_routing._render_skill_routing([])[0]

    policy, findings = _detect_charness_subagent_policy(seeded_agents)

    assert policy["charness_managed"] is True
    assert {finding["type"] for finding in findings} == {
        "agents_missing_charness_dynamic_workflow_policy",
        "agents_missing_subagent_model_policy",
    }, "both gated policy checks must be able to fire for a setup-seeded repo"

    template = (ROOT / "scripts/templates/agents_subagent_delegation.txt").read_text(encoding="utf-8")
    satisfied_policy, satisfied_findings = _detect_charness_subagent_policy(
        seeded_agents + "\n" + template
    )

    assert satisfied_policy["charness_managed"] is True
    assert satisfied_findings == [], (
        "a repo seeded from the shipped template would be flagged for policies it carries"
    )


def test_naming_the_session_start_hook_alone_does_not_declare_charness_management() -> None:
    """The #552 repair widened one signal's spelling; it must not have removed it.

    Accepting both `context-only` and `fallback` is accepting two spellings of one claim
    — the hook is not the authority and the block stands without it. A block that names
    the hook while asserting nothing about its standing still fails.

    The gather line here spends the word "fallback" on an UNRELATED subject, the way this
    repo's own `gather` prose does ("a browser-mediated fallback"). That is why the
    polarity token must appear in the same sentence as the hook: searched section-wide,
    this block would read as charness-managed on the strength of a word about acquisition
    paths, and this very test would then pass only because it happened to word its gather
    line differently.
    """
    body = "\n".join(
        [
            "",
            "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly.",
            "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
            "If the command returns nonzero, report the command failure.",
            "External URLs and source links route through `gather`, escalating to the browser-mediated fallback when official paths fail.",
            "Validation closeout and operator reading tests route through `quality`.",
            "The SessionStart hook injects this context at session open.",
            "",
        ]
    )

    assert skill_routing_declares_charness_management(body) is False


def test_a_sentence_about_session_start_without_a_hook_declares_nothing_about_one() -> None:
    """Co-location is not sufficient on its own; the sentence must be ABOUT a hook.

    Added because a mutation check found this: dropping the `hook` requirement killed no
    test, so the guard was real but unproven. A block saying "at session start this block
    is the fallback" co-locates a session-start token with a polarity token and still says
    nothing about a hook injecting context, which is the claim the signal recognizes.
    """
    body = "\n".join(
        [
            "",
            "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly.",
            "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
            "If the command returns nonzero, report the command failure.",
            "External URLs and source links route through `gather` before deciding.",
            "Validation closeout and operator reading tests route through `quality`.",
            "At session start, treat this block as the fallback routing contract.",
            "",
        ]
    )

    assert skill_routing_declares_charness_management(body) is False


def test_the_hooks_standing_is_recognized_in_hand_written_spellings_too() -> None:
    """The signal must recognize the CLAIM, not two blessed spellings of it.

    The detector's job is to read hand-written AGENTS.md as well as generated blocks. Each
    variant below declares the same thing the two shipped spellings declare — the hook
    only injects context and the block stands without it — in wording neither writer uses.
    """
    prefix = [
        "",
        "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment to start the matching workflow directly.",
        "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
        "If the command returns nonzero, report the command failure.",
        "External URLs and source links route through `gather` before deciding.",
        "Validation closeout and operator reading tests route through `quality`.",
    ]
    variants = (
        "A session-start routing hook may inject this context; this block is the fallback.",
        "The startup hook may inject this context; treat this block as the fallback.",
        "A hook may inject this context at session start; this block remains context-only.",
    )

    for variant in variants:
        body = "\n".join([*prefix, variant, ""])
        assert skill_routing_declares_charness_management(body) is True, variant


def test_setup_render_skill_routing_accepts_equivalent_action_order(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment.",
                "Directly invoke the appropriate workflow for ordinary requests.",
                "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
                "Report the command failure whenever it returns a nonzero status.",
                "External URLs and source links route through `gather` before deciding.",
                "Validation closeout and operator reading tests route through `quality`.",
                "The SessionStart hook may inject this context; it remains context-only.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_semantically_complete"] is True
    assert payload["recommended_action"] == "leave_as_is"
