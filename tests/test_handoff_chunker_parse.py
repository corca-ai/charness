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
PARSER_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "parse_handoff_entries.py"
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
