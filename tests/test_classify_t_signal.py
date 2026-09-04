from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.seed_cache import get_or_build

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "gates_support" / "classify_t_signal.py"
HEAD = "a" * 40


def _load_module():
    spec = importlib.util.spec_from_file_location("classify_t_signal_under_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=repo, check=True, capture_output=True, text=True, env=env)


def _git_env() -> dict:
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
    )
    return env


def _commit(repo: Path, message: str, env: dict) -> str:
    _run(repo, "git", "add", "-A", env=env)
    _run(repo, "git", "commit", "-q", "-m", message, env=env)
    return (repo / ".git" / "refs" / "heads" / "main").read_text(encoding="ascii").strip()


def _write(repo: Path, rel: str, content: str = "x\n") -> None:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _build_baseline_seed(staging: Path) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo

    install_committed_repo(
        staging / "repo",
        {"README.md": "# baseline\n"},
        message="initial",
    )


def _setup_with_baseline(repo: Path) -> dict:
    seed = get_or_build("classify-t-signal-baseline-seed", _build_baseline_seed)
    shutil.copytree(seed / "repo", repo)
    return _git_env()


@pytest.fixture()
def module():
    return _load_module()


@pytest.fixture()
def classify(module):
    return module.classify_t_signal


def _observe(
    module,
    entries: list[tuple[str, str]],
    message: str = "msg",
    *,
    head: str = HEAD,
):
    return module.classify_from_observation(
        entries,
        message,
        head,
    )


def test_retro_lesson_added_wins_high(module) -> None:
    result = _observe(
        module,
        [("A", "charness-artifacts/retro/2026-05-22-demo-session.md")],
    )
    assert result["t_status"] == "memory_lesson_added"
    assert result["rule_id"] == "retro-lesson-path-added"
    assert result["confidence"] == "high"
    assert result["matched_paths"] == ["charness-artifacts/retro/2026-05-22-demo-session.md"]
    assert result["commit_refs"] == [HEAD]
    assert result["diff_kind"] == "added"
    assert result["skipped_reason"] is None


def test_debug_rca_added(module) -> None:
    result = _observe(module, [("A", "charness-artifacts/debug/2026-05-22-issue-foo.md")])
    assert result["rule_id"] == "debug-rca-path-added"
    assert result["t_status"] == "debug_rca_added"
    assert result["confidence"] == "high"
    assert result["diff_kind"] == "added"


def test_gate_script_added_beats_modification(module) -> None:
    result = _observe(
        module,
        [("M", "scripts/validate_existing.py"), ("A", "scripts/check_new.py")],
    )
    assert result["rule_id"] == "gate-script-added"
    assert result["t_status"] == "gate_added"
    assert result["confidence"] == "high"
    assert "scripts/check_new.py" in result["matched_paths"]


def test_nested_gate_script_is_classified(module) -> None:
    result = _observe(module, [("A", "scripts/package/check_new.py")])

    assert result["rule_id"] == "gate-script-added"


def test_gate_script_modified_low_confidence(module) -> None:
    result = _observe(module, [("M", "scripts/validate_existing.py")])
    assert result["rule_id"] == "gate-script-modified"
    assert result["t_status"] == "gate_modified"
    assert result["confidence"] == "low"
    assert result["diff_kind"] == "modified"


def test_quality_runner_modified(module) -> None:
    result = _observe(module, [("M", "scripts/run-quality.sh")])
    assert result["rule_id"] == "quality-runner-modified"
    assert result["t_status"] == "quality_runner_modified"
    assert result["confidence"] == "medium"


def test_quality_gate_list_modified(module) -> None:
    result = _observe(module, [("M", ".agents/quality-gates.yaml")])
    assert result["rule_id"] == "quality-runner-modified"
    assert result["t_status"] == "quality_runner_modified"
    assert result["confidence"] == "medium"


def test_convention_doc_modified(module) -> None:
    result = _observe(module, [("M", "docs/operating-contract.md")])
    assert result["rule_id"] == "convention-doc-modified"
    assert result["t_status"] == "convention_modified"
    assert result["confidence"] == "medium"


def test_skill_or_reference_modified(module) -> None:
    result = _observe(module, [("M", "skills/public/quality/SKILL.md")])
    assert result["rule_id"] == "skill-or-reference-modified"
    assert result["t_status"] == "skill_or_reference_modified"
    assert result["confidence"] == "low"


def test_issue_closed_via_commit_message(module) -> None:
    result = _observe(
        module,
        [("A", "src/feature.py")],
        "Implement feature\n\nCloses #190",
    )
    assert result["rule_id"] == "issue-closed"
    assert result["t_status"] == "issue_closed"
    assert result["confidence"] == "high"


def test_strongest_rule_wins_high_over_low(module) -> None:
    result = _observe(
        module,
        [
            ("M", "skills/public/quality/SKILL.md"),
            ("A", "charness-artifacts/retro/2026-05-22-other-session.md"),
        ],
    )
    assert result["rule_id"] == "retro-lesson-path-added"
    assert result["confidence"] == "high"


def test_issue_closed_wins_alphabetical_tiebreak_over_retro_lesson(module) -> None:
    result = _observe(
        module,
        [("A", "charness-artifacts/retro/2026-05-22-collision-session.md")],
        "Land retro lesson\n\nCloses #999",
    )
    assert result["rule_id"] == "issue-closed"
    assert result["t_status"] == "issue_closed"
    assert result["confidence"] == "high"


def test_tie_broken_alphabetically_by_rule_id(module) -> None:
    result = _observe(
        module,
        [("M", "scripts/run-quality.sh"), ("M", "docs/operating-contract.md")],
    )
    assert result["rule_id"] == "convention-doc-modified"


def test_no_rule_match_returns_none(module) -> None:
    result = _observe(module, [("A", "src/unrelated.py")], "unrelated change")
    assert result["t_status"] == "none"
    assert result["skipped_reason"] is None
    assert result["rule_id"] is None


def test_no_parent_returns_skipped(tmp_path: Path, classify) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo

    repo = install_committed_repo(
        tmp_path / "repo",
        {"README.md": "# only commit\n"},
        message="initial only commit",
    )

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


def test_normal_classification_uses_one_metadata_and_one_diff_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    head = "a" * 40
    first_parent = "b" * 40
    second_parent = "c" * 40
    metadata_args = ("log", "-1", "--format=%H%x00%P%x00%B%x00", "HEAD")
    calls: list[tuple[str, ...]] = []

    def run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args == metadata_args:
            stdout = (
                f"{head}\0{first_parent} {second_parent}\0Implement feature\n\nCloses #123\n\0\n"
            )
            return subprocess.CompletedProcess(["git", *args], 0, stdout, "")
        if args == ("diff", "--name-status", f"{first_parent}..{head}"):
            return subprocess.CompletedProcess(["git", *args], 0, "M\tsrc/feature.py\n", "")
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(module, "_run_git", run_git)

    result = module.classify_t_signal(repo)

    assert result["rule_id"] == "issue-closed"
    assert result["commit_refs"] == [head]
    assert calls == [metadata_args, ("diff", "--name-status", f"{first_parent}..{head}")]


def test_not_a_git_repo_returns_diff_unavailable(tmp_path: Path, classify) -> None:
    result = classify(tmp_path)

    assert result["t_status"] == "none"
    assert result["skipped_reason"] == "diff_unavailable"
