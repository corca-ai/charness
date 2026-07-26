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
