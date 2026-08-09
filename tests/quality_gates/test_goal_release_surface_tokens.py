"""Release-surface detection, and the adapter seam that keeps the floor armed.

Split from `test_goal_coordination_floors.py` on a real concept boundary rather
than to dodge a line cap: this file owns ONE question — what counts as a release
surface, and who gets to say so — while the sibling owns the coordination-cue
floors themselves.

The defect these pin: the token list held only four of THIS repo's own script and
artifact names, so in any consuming repo nothing ever matched, `release_triggered`
was always False, and the release coordination floor never fired. A goal that
bumped a version closed with no release evidence and no line saying the check had
not applied. A floor silently inert everywhere but its authoring repo is worse
than no floor, because it reads as coverage.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"

# Modules this file is the standing coverage for, declared as quoted repo-relative
# paths so `suggest_mutation_coverage_command` can MAP them. The mapper reads
# textual references, and these tests build their paths from a variable
# (`_SCRIPTS / "x.py"`), which matches none of its patterns -- so the changed-line
# coverage gate reported these files unmapped and then blocked on lines this suite
# actually covers. Declaring the mapping is better than making the loader uglier to
# be greppable.
_COVERS = (
    "skills/public/achieve/scripts/goal_artifact_coordination_floors.py",
    "skills/public/achieve/scripts/achieve_adapter_policy.py",
)



def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cf = _load("goal_artifact_coordination_floors")
policy = _load("achieve_adapter_policy")




@pytest.mark.parametrize(
    "token",
    [
        "pyproject.toml", "package.json", "Cargo.toml", "pom.xml", "build.gradle",
        "setup.py", "version.txt", "CHANGELOG.md",
        "npm publish", "cargo publish", "twine upload", "gh release", "git tag",
        "poetry publish", "goreleaser",
    ],
)
def test_the_release_floor_recognizes_ecosystem_release_surfaces(token: str) -> None:
    """The token list held only THIS repo's four script and artifact names.

    In any consuming repo none of them ever appeared, so `release_triggered` was
    always False, the release coordination floor never fired, and a goal that
    bumped a version closed with no release evidence and no line saying the check
    had not applied. A floor silently inert everywhere but its authoring repo is
    worse than no floor, because it reads as coverage.
    """
    assert cf.release_triggered(f"## Slice Log\n\n- bumped the version in {token}\n") is True


def test_a_goal_that_touches_no_release_surface_still_does_not_trigger() -> None:
    """The widening must not make the floor fire on everything."""
    assert cf.release_triggered("## Slice Log\n\n- repaired a docstring and a test\n") is False


def test_an_adapter_can_declare_a_release_surface_the_builtin_list_cannot_know(
    tmp_path: Path,
) -> None:
    """A repo whose release surface is bespoke re-arms the floor by declaring it."""
    text = "## Slice Log\n\n- ran ./ops/ship-it.sh against staging\n"
    assert cf.release_triggered(text, tmp_path) is False

    (tmp_path / ".agents").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".agents" / "achieve-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nrelease_surface_tokens:\n  - ./ops/ship-it.sh\n",
        encoding="utf-8",
    )
    assert cf.release_triggered(text, tmp_path) is True


def test_a_broken_adapter_leaves_the_floor_ARMED_rather_than_inert(tmp_path: Path) -> None:
    """An adapter problem must not decide a floor.

    Falling back to the built-in list keeps the floor armed, which is the whole
    failure this repair is about: a floor that goes quiet is read as coverage.
    """
    (tmp_path / ".agents").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".agents" / "achieve-adapter.yaml").write_text(
        "this: [is not: valid yaml\n", encoding="utf-8"
    )
    assert cf.release_triggered("## Slice Log\n\n- edited pyproject.toml\n", tmp_path) is True


def test_the_coordination_span_is_still_blanked_with_a_repo_root(tmp_path: Path) -> None:
    """The adapter argument must not disturb the existing exclusion."""
    text = (
        "## Slice Log\n\n- nothing released here\n\n"
        "## Coordination Cues\n\n- Release: charness-artifacts/release/x.md\n"
    )
    assert cf.release_triggered(text, tmp_path) is False


def test_an_unimportable_adapter_module_leaves_the_floor_ARMED(monkeypatch, tmp_path) -> None:
    """The import itself is the real failure mode, so it is covered directly.

    `resolve_release_surface_tokens` is already graceful about adapter CONTENT, so
    the `except` around the call exists for the IMPORT: in an exported plugin
    layout the sibling may not resolve. Whatever the reason, the floor must fall
    back to the built-in list rather than going quiet — an inert floor reads as
    coverage, which is the defect this whole repair is about.
    """
    import sys
    import types

    broken = types.ModuleType("achieve_adapter_policy")  # no resolve_release_surface_tokens
    monkeypatch.setitem(sys.modules, "achieve_adapter_policy", broken)

    assert cf.release_triggered("## Slice Log\n\n- edited pyproject.toml\n", tmp_path) is True
    assert cf.release_triggered("## Slice Log\n\n- edited a docstring\n", tmp_path) is False
