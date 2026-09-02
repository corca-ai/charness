from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest

guard = importlib.import_module("scripts.core.helper_provenance_lib")


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
    installed = _installed_tree(tmp_path, version="2.11.1")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["status"] == "consuming-repo"


def test_missing_entry_counterpart_does_not_absorb_a_version_mismatch(tmp_path: Path) -> None:
    """The invoked helper itself is never compared here, so a clean verdict would be a
    pass over a scope that was never established."""

    source = _source_tree(tmp_path, version="2.11.1")
    (source / "skills" / "public" / "demo" / "scripts" / "helper.py").unlink()
    installed = _installed_tree(tmp_path, version="2.11.0")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["status"] == "drifted"
    assert verdict["target_helper"] is None
    assert verdict["version_mismatch"] is True
    assert verdict["drifted"] == []
    assert verdict["compared_pairs"] < verdict["compared_count"], "the entry point went uncompared"


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


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "", "  ", "FALSE"])
def test_falsy_override_spellings_do_not_disable_the_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    """`CHARNESS_ALLOW_FOREIGN_HELPER=0` is how an operator says "keep the guard on".

    Bare truthiness read every non-empty spelling as "on", so the escape hatch fired
    for the exact values that ask for the opposite — the same bypass inversion this
    slice repaired in `check_staged_worktree_consistency`, in the file holding the
    hardest refusal the slice added.
    """
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    monkeypatch.setenv(guard.OVERRIDE_ENV, value)

    with pytest.raises(guard.ForeignHelperError):
        guard.require_repo_local_helper(
            _helper(installed), source, loaded_modules=[], exit_on_drift=False
        )


@pytest.mark.parametrize("value", ["1", "true", "YES", " on "])
def test_truthy_override_spellings_do_disable_the_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    monkeypatch.setenv(guard.OVERRIDE_ENV, value)

    verdict = guard.require_repo_local_helper(
        _helper(installed), source, loaded_modules=[], exit_on_drift=False
    )

    assert verdict["status"] == "override-allowed"


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


def test_unknown_own_root_refuses_a_write_into_a_source_tree(tmp_path: Path) -> None:
    """An unlocatable copy establishes nothing, so it must not be handed a pass.

    The stalest possible copy reaches this branch -- a hand-copied or vendored script
    package with no tree marker above it -- and it used to write straight into the
    charness source tree.
    """

    source = _source_tree(tmp_path, version="2.11.1")
    orphan = _write(tmp_path / "orphan" / "helper.py", "# ancient helper\n")
    verdict = guard.inspect_helper_provenance(orphan, source, loaded_modules=[])
    assert verdict["status"] == "own-root-unestablished"
    assert verdict["status"] in guard._REFUSED_STATUSES
    with pytest.raises(guard.ForeignHelperError) as excinfo:
        guard.require_repo_local_helper(orphan, source, loaded_modules=[], exit_on_drift=False)
    message = str(excinfo.value)
    assert "no locatable charness tree" in message
    # The refusal must not claim a comparison it never ran.
    assert "the two copies have drifted" not in message
    assert guard.OVERRIDE_ENV in message


def test_unknown_own_root_against_a_consuming_repo_still_writes(tmp_path: Path) -> None:
    """The normal installed-plugin case: no competing copy exists in the target."""

    consumer = tmp_path / "consumer"
    _write(consumer / "README.md", "# app\n")
    orphan = _write(tmp_path / "orphan" / "helper.py", "# helper\n")
    verdict = guard.require_repo_local_helper(orphan, consumer, loaded_modules=[], exit_on_drift=False)
    assert verdict["status"] == "consuming-repo"


def test_unknown_own_root_refusal_is_overridable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    orphan = _write(tmp_path / "orphan" / "helper.py", "# ancient helper\n")
    monkeypatch.setenv(guard.OVERRIDE_ENV, "1")
    verdict = guard.require_repo_local_helper(orphan, source, loaded_modules=[], exit_on_drift=False)
    assert verdict["status"] == "override-allowed"
    assert guard.OVERRIDE_ENV in capsys.readouterr().err


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


@pytest.mark.parametrize(
    "form",
    ["--repo-root {}", "--repo {}", "--repo-roo={}", "--repo-root {ignored} --repo-root {}"],
    ids=["exact", "prefix", "prefix-equals", "last-wins"],
)
def test_entrypoint_repo_root_parsing_matches_argparse(
    monkeypatch, tmp_path: Path, capsys, form: str
) -> None:
    """argparse accepts any unambiguous prefix and lets the LAST flag win.

    Matching only the exact `--repo-root` spelling let `--repo <target>` bypass
    the guard entirely while the CLI still mutated that target.

    Asserted on the RESOLVED TARGET, not on the exit code. The first cut asserted
    `code == 2`, which the unparsed fallback (`repo_root = Path.cwd()`, i.e. the
    charness repo itself, a source tree that drifts from the 2.11.1 fixture)
    produces on its own — so three of the four forms would have stayed green
    against a parser that recognized nothing at all. That is a verdict keyed on a
    field that is constant where it must discriminate, inside the test guarding
    exactly that class.
    """
    import runpy

    runtime = runpy.run_path("scripts/skill_runtime_bootstrap.py")
    refuse = runtime["refuse_foreign_entrypoint"]
    source = _source_tree(tmp_path, version="2.11.2")
    installed = _installed_tree(tmp_path, version="2.11.1")
    ignored = tmp_path / "ignored"
    argv = form.format(source, ignored=ignored).split()

    monkeypatch.setattr("sys.argv", ["prog", *argv])
    with pytest.raises(SystemExit) as excinfo:
        refuse(_helper(installed))

    assert excinfo.value.code == 2, argv
    message = capsys.readouterr().err
    assert str(source) in message, argv
    assert str(Path.cwd()) not in message, "fell back to cwd instead of parsing the flag"


def test_entrypoint_guard_skips_help(monkeypatch, tmp_path: Path) -> None:
    import runpy

    runtime = runpy.run_path("scripts/skill_runtime_bootstrap.py")
    installed = _installed_tree(tmp_path, version="2.11.1")
    monkeypatch.setattr("sys.argv", ["prog", "--help"])
    assert runtime["refuse_foreign_entrypoint"](_helper(installed))["status"] == "skipped-read-only"


def _nested_mirror(source: Path, *, version: str, lib_body: str = "VALUE = 1\n") -> Path:
    """The materialized `plugins/<pkg>` export: a second charness tree INSIDE the target."""

    root = source / "plugins" / "charness"
    _write(root / ".claude-plugin" / "plugin.json", json.dumps({"name": "charness", "version": version}))
    _write(root / "scripts" / "runtime_bootstrap.py", "# marker\n")
    _write(root / "scripts" / "lessons_lib.py", lib_body)
    _write(root / "skills" / "demo" / "scripts" / "helper.py", "# helper\n")
    _write(root / "skills" / "demo" / "scripts" / "resolve_adapter.py", "# adapter\n")
    return root


def test_synced_nested_mirror_still_writes(tmp_path: Path) -> None:
    """No legitimate regression: a mirror in sync with its own repo passes, having compared."""

    source = _source_tree(tmp_path, version="2.11.1")
    mirror = _nested_mirror(source, version="2.11.1")
    verdict = guard.require_repo_local_helper(
        _helper(mirror), source, loaded_modules=[], exit_on_drift=False, scan="tree"
    )
    assert verdict["status"] == "in-sync"
    assert verdict["drifted"] == []
    # `compared_count` is files SCANNED; only `compared_pairs` proves a counterpart was
    # resolved and digested, which is the scope a clean verdict is reported over.
    assert verdict["compared_pairs"] == verdict["compared_count"] > 0


def test_stale_nested_mirror_is_refused_not_exempted(tmp_path: Path) -> None:
    """A1: containment is not identity. The mirror is stale during every mutate->sync window."""

    source = _source_tree(tmp_path, version="2.11.1")
    mirror = _nested_mirror(source, version="2.11.1")
    _write(mirror / "scripts" / "lessons_lib.py", "VALUE = 0\n")
    verdict = guard.inspect_helper_provenance(_helper(mirror), source, scan="tree")
    assert verdict["status"] == "drifted"
    assert verdict["drifted"] == ["scripts/lessons_lib.py"]


def test_shared_export_layout_counterpart_is_resolved(tmp_path: Path) -> None:
    """The exporter hoists `skills/shared/**` to `shared/**`; without the remap it is unscanned."""

    source = _source_tree(tmp_path, version="2.11.1")
    _write(source / "skills" / "shared" / "scripts" / "reviewer_result.py", "# newer\n")
    installed = _installed_tree(tmp_path, version="2.11.1")
    _write(installed / "shared" / "scripts" / "reviewer_result.py", "# older\n")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, scan="tree")
    assert verdict["status"] == "drifted"
    assert verdict["drifted"] == ["skills/shared/scripts/reviewer_result.py"]


def test_drift_survives_an_entry_point_absent_from_the_target(tmp_path: Path) -> None:
    """A2: a coarse existence test on the ENTRY script must not discard a computed drift list."""

    source = _source_tree(tmp_path, version="2.11.1", lib_body="VALUE = 2\n")
    (source / "skills" / "public" / "demo" / "scripts" / "helper.py").unlink()
    installed = _installed_tree(tmp_path, version="2.11.1")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, scan="tree")
    assert verdict["status"] == "drifted"
    assert verdict["target_helper"] is None
    assert verdict["drifted"] == ["scripts/lessons_lib.py"]
    message = guard.format_refusal(verdict)
    assert "python3 None" not in message
    assert "no repo-local command can be named" in message


def test_missing_entry_counterpart_without_drift_stays_consuming(tmp_path: Path) -> None:
    """The control: the existence test still governs when versions agree and nothing drifted."""

    source = _source_tree(tmp_path, version="2.11.1")
    (source / "skills" / "public" / "demo" / "scripts" / "helper.py").unlink()
    installed = _installed_tree(tmp_path, version="2.11.1")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["status"] == "consuming-repo"


def test_stale_nested_mirror_is_refused_on_the_anchors_scan_too(tmp_path: Path) -> None:
    """The write sites run the DEFAULT anchors scan; pinning only `scan="tree"` would
    leave five guarded write helpers unproven."""

    source = _source_tree(tmp_path, version="2.11.1")
    mirror = _nested_mirror(source, version="2.11.1")
    _write(mirror / "skills" / "demo" / "scripts" / "resolve_adapter.py", "# adapter, older\n")
    verdict = guard.inspect_helper_provenance(_helper(mirror), source, loaded_modules=[])
    assert verdict["status"] == "drifted"
    assert verdict["drifted"] == ["skills/public/demo/scripts/resolve_adapter.py"]


def test_drift_survives_a_missing_entry_counterpart_on_the_anchors_scan(tmp_path: Path) -> None:
    """A2 on the production default scan, not only the entrypoint scan."""

    source = _source_tree(tmp_path, version="2.11.1")
    (source / "skills" / "public" / "demo" / "scripts" / "helper.py").unlink()
    installed = _installed_tree(tmp_path, version="2.11.1")
    _write(installed / "skills" / "demo" / "scripts" / "resolve_adapter.py", "# adapter, older\n")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["target_helper"] is None
    assert verdict["status"] == "drifted"
    assert verdict["drifted"] == ["skills/public/demo/scripts/resolve_adapter.py"]


def test_exported_shared_entry_point_compares_its_siblings(tmp_path: Path) -> None:
    """The anchor sibling glob was keyed on `skills`, so an exported `shared/` entry
    point compared one lone file while its siblings drifted unseen."""

    source = _source_tree(tmp_path, version="2.11.1")
    _write(source / "skills" / "shared" / "scripts" / "run_plan_envelope.py", "# entry\n")
    _write(source / "skills" / "shared" / "scripts" / "reviewer_result.py", "# newer\n")
    installed = _installed_tree(tmp_path, version="2.11.1")
    entry = _write(installed / "shared" / "scripts" / "run_plan_envelope.py", "# entry\n")
    _write(installed / "shared" / "scripts" / "reviewer_result.py", "# older\n")
    verdict = guard.inspect_helper_provenance(entry, source, loaded_modules=[])
    assert verdict["status"] == "drifted"
    assert verdict["drifted"] == ["skills/shared/scripts/reviewer_result.py"]


def test_an_empty_comparison_is_not_a_pass(tmp_path: Path) -> None:
    """Rename the whole script package in the target: every counterpart resolves to
    None, so `no drift found` is an empty scan, not a finding."""

    source = _source_tree(tmp_path, version="2.11.1")
    (source / "skills" / "public" / "demo").rename(source / "skills" / "public" / "demo2")
    installed = _installed_tree(tmp_path, version="2.11.1")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    assert verdict["status"] == "scope-unestablished"
    assert verdict["compared_pairs"] == 0
    assert verdict["drifted"] == []
    with pytest.raises(guard.ForeignHelperError):
        guard.require_repo_local_helper(_helper(installed), source, loaded_modules=[], exit_on_drift=False)


def test_the_refusal_states_the_scope_it_compared(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.1")
    _write(installed / "skills" / "demo" / "scripts" / "resolve_adapter.py", "# adapter, older\n")
    message = guard.format_refusal(guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[]))
    assert "compared: 2 of 2 scanned module(s) had a counterpart" in message


def test_a_contained_mirror_refusal_names_the_resync(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    mirror = _nested_mirror(source, version="2.11.1")
    _write(mirror / "scripts" / "lessons_lib.py", "VALUE = 0\n")
    message = guard.format_refusal(guard.inspect_helper_provenance(_helper(mirror), source, scan="tree"))
    assert "sync_root_plugin_manifests.py --repo-root ." in message


def test_remediation_keeps_a_subcommand_cli_runnable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`issue_tool.py` declares `--repo-root` on each SUBparser, so hoisting the flag
    to the front prints a command argparse rejects before reading the subcommand."""

    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    monkeypatch.setattr(
        "sys.argv",
        ["issue_tool.py", "close-with-comment", "--repo-root", str(source), "--number", "463"],
    )
    message = guard.format_refusal(guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[]))
    remediation = next(line for line in message.splitlines() if line.strip().startswith("cd "))
    assert remediation.endswith("close-with-comment --repo-root . --number 463")


def test_remediation_retargets_an_abbreviated_repo_root_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    monkeypatch.setattr("sys.argv", ["prog", "--repo", str(source), "--part", "patch"])
    message = guard.format_refusal(guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[]))
    remediation = next(line for line in message.splitlines() if line.strip().startswith("cd "))
    assert remediation.endswith("--repo . --part patch")
    assert str(source) not in remediation.split("&&")[1]


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads a 0o000 file, so the fail-open cannot be staged")
def test_an_unreadable_pair_is_drift_not_agreement(tmp_path: Path) -> None:
    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.1")
    for root, tail in ((source, Path("skills/public/demo")), (installed, Path("skills/demo"))):
        (root / tail / "scripts" / "resolve_adapter.py").chmod(0o000)
    try:
        verdict = guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[])
    finally:
        for root, tail in ((source, Path("skills/public/demo")), (installed, Path("skills/demo"))):
            (root / tail / "scripts" / "resolve_adapter.py").chmod(0o644)
    assert verdict["status"] == "drifted"
    assert verdict["drifted"] == ["skills/public/demo/scripts/resolve_adapter.py"]
    # The operator is pointed at the file that is actually unreadable — its own —
    # not only at the target counterpart, which is fine.
    assert verdict["unreadable"] == ["skills/demo/scripts/resolve_adapter.py"]


def test_the_checked_in_export_root_is_not_a_source_tree(tmp_path: Path) -> None:
    """Load-bearing: an export root fails `is_charness_source_tree`, which is the only
    reason the one-directional source->export counterpart gap stays unreachable."""

    assert guard.is_charness_source_tree(Path(".").resolve()) is True
    assert guard.is_charness_source_tree(Path("plugins/charness").resolve()) is False


def test_remediation_preserves_a_distinct_repo_option(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`issue_tool.py` declares `--repo <owner/repo>` alongside `--repo-root`. Treating
    every prefix as an abbreviation replaced the issue's target repo with `.`."""

    source = _source_tree(tmp_path, version="2.11.1")
    installed = _installed_tree(tmp_path, version="2.11.0")
    monkeypatch.setattr(
        "sys.argv",
        ["issue_tool.py", "close-with-comment", "--repo", "corca-ai/charness",
         "--repo-root", str(source), "--number", "463"],
    )
    message = guard.format_refusal(guard.inspect_helper_provenance(_helper(installed), source, loaded_modules=[]))
    remediation = next(line for line in message.splitlines() if line.strip().startswith("cd "))
    assert "--repo corca-ai/charness" in remediation
    assert remediation.endswith("--repo-root . --number 463")


def test_a_contained_mirror_without_a_counterpart_is_told_to_resync(tmp_path: Path) -> None:
    """The no-counterpart branch warns against resyncing; for the contained mirror that
    advice is backwards, and it is the branch the mirror's worst case lands in."""

    source = _source_tree(tmp_path, version="2.11.1")
    mirror = _nested_mirror(source, version="2.11.1")
    (source / "skills" / "public" / "demo").rename(source / "skills" / "public" / "demo2")
    message = guard.format_refusal(guard.inspect_helper_provenance(_helper(mirror), source, scan="tree"))
    assert "sync_root_plugin_manifests.py --repo-root ." in message
    assert "Re-running after a resync is not a remediation" not in message


def test_a_contained_worktree_is_not_told_to_resync_the_plugin_tree(tmp_path: Path) -> None:
    """Containment alone is the wrong test: a worktree inside the repo is contained too,
    and the plugin resync would mutate the repo without touching the reported drift."""

    source = _source_tree(tmp_path, version="2.11.1")
    worktree = source / ".worktrees" / "fix"
    _write(worktree / "packaging" / "charness.json",
           json.dumps({"package_id": "charness", "version": "2.11.1"}))
    _write(worktree / "scripts" / "runtime_bootstrap.py", "# marker\n")
    _write(worktree / "scripts" / "lessons_lib.py", "VALUE = 0\n")
    entry = _write(worktree / "skills" / "public" / "demo" / "scripts" / "helper.py", "# helper\n")
    _write(worktree / "skills" / "public" / "demo" / "scripts" / "resolve_adapter.py", "# adapter\n")
    verdict = guard.inspect_helper_provenance(entry, source, scan="tree")
    assert verdict["status"] == "drifted"
    assert "sync_root_plugin_manifests.py" not in guard.format_refusal(verdict)


def test_a_tree_scan_that_matches_nothing_is_not_in_sync(tmp_path: Path) -> None:
    """The empty-scope refusal is unconditional, not gated behind the entry-counterpart
    test, so no scan can report a clean verdict over zero compared bytes."""

    source = _source_tree(tmp_path, version="2.11.1")
    (source / "skills" / "public" / "demo").rename(source / "skills" / "public" / "demo2")
    (source / "scripts" / "lessons_lib.py").unlink()
    (source / "scripts" / "runtime_bootstrap.py").unlink()
    installed = _installed_tree(tmp_path, version="2.11.1")
    verdict = guard.inspect_helper_provenance(_helper(installed), source, scan="tree")
    assert verdict["compared_pairs"] == 0
    assert verdict["status"] == "scope-unestablished"
