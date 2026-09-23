"""Scope-closure disposition for task-run lanes (#831).

A narrow scope allowlist often omits a necessary companion file (generated
artifact, manifest, fixture, test), and the lane then burns a full model run
before failing at candidate validation. These tests pin the cheap,
warning-only dispositions: frozen directory matches (no automatic widening),
repeated `./` normalization, preflight closure warnings, the typed
scope-extension request parsed from the lane's own blocker, and
same-candidate re-validation with an operator-approved scope addition.
"""

from __future__ import annotations

from pathlib import Path

from scripts.task_run import task_run_scope

from .test_task_run_fixtures import _codex, _commit, _git, _repo, _run


def test_normalize_scope_strips_repeated_dot_prefix() -> None:
    assert task_run_scope._normalize_scope("././pkg/module.py") == "pkg/module.py"


def test_refresh_keeps_directory_matches_frozen_against_lane_created_dirs(
    tmp_path: Path,
) -> None:
    """Post-freeze directories never widen a glob on their own (#831).

    A lane-created directory whose name fits the glob (the `escape.py/`
    shape) stays refused after refresh; admitting it is an explicit
    operator-approved rescope, never an automatic refresh.
    """
    repo = _repo(tmp_path)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "base.txt").write_text("base\n", encoding="utf-8")
    _commit(repo, "add package", "pkg/base.txt")
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

    specs = task_run_scope.resolve_scope_specs(repo, ["pkg*"], base_sha)
    assert specs[0]["directory_matches"] == ["pkg"]

    (repo / "pkg2").mkdir()
    (repo / "pkg2" / "child.txt").write_text("child\n", encoding="utf-8")

    refreshed = task_run_scope._refresh_scope_specs(repo, specs)

    assert refreshed[0]["directory_matches"] == ["pkg"]
    assert not task_run_scope._scope_matches("pkg2/child.txt", refreshed[0])


def test_scope_closure_warnings_name_absent_exact_scopes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

    specs = task_run_scope.resolve_scope_specs(
        repo, ["module.py", "missing-companion.yaml"], base_sha
    )
    tree_paths, _tree_directories = task_run_scope._git_tree_paths(repo, base_sha)

    warnings = task_run_scope.scope_closure_warnings(specs, tree_paths)

    assert [warning["path"] for warning in warnings] == ["missing-companion.yaml"]
    assert warnings[0]["code"] == "unmatched-literal-scope"


def test_parse_scope_extension_request_reads_the_lane_blocker() -> None:
    request = task_run_scope.parse_scope_extension_request(
        "scope mismatch - real owner gateway/manifest.yaml is outside declared scope"
    )

    assert request is not None
    assert request["requested_paths"] == ["gateway/manifest.yaml"]

    assert task_run_scope.parse_scope_extension_request(None) is None
    assert task_run_scope.parse_scope_extension_request("lane stalled") is None
    assert (
        task_run_scope.parse_scope_extension_request(
            "scope mismatch - real owner <> is outside declared scope"
        )
        is None
    )


def test_dry_run_surfaces_scope_warnings(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, "exit 0")

    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["module.py", "missing-companion.yaml"],
        dry_run=True,
    )

    assert payload["status"] == "pass", payload
    assert [warning["path"] for warning in payload["scope_warnings"]] == [
        "missing-companion.yaml"
    ]


def test_rescope_revalidates_the_same_candidate_without_relaunch(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "stray.py").write_text("STRAY = 1\n", encoding="utf-8")
    specs = task_run_scope.resolve_scope_specs(repo, ["module.py"], base_sha)

    before = task_run_scope._scope_result(repo, base_sha, specs, True)
    assert before["verdict"] == task_run_scope.FAIL
    assert before["disallowed_paths"] == ["stray.py"]

    after = task_run_scope.rescope_result(
        repo, base_sha, specs, ["stray.py"], True
    )

    assert after["verdict"] == task_run_scope.PASS
    assert after["disallowed_paths"] == []
    assert after["changed_paths"] == ["stray.py"]
