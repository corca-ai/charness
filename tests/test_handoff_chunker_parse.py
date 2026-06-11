from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.repo_copy import REPO_COPY_IGNORE

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


def _copy_installed_runtime(tmp_path: Path) -> None:
    for rel in (
        "skill_runtime_bootstrap.py",
        "scripts/skill_runtime_bootstrap.py",
        "scripts/runtime_bootstrap.py",
        "scripts/script_timeout.py",
        "scripts/adapter_lib.py",
        "scripts/artifact_naming_lib.py",
        "scripts/simple_skill_adapter_lib.py",
    ):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, target)


def _copy_installed_handoff_scripts(tmp_path: Path) -> Path:
    target = tmp_path / "skills" / "handoff" / "scripts"
    shutil.copytree(
        REPO_ROOT / "skills/public/handoff/scripts",
        target,
        ignore=REPO_COPY_IGNORE,
    )
    return target


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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
    assert [entry["index"] for entry in payload["entries"]] == [3]


def test_fixture_handoff_pipeline_preserves_issue_linked_candidates(entries):
    parser_payload = {"ok": True, "entries": [entry.to_dict() for entry in entries]}
    propose = subprocess.run(
        [
            "python3",
            str(REPO_ROOT / "skills/public/handoff/scripts/propose_merges.py"),
        ],
        input=json.dumps(parser_payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert propose.returncode == 0, propose.stderr
    payload = json.loads(propose.stdout)
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
        sys, "argv",
        ["parse_handoff_entries.py", "--handoff-path", str(handoff),
         "--repo-root", str(tmp_path), "--with-issues"],
    )

    assert peh.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["handoff_entry_count"] == 1
    assert payload["issue_entry_count"] == 1
    assert payload["deduped_issue_count"] == 0  # #250 uncited -> not deduped
    assert any(e["title"].startswith("#250:") for e in payload["entries"])


def test_cli_with_issues_resolves_installed_issue_skill_layout(tmp_path):
    _copy_installed_runtime(tmp_path)
    handoff_scripts = _copy_installed_handoff_scripts(tmp_path)
    issue_scripts = tmp_path / "skills" / "issue" / "scripts"
    issue_scripts.mkdir(parents=True)
    (issue_scripts / "resolve_adapter.py").write_text(
        "def load_adapter(repo_root):\n"
        "    return {'data': {'default_org': 'corca-ai', 'default_repo': 'charness', "
        "'remote_name': 'origin', 'issue_backend': {'id': 'stub', 'binary': 'stub', "
        "'commands': {'list_open': ['list', '{repo}', '{limit}']}}}}\n",
        encoding="utf-8",
    )
    (issue_scripts / "issue_runtime.py").write_text(
        "def resolve_target(repo_root, target, adapter_data):\n"
        "    return {'full_name': 'corca-ai/charness'}\n"
        "def _backend_json(argv):\n"
        "    assert argv == ['stub', 'list', 'corca-ai/charness', '50']\n"
        "    return [{'number': 275, 'title': 'installed issue source', "
        "'labels': [], 'body': ''}]\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    handoff = docs / "handoff.md"
    handoff.write_text("## Next Session\n\n1. Pick #184.\n\n## End\n", encoding="utf-8")

    result = subprocess.run(
        [
            "python3",
            str(handoff_scripts / "parse_handoff_entries.py"),
            "--repo-root",
            str(tmp_path),
            "--handoff-path",
            str(handoff),
            "--with-issues",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["issue_entry_count"] == 1
    assert payload["issue_source_diagnostic"] is None
    assert any(entry["referenced_issues"] == [275] for entry in payload["entries"])


def test_cli_with_issues_reports_pre_provider_diagnostic(tmp_path, monkeypatch, capsys):
    peh = _load_parser_module()
    handoff = tmp_path / "handoff.md"
    handoff.write_text("## Next Session\n\n1. Pick #184.\n\n## End\n", encoding="utf-8")

    def missing_issue_skill(root, name):
        raise ImportError("installed issue skill missing")

    monkeypatch.setattr(peh.chunked_routing_issue_source, "_load_issue_module", missing_issue_skill)
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
    payload = json.loads(capsys.readouterr().out)
    diagnostic = payload["issue_source_diagnostic"]
    assert payload["issue_entry_count"] == 0
    assert diagnostic["stage"] == "load_issue_modules"
    assert diagnostic["provider_attempted"] is False
    assert "installed issue skill missing" in diagnostic["message"]


def test_draft_goal_help_resolves_installed_achieve_skill_layout(tmp_path):
    _copy_installed_runtime(tmp_path)
    handoff_scripts = _copy_installed_handoff_scripts(tmp_path)
    achieve_scripts = tmp_path / "skills" / "achieve" / "scripts"
    achieve_scripts.mkdir(parents=True)
    (achieve_scripts / "goal_artifact_lib.py").write_text(
        "# Stub is enough for --help import-time portability proof.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", str(handoff_scripts / "draft_goal_from_chunk.py"), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--date" in result.stdout


def test_draft_goal_help_prefers_installed_achieve_over_stale_source(tmp_path):
    _copy_installed_runtime(tmp_path)
    handoff_scripts = _copy_installed_handoff_scripts(tmp_path)
    installed = tmp_path / "skills" / "achieve" / "scripts"
    source = tmp_path / "skills" / "public" / "achieve" / "scripts"
    installed.mkdir(parents=True)
    source.mkdir(parents=True)
    (installed / "goal_artifact_lib.py").write_text(
        "# Stub is enough for --help import-time portability proof.\n",
        encoding="utf-8",
    )
    (source / "goal_artifact_lib.py").write_text(
        "raise RuntimeError('stale source achieve loaded')\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", str(handoff_scripts / "draft_goal_from_chunk.py"), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--date" in result.stdout
