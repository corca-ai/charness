from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/achieve_adapter_policy.py"
spec = importlib.util.spec_from_file_location("achieve_adapter_policy", SCRIPT)
policy = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(policy)


def test_missing_adapter_uses_planning_defaults(tmp_path: Path) -> None:
    adapter = policy.load_adapter(tmp_path)

    searched_path = str((tmp_path / ".agents" / "achieve-adapter.yaml").resolve())
    assert adapter["state"] == "absent"
    assert adapter["valid"] is True
    assert adapter["searched_paths"] == [searched_path]
    assert adapter["next_step"] == f"Create `{searched_path}` to configure this adapter, then rerun."
    assert adapter["data"]["interview"]["max_questions"] == 15
    assert "closeout_publication" not in adapter["data"]
    assert "auto_retro" not in adapter["data"]
    assert "scaffold" not in adapter["data"]


def test_adapter_accepts_interview_and_discussion_policy(tmp_path: Path) -> None:
    path = tmp_path / ".agents" / "achieve-adapter.yaml"
    path.parent.mkdir()
    path.write_text(
        "version: 1\n"
        "discussion_deploy_vocab:\n  - rollout\n"
        "interview:\n  max_questions: 7\n  allow_provisional_local_fallback: true\n",
        encoding="utf-8",
    )

    adapter = policy.load_adapter(tmp_path)
    report = policy.interview_policy_report(tmp_path)

    assert adapter["state"] == "configured"
    assert report["valid"] is True
    assert adapter["next_step"] is None
    assert adapter["searched_paths"] == [str(path.resolve())]
    assert report["max_questions"] == 7
    assert report["allow_provisional_local_fallback"] is True
    assert policy.resolve_discussion_deploy_vocab(tmp_path) == ["rollout"]


@pytest.mark.parametrize("value", ["0", "-1", "true", "1.5", "many"])
def test_adapter_rejects_invalid_interview_ceiling(tmp_path: Path, value: str) -> None:
    path = tmp_path / ".agents" / "achieve-adapter.yaml"
    path.parent.mkdir()
    path.write_text(f"version: 1\ninterview:\n  max_questions: {value}\n", encoding="utf-8")

    report = policy.interview_policy_report(tmp_path)
    adapter = policy.load_adapter(tmp_path)

    assert adapter["state"] == "invalid"
    assert report["valid"] is False
    assert adapter["next_step"] == f"Repair `{path}` and rerun the adapter resolver."
    assert any("interview.max_questions" in error for error in report["errors"])


def test_removed_adapter_sections_are_invalid(tmp_path: Path) -> None:
    path = tmp_path / ".agents" / "achieve-adapter.yaml"
    path.parent.mkdir()
    path.write_text("version: 1\nauto_retro:\n  allow_none_optout: true\n", encoding="utf-8")

    report = policy.load_adapter(tmp_path)

    assert report["state"] == "invalid"
    assert report["valid"] is False
    assert any("unknown field" in error for error in report["errors"])


def test_unparseable_adapter_is_unestablished(tmp_path: Path) -> None:
    path = tmp_path / ".agents" / "achieve-adapter.yaml"
    path.parent.mkdir()
    path.write_text("version: 1\ninterview:\n  max_questions: !!int 7\n", encoding="utf-8")

    adapter = policy.load_adapter(tmp_path)

    assert adapter["state"] == "unestablished"
    assert adapter["valid"] is False
    assert any("adapter could not be parsed" in error for error in adapter["errors"])
    assert adapter["next_step"] == f"Fix `{path}` so its adapter state can be established, then rerun."


def test_unreadable_adapter_is_unestablished(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / ".agents" / "achieve-adapter.yaml"
    path.parent.mkdir()
    path.write_text("version: 1\n", encoding="utf-8")

    def read_unreadable(_path: Path) -> tuple[dict[str, object], list[str], list[str]]:
        return {}, ["adapter could not be read: permission denied"], []

    monkeypatch.setattr(policy._adapter_lib, "read_declared_adapter", read_unreadable)

    adapter = policy.load_adapter(tmp_path)

    assert adapter["state"] == "unestablished"
    assert adapter["valid"] is False
    assert adapter["errors"] == ["adapter could not be read: permission denied"]
    assert adapter["next_step"] == f"Fix `{path}` so its adapter state can be established, then rerun."
