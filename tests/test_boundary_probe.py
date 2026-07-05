from __future__ import annotations

from pathlib import Path

from scripts import boundary_probe_lib

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
    from scripts import surfaces_lib

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


# The impl stop-gate hook's in-process tests (AC7) live in
# tests/quality_gates/test_critique_boundary_ownership_presence.py so they reuse
# that file's single critique-adapter fixture writer instead of a second copy.


# --- AC8: the portable brief is reachable from the reviewer surfaces ----------
# First three surfaces are the First Slice (critique + impl); the last four are
# DBD-2's extension into issue / spec / achieve / quality (#414/#416).
_BRIEF_SURFACES = (
    "skills/public/impl/references/review-gate.md",
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


# --- AC9: the emit-only Boundary Ownership token is carried at closeout --------


def _sections(rel: str) -> dict[str, str]:
    # Header-keyed split — "## Closeout Vocabulary" also appears inline in Output Shape.
    out: dict[str, str] = {}
    for chunk in ("\n" + (ROOT / rel).read_text("utf-8")).split("\n## ")[1:]:
        out[chunk.split("\n", 1)[0].strip()] = chunk
    return out


def test_impl_and_spec_skills_carry_boundary_ownership_token() -> None:
    # impl (First Slice) + spec (DBD-2 #414/#416): impl-archetype emit-only token.
    # issue's emit-only `Boundary #N:` close-comment line is prose (not validator-
    # enforced), covered by the brief-reachability surface above; no separate test.
    for rel in ("skills/public/impl/SKILL.md", "skills/public/spec/SKILL.md"):
        s = _sections(rel)
        assert "Boundary Ownership" in s["Output Shape"] and "Boundary Ownership" in s["Closeout Vocabulary"], rel
        assert all(v in s["Closeout Vocabulary"] for v in _VERDICTS), rel
