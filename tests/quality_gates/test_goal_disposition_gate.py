"""Tests for the #253 improvement-disposition closeout gate.

Loads ``goal_artifact_disposition.py`` (the deterministic rung) and
``goal_artifact_closeout_evidence.py`` (the wrapper that calls it) **directly**
so the achieve lib gains zero new re-export lines (it sits at 358/360; a new
re-export would hard-fail the single-file gate — goal Boundary "Home + export
budget").
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"
_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


disp = _load("goal_artifact_disposition")
ce = _load("goal_artifact_closeout_evidence")
section_placeholders = _load("goal_artifact_section_placeholders")
markdown = _load("goal_artifact_markdown")


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each fragment belongs to its option block, not only usage text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_audit_disposition_corpus_help_describes_options() -> None:
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS / "audit_disposition_corpus.py"), "--help"],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    _assert_help_pairs(
        result.stdout,
        {
            "--repo-root": "Repo root containing the goal corpus to audit.",
            "--fail-on-pre-rule-refusal": "Fail if a pre-rule goal is refused by the disposition floor.",
        },
    )


# --- grandfather-by-Created-date -------------------------------------------


def test_grandfather_inclusive_of_rule_date() -> None:
    assert disp.disposition_gate_applies("Created: 2026-05-30\n") is True  # inclusive
    assert disp.disposition_gate_applies("Created: 2026-06-01\n") is True
    assert disp.disposition_gate_applies("Created: 2026-05-29\n") is False  # pre-rule


def test_grandfather_fails_closed_on_missing_or_malformed_created() -> None:
    assert disp.disposition_gate_applies("no created line here\n") is True
    assert disp.disposition_gate_applies("Created: not-a-date\n") is True
    assert disp.disposition_gate_applies("Created: 2026-13-40\n") is True  # invalid month/day


def test_grandfather_ignores_fenced_created_line() -> None:
    # A fenced example Created: must not be read as the real one; with no real
    # Created line the goal fails closed (in-scope), not parsed from the fence.
    fenced = "Created: 2026-05-29\n"  # real line: pre-rule
    assert disp.disposition_gate_applies(fenced) is False
    only_fenced = "```\nCreated: 2026-05-29\n```\n"  # only inside a fence
    assert disp.disposition_gate_applies(only_fenced) is True  # fail-closed, fence ignored


# --- Auto-Retro blank detection (scoped + fence-safe) ----------------------


def test_auto_retro_blank_variants() -> None:
    assert disp.auto_retro_is_blank("## Auto-Retro\n\n   \n") is True  # whitespace
    assert disp.auto_retro_is_blank("## Goal\n\nx\n") is True  # absent section
    assert disp.auto_retro_is_blank("## Auto-Retro\n\napplied: a gate\n") is False  # content


def test_auto_retro_empty_section_does_not_absorb_next_section() -> None:
    # Regression for the section-scan off-by-one: an empty Auto-Retro followed
    # immediately by another H2 must read as blank, not swallow that H2's body.
    assert disp.auto_retro_is_blank("## Auto-Retro\n## After\nlots of text\n") is True


def test_auto_retro_heading_inside_fence_is_ignored() -> None:
    # A fenced ``## Auto-Retro`` is documentation, not the real section; with no
    # real section present the goal reads as blank (absent).
    fenced = "## Goal\n\n```md\n## Auto-Retro\n\napplied: x\n```\n"
    assert disp.auto_retro_is_blank(fenced) is True


# --- retro Next-Improvements presence (structure only) ---------------------


def test_retro_lists_improvements_counts_list_items_only() -> None:
    assert disp.retro_lists_improvements("## Next Improvements\n\n- do x\n") is True
    assert disp.retro_lists_improvements("## Next Improvements\n\n1. do x\n") is True
    assert disp.retro_lists_improvements("## Next Improvements\n\nprose, no bullet\n") is False
    assert disp.retro_lists_improvements("## Other\n\n- x\n") is False  # renamed -> inert


def test_retro_lists_improvements_ignores_fenced_bullets() -> None:
    fenced = "## Next Improvements\n\n```\n- fake bullet in a fence\n```\n"
    assert disp.retro_lists_improvements(fenced) is False


# --- opt-out (Auto-Retro-scoped, min-length, un-poisoned) ------------------


def test_optout_valid_and_min_length() -> None:
    ok = "## Auto-Retro\n\nRetro dispositions: none — no actionable improvement surfaced this run\n"
    assert disp.find_disposition_optout(ok) == "no actionable improvement surfaced this run"
    short = "## Auto-Retro\n\nRetro dispositions: none — nope\n"
    assert disp.find_disposition_optout(short) is None  # below MIN_OPTOUT_REASON


def test_optout_is_auto_retro_scoped_not_poisoned_by_body_prose() -> None:
    # The round-2 B-2 poisoning shape: the body *describes* the opt-out marker
    # outside the Auto-Retro span. A full-text scan would falsely exempt; the
    # scoped scan must not.
    poisoned = (
        "## Goal\n\nThe opt-out line is `Retro dispositions: none — because there is nothing`.\n\n"
        "## Auto-Retro\n\n   \n"
    )
    assert disp.find_disposition_optout(poisoned) is None
    assert disp.auto_retro_is_blank(poisoned) is True


# --- integration: rung 1a via check_complete_evidence ----------------------

_SLUG = "253-dispo"


def _seed(tmp_path: Path, rel: str, body: str) -> Path:
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def _build_goal(created: str, auto_retro_body: str, *, slug: str = _SLUG, review_line: str = "") -> str:
    extra = f"{review_line}\n" if review_line else ""
    return (
        f"# Achieve Goal: T\n\nStatus: active\nCreated: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{slug}.md`\n\n"
        "## Final Verification\n\n"
        f"Retro: charness-artifacts/retro/{created}-{slug}.md\n"
        f"Host log probe: charness-artifacts/probe/{created}-{slug}.json\n{extra}\n"
        f"## Auto-Retro\n\n{auto_retro_body}\n"
    )


def _seed_review(tmp_path: Path, created: str, *, slug: str = _SLUG, bind: bool = True) -> str:
    name = f"{created}-{slug}-disposition.md" if bind else f"{created}-unrelated-review.md"
    _seed(
        tmp_path,
        f"charness-artifacts/critique/{name}",
        f"# Disposition review {'for ' + slug if bind else 'of a different goal'}\n\n- improvement 1: applied\n",
    )
    return f"Disposition review: charness-artifacts/critique/{name}"


def _seed_evidence(tmp_path: Path, created: str, *, improvements: bool = True, slug: str = _SLUG) -> None:
    next_improvements = "## Next Improvements\n\n- workflow: do x next time\n" if improvements else "## Next Improvements\n\nnone\n"
    _seed(tmp_path, f"charness-artifacts/retro/{created}-{slug}.md", f"# Retro\n\n{next_improvements}")
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{slug}.json", '{"host":"claude-code"}\n')


def test_block_the_blank_fires_in_scope_blank_with_improving_retro(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, "   "))
    assert report["disposition_scope"]["in_scope"] is True
    assert report["retro_improvements_present"] is True
    assert report["auto_retro_blank"] is True
    assert "disposition_blank" in report
    assert report["ok"] is False


def test_block_the_blank_grandfathered_pre_rule(tmp_path: Path) -> None:
    created = "2026-05-29"  # pre-rule
    _seed_evidence(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, "   "))
    assert report["disposition_scope"]["in_scope"] is False
    assert "disposition_blank" not in report  # gate inert for grandfathered goals


def test_block_the_blank_passes_with_filled_auto_retro(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    review_line = _seed_review(tmp_path, created)  # rung 1b satisfied; isolate rung 1a
    report = ce.check_complete_evidence(
        tmp_path,
        _build_goal(created, "applied: shipped a gate this run; issue #999 filed for the rest", review_line=review_line),
    )
    assert "disposition_blank" not in report
    assert report["ok"] is True


def test_complete_gate_blocks_pending_section_first_line(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created, improvements=False)
    review_line = _seed_review(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _build_goal(
            created,
            "Pending until active run closeout. Retro dispositions must be recorded before completion.",
            review_line=review_line,
        ),
    )
    assert report["ok"] is False
    assert report["section_placeholders"] == [
        {
            "section": "Auto-Retro",
            "line": 15,
            "marker": "Pending until",
            "text": "Pending until active run closeout. Retro dispositions must be recorded before completion.",
        }
    ]


def test_section_placeholder_scan_ignores_fenced_examples() -> None:
    text = (
        "## Goal\n\nReal goal content.\n\n"
        "```md\n## Auto-Retro\n\nPending until closeout.\n```\n\n"
        "## Auto-Retro\n\napplied: final disposition recorded\n"
    )
    assert section_placeholders.final_status_placeholders(text) == []


def test_section_placeholder_scan_handles_heading_at_eof() -> None:
    assert section_placeholders.final_status_placeholders("## Auto-Retro") == []


def test_section_placeholder_scan_ignores_non_placeholder_pending_noun() -> None:
    text = "## Auto-Retro\n\nPending reviewer assignment was deliberately out of scope.\n"
    assert section_placeholders.final_status_placeholders(text) == []


def test_slice_plan_row_count_handles_absent_section_and_extra_separator() -> None:
    assert markdown.slice_plan_data_row_count("## Other\n\n| A |\n| --- |\n| x |\n") == 0
    assert markdown.slice_plan_data_row_count(
        "## Slice Plan\n\n| Slice | Status |\n| --- | --- |\n| 1 | done |\n| --- | --- |\n| 2 | done |\n"
    ) == 2


def test_section_placeholder_scan_catches_labeled_todo_first_line() -> None:
    text = "## Auto-Retro\n\nRetro dispositions: TODO — disposition every surfaced improvement\n"
    assert section_placeholders.final_status_placeholders(text) == [
        {
            "section": "Auto-Retro",
            "line": 3,
            "marker": "TODO",
            "text": "Retro dispositions: TODO — disposition every surfaced improvement",
        }
    ]


def test_section_placeholder_loader_fails_closed_when_markdown_helper_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_spec(*_args, **_kwargs):
        return None

    monkeypatch.setattr(importlib.util, "spec_from_file_location", missing_spec)
    with pytest.raises(ImportError, match="goal_artifact_markdown.py not found"):
        section_placeholders._load_markdown()


def test_block_the_blank_inert_when_retro_lists_no_improvements(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created, improvements=False)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, "   "))
    assert report["retro_improvements_present"] is False
    assert "disposition_blank" not in report  # nothing to disposition -> no block


def test_optout_passes_blank_and_is_surfaced(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    review_line = _seed_review(tmp_path, created)  # rung 1b satisfied; isolate the opt-out path
    optout = "Retro dispositions: none — every surfaced lesson was already captured upstream this run"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, optout, review_line=review_line))
    assert "disposition_blank" not in report
    assert report["disposition_optout"]["reason"].startswith("every surfaced lesson")
    assert report["ok"] is True


# --- integration: rung 1b (disposition_review line) ------------------------

_FILLED = "applied: shipped a gate this run; issue #999 filed for the rest"


def test_disposition_review_line_parsed_and_normalized() -> None:
    parsed = ce.parse_closeout_evidence("Disposition review: charness-artifacts/critique/x.md\n")
    assert parsed["disposition_review"] == {"kind": "evidence", "value": "charness-artifacts/critique/x.md"}
    # the hyphenated label + skip form both normalize/parse (round-3 B1 regex arm)
    skip = ce.parse_closeout_evidence(
        "Disposition-review: skipped: host-blocked-subagent: the host rejected Agent spawn at runtime\n"
    )
    assert skip["disposition_review"]["kind"] == "skip"


def test_disposition_review_prose_in_auto_retro_is_not_evidence() -> None:
    text = (
        "# Achieve Goal: T\n\n"
        "Created: 2026-05-30\n"
        "Activation: `/goal @charness-artifacts/goals/2026-05-30-253-dispo.md`\n\n"
        "## Final Verification\n\n"
        "Retro: charness-artifacts/retro/2026-05-30-253-dispo.md\n"
        "Host log probe: charness-artifacts/probe/2026-05-30-253-dispo.json\n\n"
        "## Auto-Retro\n\n"
        "- Disposition review: this prose notes that the review happened elsewhere\n"
        "Disposition review: this unbulleted prose is still outside Final Verification\n"
    )
    parsed = ce.parse_closeout_evidence(text)
    assert "disposition_review" not in parsed


def test_derive_goal_tokens_keeps_slug_and_numeric_cluster() -> None:
    assert ce.derive_goal_tokens(
        "Activation: `/goal @charness-artifacts/goals/2026-05-31-261-coordination-cues.md`\n"
    ) == ["261-coordination-cues", "261"]


def test_a_purely_numeric_goal_slug_opts_out_of_binding_rather_than_refusing() -> None:
    """A bare number is the ONLY token for a `<date>-<n>.md` goal, and a bare number
    now has to be CITED in evidence content (hunt B4). The canonical way a retro
    names its goal is by path — `charness-artifacts/goals/2026-05-31-261.md` — where
    the date segment sits between the `goal` marker and the number, so the citation
    fails and a CORRECT closeout is refused. Empty tokens mean "caller opts out of
    binding", which is the safe direction: presence still applies.
    """
    assert ce.derive_goal_tokens(
        "Activation: `/goal @charness-artifacts/goals/2026-05-31-261.md`\n"
    ) == []


def test_narration_sections_present_is_exact_and_case_insensitive() -> None:
    retro = "# Retro\n\n## waste\n\nx\n\n## Other\n\nx\n\n## Next Improvements\n\n- x\n"
    assert ce.narration_sections_present(retro) == ["Waste", "Next Improvements"]


def test_in_scope_goal_refused_without_disposition_review_line(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED))
    assert report["ok"] is False
    assert "disposition_review" in report["missing"]


def test_in_scope_goal_flips_with_bound_disposition_review(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    review_line = _seed_review(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED, review_line=review_line))
    assert report["ok"] is True
    assert report["binding_failures"] == []


def test_check_complete_evidence_surfaces_retro_narration_sections(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed(
        tmp_path,
        f"charness-artifacts/retro/{created}-{_SLUG}.md",
        "# Retro\n\n## Waste\n\nnone\n\n## Critical Decisions\n\n- kept the gate\n",
    )
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{_SLUG}.json", '{"host":"claude-code"}\n')
    review_line = _seed_review(tmp_path, created)

    report = ce.check_complete_evidence(
        tmp_path,
        _build_goal(created, _FILLED, review_line=review_line),
    )

    assert report["ok"] is True
    assert report["narration_required_sections"] == ["Waste", "Critical Decisions"]


def test_check_complete_evidence_narration_skips_non_retro_evidence_first(
    tmp_path: Path, monkeypatch
) -> None:
    retro = _seed(
        tmp_path,
        "charness-artifacts/retro/2026-05-29-loop-order.md",
        "# Retro\n\n## Waste\n\nnone\n",
    )
    probe = _seed(tmp_path, "charness-artifacts/probe/2026-05-29-loop-order.json", '{"host":"test"}\n')

    class FakeHelper:
        @staticmethod
        def check(**kwargs):
            return {
                "ok": True,
                "missing": [],
                "missing_evidence_files": [],
                "invalid_skips": [],
                "satisfied": [
                    {"name": "host_log_probe", "via": "evidence", "path": str(probe)},
                    {"name": "retro_artifact", "via": "evidence", "path": str(retro)},
                ],
            }

        @staticmethod
        def evidence_binds_to_context(path, *, tokens):
            return True, "bound for test"

    monkeypatch.setattr(ce, "_load_shared_helper", lambda: FakeHelper)
    text = (
        "# Achieve Goal: T\n\n"
        "Created: 2026-05-29\n"
        "Activation: `/goal @charness-artifacts/goals/2026-05-29-loop-order.md`\n\n"
        "## Final Verification\n\n"
        "Retro: charness-artifacts/retro/2026-05-29-loop-order.md\n"
        "Host log probe: charness-artifacts/probe/2026-05-29-loop-order.json\n"
        "## Auto-Retro\n\nx\n"
    )

    report = ce.check_complete_evidence(tmp_path, text)

    assert report["narration_required_sections"] == ["Waste"]


def test_disposition_review_host_blocked_skip_flips(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    skip = "Disposition review: skipped: host-blocked-subagent: this host rejected the Agent spawn at runtime"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED, review_line=skip))
    assert report["ok"] is True


def test_grandfathered_goal_does_not_require_disposition_review(tmp_path: Path) -> None:
    created = "2026-05-29"  # pre-rule
    _seed_evidence(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED))
    assert "disposition_review" not in report["missing"]
    assert report["ok"] is True


def test_disposition_review_must_bind_to_goal(tmp_path: Path) -> None:
    # 1b is presence/binding-only BY DESIGN: a present-but-unrelated review file
    # is refused (cannot satisfy by citing a stranger's artifact).
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    unbound = _seed_review(tmp_path, created, bind=False)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED, review_line=unbound))
    assert "disposition_review" in {e["name"] for e in report["binding_failures"]}
    assert report["ok"] is False


def test_block_the_blank_fires_independently_of_review_skip(tmp_path: Path) -> None:
    # Host portability: a rung-1b skip must NOT disable rung-1a (block-the-blank).
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    skip = "Disposition review: skipped: host-blocked-subagent: this host rejected the Agent spawn at runtime"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, "   ", review_line=skip))
    assert "disposition_blank" in report  # blank caught despite the rung-1b skip
    assert report["ok"] is False


# --- #315: seeded scaffold placeholders must not satisfy the gate ----------


def test_is_placeholder_value_recognizes_literal_markers() -> None:
    for marker in ("TODO", "TODO — fill or skip", "TBD", "<path>", "<retro-path>", "FIXME"):
        assert ce.is_placeholder_value(marker) is True
    # a real bound path never starts with a placeholder marker
    assert ce.is_placeholder_value("charness-artifacts/retro/2026-06-06-g.md") is False
    assert ce.is_placeholder_value("skipped: host-log-not-exposed: detail here") is False


def test_parse_drops_todo_placeholder_evidence_lines() -> None:
    # The template seeds visible `Retro: TODO …` / `Host log probe: TODO …` /
    # `Disposition review: TODO …` lines. An untouched placeholder must NOT be
    # read as satisfied evidence — it is dropped so the name lands in `missing`.
    text = (
        "## Final Verification\n\n"
        "Retro: TODO — create or explicitly skip with an allowed reason before complete\n"
        "Host log probe: TODO — create or explicitly skip with an allowed reason before complete\n"
        "Disposition review: TODO — create or explicitly skip only when policy allows before complete\n"
    )
    parsed = ce.parse_closeout_evidence(text)
    assert parsed == {}  # no placeholder is parsed as evidence or skip


def test_placeholder_only_artifact_cannot_pass_complete_evidence_gate(tmp_path: Path) -> None:
    # An in-scope goal whose Final Verification still carries the untouched
    # `TODO` scaffold placeholders must be refused: every required evidence name
    # falls back to `missing`.
    created = "2026-06-06"
    text = (
        "# Achieve Goal: T\n\nStatus: active\nCreated: " + created + "\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{_SLUG}.md`\n\n"
        "## Final Verification\n\n"
        "Retro: TODO — create or explicitly skip with an allowed reason before complete\n"
        "Host log probe: TODO — create or explicitly skip with an allowed reason before complete\n"
        "Disposition review: TODO — create or explicitly skip only when policy allows before complete\n\n"
        "## Auto-Retro\n\n"
        "Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out\n"
    )
    report = ce.check_complete_evidence(tmp_path, text)
    assert report["ok"] is False
    assert set(report["missing"]) == {"retro_artifact", "host_log_probe", "disposition_review"}


def test_auto_retro_placeholder_reads_as_blank_keeping_rung_1a_live() -> None:
    # Seeding the `Retro dispositions: TODO …` placeholder must not silently
    # disable rung 1a: an Auto-Retro carrying only the untouched placeholder
    # still reads as blank-equivalent.
    placeholder = (
        "## Auto-Retro\n\nRetro dispositions: TODO — disposition every surfaced "
        "improvement, or record the explicit no-improvement opt-out\n"
    )
    assert disp.auto_retro_is_blank(placeholder) is True
    # once replaced by a real opt-out or per-improvement record it is non-blank
    optout = "## Auto-Retro\n\nRetro dispositions: none — every lesson was captured upstream this run\n"
    assert disp.auto_retro_is_blank(optout) is False
    assert disp.auto_retro_is_blank("## Auto-Retro\n\napplied: shipped a gate this run\n") is False


def test_block_the_blank_fires_when_auto_retro_holds_only_the_placeholder(tmp_path: Path) -> None:
    # End-to-end: a goal that filled the disposition-review line but left the
    # seeded Auto-Retro TODO placeholder is still block-the-blank refused.
    created = "2026-06-06"
    _seed_evidence(tmp_path, created)
    review_line = _seed_review(tmp_path, created)  # rung 1b satisfied; isolate rung 1a
    placeholder = (
        "Retro dispositions: TODO — disposition every surfaced improvement, or "
        "record the explicit no-improvement opt-out"
    )
    report = ce.check_complete_evidence(
        tmp_path, _build_goal(created, placeholder, review_line=review_line)
    )
    assert report["auto_retro_blank"] is True
    assert "disposition_blank" in report
    assert report["ok"] is False


# --- corpus invariant: grandfather never retroactively refuses -------------


def test_live_corpus_pre_rule_goals_are_never_rung1a_refused() -> None:
    """No pre-rule (Created < rule date) completed goal is block-the-blank refused.

    Honest about its own strength: this holds for ANY corpus, because
    `apply_disposition_rungs` returns at `if not in_scope` before setting
    `disposition_blank` -- so the two predicates are mutually exclusive by
    control flow, not by corpus content. It therefore guards the CONTROL FLOW
    (a future rung that set `disposition_blank` before the scope check would
    turn it red), not the grandfather's behaviour on real goals. Its previous
    docstring called it a stable corpus invariant, which read as the stronger
    claim it cannot make.
    """
    runner = _load("audit_disposition_corpus")
    repo_root = Path(__file__).resolve().parents[2]
    rows = [
        runner.audit_goal(repo_root, p)
        for p in sorted((repo_root / "charness-artifacts/goals").glob("*.md"))
    ]
    pre_rule = [r for r in rows if r["status_normalized"] == "complete" and r["in_scope"] is False]
    assert pre_rule, "expected at least one pre-rule completed goal in the corpus"
    assert all(r["rung1a_block_the_blank"] is False for r in pre_rule)


# --- corpus measurement states its own denominator --------------------------


def _live_corpus_summary() -> tuple[dict, list[dict]]:
    runner = _load("audit_disposition_corpus")
    repo_root = Path(__file__).resolve().parents[2]
    rows = [
        runner.audit_goal(repo_root, p)
        for p in sorted((repo_root / "charness-artifacts/goals").glob("*.md"))
    ]
    return runner.summarize(rows), rows


def test_live_corpus_summary_states_the_dated_denominator() -> None:
    """`in_scope` alone does not say what population it selected.

    It is the FAIL-CLOSED count: goals dated into the floor's window PLUS every
    goal whose `Created:` could not be parsed. Reported bare, a reader cannot
    tell those apart, and the undatable share can grow without the headline
    number moving in a way anyone can see. This pins the split over the REAL
    corpus -- a synthetic fixture would only re-ask whether the arithmetic adds
    up, which was never the defect.
    """
    summary, rows = _live_corpus_summary()
    assert summary["in_scope"] == summary["in_scope_dated"] + summary["in_scope_undatable"]
    assert summary["disposition_rule_date"] == disp.DISPOSITION_RULE_DATE.isoformat()
    assert "fail-closed" in summary["in_scope_population"]
    # The population statement names the status filter (the largest one, and
    # previously unstated) and the exact three-way split of the intake.
    assert "`Status:` is `complete`" in summary["in_scope_population"]
    assert "rows_without_status + rows_with_other_status + completed_goals" in summary["in_scope_population"]
    # Intake is reported, so the files the glob picks up and then drops are
    # visible rather than absorbed.
    assert summary["audited_files"] == len(rows)
    assert summary["rows_without_status"] == len([r for r in rows if not r["status_normalized"]])
    # Intake splits EXACTLY three ways, with no unnamed remainder. `<=` here would
    # pass while any number of files fell out of every reported bucket -- which is
    # how a completed goal spelled `Status: COMPLETE` went unexamined.
    assert (
        summary["rows_without_status"] + summary["rows_with_other_status"] + summary["completed_goals"]
        == summary["audited_files"]
    )
    # Every undatable in-scope goal is NAMED, never just counted. Checked against
    # the ROWS, not against its own count -- comparing the list's length to the
    # number derived from that same list holds for any implementation, including
    # one that names the wrong goals.
    named = set(summary["in_scope_undatable_goals"])
    actually_undatable = {
        r["goal"] for r in rows if r["status_normalized"] == "complete" and r["in_scope"] is True and not r["created"]
    }
    assert named == actually_undatable


def test_live_corpus_dated_denominator_does_not_collapse() -> None:
    """Fails if the dated population collapses into the undatable remainder.

    The failure this guards is silent by construction: goals losing their
    `Created:` line stay in `in_scope` (fail-closed), so the gate keeps firing
    and the headline count keeps looking healthy while the share of it backed by
    an actual date drains away.

    STRICT zero, not a majority threshold. The realistic regression is one goal
    at a time -- `parse_created_date` returns None for a whole file on an
    unbalanced fence or two conflicting `Created:` lines, both single-file
    editing accidents on long markdown artifacts. A majority bar would have
    tolerated 56 of them. And the audit's own docstring calls any non-zero
    `in_scope_undatable` a corpus defect to repair, so the assertable pin is the
    one that matches that claim. Ordinary work WILL touch this test -- the corpus
    grows every session -- but every red it produces is a real defect with a
    one-character repair, which is the trade being made.
    """
    summary, _ = _live_corpus_summary()
    assert summary["in_scope"] > 0, "expected a non-empty in-scope population"
    assert summary["in_scope_undatable_goals"] == [], (
        "a completed goal is in scope only because its `Created:` could not be parsed, so the "
        "dated denominator no longer backs the whole in-scope population: "
        f"{summary['in_scope_dated']} dated of {summary['in_scope']} in scope; "
        f"undatable: {summary['in_scope_undatable_goals']}"
    )
    assert summary["in_scope_dated"] == summary["in_scope"]


def test_summarize_splits_a_synthetic_undatable_row_out_of_the_dated_count() -> None:
    """The split must actually move when an undatable goal exists.

    The live corpus currently carries zero undatable completed goals, so the
    two tests above would also pass against a `summarize` that hard-coded
    `in_scope_undatable` to 0. This drives the branch they cannot.
    """
    runner = _load("audit_disposition_corpus")
    # Deliberately the CONSUMED SUBSET of an `audit_goal` row, not a full-fidelity
    # fixture: `summarize` indexes with `[]`, so a future field it starts reading
    # raises KeyError here loudly rather than passing on a stale stub.
    base = {
        "status": "complete",
        "status_normalized": "complete",
        "in_scope": True,
        "rung1a_block_the_blank": False,
        "has_disposition_review_line": True,
    }
    summary = runner.summarize(
        [
            {**base, "goal": "dated.md", "created": "2026-07-01"},
            {**base, "goal": "undatable.md", "created": None},
        ]
    )
    assert summary["in_scope"] == 2
    assert summary["in_scope_dated"] == 1
    assert summary["in_scope_undatable"] == 1
    # The naming assertion lives HERE, where it can discriminate. On the live
    # corpus the undatable set is empty (and a sibling test pins it empty), so
    # the same assertion there compares two empty sets and cannot fail.
    assert summary["in_scope_undatable_goals"] == ["undatable.md"]


def test_normalized_status_recovers_spelling_variants_of_complete() -> None:
    """`Status: COMPLETE (2026-06-07)` is a completed goal, not a third category.

    `_STATUS` captures the first whitespace-delimited token, so a trailing
    parenthetical or period rides along. Compared case-sensitively against
    `"complete"`, such a goal fell out of `completed_goals` AND out of
    `rows_without_status` (its status is truthy) -- present in the corpus,
    absent from every reported bucket. This is the live corpus's real spelling,
    not a hypothetical.
    """
    runner = _load("audit_disposition_corpus")
    assert runner.normalized_status("COMPLETE") == "complete"
    assert runner.normalized_status("complete.") == "complete"
    assert runner.normalized_status("Complete;") == "complete"
    assert runner.normalized_status("active") == "active"
    assert runner.normalized_status(None) is None
    assert runner.normalized_status("...") is None


def test_summarize_on_an_empty_corpus_still_states_a_string_rule_date() -> None:
    """The branch that motivated reading the constant instead of the rows.

    Derived from rows, `disposition_rule_date` rendered `[]` for a corpus with
    no goals -- a denominator statement pointing at an empty list, with a type
    that varied str-vs-list between runs. This is the shipped surface in every
    consuming repo, where an empty `charness-artifacts/goals/` is normal.
    """
    runner = _load("audit_disposition_corpus")
    summary = runner.summarize([])
    assert summary["disposition_rule_date"] == disp.DISPOSITION_RULE_DATE.isoformat()
    assert isinstance(summary["disposition_rule_date"], str)
    assert summary["audited_files"] == 0
    assert summary["in_scope"] == 0


def test_completed_only_trims_printed_rows_without_moving_the_summary(tmp_path: Path) -> None:
    """The invariant the `main()` restructure exists to create.

    `--completed-only` is a DISPLAY flag. Summarizing the filtered list instead
    of the full audited set would make `audited_files` / `rows_without_status`
    report the filter's output as if it were the intake -- a denominator that
    moves with a display flag. Nothing pinned that, so a future author
    re-inlining the filter would reintroduce it with a green suite.
    """
    goals = tmp_path / "charness-artifacts/goals"
    goals.mkdir(parents=True)
    (goals / "2026-07-01-done.md").write_text(
        "# G\n\nStatus: complete\nCreated: 2026-07-01\n", encoding="utf-8"
    )
    (goals / "2026-07-02-running.md").write_text(
        "# G\n\nStatus: active\nCreated: 2026-07-02\n", encoding="utf-8"
    )
    (goals / "2026-07-03-not-a-goal.md").write_text("# Early close report\n\nno status line\n", encoding="utf-8")

    def _run(*extra: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS / "audit_disposition_corpus.py"), "--repo-root", str(tmp_path), *extra],
            cwd=_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    full = _run()
    trimmed = _run("--completed-only")
    assert full["summary"] == trimmed["summary"]
    assert full["summary"]["audited_files"] == 3
    assert full["summary"]["rows_without_status"] == 1
    assert full["summary"]["rows_with_other_status"] == 1
    assert full["summary"]["completed_goals"] == 1
    assert len(full["rows"]) == 3
    assert [r["goal"] for r in trimmed["rows"]] == ["2026-07-01-done.md"]


# --- sibling-leaf loader fail-closed (the module-split glue) ----------------
#
# Slices 1 & 2 introduced a `_load_local_module` helper in each wrapper that
# loads its cohesive leaf (the disposition grammar / the closeout loaders) via
# filesystem spec. The happy path runs at import (covered by every test that
# loads the module); these pin the fail-CLOSED branch — both `spec is None` and
# `spec.loader is None` must raise ImportError naming the missing module beside
# the right wrapper — so a moved/missing leaf surfaces loudly, never silently.


def test_disposition_load_local_module_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    with pytest.raises(ImportError, match="goal_artifact_disposition_grammar.py not found beside goal_artifact_disposition.py"):
        disp._load_local_module("goal_artifact_disposition_grammar")

    class _SpecNoLoader:
        loader = None

    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: _SpecNoLoader())
    with pytest.raises(ImportError, match="anything.py not found beside goal_artifact_disposition.py"):
        disp._load_local_module("anything")


def test_closeout_evidence_load_local_module_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    with pytest.raises(ImportError, match="goal_artifact_closeout_loaders.py not found beside goal_artifact_closeout_evidence.py"):
        ce._load_local_module("goal_artifact_closeout_loaders")

    class _SpecNoLoader:
        loader = None

    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: _SpecNoLoader())
    with pytest.raises(ImportError, match="anything.py not found beside goal_artifact_closeout_evidence.py"):
        ce._load_local_module("anything")


def test_closeout_loaders_fail_closed_for_each_sibling(monkeypatch) -> None:
    # The 8 sibling/shared loaders moved verbatim into goal_artifact_closeout_loaders.py.
    # `_load_shared_helper`/`_load_sibling_disposition`/`_load_sibling_coordination_floors`
    # are already pinned in test_goal_coordination_floors.py; these cover the
    # remaining 5 fail-CLOSED raise branches so a moved/missing sibling surfaces
    # loudly with the right name. The shared importlib.util patch reaches the leaf
    # across the re-bind because the loaders reference `importlib.util.spec_from_file_location`.
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    for loader, missing in (
        (ce._load_sibling_early_close_report, "goal_artifact_early_close_report.py not found"),
        (ce._load_sibling_metric_window, "goal_metric_window_lib.py not found"),
        (ce._load_sibling_phase_routing, "goal_artifact_phase_routing.py not found"),
        (ce._load_sibling_closeout_delegation, "goal_artifact_closeout_delegation.py not found"),
        (ce._load_sibling_adapter_policy, "achieve_adapter_policy.py not found"),
    ):
        with pytest.raises(ImportError, match=missing):
            loader()


def test_grammar_mask_fences_returns_text_on_unbalanced_fence() -> None:
    # An odd number of fence markers leaves `in_fence` True at EOF; `_mask_fences`
    # then returns the original text unchanged (it cannot safely blank an unclosed
    # fence). Pins goal_artifact_disposition_grammar.py `_mask_fences` `return text`.
    unbalanced = "```\nx = 1\n"  # opening fence, never closed
    assert disp._mask_fences(unbalanced) == unbalanced


def test_grammar_section_body_empty_when_heading_is_last_char() -> None:
    # When the heading is the final line with no trailing newline,
    # `masked.find("\n", start.end())` is -1, so `_section_body` returns "".
    # Pins goal_artifact_disposition_grammar.py `_section_body` `return ""`.
    assert disp._section_body("## Auto-Retro", "Auto-Retro") == ""
