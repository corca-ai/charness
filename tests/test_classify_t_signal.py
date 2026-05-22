from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "classify_t_signal.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("classify_t_signal_under_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=repo, check=True, capture_output=True, text=True, env=env)
    return result


def _init_repo(repo: Path) -> dict:
    repo.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
    )
    _run(repo, "git", "init", "-q", env=env)
    _run(repo, "git", "checkout", "-q", "-b", "main", env=env)
    return env


def _commit(repo: Path, message: str, env: dict) -> str:
    _run(repo, "git", "add", "-A", env=env)
    _run(repo, "git", "commit", "-q", "-m", message, env=env)
    head = _run(repo, "git", "rev-parse", "HEAD", env=env)
    return head.stdout.strip()


def _write(repo: Path, rel: str, content: str = "x\n") -> None:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _setup_with_baseline(repo: Path) -> dict:
    env = _init_repo(repo)
    _write(repo, "README.md", "# baseline\n")
    _commit(repo, "initial", env)
    return env


@pytest.fixture()
def classify():
    return _load_module().classify_t_signal


def test_retro_lesson_added_wins_high(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "charness-artifacts/retro/2026-05-22-demo-session.md", "lesson\n")
    head = _commit(repo, "add retro lesson", env)

    result = classify(repo)

    assert result["t_status"] == "memory_lesson_added"
    assert result["rule_id"] == "retro-lesson-path-added"
    assert result["confidence"] == "high"
    assert result["matched_paths"] == ["charness-artifacts/retro/2026-05-22-demo-session.md"]
    assert result["commit_refs"] == [head]
    assert result["diff_kind"] == "added"
    assert result["skipped_reason"] is None


def test_debug_rca_added(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "charness-artifacts/debug/2026-05-22-issue-foo.md", "rca\n")
    _commit(repo, "add debug rca", env)

    result = classify(repo)

    assert result["rule_id"] == "debug-rca-path-added"
    assert result["t_status"] == "debug_rca_added"
    assert result["confidence"] == "high"
    assert result["diff_kind"] == "added"


def test_gate_script_added_beats_modification(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "scripts/validate_existing.py", "#initial\n")
    _commit(repo, "seed existing gate", env)
    _write(repo, "scripts/validate_existing.py", "#changed\n")
    _write(repo, "scripts/check_new.py", "#new\n")
    _commit(repo, "modify and add gates", env)

    result = classify(repo)

    assert result["rule_id"] == "gate-script-added"
    assert result["t_status"] == "gate_added"
    assert result["confidence"] == "high"
    assert "scripts/check_new.py" in result["matched_paths"]


def test_gate_script_modified_low_confidence(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "scripts/validate_existing.py", "#initial\n")
    _commit(repo, "seed gate", env)
    _write(repo, "scripts/validate_existing.py", "#changed\n")
    _commit(repo, "modify gate", env)

    result = classify(repo)

    assert result["rule_id"] == "gate-script-modified"
    assert result["t_status"] == "gate_modified"
    assert result["confidence"] == "low"
    assert result["diff_kind"] == "modified"


def test_quality_runner_modified(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "scripts/run-quality.sh", "#!/bin/sh\necho one\n")
    _commit(repo, "seed runner", env)
    _write(repo, "scripts/run-quality.sh", "#!/bin/sh\necho two\n")
    _commit(repo, "tweak runner", env)

    result = classify(repo)

    assert result["rule_id"] == "quality-runner-modified"
    assert result["t_status"] == "quality_runner_modified"
    assert result["confidence"] == "medium"


def test_convention_doc_modified(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "docs/conventions/operating-contract.md", "# a\n")
    _commit(repo, "seed convention", env)
    _write(repo, "docs/conventions/operating-contract.md", "# b\n")
    _commit(repo, "tweak convention", env)

    result = classify(repo)

    assert result["rule_id"] == "convention-doc-modified"
    assert result["t_status"] == "convention_modified"
    assert result["confidence"] == "medium"


def test_skill_or_reference_modified(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "skills/public/find-skills/SKILL.md", "# a\n")
    _commit(repo, "seed skill", env)
    _write(repo, "skills/public/find-skills/SKILL.md", "# b\n")
    _commit(repo, "tweak skill", env)

    result = classify(repo)

    assert result["rule_id"] == "skill-or-reference-modified"
    assert result["t_status"] == "skill_or_reference_modified"
    assert result["confidence"] == "low"


def test_deferred_decision_added_when_new_d_heading(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "docs/deferred-decisions.md", "# Deferred Decisions\n\n## D1 — first\n")
    _commit(repo, "seed deferred", env)
    _write(
        repo,
        "docs/deferred-decisions.md",
        "# Deferred Decisions\n\n## D1 — first\n\n## D2 — second\n",
    )
    _commit(repo, "add deferred decision", env)

    result = classify(repo)

    assert result["rule_id"] == "deferred-decision-added"
    assert result["t_status"] == "deferred_decision_added"
    assert result["confidence"] == "medium"


def test_deferred_decision_modification_without_new_heading_does_not_match(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "docs/deferred-decisions.md", "# Deferred Decisions\n\n## D1 — first\n")
    _commit(repo, "seed deferred", env)
    _write(repo, "docs/deferred-decisions.md", "# Deferred Decisions\n\n## D1 — first edited\n")
    _commit(repo, "wordsmith deferred", env)

    result = classify(repo)

    assert result["rule_id"] != "deferred-decision-added"


def test_issue_closed_via_commit_message(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "src/feature.py", "x = 1\n")
    _commit(repo, "Implement feature\n\nCloses #190", env)

    result = classify(repo)

    assert result["rule_id"] == "issue-closed"
    assert result["t_status"] == "issue_closed"
    assert result["confidence"] == "high"


def test_strongest_rule_wins_high_over_low(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "skills/public/find-skills/SKILL.md", "# a\n")
    _commit(repo, "seed", env)
    _write(repo, "skills/public/find-skills/SKILL.md", "# b\n")
    _write(repo, "charness-artifacts/retro/2026-05-22-other-session.md", "lesson\n")
    _commit(repo, "tweak skill and add retro", env)

    result = classify(repo)

    assert result["rule_id"] == "retro-lesson-path-added"
    assert result["confidence"] == "high"


def test_issue_closed_wins_alphabetical_tiebreak_over_retro_lesson(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "charness-artifacts/retro/2026-05-22-collision-session.md", "lesson\n")
    _commit(repo, "Land retro lesson\n\nCloses #999", env)

    result = classify(repo)

    assert result["rule_id"] == "issue-closed"
    assert result["t_status"] == "issue_closed"
    assert result["confidence"] == "high"


def test_tie_broken_alphabetically_by_rule_id(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "scripts/run-quality.sh", "#!/bin/sh\necho one\n")
    _write(repo, "docs/conventions/operating-contract.md", "# a\n")
    _commit(repo, "seed", env)
    _write(repo, "scripts/run-quality.sh", "#!/bin/sh\necho two\n")
    _write(repo, "docs/conventions/operating-contract.md", "# b\n")
    _commit(repo, "tweak both medium-confidence surfaces", env)

    result = classify(repo)

    assert result["rule_id"] == "convention-doc-modified"


def test_no_parent_returns_skipped(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _init_repo(repo)
    _write(repo, "README.md", "# only commit\n")
    _commit(repo, "initial only commit", env)

    result = classify(repo)

    assert result["t_status"] == "none"
    assert result["skipped_reason"] == "no_parent"
    assert result["rule_id"] is None
    assert result["matched_paths"] is None


def test_shallow_clone_returns_skipped(tmp_path: Path, classify) -> None:
    upstream = tmp_path / "upstream"
    env = _setup_with_baseline(upstream)
    _write(upstream, "README.md", "# v2\n")
    _commit(upstream, "v2", env)
    _write(upstream, "README.md", "# v3\n")
    _commit(upstream, "v3", env)

    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "--depth", "1", "file://" + str(upstream.resolve()), str(shallow)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    result = classify(shallow)

    assert result["t_status"] == "none"
    assert result["skipped_reason"] == "shallow_clone"


def test_no_rule_match_returns_none(tmp_path: Path, classify) -> None:
    repo = tmp_path / "repo"
    env = _setup_with_baseline(repo)
    _write(repo, "src/unrelated.py", "y = 2\n")
    _commit(repo, "unrelated change", env)

    result = classify(repo)

    assert result["t_status"] == "none"
    assert result["skipped_reason"] is None
    assert result["rule_id"] is None


def test_not_a_git_repo_returns_diff_unavailable(tmp_path: Path, classify) -> None:
    result = classify(tmp_path)

    assert result["t_status"] == "none"
    assert result["skipped_reason"] == "diff_unavailable"
