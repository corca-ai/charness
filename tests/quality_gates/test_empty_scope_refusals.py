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

import subprocess
from pathlib import Path

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

# In-process, not subprocess: this repo ratchets the test-suite process boundary
# down (43% of test files drive a nested CLI, which is what makes the suite
# subprocess-bound), so a new gate-behavior file must not add three more.
_MODULES = {
    name: load_script_module(name.removesuffix(".py").replace("/", "_"), ROOT / name)
    for name in (
        "scripts/validate_packaging.py",
        "scripts/check_bootstrap_shim_consistency.py",
        "scripts/validate_critique_artifacts.py",
        "scripts/validate_retro_artifact.py",
        "scripts/validate_ideation_artifact.py",
        "scripts/check_mutation_run_proof.py",
        "scripts/check_code_lengths.py",
        "scripts/check_skill_bootstrap_vars.py",
        "scripts/check_skill_cut_safety.py",
        "scripts/check_skill_surface_preflight.py",
        "scripts/check_test_repo_copy_invariants.py",
        "scripts/validate_integrations.py",
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "scripts/check_coverage.py",
    )
}


_CODE_LENGTHS = _MODULES["scripts/check_code_lengths.py"]


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
        # The `no bootstrap shim copies found under <root>` sentence was deleted with
        # `--json` on 2026-08-14; the same refusal now rides on `status: empty-scope`,
        # `checked_files: 0`, `scanned_repo_root` and this remedy line.
        ("scripts/check_bootstrap_shim_consistency.py", [], "nothing was compared"),
        # S42: zero SKILL.md under the named root.
        ("scripts/check_skill_bootstrap_vars.py", [], "no public/support SKILL.md files found"),
        # S46: no tests/ means the gate inspected no Python files.
        ("scripts/check_test_repo_copy_invariants.py", [], "no test Python files found"),
        # S49: every per-manifest rule iterates a hardcoded glob under the root.
        ("scripts/validate_integrations.py", [], "no integration manifests found"),
    ],
)
def test_zero_scope_scan_refuses(tmp_path: Path, script: str, args: list[str], expected_fragment: str) -> None:
    result = run_gate(script, "--repo-root", str(_empty_root(tmp_path)), *args)
    assert result.returncode != 0, result.stdout + result.stderr
    assert expected_fragment.lower() in (result.stdout + result.stderr).lower()


def test_bootstrap_shim_payload_names_the_empty_scope(tmp_path: Path) -> None:
    """The payload consumer must see a state distinct from `ok`, not `ok` with a
    zero count it has to notice on its own."""
    result = run_gate(
        "scripts/check_bootstrap_shim_consistency.py", "--repo-root", str(_empty_root(tmp_path))
    )
    payload = yaml.safe_load(result.stdout)
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


def test_named_critique_path_traversal_refuses(tmp_path: Path) -> None:
    result = run_gate(
        "scripts/validate_critique_artifacts.py",
        "--repo-root", str(tmp_path),
        "--paths", "charness-artifacts/critique/../../outside.md",
    )
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
    verdict = yaml.safe_load(result.stdout)
    assert verdict["provable"] is False
    assert expected_fragment in verdict["reason"]


def test_mutation_run_proof_still_confirms_a_green_identified_run() -> None:
    result = run_gate(
        "scripts/check_mutation_run_proof.py",
        "--claim", "score", "--event", "schedule", "--conclusion", "success",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = yaml.safe_load(result.stdout)
    assert verdict["provable"] is True
    assert verdict["conclusion_established"] is True


def test_provable_says_whether_the_run_was_known_green() -> None:
    """A manifest carries no conclusion, so `provable` there means "this trigger
    could evaluate the claim", not "and the run was green". The verdict must not
    let one word carry both."""
    result = run_gate("scripts/check_mutation_run_proof.py", "--claim", "score", "--event", "schedule")
    verdict = yaml.safe_load(result.stdout)
    assert verdict["provable"] is True
    assert verdict["conclusion_established"] is False


def test_known_red_run_is_distinguishable_from_unknown_conclusion() -> None:
    """Both refuse, for opposite reasons. A consumer reading a missing field as
    False would collapse "known red" into "nobody checked"."""
    red = run_gate(
        "scripts/check_mutation_run_proof.py",
        "--claim", "score", "--event", "schedule", "--conclusion", "failure",
    )
    verdict = yaml.safe_load(red.stdout)
    assert red.returncode != 0
    assert verdict["provable"] is False
    assert verdict["conclusion_established"] is True


# --- 2026-07-28 triage sweep, class (a): a glob that matched NOTHING reported a
# successful validation. Same two rules as above, applied per gate: a scope the
# CALLER NAMED that resolves to nothing refuses; a DISCOVERED empty set stays a
# pass. The third shape these added: named paths this gate does not govern
# (`plugins/` mirrors, root-level helpers) stay a pass, but may not print a
# `Validated ... 0 file(s)` verdict.


def test_skill_cut_safety_named_non_skill_path_refuses() -> None:
    """S43: `--path` is how a caller ASKS whether a cut is safe. A named path this
    gate cannot judge (a references/*.md contract home) answered `clean` over zero
    checks -- a green verdict for a question that was never evaluated."""
    result = run_gate(
        "scripts/check_skill_cut_safety.py",
        "--repo-root", str(ROOT),
        "--path", "skills/public/release/references/critique-boundary.md",
    )
    assert result.returncode != 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "unscoped"
    assert payload["unscoped_paths"] == ["skills/public/release/references/critique-boundary.md"]


def test_skill_cut_safety_named_skill_md_still_passes() -> None:
    """Control: a named SKILL.md with no broken pin is a real clean verdict."""
    result = run_gate(
        "scripts/check_skill_cut_safety.py",
        "--repo-root", str(ROOT), "--path", "skills/public/release/SKILL.md",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "clean"


def test_skill_core_headroom_absolute_path_refuses() -> None:
    """S44: `_is_skill_core_path` requires exactly four REPO-RELATIVE parts, so the
    ABSOLUTE path of a real SKILL.md was dropped and reported `status: ok`."""
    result = run_gate(
        "scripts/check_skill_surface_preflight.py",
        "--repo-root", str(ROOT),
        "--changed-skill-md", str(ROOT / "skills/public/impl/SKILL.md"),
    )
    assert result.returncode != 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "unscoped"
    assert payload["checked"] == []


def test_skill_core_headroom_empty_list_stays_a_pass() -> None:
    """The asymmetry, at this gate: `--changed-skill-md` with NO values is the hook
    reporting an empty changed set -- a real answer that must stay a cheap pass."""
    result = run_gate(
        "scripts/check_skill_surface_preflight.py", "--repo-root", str(ROOT), "--changed-skill-md"
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "ok"


def test_skill_core_headroom_relative_path_still_passes() -> None:
    """Control for the refusal above: the same file, named the way the commit-gate
    caller names it, is really ratcheted."""
    result = run_gate(
        "scripts/check_skill_surface_preflight.py",
        "--repo-root", str(ROOT), "--changed-skill-md", "skills/public/impl/SKILL.md",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "ok"
    assert [row["path"] for row in payload["checked"]] == ["skills/public/impl/SKILL.md"]


def test_code_lengths_headroom_without_paths_reports_every_gated_file() -> None:
    """S39: `args.paths or []` turned an OMITTED --paths into an explicit EMPTY
    selection, so the advisory whose --help promises per-gated-file headroom
    printed `{"headroom": []}`."""
    result = run_gate("scripts/check_code_lengths.py", "--repo-root", str(ROOT), "--headroom")
    assert result.returncode == 0, result.stdout + result.stderr
    rows = yaml.safe_load(result.stdout)["headroom"]
    assert len(rows) > 1
    assert "scripts/check_code_lengths.py" in {row["path"] for row in rows}


def test_code_lengths_unresolvable_named_path_refuses() -> None:
    """S40: a named path that resolves to nothing (a typo, or paths expressed
    relative to a subdirectory) measured zero files and printed `Validated ... 0
    file(s).` -- a hard length gate passing over nothing."""
    result = run_gate(
        "scripts/check_code_lengths.py", "--repo-root", str(ROOT), "--paths", "scripts/no_such_file.py"
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "resolve to nothing" in (result.stdout + result.stderr)


def test_code_lengths_named_ungated_paths_pass_without_a_validated_verdict() -> None:
    """The false-refusal boundary, and why this half is NOT a refusal: the staged
    pre-commit caller hands over staged .py files, and real ones sit outside the
    gated globs (`runtime_bootstrap.py`, the generated `plugins/` mirror). Failing
    those would block a legitimate commit -- but the run may not claim it validated."""
    result = run_gate(
        "scripts/check_code_lengths.py", "--repo-root", str(ROOT), "--paths", "runtime_bootstrap.py"
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # Formatted from the gate's own template, not re-spelled: renaming this message
    # used to mean chasing string literals across test files serially. The COUNT is
    # still the assertion -- a run that validated nothing may not claim a verdict.
    assert _CODE_LENGTHS.validated_verdict(0) not in result.stdout
    assert "nothing was validated" in result.stdout


def test_code_lengths_named_gated_path_still_validates() -> None:
    """Control: the ordinary staged-file invocation still measures and passes."""
    result = run_gate(
        "scripts/check_code_lengths.py",
        "--repo-root", str(ROOT), "--paths", "scripts/check_code_lengths.py",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert _CODE_LENGTHS.validated_verdict(1) in result.stdout


def test_skill_cut_safety_unscoped_payload_names_the_paths_and_the_remedy() -> None:
    """The operator-facing half of the S43 refusal.

    In-process on purpose. The end-to-end arm above is exercised through
    `run_gate`, a subprocess the coverage mapper cannot attribute, so the
    `unscoped` branch of the emitted document read as untested and the armed
    changed-line gate blocked on it. That is issue #465's class arriving in the
    very slice that closed S43.

    `format_human` was deleted with `--json` on 2026-08-14 and its narration folded
    into `report_payload`. A refusal whose payload does not name what it refused,
    or what to do instead, is still a refusal the operator can only work around.
    """
    cut_safety = _MODULES["scripts/check_skill_cut_safety.py"]
    report = {
        "status": "unscoped",
        "skills": [],
        "unscoped_paths": [
            "skills/public/release/references/critique-boundary.md",
            "docs/index.md",
        ],
    }

    payload = cut_safety.report_payload(report)

    assert payload["status"] == "unscoped"
    for path in report["unscoped_paths"]:
        assert path in payload["summary"]
    assert "nothing was checked" in payload["summary"]
    assert "Name the SKILL.md" in payload["remedy"]  # the remedy, not just the refusal

    # Control: a real clean verdict does not borrow the unscoped narration.
    clean = cut_safety.report_payload({"status": "clean", "skills": []})
    assert "nothing was checked" not in clean["summary"]
    assert clean["summary"] == "no changed public/support SKILL.md surfaces to check."
    assert "remedy" not in clean


# --- 2026-08-01, triage-sweep rows S1/S26/S30/S32. Same rule, four more surfaces:
# a denominator that reached zero must be a value in the payload, and a scope the
# CALLER NAMED that resolved to nothing must refuse. Each pairs its refusal with a
# positive control, because a gate that always fails passes every refusal test.


def test_per_file_floor_over_zero_files_is_not_enforced() -> None:
    """S1: `build_per_file_floor_report([])` self-declared `status: "enforced"` with
    every bucket empty — a fully green per-file floor report over a population of
    zero, reachable from a coverage JSON read with the wrong key, a scope filter
    that matched nothing, or a failed producer. The sibling summary in the same
    subsystem already answered this with `measurement_scope`; the floor now does.
    """
    lib = load_script_module("scripts_check_coverage_lib", ROOT / "scripts/check_coverage_lib.py")

    empty = lib.build_per_file_floor_report([])
    assert empty["status"] == "unestablished"
    assert empty["measurement_scope"] == "empty"
    assert empty["files_evaluated"] == 0

    # Control: a real population still reports an enforced floor, and still finds
    # the violation in it. An implementation that returned "unestablished" always
    # would pass the assertions above.
    evaluated = lib.build_per_file_floor_report(
        [{"path": "a.py", "covered": 10, "total": 100, "coverage": 0.10}], floor=0.85
    )
    assert evaluated["status"] == "enforced"
    assert evaluated["measurement_scope"] == "evaluated"
    assert [item["path"] for item in evaluated["violations"]] == ["a.py"]


def _workflow_repo(tmp_path: Path, name: str, body: str) -> Path:
    repo = tmp_path / "wf-repo"
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / name).write_text(body, encoding="utf-8")
    return repo


_PARITY_WORKFLOW = (
    "name: ci\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
    "    steps:\n      - run: npm run verify\n      - run: npm run secret-scan\n"
)
_ALL_USES_WORKFLOW = (
    "name: ci\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
    "    steps:\n      - uses: actions/checkout@v4\n      - uses: ./.github/actions/run-everything\n"
)


@pytest.mark.parametrize("suffix", ["yml", "yaml"])
def test_parity_gate_reads_both_workflow_extensions(tmp_path: Path, suffix: str) -> None:
    """S30: GitHub Actions accepts both extensions and the default glob read only
    `.yml`, so the identical workflow saved as `ci.yaml` scanned 0 files and exited
    0 where `ci.yml` raised a parity issue and exited 1. The denominator, not the
    verdict, was wrong.
    """
    repo = _workflow_repo(tmp_path, f"ci.{suffix}", _PARITY_WORKFLOW)
    result = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(repo),
        "--require-empty-parity-issues",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "secret-scan" in result.stdout + result.stderr


def test_parity_gate_refuses_a_named_glob_that_matched_nothing(tmp_path: Path) -> None:
    """A scope the caller NAMED that resolves to nothing is a failed assertion."""
    repo = _workflow_repo(tmp_path, "ci.yml", _PARITY_WORKFLOW)
    result = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(repo),
        "--workflow-glob",
        ".github/workflows/*.toml",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "matched no workflow file" in result.stdout + result.stderr


def test_parity_gate_discovered_empty_scope_stays_a_pass(tmp_path: Path) -> None:
    """Control, and the asymmetry this file exists to pin: a repo with no workflows
    at all is a real answer, not a failed assertion. It must still SAY it evaluated
    nothing."""
    repo = tmp_path / "no-workflows"
    repo.mkdir()
    result = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(repo),
        "--require-empty-parity-issues",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "establishes NOTHING" in result.stdout + result.stderr


def test_parity_gate_names_a_job_it_could_not_read(tmp_path: Path) -> None:
    """S26: a job whose steps are all `uses:` was dropped by a bare `continue`, so
    it was indistinguishable from a job that passed. The canonical gate may run
    inside the composite action; this reader cannot open it. Unestablished is its
    own answer.
    """
    repo = _workflow_repo(tmp_path, "ci.yml", _ALL_USES_WORKFLOW)
    result = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(repo),
        "--require-established-gate-match",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "gate-match-unestablished" in result.stdout + result.stderr

    # Control: the same flag over a job whose gate IS visible stays a pass, so the
    # refusal is about the unreadable job and not about the flag.
    ok_repo = _workflow_repo(
        tmp_path,
        "ci.yml",
        "name: ci\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: npm run verify\n",
    )
    ok = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(ok_repo),
        "--require-established-gate-match",
        "--require-canonical-gate-match",
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr

    # ...and the OLD flag does not fire on the unreadable job: round 1 established
    # that a composite-action wrapper is an honest CI shape whose only escapes from
    # a folded-in refusal were dropping real teeth or misusing a gate-policy marker.
    unfolded = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(repo),
        "--require-canonical-gate-match",
    )
    assert unfolded.returncode == 0, unfolded.stdout + unfolded.stderr


# --- Round 2 of the same slice: cases round 1 established the first cut missed.


def test_parity_gate_names_a_job_level_reusable_workflow_call(tmp_path: Path) -> None:
    """The S26 class in its more common shape, which the first cut still dropped:
    `jobs.<id>.uses:` has NO `steps` key, so it fell through the `not steps` skip
    into no bucket at all — exit 0 with every list empty, verified by execution
    before this repair. That is how repos factor a whole gate graph.
    """
    repo = _workflow_repo(
        tmp_path,
        "ci.yml",
        "name: ci\non: [push]\njobs:\n  build:\n    uses: ./.github/workflows/run-everything.yml\n",
    )
    result = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(repo),
        "--require-established-gate-match",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "gate-match-unestablished" in result.stdout + result.stderr

    # Control: a job with neither steps nor `uses:` genuinely runs nothing, so it
    # stays a silent skip rather than joining the unestablished bucket.
    empty_job = _workflow_repo(
        tmp_path, "ci.yml", "name: ci\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
    )
    ok = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(empty_job),
        "--require-established-gate-match",
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr


def test_parity_named_scope_refusal_carries_a_payload(tmp_path: Path) -> None:
    """The structured refusal stays readable by the current YAML consumer."""
    repo = _workflow_repo(tmp_path, "ci.yml", _PARITY_WORKFLOW)
    result = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(repo),
        "--workflow-glob",
        ".github/workflows/*.toml",
        "--detail",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "named-scope-empty"
    assert payload["jobs_evaluated"] == 0
    assert "Remedy" in payload["reason"]


def test_parity_require_evaluated_scope_has_both_arms(tmp_path: Path) -> None:
    """The flag shipped untested in the first cut. Both arms, because a flag that
    always refuses and a flag that never refuses both pass a one-arm test."""
    exempt = _workflow_repo(
        tmp_path,
        "ci.yml",
        "# charness:gate-policy scheduled-deeper-check\nname: ci\non: [push]\njobs:\n"
        "  build:\n    runs-on: ubuntu-latest\n    steps:\n      - run: mutmut run\n",
    )
    refused = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(exempt),
        "--require-evaluated-scope",
    )
    assert refused.returncode == 1, refused.stdout + refused.stderr

    evaluated = _workflow_repo(
        tmp_path,
        "ci.yml",
        "name: ci\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: npm run verify\n",
    )
    passed = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(evaluated),
        "--require-evaluated-scope",
        "--detail",
    )
    assert passed.returncode == 0, passed.stdout + passed.stderr
    # A nonzero denominator, asserted: every other pin on these fields is a zero,
    # so a refactor that made `jobs_evaluated` always 0 would pass all of them.
    assert yaml.safe_load(passed.stdout)["jobs_evaluated"] == 1


def test_per_file_floor_over_an_all_exempt_population_is_not_enforced() -> None:
    """Round 1's blocker on the S1 slice: the first cut keyed `status` on the INPUT
    length, so a population that is entirely unmeasured or entirely below the
    statement threshold still self-declared `enforced` with an empty `violations`
    list — the same green, one bucket over.
    """
    lib = load_script_module("scripts_check_coverage_lib", ROOT / "scripts/check_coverage_lib.py")

    all_exempt = lib.build_per_file_floor_report(
        [{"path": "a.py", "covered": 0, "total": 5, "coverage": 0.0}]
    )
    assert all_exempt["status"] == "unestablished"
    assert all_exempt["files_received"] == 1
    assert all_exempt["files_evaluated"] == 0

    all_unmeasured = lib.build_per_file_floor_report(
        [{"path": "b.py", "covered": 0, "total": 0, "coverage": 1.0}]
    )
    assert all_unmeasured["status"] == "unestablished"
    assert all_unmeasured["files_evaluated"] == 0

    # Control: one comparable file among exempt ones restores an enforced verdict.
    mixed = lib.build_per_file_floor_report(
        [
            {"path": "a.py", "covered": 0, "total": 5, "coverage": 0.0},
            {"path": "b.py", "covered": 90, "total": 100, "coverage": 0.90},
        ],
        floor=0.85,
    )
    assert mixed["status"] == "enforced"
    assert mixed["files_evaluated"] == 1


def test_per_file_floor_payload_names_the_unestablished_scope() -> None:
    """The emitted document is the operator surface, and the branch that says
    "zero files reached the comparison" had no test — the exact shape #465 punished
    when an unrendered branch met the armed changed-line gate.

    `format_per_file_floor_line` was deleted with `--json` on 2026-08-14; the
    caveat it carried is now `per_file_floor_caveat` on the emitted payload, and
    `coverage_report` takes the WHOLE summary rather than the floor report alone."""
    check_coverage = _MODULES["scripts/check_coverage.py"]
    empty = {"measurement_scope": "empty", "files_received": 3, "files_evaluated": 0}
    caveat = check_coverage.coverage_report({"per_file_floor": empty})["per_file_floor_caveat"]
    assert "UNESTABLISHED" in caveat
    assert "received 3" in caveat

    populated = {
        "measurement_scope": "evaluated",
        "files_received": 2,
        "files_evaluated": 2,
        "violations": [{"path": "a.py", "coverage": 0.1}],
        "warn_band": [],
    }
    assert "per_file_floor_caveat" not in check_coverage.coverage_report(
        {"per_file_floor": populated}
    )

    # A payload MISSING the key must fail closed onto the caveat, not take the
    # green numeric arm — round 1, MINOR 2.
    assert "UNESTABLISHED" in check_coverage.coverage_report(
        {"per_file_floor": {"violations": [], "warn_band": []}}
    )["per_file_floor_caveat"]


def test_parity_gate_names_a_job_whose_steps_it_could_not_parse(tmp_path: Path) -> None:
    """Round 2: a `steps:` key the reader could not parse (the repo's loader returns
    a YAML flow sequence as a string) landed in NO bucket — the S26 escape surviving
    in a third shape, on valid GitHub Actions YAML."""
    repo = _workflow_repo(
        tmp_path,
        "ci.yml",
        "name: ci\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
        "    steps: [{run: npm test}, {run: npm run secret-scan}]\n",
    )
    result = run_gate(
        "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
        "--repo-root",
        str(repo),
        "--require-established-gate-match",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "gate-match-unestablished" in result.stdout + result.stderr
