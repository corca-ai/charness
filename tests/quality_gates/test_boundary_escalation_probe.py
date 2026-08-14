from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts import boundary_probe_lib

from .support import ROOT, run_script

# The cross-surface escalation probe's typed outcome, at the library and at the CLI.
#
# `triggered` is a VERDICT KEY. The old payload led with `triggered: false` for a repo
# that configured no probe, a repo whose configured surface id could not be resolved, and
# a repo whose probe genuinely found nothing — and the non-`--detail` path printed only
# that line, so three different worlds read as one answer, and the one that means "do
# nothing" was the answer to all of them.
#
# The library half matters as much as the CLI half: `resolve_cross_surface_scope` typed
# the states it could see from OUTSIDE the probe and then delegated the rest to
# `cross_surface_hit`, so a missing `.agents/surfaces.json` resolved to
# `evaluated (no match)` — a positive claim that the probe ran — and silently disarmed the
# cross-surface `single-surface` rejection in `validate-critique-artifacts` too, not just
# the impl stop gate.

_SCRIPT = "skills/public/prove/scripts/check_boundary_escalation.py"

_SURFACES_MANIFEST = {
    "version": 1,
    "surfaces": [
        {
            "surface_id": "declared-surface",
            "description": "a declared surface",
            "source_paths": ["scripts/**"],
            "derived_paths": [],
            "sync_commands": [],
            "verify_commands": [],
            "notes": [],
        }
    ],
}


def _repo(tmp_path: Path, *adapter_lines: str, surfaces: bool = False) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "critique-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: consumer", *adapter_lines, ""]), encoding="utf-8"
    )
    if surfaces:
        (repo / ".agents" / "surfaces.json").write_text(
            json.dumps(_SURFACES_MANIFEST), encoding="utf-8"
        )
    return repo


# --- library: the three states, and the hit that short-circuits them -----------


def test_probe_state_not_configured_is_a_verdict_not_a_failure(tmp_path: Path) -> None:
    # Opt-in by design: a repo that configures nothing keeps the always-brief +
    # presence floor WITHOUT the objective override. Reporting this as undetermined
    # would make every unconfigured repo refuse forever.
    state = boundary_probe_lib.cross_surface_probe_state(tmp_path, ["scripts/x.py"])
    assert state["state"] == boundary_probe_lib.PROBE_NOT_CONFIGURED
    assert state["hit"] is False
    assert state["undetermined_reasons"] == []


def test_probe_state_evaluated_reports_hit_and_miss(tmp_path: Path) -> None:
    hit = boundary_probe_lib.cross_surface_probe_state(
        tmp_path, ["scripts/reducer.py"], globs=["scripts/*.py"]
    )
    miss = boundary_probe_lib.cross_surface_probe_state(
        tmp_path, ["docs/readme.md"], globs=["scripts/*.py"]
    )
    assert (hit["state"], hit["hit"]) == (boundary_probe_lib.PROBE_EVALUATED, True)
    assert (miss["state"], miss["hit"]) == (boundary_probe_lib.PROBE_EVALUATED, False)
    assert miss["scanned_paths"] == 1


def test_probe_state_missing_manifest_is_not_established(tmp_path: Path) -> None:
    """The residual hole under the wrapper. `load_surfaces(required=False)` returns None
    for an absent manifest, and the old code fell straight through to `return False`."""
    state = boundary_probe_lib.cross_surface_probe_state(
        tmp_path, ["scripts/x.py"], surfaces=["declared-surface"]
    )
    assert state["state"] == boundary_probe_lib.PROBE_NOT_ESTABLISHED
    assert state["hit"] is False
    assert any("surfaces.json" in reason for reason in state["undetermined_reasons"])


def test_probe_state_unresolved_surface_id_is_not_established(tmp_path: Path) -> None:
    """A typo used to be "simply cannot match", i.e. indistinguishable from a real miss."""
    repo = _repo(tmp_path, surfaces=True)
    state = boundary_probe_lib.cross_surface_probe_state(
        repo, ["docs/x.md"], surfaces=["declaredd-surface"]
    )
    assert state["state"] == boundary_probe_lib.PROBE_NOT_ESTABLISHED
    assert state["unresolved_surfaces"] == ["declaredd-surface"]


def test_probe_state_empty_changed_set_is_not_established(tmp_path: Path) -> None:
    state = boundary_probe_lib.cross_surface_probe_state(tmp_path, [], globs=["scripts/*.py"])
    assert state["state"] == boundary_probe_lib.PROBE_NOT_ESTABLISHED
    assert state["scanned_paths"] == 0


def test_probe_state_hit_short_circuits_an_unresolvable_sibling(tmp_path: Path) -> None:
    """A glob match beside a typo'd surface id stays `evaluated`.

    Deliberate asymmetry: the positive is established by the path that matched, and
    downgrading it would DISARM the cross-surface `single-surface` rejection — turning a
    fix against silence into a new silence."""
    repo = _repo(tmp_path, surfaces=True)
    state = boundary_probe_lib.cross_surface_probe_state(
        repo, ["scripts/x.py"], globs=["scripts/*.py"], surfaces=["declaredd-surface"]
    )
    assert state["state"] == boundary_probe_lib.PROBE_EVALUATED
    assert state["hit"] is True


def test_cross_surface_hit_keeps_its_bool_contract_for_positive_only_callers(
    tmp_path: Path,
) -> None:
    # `resolve_cross_surface_scope`'s per-path witness search and the severity upgrade
    # only act on a hit, so the shorthand keeps working unchanged — every truth value it
    # returned before is the truth value it returns now.
    repo = _repo(tmp_path, surfaces=True)
    assert boundary_probe_lib.cross_surface_hit(repo, ["scripts/x.py"], globs=["scripts/*.py"])
    assert not boundary_probe_lib.cross_surface_hit(repo, ["docs/x.md"], globs=["scripts/*.py"])
    assert not boundary_probe_lib.cross_surface_hit(tmp_path, ["scripts/x.py"], surfaces=["s"])


# --- CLI: state is key #1, `triggered` only when the probe ran ----------------


def test_cli_evaluated_hit_reports_triggered(tmp_path: Path) -> None:
    repo = _repo(tmp_path, "boundary_cross_surface_globs:", "  - 'scripts/*.py'")
    result = run_script(_SCRIPT, "--repo-root", str(repo), "--changed-path", "scripts/x.py", "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert list(payload)[0] == "state"
    assert payload["state"] == "evaluated"
    assert payload["triggered"] is True


def test_cli_not_configured_is_exit_zero_with_a_real_false(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result = run_script(_SCRIPT, "--repo-root", str(repo), "--changed-path", "scripts/x.py", "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "not-configured"
    assert payload["triggered"] is False


@pytest.mark.parametrize(
    "adapter_lines, surfaces, changed, marker",
    [
        pytest.param(
            ("boundary_cross_surface_surfaces:", "  - declared-surface"),
            False,
            ("scripts/x.py",),
            "surfaces.json",
            id="missing-surfaces-manifest",
        ),
        pytest.param(
            ("boundary_cross_surface_surfaces:", "  - declaredd-surface"),
            True,
            ("docs/x.md",),
            "not declared",
            id="typoed-surface-id",
        ),
        pytest.param(
            ("boundary_cross_surface_globs:", "  - 'scripts/*.py'"),
            False,
            (),
            "zero changed paths",
            id="empty-changed-scope",
        ),
    ],
)
def test_cli_undetermined_omits_triggered_and_exits_nonzero(
    tmp_path: Path, adapter_lines, surfaces: bool, changed, marker: str
) -> None:
    repo = _repo(tmp_path, *adapter_lines, surfaces=surfaces)
    result = run_script(
        _SCRIPT, "--repo-root", str(repo), "--changed-path", *changed, "--detail"
    )

    # Exit 3 matches run-quality.sh's UNESTABLISHED_EXIT: ran, established nothing.
    # The payload still goes to STDOUT so one parse works in every state; the byte, not
    # the stream, is what stops `probe && skip` from skipping on a failure mode.
    assert result.returncode == 3, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "not-established"
    assert "triggered" not in payload
    assert any(marker in reason for reason in payload["undetermined"]), payload


def test_cli_plain_output_never_prints_a_bare_false_for_an_undetermined_run(
    tmp_path: Path,
) -> None:
    """The reported experience was the non-`--detail` path: `reason` then
    `triggered: false`, with the empty probe config visible only under `--detail`."""
    repo = _repo(tmp_path, "boundary_cross_surface_surfaces:", "  - declared-surface")
    result = run_script(_SCRIPT, "--repo-root", str(repo), "--changed-path", "scripts/x.py")

    assert result.returncode == 3, result.stdout
    assert "triggered:" not in result.stdout
    assert "state: not-established" in result.stdout
    assert "undetermined:" in result.stdout


def test_prove_skill_names_the_undetermined_case() -> None:
    # The skill text is the surface that told the caller to act on `triggered: true` and
    # said nothing about the other outcomes, which reads as license to skip on anything
    # else. Both probe references have to name the undetermined case.
    text = (ROOT / "skills" / "public" / "prove" / "SKILL.md").read_text(encoding="utf-8")
    assert "not-established" in text
    assert "not-configured" in text
    assert "check_boundary_escalation.py" in text
    assert "check_auto_trigger.py" in text
