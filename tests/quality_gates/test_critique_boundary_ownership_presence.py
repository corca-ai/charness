from __future__ import annotations

from pathlib import Path

from .support import ROOT, run_script

# The boundary-ownership typed-presence floor (#408/#414/#416): every critique
# artifact records a `## Boundary Ownership` section with a typed `Verdict:` so a
# producer/consumer ownership decision cannot be silently skipped — the
# symptom-caught-in-the-wrong-layer trap #408 took, where a passing unit test at
# the nearest surface looked like a finished fix. Presence + typed-value only;
# correctness (is the named owner right?) stays reviewer judgment, the same
# boundary as the fresh-eye floor and the D34 announcement presence posture.
# Enforced for artifacts dated on/after `BOUNDARY_OWNERSHIP_RULE_DATE`
# (2026-07-06); a dated artifact on/before the landing day (2026-07-05) is
# grandfathered — same `RULE_DATE = landing_day + 1` shape as the fresh-eye
# floor. Every post-cutoff artifact carries a valid `Fresh-eye satisfaction:`
# line here so the fresh-eye floor (checked first) passes and these cases
# isolate the boundary floor.

# `nested-delegated` passes the fresh-eye floor WITHOUT triggering the
# Reviewer-Tier-Evidence requirement that `parent-delegated` does under `--paths`,
# so these cases isolate the boundary floor cleanly.
_FRESH_EYE_OK = "Fresh-eye satisfaction: nested-delegated; recursive delegation actually ran."


def _write(repo: Path, name: str, *body: str) -> str:
    artifact = repo / "charness-artifacts" / "critique" / name
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("\n".join(["# Demo Critique", "", *body, ""]), encoding="utf-8")
    return f"charness-artifacts/critique/{name}"


def _run(repo: Path, relpath: str, *extra: str) -> object:
    return run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        relpath,
        *extra,
    )


def test_boundary_validator_rejects_missing_section_post_cutoff(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    relpath = _write(repo, "2026-07-06-demo.md", _FRESH_EYE_OK)

    result = _run(repo, relpath)

    assert result.returncode == 1
    assert "no `## Boundary Ownership` section" in result.stderr
    assert "single-surface" in result.stderr
    assert "escalated-to-issue-spec" in result.stderr


def test_boundary_validator_rejects_untyped_verdict_post_cutoff(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    relpath = _write(
        repo,
        "2026-07-06-demo.md",
        _FRESH_EYE_OK,
        "",
        "## Boundary Ownership",
        "",
        "- Verdict: reviewed carefully, seems fine.",
    )

    result = _run(repo, relpath)

    assert result.returncode == 1
    assert "does not open with one of" in result.stderr
    assert "Boundary Ownership" in result.stderr


def test_boundary_validator_rejects_typed_verdict_with_unedited_todo(tmp_path: Path) -> None:
    """A typed prefix is not enough if the remainder is still an unedited TODO —
    that is a stub silently claiming a disposition (the exact loophole the
    default scaffold Verdict line is written to avoid), mirrors the fresh-eye
    floor's todo-remainder rejection."""
    repo = tmp_path / "repo"
    relpath = _write(
        repo,
        "2026-07-06-demo.md",
        _FRESH_EYE_OK,
        "",
        "## Boundary Ownership",
        "",
        "- Verdict: single-surface (TODO confirm no producer-owned state is touched).",
    )

    result = _run(repo, relpath)

    assert result.returncode == 1
    assert "unedited `todo`" in result.stderr


def test_boundary_validator_accepts_single_surface_post_cutoff(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    relpath = _write(
        repo,
        "2026-07-06-demo.md",
        _FRESH_EYE_OK,
        "",
        "## Boundary Ownership",
        "",
        "- Producer: the request handler.",
        "- Consumer: the renderer.",
        "- Owning surface: request-layer.",
        "- Verdict: single-surface",
    )

    result = _run(repo, relpath)

    assert result.returncode == 0, result.stderr


def test_boundary_validator_accepts_moved_to_owner_post_cutoff(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    relpath = _write(
        repo,
        "2026-07-06-demo.md",
        _FRESH_EYE_OK,
        "",
        "## Boundary Ownership",
        "",
        "- Verdict: `moved-to-owner`; relocated the fact to its producer plus generic rendering.",
    )

    result = _run(repo, relpath)

    assert result.returncode == 0, result.stderr


def test_boundary_validator_grandfathers_missing_section_on_landing_day(tmp_path: Path) -> None:
    """Dated on the floor's landing day (2026-07-05): the boundary floor is
    grandfathered even though the section is absent. The fresh-eye line is valid
    so the (already-enforced) fresh-eye floor is not what passes this case."""
    repo = tmp_path / "repo"
    relpath = _write(repo, "2026-07-05-demo.md", _FRESH_EYE_OK)

    result = _run(repo, relpath)

    assert result.returncode == 0, result.stderr


def test_boundary_scaffold_default_stub_fails_validation_post_cutoff(tmp_path: Path) -> None:
    """The scaffold's own unedited `## Boundary Ownership` Verdict stub must NOT
    satisfy the boundary floor once dated post-cutoff — defense-in-depth against
    a future change pre-filling a real verdict (the same loophole the fresh-eye
    stub test guards). `--report-all` surfaces both floors so the boundary
    message is asserted even though the unedited fresh-eye stub also fails."""
    import sys

    sys.path.insert(0, str(ROOT / "skills" / "public" / "critique" / "scripts"))
    import scaffold_critique_artifact as scaffold

    template = scaffold.render_template(title="Critique Review", date_text="2026-07-06")
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-06-critique-review.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(template, encoding="utf-8")

    result = _run(repo, "charness-artifacts/critique/2026-07-06-critique-review.md", "--report-all")

    assert result.returncode == 1
    assert "Boundary Ownership" in result.stderr
    assert "single-surface" in result.stderr
