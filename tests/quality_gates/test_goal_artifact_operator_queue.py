from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_OPERATOR_QUEUE = (
    Path(__file__).resolve().parents[2]
    / "skills/public/achieve/scripts/goal_artifact_operator_queue.py"
)
_spec = importlib.util.spec_from_file_location("goal_artifact_operator_queue", _OPERATOR_QUEUE)
oq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oq)


def test_operator_queue_loader_fails_when_markdown_helper_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(oq.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None)

    with pytest.raises(ImportError, match="goal_artifact_markdown.py not found"):
        oq._load_markdown()


def test_operator_queue_invalid_created_date_still_applies() -> None:
    assert oq.applies("Created: 2026-99-99\n") is True


def test_operator_queue_blank_heading_body_fails() -> None:
    result = oq.check("Created: 2026-06-17\n\n## Operator Decision Queue")

    assert result == {
        "applies": True,
        "ok": False,
        "reason": "queue section is blank",
    }


def test_operator_queue_unrecognized_body_fails_with_actionable_reason() -> None:
    result = oq.check("Created: 2026-06-17\n\n## Operator Decision Queue\n\nNeeds follow-up.\n")

    assert result == {
        "applies": True,
        "ok": False,
        "reason": "queue needs `none — <reason>` or at least one `Decision:` item",
    }
