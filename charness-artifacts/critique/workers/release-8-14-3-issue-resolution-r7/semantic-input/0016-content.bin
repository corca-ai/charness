"""Scope-evidence precision (#879).

Dotted identifiers in inline code and slash tokens whose first segment is
not a repository top-level name are not repository paths, and the
"scope mismatch" substring must not make every dotted token count. A new
file under a real top-level directory — or a file-shaped slash token —
still counts.
"""

from __future__ import annotations

from pathlib import Path

from scripts.task_run import task_run, task_run_scope_evidence

from .test_task_run_fixtures import _codex, _repo


def _root_with(tmp_path: Path, *names: str) -> Path:
    root = tmp_path / "lane-repo"
    root.mkdir()
    for name in names:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
    (root / "gateway").mkdir(exist_ok=True)
    (root / "scripts").mkdir(exist_ok=True)
    return root


def test_dotted_identifiers_and_foreign_slash_tokens_suggest_no_scope(
    tmp_path: Path,
) -> None:
    root = _root_with(tmp_path)

    suggested = task_run_scope_evidence.suggest_scopes(
        "Call `issue.create` on origin/main for task/abc; "
        "see `ceal.gateway_leased_agent_notion_search_arguments.v1`, "
        "corca-org/ceal and fs/promises.",
        repo_root=root,
    )

    assert suggested == []


def test_new_file_under_real_top_level_directory_still_suggests(
    tmp_path: Path,
) -> None:
    root = _root_with(tmp_path)

    suggested = task_run_scope_evidence.suggest_scopes(
        "add gateway/src/new-file.ts and check scripts/x.ts:12",
        repo_root=root,
    )

    assert suggested == ["gateway/src/new-file.ts", "scripts/x.ts"]


def test_file_shaped_slash_token_counts_without_a_repo_foothold(
    tmp_path: Path,
) -> None:
    """#880 recall survives: a file-shaped token stays advisory evidence."""
    root = _root_with(tmp_path)

    assert task_run_scope_evidence.suggest_scopes(
        "fix the helper in zebra/qux.ts", repo_root=root
    ) == ["zebra/qux.ts"]


def test_scope_mismatch_phrase_no_longer_counts_every_dotted_token(
    tmp_path: Path,
) -> None:
    root = _root_with(tmp_path)

    assert (
        task_run_scope_evidence.suggest_scopes(
            "scope mismatch - see foo.bar and baz.qux", repo_root=root
        )
        == []
    )


def test_existing_path_survives_an_unreadable_root_listing(
    tmp_path: Path, monkeypatch
) -> None:
    root = _root_with(tmp_path, "pkg/Makefile")
    monkeypatch.setattr(
        task_run_scope_evidence, "_repo_top_level_names", lambda _root: set()
    )

    assert task_run_scope_evidence.suggest_scopes(
        "update pkg/Makefile", repo_root=root
    ) == ["pkg/Makefile"]


def test_preflight_reads_first_segments_from_the_lane_repo(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    executable = _codex(tmp_path, "exit 0")

    payload = task_run.run_task(
        repo,
        target_path=tmp_path / "lane",
        branch="lane/evidence-root",
        base="HEAD",
        scopes=["module.py"],
        prompt="scaffold pkg/notes for the feature; compare against origin/main",
        codex=str(executable),
        effort="medium",
        dry_run=True,
    )

    assert payload["status"] == "pass", payload
    assert payload["scope_preflight"]["evidence_paths"] == ["pkg/notes"]
