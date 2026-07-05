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


def test_brief_linked_from_reviewer_surfaces() -> None:
    """check_doc_links only fails a BROKEN link, not a MISSING one, so this guards
    against a regression that silently drops the brief from a reviewer surface."""
    brief = "boundary-ownership-brief.md"
    for rel in (
        "skills/public/impl/references/review-gate.md",
        "skills/public/critique/references/code-critique.md",
        "skills/public/critique/references/spec-critique.md",
    ):
        assert brief in (ROOT / rel).read_text(encoding="utf-8"), f"{rel} must link {brief}"


# --- AC9: impl carries the emit-only Boundary Ownership token -----------------


def test_impl_skill_carries_boundary_ownership_token() -> None:
    skill = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    # Header-keyed section split (the string "## Closeout Vocabulary" also appears
    # inline inside Output Shape, so a plain substring split picks the wrong span).
    sections = {}
    for chunk in ("\n" + skill).split("\n## ")[1:]:
        sections[chunk.split("\n", 1)[0].strip()] = chunk
    assert "Boundary Ownership" in sections["Output Shape"]
    vocab = sections["Closeout Vocabulary"]
    assert "Boundary Ownership" in vocab
    for verdict in ("single-surface", "owned-correctly", "moved-to-owner", "escalated-to-issue-spec"):
        assert verdict in vocab
