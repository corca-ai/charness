from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_LIB = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts/goal_artifact_lib.py"
_spec = importlib.util.spec_from_file_location("goal_artifact_lib", _LIB)
gal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gal)


def _goal_text(tmp_path: Path, slug: str = "g", date: str = "2026-05-27") -> str:
    path = gal.goal_path(tmp_path, date, slug)
    return path.read_text(encoding="utf-8")


def test_upsert_creates_then_updates_status_only(tmp_path: Path) -> None:
    first = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="First", goal_body="BODY-AAA")
    assert first["action"] == "created"

    again = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="Second", status="active", goal_body="BODY-BBB")
    assert again["action"] in ("updated", "unchanged")
    assert "note" in again  # signals the existing-artifact / collision case

    text = _goal_text(tmp_path)
    assert "BODY-AAA" in text and "BODY-BBB" not in text  # body never overwritten
    assert "First" in text and "Second" not in text  # title never overwritten
    assert "Status: active" in text


def test_check_goal_passes_on_scaffold_and_reports_gaps(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    text = _goal_text(tmp_path)
    assert gal.check_goal(text)["ok"] is True
    assert text.index("## Active Operating Frame") < text.index("## Goal")
    assert "Verification cadence: cheap deterministic checks at commit boundaries" in text
    assert "changed\n  files and owning/generated surfaces" in text
    assert "out-of-scope lines" in text
    assert "History boundary: keep this frame current" in text

    bad = gal.check_goal("# Achieve Goal: T\n\nStatus: bogus\n\n## Goal\n")
    assert bad["ok"] is False
    assert "Non-Goals" in bad["missing_sections"]
    assert any("bogus" in issue for issue in bad["issues"])


def test_append_slice_numbers_and_spacing(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    text = path.read_text(encoding="utf-8")
    assert gal.next_slice_number(text) == 1
    text = gal.append_slice(text, gal.render_slice_block(1, "one", {"Objective": "a"}))
    text = gal.append_slice(text, gal.render_slice_block(gal.next_slice_number(text), "two", {}))
    assert "### Slice 1: one" in text and "### Slice 2: two" in text
    assert "\n\n\n" not in text  # single blank-line separation
    assert "- Objective:\n" in text  # empty field carries no trailing space


def test_render_slice_block_includes_test_duplication_pressure(tmp_path: Path) -> None:
    block = gal.render_slice_block(1, "s", {"Test duplication pressure": "23.2% vs 22% gate"})
    assert "- Test duplication pressure: 23.2% vs 22% gate" in block
    # field stays ordered between targeted verification and critique
    assert block.index("Targeted verification") < block.index("Test duplication pressure") < block.index("Critique")


def test_pursue_readiness_flags_unshaped_auto_draft() -> None:
    """#247: a goal still carrying the Before-phase placeholder marker is unshaped,
    so `/goal` must fail-fast (route to `/achieve`) instead of pursuing it."""
    unshaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\n*To be filled by the achieve Before-phase interview.*\n\n"
        "## Agent Verification Plan\n\n*To be filled by the achieve Before-phase interview.*\n"
    )
    report = gal.pursue_readiness(unshaped)
    assert report["pursue_ready"] is False
    assert report["placeholder_count"] >= 1
    assert "/achieve" in report["reason"]


def test_pursue_readiness_passes_when_shaped() -> None:
    """A shaped goal (no Before-phase placeholder marker) is safe to pursue."""
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\nUser runs X and sees Y.\n\n"
        "## Agent Verification Plan\n\nRun the suite; assert Z.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is True
    assert report["placeholder_count"] == 0
    assert report["discussion_required"] is False


def test_pursue_readiness_blocks_hidden_consequential_decisions() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Boundaries\n\n#184 must close inside this bundled goal.\n\n"
        "## Agent Verification Plan\n\n### External Or Live Proof\n\nUse real GitHub lookup proof, not fixture-only proof.\n\n"
        "## Interview Decisions\n\nProduction contact is allowed, including apply/restart.\n\n"
        "## Plan Critique Findings\n\nNo blockers.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["placeholder_count"] == 0
    assert report["discussion_required"] is True
    assert "issue_close_or_split" in report["discussion_triggers"]
    assert "operator discussion required" in report["reason"]


@pytest.mark.parametrize(
    ("body", "trigger"),
    [
        ("## Agent Verification Plan\n\n### External Or Live Proof\n\nUse live proof in production.\n", "production_or_live_proof"),
        ("## Boundaries\n\nResolve #275 and #276 together.\n", "broad_bundle_scope"),
        ("## Boundaries\n\nComplete all four proposed changes.\n", "broad_bundle_scope"),
        ("## Agent Verification Plan\n\nProof non-claim: live proof not run.\n", "proof_nonclaim_or_downgrade"),
        ("## Interview Decisions\n\nIrreversible side effects are allowed.\n", "irreversible_side_effect"),
        ("## Non-Goals\n\nDo not close #276 until push and remote verification.\n", "issue_close_or_split"),
    ],
)
def test_pursue_readiness_discussion_trigger_families(body: str, trigger: str) -> None:
    report = gal.pursue_readiness(
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n" + body
    )
    assert report["pursue_ready"] is False
    assert trigger in report["discussion_triggers"]


def test_pursue_readiness_does_not_treat_empty_discussion_label_as_summary() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "Discuss before activation:\n\n"
        "## Agent Verification Plan\n\n### External Or Live Proof\n\nUse live proof.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_summary_present"] is False


def test_pursue_readiness_does_not_treat_empty_discussion_heading_as_summary() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Agent Verification Plan\n\n"
        "### Discuss before activation\n\n"
        "### External Or Live Proof\n\nUse live proof.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_summary_present"] is False


def test_pursue_readiness_ignores_stale_discussion_summary_in_slice_log() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Non-Goals\n\nDo not close #276 until push.\n\n"
        "## Slice Log\n\nDiscuss before activation: close #100 was already discussed.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_required"] is True
    assert report["discussion_summary_present"] is False


def test_pursue_readiness_does_not_trigger_on_critique_not_yet_run() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Plan Critique Findings\n\nNot yet run. First active slice should run critique.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is True
    assert report["discussion_required"] is False


def test_pursue_readiness_allows_surfaced_consequential_decisions() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Boundaries\n\n#184 must close inside this bundled goal.\n\n"
        "Discuss before activation: close #184 in-goal; production contact is allowed with recorded target, preflight, stop condition, and post-proof.\n\n"
        "## Agent Verification Plan\n\n### External Or Live Proof\n\nUse real GitHub lookup proof.\n\n"
        "## Interview Decisions\n\nProduction contact is allowed, including apply/restart.\n\n"
        "## Plan Critique Findings\n\nNo blockers.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is True
    assert report["discussion_required"] is True
    assert report["discussion_summary_present"] is True


def test_pursue_readiness_allows_summary_starting_with_issue_number() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## Non-Goals\n\nDo not close #276 until push.\n\n"
        "Discuss before activation: #276 remains local-only until push verifies closure.\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is True
    assert report["discussion_summary_present"] is True


def test_pursue_readiness_rejects_na_summary_when_decisions_are_consequential() -> None:
    shaped = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "Discuss before activation: n/a -- no discussion needed.\n\n"
        "## Interview Decisions\n\n#220 will use fixture-only proof.\n\n"
    )
    report = gal.pursue_readiness(shaped)
    assert report["pursue_ready"] is False
    assert report["discussion_summary_present"] is False


def test_pursue_readiness_ignores_marker_inside_code_fence() -> None:
    """A marker quoted inside a fenced block must not trip the detector (fences
    are masked), so a documentation example cannot force a false unshaped verdict."""
    fenced = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x.md`\n\n"
        "## User Acceptance\n\nUser runs X.\n\n```\n"
        "To be filled by the achieve Before-phase interview.\n```\n"
    )
    assert gal.pursue_readiness(fenced)["pursue_ready"] is True


def test_slugify_neutralizes_path_chars() -> None:
    assert gal.slugify("../../etc/passwd") == "etc-passwd"
    assert gal.slugify("Mixed CASE!!") == "mixed-case"


def test_set_status_rejects_invalid_and_preserves_crlf() -> None:
    with pytest.raises(ValueError):
        gal.set_status("Status: draft\n", "bogus")
    crlf = "# Achieve Goal: T\r\nStatus: draft\r\nCreated: 2026-05-27\r\n"
    out = gal.set_status(crlf, "active")
    assert "Status: active\r\n" in out  # CRLF on the status line preserved
    assert "Status: draft" not in out


def test_goal_path_rejects_malformed_dates(tmp_path: Path) -> None:
    for bad in ("2026/05/27", "../escape", "2026-5-7", "not-a-date"):
        with pytest.raises(ValueError):
            gal.goal_path(tmp_path, bad, "g")
    # well-formed date is accepted and stays inside the goals namespace
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    assert path.parent == tmp_path / "charness-artifacts" / "goals"


def test_fenced_headings_are_ignored(tmp_path: Path) -> None:
    doc = (
        "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n"
        "## Slice Log\n\n"
        "### Slice 1: real\n- Objective: x\n\n"
        "```md\n### Slice 9: fake-in-fence\n## Off-Goal Findings\n```\n\n"
        "## Off-Goal Findings\n\nKEEP-THIS\n"
    )
    # fenced "### Slice 9" must not bump the counter
    assert gal.next_slice_number(doc) == 2
    out = gal.append_slice(doc, gal.render_slice_block(2, "second", {"Objective": "y"}))
    # inserted into the real Slice Log (before the real Off-Goal section), trailing content intact
    assert "KEEP-THIS" in out
    assert out.index("### Slice 2: second") < out.rindex("## Off-Goal Findings")
    assert "### Slice 9: fake-in-fence" in out  # fenced content untouched


def test_unbalanced_fence_fails_open_and_still_sees_sections() -> None:
    # An unclosed ``` must not mask every heading to EOF (regression guard).
    doc = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x`\n\n"
        "## Active Operating Frame\n"
        "## Goal\n```python\nprint(1)\n"  # fence never closed
        "## Non-Goals\n## Boundaries\n## User Acceptance\n## Agent Verification Plan\n"
        "## Slice Plan\n## Slice Log\n## Off-Goal Findings\n## Final Verification\n"
        "## User Verification Instructions\n## Auto-Retro\n"
    )
    result = gal.check_goal(doc)
    assert result["missing_sections"] == []  # all sections still detected


def test_check_goal_does_not_count_fenced_sections() -> None:
    fenced_only = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x`\n\n"
        "```md\n## Goal\n## Non-Goals\n## Boundaries\n```\n"
    )
    result = gal.check_goal(fenced_only)
    assert result["ok"] is False
    assert "Goal" in result["missing_sections"]


# --- Portability self-test fixtures (#230 + #229 goal, slice 2) -----------


_REQUIRED_BODY = (
    "## Active Operating Frame\n## Goal\n## Non-Goals\n## Boundaries\n## User Acceptance\n"
    "## Agent Verification Plan\n"
)
_TAIL_SECTIONS = (
    "## Slice Log\n## Off-Goal Findings\n## Final Verification\n"
    "## User Verification Instructions\n## Auto-Retro\n"
)
_PORTABILITY_BODY = (
    "## Context Sources\n- src\n## Interview Decisions\n- Q1\n"
    "## Plan Critique Findings\n- blocker folded\n"
)
_GOAL_HEAD = "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n"


def _goal_with_table(rows: list[str], portability: str = "") -> str:
    body = _GOAL_HEAD + _REQUIRED_BODY
    body += "## Slice Plan\n\n"
    body += "| Slice | Objective | Why | Evidence | Status |\n"
    body += "| --- | --- | --- | --- | --- |\n"
    for row in rows:
        body += row + "\n"
    body += "\n" + portability + _TAIL_SECTIONS
    return body


def test_slice_plan_table_row_count_table_form() -> None:
    one_row = _goal_with_table(["| 1 | a | now | x | planned |"])
    assert gal.slice_plan_data_row_count(one_row) == 1
    two_rows = _goal_with_table([
        "| 1 | a | now | x | planned |",
        "| 2 | b | next | y | planned |",
    ])
    assert gal.slice_plan_data_row_count(two_rows) == 2


def test_single_slice_goal_still_requires_portability() -> None:
    # #255: size no longer exempts. Even a 1-row Slice Plan must carry the
    # three portability headings now that the trivial-goal exemption is gone.
    one_row = _goal_with_table(["| 1 | a | now | x | planned |"])  # no portability
    result = gal.check_goal(one_row)
    assert result["ok"] is False
    assert result["portability_missing_sections"] == list(gal.PORTABILITY_SECTIONS)


def test_marker_prose_does_not_exempt_portability() -> None:
    # #255 regression lock: a goal whose prose merely *mentions* the old
    # "single-slice goal" marker phrase must still be portability-checked. The
    # removed full-text _TRIVIAL_GOAL_MARKER scan silently exempted exactly this.
    body = _goal_with_table([
        "| 1 | a | now | x | planned |",
        "| 2 | b | next | y | planned |",
    ])  # no portability sections
    body = body.replace(
        "## Slice Plan\n",
        "## Slice Plan\n\nThis is not a single-slice goal; it has two slices.\n",
        1,
    )
    result = gal.check_goal(body)
    assert result["ok"] is False
    assert result["portability_missing_sections"] == list(gal.PORTABILITY_SECTIONS)


def test_marker_prose_with_portability_sections_passes() -> None:
    # The phrase is inert once the three headings are present: content/prose is
    # never classified; only heading presence is checked.
    body = _goal_with_table(
        [
            "| 1 | a | now | x | planned |",
            "| 2 | b | next | y | planned |",
        ],
        portability=_PORTABILITY_BODY,
    )
    body = body.replace(
        "## Goal\n", "## Goal\nThis mentions a single-slice goal in prose.\n", 1
    )
    result = gal.check_goal(body)
    assert result["ok"] is True
    assert result["portability_missing_sections"] == []


def test_check_goal_reports_missing_portability() -> None:
    body = _goal_with_table([
        "| 1 | a | now | x | planned |",
        "| 2 | b | next | y | planned |",
    ])  # no portability sections
    result = gal.check_goal(body)
    assert result["ok"] is False
    assert result["portability_missing_sections"] == list(gal.PORTABILITY_SECTIONS)
    assert any("portability" in issue.lower() for issue in result["issues"])


def test_check_goal_passes_with_portability_sections_present() -> None:
    body = _goal_with_table(
        [
            "| 1 | a | now | x | planned |",
            "| 2 | b | next | y | planned |",
        ],
        portability=_PORTABILITY_BODY,
    )
    result = gal.check_goal(body)
    assert result["ok"] is True
    assert result["portability_missing_sections"] == []


def test_scaffold_carries_portability_headings(tmp_path: Path) -> None:
    # A freshly scaffolded goal carries all three portability headings from the
    # template, so the always-on check passes at draft time. (#255: the check is
    # always-on; the template — not an exemption — is what keeps it quiet.)
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    text = _goal_text(tmp_path)
    result = gal.check_goal(text)
    assert result["ok"] is True
    assert result["portability_missing_sections"] == []


# --- After-phase closeout-evidence gate (#230, slice 3) -------------------


def _seed_retro(tmp_path: Path, slug: str = "g") -> Path:
    retro = tmp_path / "charness-artifacts/retro" / f"2026-05-28-{slug}.md"
    retro.parent.mkdir(parents=True, exist_ok=True)
    retro.write_text("# Retro\n\nbody\n", encoding="utf-8")
    return retro


def _seed_probe(tmp_path: Path, slug: str = "g") -> Path:
    probe = tmp_path / "charness-artifacts/probe" / f"2026-05-28-{slug}.json"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text('{"host":"claude-code"}\n', encoding="utf-8")
    return probe


def _append_evidence_lines(text: str, retro_value: str, probe_value: str) -> str:
    return text.replace(
        "## Final Verification\n",
        f"## Final Verification\n\nRetro: {retro_value}\nHost log probe: {probe_value}\n",
        1,
    )


def test_parse_closeout_evidence_handles_path_and_skip() -> None:
    text = (
        "Retro: charness-artifacts/retro/2026-05-28-g.md\n"
        "Host log probe: skipped: host-log-not-exposed: claude jsonl unavailable\n"
    )
    parsed = gal.parse_closeout_evidence(text)
    assert parsed["retro_artifact"] == {
        "kind": "evidence",
        "value": "charness-artifacts/retro/2026-05-28-g.md",
    }
    assert parsed["host_log_probe"]["kind"] == "skip"
    assert "host-log-not-exposed" in parsed["host_log_probe"]["value"]


def test_check_complete_evidence_passes_with_real_files(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug="g", title="T")
    retro = _seed_retro(tmp_path)
    probe = _seed_probe(tmp_path)
    text = _goal_text(tmp_path, date="2026-05-28")
    text = _append_evidence_lines(
        text,
        retro_value=str(retro.relative_to(tmp_path)),
        probe_value=str(probe.relative_to(tmp_path)),
    )
    report = gal.check_complete_evidence(tmp_path, text)
    assert report["ok"] is True


def test_check_complete_evidence_fails_when_no_lines(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug="g", title="T")
    text = _goal_text(tmp_path, date="2026-05-28")
    report = gal.check_complete_evidence(tmp_path, text)
    assert report["ok"] is False
    assert set(report["missing"]) == set(gal.CLOSEOUT_EVIDENCE_NAMES)


def test_upsert_refuses_flip_to_complete_without_evidence(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug="g", title="T")
    refusal = gal.upsert_goal(
        tmp_path, date="2026-05-28", slug="g", title="T", status="complete"
    )
    assert refusal["action"] == "refused"
    assert refusal["status"] != "complete"
    # the file's Status line must still say what it was before the call
    assert "Status: complete" not in _goal_text(tmp_path, date="2026-05-28")
    # the refusal payload carries the evidence diagnostic
    assert refusal["evidence_report"]["ok"] is False


def test_upsert_allows_flip_to_complete_with_valid_skips(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug="g", title="T")
    skip_line = "skipped: host-log-not-exposed: claude jsonl path missing on this host"
    text = _goal_text(tmp_path, date="2026-05-28")
    text = _append_evidence_lines(text, retro_value=skip_line, probe_value=skip_line)
    gal.goal_path(tmp_path, "2026-05-28", "g").write_text(text, encoding="utf-8")
    result = gal.upsert_goal(
        tmp_path, date="2026-05-28", slug="g", title="T", status="complete"
    )
    assert result["action"] in ("updated", "unchanged")
    assert result["status"] == "complete"
    assert "Status: complete" in _goal_text(tmp_path, date="2026-05-28")


def test_upsert_refuses_flip_to_complete_with_invalid_skip(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug="g", title="T")
    text = _goal_text(tmp_path, date="2026-05-28")
    text = _append_evidence_lines(
        text,
        retro_value="skipped: ad-hoc: lighter substitute (anti-pattern)",
        probe_value="skipped: ad-hoc: lighter substitute (anti-pattern)",
    )
    gal.goal_path(tmp_path, "2026-05-28", "g").write_text(text, encoding="utf-8")
    refusal = gal.upsert_goal(
        tmp_path, date="2026-05-28", slug="g", title="T", status="complete"
    )
    assert refusal["action"] == "refused"
    invalid_names = {entry["name"] for entry in refusal["evidence_report"]["invalid_skips"]}
    assert invalid_names == set(gal.CLOSEOUT_EVIDENCE_NAMES)


# --- #233 F1 binding + F2 narration -----------------------------------------

_BIND_SLUG = "233-closeout-binding"


def _seed_named(tmp_path: Path, rel: str, body: str) -> Path:
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def test_derive_goal_tokens_includes_slug_and_numeric_cluster(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug=_BIND_SLUG, title="T")
    text = _goal_text(tmp_path, slug=_BIND_SLUG, date="2026-05-28")
    tokens = gal.derive_goal_tokens(text)
    assert _BIND_SLUG in tokens
    assert "233" in tokens


def test_check_complete_evidence_passes_with_bound_files(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug=_BIND_SLUG, title="T")
    retro = _seed_named(
        tmp_path,
        f"charness-artifacts/retro/2026-05-28-{_BIND_SLUG}.md",
        "# Retro\n\n## Waste\n\nx\n",
    )
    probe = _seed_named(
        tmp_path,
        f"charness-artifacts/probe/2026-05-28-{_BIND_SLUG}.json",
        '{"host":"claude-code"}\n',
    )
    text = _goal_text(tmp_path, slug=_BIND_SLUG, date="2026-05-28")
    text = _append_evidence_lines(
        text,
        retro_value=str(retro.relative_to(tmp_path)),
        probe_value=str(probe.relative_to(tmp_path)),
    )
    report = gal.check_complete_evidence(tmp_path, text)
    assert report["ok"] is True
    assert report["binding_failures"] == []


def test_check_complete_evidence_rejects_stale_unrelated_retro(tmp_path: Path) -> None:
    # The #233 F1 attack: cite a present, non-empty, but unrelated retro.
    gal.upsert_goal(tmp_path, date="2026-05-28", slug=_BIND_SLUG, title="T")
    stale = _seed_named(
        tmp_path,
        "charness-artifacts/retro/2026-04-10-some-old.md",
        "# Old retro from a different goal\n",
    )
    probe = _seed_named(
        tmp_path,
        f"charness-artifacts/probe/2026-05-28-{_BIND_SLUG}.json",
        '{"host":"claude-code"}\n',
    )
    text = _goal_text(tmp_path, slug=_BIND_SLUG, date="2026-05-28")
    text = _append_evidence_lines(
        text,
        retro_value=str(stale.relative_to(tmp_path)),
        probe_value=str(probe.relative_to(tmp_path)),
    )
    report = gal.check_complete_evidence(tmp_path, text)
    assert report["ok"] is False
    failed = {entry["name"] for entry in report["binding_failures"]}
    assert failed == {"retro_artifact"}


def test_upsert_refuses_flip_to_complete_with_stale_retro(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug=_BIND_SLUG, title="T")
    stale = _seed_named(
        tmp_path,
        "charness-artifacts/retro/2026-04-10-some-old.md",
        "# Old retro\n",
    )
    probe = _seed_named(
        tmp_path,
        f"charness-artifacts/probe/2026-05-28-{_BIND_SLUG}.json",
        '{"host":"claude-code"}\n',
    )
    text = _goal_text(tmp_path, slug=_BIND_SLUG, date="2026-05-28")
    text = _append_evidence_lines(
        text,
        retro_value=str(stale.relative_to(tmp_path)),
        probe_value=str(probe.relative_to(tmp_path)),
    )
    gal.goal_path(tmp_path, "2026-05-28", _BIND_SLUG).write_text(text, encoding="utf-8")
    refusal = gal.upsert_goal(
        tmp_path, date="2026-05-28", slug=_BIND_SLUG, title="T", status="complete"
    )
    assert refusal["action"] == "refused"
    assert refusal["evidence_report"]["binding_failures"]


def test_check_complete_evidence_fails_closed_when_identity_underivable(
    tmp_path: Path,
) -> None:
    # F-A: a bare `Activation:` substring satisfies check_goal but yields no
    # binding tokens. Binding must fail closed for cited evidence files rather
    # than silently opt out (which would reopen the F1 stale-citation hole).
    retro = _seed_named(
        tmp_path, "charness-artifacts/retro/2026-04-10-some-old.md", "# Old\n"
    )
    probe = _seed_named(
        tmp_path, "charness-artifacts/probe/2026-04-10-some-old.json", "{}\n"
    )
    text = (
        "# Achieve Goal: T\n\nStatus: active\nActivation: see above\n\n"
        "## Final Verification\n\n"
        f"Retro: {retro.relative_to(tmp_path)}\n"
        f"Host log probe: {probe.relative_to(tmp_path)}\n"
    )
    assert gal.derive_goal_tokens(text) == []
    report = gal.check_complete_evidence(tmp_path, text)
    assert report["ok"] is False
    failed = {entry["name"] for entry in report["binding_failures"]}
    assert failed == set(gal.CLOSEOUT_EVIDENCE_NAMES)


def test_narration_required_sections_surface_from_bound_retro(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug=_BIND_SLUG, title="T")
    retro = _seed_named(
        tmp_path,
        f"charness-artifacts/retro/2026-05-28-{_BIND_SLUG}.md",
        "# Retro\n\n## Waste\n\na\n\n## Critical Decisions\n\nb\n"
        "\n## Next Improvements\n\nc\n\n## Sibling Search\n\nd\n",
    )
    probe = _seed_named(
        tmp_path,
        f"charness-artifacts/probe/2026-05-28-{_BIND_SLUG}.json",
        '{"host":"claude-code"}\n',
    )
    text = _goal_text(tmp_path, slug=_BIND_SLUG, date="2026-05-28")
    text = _append_evidence_lines(
        text,
        retro_value=str(retro.relative_to(tmp_path)),
        probe_value=str(probe.relative_to(tmp_path)),
    )
    report = gal.check_complete_evidence(tmp_path, text)
    assert report["narration_required_sections"] == [
        "Waste",
        "Critical Decisions",
        "Next Improvements",
        "Sibling Search",
    ]
