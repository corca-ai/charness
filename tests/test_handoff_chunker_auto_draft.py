"""Slice 5 auto-draft writer tests.

Pins the spec's depth-bounded guarantees:

- Rendered heading line is `# Achieve Goal: <objective>` with a single
  prefix (no `# Achieve Goal: Achieve Goal: ...` double-prefix bug from
  slice-1 critique finding 1).
- The auto-drafted artifact passes ``check_goal_artifact.check_goal``
  at status `draft`.
- ``Context Sources`` is non-empty (preserves provenance).
- ``User Acceptance``, ``Agent Verification Plan``, ``Interview
  Decisions``, and ``Plan Critique Findings`` contain only the
  placeholder line — no narrative prose, no data rows, no sub-headings.
- ``Slice Plan`` data row count is 0 at write time (the /achieve
  Before-phase fills the rows).
- Marker prose quoted from a handoff entry is rendered verbatim and is
  harmless: #255 removed the trivial-goal exemption, so no phrase can
  neuter the portability gate.
- The slice-5 Standalone-Usefulness Invariant: no file under
  ``skills/public/achieve/`` was mutated by the slice (file-mutation
  gate, not import gate).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "handoff-snapshot-2026-05-28.md"
LIB_PATH = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "chunked_routing_lib.py"
)
DRAFTER_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "draft_goal_from_chunk.py"
)
GOAL_LIB_PATH = (
    REPO_ROOT
    / "skills"
    / "public"
    / "achieve"
    / "scripts"
    / "goal_artifact_lib.py"
)


def _load_lib(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lib():
    return _load_lib(LIB_PATH, "chunked_routing_lib")


@pytest.fixture(scope="module")
def goal_lib():
    return _load_lib(GOAL_LIB_PATH, "achieve_goal_artifact_lib")


@pytest.fixture(scope="module")
def real_entries(lib):
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    return lib.parse_handoff_entries(text)


@pytest.fixture(scope="module")
def chunk_from_entry_1(lib, real_entries):
    """The first standalone chunk derived from the slice-2 fixture
    (entry 1: 'Activate the handoff-chunked-routing goal'). Real
    handoff text so the writer is exercised against real content."""
    proposal = lib.propose_merges(real_entries)
    return proposal.standalone[0]


# Heading single-prefix invariant -------------------------------------------


def test_rendered_heading_is_single_prefix(lib, chunk_from_entry_1):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    first_line = text.splitlines()[0]
    assert first_line.startswith("# Achieve Goal: ")
    # The objective text immediately follows; no second "Achieve Goal:"
    # token should appear in the heading line.
    body_after_prefix = first_line[len("# Achieve Goal: "):]
    assert not body_after_prefix.startswith("Achieve Goal:")
    # The objective should be the chunk's objective_summary verbatim.
    assert body_after_prefix == chunk_from_entry_1.objective_summary.strip()


# check_goal_artifact contract ----------------------------------------------


def test_auto_drafted_artifact_passes_check_goal(lib, goal_lib, chunk_from_entry_1):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    report = goal_lib.check_goal(text)
    assert report["ok"] is True, report["issues"]
    assert report["status"] == "draft"
    assert report["missing_sections"] == []


def test_auto_drafted_artifact_has_all_required_sections(
    lib, goal_lib, chunk_from_entry_1
):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    for section in goal_lib.REQUIRED_SECTIONS:
        assert f"## {section}" in text, section
    assert "## Active Operating Frame" in text
    assert "run `/achieve @charness-artifacts/goals/2026-05-28-test.md`" in text


# Auto-draft skeleton invariant: Slice Plan has 0 data rows -----------------


def test_slice_plan_data_row_count_is_zero(lib, goal_lib, chunk_from_entry_1):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    # The auto-draft skeleton leaves the Slice Plan empty; the /achieve
    # Before-phase fills the rows.
    assert goal_lib.slice_plan_data_row_count(text) == 0


# #255: marker prose in a handoff entry is rendered verbatim and is harmless --


def test_quoted_handoff_marker_prose_is_harmless(lib, goal_lib):
    """#255 removed the trivial-goal exemption, so there is no marker phrase a
    quoted handoff entry could use to neuter the portability gate. The former
    ``_scrub_trivial_goal_marker`` mitigation is therefore gone: marker prose is
    rendered verbatim (ASCII hyphen, not the old U+2011 escape), the draft still
    passes ``check_goal`` because the template seeds all three portability
    headings, and filling slice rows never changes that — the headings are
    always required, never exempted.
    """
    poison_entry = lib.HandoffEntry(
        index=1,
        title="Defer the single-slice goal pattern review",
        body=(
            "This residual mentions a previous single-slice goal artifact "
            "by name. Background: we wrote a single-slice goal in May.\n"
            "Single-Slice Goal is a phrase that no longer affects the gate."
        ),
        referenced_paths=("docs/handoff.md",),
        referenced_issues=(),
        referenced_skills=(),
        boundary_tokens=("docs/handoff.md",),
    )
    chunk = lib.ChunkCandidate(
        entries=(poison_entry,),
        label="chunk-1",
        objective_summary=(
            "Resolve the single-slice goal followup without poisoning the gate"
        ),
    )
    text = lib.render_auto_draft_artifact(
        chunk,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-poison-test.md",
    )
    # Rendered verbatim: the ASCII-hyphen phrase IS present (no scrub), and the
    # old non-breaking-hyphen escape form is absent.
    assert "single-slice goal" in text.lower()
    assert "single‑slice goal" not in text.lower()
    # The draft passes check_goal at write time (template seeds the 3 headings).
    assert goal_lib.check_goal(text)["ok"] is True
    # Filling two Slice Plan data rows does not change the portability outcome:
    # the headings are present, so the marker prose is irrelevant.
    populated = text.replace(
        "| Slice | Objective | Why Now | Expected Evidence | Status |\n"
        "| --- | --- | --- | --- | --- |\n",
        "| Slice | Objective | Why Now | Expected Evidence | Status |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| 1 | First | Now | Evidence | planned |\n"
        "| 2 | Second | Now | Evidence | planned |\n",
    )
    assert goal_lib.check_goal(populated)["ok"] is True
    assert goal_lib.check_goal(populated)["portability_missing_sections"] == []


# Context Sources is seeded (non-empty) -------------------------------------


def test_context_sources_is_non_empty_with_citations(lib, chunk_from_entry_1):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    after_heading = text.split("## Context Sources", 1)[1].split("##", 1)[0]
    # Non-empty: contains the source-entry citation pattern.
    assert "Source: handoff entry" in after_heading
    # The slice-2 entry 1 references an artifact path; the citation list
    # carries it forward.
    assert "Cited path:" in after_heading


# Placeholder-only sections (no prose / no data / no sub-headings) ----------


def _section_body(text: str, section: str) -> str:
    after = text.split(f"## {section}", 1)[1]
    return after.split("\n## ", 1)[0]


def test_user_acceptance_contains_only_placeholder(lib, chunk_from_entry_1):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    body = _section_body(text, "User Acceptance").strip()
    assert body == lib.USER_ACCEPTANCE_PLACEHOLDER


def test_agent_verification_contains_only_placeholder_no_subheadings(
    lib, chunk_from_entry_1
):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    body = _section_body(text, "Agent Verification Plan").strip()
    assert body == lib.AGENT_VERIFICATION_PLACEHOLDER
    # The empty goal-artifact template has 3 sub-headings (Low-Cost /
    # High-Confidence / External-Or-Live); the auto-draft writer must
    # strip them per slice-1 critique finding 4.
    assert "### Low-Cost Checks" not in body
    assert "### High-Confidence Checks" not in body
    assert "### External Or Live Proof" not in body


def test_interview_decisions_contains_only_placeholder(lib, chunk_from_entry_1):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    body = _section_body(text, "Interview Decisions").strip()
    assert body == lib.INTERVIEW_DECISIONS_PLACEHOLDER


def test_plan_critique_findings_contains_only_placeholder(lib, chunk_from_entry_1):
    text = lib.render_auto_draft_artifact(
        chunk_from_entry_1,
        date="2026-05-28",
        goal_rel="charness-artifacts/goals/2026-05-28-test.md",
    )
    body = _section_body(text, "Plan Critique Findings").strip()
    assert body == lib.PLAN_CRITIQUE_PLACEHOLDER


# Standalone-Usefulness Invariant -------------------------------------------


def test_no_file_under_skills_public_achieve_was_mutated_by_this_slice():
    """The slice-5 gate from the goal artifact: `git diff --name-only
    main..HEAD | grep '^skills/public/achieve/'` must return empty
    for this slice's diff. The check covers the staged + unstaged
    + currently-committed-but-unpushed range main..HEAD.

    This test runs only when the repo is in a state where `main` is
    reachable; otherwise it skips (relevant only in the active branch
    context).
    """
    git_root = REPO_ROOT
    result = subprocess.run(
        ["git", "diff", "--name-only", "main..HEAD"],
        cwd=git_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"git diff main..HEAD not resolvable: {result.stderr.strip()}")
    changed = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip().startswith("skills/public/achieve/")
    ]
    assert changed == [], (
        "Slice 5 must not mutate any file under skills/public/achieve/ "
        "to preserve the standalone-usefulness invariant; offending: "
        f"{changed}"
    )


# Slug derivation ------------------------------------------------------------


def test_auto_draft_slug_includes_issue_numbers_when_present(lib, real_entries):
    """Entry 3 of the slice-2 fixture references #233, #230, #229; the
    auto-derived slug must carry these so the artifact filename names
    the issues it addresses."""
    proposal = lib.propose_merges(real_entries)
    chunk_3 = proposal.standalone[2]
    slug = lib.auto_draft_slug(chunk_3)
    assert "issue-" in slug
    assert "233" in slug


# CLI smoke -----------------------------------------------------------------


def test_cli_writes_artifact_and_reports_check_goal_ok(tmp_path, lib, chunk_from_entry_1):
    """End-to-end CLI smoke: pipe a ChunkCandidate JSON to the drafter,
    assert it writes the artifact under tmp_path's charness-artifacts/goals/
    and reports ok=true with the activation line filled."""
    chunk_payload = json.dumps(chunk_from_entry_1.to_dict())
    result = subprocess.run(
        [
            "python3",
            str(DRAFTER_SCRIPT),
            "--chunk",
            "-",
            "--date",
            "2026-05-28",
            "--slug",
            "test-cli-smoke",
            "--repo-root",
            str(tmp_path),
        ],
        input=chunk_payload,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "draft"
    written = Path(payload["path"])
    assert written.is_file()
    assert written.name == "2026-05-28-test-cli-smoke.md"
    text = written.read_text(encoding="utf-8")
    assert text.startswith("# Achieve Goal: ")
    assert "Activation: `/goal @" in text


def test_cli_next_step_routes_through_achieve_before_phase(
    tmp_path, lib, chunk_from_entry_1
):
    """#246: an auto-drafted goal is UNSHAPED (placeholder sections), so the
    drafter must surface the achieve Before-phase shaping step as the
    operator's next move — not `/goal` activation, which would start the During
    run on an unshaped goal. The artifact's own `activation` line stays `/goal`
    (a correct goal-artifact field); `next_step`/`shape_command` route through
    `/achieve`."""
    chunk_payload = json.dumps(chunk_from_entry_1.to_dict())
    result = subprocess.run(
        [
            "python3",
            str(DRAFTER_SCRIPT),
            "--chunk",
            "-",
            "--date",
            "2026-05-28",
            "--slug",
            "test-next-step",
            "--repo-root",
            str(tmp_path),
        ],
        input=chunk_payload,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    goal_rel = "charness-artifacts/goals/2026-05-28-test-next-step.md"
    # The artifact's own activation line is unchanged (correct goal field).
    assert payload["activation"] == f"/goal @{goal_rel}"
    # The operator's next move must shape via the achieve Before-phase, and
    # must NOT be a bare `/goal` (that is exactly the #246 regression).
    assert payload["shape_command"] == f"/achieve @{goal_rel}"
    next_step = payload["next_step"]
    assert f"/achieve @{goal_rel}" in next_step
    assert "Before-phase" in next_step
    assert not next_step.lstrip().startswith("/goal")
    # The placeholder sentinels confirm the draft really is unshaped, so the
    # shape-first routing is load-bearing, not cosmetic.
    text = Path(payload["path"]).read_text(encoding="utf-8")
    assert lib.USER_ACCEPTANCE_PLACEHOLDER in text


def test_cli_refuses_to_overwrite_existing_artifact(tmp_path, lib, chunk_from_entry_1):
    chunk_payload = json.dumps(chunk_from_entry_1.to_dict())
    args = [
        "python3",
        str(DRAFTER_SCRIPT),
        "--chunk",
        "-",
        "--date",
        "2026-05-28",
        "--slug",
        "test-cli-overwrite-guard",
        "--repo-root",
        str(tmp_path),
    ]
    first = subprocess.run(args, input=chunk_payload, capture_output=True, text=True, check=False)
    assert first.returncode == 0, first.stderr
    second = subprocess.run(args, input=chunk_payload, capture_output=True, text=True, check=False)
    assert second.returncode != 0
    assert "already exists" in second.stderr
