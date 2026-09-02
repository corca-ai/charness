from __future__ import annotations

from pathlib import Path

from scripts.evidence import boundary_probe_lib

ROOT = Path(__file__).resolve().parents[1]


# --- cross_surface_hit: globs (AC3) -----------------------------------------


def test_empty_config_never_hits(tmp_path: Path) -> None:
    assert boundary_probe_lib.cross_surface_hit(tmp_path, ["scripts/foo.py"]) is False
    assert (
        boundary_probe_lib.cross_surface_hit(tmp_path, ["scripts/foo.py"], globs=[], surfaces=[])
        is False
    )


def test_glob_match_hits(tmp_path: Path) -> None:
    assert (
        boundary_probe_lib.cross_surface_hit(tmp_path, ["scripts/reducer.py"], globs=["scripts/*.py"])
        is True
    )


def test_glob_no_match_misses(tmp_path: Path) -> None:
    assert (
        boundary_probe_lib.cross_surface_hit(tmp_path, ["docs/readme.md"], globs=["scripts/*.py"])
        is False
    )


# --- cross_surface_hit: surface ids against the real manifest (AC3) ----------


def _first_real_surface() -> tuple[str, str]:
    from scripts.adapters import surfaces_lib

    manifest = surfaces_lib.load_surfaces(ROOT, required=False)
    assert manifest, "charness ships .agents/surfaces.json"
    for surface in manifest["surfaces"]:
        for pattern in surface["source_paths"] + surface["derived_paths"]:
            if "*" not in pattern:
                return surface["surface_id"], pattern
    # fall back: a globbed pattern with a concrete stem
    surface = manifest["surfaces"][0]
    pattern = (surface["source_paths"] + surface["derived_paths"])[0]
    return surface["surface_id"], pattern.replace("**", "x").replace("*", "x")


def test_surface_id_match_hits() -> None:
    surface_id, matching_path = _first_real_surface()
    assert (
        boundary_probe_lib.cross_surface_hit(ROOT, [matching_path], surfaces=[surface_id]) is True
    )


def test_unknown_surface_id_misses() -> None:
    _, matching_path = _first_real_surface()
    assert (
        boundary_probe_lib.cross_surface_hit(
            ROOT, [matching_path], surfaces=["no-such-surface-id"]
        )
        is False
    )


# --- probe_config_from_adapter ----------------------------------------------


def test_probe_config_tolerates_absent_and_bad_values() -> None:
    assert boundary_probe_lib.probe_config_from_adapter({}) == {"globs": [], "surfaces": []}
    assert boundary_probe_lib.probe_config_from_adapter(
        {"boundary_cross_surface_globs": "scripts/*.py"}
    ) == {"globs": [], "surfaces": []}  # non-list -> empty
    assert boundary_probe_lib.probe_config_from_adapter(
        {"boundary_cross_surface_globs": ["a/*"], "boundary_cross_surface_surfaces": ["s1"]}
    ) == {"globs": ["a/*"], "surfaces": ["s1"]}


# --- resolve_changed_paths: explicit / ref / working-tree fallback (#421) ----


def test_resolve_changed_paths_explicit_path_wins(tmp_path: Path, monkeypatch) -> None:
    # Explicit changed_path bypasses both git branches entirely.
    def _boom(*_a, **_k):
        raise AssertionError("must not touch git when changed_path is explicit")

    monkeypatch.setattr(boundary_probe_lib._surfaces_lib, "collect_changed_paths_for_ref", _boom)
    monkeypatch.setattr(boundary_probe_lib._surfaces_lib, "collect_changed_paths", _boom)
    assert boundary_probe_lib.resolve_changed_paths(tmp_path, ["a.py", "b.py"], "some-ref") == ["a.py", "b.py"]
    # An empty explicit list is still "not None" -> still wins, still returns [].
    assert boundary_probe_lib.resolve_changed_paths(tmp_path, [], "some-ref") == []


def test_resolve_changed_paths_uses_changed_ref_when_no_explicit_path(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        boundary_probe_lib._surfaces_lib,
        "collect_changed_paths_for_ref",
        lambda repo_root, ref: [f"ref:{repo_root}:{ref}"],
    )
    assert boundary_probe_lib.resolve_changed_paths(tmp_path, None, "base..HEAD") == [
        f"ref:{tmp_path}:base..HEAD"
    ]


def test_resolve_changed_paths_falls_back_to_working_tree_diff(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        boundary_probe_lib._surfaces_lib,
        "collect_changed_paths",
        lambda repo_root: [f"wt:{repo_root}"],
    )
    assert boundary_probe_lib.resolve_changed_paths(tmp_path, None, None) == [f"wt:{tmp_path}"]
    # A falsy (empty-string) changed_ref also falls through to the working-tree diff.
    assert boundary_probe_lib.resolve_changed_paths(tmp_path, None, "") == [f"wt:{tmp_path}"]


def test_include_worktree_unions_instead_of_replacing(tmp_path: Path, monkeypatch) -> None:
    """Audit row C6: verify precedes commit, so the slice under critique is on disk.

    A committed range alone is structurally blind to it — measured on the live
    repo, the same working tree gave `hit=False` from `HEAD..HEAD` and `hit=True`
    from its own worktree paths, so the #408 5b tooth was armed or disarmed by
    which question was asked rather than by the code. The union is the fix; a
    REPLACE would have lost the committed half of a pre-push range.
    """
    monkeypatch.setattr(
        boundary_probe_lib._surfaces_lib,
        "collect_changed_paths_for_ref",
        lambda repo_root, ref: ["committed.py"],
    )
    monkeypatch.setattr(
        boundary_probe_lib._surfaces_lib,
        "collect_changed_paths",
        lambda repo_root: ["worktree.py", "committed.py"],
    )
    assert boundary_probe_lib.resolve_changed_paths(tmp_path, None, "base..HEAD") == ["committed.py"]
    assert boundary_probe_lib.resolve_changed_paths(
        tmp_path, None, "base..HEAD", include_worktree=True
    ) == ["committed.py", "worktree.py"]
    # Explicit paths keep winning, and are unioned rather than replaced too.
    assert boundary_probe_lib.resolve_changed_paths(
        tmp_path, ["explicit.py"], "base..HEAD", include_worktree=True
    ) == ["explicit.py", "worktree.py", "committed.py"]


def test_include_worktree_does_not_widen_ref_or_explicit_scope(tmp_path: Path, monkeypatch) -> None:
    """Off by default for the two shapes that RESOLVE a scope of their own.

    Named for what it tests. The third shape (no ref, no explicit paths) reads the
    working tree by default and always has -- an earlier name claimed the worktree
    was never read without the flag, which is false there.
    """

    def _boom(*_a, **_k):
        raise AssertionError("a resolved ref/explicit scope must not be widened without the flag")

    monkeypatch.setattr(
        boundary_probe_lib._surfaces_lib,
        "collect_changed_paths_for_ref",
        lambda repo_root, ref: ["committed.py"],
    )
    monkeypatch.setattr(boundary_probe_lib._surfaces_lib, "collect_changed_paths", _boom)
    assert boundary_probe_lib.resolve_changed_paths(tmp_path, None, "base..HEAD") == ["committed.py"]
    assert boundary_probe_lib.resolve_changed_paths(tmp_path, ["x.py"], None) == ["x.py"]


# --- AC8: the portable brief is reachable from the reviewer surfaces ----------
# The first surfaces are the critique and Prove references; the remaining ones
# are the boundary-ownership brief's other consumers.
_BRIEF_SURFACES = (
    "skills/public/prove/references/review-gate.md",
    "skills/public/critique/references/code-critique.md",
    "skills/public/critique/references/spec-critique.md",
    "skills/public/issue/references/causal-review.md",
    "skills/public/spec/references/design-lenses.md",
    "skills/public/achieve/references/coordination.md",
    "skills/public/quality/references/quality-lenses.md",
)
_VERDICTS = ("single-surface", "owned-correctly", "moved-to-owner", "escalated-to-issue-spec")


def test_brief_linked_from_reviewer_surfaces() -> None:
    # check_doc_links fails only a BROKEN link, not a MISSING one; guard the brief surfaces + issue disposition line.
    for rel in _BRIEF_SURFACES:
        assert "boundary-ownership-brief.md" in (ROOT / rel).read_text("utf-8"), rel
    assert "Boundary #N:" in (ROOT / "skills/public/issue/references/causal-review.md").read_text("utf-8")
