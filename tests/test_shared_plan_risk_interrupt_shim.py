"""The risk-interrupt planner must be reachable by ONE path in BOTH layouts (#477).

`impl`/`spec` invoked it as `$SKILL_DIR/../../../scripts/plan_risk_interrupt.py`.
Three levels up reaches the repo root from `skills/public/<skill>` and overshoots
from `plugins/<pkg>/skills/<skill>`, so the command resolved in the authoring tree
and nowhere else — silently, because both call sites ended in `2>/dev/null || true`.
The planner had therefore never run in an installed plugin.

These tests pin the shim that removes the layout ambiguity, and pin that the
prose now names a path resolving in both trees.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.script_main import load_script_module

REPO_ROOT = Path(__file__).resolve().parents[1]
SHIM_PATH = REPO_ROOT / "skills" / "shared" / "scripts" / "plan_risk_interrupt.py"
MIRROR_SHIM_PATH = REPO_ROOT / "plugins" / "charness" / "shared" / "scripts" / "plan_risk_interrupt.py"

shim = load_script_module("shared_plan_risk_interrupt_shim", SHIM_PATH)

CALL_SITES = (
    REPO_ROOT / "skills" / "public" / "impl" / "SKILL.md",
    REPO_ROOT / "skills" / "public" / "spec" / "SKILL.md",
)


def test_the_shim_does_not_find_itself() -> None:
    """`skills/shared` + `scripts/<name>` IS the shim.

    An unguarded ancestor walk resolves to this file and recurses until the
    interpreter dies — which is exactly what the first version did.
    """
    located = shim.locate_planner()
    assert located.resolve() != SHIM_PATH.resolve()
    assert located.name == shim.PLANNER_NAME
    assert located.is_file()


def test_the_shim_reaches_the_repo_level_planner() -> None:
    assert shim.locate_planner().resolve() == (REPO_ROOT / "scripts" / shim.PLANNER_NAME).resolve()


def test_locate_raises_rather_than_returning_none_when_nothing_is_there(tmp_path: Path) -> None:
    stranded = tmp_path / "a" / "b" / "plan_risk_interrupt.py"
    stranded.parent.mkdir(parents=True)
    stranded.write_text("", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        shim.locate_planner(stranded)


@pytest.mark.parametrize(
    "shim_path",
    [
        pytest.param(SHIM_PATH, id="authoring"),
        pytest.param(MIRROR_SHIM_PATH, id="shipped"),
    ],
)
def test_the_shim_runs_in_both_layouts(shim_path: Path, tmp_path: Path) -> None:
    """The claim the old path could not make: one spelling, both trees.

    Run as a subprocess against a repo with no debug artifact — the shape a
    consuming repo presents — so a degrade is proven to be graceful rather than
    assumed.
    """
    assert shim_path.is_file(), f"{shim_path} missing; the mirror is out of sync"
    (tmp_path / ".agents").mkdir()

    result = subprocess.run(
        [sys.executable, str(shim_path), "--repo-root", str(tmp_path), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "not-applicable"


def test_the_call_sites_name_a_path_that_resolves_in_both_layouts() -> None:
    """No `../../../scripts`, and no swallow hiding the planner's verdict.

    The planner returns 1 when it blocks; `2>/dev/null || true` discarded both
    that signal and the file-not-found that preceded it.
    """
    for call_site in CALL_SITES:
        text = call_site.read_text(encoding="utf-8")
        invocations = [line for line in text.splitlines() if shim.PLANNER_NAME in line]
        assert len(invocations) == 1, f"{call_site}: expected exactly one invocation"
        line = invocations[0]
        assert "$SKILL_DIR/../../shared/scripts/" in line, line
        assert "../../../" not in line, line
        assert "|| true" not in line, f"{call_site}: swallow hides a real block verdict"
        assert "2>/dev/null" not in line, line
