"""The corpus plumbing both inventory measurements share.

Its exemption ladder decides which artifacts a measurement may count at all: the gate
returns 0 without running a floor on a pre-contract artifact, so counting one reports a
cost on an artifact the gate never judges. Each arm is driven here because the real
corpus exercises only one of them — every checked-in artifact is `not-claimed`, so the
other three would otherwise ship unmeasured.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB = import_repo_module(
    REPO_ROOT / "scripts" / "gates" / "inventory_measurement_lib.py",
    "scripts.gates.inventory_measurement_lib",
)

_PRE_CONTRACT = "Date: 2026-01-01\n"
_POST_CONTRACT = "Date: 2099-01-01\n"


def test_no_date_line_is_not_claimed(tmp_path):
    assert LIB.exemption_state(tmp_path, tmp_path / "a.md", "no date here\n") == "not-claimed"


def test_a_post_contract_date_is_not_claimed(tmp_path):
    assert LIB.exemption_state(tmp_path, tmp_path / "a.md", _POST_CONTRACT) == "not-claimed"


@pytest.mark.parametrize(
    ("commit_state", "expected"),
    [
        # git could not date the file at all -- not a repository, or no git binary.
        (("unavailable", None), "not-corroborated"),
        # git answered but produced no date; a check that did not run is not one that
        # passed, so this is NOT silently upgraded to corroborated.
        (("dated", None), "not-corroborated"),
        # git dates the bytes before the contract: the artifact's own claim is
        # corroborated by a channel it does not author.
        (("dated", date(2026, 1, 2)), "corroborated"),
        # the claim is pre-contract but git saw these bytes after it started.
        (("dated", date(2099, 1, 2)), "REFUSED-uncorroborated"),
    ],
)
def test_the_pre_contract_ladder_reads_git_not_the_artifacts_own_claim(
    tmp_path, monkeypatch, commit_state, expected
):
    monkeypatch.setattr(LIB.gate, "commit_state", lambda root, path: commit_state)

    assert LIB.exemption_state(tmp_path, tmp_path / "a.md", _PRE_CONTRACT) == expected


def test_an_unavailable_state_with_a_date_still_refuses_corroboration(tmp_path, monkeypatch):
    """`state == "unavailable"` wins even when a date came back, because the date then
    describes something other than this file's bytes."""
    monkeypatch.setattr(
        LIB.gate, "commit_state", lambda root, path: ("unavailable", date(2026, 1, 2))
    )

    assert LIB.exemption_state(tmp_path, tmp_path / "a.md", _PRE_CONTRACT) == "not-corroborated"


def test_refuse_empty_corpus_is_true_for_a_missing_directory(tmp_path, capsys):
    assert LIB.refuse_empty_corpus(tmp_path / "nope") is True
    assert "not a measurement" in capsys.readouterr().err


def test_refuse_empty_corpus_is_false_when_the_corpus_has_files(tmp_path):
    (tmp_path / "a.md").write_text("x\n", encoding="utf-8")

    assert LIB.refuse_empty_corpus(tmp_path) is False


def test_split_bodies_keeps_the_commands_section_out_of_the_body(tmp_path):
    text = (
        f"## {LIB.gate.COMMANDS_RUN_HEADER.lstrip('# ')}\n\n- ran a thing\n\n"
        "## Findings\n\n- found a thing\n"
    )
    commands, body = LIB.split_bodies(text)

    # The split is what stops an artifact satisfying a field floor by pasting the
    # command line that names the field.
    assert "ran a thing" in commands
    assert "ran a thing" not in body
    assert "found a thing" in body
