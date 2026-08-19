from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace

import pytest

from runtime_bootstrap import import_repo_module

from .support import ROOT

_artifact_validator = import_repo_module(
    ROOT / "scripts" / "artifact_validator.py",
    "scripts.artifact_validator",
)
# Bound by its own DOTTED path even though every call below goes through the
# re-exports above: the changed-line coverage mapper resolves a changed file to its
# tests by dotted module path, so without this line the gate reported these very lines
# as covered by nothing while this file was exercising them. Measured, not assumed --
# `coverage report -m` over this file alone shows the arms hit either way; what changes
# is whether the GATE can see it.
_violation_report = import_repo_module(
    ROOT / "scripts" / "artifact_violation_report.py",
    "scripts.artifact_violation_report",
)
# Same binding, same reason, for the 2026-08-19 split: `artifact_words` and
# `validate_max_words` moved into their own module and are exercised here only
# through `artifact_validator`'s re-exports. A bounded reviewer flagged that this
# repo had already paid for the missing binding once on the line above, and that
# the new split shipped without it.
_size_budget = import_repo_module(
    ROOT / "scripts" / "artifact_size_budget.py",
    "scripts.artifact_size_budget",
)


def test_the_size_budget_module_is_exercised_through_the_validator_reexports() -> None:
    """Both re-exports resolve to the split module's own objects, not to copies.

    Pins the split itself: if a later edit re-inlines either function into
    `artifact_validator`, or binds a second module instance from a different
    sys.path entry, this fails rather than leaving the coverage gate to notice.
    """
    assert _artifact_validator.artifact_words is _size_budget.artifact_words
    assert _artifact_validator.validate_max_words is _size_budget.validate_max_words
    # `# Title` is two tokens, `[label](path)` is one -- the two arithmetic claims the
    # module docstrings make about what a "word" is, pinned so the prose cannot drift
    # from the code again.
    assert _size_budget.artifact_words(["# Title"]) == 2
    assert _size_budget.artifact_words(["[label](path)"]) == 1

# The registry is imported by NAME inside `_scaffold_rel`, so binding it here through
# the same top-level import is what makes the monkeypatch land on the object the lazy
# import resolves rather than on a second copy loaded from a different sys.path entry.
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
PREFLIGHT = importlib.import_module("check_artifact_surface_preflight")


@pytest.fixture
def register_surface(monkeypatch: pytest.MonkeyPatch):
    """Add one artifact surface to the preflight registry for the duration of a test.

    Every scaffold this repo currently declares sits at `skills/public/<id>/scripts/`,
    so the shape guard in `_skill_id` -- the one that decides a scaffold path does NOT
    name a public skill -- has no live instance to fire on. A registry entry is how the
    guard is reached without inventing a second artifact-type mapping beside the one
    `_skill_id` exists to avoid.
    """

    def register(artifact_type: str, scaffold: str) -> None:
        surface = SimpleNamespace(artifact_type=artifact_type, scaffold=scaffold)
        monkeypatch.setattr(PREFLIGHT, "REGISTRY", (*PREFLIGHT.REGISTRY, surface))

    return register


def test_a_repo_root_scaffold_names_no_owning_skill(register_surface) -> None:
    """A scaffold that lives outside the skill tree has no skill to name.

    `_skill_id` reads the owner off the scaffold path, and a path with fewer than
    three segments has no `<id>` segment to read. Indexing it anyway would either
    crash the hint or invent an owner, and the hint runs on the failure path of every
    validator -- the worst place to raise.
    """
    register_surface("probe-repo-root-owned", "scripts/artifact_validator.py")

    # Guard: the registration took, so the assertions below are about the shape rule
    # rather than about an artifact type the registry never resolved.
    assert _artifact_validator._scaffold_rel("probe-repo-root-owned") == "scripts/artifact_validator.py"
    assert _artifact_validator._skill_id("probe-repo-root-owned") is None

    hint = _artifact_validator.scaffold_hint("probe-repo-root-owned")
    assert hint is not None
    # The scaffold half of the hint still lands; only the skill invitation is withheld.
    assert "python3 scripts/artifact_validator.py --repo-root ." in hint
    assert "skill for the authoring discipline" not in hint


def test_a_shared_tree_scaffold_is_not_read_as_a_public_skill_id(register_surface) -> None:
    """The subtler arm: a path deep enough to index, whose third segment is not a skill.

    `skills/shared/scripts/...` has a segment sitting exactly where `<id>` sits under
    `skills/public/`, so a purely positional read would tell an author to load
    `charness:scripts` -- a skill that does not exist, printed at the moment they are
    already looking at a refusal.
    """
    register_surface("probe-shared-owned", "skills/shared/scripts/reviewer_boundary_fingerprint.py")

    assert _artifact_validator._skill_id("probe-shared-owned") is None

    hint = _artifact_validator.scaffold_hint("probe-shared-owned")
    assert hint is not None
    assert "charness:scripts" not in hint
    assert "skill for the authoring discipline" not in hint


def test_a_public_skill_scaffold_still_names_its_owner(register_surface) -> None:
    """Discriminating control: the shape guard rejects only the paths it must.

    Registered the same way as the two above, so a guard that started refusing
    everything -- the cheap way to make both refusal tests pass -- fails here.
    """
    register_surface("probe-public-owned", "skills/public/handoff/scripts/scaffold_handoff_artifact.py")

    assert _artifact_validator._skill_id("probe-public-owned") == "charness:handoff"
    assert "`charness:handoff` skill" in _artifact_validator.scaffold_hint("probe-public-owned")


def test_the_exported_flattened_layout_still_names_its_owner() -> None:
    """The consumer's spelling: the export flattens `skills/public/<id>/` to `skills/<id>/`.

    Reading only the source spelling returned None for every artifact type in an
    installed repo, so the one audience that cannot read this repo's source lost the
    entire hint -- including the clause naming the ceiling as adapter-configurable.
    Found by an adversarial installed-layout round.
    """
    assert (
        _artifact_validator._skill_id_from_scaffold("skills/handoff/scripts/scaffold_handoff_artifact.py")
        == "charness:handoff"
    )
    # The source spelling keeps working, so this is an addition, not a swap.
    assert (
        _artifact_validator._skill_id_from_scaffold(
            "skills/public/handoff/scripts/scaffold_handoff_artifact.py"
        )
        == "charness:handoff"
    )


def test_a_flattened_shared_path_is_still_not_a_skill_id() -> None:
    """Discriminating control for the arm above.

    Accepting the flattened spelling positionally would read `skills/shared/...` as the
    skill `charness:shared`. The export flattens ONLY `skills/public/`, so `shared` and
    `support` keep their names in both layouts and must stay refused in both.
    """
    for scaffold in (
        "skills/shared/scripts/reviewer_boundary_fingerprint.py",
        "skills/support/markdown-preview/scripts/markdown_preview_render.py",
    ):
        assert _violation_report._skill_id_from_scaffold(scaffold) is None, scaffold


def test_an_absolute_installed_scaffold_path_still_names_its_owner() -> None:
    """The installed hint emits an ABSOLUTE path so the printed command is runnable.

    Anchoring the skill name on `parts[0] == "skills"` therefore dropped it for the one
    reader the flattened arm was added for. Located, not positional.
    """
    assert (
        _artifact_validator._skill_id_from_scaffold(
            "/home/someone/.agents/plugins/charness/skills/handoff/scripts/scaffold_handoff_artifact.py"
        )
        == "charness:handoff"
    )
    assert (
        _artifact_validator._skill_id_from_scaffold(
            "/opt/charness/skills/shared/scripts/reviewer_boundary_fingerprint.py"
        )
        is None
    )


def test_a_registered_scaffold_that_ships_in_neither_layout_yields_no_hint(register_surface) -> None:
    """Both spellings miss, so the hint is withheld rather than naming a missing file.

    The two-spelling loop exists because the export flattens `skills/public/<id>/`; a
    surface whose file is absent from BOTH layouts must fall through every candidate.
    A hint is decoration and must never name a command the reader cannot run — the
    same bar that made the installed path absolute.
    """
    register_surface("probe-absent-everywhere", "skills/public/nope/scripts/scaffold_nope.py")

    assert _violation_report._scaffold_rel("probe-absent-everywhere") is None
    assert _violation_report.scaffold_hint("probe-absent-everywhere") is None


def test_a_path_with_no_skill_segment_after_skills_yields_no_owner() -> None:
    """`skills/<file>` indexes far enough to find `skills` and not far enough to name an id.

    Without the length arm a positional read would raise, or invent an owner from a
    filename, at the moment the reader is already looking at a refusal.
    """
    for scaffold in ("skills/scaffold_handoff_artifact.py", "skills", "/opt/x/skills/only.py"):
        assert _violation_report._skill_id_from_scaffold(scaffold) is None, scaffold
