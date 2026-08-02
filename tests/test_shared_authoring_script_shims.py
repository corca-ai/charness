"""An authoring-repo script must be reachable by ONE path in BOTH layouts (#477, #478).

`<repo>/scripts/X.py` and `<plugin-root>/scripts/X.py` sit at different depths
from a skill package — three levels up versus two — so no single
`$SKILL_DIR/../../../` count reaches both. `impl`/`spec` used the three-level
form, so the risk-interrupt planner resolved in the authoring tree and nowhere
else, silently, behind `2>/dev/null || true`.

`$SKILL_DIR/../../shared/scripts/` is the one prefix at equal depth in both.
These tests pin the shared resolution logic, every shim built on it, and the
prose that names them.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.script_main import load_script_module

REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPTS = REPO_ROOT / "skills" / "shared" / "scripts"
MIRROR_SCRIPTS = REPO_ROOT / "plugins" / "charness" / "shared" / "scripts"

shim_lib = load_script_module("authoring_script_shim", SHARED_SCRIPTS / "authoring_script_shim.py")

# Every shim, and the call site whose prose must name it.
SHIMS = {
    "plan_risk_interrupt.py": (
        REPO_ROOT / "skills" / "public" / "impl" / "SKILL.md",
        REPO_ROOT / "skills" / "public" / "spec" / "SKILL.md",
    ),
    "check_title_slug_drift.py": (
        REPO_ROOT / "skills" / "public" / "critique" / "references" / "angle-selection.md",
        REPO_ROOT / "skills" / "public" / "critique" / "references" / "rename-critique.md",
    ),
    "validate_skills.py": (
        REPO_ROOT / "skills" / "shared" / "references" / "binary-preflight.md",
    ),
}


@pytest.mark.parametrize("name", sorted(SHIMS))
def test_the_shim_does_not_find_itself(name: str) -> None:
    """`skills/shared/scripts/<name>` IS an `<ancestor>/scripts/<name>`.

    An unguarded ancestor walk resolves to the shim itself and recurses until
    the interpreter dies — which is exactly what the first version did.
    """
    caller = SHARED_SCRIPTS / name
    located = shim_lib.locate(name, caller)
    assert located.resolve() != caller.resolve()
    assert located.resolve() == (REPO_ROOT / "scripts" / name).resolve()


def test_locate_raises_rather_than_returning_none_when_nothing_is_there(tmp_path: Path) -> None:
    stranded = tmp_path / "a" / "b" / "ghost.py"
    stranded.parent.mkdir(parents=True)
    stranded.write_text("", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        shim_lib.locate("ghost.py", stranded)


@pytest.mark.parametrize("name", sorted(SHIMS))
@pytest.mark.parametrize(
    "scripts_dir",
    [pytest.param(SHARED_SCRIPTS, id="authoring"), pytest.param(MIRROR_SCRIPTS, id="shipped")],
)
def test_every_shim_answers_help_in_both_layouts(name: str, scripts_dir: Path) -> None:
    """The claim the old path could not make: one spelling, both trees.

    `--help` is the invocation every shim's target accepts regardless of its own
    option surface, so this proves the locate+load chain end to end without
    encoding each target's arguments.
    """
    shim = scripts_dir / name
    assert shim.is_file(), f"{shim} missing; the mirror is out of sync"

    result = subprocess.run(
        [sys.executable, str(shim), "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.lower()


def test_the_planner_shim_degrades_gracefully_where_no_debug_artifact_exists(tmp_path: Path) -> None:
    """A consuming repo's shape: the command must run, not just resolve."""
    (tmp_path / ".agents").mkdir()
    result = subprocess.run(
        [
            sys.executable,
            str(MIRROR_SCRIPTS / "plan_risk_interrupt.py"),
            "--repo-root",
            str(tmp_path),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "not-applicable"


@pytest.mark.parametrize("name", sorted(SHIMS))
def test_the_call_sites_name_a_path_that_resolves_in_both_layouts(name: str) -> None:
    """No `../../../scripts`, and no swallow hiding a real verdict.

    The planner returns 1 when it blocks; `2>/dev/null || true` discarded both
    that signal and the file-not-found that preceded it.
    """
    for call_site in SHIMS[name]:
        text = call_site.read_text(encoding="utf-8")
        # Only lines carrying a PATH are constrained. A doc may legitimately
        # mention the script by bare name ("`check_title_slug_drift.py` output"),
        # and requiring a prefix there would be a manufactured finding.
        pathed = [line for line in text.splitlines() if f"scripts/{name}" in line]
        assert pathed, f"{call_site}: no longer names a path to {name}"
        for line in pathed:
            assert "$SKILL_DIR/../../shared/scripts/" in line, line
            assert "../../../" not in line, line
            assert "|| true" not in line, f"{call_site}: swallow hides a real verdict"
