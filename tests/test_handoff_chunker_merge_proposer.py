"""Slice 4 merge-proposer tests.

Covers the spec's three required sub-cases (shared-file, shared-skill,
shared-policy) plus the negative-merge invariant from slice 1's spec
critique (entries 2 and 7 of the slice-2 handoff snapshot share bare
common-noun directory roots but must NOT merge because the boundary
tokenization rejects common nouns and single-segment directory roots).
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
MERGE_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "propose_merges.py"
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


def _entry(lib, index, title, paths, skills_=(), issues=()):
    """Construct a HandoffEntry shorthand for fixture tests.

    boundary_tokens is derived via the lib helpers so the test exercises
    the production tokenization path, not a hand-crafted shortcut.
    """
    referenced_paths = tuple(paths)
    referenced_skills = tuple(skills_)
    boundary_tokens = lib._build_boundary_tokens(referenced_paths, referenced_skills)
    return lib.HandoffEntry(
        index=index,
        title=title,
        body=f"Body for {title}",
        referenced_paths=referenced_paths,
        referenced_issues=tuple(issues),
        referenced_skills=referenced_skills,
        boundary_tokens=boundary_tokens,
    )


# Shared-file ----------------------------------------------------------------


def test_shared_file_pair_merges_on_full_path(lib):
    entry_a = _entry(
        lib,
        1,
        "Tighten doc-link validator",
        paths=("scripts/check_doc_links.py",),
    )
    entry_b = _entry(
        lib,
        2,
        "Extend doc-link validator for portable placeholders",
        paths=("scripts/check_doc_links.py", "docs/conventions/implementation-discipline.md"),
    )
    proposal = lib.propose_merges([entry_a, entry_b])
    assert len(proposal.standalone) == 2
    assert len(proposal.merged) == 1
    merged = proposal.merged[0]
    assert merged.label == "chunk-1-2"
    assert tuple(entry.index for entry in merged.entries) == (1, 2)
    reason = proposal.shared_boundary_reason[merged.label]
    assert "scripts/check_doc_links.py" in reason


def test_cli_preserves_issue_source_diagnostic(lib):
    entry = _entry(
        lib,
        1,
        "Live issue fallback",
        paths=("skills/public/handoff/scripts/parse_handoff_entries.py",),
    )
    payload = {
        "entries": [entry.to_dict()],
        "issue_source_diagnostic": {
            "stage": "list_open_issues",
            "provider_attempted": True,
            "type": "RuntimeError",
            "message": "provider listing failed",
        },
    }

    result = subprocess.run(
        ["python3", str(MERGE_SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["issue_source_diagnostic"] == payload["issue_source_diagnostic"]


# Shared-skill ---------------------------------------------------------------


def test_shared_skill_pair_merges_on_skill_id(lib):
    entry_a = _entry(
        lib,
        3,
        "Refresh handoff state-selection reference",
        paths=("skills/public/handoff/references/state-selection.md",),
        skills_=("skills/public/handoff/",),
    )
    entry_b = _entry(
        lib,
        4,
        "Add handoff continuation-sequence link",
        paths=("skills/public/handoff/references/continuation-sequence.md",),
        skills_=("skills/public/handoff/",),
    )
    proposal = lib.propose_merges([entry_a, entry_b])
    assert len(proposal.merged) == 1
    merged = proposal.merged[0]
    assert tuple(entry.index for entry in merged.entries) == (3, 4)
    reason = proposal.shared_boundary_reason[merged.label]
    assert "skills/public/handoff/" in reason


# Shared-policy --------------------------------------------------------------


def test_shared_policy_pair_merges_on_convention_doc(lib):
    policy = "docs/conventions/implementation-discipline.md"
    entry_a = _entry(
        lib,
        5,
        "Document validator order",
        paths=(policy,),
    )
    entry_b = _entry(
        lib,
        6,
        "Document sync-before-verify rule",
        paths=(policy,),
    )
    proposal = lib.propose_merges([entry_a, entry_b])
    assert len(proposal.merged) == 1
    merged = proposal.merged[0]
    assert tuple(entry.index for entry in merged.entries) == (5, 6)
    assert policy in proposal.shared_boundary_reason[merged.label]


# Negative-merge invariant ---------------------------------------------------


def test_real_handoff_snapshot_entries_2_and_7_do_not_merge(lib):
    """Spec slice-4 fixture demand: in the real 2026-05-28 handoff
    snapshot, entries 2 and 7 both mention bare common-noun directory
    tokens (scripts, tests) but neither has a non-trivial overlapping
    path, so they must NOT merge."""
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    entries = lib.parse_handoff_entries(text)
    proposal = lib.propose_merges(entries)
    by_indices = {
        tuple(entry.index for entry in candidate.entries): candidate
        for candidate in proposal.merged
    }
    # Any merge candidate containing index 2 must NOT also contain index 7.
    for indices in by_indices:
        if 2 in indices:
            assert 7 not in indices, by_indices[indices].label


def test_real_handoff_snapshot_yields_no_spurious_merges(lib):
    """The real handoff snapshot has 7 entries with diverse boundary
    tokens; none share a non-trivial overlap, so the merged list must
    be empty. Any future merge that appears here surfaces a tokenization
    drift."""
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    entries = lib.parse_handoff_entries(text)
    proposal = lib.propose_merges(entries)
    assert proposal.merged == ()
    assert proposal.shared_boundary_reason == {}
    # Standalone always carries every entry.
    assert len(proposal.standalone) == len(entries)


def test_three_way_merge_chains_components(lib):
    """A → B (share file X), B → C (share file Y). All three must merge
    into one component (connected components by overlap)."""
    entry_a = _entry(lib, 1, "A", paths=("path/to/x.py",))
    entry_b = _entry(lib, 2, "B", paths=("path/to/x.py", "path/to/y.py"))
    entry_c = _entry(lib, 3, "C", paths=("path/to/y.py",))
    proposal = lib.propose_merges([entry_a, entry_b, entry_c])
    assert len(proposal.merged) == 1
    merged = proposal.merged[0]
    assert tuple(entry.index for entry in merged.entries) == (1, 2, 3)


def test_entries_without_boundary_tokens_never_merge(lib):
    """An entry with empty boundary_tokens cannot satisfy the
    overlap-required rule even with itself."""
    entry_a = _entry(lib, 1, "Empty A", paths=())
    entry_b = _entry(lib, 2, "Empty B", paths=())
    proposal = lib.propose_merges([entry_a, entry_b])
    assert proposal.merged == ()
    assert len(proposal.standalone) == 2


def test_candidate_labels_are_stable_and_index_sorted(lib):
    """The candidate label is the deterministic join key the agent uses
    in the ranker response, so it must be stable under input reorder."""
    entry_a = _entry(lib, 5, "A", paths=("path/to/x.py",))
    entry_b = _entry(lib, 2, "B", paths=("path/to/x.py",))
    # Provide entries in reverse order; label must still be chunk-2-5.
    proposal = lib.propose_merges([entry_a, entry_b])
    assert proposal.merged[0].label == "chunk-2-5"


# Standalone always present --------------------------------------------------


def test_standalone_carries_every_entry_even_when_merged(lib):
    """Per spec: standalone is always one ChunkCandidate per entry; the
    merged list is additive, not a replacement. The user picks which to
    take."""
    entry_a = _entry(lib, 1, "A", paths=("path/to/x.py",))
    entry_b = _entry(lib, 2, "B", paths=("path/to/x.py",))
    proposal = lib.propose_merges([entry_a, entry_b])
    assert len(proposal.standalone) == 2
    assert len(proposal.merged) == 1


# CLI round-trip -------------------------------------------------------------


def test_cli_emits_proposal_from_parser_payload_stdin(lib, tmp_path):
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    entries = lib.parse_handoff_entries(text)
    parser_payload = {
        "ok": True,
        "handoff_path": str(FIXTURE_PATH),
        "entry_count": len(entries),
        "entries": [entry.to_dict() for entry in entries],
    }
    result = subprocess.run(
        ["python3", str(MERGE_SCRIPT), "--entries", "-"],
        input=json.dumps(parser_payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    proposal_payload = json.loads(result.stdout)
    assert "standalone" in proposal_payload
    assert "merged" in proposal_payload
    assert "shared_boundary_reason" in proposal_payload
    assert len(proposal_payload["standalone"]) == len(entries)
    assert proposal_payload["merged"] == []
