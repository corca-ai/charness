"""Direct counterexamples for rare reviewer-consumer branches.

The exact-base changed-line gate found these paths after the broad suite passed.
Keep the probes at the owning helpers so a future refactor cannot hide a refusal
behind a successful aggregate closeout.
"""

from __future__ import annotations

import importlib
import importlib.util
import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]


def _load(relative: str, name: str):
    return load_script_module(name, ROOT / relative)


CRITIQUE_EVIDENCE_PATH = ROOT / "scripts/review/critique_reviewer_evidence.py"
CRITIQUE_EVIDENCE = _load("scripts/review/critique_reviewer_evidence.py", "gaps_critique_evidence")
OBSERVER_PATH = ROOT / "skills/public/issue/scripts/issue_critique_observer.py"
OBSERVER = _load("skills/public/issue/scripts/issue_critique_observer.py", "gaps_observer")
OBSERVER_SUPPORT = _load(
    "skills/public/issue/scripts/issue_critique_observer_support.py", "gaps_observer_support"
)
MARKDOWN = _load("skills/public/issue/scripts/issue_markdown_lib.py", "gaps_markdown")
RESOLUTION_PATH = ROOT / "skills/public/issue/scripts/issue_resolution_critique.py"
RESOLUTION = _load("skills/public/issue/scripts/issue_resolution_critique.py", "gaps_resolution")
RESOLUTION_OBSERVER = _load(
    "skills/public/issue/scripts/issue_resolution_observer.py", "gaps_resolution_observer"
)


def test_typed_closeout_reads_the_canonical_critique_tier_shape() -> None:
    assert RESOLUTION_OBSERVER._TYPED_TIER_FIELDS == CRITIQUE_EVIDENCE.TYPED_REVIEWER_TIER_FIELDS
    assert CRITIQUE_EVIDENCE.REVIEWER_EXECUTION_MODE_VALUES == (
        "file-backed-worker",
        "typed-subagent",
    )


def test_reviewer_tier_validator_rejects_unknown_execution_mode() -> None:
    fields = {
        "requested tier": "high-leverage",
        "requested spawn fields": "typed bounded reviewer",
        "host exposure state": "host-defaulted",
        "application state": "n/a",
        "execution mode": "unknown",
    }
    with pytest.raises(CRITIQUE_EVIDENCE.ValidationError, match="execution mode"):
        CRITIQUE_EVIDENCE.validate_reviewer_tier_evidence(
            Path("critique.md"),
            "",
            section_field_map=lambda _text, _heading: fields,
        )


def test_worker_loader_refuses_when_every_candidate_has_no_loader(monkeypatch) -> None:
    monkeypatch.setattr(
        CRITIQUE_EVIDENCE.importlib.util,
        "spec_from_file_location",
        lambda *args, **kwargs: SimpleNamespace(loader=None),
    )
    with pytest.raises(ImportError, match="reviewer_worker_carrier.py not found"):
        CRITIQUE_EVIDENCE._load_worker_carrier()


def test_observer_loader_reports_no_carrier_when_specs_have_no_loader(monkeypatch) -> None:
    monkeypatch.setattr(
        OBSERVER.importlib.util,
        "spec_from_file_location",
        lambda *args, **kwargs: SimpleNamespace(loader=None),
    )
    assert OBSERVER._load_worker_carrier() is None


def test_top_level_support_loader_failure_is_typed(monkeypatch) -> None:
    original = importlib.util.spec_from_file_location

    def reject_support(name, location, *args, **kwargs):
        if Path(location).name == "issue_critique_observer_support.py":
            return SimpleNamespace(loader=None)
        return original(name, location, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "spec_from_file_location", reject_support)
    with pytest.raises(ImportError, match="issue critique observer support is unavailable"):
        runpy.run_path(str(OBSERVER_PATH))


def test_observer_fence_and_indented_code_paths_fail_closed() -> None:
    assert OBSERVER._strip_fenced_lines("    hidden\n\nvisible") == ["visible"]
    assert OBSERVER._strip_fenced_lines("```md\nhidden\n```\nvisible") == ["visible"]


def test_worker_carrier_unavailable_is_not_a_delegated_verdict(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(OBSERVER, "_worker_carrier", None)
    result = OBSERVER._worker_carrier_disposition(tmp_path, "worker-delivered")
    assert result["disposition"] == "carrier-unverified"
    assert result["carrier_verified"] is False


def test_round_cap_is_non_approval_even_when_it_contains_delegated_words() -> None:
    result = OBSERVER.observer_disposition(
        "Fresh-eye satisfaction: accepted-unreviewed-under-round-cap\n",
        strip_code_fences=MARKDOWN.strip_code_fences,
    )
    assert result["disposition"] == "round-cap-unreviewed"


def test_observer_support_skips_indented_and_fenced_examples() -> None:
    normalized = OBSERVER_SUPPORT._normalize_contract_text(
        "    hidden\n\nvisible\n```md\nexample\n```\n"
    )
    assert "hidden" not in normalized
    assert "visible" in normalized
    assert "example" not in normalized


def test_current_tracked_date_is_not_grandfathered(monkeypatch, tmp_path: Path) -> None:
    def fake_run(argv, **kwargs):
        if argv[1] == "ls-files":
            return SimpleNamespace(stdout="tracked.md")
        return SimpleNamespace(stdout="2026-08-21T00:00:00+00:00")

    monkeypatch.setattr(OBSERVER_SUPPORT.subprocess, "run", fake_run)
    assert OBSERVER_SUPPORT._tracked_before_rule(tmp_path / "tracked.md", tmp_path) is False


def test_over_indented_markdown_closer_is_not_a_closer() -> None:
    assert MARKDOWN._closing_fence("    ```", "```") is False


def test_resolution_loader_and_typed_evidence_refusals_are_explicit(monkeypatch, tmp_path: Path) -> None:
    class EmptyPath:
        @property
        def parents(self):
            return ()

        def resolve(self):
            return self

    with monkeypatch.context() as patch:
        patch.setattr(RESOLUTION_OBSERVER, "Path", lambda _: EmptyPath())
        with pytest.raises(ImportError, match="check_prescribed_skill_executed_lib.py not found"):
            RESOLUTION_OBSERVER._load_shared_helper()

    base = {
        "requested tier": "high-leverage",
        "requested spawn fields": "typed bounded reviewer",
        "host exposure state": "host-defaulted",
        "application state": "n/a",
        "delivery state": "findings-received",
        "execution mode": "typed-subagent",
    }

    def evidence(**changes: str) -> str:
        fields = {**base, **changes}
        return "\n".join(
            [
                "## Reviewer Tier Evidence",
                *[f"- {key.title()}: {value}" for key, value in fields.items()],
                "",
            ]
        )

    assert "missing fields" in RESOLUTION_OBSERVER._typed_delegation_error(
        "## Reviewer Tier Evidence\n"
    )
    assert "placeholders" in RESOLUTION_OBSERVER._typed_delegation_error(
        evidence(**{"requested tier": "TODO"})
    )
    assert "execution mode" in RESOLUTION_OBSERVER._typed_delegation_error(
        evidence(**{"execution mode": "manual"})
    )
    assert "host exposure state" in RESOLUTION_OBSERVER._typed_delegation_error(
        evidence(**{"host exposure state": "unknown"})
    )
    assert "delivery state" in RESOLUTION_OBSERVER._typed_delegation_error(
        evidence(**{"delivery state": "unknown-delivery"})
    )
    assert "host-confirmed" in RESOLUTION_OBSERVER._typed_delegation_error(
        evidence(**{"host exposure state": "applied", "application state": "applied"})
    )

    cited = tmp_path / "critique.md"
    cited.write_text(
        "Fresh-eye satisfaction: parent-delegated\n\n" + evidence(**{"requested tier": "TODO"}),
        encoding="utf-8",
    )
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(cited)}]}
    result = RESOLUTION_OBSERVER._observer_disposition(tmp_path, check)
    assert result["disposition"] == "delegation-unverified"
    assert "tier_reason" in result


def test_critique_shape_loader_reports_missing_module(monkeypatch) -> None:
    class EmptyPath:
        @property
        def parents(self):
            return ()

        def resolve(self):
            return self

    monkeypatch.setattr(RESOLUTION_OBSERVER, "Path", lambda _: EmptyPath())
    with pytest.raises(ImportError, match="critique_reviewer_evidence.py not found"):
        RESOLUTION_OBSERVER._load_critique_shape()


def test_resolution_critique_refuses_when_observer_support_spec_has_no_loader(monkeypatch) -> None:
    original = importlib.util.spec_from_file_location

    def reject_resolution_observer(name, location, *args, **kwargs):
        if Path(location).name == "issue_resolution_observer.py":
            return SimpleNamespace(loader=None)
        return original(name, location, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "spec_from_file_location", reject_resolution_observer)
    with pytest.raises(ImportError, match="issue resolution observer support is unavailable"):
        runpy.run_path(str(RESOLUTION_PATH))
