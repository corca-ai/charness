from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_PATH = ROOT / "skills/public/achieve/scripts/goal_artifact_closeout_plan.py"
_SPEC = importlib.util.spec_from_file_location("goal_closeout_plan_under_test", _PATH)
assert _SPEC is not None and _SPEC.loader is not None
plan = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(plan)


def _body(*, heading: str = "## Closeout Binding Plan", fields: str | None = None) -> str:
    values = fields or "".join(f"- {field} value\n" for field in plan.CLOSEOUT_PLAN_FIELDS)
    return f"# Goal\n\nStatus: draft — shaped\n\n{heading}\n{values}"


def test_typed_plan_reads_the_canonical_fields() -> None:
    result = plan.parse_closeout_plan(_body())

    assert isinstance(result, plan.CloseoutPlan)
    assert result.complete is True
    assert result.missing_fields == ()
    assert dict(result.values)["Reviewed inputs:"] == "value"


def test_typed_plan_reports_missing_fields() -> None:
    result = plan.parse_closeout_plan(_body(fields="- Reviewed inputs: value\n"))

    assert result.complete is False
    assert result.missing_fields == tuple(plan.CLOSEOUT_PLAN_FIELDS[1:])


def test_typed_plan_rejects_duplicate_field_labels() -> None:
    body = _body(fields="- Reviewed inputs: packet.json\n" + "".join(
        f"- {field} value\n" for field in plan.CLOSEOUT_PLAN_FIELDS[1:]
    )).replace(
        "- Reviewed inputs: packet.json",
        "- Reviewed inputs: packet.json\n- Reviewed inputs: other-packet.json",
    )
    result = plan.parse_closeout_plan(body)
    assert result.duplicate is True
    assert result.complete is False


def test_typed_plan_reports_duplicate_headings() -> None:
    result = plan.parse_closeout_plan(_body() + "\n" + _body().split("# Goal\n\n", 1)[1])

    assert result.duplicate is True
    assert result.complete is False


def test_typed_plan_ignores_fenced_heading_and_fields() -> None:
    fenced = "# Goal\n\nStatus: draft — shaped\n\n```md\n" + _body().split("\n\n", 1)[1] + "```\n"
    result = plan.parse_closeout_plan(fenced)

    assert result.present is False
    assert result.missing_fields == ()
    assert result.complete is False
