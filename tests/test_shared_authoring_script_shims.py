"""An authoring-repo script must be reachable by ONE path in BOTH layouts (#477, #478).

`<repo>/scripts/X.py` and `<plugin-root>/scripts/X.py` sit at different depths
from a skill package — three levels up versus two — so no single
`$SKILL_DIR/../../../` count reaches both. The spec skill once used the
three-level form, so the risk-interrupt planner resolved in the authoring tree
and nowhere else, silently, behind `2>/dev/null || true`.

`$SKILL_DIR/../../shared/scripts/` is the one prefix at equal depth in both.
These tests pin the shared resolution logic, every shim built on it, and the
prose that names them.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.script_main import load_script_module

REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_SCRIPTS = REPO_ROOT / "skills" / "shared" / "scripts"
MIRROR_SCRIPTS = REPO_ROOT / "plugins" / "charness" / "shared" / "scripts"

shim_lib = load_script_module("authoring_script_shim", SHARED_SCRIPTS / "authoring_script_shim.py")
# The MIRROR's own copy, loaded separately. Running the authoring module against
# a mirror path would not notice the two diverging (a different `_MAX_ANCESTORS`,
# say) — and "the shipped copy behaves like the source" is the claim.
mirror_shim_lib = load_script_module(
    "mirror_authoring_script_shim", MIRROR_SCRIPTS / "authoring_script_shim.py"
)

# Every shim, and the call site whose prose must name it.
SHIMS = {
    "plan_risk_interrupt.py": (
        REPO_ROOT / "skills" / "public" / "spec" / "SKILL.md",
    ),
    "validate_skills.py": (
        REPO_ROOT / "skills" / "shared" / "references" / "binary-preflight.md",
    ),
}


@pytest.mark.parametrize("name", sorted(SHIMS))
@pytest.mark.parametrize(
    ("scripts_dir", "expected_target_dir"),
    [
        pytest.param(SHARED_SCRIPTS, REPO_ROOT / "scripts", id="authoring"),
        pytest.param(
            MIRROR_SCRIPTS, REPO_ROOT / "plugins" / "charness" / "scripts", id="shipped"
        ),
    ],
)
def test_each_shim_resolves_to_its_OWN_tree(
    name: str, scripts_dir: Path, expected_target_dir: Path
) -> None:
    """The #477 class, one level up: WHICH target did the walk find?

    `--help` passes for either resolution, because both trees live under this
    repo. So a mirror shim silently falling through to the AUTHORING target
    would look green here and be broken in every real install, where the
    authoring tree is not an ancestor. Assert the tree, not just success.

    Also pins the self-skip: `<tier>/scripts/<name>` is itself an
    `<ancestor>/scripts/<name>`, so an unguarded walk finds itself and recurses
    until the interpreter dies — which is what the first version did.
    """
    caller = scripts_dir / name
    lib = shim_lib if scripts_dir == SHARED_SCRIPTS else mirror_shim_lib
    assert lib._MAX_ANCESTORS == shim_lib._MAX_ANCESTORS, "mirror shim logic drifted from source"
    located = lib.locate(name, caller)
    assert located.resolve() != caller.resolve()
    assert located.resolve() == (expected_target_dir / name).resolve()


def test_the_walk_is_bounded_and_cannot_reach_an_unrelated_scripts_dir(tmp_path: Path) -> None:
    """An unbounded walk would EXECUTE a consumer's own `validate_skills.py`.

    Failing closed is the required behaviour: a plausible basename collision in
    someone else's tree must raise, not run their file.
    """
    outsider = tmp_path / "scripts"
    outsider.mkdir()
    (outsider / "validate_skills.py").write_text("print('not ours')\n", encoding="utf-8")
    # Depth chosen to PIN the bound, not merely to prove one exists: the outsider
    # sits at ancestor index 5, so this refuses at the shipped cap and would find
    # it at 6. An earlier fixture buried it at index 7 and stayed green for any
    # cap up to 7 — it could not see a 5→7 loosening, which is the regression the
    # cap exists to stop.
    deep = tmp_path / "x1" / "x2" / "x3" / "shared" / "scripts"
    deep.mkdir(parents=True)
    caller = deep / "validate_skills.py"
    caller.write_text("", encoding="utf-8")
    assert list(caller.resolve().parents).index(tmp_path.resolve()) == 5

    with pytest.raises(FileNotFoundError):
        shim_lib.locate("validate_skills.py", caller)


@pytest.mark.boundary_contract(
    reason="the shim must preserve the target's __main__ error and exit contract"
)
def test_a_failing_target_reports_its_own_verdict_not_a_traceback(tmp_path: Path) -> None:
    """Two targets put their ERROR HANDLING in the `__main__` guard.

    Importing and calling `main()` leaves that guard false, so a failing
    validation reached the operator as a traceback with the reason buried at the
    bottom — on the exact path `binary-preflight.md` step 5 exists to serve.
    `runpy` runs the guard, so the shim inherits the target's entry contract.
    """
    package = tmp_path / "skills" / "public" / "broken"
    package.mkdir(parents=True)
    (package / "SKILL.md").write_text("---\nname: broken\n---\n\n# Broken\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SHARED_SCRIPTS / "validate_skills.py"), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "Traceback" not in result.stderr, result.stderr
    assert "missing field" in (result.stdout + result.stderr)


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
@pytest.mark.boundary_contract(
    reason="shim help is a standalone __main__ dispatch smoke in both layouts"
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


@pytest.mark.boundary_contract(
    reason="the planner shim must run as the installed standalone command"
)
def test_the_planner_shim_degrades_gracefully_where_no_debug_artifact_exists(tmp_path: Path) -> None:
    """A consuming repo's shape: the command must run, not just resolve."""
    (tmp_path / ".agents").mkdir()
    result = subprocess.run(
        [
            sys.executable,
            str(MIRROR_SCRIPTS / "plan_risk_interrupt.py"),
            "--repo-root",
            str(tmp_path),
            "--detail",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "not-applicable"


@pytest.mark.parametrize("name", sorted(SHIMS))
def test_the_call_sites_name_a_path_that_resolves_in_both_layouts(name: str) -> None:
    """No `../../../scripts`, and no swallow hiding a real verdict.

    The planner returns 1 when it blocks; `2>/dev/null || true` discarded both
    that signal and the file-not-found that preceded it.
    """
    for call_site in SHIMS[name]:
        text = call_site.read_text(encoding="utf-8")
        # Only lines carrying a PATH are constrained; requiring a prefix on a
        # bare conceptual mention would be a manufactured finding.
        pathed = [line for line in text.splitlines() if f"scripts/{name}" in line]
        assert pathed, f"{call_site}: no longer names a path to {name}"
        for line in pathed:
            assert "$SKILL_DIR/../../shared/scripts/" in line, line
            assert "../../../" not in line, line
            assert "|| true" not in line, f"{call_site}: swallow hides a real verdict"
            # BOTH halves of the #477 swallow. `2>/dev/null` alone still hides
            # the file-not-found, and three of these call sites are `references/`
            # prose that `validate_skills`' Bootstrap-fence guard never reaches —
            # so this assertion is their only guard.
            assert "2>/dev/null" not in line, f"{call_site}: stderr swallow hides a missing file"
            # The shims ship mode 100644, so a bare path is `permission denied`.
            # Naming a command that cannot run is the very class #477 filed.
            assert "python3 " in line, f"{call_site}: names a non-executable path with no interpreter"
