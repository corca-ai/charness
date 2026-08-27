from __future__ import annotations

import argparse
import runpy
from pathlib import Path

from tests.quality_gates.support import ROOT, write_issue_adapter_with_backend

PROVIDER_PATH = ROOT / "skills/public/issue/scripts/issue_provider_selection.py"
TOOL_PATH = ROOT / "skills/public/issue/scripts/issue_tool.py"
CONTRACT_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_contract.py"


def test_provider_selection_resolves_target_in_one_call_and_reuses_loaded_adapter(tmp_path: Path) -> None:
    backend = runpy.run_path(str(PROVIDER_PATH))
    write_issue_adapter_with_backend(tmp_path, backend_id="acme", binary="acme")

    resolved = backend["resolve_backend"](tmp_path, target_repo="acme/project")
    assert resolved["adapter_ok"] is True
    assert resolved["backend"]["id"] == "acme"
    assert "provider_selection" not in resolved

    loaded = resolved["adapter"]
    backend["ADAPTER"].load_adapter = lambda _root: (_ for _ in ()).throw(
        AssertionError("an already-loaded adapter must be reusable")
    )
    reused = backend["resolve_backend"](
        tmp_path, target_repo="acme/project", adapter=loaded
    )
    assert reused["adapter"] is loaded
    assert reused["backend"] == resolved["backend"]

    scoped_adapter = {
        "valid": True,
        "data": {
            "issue_backend": {"id": "acme", "binary": "acme", "repo_scoped": "acme/project"}
        },
    }
    try:
        backend["resolve_backend"](tmp_path, target_repo="other/project", adapter=scoped_adapter)
    except RuntimeError as exc:
        assert "scoped" in str(exc)
    else:
        raise AssertionError("a repo-scoped backend must reject a foreign target")


def test_invalid_adapter_refuses_explicit_selection_before_parsing_or_provider_call(
    tmp_path: Path,
) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "issue-adapter.yaml").write_text("version: 999\n", encoding="utf-8")
    tool = runpy.run_path(str(TOOL_PATH))
    tool["RUNTIME"].parse_selector = lambda _value: (_ for _ in ()).throw(
        AssertionError("invalid adapter must refuse before selection")
    )
    emitted: list[dict[str, object]] = []
    tool["command_select"].__globals__["emit"] = emitted.append

    rc = tool["command_select"](
        argparse.Namespace(
            repo_root=tmp_path,
            repo="owner/repo",
            selector="724",
        )
    )

    assert rc == 1
    assert emitted[0]["status"] == "adapter-invalid"
    # Inspect the typed resolver directly for the no-fallback invariant too.
    selected = tool["_resolve_backend"](tmp_path)
    assert selected["adapter_ok"] is False
    assert "provider_selection" not in selected


def test_goal_run_capability_probe_uses_bound_target_not_placeholder_repo() -> None:
    contract = runpy.run_path(str(CONTRACT_PATH))
    backend = {
        "id": "acme",
        "binary": "acme",
        "repo_scoped": "acme/project",
        "commands": {"view": ["view", "{repo}", "{number}", "{json_fields}"]},
    }
    seen: list[str] = []
    original_resolve_op = contract["BACKEND"].resolve_op

    def capture_repo(*_args: object, **kwargs: str) -> list[str]:
        seen.append(kwargs["repo"])
        return ["acme", "view"]

    contract["BACKEND"].resolve_op = capture_repo
    try:
        ready = contract["capability_report"](backend, ["read-body"], repo="acme/project")
    finally:
        contract["BACKEND"].resolve_op = original_resolve_op
    wrong_target = contract["capability_report"](backend, ["read-body"], repo="other/project")

    assert ready["ok"] is True
    assert ready["probe_repo"] == "acme/project"
    assert seen == ["acme/project"]
    assert wrong_target["ok"] is True
    assert wrong_target["probe_repo"] == "other/project"
