"""Focused failure and fallback coverage for common runner helpers.

These tests keep the unusual paths in one standing target because they are
otherwise reached only by partial installed layouts or by faults at a live
boundary.  The assertions pin the observable refusal, retention, or cleanup
contract for each path.
"""

from __future__ import annotations

import builtins
import importlib.util
import io
import json
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.support_sync_lib as support_sync
from scripts.run_quality_engine import run as run_quality_engine
from scripts.task_run import task_run_completion, task_run_completion_next_step, task_run_execution
from tests.script_main import load_script_module

ROOT = Path(__file__).resolve().parents[1]


def _load_with_one_import_failure(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
    path: Path,
    blocked_import: str,
    error_type: type[ImportError] = ImportError,
):
    original_import = builtins.__import__
    blocked = True

    def importing(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal blocked
        if blocked and name == blocked_import:
            blocked = False
            raise error_type(f"forced optional import failure: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", importing)
    return load_script_module(module_name, path)


def _without_repo_on_sys_path(monkeypatch: pytest.MonkeyPatch) -> None:
    saved = list(sys.path)
    entries = [entry for entry in saved if entry and Path(entry).resolve() != ROOT]
    monkeypatch.setattr(sys, "path", entries)


def test_lesson_writer_refuses_a_fallback_without_a_repository_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = ROOT / "scripts" / "lessons" / "lesson_ledger_writer_lib.py"
    original_resolve = Path.resolve

    def hide_source_root(path: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if path == source:
            return tmp_path / "partial-install" / source.name
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", hide_source_root)
    with pytest.raises(ImportError, match="forced optional import failure"):
        _load_with_one_import_failure(
            monkeypatch,
            "lesson_writer_without_root",
            source,
            "scripts.runtime_bootstrap",
        )


def test_lesson_writer_import_fallback_bootstraps_a_source_checkout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _without_repo_on_sys_path(monkeypatch)
    module = _load_with_one_import_failure(
        monkeypatch,
        "lesson_writer_partial_import",
        ROOT / "scripts" / "lessons" / "lesson_ledger_writer_lib.py",
        "scripts.runtime_bootstrap",
    )

    # The fallback re-enters the repository package after the first import is
    # refused, leaving the writer with the real runtime-root owner available.
    assert module.runtime_root(ROOT).is_absolute()


def test_lesson_writer_fallback_bootstraps_a_partial_layout_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _without_repo_on_sys_path(monkeypatch)
    source = ROOT / "scripts" / "lessons" / "lesson_ledger_writer_lib.py"
    partial_root = tmp_path / "partial-install"
    (partial_root / "scripts").mkdir(parents=True)
    (partial_root / "scripts" / "runtime_bootstrap.py").write_text("# layout marker\n", encoding="utf-8")
    original_resolve = Path.resolve

    def resolve_partial_source(path: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if path == source:
            return partial_root / "scripts" / "lessons" / source.name
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve_partial_source)
    module = _load_with_one_import_failure(
        monkeypatch,
        "lesson_writer_partial_layout",
        source,
        "scripts.runtime_bootstrap",
    )

    assert module.runtime_root(ROOT).is_absolute()


def test_prepush_partial_layout_fallback_owns_and_cleans_its_temp_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_with_one_import_failure(
        monkeypatch,
        "prepush_partial_layout",
        ROOT / "scripts" / "prepush_close_keyword_guard.py",
        "scripts.runtime_scratch",
        ModuleNotFoundError,
    )

    with module.owned_scratch(tmp_path / "repo", "partial-layout") as scratch:
        assert scratch.is_dir()
        (scratch / "diagnostic.txt").write_text("kept only while owned\n", encoding="utf-8")
        retained_path = scratch

    assert not retained_path.exists()


def test_markdown_preview_partial_layout_imports_the_real_scratch_owner(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _without_repo_on_sys_path(monkeypatch)
    module = _load_with_one_import_failure(
        monkeypatch,
        "markdown_preview_partial_layout",
        ROOT / "skills" / "support" / "markdown-preview" / "scripts" / "markdown_preview_render.py",
        "scripts.runtime_scratch",
    )

    with module.owned_scratch(
        tmp_path / "repo", "markdown-flat", runtime_root_path=tmp_path / "runtime"
    ) as scratch:
        assert scratch.is_dir()
        owner_path = scratch

    assert not owner_path.exists()


def test_quality_engine_recovery_refusal_still_closes_runtime(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    context = SimpleNamespace(repo_root=tmp_path, environment={}, terminal_state="active")
    closed: list[SimpleNamespace] = []
    monkeypatch.setattr("scripts.run_quality_engine.prepare_runtime", lambda *a, **k: context)
    monkeypatch.setattr("scripts.run_quality_engine.close_runtime", lambda value: closed.append(value))
    monkeypatch.setattr("scripts.run_quality_engine.load_gate_list", lambda _path: SimpleNamespace(gates=()))
    monkeypatch.setattr("scripts.run_quality_engine._mutation_recovery_pending", lambda _ctx: True)
    args = _quality_args(tmp_path)

    assert run_quality_engine(args) == 2
    assert "interrupted mutation recovery is REQUIRED" in capsys.readouterr().err
    assert closed == [context]
    assert context.terminal_state == "failed"


def test_quality_engine_empty_selection_finishes_then_closes_runtime(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    context = SimpleNamespace(repo_root=tmp_path, environment={}, terminal_state="active")
    closed: list[SimpleNamespace] = []
    finished: list[dict[str, object]] = []
    monkeypatch.setattr("scripts.run_quality_engine.prepare_runtime", lambda *a, **k: context)
    monkeypatch.setattr("scripts.run_quality_engine.close_runtime", lambda value: closed.append(value))
    monkeypatch.setattr("scripts.run_quality_engine.load_gate_list", lambda _path: SimpleNamespace(gates=()))
    monkeypatch.setattr("scripts.run_quality_engine._mutation_recovery_pending", lambda _ctx: False)
    monkeypatch.setattr("scripts.run_quality_engine.select_gates", lambda *a, **k: {})
    monkeypatch.setattr("scripts.run_quality_engine.not_run_gates", lambda *a, **k: ())
    monkeypatch.setattr("scripts.run_quality_engine.selected_count", lambda _selected: 0)
    monkeypatch.setattr(
        "scripts.run_quality_engine.finish",
        lambda *a, **kwargs: finished.append(kwargs),
    )
    args = _quality_args(tmp_path)

    assert run_quality_engine(args) == 2
    assert finished and finished[0]["overall_rc"] == 2
    assert closed == [context]
    assert context.terminal_state == "failed"


@pytest.mark.parametrize(
    ("native_rc", "preamble_rc", "expected_call"),
    [(1, 0, "native"), (0, 1, "preamble")],
)
def test_quality_engine_early_preflight_returns_close_runtime(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    native_rc: int,
    preamble_rc: int,
    expected_call: str,
) -> None:
    context = SimpleNamespace(repo_root=tmp_path, environment={}, terminal_state="active")
    closed: list[SimpleNamespace] = []
    calls: list[str] = []
    selected = {"phase": (SimpleNamespace(label="selected"),)}
    monkeypatch.setattr("scripts.run_quality_engine.prepare_runtime", lambda *a, **k: context)
    monkeypatch.setattr("scripts.run_quality_engine.close_runtime", lambda value: closed.append(value))
    monkeypatch.setattr("scripts.run_quality_engine.load_gate_list", lambda _path: SimpleNamespace(gates=()))
    monkeypatch.setattr("scripts.run_quality_engine._mutation_recovery_pending", lambda _ctx: False)
    monkeypatch.setattr("scripts.run_quality_engine.select_gates", lambda *a, **k: selected)
    monkeypatch.setattr("scripts.run_quality_engine.not_run_gates", lambda *a, **k: ())
    monkeypatch.setattr("scripts.run_quality_engine.selected_count", lambda _selected: 1)

    def native(_context, _gates):
        calls.append("native")
        return native_rc

    def preamble(_context, *, read_only):
        del read_only
        calls.append("preamble")
        return preamble_rc

    monkeypatch.setattr("scripts.run_quality_engine._native_preflight", native)
    monkeypatch.setattr("scripts.run_quality_engine.run_preamble", preamble)

    assert run_quality_engine(_quality_args(tmp_path)) == 1
    expected_calls = ["native"] if expected_call == "native" else ["native", "preamble"]
    assert calls == expected_calls
    assert closed == [context]
    assert context.terminal_state == "failed"


def _quality_args(repo_root: Path) -> SimpleNamespace:
    return SimpleNamespace(
        repo_root=repo_root,
        gates=repo_root / "quality-gates.yaml",
        full=False,
        read_only=False,
        release=False,
        release_prepare=0,
        review=False,
        non_claim="",
        receipt_json=None,
        labels="",
        print_docs_only_labels=False,
    )


def test_runtime_engine_optional_owner_fallback_cleans_fixture_scratch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import scripts.runtime_bootstrap as bootstrap

    real_import_repo_module = bootstrap.import_repo_module

    def import_without_optional_owner(path: str, module_name: str):
        if module_name == "scripts.runtime_scratch":
            raise ModuleNotFoundError(module_name)
        return real_import_repo_module(path, module_name)

    monkeypatch.setattr(bootstrap, "import_repo_module", import_without_optional_owner)
    module = load_script_module(
        "quality_runtime_partial_owner",
        ROOT / "scripts" / "run_quality_engine_runtime.py",
    )
    owner = module.OwnedScratch(
        tmp_path / "fixture-repo",
        "fixture-owner",
        runtime_root_path=tmp_path / "runtime",
    )

    scratch = owner.open()
    assert scratch.is_dir()
    assert scratch.parent.parent == tmp_path / "runtime"
    owner.close(state="failed")
    assert not scratch.exists()
    assert owner._directory is None


def _tarball(entries: list[tarfile.TarInfo], payloads: dict[str, bytes] | None = None) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        for entry in entries:
            content = (payloads or {}).get(entry.name, b"")
            if entry.isfile():
                entry.size = len(content)
                archive.addfile(entry, io.BytesIO(content))
            else:
                archive.addfile(entry)
    return output.getvalue()


def test_support_sync_refuses_a_special_archive_entry(tmp_path: Path) -> None:
    destination = tmp_path / "extract"
    destination.mkdir()
    special = tarfile.TarInfo("repo/device")
    special.type = tarfile.FIFOTYPE

    with pytest.raises(ValueError, match="special archive entry"):
        support_sync._safe_extract_tarball(_tarball([special]), destination)
    assert not any(destination.rglob("*"))


def test_support_sync_download_fallback_uses_cwd_and_cleans_owned_scratch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("CHARNESS_CACHE_HOME", str(tmp_path / "cache"))
    runtime_root = tmp_path / "runtime"
    real_owned_scratch = support_sync.owned_scratch

    def owned_scratch_in_test_runtime(repo_root, producer, **kwargs):  # type: ignore[no-untyped-def]
        return real_owned_scratch(
            repo_root,
            producer,
            runtime_root_path=runtime_root,
            **kwargs,
        )

    monkeypatch.setattr(support_sync, "owned_scratch", owned_scratch_in_test_runtime)
    root = tarfile.TarInfo("upstream")
    root.type = tarfile.DIRTYPE
    skill = tarfile.TarInfo("upstream/skills/demo")
    skill.type = tarfile.DIRTYPE
    readme = tarfile.TarInfo("upstream/skills/demo/SKILL.md")
    readme.type = tarfile.REGTYPE
    archive = _tarball([root, skill, readme], {readme.name: b"# downloaded\n"})
    monkeypatch.setattr(support_sync, "_fetch_upstream_archive", lambda _repo, _ref: archive)

    manifest = {
        "tool_id": "demo",
        "upstream_repo": "example/demo",
        "support_skill_source": {"path": "skills/demo", "ref": "main"},
    }
    resolved = support_sync._resolve_upstream_source_path(
        manifest,
        upstream_checkouts={},
        repo_root=None,
    )

    assert resolved.parent == support_sync.support_skill_cache_dir() / "demo"
    assert (resolved / "SKILL.md").read_text(encoding="utf-8") == "# downloaded\n"
    scratch_producer = runtime_root / "scratch" / "support-sync"
    assert not scratch_producer.exists() or not any(scratch_producer.iterdir())


def test_task_completion_persists_delivery_failure_and_reviewer_carrier(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = {"task_id": "delivery-failure", "execution": {}}
    persisted: list[dict[str, object]] = []
    candidate = {"useful": False, "changed_paths": []}
    scope = {
        "verdict": "fail",
        "reason": "scope refusal",
        "candidate_carrier": {"observed_branch": "main", "observed_head_sha": "head-sha"},
    }
    monkeypatch.setattr(
        task_run_completion,
        "_execution_reviewer_result",
        lambda _delivery: {"state": "partial"},
    )
    monkeypatch.setattr(
        task_run_completion,
        "_prove_ready_candidate",
        lambda _payload, _candidate, **kwargs: (
            {"status": "skipped", "reason": "blocked"},
            kwargs["blockers"],
            "failed",
        ),
    )
    monkeypatch.setattr(task_run_completion, "_apply_lane_retention", lambda *a, **k: None)

    result = task_run_completion.complete_task(
        payload,
        runtime_path=tmp_path / "result.json",
        resolved_target=tmp_path / "target",
        resolved_repo=tmp_path / "repo",
        before_exec={},
        base_sha="base-sha",
        scope_specs=[],
        require_change=False,
        parent_before={},
        parent_before_head="parent-sha",
        stdout_log=tmp_path / "stdout.log",
        execution=payload["execution"],
        started_at=0.0,
        persist=lambda value, _path: persisted.append(value.copy()),
        result_delivery=lambda _log: (_ for _ in ()).throw(OSError("log is unreadable")),
        completion_evidence=lambda **_kwargs: (
            {"populations": {}},
            scope,
            {"blocking": False, "classification": "no-parent-progress"},
        ),
        execution_state=lambda _execution, _delivery: "failed",
        candidate_result_state=lambda **_kwargs: (candidate, "failed"),
        candidate_commit=None,
        git=lambda *_args: pytest.fail("branch lookup should use the observed carrier"),
        git_output=lambda *_args: pytest.fail("target sha should use the observed carrier"),
        pass_value="pass",
    )

    delivery = result["result_delivery"]
    assert delivery["status"] == "non-delivery"
    assert delivery["delivery_error"] == "log is unreadable"
    assert result["reviewer_result"] == {
        "state": "partial",
        "task_id": "delivery-failure",
        "task_result_path": str(tmp_path / "result.json"),
    }
    assert result["status"] == "failed"
    assert "result delivery could not be read: log is unreadable" in result["next_step"]
    assert persisted


def test_completion_next_step_discloses_validated_partial_result() -> None:
    message = task_run_completion_next_step._next_step(
        {"target_branch": "main", "target_sha": "head-sha"},
        resolved_target=Path("/tmp/task-target"),
        candidate={"head_is_complete": True},
        execution_status="completed",
        result_state="validated-partial-result",
        blockers=[],
    )

    assert message == (
        "Review the validated candidate on branch main at head-sha; "
        "it is useful but not approval-eligible."
    )


def test_task_execution_reports_missing_reviewer_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(task_run_execution, "_REVIEWER_CONTRACT", None)
    original_is_file = Path.is_file

    def no_contract(path: Path) -> bool:
        if path.name == "reviewer_result_contract.py":
            return False
        return original_is_file(path)

    monkeypatch.setattr(Path, "is_file", no_contract)
    with pytest.raises(ImportError, match="shared reviewer_result_contract.py is unavailable"):
        task_run_execution._bounded_result_shape({})


def test_task_execution_reports_unloadable_reviewer_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(task_run_execution, "_REVIEWER_CONTRACT", None)
    original_spec = importlib.util.spec_from_file_location

    def no_loader(name, location, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "charness_reviewer_result_contract":
            return SimpleNamespace(loader=None)
        return original_spec(name, location, *args, **kwargs)

    monkeypatch.setattr(task_run_execution.importlib.util, "spec_from_file_location", no_loader)
    with pytest.raises(ImportError, match="cannot load reviewer result contract"):
        task_run_execution._bounded_result_shape({})


def _bounded_review() -> dict[str, object]:
    return {"kind": "charness.bounded_review.v1", "verdict": "defer"}


def test_task_execution_recovers_nested_and_windowed_bounded_reviews(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nested = json.dumps([{"noise": []}, [{"kind": "charness.bounded_review.v1", "verdict": "defer"}]])
    nested_carrier = task_run_execution._reviewer_result_carrier({"text": nested})
    assert nested_carrier is not None
    assert nested_carrier["source"] == "text-json"

    monkeypatch.setattr(task_run_execution, "_REVIEW_SCAN_LIMIT_BYTES", 256)
    result = json.dumps(_bounded_review()).encode("utf-8")
    oversized = b"x" * 300 + result
    windowed_carrier = task_run_execution._reviewer_result_carrier(
        {"text": "not-json " + oversized.decode("utf-8")}
    )

    assert windowed_carrier is not None
    assert windowed_carrier["result"]["kind"] == "charness.bounded_review.v1"
    assert windowed_carrier["source"] == "text-json"


def test_task_execution_result_delivery_reports_unreadable_log(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    log = tmp_path / "stdout.log"
    log.write_text("result\n", encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def unreadable(path: Path) -> bytes:
        if path == log:
            raise OSError("permission denied")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", unreadable)
    delivery = task_run_execution._result_delivery(log)

    assert delivery == {
        "status": "non-delivery",
        "bytes": None,
        "truncated": False,
        "text": "",
        "log": str(log),
        "structured_status": "unavailable",
        "delivery_error": "permission denied",
        "delivery_error_type": "OSError",
    }
