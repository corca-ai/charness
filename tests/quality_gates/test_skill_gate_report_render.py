"""Direct cover for the shared skill-gate report renderer.

This module is the one #467's blocking signal named
(`scripts/core/skill_gate_report_render.py:31`, `blocked = status == "blocked"`), and
it had no test of any kind. Both production callers
(`check_skill_surface_preflight.py`, `skill_issue_anchor_scan.py`) pass `blocked`
explicitly, so the default-derivation branch is unreachable through either of
them — it is public API exercised only by a direct call, which is exactly the
shape a changed-line gate flags and a caller-driven test suite never covers.
"""
from __future__ import annotations

import importlib.util

from .support import ROOT

MODULE_PATH = ROOT / "scripts" / "core" / "skill_gate_report_render.py"


def _render():
    spec = importlib.util.spec_from_file_location("skill_gate_report_render", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_gate_report


def test_status_blocked_derives_the_remediation_without_being_told() -> None:
    """The default branch: omit `blocked`, and `status` decides."""
    out = _render()(
        "skill-anchor-scan",
        "blocked",
        ["a/skill.md: 1 anchor(s)"],
        blocked_message="remove the anchor before committing",
    )

    assert out.splitlines() == [
        "skill-anchor-scan: blocked",
        "a/skill.md: 1 anchor(s)",
        "remove the anchor before committing",
    ]


def test_a_non_blocked_status_derives_no_remediation() -> None:
    out = _render()(
        "skill-anchor-scan",
        "ok",
        ["a/skill.md: 0 anchor(s)"],
        blocked_message="remove the anchor before committing",
    )

    assert out.splitlines() == ["skill-anchor-scan: ok", "a/skill.md: 0 anchor(s)"]


def test_an_explicit_blocked_overrides_an_unrecognized_status() -> None:
    """The reason the parameter exists, stated in the module's own docstring: a
    caller whose vocabulary is not `blocked` would otherwise print a failure with
    no way out, because the string compare silently drops the remediation."""
    out = _render()(
        "skill-surface-preflight",
        "refused",
        ["a/skill.md: over budget"],
        blocked_message="split the concept before committing",
        blocked=True,
    )

    assert out.splitlines()[-1] == "split the concept before committing"


def test_an_explicit_false_suppresses_it_even_when_status_says_blocked() -> None:
    """The other direction of the override, so the parameter is pinned as a real
    override rather than an OR with the status compare."""
    out = _render()(
        "skill-surface-preflight",
        "blocked",
        ["a/skill.md: advisory only"],
        blocked_message="split the concept before committing",
        blocked=False,
    )

    assert out.splitlines() == ["skill-surface-preflight: blocked", "a/skill.md: advisory only"]


def test_rows_are_consumed_from_any_iterable_not_just_a_list() -> None:
    """The signature takes `Iterable[str]`; a generator is the ordinary caller
    shape and would break on a second pass over the rows."""
    out = _render()(
        "skill-anchor-scan",
        "ok",
        (f"row {index}" for index in range(2)),
        blocked_message="unused",
    )

    assert out.splitlines() == ["skill-anchor-scan: ok", "row 0", "row 1"]
