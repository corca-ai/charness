from __future__ import annotations

from pathlib import Path

import pytest
import quality_label_universe

from tests.quality_gates.repo_shapes import install_two_commit_repo

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


# The post-cutoff presence/typed-value floor, table-driven. A typed prefix is not
# enough if the remainder is still an unedited TODO — a stub silently claiming a
# disposition (the loophole the default scaffold Verdict line avoids); a missing
# section and an untyped verdict reject the same way.
@pytest.mark.parametrize(
    "body, errors",
    [
        (
            (_FRESH_EYE_OK,),
            ("no `## Boundary Ownership` section", "single-surface", "escalated-to-issue-spec"),
        ),
        (
            (
                _FRESH_EYE_OK,
                "",
                "## Boundary Ownership",
                "",
                "- Verdict: reviewed carefully, seems fine.",
            ),
            ("does not open with one of", "Boundary Ownership"),
        ),
        (
            (
                _FRESH_EYE_OK,
                "",
                "## Boundary Ownership",
                "",
                "- Verdict: single-surface (TODO confirm no producer-owned state is touched).",
            ),
            ("unedited `todo`",),
        ),
    ],
)
def test_boundary_validator_rejects_post_cutoff(tmp_path: Path, body: tuple, errors: tuple) -> None:
    result = _run(tmp_path / "repo", _write(tmp_path / "repo", "2026-07-06-demo.md", *body))
    assert result.returncode == 1
    for token in errors:
        assert token in result.stderr


@pytest.mark.parametrize(
    "body",
    [
        (
            _FRESH_EYE_OK,
            "",
            "## Boundary Ownership",
            "",
            "- Producer: the request handler.",
            "- Consumer: the renderer.",
            "- Owning surface: request-layer.",
            "- Verdict: single-surface",
        ),
        (
            _FRESH_EYE_OK,
            "",
            "## Boundary Ownership",
            "",
            "- Verdict: `moved-to-owner`; relocated the fact to its producer plus generic rendering.",
        ),
    ],
)
def test_boundary_validator_accepts_post_cutoff(tmp_path: Path, body: tuple) -> None:
    result = _run(tmp_path / "repo", _write(tmp_path / "repo", "2026-07-06-demo.md", *body))
    assert result.returncode == 0, result.stderr


def test_boundary_validator_grandfathers_missing_section_on_landing_day(tmp_path: Path) -> None:
    """Dated on the floor's landing day (2026-07-05): the boundary floor is
    grandfathered even though the section is absent. The fresh-eye line is valid
    so the (already-enforced) fresh-eye floor is not what passes this case."""
    repo = tmp_path / "repo"
    relpath = _write(repo, "2026-07-05-demo.md", _FRESH_EYE_OK)

    result = _run(repo, relpath)

    assert result.returncode == 0, result.stderr


def _write_adapter_with_globs(repo: Path, *globs: str) -> None:
    adapter = repo / ".agents" / "critique-adapter.yaml"
    adapter.parent.mkdir(parents=True, exist_ok=True)
    # `[]` when empty, not a bare `boundary_cross_surface_globs:`. The bare form parses
    # to an empty MAPPING, which the adapter validator refuses -- and it refuses it on
    # purpose, because dash-less children parse to the same `{}` after the parser drops
    # them. This fixture spelled the refused form, which read as harmless only while the
    # probe was discarding loader errors; once it stopped, the fixture was the thing
    # asking for a malformed adapter to be honoured.
    declaration = (
        "boundary_cross_surface_globs:\n" + "".join(f'  - "{g}"\n' for g in globs)
        if globs
        else "boundary_cross_surface_globs: []\n"
    )
    adapter.write_text("version: 1\nrepo: demo\n" + declaration, encoding="utf-8")


def _write_with_verdict(repo: Path, name: str, verdict: str) -> str:
    return _write(
        repo,
        name,
        _FRESH_EYE_OK,
        "",
        "## Boundary Ownership",
        "",
        f"- Verdict: {verdict}",
    )


def test_probe_rejects_single_surface_on_cross_surface_hit(tmp_path: Path) -> None:
    """The #408 objective override: a changed path matching the repo cross-surface
    probe rejects a bare `single-surface` verdict even though the presence floor
    alone would accept it."""
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*.py")
    relpath = _write_with_verdict(repo, "2026-07-06-demo.md", "single-surface")

    result = _run(repo, relpath, "--changed-path", "scripts/reducer.py")

    assert result.returncode == 1
    assert "cross-surface probe" in result.stderr
    assert "single-surface" in result.stderr and "rejected" in result.stderr


def test_probe_accepts_moved_to_owner_on_cross_surface_hit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*.py")
    relpath = _write_with_verdict(repo, "2026-07-06-demo.md", "moved-to-owner")

    result = _run(repo, relpath, "--changed-path", "scripts/reducer.py")

    assert result.returncode == 0, result.stderr


def test_probe_accepts_single_surface_without_hit(tmp_path: Path) -> None:
    """No probe match -> `single-surface` stays acceptable (the floor is presence
    only when the objective override does not fire)."""
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*.py")
    relpath = _write_with_verdict(repo, "2026-07-06-demo.md", "single-surface")

    result = _run(repo, relpath, "--changed-path", "docs/readme.md")

    assert result.returncode == 0, result.stderr


def test_boundary_scaffold_default_stub_fails_validation_post_cutoff(tmp_path: Path) -> None:
    """The scaffold's own unedited `## Boundary Ownership` Verdict stub must NOT
    satisfy the boundary floor once dated post-cutoff — defense-in-depth against
    a future change pre-filling a real verdict (the same loophole the fresh-eye
    stub test guards). Default one-pass reporting surfaces both floors, so the
    boundary message is asserted even though the unedited fresh-eye stub also fails."""
    import sys

    sys.path.insert(0, str(ROOT / "skills" / "public" / "critique" / "scripts"))
    import scaffold_critique_artifact as scaffold

    template = scaffold.render_template(title="Critique Review", date_text="2026-07-06")
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-06-critique-review.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(template, encoding="utf-8")

    result = _run(repo, "charness-artifacts/critique/2026-07-06-critique-review.md")

    assert result.returncode == 1
    assert "Boundary Ownership" in result.stderr
    assert "single-surface" in result.stderr


def test_critique_validator_refuses_unreadable_cross_surface_adapter(tmp_path: Path) -> None:
    """The validator must not turn malformed probe config into an opt-out."""
    from scripts import boundary_probe_lib, critique_adapter_lib, critique_enforcement_scope

    repo = tmp_path / "repo"
    adapter = repo / ".agents" / "critique-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        'version: 1\nrepo: demo\nboundary_cross_surface_globs: "docs/**"\n',
        encoding="utf-8",
    )

    scope = critique_enforcement_scope.resolve_cross_surface_scope(
        repo,
        None,
        ["docs/x.md"],
        probe_lib=boundary_probe_lib,
        adapter_lib=critique_adapter_lib,
    )

    assert scope.state == critique_enforcement_scope.CROSS_SURFACE_NOT_ESTABLISHED
    assert scope.hit is False


# --- charness dogfoods its own probe (DBD-4) --------------------------------
# These guard the self-adoption against silent regression: emptying the globs or
# dropping --changed-ref would turn the #408 5b tooth back off in charness CI
# (fixture-proven but not live), which is exactly the residual DBD-4 closed.


def test_charness_dogfoods_its_own_cross_surface_probe() -> None:
    from scripts import boundary_probe_lib, critique_adapter_lib

    probe = boundary_probe_lib.probe_config_from_adapter(
        critique_adapter_lib.load_adapter(ROOT)["data"]
    )
    assert probe["globs"], (
        "charness must configure its own boundary_cross_surface_globs (DBD-4 dogfood)"
    )
    # A change to a root shared lib must hit; a doc/test change must not.
    assert boundary_probe_lib.cross_surface_hit(
        ROOT, ["scripts/surfaces_lib.py"], globs=probe["globs"]
    )
    assert not boundary_probe_lib.cross_surface_hit(ROOT, ["docs/index.md"], globs=probe["globs"])
    assert not boundary_probe_lib.cross_surface_hit(ROOT, ["tests/test_x.py"], globs=probe["globs"])


def test_run_quality_wires_changed_ref_range_for_cross_surface_probe() -> None:
    rows = quality_label_universe.quality_gate_rows(ROOT) or []
    critique_row = next(row for row in rows if row["label"] == "validate-critique-artifacts")
    command = critique_row["command"]
    assert "--changed-ref" in command, (
        "quality-gates.yaml must pass --changed-ref to validate-critique-artifacts so the "
        "cross-surface 5b tooth fires in charness CI, not just unit fixtures (DBD-4)"
    )
    # A BARE ref resolves to that one commit's diff-tree (the fork point), not the
    # unpushed range — silently mis-targeting the tooth. Require the RANGE form.
    assert "$CRITIQUE_CHANGED_REF" in command, (
        "the --changed-ref value must come from the runner-computed range variable"
    )
    run_quality = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    assert "..HEAD" in run_quality, (
        "the --changed-ref value must be a range (base..HEAD); a bare sha resolves to "
        "the fork-point commit's own diff, not the change under review (DBD-4 wiring bug)"
    )


def test_changed_ref_range_fires_tooth_end_to_end(tmp_path: Path) -> None:
    # End-to-end proof of the run-quality wiring: a `base..HEAD` range whose
    # committed change touches a `scripts/*_lib.py` path rejects a bare
    # `single-surface` verdict — exactly the CI path. Fails if the wiring regresses
    # to a bare sha (which resolves the fork-point's own diff, not the range).
    artifact = "\n".join(
        [
            "# Demo Critique",
            "",
            _FRESH_EYE_OK,
            "",
            "## Boundary Ownership",
            "",
            "- Verdict: single-surface",
            "",
        ]
    )
    repo, base, _head = install_two_commit_repo(
        tmp_path / "repo",
        {
            ".agents/critique-adapter.yaml": (
                'version: 1\nrepo: demo\nboundary_cross_surface_globs:\n  - "scripts/*_lib.py"\n'
            ),
            "scripts/keep.py": "x = 1\n",
        },
        {
            "scripts/foo_lib.py": "def f():\n    return 1\n",
            "charness-artifacts/critique/2026-07-06-demo.md": artifact,
        },
        first_message="base",
        second_message="change",
    )
    relpath = "charness-artifacts/critique/2026-07-06-demo.md"

    result = _run(repo, relpath, "--changed-ref", f"{base}..HEAD")
    assert result.returncode == 1
    assert "cross-surface probe" in result.stderr
