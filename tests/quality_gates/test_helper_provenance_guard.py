from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

guard = importlib.import_module("scripts.helper_provenance_lib")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _source_tree(tmp_path: Path, *, version: str, lib_body: str = "VALUE = 1\n") -> Path:
    root = tmp_path / "source"
    _write(root / "packaging" / "charness.json", json.dumps({"package_id": "charness", "version": version}))
    _write(root / "scripts" / "runtime_bootstrap.py", "# marker\n")
    _write(root / "scripts" / "lessons_lib.py", lib_body)
    _write(root / "skills" / "public" / "demo" / "scripts" / "helper.py", "# helper\n")
    _write(root / "skills" / "public" / "demo" / "scripts" / "resolve_adapter.py", "# adapter\n")
    return root


def _installed_tree(tmp_path: Path, *, version: str, lib_body: str = "VALUE = 1\n") -> Path:
    root = tmp_path / "installed"
    _write(root / ".claude-plugin" / "plugin.json", json.dumps({"name": "charness", "version": version}))
    _write(root / "scripts" / "runtime_bootstrap.py", "# marker\n")
    _write(root / "scripts" / "lessons_lib.py", lib_body)
    _write(root / "skills" / "demo" / "scripts" / "helper.py", "# helper\n")
    _write(root / "skills" / "demo" / "scripts" / "resolve_adapter.py", "# adapter\n")
    return root


def _helper(root: Path) -> Path:
    for candidate in (
        root / "skills" / "demo" / "scripts" / "helper.py",
        root / "skills" / "public" / "demo" / "scripts" / "helper.py",
    ):
        if candidate.is_file():
            return candidate
    raise AssertionError(f"no helper under {root}")


def test_version_mismatch_refuses_and_names_the_repo_local_copy(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    with pytest.raises(guard.ForeignHelperError) as excinfo:
        guard.require_repo_local_helper(_helper(installed), source, loaded_modules=[], exit_on_drift=False)
    message = str(excinfo.value)
    assert "skills/public/demo/scripts/helper.py" in message
    assert "2.11.0" in message and "2.11.1" in message
    assert guard.OVERRIDE_ENV in message


def test_identical_copies_at_the_same_version_may_write(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.1")
    verdict = guard.require_repo_local_helper(_helper(installed), source, loaded_modules=[], exit_on_drift=False)
    assert verdict["status"] == "in-sync"
    assert verdict["drifted"] == []


def test_sibling_library_drift_at_equal_versions_still_refuses(tmp_path: Path) -> None:
    """The real incident: same version string, a skill-local module already changed."""

    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.1")
    _write(installed / "skills" / "demo" / "scripts" / "resolve_adapter.py", "# adapter, older\n")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["status"] == "drifted"
    assert verdict["drifted"] == ["skills/public/demo/scripts/resolve_adapter.py"]
    assert verdict["version_mismatch"] is False


def test_loaded_repo_module_drift_is_detected(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1", lib_body="VALUE = 2\n")
    installed = _installed_tree(tmp_path, version="2.11.1")
    loaded = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location("fake_lessons_lib", installed / "scripts" / "lessons_lib.py")
    )
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[loaded])
    assert verdict["status"] == "drifted"
    assert "scripts/lessons_lib.py" in verdict["drifted"]


def test_consuming_repo_target_is_never_refused(tmp_path: Path) -> None:
    installed = _installed_tree(tmp_path, version="2.11.0")
    consumer = tmp_path / "consumer"
    _write(consumer / "README.md", "# app\n")
    verdict = guard.require_repo_local_helper(_helper(installed), consumer, loaded_modules=[], exit_on_drift=False)
    assert verdict["status"] == "consuming-repo"


def test_source_tree_without_a_matching_helper_is_treated_as_consuming(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    (source / "skills" / "public" / "demo" / "scripts" / "helper.py").unlink()
    installed = _installed_tree(tmp_path, version="2.11.0")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["status"] == "consuming-repo"


def test_repo_local_invocation_is_the_same_tree(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    verdict = guard.require_repo_local_helper(_helper(source), source, loaded_modules=[], exit_on_drift=False)
    assert verdict["status"] == "same-tree"


def test_override_env_warns_and_allows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    monkeypatch.setenv(guard.OVERRIDE_ENV, "1")
    verdict = guard.require_repo_local_helper(_helper(installed), source, loaded_modules=[], exit_on_drift=False)
    assert verdict["status"] == "override-allowed"
    assert guard.OVERRIDE_ENV in capsys.readouterr().err


def test_cli_default_exits_two_with_the_message_on_stderr(tmp_path: Path, capsys) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    with pytest.raises(SystemExit) as excinfo:
        guard.require_repo_local_helper(_helper(installed), source, loaded_modules=[])
    assert excinfo.value.code == 2
    assert "charness helper provenance refusal" in capsys.readouterr().err


def test_support_skill_counterpart_is_resolved(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    _write(source / "skills" / "support" / "hidden" / "scripts" / "helper.py", "# newer\n")
    installed = _installed_tree(tmp_path, version="2.11.1")
    installed_helper = _write(installed / "skills" / "hidden" / "scripts" / "helper.py", "# older\n")
    verdict = guard.inspect_helper_provenance(installed_helper, source, loaded_modules=[])
    assert verdict["status"] == "drifted"
    assert verdict["target_helper"] == "skills/support/hidden/scripts/helper.py"


def test_refusal_names_the_invoked_entry_point_not_the_library(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A guard called from a library must not tell the operator to run the library.

    `scripts/recent_lessons_lib.py --repo-root .` is not a runnable command, so the
    remediation has to name what was actually invoked.
    """
    source = _source_tree(tmp_path, version="2.11.1")
    _write(source / "scripts" / "build_index.py", "# newer\n")
    installed = _installed_tree(tmp_path, version="2.11.1")
    entry = _write(installed / "scripts" / "build_index.py", "# older\n")
    library = installed / "scripts" / "lessons_lib.py"
    monkeypatch.setattr("sys.argv", [str(entry), "--repo-root", str(source)])

    with pytest.raises(guard.ForeignHelperError) as excinfo:
        guard.require_repo_local_helper(library, source, loaded_modules=[], exit_on_drift=False)

    message = str(excinfo.value)
    assert "python3 scripts/build_index.py --repo-root ." in message
    assert "lessons_lib.py --repo-root" not in message


def test_entry_script_outside_the_running_tree_is_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pytest or wrapper `argv[0]` from elsewhere must not be reported as the helper."""
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    monkeypatch.setattr("sys.argv", ["/usr/bin/pytest"])
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["invoked"] == str(_helper(installed))


def test_unknown_own_root_does_not_block(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    orphan = _write(tmp_path / "orphan" / "helper.py", "# helper\n")
    verdict = guard.require_repo_local_helper(orphan, source, loaded_modules=[], exit_on_drift=False)
    assert verdict["status"] == "own-root-unknown"


def test_guard_is_reachable_from_both_bootstrap_surfaces() -> None:
    root = Path(__file__).resolve().parents[2]
    shim = (root / "skill_runtime_bootstrap.py").read_text(encoding="utf-8")
    assert "require_repo_local_helper" in shim
    skill_bootstrap = importlib.import_module("scripts.skill_runtime_bootstrap")
    runtime_bootstrap = importlib.import_module("scripts.runtime_bootstrap")
    assert callable(skill_bootstrap.require_repo_local_helper)
    assert callable(runtime_bootstrap.require_repo_local_helper)


# Entrypoint tree scan (#the 2.11.2 publish failures) -------------------------


def _entrypoint_condition(tmp_path: Path) -> tuple[Path, Path]:
    """The state a release entrypoint actually sees: versions agree, code lags.

    This is the exact shape of the two failed 2.11.2 publishes. The bump that
    would expose a version mismatch happens *after* the entrypoint, and the
    module that had drifted (`recent_lessons_lib`) is imported lazily, much
    later, when the retro closeout writes. So at the moment the entrypoint could
    still refuse cheaply, both signals the anchor scan relies on are absent.
    """
    source = _source_tree(tmp_path, version="2.11.2", lib_body="VALUE = 2  # new schema\n")
    installed = _installed_tree(tmp_path, version="2.11.2", lib_body="VALUE = 1\n")
    return source, installed


def test_anchor_scan_misses_a_lazily_imported_drifted_module(tmp_path: Path) -> None:
    """Documents the gap, so a future change cannot quietly reintroduce it."""
    source, installed = _entrypoint_condition(tmp_path)
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["status"] == "in-sync"
    assert verdict["drifted"] == []


def test_tree_scan_catches_the_drift_the_anchor_scan_misses(tmp_path: Path) -> None:
    source, installed = _entrypoint_condition(tmp_path)
    verdict = guard.inspect_helper_provenance(
        _helper(installed), source, loaded_modules=[], scan="tree"
    )
    assert verdict["status"] == "drifted"
    assert "scripts/lessons_lib.py" in verdict["drifted"]
    assert verdict["scan"] == "tree"
    assert verdict["compared_count"] > 0


def test_tree_scan_refuses_and_names_the_runnable_repo_local_command(tmp_path: Path) -> None:
    source, installed = _entrypoint_condition(tmp_path)
    with pytest.raises(guard.ForeignHelperError) as excinfo:
        guard.require_repo_local_helper(
            _helper(installed), source, loaded_modules=[], exit_on_drift=False, scan="tree"
        )
    message = str(excinfo.value)
    assert "scripts/lessons_lib.py" in message
    assert "skills/public/demo/scripts/helper.py" in message


def test_tree_scan_stays_silent_for_a_consuming_repo(tmp_path: Path) -> None:
    """The normal installed-plugin case must not be blocked by the wider scan."""
    consumer = tmp_path / "consumer"
    _write(consumer / "README.md", "# not a charness source tree\n")
    installed = _installed_tree(tmp_path, version="2.11.2")
    verdict = guard.require_repo_local_helper(
        _helper(installed), consumer, loaded_modules=[], exit_on_drift=False, scan="tree"
    )
    assert verdict["status"] == "consuming-repo"


def test_tree_scan_allows_an_identical_installed_copy(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.2")
    installed = _installed_tree(tmp_path, version="2.11.2")
    verdict = guard.require_repo_local_helper(
        _helper(installed), source, loaded_modules=[], exit_on_drift=False, scan="tree"
    )
    assert verdict["status"] == "in-sync"


def test_refusal_caps_the_drift_list_instead_of_burying_the_remediation(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.2")
    installed = _installed_tree(tmp_path, version="2.11.2")
    for index in range(guard._REFUSAL_DRIFT_LIMIT + 4):
        _write(source / "scripts" / f"mod_{index}.py", "SOURCE = 1\n")
        _write(installed / "scripts" / f"mod_{index}.py", "INSTALLED = 1\n")
    with pytest.raises(guard.ForeignHelperError) as excinfo:
        guard.require_repo_local_helper(
            _helper(installed), source, loaded_modules=[], exit_on_drift=False, scan="tree"
        )
    message = str(excinfo.value)
    assert "more)" in message
    # The remediation must survive the evidence.
    assert "Run the target repo's own copy instead:" in message


# Post-review fixes ----------------------------------------------------------


def test_identity_candidate_survives_for_a_same_layout_foreign_tree(tmp_path: Path) -> None:
    """Two source-layout checkouts share paths verbatim; dropping identity skipped them."""
    source = _source_tree(tmp_path, version="2.11.2")
    other = tmp_path / "other"
    _write(other / "packaging" / "charness.json", json.dumps({"package_id": "charness", "version": "2.11.2"}))
    _write(other / "scripts" / "runtime_bootstrap.py", "# marker\n")
    _write(other / "skills" / "shared" / "scripts" / "fingerprint.py", "DRIFTED = 1\n")
    _write(source / "skills" / "shared" / "scripts" / "fingerprint.py", "DRIFTED = 2\n")
    _write(other / "skills" / "public" / "demo" / "scripts" / "helper.py", "# helper\n")
    verdict = guard.inspect_helper_provenance(
        other / "skills" / "public" / "demo" / "scripts" / "helper.py",
        source,
        loaded_modules=[],
        scan="tree",
    )
    assert verdict["status"] == "drifted"
    assert "skills/shared/scripts/fingerprint.py" in verdict["drifted"]


def test_tree_scan_reaches_the_exported_support_layout(tmp_path: Path) -> None:
    """The exporter puts support skills at top-level `support/`, not under `skills/`."""
    source = _source_tree(tmp_path, version="2.11.2")
    _write(source / "skills" / "support" / "web-fetch" / "scripts" / "reader.py", "V = 2\n")
    installed = _installed_tree(tmp_path, version="2.11.2")
    _write(installed / "support" / "web-fetch" / "scripts" / "reader.py", "V = 1\n")
    verdict = guard.inspect_helper_provenance(
        _helper(installed), source, loaded_modules=[], scan="tree"
    )
    assert verdict["status"] == "drifted"
    assert "skills/support/web-fetch/scripts/reader.py" in verdict["drifted"]


def test_refusal_remediation_keeps_the_other_arguments(monkeypatch, tmp_path: Path) -> None:
    """`publish_release.py` requires one of --part/--publish-current/--set-version.

    A remediation that drops them exits 2 again — the remediation-that-cannot-
    terminate shape this module exists to kill.
    """
    monkeypatch.setattr(
        guard.sys, "argv", ["publish_release.py", "--repo-root", "/x", "--part", "patch"]
    )
    source = _source_tree(tmp_path, version="2.11.2")
    installed = _installed_tree(tmp_path, version="2.11.1")
    with pytest.raises(guard.ForeignHelperError) as excinfo:
        guard.require_repo_local_helper(
            _helper(installed), source, loaded_modules=[], exit_on_drift=False
        )
    remediation = next(
        line for line in str(excinfo.value).splitlines() if line.strip().startswith("cd ")
    )
    assert remediation.endswith("--repo-root . --part patch")
    assert remediation.count("--repo-root") == 1, "the caller's --repo-root must not be re-added"


def test_entrypoint_repo_root_parsing_matches_argparse(monkeypatch, tmp_path: Path) -> None:
    """argparse accepts any unambiguous prefix and lets the LAST flag win.

    Matching only the exact `--repo-root` spelling let `--repo <target>` bypass
    the guard entirely while the CLI still mutated that target.
    """
    import runpy

    runtime = runpy.run_path("scripts/skill_runtime_bootstrap.py")
    refuse = runtime["refuse_foreign_entrypoint"]
    source = _source_tree(tmp_path, version="2.11.2")
    installed = _installed_tree(tmp_path, version="2.11.1")
    forms = (
        ["--repo-root", str(source)],
        ["--repo", str(source)],
        [f"--repo-roo={source}"],
        ["--repo-root", str(tmp_path / "ignored"), "--repo-root", str(source)],
    )
    for argv in forms:
        monkeypatch.setattr("sys.argv", ["prog", *argv])
        with pytest.raises(SystemExit) as excinfo:
            refuse(_helper(installed))
        assert excinfo.value.code == 2, argv


def test_entrypoint_guard_skips_help(monkeypatch, tmp_path: Path) -> None:
    import runpy

    runtime = runpy.run_path("scripts/skill_runtime_bootstrap.py")
    installed = _installed_tree(tmp_path, version="2.11.1")
    monkeypatch.setattr("sys.argv", ["prog", "--help"])
    assert runtime["refuse_foreign_entrypoint"](_helper(installed))["status"] == "skipped-read-only"
