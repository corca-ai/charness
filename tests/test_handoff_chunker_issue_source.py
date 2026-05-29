"""#249 slice 2: issue-backed source feeds HandoffEntry records that the
merge proposer clusters by surface, unioned with handoff entries.

All offline: provider listing is exercised through an injected runner stub, so
no live tracker call is made. The live route is proven in the goal's behavior
slice.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "public" / "handoff" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lib():
    return _load("chunked_routing_lib")


@pytest.fixture(scope="module")
def src():
    return _load("chunked_routing_issue_source")


# --- conversion -----------------------------------------------------------


def test_title_path_is_a_boundary_but_body_path_is_not(src):
    """Title paths cluster; body paths are captured as referenced_paths but
    NOT as merge boundaries (precision — avoids the dogfood over-merge)."""
    issue = {
        "number": 244,
        "title": "scripts/host_hook_install_lib.py hardcodes the hook path",
        "labels": [],
        "body": "incidental mention of skills/public/quality/references/x.md here.",
    }
    entry = src.issue_to_handoff_entry(issue, index=7)
    assert entry.index == 7
    assert entry.title.startswith("#244:")
    # title path -> boundary token
    assert "scripts/host_hook_install_lib.py" in entry.boundary_tokens
    # body path -> referenced, but NOT a merge boundary
    assert "skills/public/quality/references/x.md" in entry.referenced_paths
    assert "skills/public/quality/references/x.md" not in entry.boundary_tokens
    # own number leads referenced_issues (slice-3 dedup key)
    assert entry.referenced_issues[0] == 244


def test_specific_label_becomes_boundary_but_generic_does_not(src):
    specific = src.issue_to_handoff_entry(
        {"number": 242, "title": "Mutation regression", "labels": [{"name": "mutation-test"}], "body": ""},
        index=1,
    )
    generic = src.issue_to_handoff_entry(
        {"number": 184, "title": "Define metrics", "labels": [{"name": "bug"}], "body": ""},
        index=2,
    )
    assert "label/mutation-test" in specific.boundary_tokens
    assert not any(t.startswith("label/") for t in generic.boundary_tokens)


# --- clustering via propose_merges ---------------------------------------


def _entries(src, issues):
    return [src.issue_to_handoff_entry(issue, index=i + 1) for i, issue in enumerate(issues)]


def test_same_surface_issues_merge_others_stay_standalone(lib, src):
    issues = [
        # shared TITLE path -> cluster
        {"number": 244, "title": "scripts/host_hook_install_lib.py: hook not auto-installed",
         "labels": [], "body": ""},
        {"number": 245, "title": "scripts/host_hook_install_lib.py: duplicate hooks",
         "labels": [], "body": ""},
        # shared SPECIFIC label -> cluster
        {"number": 242, "title": "Mutation regression", "labels": [{"name": "mutation-test"}], "body": ""},
        {"number": 219, "title": "Mutation regression (older)", "labels": [{"name": "mutation-test"}], "body": ""},
        # generic label only -> never merges
        {"number": 184, "title": "Define product metrics", "labels": [{"name": "bug"}], "body": "no shared surface"},
    ]
    proposal = lib.propose_merges(_entries(src, issues))
    merged_label_sets = {
        frozenset(e.referenced_issues[0] for e in cand.entries) for cand in proposal.merged
    }
    assert frozenset({244, 245}) in merged_label_sets  # shared title path token
    assert frozenset({242, 219}) in merged_label_sets  # shared specific label
    # the generic-label issue never joins a merge
    assert all(184 not in s for s in merged_label_sets)


def test_body_only_path_overlap_does_not_over_merge(lib, src):
    """Two issues that share only an incidental BODY path stay standalone —
    the slice-2 dogfood over-merge guard."""
    issues = [
        {"number": 300, "title": "Closeout gates bind evidence", "labels": [],
         "body": "touches skills/public/achieve/scripts/goal_artifact_lib.py among others"},
        {"number": 301, "title": "Mutation survivors on main", "labels": [],
         "body": "mutants under skills/public/achieve/scripts/goal_artifact_lib.py listed"},
    ]
    proposal = lib.propose_merges(_entries(src, issues))
    assert proposal.merged == ()  # no spurious body-path cluster


# --- union ----------------------------------------------------------------


def test_union_reindexes_issues_after_handoff_max(lib, src):
    handoff_text = (
        "## Next Session\n\n"
        "1. **First.** do a thing.\n"
        "2. **Second.** do another.\n\n"
        "## Other\n"
    )
    handoff_entries = lib.parse_handoff_entries(handoff_text)
    assert [e.index for e in handoff_entries] == [1, 2]
    issue_entries = _entries(src, [
        {"number": 244, "title": "x", "labels": [], "body": ""},
        {"number": 245, "title": "y", "labels": [], "body": ""},
    ])
    unioned = src.union_entries(handoff_entries, issue_entries)
    assert [e.index for e in unioned] == [1, 2, 3, 4]
    # labels are collision-free (chunk-1..chunk-4)
    proposal = lib.propose_merges(unioned)
    labels = [c.label for c in proposal.standalone]
    assert len(set(labels)) == len(labels) == 4


def test_union_with_no_issues_is_identity(lib, src):
    handoff_entries = lib.parse_handoff_entries(
        "## Next Session\n\n1. **Only.** thing.\n\n## End\n"
    )
    assert src.union_entries(handoff_entries, []) == handoff_entries


# --- provider routing (injected runner; no live call) ---------------------


def test_list_open_issues_uses_gh_default_template(src):
    seen = {}

    def stub(argv):
        seen["argv"] = argv
        return [{"number": 1, "title": "t", "labels": [], "body": ""}]

    out = src.list_open_issues("corca-ai/charness", limit=25, runner=stub)
    assert out and out[0]["number"] == 1
    assert seen["argv"][0] == "gh"
    assert "corca-ai/charness" in seen["argv"]
    assert "25" in seen["argv"]


def test_non_gh_backend_requires_command_template(src):
    with pytest.raises(RuntimeError, match="commands.list_open"):
        src.list_open_issues(
            "x/y", backend={"id": "ceal", "binary": "ceal", "commands": None}, runner=lambda a: []
        )


def test_build_issue_entries_filters_and_converts(src, monkeypatch, tmp_path):
    # Force-enable + bypass adapter/target resolution by stubbing the helpers.
    monkeypatch.setattr(src, "load_issue_source_config", lambda root: {
        "enabled": True, "limit": 50, "repo": None,
        "labels_include": (), "labels_exclude": ("wontfix",), "exclude_numbers": (999,),
    })

    def fake_load_issue_module(root, name):
        class _Mod:
            @staticmethod
            def load_adapter(r):
                return {"data": {"issue_backend": {"id": "gh", "binary": "gh", "commands": None},
                                 "default_org": "corca-ai", "default_repo": "charness",
                                 "remote_name": "origin"}}

            @staticmethod
            def resolve_target(r, repo, data):
                return {"full_name": "corca-ai/charness"}

            @staticmethod
            def _backend_json(argv):
                return []
        return _Mod

    monkeypatch.setattr(src, "_load_issue_module", fake_load_issue_module)

    def runner(argv):
        return [
            {"number": 244, "title": "keep", "labels": [], "body": "scripts/x/y.py"},
            {"number": 999, "title": "excluded by number", "labels": [], "body": ""},
            {"number": 250, "title": "excluded by label", "labels": [{"name": "wontfix"}], "body": ""},
        ]

    entries = src.build_issue_entries(tmp_path, start_index=5, runner=runner)
    numbers = [e.referenced_issues[0] for e in entries]
    assert numbers == [244]
    assert entries[0].index == 5


def test_build_issue_entries_disabled_returns_empty(src, monkeypatch, tmp_path):
    monkeypatch.setattr(src, "load_issue_source_config", lambda root: {
        "enabled": False, "limit": 50, "repo": None,
        "labels_include": (), "labels_exclude": (), "exclude_numbers": (),
    })
    assert src.build_issue_entries(tmp_path, start_index=1, runner=lambda a: [{"number": 1}]) == []
