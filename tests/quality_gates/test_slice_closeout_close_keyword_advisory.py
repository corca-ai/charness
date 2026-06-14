"""Close-keyword-leakage advisory (#363).

A GitHub close keyword (close/fix/resolve + #N) in a commit whose changed paths
are not a plausible fix for #N (an artifact-only goal-shaping commit) auto-closes
#N before its fix lands when pushed to the default branch. This advisory flags
that leak. It is non-blocking (a commit still succeeds), per Floor-Addition
Restraint (one recorded recurrence: #362 auto-closed by a draft-goal commit).
"""
from __future__ import annotations

import subprocess

import pytest

from scripts import slice_closeout_advisories as adv
from scripts.slice_closeout_advisories import (
    advise_close_keyword_leakage,
    is_artifact_only_commit,
    parse_close_keyword_refs,
)

# --- pure: close-keyword parsing (the live GitHub auto-close carrier) ---


def test_parses_basic_close_keywords() -> None:
    assert parse_close_keyword_refs("Closes #365") == [365]
    assert parse_close_keyword_refs("fix #7") == [7]
    assert parse_close_keyword_refs("Resolved: #42") == [42]
    assert parse_close_keyword_refs("fixes:#9") == [9]


def test_parses_multiple_and_dedupes() -> None:
    assert parse_close_keyword_refs("fixes #1 and resolves #2") == [1, 2]
    assert parse_close_keyword_refs("Closes #3. Closes #3.") == [3]


def test_parses_url_and_owner_repo_forms() -> None:
    assert parse_close_keyword_refs("Resolves https://github.com/corca-ai/charness/issues/42") == [42]
    assert parse_close_keyword_refs("closes corca-ai/charness#9") == [9]


def test_bare_reference_without_close_verb_is_not_matched() -> None:
    # A bare #N mention (the SAFE form for a shaping/handoff commit) must not fire.
    assert parse_close_keyword_refs("see #5 for context; tracks #362") == []
    assert parse_close_keyword_refs("Pursue-ready draft goal for #362") == []


def test_close_verb_inside_a_word_is_not_matched() -> None:
    # `prefix #1` / `affixes #1` contain fix/fixes but are not close keywords.
    assert parse_close_keyword_refs("prefix #1") == []
    assert parse_close_keyword_refs("affixes #2") == []
    # no separator between keyword and ref -> not a GitHub close keyword.
    assert parse_close_keyword_refs("fix#1") == []


# --- pure: artifact-only signal (shared with the over-slicing advisory) ---


def test_artifact_only_commit_signal() -> None:
    assert is_artifact_only_commit(["charness-artifacts/goals/g.md"]) is True
    assert is_artifact_only_commit(["charness-artifacts/goals/g.md", "charness-artifacts/retro/r.md"]) is True
    # any code/test/skill/doc path makes it a plausible fix.
    assert is_artifact_only_commit(["charness-artifacts/goals/g.md", "scripts/x.py"]) is False
    assert is_artifact_only_commit(["scripts/x.py"]) is False
    assert is_artifact_only_commit([]) is False


# --- advisory orchestration (monkeypatched git) ---


def test_advise_fires_on_artifact_only_close_keyword_commit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    monkeypatch.setattr(
        adv,
        "_unpushed_commits",
        lambda repo_root, base: [
            ("deadbeef123", "Pursue-ready draft goal to resolve #999", ["charness-artifacts/goals/g.md"]),
        ],
    )
    advise_close_keyword_leakage(tmp_path)
    err = capsys.readouterr().err
    assert "#363" in err
    assert "#999" in err
    assert "deadbeef1" in err


def test_advise_silent_on_real_fix_commit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    # close keyword + an actual code change -> plausible fix -> silent.
    monkeypatch.setattr(
        adv,
        "_unpushed_commits",
        lambda repo_root, base: [
            ("cafe000", "Scope the guard\n\nCloses #365", ["scripts/agent_browser_runtime_guard.py", "charness-artifacts/goals/g.md"]),
        ],
    )
    advise_close_keyword_leakage(tmp_path)
    assert capsys.readouterr().err == ""


def test_advise_silent_on_bare_reference_artifact_commit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    # artifact-only, but the issue is cited as a bare #N (no close verb) -> safe.
    monkeypatch.setattr(
        adv,
        "_unpushed_commits",
        lambda repo_root, base: [
            ("face111", "Shape goal for #999 (draft)", ["charness-artifacts/goals/g.md"]),
        ],
    )
    advise_close_keyword_leakage(tmp_path)
    assert capsys.readouterr().err == ""


def test_advise_is_non_blocking(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    # The advisory returns None and never raises, even on a firing leak: a commit
    # still succeeds. Guards against a future hand converting it to a precondition.
    monkeypatch.setattr(
        adv,
        "_unpushed_commits",
        lambda repo_root, base: [("dead000", "resolve #1", ["charness-artifacts/goals/g.md"])],
    )
    assert advise_close_keyword_leakage(tmp_path) is None


def test_advise_not_wired_into_blocking_commit_gate() -> None:
    # Floor-Addition Restraint: this stays an advisory, never a blocking gate.
    from scripts import staged_commit_gate_plan

    source = staged_commit_gate_plan.__file__
    text = open(source, encoding="utf-8").read()
    assert "advise_close_keyword_leakage" not in text
    assert "close_keyword" not in text


# --- real git repo: pins the unmocked git plumbing end-to-end ---


def _git(repo, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _seed_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t.t")
    _git(repo, "config", "user.name", "t")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "base")
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()
    return repo, base_sha


def test_real_repo_fires_on_artifact_only_close_keyword(
    capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    repo, base_sha = _seed_repo(tmp_path)
    art = repo / "charness-artifacts" / "goals"
    art.mkdir(parents=True)
    (art / "g.md").write_text("draft\n", encoding="utf-8")
    _git(repo, "add", "charness-artifacts/goals/g.md")
    _git(repo, "commit", "-q", "-m", "Pursue-ready draft goal to resolve #999")

    advise_close_keyword_leakage(repo, base=base_sha)
    err = capsys.readouterr().err
    assert "#363" in err and "#999" in err


def test_real_repo_silent_on_real_fix_close_keyword(
    capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    repo, base_sha = _seed_repo(tmp_path)
    (repo / "fix.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", "fix.py")
    _git(repo, "commit", "-q", "-m", "Real fix\n\nCloses #999")

    advise_close_keyword_leakage(repo, base=base_sha)
    assert capsys.readouterr().err == ""


def test_real_repo_silent_when_base_unresolvable(
    capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    repo, _ = _seed_repo(tmp_path)
    advise_close_keyword_leakage(repo, base="origin/does-not-exist")
    assert capsys.readouterr().err == ""
