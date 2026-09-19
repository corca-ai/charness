from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT, run_script

SCRIPT = ROOT / "skills/public/achieve/scripts/goal_binding.py"
OBSERVATION = ROOT / "skills/public/issue/scripts/issue_tracker_observation.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


binding = _load("goal_binding_freeze_under_test", SCRIPT)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parent(number: int = 724) -> dict[str, object]:
    return {
        "repo": "corca-ai/charness",
        "number": number,
        "url": f"https://github.com/corca-ai/charness/issues/{number}",
    }


def _created(key: str, dependencies: list[str] | None = None, rank: int = 1) -> dict[str, object]:
    return {
        "key": key,
        "intent": "create",
        "issue": None,
        "dependencies": dependencies or [],
        "rank": rank,
        "observed": None,
    }


def test_build_binding_canonicalizes_planner_dependency_order() -> None:
    payload = binding.build_binding(
        draft_path="charness-artifacts/goals/demo.md",
        draft_sha256=_sha("draft"),
        briefing_sha256=_sha("briefing"),
        approval_response="approved",
        approval_session_id="session-1",
        approval_observed_at="2026-09-19T00:00:00+09:00",
        parent=_parent(),
        approved_work_items=[
            _created("b", dependencies=["a"], rank=2),
            _created("a", rank=1),
        ],
    )
    assert [item["key"] for item in payload["approved_work_items"]] == ["a", "b"]

    unordered = binding.build_binding(
        draft_path="charness-artifacts/goals/demo.md",
        draft_sha256=_sha("draft"),
        briefing_sha256=_sha("briefing"),
        approval_response="approved",
        approval_session_id="session-1",
        approval_observed_at="2026-09-19T00:00:00+09:00",
        parent=_parent(),
        approved_work_items=[
            _created("b", dependencies=["c", "a", "c"], rank=3),
            _created("c", dependencies=["a"], rank=2),
            _created("a", rank=1),
        ],
    )
    by_key = {item["key"]: item for item in unordered["approved_work_items"]}
    assert by_key["b"]["dependencies"] == ["a", "c"]
    assert by_key["c"]["dependencies"] == ["a"]


def test_build_binding_still_refuses_self_unknown_and_cycle() -> None:
    common = {
        "draft_path": "charness-artifacts/goals/demo.md",
        "draft_sha256": _sha("draft"),
        "briefing_sha256": _sha("briefing"),
        "approval_response": "approved",
        "approval_session_id": "session-1",
        "approval_observed_at": "2026-09-19T00:00:00+09:00",
        "parent": _parent(),
    }
    for items, code in (
        ([_created("a", dependencies=["a"], rank=1)], "schema-invalid"),
        ([_created("a", dependencies=["missing"], rank=1)], "schema-invalid"),
    ):
        try:
            binding.build_binding(**common, approved_work_items=items)
        except binding.BindingError as exc:
            assert exc.code == code
        else:
            raise AssertionError(f"expected {code} for {items!r}")


def test_freeze_cli_hashes_draft_and_writes_deterministic_sibling(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    draft_rel = "charness-artifacts/goals/2026-09-19-demo.md"
    draft = repo / draft_rel
    draft.parent.mkdir(parents=True)
    draft.write_text("# approved draft\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {"key": "b", "intent": "create", "issue": None,
                 "dependencies": ["a"], "rank": 2, "observed": None},
                {"key": "a", "intent": "create", "issue": None,
                 "dependencies": [], "rank": 1, "observed": None},
            ]
        ),
        encoding="utf-8",
    )
    result = run_script(
        str(SCRIPT),
        "freeze",
        "--repo-root", str(repo),
        "--draft", draft_rel,
        "--parent-repo", "corca-ai/charness",
        "--parent-number", "724",
        "--briefing-sha256", _sha("briefing"),
        "--approval-response", "approved",
        "--approval-session-id", "session-1",
        "--approval-observed-at", "2026-09-19T00:00:00+09:00",
        "--manifest", str(manifest),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["draft_sha256"] == binding.sha256_file(draft)
    written = repo / payload["binding_path"]
    assert written.is_file()
    stored = json.loads(written.read_text(encoding="utf-8"))
    assert stored["draft"]["sha256"] == payload["draft_sha256"]
    assert [item["key"] for item in stored["approved_work_items"]] == ["a", "b"]


def test_freeze_cli_help_names_freeze_subcommand() -> None:
    result = run_script(str(SCRIPT), "--help")
    assert result.returncode == 0, result.stderr
    assert "freeze" in result.stdout


def test_build_binding_passes_malformed_dependencies_to_typed_refusal() -> None:
    malformed = _created("a", rank=1)
    malformed["dependencies"] = "a"
    with pytest.raises(binding.BindingError) as exc_info:
        binding.build_binding(
            draft_path="charness-artifacts/goals/demo.md",
            draft_sha256=_sha("draft"),
            briefing_sha256=_sha("briefing"),
            approval_response="approved",
            approval_session_id="session-1",
            approval_observed_at="2026-09-19T00:00:00+09:00",
            parent=_parent(),
            approved_work_items=[malformed],
        )
    assert exc_info.value.code == "schema-invalid"


def test_freeze_main_runs_in_process(tmp_path: Path) -> None:
    freeze = _load(
        "goal_binding_freeze_inproc",
        ROOT / "skills/public/achieve/scripts/goal_binding_freeze.py",
    )
    repo = tmp_path / "inproc"
    draft_rel = "charness-artifacts/goals/2026-09-19-inproc.md"
    draft = repo / draft_rel
    draft.parent.mkdir(parents=True)
    draft.write_text("# approved draft\n", encoding="utf-8")
    manifest = tmp_path / "inproc-manifest.json"
    manifest.write_text(json.dumps([_created("a", rank=1)]), encoding="utf-8")
    rc = freeze.main(
        [
            "freeze",
            "--repo-root", str(repo),
            "--draft", draft_rel,
            "--parent-repo", "corca-ai/charness",
            "--parent-number", "724",
            "--briefing-sha256", _sha("briefing"),
            "--approval-response", "approved",
            "--approval-session-id", "session-1",
            "--approval-observed-at", "2026-09-19T00:00:00+09:00",
            "--manifest", str(manifest),
        ]
    )
    assert rc == 0
    assert (repo / "charness-artifacts/goals/2026-09-19-inproc.binding.json").is_file()


def test_observation_link_race_names_new_attempt_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    observation = _load(
        "goal_binding_freeze_observation_race",
        ROOT / "skills/public/issue/scripts/issue_tracker_observation.py",
    )

    def raced_link(src: str, dst: str, *args: object, **kwargs: object) -> None:
        raise FileExistsError("simulated link race")

    monkeypatch.setattr(os, "link", raced_link)
    with pytest.raises(RuntimeError, match="new attempt_id"):
        observation.begin(
            repo_root=tmp_path / "race",
            observation_dir=Path("observations"),
            attempt_id="attempt-race",
            draft_sha256=_sha("d"),
            binding_sha256=_sha("b"),
            repo="corca-ai/charness",
            parent_number=724,
            operation="update-body",
            target={"repo": "corca-ai/charness", "number": 724},
            submitted_body_sha256=None,
            backend={"id": "gh", "binary": "gh"},
        )


def test_freeze_manifest_error_branches_stay_typed(tmp_path: Path) -> None:
    freeze = _load(
        "goal_binding_freeze_manifest_errors",
        ROOT / "skills/public/achieve/scripts/goal_binding_freeze.py",
    )
    with pytest.raises(freeze.BindingError) as exc_info:
        freeze.load_manifest_file(tmp_path / "missing.json")
    assert exc_info.value.code == "input-missing"
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(freeze.BindingError) as exc_info:
        freeze.load_manifest_file(bad)
    assert exc_info.value.code == "input-invalid"
    shape = tmp_path / "shape.json"
    shape.write_text(json.dumps({"kind": "other"}), encoding="utf-8")
    with pytest.raises(freeze.BindingError) as exc_info:
        freeze.load_manifest_file(shape)
    assert exc_info.value.code == "schema-invalid"
    objform = tmp_path / "obj.json"
    objform.write_text(
        json.dumps({"approved_work_items": [_created("a", rank=1)]}), encoding="utf-8"
    )
    assert freeze.load_manifest_file(objform) == [_created("a", rank=1)]


def test_freeze_main_refusal_returns_typed_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    freeze = _load(
        "goal_binding_freeze_main_refusal",
        ROOT / "skills/public/achieve/scripts/goal_binding_freeze.py",
    )
    repo = tmp_path / "refuse"
    repo.mkdir()
    manifest = tmp_path / "refuse-manifest.json"
    manifest.write_text(json.dumps([_created("a", rank=1)]), encoding="utf-8")
    rc = freeze.main(
        [
            "freeze",
            "--repo-root", str(repo),
            "--draft", "charness-artifacts/goals/missing.md",
            "--parent-repo", "corca-ai/charness",
            "--parent-number", "724",
            "--briefing-sha256", _sha("briefing"),
            "--approval-response", "approved",
            "--approval-session-id", "session-1",
            "--approval-observed-at", "2026-09-19T00:00:00+09:00",
            "--manifest", str(manifest),
        ]
    )
    assert rc == 2
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["error_code"] == "draft-missing"


def test_freeze_emit_yaml_without_helper_refuses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    freeze = _load(
        "goal_binding_freeze_emit_errors",
        ROOT / "skills/public/achieve/scripts/goal_binding_freeze.py",
    )
    monkeypatch.setattr(
        importlib.util, "spec_from_file_location", lambda *args, **kwargs: None
    )
    with pytest.raises(RuntimeError, match="yaml_output"):
        freeze.emit_yaml({"ok": True})


def test_freeze_main_non_freeze_command_returns_two(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    freeze = _load(
        "goal_binding_freeze_other_command",
        ROOT / "skills/public/achieve/scripts/goal_binding_freeze.py",
    )

    class _StubParser:
        def parse_args(self, argv: object = None) -> object:
            return SimpleNamespace(command="other")

    monkeypatch.setattr(freeze, "build_freeze_parser", lambda: _StubParser())
    assert freeze.main([]) == 2


def test_freeze_script_guard_invokes_main(monkeypatch: pytest.MonkeyPatch) -> None:
    import runpy

    monkeypatch.setattr(sys, "argv", ["goal_binding_freeze.py", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(
            str(ROOT / "skills/public/achieve/scripts/goal_binding_freeze.py"),
            run_name="__main__",
        )
    assert exc_info.value.code == 0


def test_freeze_module_inserts_sibling_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    sibling = str(ROOT / "skills/public/achieve/scripts")
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != sibling])
    assert sibling not in sys.path
    _load(
        "goal_binding_freeze_path_probe",
        ROOT / "skills/public/achieve/scripts/goal_binding_freeze.py",
    )
    assert sibling in sys.path


def test_observation_reuse_refusal_names_new_attempt_id(tmp_path: Path) -> None:
    observation = _load("goal_binding_freeze_observation", OBSERVATION)
    repo = tmp_path / "repo"
    repo.mkdir()
    started = observation.begin(
        repo_root=repo,
        observation_dir=Path("observations"),
        attempt_id="attempt-1",
        draft_sha256=_sha("d"),
        binding_sha256=_sha("b"),
        repo="corca-ai/charness",
        parent_number=724,
        operation="update-body",
        target={"repo": "corca-ai/charness", "number": 724},
        submitted_body_sha256=None,
        backend={"id": "gh", "binary": "gh"},
    )
    assert started["payload"]["attempt_id"] == "attempt-1"
    try:
        observation.begin(
            repo_root=repo,
            observation_dir=Path("observations"),
            attempt_id="attempt-1",
            draft_sha256=_sha("d"),
            binding_sha256=_sha("b"),
            repo="corca-ai/charness",
            parent_number=724,
            operation="update-body",
            target={"repo": "corca-ai/charness", "number": 724},
            submitted_body_sha256=None,
            backend={"id": "gh", "binary": "gh"},
        )
    except RuntimeError as exc:
        assert "already exists and is immutable" in str(exc)
        assert "new attempt_id" in str(exc)
    else:
        raise AssertionError("reusing an attempt id must refuse")
