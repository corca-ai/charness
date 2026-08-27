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

    assert adapter["valid"] is True
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

    report = policy.interview_policy_report(tmp_path)

    assert report["valid"] is True
    assert report["max_questions"] == 7
    assert report["allow_provisional_local_fallback"] is True
    assert policy.resolve_discussion_deploy_vocab(tmp_path) == ["rollout"]


@pytest.mark.parametrize("value", ["0", "-1", "true", "1.5", "many"])
def test_adapter_rejects_invalid_interview_ceiling(tmp_path: Path, value: str) -> None:
    path = tmp_path / ".agents" / "achieve-adapter.yaml"
    path.parent.mkdir()
    path.write_text(f"version: 1\ninterview:\n  max_questions: {value}\n", encoding="utf-8")

    report = policy.interview_policy_report(tmp_path)

    assert report["valid"] is False
    assert any("interview.max_questions" in error for error in report["errors"])


def test_removed_adapter_sections_are_invalid(tmp_path: Path) -> None:
    path = tmp_path / ".agents" / "achieve-adapter.yaml"
    path.parent.mkdir()
    path.write_text("version: 1\nauto_retro:\n  allow_none_optout: true\n", encoding="utf-8")

    report = policy.load_adapter(tmp_path)

    assert report["valid"] is False
    assert any("unknown field" in error for error in report["errors"])
