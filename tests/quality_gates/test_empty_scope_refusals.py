"""An unestablished scope is not a pass.

Every gate here was observed reporting success over a scope it never
established: zero packaging manifests read as "mirror matches", zero scanned
files read as "validated", a named artifact path that matched nothing read as
"validated 0", and a mutation-run proof claim read as `provable` without any run
being identified. Each is indistinguishable, in output and exit code, from the
same gate having actually checked something.

The rule these pin: **a gate that compared nothing must say so, and must not
exit 0.** The exception is a *discovered* empty set — "this commit touched no
artifact of this family" is a real answer to a real question, and stays a cheap
no-op; that asymmetry is pinned below too, because collapsing it would make
every commit pay for every artifact family.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

# In-process, not subprocess: this repo ratchets the test-suite process boundary
# down (43% of test files drive a nested CLI, which is what makes the suite
# subprocess-bound), so a new gate-behavior file must not add three more.
_MODULES = {
    name: load_script_module(name.removesuffix(".py").replace("/", "_"), ROOT / name)
    for name in (
        "scripts/validate_packaging.py",
        "scripts/check_export_safe_imports.py",
        "scripts/check_bootstrap_shim_consistency.py",
        "scripts/validate_critique_artifacts.py",
        "scripts/validate_retro_artifact.py",
        "scripts/validate_ideation_artifact.py",
        "scripts/check_mutation_run_proof.py",
        "scripts/check_python_lengths.py",
        "scripts/check_skill_bootstrap_vars.py",
        "scripts/check_skill_cut_safety.py",
        "scripts/check_skill_surface_preflight.py",
        "scripts/check_test_repo_copy_invariants.py",
        "scripts/validate_integrations.py",
    )
}


def run_gate(script: str, *args: str):
    return run_loaded_script_main(Path(script).name, _MODULES[script], *args)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args], cwd=repo, check=True, capture_output=True
    )


def _seeded_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-qm", "seed")
    return repo


def _empty_root(tmp_path: Path) -> Path:
    root = tmp_path / "empty-root"
    root.mkdir()
    return root


@pytest.mark.parametrize(
    ("script", "args", "expected_fragment"),
    [
        ("scripts/validate_packaging.py", [], "no packaging manifests found"),
        ("scripts/check_export_safe_imports.py", [], "no export-surface Python files found"),
        ("scripts/check_bootstrap_shim_consistency.py", [], "no bootstrap shim copies found"),
    ],
)
def test_zero_scope_scan_refuses(tmp_path: Path, script: str, args: list[str], expected_fragment: str) -> None:
    result = run_gate(script, "--repo-root", str(_empty_root(tmp_path)), *args)
    assert result.returncode != 0, result.stdout + result.stderr
    assert expected_fragment.lower() in (result.stdout + result.stderr).lower()


@pytest.mark.parametrize(
    "script",
    [
        "scripts/validate_packaging.py",
        "scripts/check_export_safe_imports.py",
        "scripts/check_bootstrap_shim_consistency.py",
    ],
)
def test_zero_scope_refusal_is_not_an_unconditional_failure(script: str) -> None:
    """Positive control: an implementation that simply exits 1 always would pass
    every refusal test above. These gates must still pass on the real repo."""
    result = run_gate(script, "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stdout + result.stderr


def test_bootstrap_shim_json_names_the_empty_scope(tmp_path: Path) -> None:
    """The JSON consumer must see a state distinct from `ok`, not `ok` with a
    zero count it has to notice on its own."""
    result = run_gate(
        "scripts/check_bootstrap_shim_consistency.py", "--repo-root", str(_empty_root(tmp_path)), "--json"
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "empty-scope"
    assert payload["checked_files"] == 0
    assert result.returncode != 0


@pytest.mark.parametrize(
    ("script", "named"),
    [
        ("scripts/validate_critique_artifacts.py", "charness-artifacts/critique/typo.md"),
        ("scripts/validate_retro_artifact.py", "charness-artifacts/retro/typo.md"),
        ("scripts/validate_ideation_artifact.py", "charness-artifacts/ideation/typo.md"),
    ],
)
def test_named_path_that_resolves_to_nothing_refuses(tmp_path: Path, script: str, named: str) -> None:
    """A typo or a stale reference previously printed `Validated 0 <label>(s).`
    and exited 0. Only paths the validator OWNS are judged: a changed path from
    another family is the tool saying "none of this is yours"."""
    (tmp_path / named).parent.mkdir(parents=True)
    result = run_gate(script, "--repo-root", str(tmp_path), "--paths", named)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "resolve to nothing" in (result.stdout + result.stderr)


def test_named_path_from_another_family_is_not_this_validator_business(tmp_path: Path) -> None:
    """The commit-boundary tools pass a slice of the changed set. A path outside
    this validator's artifact directory must stay a pass whether or not it
    exists, or every commit fails every family's validator."""
    (tmp_path / "charness-artifacts/critique").mkdir(parents=True)
    result = run_gate(
        "scripts/validate_critique_artifacts.py",
        "--repo-root", str(tmp_path), "--paths", "scripts/unrelated.py",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_named_path_the_validator_filters_out_still_passes(tmp_path: Path) -> None:
    """The narrow discriminator, and the reason it is narrow: `--paths` is fed by
    TOOLS (the surface preflight, the closeout sweep) with a slice of the changed
    set, which legitimately contains generated packets a validator drops by
    content. Failing those breaks ordinary commits."""
    packet = tmp_path / "charness-artifacts/critique/2026-07-27-demo-packet.md"
    packet.parent.mkdir(parents=True)
    packet.write_text(
        "# Critique Prepare Packet — demo\n\n- **Kind**: `charness.critique_prepare_packet` (v1)\n",
        encoding="utf-8",
    )
    result = run_gate(
        "scripts/validate_critique_artifacts.py",
        "--repo-root", str(tmp_path),
        "--paths", "charness-artifacts/critique/2026-07-27-demo-packet.md",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_named_path_deleted_by_this_change_still_passes(tmp_path: Path) -> None:
    """An archival move or a deletion names a path that is gone ON PURPOSE. Git
    knows it was deleted, so it is not a typo and must not refuse."""
    repo = _seeded_repo(tmp_path)
    artifact = repo / "charness-artifacts/critique/2026-07-27-old.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# old\nDate: 2026-07-27\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "artifact")
    _git(repo, "rm", "-q", "charness-artifacts/critique/2026-07-27-old.md")

    result = run_gate(
        "scripts/validate_critique_artifacts.py",
        "--repo-root", str(repo),
        "--paths", "charness-artifacts/critique/2026-07-27-old.md",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_discovered_empty_set_stays_a_cheap_pass(tmp_path: Path) -> None:
    """The asymmetry: nothing NAMED, nothing found. That is a real answer — the
    common commit touches no artifact of a given family — and must not become a
    failure, or every commit pays for every family."""
    repo = _seeded_repo(tmp_path)
    result = run_gate("scripts/validate_critique_artifacts.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("args", "expected_fragment"),
    [
        (["--claim", "score"], "no run identified"),
        (["--claim", "changed-line"], "no base_sha evidence"),
    ],
)
def test_mutation_run_proof_refuses_without_a_run(args: list[str], expected_fragment: str) -> None:
    """`--claim score` with no facts at all used to return `provable: true` for a
    run the caller never identified. The changed-line claim already refused, on
    its own discriminator (base_sha), which is why it tolerates an unknown event."""
    result = run_gate("scripts/check_mutation_run_proof.py", *args)
    assert result.returncode != 0, result.stdout + result.stderr
    verdict = json.loads(result.stdout)
    assert verdict["provable"] is False
    assert expected_fragment in verdict["reason"]


def test_mutation_run_proof_still_confirms_a_green_identified_run() -> None:
    result = run_gate(
        "scripts/check_mutation_run_proof.py",
        "--claim", "score", "--event", "schedule", "--conclusion", "success",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = json.loads(result.stdout)
    assert verdict["provable"] is True
    assert verdict["conclusion_established"] is True


def test_provable_says_whether_the_run_was_known_green() -> None:
    """A manifest carries no conclusion, so `provable` there means "this trigger
    could evaluate the claim", not "and the run was green". The verdict must not
    let one word carry both."""
    result = run_gate("scripts/check_mutation_run_proof.py", "--claim", "score", "--event", "schedule")
    verdict = json.loads(result.stdout)
    assert verdict["provable"] is True
    assert verdict["conclusion_established"] is False


def test_known_red_run_is_distinguishable_from_unknown_conclusion() -> None:
    """Both refuse, for opposite reasons. A consumer reading a missing field as
    False would collapse "known red" into "nobody checked"."""
    red = run_gate(
        "scripts/check_mutation_run_proof.py",
        "--claim", "score", "--event", "schedule", "--conclusion", "failure",
    )
    verdict = json.loads(red.stdout)
    assert red.returncode != 0
    assert verdict["provable"] is False
    assert verdict["conclusion_established"] is True


# --- 2026-07-28 triage sweep, class (a): a glob that matched NOTHING reported a
# successful validation. Same two rules as above, applied per gate: a scope the
# CALLER NAMED that resolves to nothing refuses; a DISCOVERED empty set stays a
# pass. The third shape these added: named paths this gate does not govern
# (`plugins/` mirrors, root-level helpers) stay a pass, but may not print a
# `Validated ... 0 file(s)` verdict.


@pytest.mark.parametrize(
    ("script", "args", "expected_fragment"),
    [
        # S42: zero SKILL.md under the named root.
        ("scripts/check_skill_bootstrap_vars.py", [], "no public/support SKILL.md files found"),
        # S46: `find_violations` returns [] with no tests/ dir, and --repo-root
        # defaults to the CWD, so a wrong cwd certified PASS over zero files.
        ("scripts/check_test_repo_copy_invariants.py", [], "no test Python files found"),
        # S49: every per-manifest rule iterates a hardcoded glob under the root.
        ("scripts/validate_integrations.py", [], "no integration manifests found"),
    ],
)
def test_zero_scope_scan_refuses_sweep(
    tmp_path: Path, script: str, args: list[str], expected_fragment: str
) -> None:
    result = run_gate(script, "--repo-root", str(_empty_root(tmp_path)), *args)
    assert result.returncode != 0, result.stdout + result.stderr
    assert expected_fragment.lower() in (result.stdout + result.stderr).lower()


@pytest.mark.parametrize(
    "script",
    [
        "scripts/check_skill_bootstrap_vars.py",
        "scripts/check_test_repo_copy_invariants.py",
        "scripts/validate_integrations.py",
    ],
)
def test_zero_scope_refusal_is_not_an_unconditional_failure_sweep(script: str) -> None:
    """Positive control: an implementation that exits 1 always would pass every
    refusal above. These gates must still pass on the real repo."""
    result = run_gate(script, "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stdout + result.stderr


def test_skill_cut_safety_named_non_skill_path_refuses() -> None:
    """S43: `--path` is how a caller ASKS whether a cut is safe. A named path this
    gate cannot judge (a references/*.md contract home) answered `clean` over zero
    checks -- a green verdict for a question that was never evaluated."""
    result = run_gate(
        "scripts/check_skill_cut_safety.py",
        "--repo-root", str(ROOT),
        "--path", "skills/public/release/references/critique-boundary.md",
        "--json",
    )
    assert result.returncode != 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "unscoped"
    assert payload["unscoped_paths"] == ["skills/public/release/references/critique-boundary.md"]


def test_skill_cut_safety_named_skill_md_still_passes() -> None:
    """Control: a named SKILL.md with no broken pin is a real clean verdict."""
    result = run_gate(
        "scripts/check_skill_cut_safety.py",
        "--repo-root", str(ROOT), "--path", "skills/public/release/SKILL.md", "--json",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "clean"


def test_skill_core_headroom_absolute_path_refuses() -> None:
    """S44: `_is_skill_core_path` requires exactly four REPO-RELATIVE parts, so the
    ABSOLUTE path of a real SKILL.md was dropped and reported `status: ok`."""
    result = run_gate(
        "scripts/check_skill_surface_preflight.py",
        "--repo-root", str(ROOT),
        "--changed-skill-md", str(ROOT / "skills/public/impl/SKILL.md"),
        "--json",
    )
    assert result.returncode != 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "unscoped"
    assert payload["checked"] == []


def test_skill_core_headroom_empty_list_stays_a_pass() -> None:
    """The asymmetry, at this gate: `--changed-skill-md` with NO values is the hook
    reporting an empty changed set -- a real answer that must stay a cheap pass."""
    result = run_gate(
        "scripts/check_skill_surface_preflight.py", "--repo-root", str(ROOT), "--changed-skill-md", "--json"
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "ok"


def test_skill_core_headroom_relative_path_still_passes() -> None:
    """Control for the refusal above: the same file, named the way the commit-gate
    caller names it, is really ratcheted."""
    result = run_gate(
        "scripts/check_skill_surface_preflight.py",
        "--repo-root", str(ROOT), "--changed-skill-md", "skills/public/impl/SKILL.md", "--json",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert [row["path"] for row in payload["checked"]] == ["skills/public/impl/SKILL.md"]


def test_python_lengths_headroom_without_paths_reports_every_gated_file() -> None:
    """S39: `args.paths or []` turned an OMITTED --paths into an explicit EMPTY
    selection, so the advisory whose --help promises per-gated-file headroom
    printed `{"headroom": []}`."""
    result = run_gate("scripts/check_python_lengths.py", "--repo-root", str(ROOT), "--headroom", "--json")
    assert result.returncode == 0, result.stdout + result.stderr
    rows = json.loads(result.stdout)["headroom"]
    assert len(rows) > 1
    assert "scripts/check_python_lengths.py" in {row["path"] for row in rows}


def test_python_lengths_unresolvable_named_path_refuses() -> None:
    """S40: a named path that resolves to nothing (a typo, or paths expressed
    relative to a subdirectory) measured zero files and printed `Validated ... 0
    file(s).` -- a hard length gate passing over nothing."""
    result = run_gate(
        "scripts/check_python_lengths.py", "--repo-root", str(ROOT), "--paths", "scripts/no_such_file.py"
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "resolve to nothing" in (result.stdout + result.stderr)


def test_python_lengths_named_ungated_paths_pass_without_a_validated_verdict() -> None:
    """The false-refusal boundary, and why this half is NOT a refusal: the staged
    pre-commit caller hands over staged .py files, and real ones sit outside the
    gated globs (`runtime_bootstrap.py`, the generated `plugins/` mirror). Failing
    those would block a legitimate commit -- but the run may not claim it validated."""
    result = run_gate(
        "scripts/check_python_lengths.py", "--repo-root", str(ROOT), "--paths", "runtime_bootstrap.py"
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Validated Python length limits for 0 file(s)." not in result.stdout
    assert "nothing was validated" in result.stdout


def test_python_lengths_named_gated_path_still_validates() -> None:
    """Control: the ordinary staged-file invocation still measures and passes."""
    result = run_gate(
        "scripts/check_python_lengths.py",
        "--repo-root", str(ROOT), "--paths", "scripts/check_python_lengths.py",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Validated Python length limits for 1 file(s)." in result.stdout


def test_skill_cut_safety_unscoped_human_output_names_the_paths_and_the_remedy() -> None:
    """The operator-facing half of the S43 refusal.

    In-process on purpose. The `--json` arm above is exercised through `run_gate`,
    a subprocess the coverage mapper cannot attribute, so the human renderer's
    `unscoped` branch read as untested and the armed changed-line gate blocked on
    it. That is issue #465's class arriving in the very slice that closed S43.

    A refusal whose message does not name what it refused, or what to do instead,
    is a refusal the operator can only work around.
    """
    cut_safety = _MODULES["scripts/check_skill_cut_safety.py"]
    report = {
        "status": "unscoped",
        "skills": [],
        "unscoped_paths": [
            "skills/public/release/references/critique-boundary.md",
            "docs/handoff.md",
        ],
    }

    text = cut_safety.format_human(report)

    assert text.splitlines()[0] == "skill-cut-safety: unscoped"
    for path in report["unscoped_paths"]:
        assert path in text
    assert "nothing was checked" in text
    assert "Name the SKILL.md" in text  # the remedy, not just the refusal

    # Control: a real clean verdict does not borrow the unscoped narration.
    clean = cut_safety.format_human({"status": "clean", "skills": []})
    assert "nothing was checked" not in clean
    assert "no changed public/support SKILL.md surfaces to check." in clean
