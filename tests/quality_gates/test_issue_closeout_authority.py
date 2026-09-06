"""Closeout authority refuses malformed declarations before evidence dispatch."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.quality_gates.issue_closeout_support import load_verify_module
from tests.quality_gates.seeding_support import load_module
from tests.quality_gates.support import ROOT
from tests.quality_gates.test_issue_closeout_commit_msg_hook import hook


@pytest.mark.parametrize(
    "body,numbers,scalar,fallback,reason",
    [
        ("Classification foreign/repo#42: bug", [42], None, "bug", "must use"),
        ("Classification #42: bug", [42, 42], None, "bug", "duplicate issue numbers"),
        ("Classification #42: unknown", [42], None, "bug", "unknown targeted"),
        ("Classification: bug\nClassification: feature", [42], None, "bug", "conflicting global"),
        ("", [42], None, "unknown", "unknown classification"),
    ],
)
def test_classification_authority_refuses_invalid_forms(body, numbers, scalar, fallback, reason):
    verifier = load_verify_module()
    with pytest.raises(RuntimeError, match=reason):
        verifier.resolve_classifications(
            body, numbers, scalar_classification=scalar, fallback_classification=fallback,
            strip_fences=verifier.strip_code_fences,
        )


def test_supplied_and_scalar_classification_authorities_cannot_mix():
    with pytest.raises(RuntimeError, match="scalar classification authority"):
        load_verify_module()._resolve_closeout_classifications("", [42], "bug", {42: "bug"})


@pytest.mark.parametrize("target", ["#42 #42", "#42 #44"])
def test_citation_scope_refuses_duplicate_and_extra_targets_before_dispatch(target):
    critique = load_module(
        "closeout_citation_scope_contract",
        ROOT / "skills/public/issue/scripts/issue_resolution_critique.py",
    )
    lines = critique._critique_lines(f"Critique {target}: evidence.md")
    assert critique._line_numbers(lines[0], [42, 43]) == []


def test_legacy_artifact_reader_resolves_the_same_classification_owner(tmp_path: Path):
    verifier = load_verify_module()
    path = "charness-artifacts/issue/closeout.md"
    artifacts = hook._issue_closeout_artifacts(
        tmp_path, verifier.iter_close_keyword_refs, verifier.strip_code_fences,
        list_paths=lambda _root: [path],
        read_file=lambda _root, _path: "Closes #42.\nClassification: feature\n",
    )
    assert artifacts[0]["classifications"] == {42: "feature"}
