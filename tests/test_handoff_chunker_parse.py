from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module

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
PARSER_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "parse_handoff_entries.py"
)
_propose_merges = import_repo_module(
    REPO_ROOT / "skills" / "public" / "handoff" / "scripts" / "propose_merges.py",
    "skills.public.handoff.scripts.propose_merges",
)






def _load_lib():
    spec = importlib.util.spec_from_file_location("chunked_routing_lib", LIB_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lib():
    return _load_lib()


@pytest.fixture(scope="module")
def entries(lib):
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    return lib.parse_handoff_entries(text)


def test_parser_returns_seven_entries(entries):
    assert len(entries) == 7


def test_entry_indices_are_one_based_and_contiguous(entries):
    indices = [entry.index for entry in entries]
    assert indices == list(range(1, 8))


def test_titles_collapse_soft_wrapped_bold_markers(entries):
    by_index = {entry.index: entry for entry in entries}
    assert by_index[1].title == "Activate the handoff-chunked-routing goal"
    assert by_index[2].title == (
        "Push the #230 + #229 commits + this handoff-chunked-routing draft"
    )
    # Entry 3 wraps the bold marker across two source lines; the title must
    # collapse to a single line with internal whitespace normalized.
    assert by_index[3].title == (
        "#233 — closeout-gate hardening "
        "(F1 binding + F2 user-message surfacing)"
    )
    assert by_index[4].title == "Confirm Codex host smoke"
    assert by_index[7].title == "Mutation residuals"


def test_issue_references_are_collected_in_first_seen_order(entries):
    by_index = {entry.index: entry for entry in entries}
    assert by_index[2].referenced_issues == (230, 229)
    assert by_index[3].referenced_issues == (233, 230, 229)
    assert by_index[5].referenced_issues == (227,)
    assert by_index[6].referenced_issues == (184, 185)
    assert by_index[7].referenced_issues == (224,)


def test_issue_ranges_are_expanded_in_first_seen_order(lib):
    text = """# Handoff

## Next Session

1. Close #285-#289 after checking #287 and #293 with `issue_tool.py --number 286 --number 294`.
"""
    entries = lib.parse_handoff_entries(text)

    assert entries[0].referenced_issues == (285, 286, 287, 288, 289, 293, 294)


def test_referenced_paths_are_deduped_after_normalization(entries, lib):
    by_index = {entry.index: entry for entry in entries}
    entry_1 = by_index[1]
    canonical = "charness-artifacts/goals/2026-05-28-handoff-chunked-routing.md"
    assert entry_1.referenced_paths == (canonical,)


def test_boundary_tokens_apply_nontrivial_filter(entries, lib):
    by_index = {entry.index: entry for entry in entries}
    # Entry 2 lists many bare-directory tokens (.githooks/, scripts/, skills/,
    # tests/, integrations/) but those are common-noun / single-segment and
    # must NOT count as boundary tokens. integrations/tools/ survives as a
    # 2-segment directory token.
    assert by_index[2].boundary_tokens == ("integrations/tools/",)
    # Entry 7 references nothing path-like at all.
    assert by_index[7].boundary_tokens == ()
    # Entry 1 keeps its one canonical artifact path.
    assert by_index[1].boundary_tokens == (
        "charness-artifacts/goals/2026-05-28-handoff-chunked-routing.md",
    )


def test_negative_merge_pair_entries_2_and_7_share_no_boundary(entries):
    """Spec slice-4 fixture demand: entries 2 and 7 must not merge despite
    both mentioning common bare directory roots in their prose."""
    by_index = {entry.index: entry for entry in entries}
    shared = set(by_index[2].boundary_tokens) & set(by_index[7].boundary_tokens)
    assert shared == set()


def test_is_nontrivial_token_rejects_common_nouns(lib):
    for trivial in (
        "scripts/",
        "tests/",
        "docs/",
        "skills/",
        ".githooks/",
        "plugins/",
        "integrations/",
    ):
        assert not lib.is_nontrivial_token(trivial), trivial


def test_is_nontrivial_token_requires_path_separator(lib):
    assert not lib.is_nontrivial_token("foo")
    assert not lib.is_nontrivial_token("")
    assert lib.is_nontrivial_token("foo/bar")
    assert lib.is_nontrivial_token("integrations/tools/")
    assert lib.is_nontrivial_token("docs/conventions/implementation-discipline.md")


def test_parser_cli_emits_valid_json_with_expected_shape(tmp_path):
    result = subprocess.run(
        [
            "python3",
            str(PARSER_SCRIPT),
            "--handoff-path",
            str(FIXTURE_PATH),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["entry_count"] == 7
    assert len(payload["entries"]) == 7
    for entry in payload["entries"]:
        assert set(entry.keys()) == {
            "index",
            "title",
            "body",
            "referenced_paths",
            "referenced_issues",
            "referenced_skills",
            "boundary_tokens",
            "missing_paths",
            "closed_issues",
            "unresolved_issues",
        }


def test_parser_filters_preflight_and_completed_goal_activation(lib, tmp_path):
    goal = tmp_path / "charness-artifacts/goals/2026-06-01-done.md"
    goal.parent.mkdir(parents=True)
    goal.write_text(
        "# Achieve Goal: Done\n\nStatus: complete\n\n## Goal\nDone.\n",
        encoding="utf-8",
    )
    text = """# Handoff

## Next Session

1. Verify local branch state: `git status --short --branch` and
   `git log --oneline origin/main..HEAD`.
2. Activate the finished goal only when broad work is intended:
   `/goal @charness-artifacts/goals/2026-06-01-done.md`.
3. During any broad goal, follow the proof cadence.
4. Pick the next issue explicitly: #184 or #261.

## Discuss
"""

    entries = lib.parse_handoff_entries(text, repo_root=tmp_path)

    assert [entry.index for entry in entries] == [4]
    assert entries[0].referenced_issues == (184, 261)


def test_parser_reads_top_level_bullet_next_session_entries(lib):
    text = """# Handoff

## Next Session

- **Push the goal-closeout commit** before new work.
- **#353** — adapter_lib renderer hygiene.
- **#184** — operator decision first, not a slice.

## Discuss

- Not part of Next Session parsing.
"""

    entries = lib.parse_handoff_entries(text)

    assert [entry.index for entry in entries] == [1, 2, 3]
    assert [entry.title for entry in entries] == [
        "Push the goal-closeout commit",
        "#353",
        "#184",
    ]
    assert entries[1].referenced_issues == (353,)
    assert entries[2].referenced_issues == (184,)


def test_parser_filters_completed_goal_markdown_link_activation(lib, tmp_path):
    goal = tmp_path / "charness-artifacts/goals/2026-06-01-done.md"
    goal.parent.mkdir(parents=True)
    goal.write_text(
        "# Achieve Goal: Done\n\nStatus: complete\n\n## Goal\nDone.\n",
        encoding="utf-8",
    )
    text = """# Handoff

## Next Session

1. Activate completed goal:
   [done](charness-artifacts/goals/2026-06-01-done.md).
2. Pick the next issue explicitly: #184.

## Discuss
"""

    entries = lib.parse_handoff_entries(text, repo_root=tmp_path)

    assert [entry.index for entry in entries] == [2]


def test_parser_keeps_incomplete_goal_activation(lib, tmp_path):
    goal = tmp_path / "charness-artifacts/goals/2026-06-01-draft.md"
    goal.parent.mkdir(parents=True)
    goal.write_text(
        "# Achieve Goal: Draft\n\nStatus: draft\n\n## Goal\nDraft.\n",
        encoding="utf-8",
    )
    text = """# Handoff

## Next Session

1. Activate the draft goal:
   `/goal @charness-artifacts/goals/2026-06-01-draft.md`.

## Discuss
"""

    entries = lib.parse_handoff_entries(text, repo_root=tmp_path)

    assert len(entries) == 1
    assert entries[0].referenced_paths == (
        "charness-artifacts/goals/2026-06-01-draft.md",
    )


def test_parser_filters_active_goal_activation(lib, tmp_path):
    goal = tmp_path / "charness-artifacts/goals/2026-06-01-active.md"
    goal.parent.mkdir(parents=True)
    goal.write_text(
        "# Achieve Goal: Active\n\nStatus: active\n\n## Goal\nIn progress.\n",
        encoding="utf-8",
    )
    text = """# Handoff

## Next Session

1. Continue active goal:
   `/goal @charness-artifacts/goals/2026-06-01-active.md`.
2. Pick the next issue explicitly: #184.

## Discuss
"""

    entries = lib.parse_handoff_entries(text, repo_root=tmp_path)

    assert [entry.index for entry in entries] == [2]


def test_parser_cli_explicit_docs_handoff_filters_completed_goal(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    goal = tmp_path / "charness-artifacts/goals/2026-06-01-done.md"
    goal.parent.mkdir(parents=True)
    goal.write_text(
        "# Achieve Goal: Done\n\nStatus: complete\n\n## Goal\nDone.\n",
        encoding="utf-8",
    )
    handoff = docs / "handoff.md"
    handoff.write_text(
        """# Handoff

## Next Session

1. Verify local repo state: `git status --short --branch`.
2. Activate completed goal:
   [done](charness-artifacts/goals/2026-06-01-done.md).
3. Pick the next issue explicitly: #184.

## Discuss
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", str(PARSER_SCRIPT), str(handoff)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [entry["index"] for entry in payload["entries"]] == [3]


def test_fixture_handoff_pipeline_preserves_issue_linked_candidates(entries, monkeypatch, capsys):
    parser_payload = {"ok": True, "entries": [entry.to_dict() for entry in entries]}
    monkeypatch.setattr(sys, "argv", ["propose_merges.py"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(parser_payload)))

    assert _propose_merges.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    candidates = payload["standalone"] + payload["merged"]
    assert candidates
    referenced = [
        issue
        for candidate in candidates
        for entry in candidate["entries"]
        for issue in entry["referenced_issues"]
    ]
    assert referenced, "expected the fixture handoff pipeline to surface issue-linked candidates"
    assert all(isinstance(issue, int) and issue > 0 for issue in referenced)


def _load_parser_module():
    spec = importlib.util.spec_from_file_location("parse_handoff_entries", PARSER_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_with_issues_unions_live_backlog(tmp_path, monkeypatch, capsys):
    """#251 regression coverage: the ``--with-issues`` union branch
    (build_issue_entries + dedup_and_union + deduped_issue_count) was never
    exercised, leaving parse_handoff_entries.py with uncovered changed lines
    that blocked the mutation gate. Stub the provider call so no live tracker
    request is made.
    """
    peh = _load_parser_module()
    handoff = tmp_path / "handoff.md"
    handoff.write_text(
        "## Next Session\n\n1. **Only.** do a thing about #99.\n\n## End\n",
        encoding="utf-8",
    )
    iss = peh.chunked_routing_issue_source

    def fake_build(repo_root, *, start_index):
        # one fresh (uncited) issue -> survives the union as a new chunk
        return [iss.issue_to_handoff_entry(
            {"number": 250, "title": "fresh untracked issue", "labels": [], "body": ""},
            start_index,
        )]

    monkeypatch.setattr(iss, "build_issue_entries", fake_build)
    monkeypatch.setattr(
        peh.chunked_routing_staleness,
        "resolve_states_for_repo",
        lambda *_args, **_kwargs: ({}, {"stage": "test-staleness-failure"}),
    )
    monkeypatch.setattr(
        sys, "argv",
        ["parse_handoff_entries.py", "--handoff-path", str(handoff),
         "--repo-root", str(tmp_path), "--with-issues"],
    )

    assert peh.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["handoff_entry_count"] == 1
    assert payload["issue_entry_count"] == 1
    assert payload["deduped_issue_count"] == 0  # #250 uncited -> not deduped
    assert any(e["title"].startswith("#250:") for e in payload["entries"])




def test_cli_with_issues_reports_pre_provider_diagnostic(tmp_path, monkeypatch, capsys):
    peh = _load_parser_module()
    handoff = tmp_path / "handoff.md"
    handoff.write_text("## Next Session\n\n1. Pick #184.\n\n## End\n", encoding="utf-8")

    def missing_issue_skill(root, name):
        raise ImportError("installed issue skill missing")

    def should_not_run(*_args, **_kwargs):
        raise AssertionError("staleness provider must not run after a pre-provider failure")

    monkeypatch.setattr(peh.chunked_routing_issue_source, "_load_issue_module", missing_issue_skill)
    monkeypatch.setattr(peh.chunked_routing_staleness, "resolve_states_for_repo", should_not_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "parse_handoff_entries.py",
            "--handoff-path",
            str(handoff),
            "--repo-root",
            str(tmp_path),
            "--with-issues",
        ],
    )

    assert peh.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    diagnostic = payload["issue_source_diagnostic"]
    assert payload["issue_entry_count"] == 0
    assert diagnostic["stage"] == "load_issue_modules"
    assert diagnostic["provider_attempted"] is False
    assert "installed issue skill missing" in diagnostic["message"]
    assert payload["staleness"]["issue_states_checked"] is False
    assert payload["staleness"]["diagnostic"]["stage"] == "issue_source"
    assert payload["staleness"]["diagnostic"]["provider_attempted"] is False
    assert "skipped because issue source failed" in payload["staleness"]["diagnostic"]["message"]






def test_a_dot_slash_link_resolves_against_the_citing_artifact(tmp_path: Path, lib) -> None:
    """A cited link is relative to the CITING file, not to the repo root.

    Prefix-stripping made `../charness-artifacts/x.md` right by coincidence (from
    `docs/`, `docs/..` IS the root) and `./deferred-decisions.md` wrong, so a live
    correct link was reported as a stale citation and the drafter stamped MISSING
    on it. Reproduced against the repo's own handoff before this fix:
    `missing_path_count` was 1 with zero stale citations.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "deferred-decisions.md").write_text("d\n", encoding="utf-8")
    (repo / "charness-artifacts" / "critique").mkdir(parents=True)
    (repo / "charness-artifacts" / "critique" / "x.md").write_text("c\n", encoding="utf-8")
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n"
        "1. Work the rows in [that critique](../charness-artifacts/critique/x.md)\n"
        "   and the deferred [D39](./deferred-decisions.md).\n",
        encoding="utf-8",
    )

    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == [
        "charness-artifacts/critique/x.md",
        "docs/deferred-decisions.md",
    ]

    staleness = import_repo_module(
        REPO_ROOT / "skills" / "public" / "handoff" / "scripts" / "chunked_routing_staleness.py",
        "skills.public.handoff.scripts.chunked_routing_staleness",
    )
    assert staleness.missing_paths(repo, entries[0].referenced_paths) == ()


def test_prefix_stripping_survives_when_no_artifact_dir_is_supplied(tmp_path: Path, lib) -> None:
    """Library callers that only have text keep today's behavior.

    The fallback is deliberate, not an oversight: without the citing directory
    there is no correct base, and inventing one would be the same wrong-base
    mistake in the other direction.
    """
    text = "# H\n\n## Next Session\n\n1. See [d](./deferred-decisions.md).\n"
    entries = lib.parse_handoff_entries(text)
    assert list(entries[0].referenced_paths) == ["deferred-decisions.md"]


def test_a_link_escaping_the_repo_is_not_pulled_back_inside(tmp_path: Path, lib) -> None:
    """An out-of-tree citation must not be claimed as an in-repo path.

    What this pins is the ESCAPE GUARD: without the `../` check in
    `_resolve_lexically` the token would canonicalize to `../outside/thing.md` and
    the assertion fails.

    What it does NOT pin, stated because the first version of this docstring
    claimed it did: a restored root-base fallback would resolve the stripped form
    against `.` and return the same string, so this test cannot tell the two
    apart. The in-repo decoy below is therefore scenery for that half; the
    cross-style laundering it was meant to catch is pinned by
    `test_a_genuinely_missing_citation_is_reported_at_its_CORRECT_base` instead,
    where the two behaviors DO produce different strings.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "outside").mkdir(parents=True)
    (repo / "outside" / "thing.md").write_text("the IN-repo decoy\n", encoding="utf-8")
    (tmp_path / "outside").mkdir(parents=True, exist_ok=True)
    (tmp_path / "outside" / "thing.md").write_text("the real target\n", encoding="utf-8")
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. See [up](../../outside/thing.md).\n", encoding="utf-8"
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == ["outside/thing.md"]
    assert not any(path.startswith("/") for path in entries[0].referenced_paths)


def test_a_repo_root_relative_bare_path_is_not_resolved_against_the_artifact_dir(
    tmp_path: Path, lib
) -> None:
    """The other citation style, pinned as the regression it was.

    This repo's handoffs also write bare repo-root-relative paths. Resolving those
    against the citing directory turns `charness-artifacts/goals/x.md` into
    `docs/charness-artifacts/goals/x.md`, which does not exist -- and the
    completed-goal filter silently stops firing. The first cut of this fix did
    exactly that and the repo's own CLI test caught it.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)
    (repo / "charness-artifacts" / "goals" / "x.md").write_text("g\n", encoding="utf-8")
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. See [g](charness-artifacts/goals/x.md).\n",
        encoding="utf-8",
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == ["charness-artifacts/goals/x.md"]


def test_a_genuinely_missing_citation_is_reported_at_its_CORRECT_base(
    tmp_path: Path, lib
) -> None:
    """An explicitly relative link resolves whether or not the file is on disk.

    Falling back to the stripped form when the correct base is missing is not
    neutral: `./README.md` cited from `docs/` strips to `README.md`, which the
    staleness check then finds at the ROOT and reports live — the citation names
    the wrong surface with no MISSING marker, which is this row's own defect
    running in the other direction. Reporting `docs/README.md` as missing is the
    honest answer.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("the ROOT readme, not the cited one\n", encoding="utf-8")
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. See [r](./README.md).\n", encoding="utf-8"
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == ["docs/README.md"]

    staleness = import_repo_module(
        REPO_ROOT / "skills" / "public" / "handoff" / "scripts" / "chunked_routing_staleness.py",
        "skills.public.handoff.scripts.chunked_routing_staleness",
    )
    assert staleness.missing_paths(repo, entries[0].referenced_paths) == ("docs/README.md",)


def test_a_directory_token_keeps_its_trailing_slash(tmp_path: Path, lib) -> None:
    """Boundary tokens are intersected as EXACT strings across sources.

    Handoff entries normalize with an artifact dir; issue-derived entries do not.
    Path joining discards a trailing slash, so `integrations/tools` (handoff side)
    and `integrations/tools/` (issue side) stopped intersecting and a merge that
    fired before this slice silently stopped firing — in the very invocation the
    slice enables (`--with-issues`).
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. Work integrations/tools/ next.\n", encoding="utf-8"
    )
    with_dir = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    without_dir = lib.parse_handoff_entries(handoff.read_text(encoding="utf-8"))
    assert list(with_dir[0].referenced_paths) == ["integrations/tools/"]
    assert list(with_dir[0].referenced_paths) == list(without_dir[0].referenced_paths)


def test_a_relative_directory_token_keeps_its_trailing_slash(tmp_path: Path, lib) -> None:
    """The relative branch's slash re-append, which the bare-token test never reaches.

    A bare token resolves through the root base and returns before the relative
    branch runs, so deleting that branch's `_with_token_slash` wrapper would leave
    the suite green while re-introducing the blocker for `../integrations/tools/`.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. Work [tools](../integrations/tools/) next.\n",
        encoding="utf-8",
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == ["integrations/tools/"]


def test_a_bare_token_uses_the_root_base_on_both_sources(tmp_path: Path, lib) -> None:
    """Round 1's blocker, re-created by round 1's repair with the BASE diverging.

    Issue-derived entries normalize with no artifact dir. When bare tokens also
    tried the artifact base, a handoff citation of `conventions/x.md` became
    `docs/conventions/x.md` while the issue side stayed `conventions/x.md`, and the
    merger intersects boundary tokens as EXACT strings — so the two never met.
    """
    repo = tmp_path / "repo"
    (repo / "docs" / "conventions").mkdir(parents=True)
    (repo / "docs" / "conventions" / "x.md").write_text("x\n", encoding="utf-8")
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. See conventions/x.md.\n", encoding="utf-8"
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    parser = import_repo_module(
        REPO_ROOT / "skills" / "public" / "handoff" / "scripts" / "chunked_routing_parser.py",
        "skills.public.handoff.scripts.chunked_routing_parser",
    )
    issue_side = parser._normalize_path("conventions/x.md")
    assert list(entries[0].referenced_paths) == [issue_side]


def test_an_anchor_only_link_cites_no_path(tmp_path: Path, lib) -> None:
    """`[the rule](#skill-routing)` names no path and must not become one.

    The fragment split leaves an empty token; joined onto the artifact base it
    normalized to the artifact DIRECTORY, and the drafter rendered
    `- In scope: docs` — a goal claiming a whole top-level directory, sourced from
    a link that cites nothing. Pre-slice it reached `referenced_paths` as an empty
    string and rendered as an empty backtick; neither is a citation.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. See [the rule](#skill-routing) first.\n",
        encoding="utf-8",
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == []


def test_a_cited_current_pointer_is_not_rewritten_to_its_target(tmp_path: Path, lib) -> None:
    """Resolution is LEXICAL, so a checked-in current-pointer symlink survives.

    `Path.resolve()` follows symlinks, and this repo checks in current pointers
    (`charness-artifacts/*/latest.md`, `CLAUDE.md -> AGENTS.md`). Resolving would
    put the frozen dated target into a drafted goal's Boundaries instead of the
    pointer the author cited, and collapse a pointer+target pair into one entry.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    quality = repo / "charness-artifacts" / "quality"
    quality.mkdir(parents=True)
    (quality / "2026-07-25-review.md").write_text("frozen\n", encoding="utf-8")
    (quality / "latest.md").symlink_to("2026-07-25-review.md")
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. See [q](../charness-artifacts/quality/latest.md).\n",
        encoding="utf-8",
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == ["charness-artifacts/quality/latest.md"]


def test_an_artifact_dir_outside_the_repo_falls_back_to_stripping(tmp_path: Path, lib) -> None:
    """No usable base: keep the pre-slice behavior rather than inventing one.

    `relative_to` raises when the artifact does not live under the given root —
    a mismatched `--repo-root`, or a handoff outside the tree. Guessing a base
    there is the wrong-base mistake this change exists to remove.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    handoff = elsewhere / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. See [d](./deferred-decisions.md).\n", encoding="utf-8"
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == ["deferred-decisions.md"]


def test_a_bare_token_that_escapes_the_root_falls_back_to_stripping(tmp_path: Path, lib) -> None:
    """A bare token whose lexical resolution leaves the tree keeps the stripped form."""
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    handoff = repo / "docs" / "handoff.md"
    handoff.write_text(
        "# H\n\n## Next Session\n\n1. See ../../escaped/thing.md there.\n", encoding="utf-8"
    )
    entries = lib.parse_handoff_entries(
        handoff.read_text(encoding="utf-8"), repo_root=repo, artifact_dir=handoff.parent
    )
    assert list(entries[0].referenced_paths) == ["escaped/thing.md"]


def test_the_citation_root_is_none_outside_any_repo(tmp_path: Path, monkeypatch) -> None:
    """`_path_root_for_citations` returns None rather than guessing.

    The `.git` ancestor is faked ABSENT rather than assumed absent: pytest's
    tmp_path can itself sit inside a git repo (it does on this machine, under
    `~/.cache`), so a test that merely used a temp directory would pin the
    environment instead of the code. That latching is real but bounded — it only
    chooses between two candidate base strings and never drops an entry.
    """
    cli = import_repo_module(PARSER_SCRIPT, "skills.public.handoff.scripts.parse_handoff_entries")
    import argparse

    lonely = tmp_path / "nowhere" / "handoff.md"
    lonely.parent.mkdir(parents=True)
    lonely.write_text("# H\n", encoding="utf-8")

    real_exists = Path.exists
    monkeypatch.setattr(
        Path, "exists", lambda self: False if self.name == ".git" else real_exists(self)
    )
    args = argparse.Namespace(repo_root=None, handoff=None, handoff_path=lonely)
    assert cli._path_root_for_citations(args) is None


def test_a_bare_token_resolving_to_nothing_keeps_the_stripped_form(tmp_path: Path, lib) -> None:
    """The bare branch's own fallback: `resolve_lexically` can return empty.

    A bare `./` (or any token that normalizes away) yields no candidate, and the
    stripped form is what stays — the same non-inventing posture as the relative
    branch.
    """
    paths = import_repo_module(
        REPO_ROOT / "skills" / "public" / "handoff" / "scripts" / "chunked_routing_paths.py",
        "skills.public.handoff.scripts.chunked_routing_paths",
    )
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    assert paths.resolve_lexically(".", "./") == ""
    assert (
        paths.normalize_path("./", artifact_dir=repo / "docs", repo_root=repo) == "docs/"
    )
    assert paths.normalize_path("", artifact_dir=repo / "docs", repo_root=repo) == ""
    # A BARE token that normalizes away takes the bare branch's own fallback.
    assert paths.normalize_path(".", artifact_dir=repo / "docs", repo_root=repo) == "."


def test_the_citation_root_uses_the_live_filter_root_when_there_is_one(tmp_path: Path) -> None:
    """The common case: the two roots coincide and the `.git` walk never runs.

    `--repo-root` is the documented form, and the walk exists only for an explicit
    path from another cwd.
    """
    cli = import_repo_module(PARSER_SCRIPT, "skills.public.handoff.scripts.parse_handoff_entries")
    import argparse

    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    args = argparse.Namespace(repo_root=repo, handoff=None, handoff_path=None)
    assert cli._path_root_for_citations(args) == repo.resolve()
