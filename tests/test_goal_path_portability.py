from __future__ import annotations

import importlib.util
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve().parents[1] / "skills/public/achieve/scripts/goal_path_portability.py"
_SPEC = importlib.util.spec_from_file_location("goal_path_portability", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
portability = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(portability)


def test_executable_checkout_root_requires_explicit_disposition() -> None:
    report = portability.check_goal_path_portability(
        "## Agent Verification Plan\n"
        "Run python3 /home/hwidong/codes/ceal-cli/scripts/check.py\n"
    )

    assert report["ok"] is False
    assert report["disposition"]["present"] is False
    assert report["executable_paths"][0]["path"] == "/home/hwidong/codes/ceal-cli/scripts/check.py"
    assert report["executable_paths"][0]["kind"] == "executable"


def test_valid_machine_bound_disposition_closes_the_refusal() -> None:
    report = portability.check_goal_path_portability(
        "## Agent Verification Plan\n"
        "Run python3 /home/hwidong/codes/ceal-cli/scripts/check.py\n"
        "Path portability disposition: machine-bound — this goal runs only in the declared Worker checkout\n"
    )

    assert report["ok"] is True
    assert report["disposition"]["status"] == "machine-bound"
    assert report["disposition"]["reason"].startswith("this goal runs")


def test_historical_evidence_is_reported_without_failing_the_goal() -> None:
    report = portability.check_goal_path_portability(
        "## Final Verification\n"
        "Historical evidence: /home/hwidong/codes/ceal-agent was absent on the source host.\n"
    )

    assert report["ok"] is True
    assert report["executable_paths"] == []
    assert report["intentional_evidence"][0]["kind"] == "intentional-evidence"


def test_ambiguous_checkout_root_also_requires_a_disposition() -> None:
    report = portability.check_goal_path_portability(
        "## Non-Goals\n"
        "The cross-repository boundary is /Users/ted/codes/ceal-cli.\n"
    )

    assert report["ok"] is False
    assert report["executable_paths"][0]["kind"] == "ambiguous"


def test_non_checkout_absolute_paths_and_urls_are_not_findings() -> None:
    report = portability.check_goal_path_portability(
        "## Goal\n"
        "Use /tmp/fixture and /usr/bin/python; documentation lives at https://example.test/a.\n"
    )

    assert report["ok"] is True
    assert report["references"] == []


def test_placeholder_or_unknown_disposition_does_not_clear_a_finding() -> None:
    for disposition in (
        "Path portability disposition: TODO",
        "Path portability disposition: maybe later — <reason>",
    ):
        report = portability.check_goal_path_portability(
            "## Goal\n"
            "Use /home/hwidong/codes/ceal-cli.\n"
            + disposition
            + "\n"
        )
        assert report["ok"] is False
        assert report["disposition"]["present"] is True


def test_windows_checkout_root_uses_the_same_classifier() -> None:
    report = portability.check_goal_path_portability(
        "## User Acceptance\n"
        r"Run C:\Users\ted\worktrees\ceal-cli\check.py."
        "\nPath portability disposition: rewritten — use the logical sibling root at runtime\n"
    )

    assert report["ok"] is True
    assert report["executable_paths"][0]["path"] == r"C:\Users\ted\worktrees\ceal-cli\check.py"
