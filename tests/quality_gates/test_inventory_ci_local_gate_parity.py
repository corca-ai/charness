from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module
from tests.script_main import run_loaded_script_main

from .seeding_support import load_module
from .support import run_script as subprocess_run_script

SCRIPT = "skills/public/quality/scripts/inventory_ci_local_gate_parity.py"
REPO_ROOT = Path(__file__).resolve().parents[2]
_argparse_surface = import_repo_module(
    REPO_ROOT / "scripts/core/argparse_surface_lib.py", "scripts.core.argparse_surface_lib"
)
_MODULE = load_module(
    "inventory_ci_local_gate_parity_under_test",
    REPO_ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_ci_local_gate_parity.py",
)
VisibleRepoFilesSnapshot = sys.modules["git_inventory_lib"].VisibleRepoFilesSnapshot


def run_script(*args: str, real_inventory: bool = False):
    if real_inventory:
        return subprocess_run_script(*args)
    original_capture = _MODULE.capture_visible_repo_files
    _MODULE.capture_visible_repo_files = lambda _repo, **_kwargs: VisibleRepoFilesSnapshot(None)
    try:
        return run_loaded_script_main(str(args[0]), _MODULE, *args[1:])
    finally:
        _MODULE.capture_visible_repo_files = original_capture


def _write_workflow(tmp_path: Path, body: str) -> Path:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    workflows.mkdir(parents=True)
    target = workflows / "verify.yml"
    target.write_text(body, encoding="utf-8")
    return repo


def test_silent_when_no_workflows(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    # Still exact-equality, and still a clean exit: a DISCOVERED empty scope stays
    # a pass (`test_empty_scope_refusals.py`'s rule). What the payload gained is the
    # denominator — `workflows_not_exempt` / `jobs_evaluated` — because scanned-but-
    # all-exempt used to be indistinguishable from every-job-checked-and-passed.
    assert payload == {
        "status": "nothing-evaluated",
        "workflows_scanned": 0,
        "workflows_not_exempt": 0,
        "jobs_evaluated": 0,
        "workflows": [],
        "parity_issues": [],
        "jobs_without_canonical_gate": [],
        "jobs_gate_match_unestablished": [],
        "exempt_workflows": [],
    }


def test_output_modes_keep_json_compatibility_and_offer_yaml_triage(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
      - run: npm run lint:strict
""",
    )
    full_json = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert full_json.returncode == 0, full_json.stderr
    assert "parity_issues" in yaml.safe_load(full_json.stdout)

    summary = run_script(SCRIPT, "--repo-root", str(repo), "--summary")
    assert summary.returncode == 0, summary.stderr
    assert "parity_issue_count: 1" in summary.stdout
    assert "workflows:" not in summary.stdout

    detail = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert detail.returncode == 0, detail.stderr
    assert "parity_issues:" in detail.stdout

    summary_json = run_script(SCRIPT, "--repo-root", str(repo), "--summary")
    assert summary_json.returncode == 0, summary_json.stderr
    assert yaml.safe_load(summary_json.stdout)["parity_issue_count"] == 1


@pytest.mark.boundary_contract(
    reason="target spawns git and this test observes the exact unavailable-listing stderr contract"
)
def test_strict_workflow_listing_fails_closed_outside_git(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "verify.yml").write_text("name: verify\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--require-git-file-listing",
        "--detail",
        real_inventory=True,
    )

    assert result.returncode == 1
    assert "CI/local gate parity workflow listing failed" in result.stderr
    assert "command: git ls-files -z --cached --others --exclude-standard" in result.stderr


def test_flags_required_steps_after_npm_run_verify(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run verify
      - run: npm run test:coverage
      - run: npm run coverage:floor:check
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    issue_runs = sorted(issue["run"] for issue in payload["parity_issues"])
    assert issue_runs == ["npm run coverage:floor:check", "npm run test:coverage"]


def test_classifies_setup_steps_as_setup(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    classifications = sorted(
        entry["classification"]
        for workflow in payload["workflows"]
        for job in workflow["jobs"]
        for entry in job["subsequent"]
    )
    assert classifications == ["setup", "setup"]
    assert payload["parity_issues"] == []


def test_ci_only_marker_via_step_name_is_violation(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
      - name: Upload coverage (CI-only)
        run: bash <(curl -s https://codecov.io/bash)
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["parity_issues"] == [
        {
            "workflow": str(repo / ".github/workflows/verify.yml"),
            "job": "verify",
            "name": "Upload coverage (CI-only)",
            "run": "bash <(curl -s https://codecov.io/bash)",
            "uses": None,
            "classification": "ci-only-violation",
        }
    ]


def test_ci_only_marker_via_leading_comment_is_violation(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
      # CI-only: requires CODECOV_TOKEN secret
      - run: bash <(curl -s https://codecov.io/bash)
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["parity_issues"][0]["classification"] == "ci-only-violation"


def test_text_summary_lists_exempt_workflows(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """# charness:gate-policy scheduled-deeper-check
name: Mutation Tests
on:
  schedule:
    - cron: "17 */3 * * *"
jobs:
  mutation:
    runs-on: ubuntu-latest
    steps:
      - run: mutmut run
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "exempt " in result.stdout
    assert "gate-policy=scheduled-deeper-check" in result.stdout


def test_scheduled_deeper_check_marker_exempts_workflow(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """# charness:gate-policy scheduled-deeper-check
name: Mutation Tests
on:
  schedule:
    - cron: "17 */3 * * *"
jobs:
  mutation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: mutmut run
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["parity_issues"] == []
    assert payload["jobs_without_canonical_gate"] == []
    assert len(payload["exempt_workflows"]) == 1
    assert payload["exempt_workflows"][0]["gate_policy"] == "scheduled-deeper-check"


def test_local_gate_subset_mirror_marker_exempts_workflow(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """# charness:gate-policy local-gate-subset-mirror
name: Quality Core
on:
  push:
    branches: [main]
jobs:
  core:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ruff check scripts
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["parity_issues"] == []
    assert payload["jobs_without_canonical_gate"] == []
    assert len(payload["exempt_workflows"]) == 1
    assert payload["exempt_workflows"][0]["gate_policy"] == "local-gate-subset-mirror"


def test_gate_policy_marker_must_be_known_keyword(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """# charness:gate-policy unknown-policy
name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: mutmut run
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    # Unknown keyword falls back to standard gate-parity enforcement,
    # so the workflow is NOT exempt and surfaces jobs_without_canonical_gate.
    assert payload["exempt_workflows"] == []
    assert len(payload["jobs_without_canonical_gate"]) == 1


def test_gate_policy_unknown_keyword_emits_stderr_warning(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """# charness:gate-policy scheduledd-deeper-check
name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: mutmut run
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0
    assert "unknown gate-policy" in result.stderr
    assert "'scheduledd-deeper-check'" in result.stderr


def test_gate_policy_earlier_unknown_marker_does_not_shadow_later_valid(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """# charness:gate-policy unknown-policy
# charness:gate-policy scheduled-deeper-check
name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: mutmut run
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    # First marker keyword wins. Earlier unknown keyword means the workflow
    # is NOT exempt — operator must remove the dead marker for the real one
    # to take effect. The stderr warning surfaces the typo.
    assert payload["exempt_workflows"] == []
    assert "unknown gate-policy" in result.stderr


def test_gate_policy_marker_inside_step_run_is_ignored(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "# charness:gate-policy scheduled-deeper-check"
          mutmut run
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    # Marker buried inside a step body does not exempt: parser stops at the
    # first non-comment line (`name:`).
    assert payload["exempt_workflows"] == []


def test_require_empty_parity_issues_returns_nonzero_when_violation(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
      - run: npm run lint:strict
""",
    )
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--require-empty-parity-issues",
    )
    assert result.returncode == 1, result.stdout
    assert "npm run lint:strict" in result.stdout


def test_canonical_gate_pattern_override(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: ./repo-gate.sh
      - run: extra-required-check
""",
    )
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--canonical-gate-pattern",
        r"\./repo-gate\.sh",
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [issue["run"] for issue in payload["parity_issues"]] == ["extra-required-check"]


def test_ci_parity_reads_consumer_gate_patterns_and_refuses_unmatched_gate(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: ./consumer-gate.sh
      - run: npm run extra-required
""",
    )
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nuniverses:\n"
        "  ci_gate_patterns:\n    - '\\./missing-gate\\.sh'\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["jobs_without_canonical_gate"] == [
        {"workflow": str(repo / ".github/workflows/verify.yml"), "jobs": ["verify"]}
    ]


def test_ci_parity_refuses_empty_declared_gate_patterns(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: ./consumer-gate.sh
""",
    )
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nuniverses:\n  ci_gate_patterns: []\n",
        encoding="utf-8",
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")

    assert result.returncode == 1
    assert "inventory-ci-local-gate-parity: refusing empty declared universe" in result.stdout


def test_default_patterns_anchor_each_shipped_run_quality_invocation(tmp_path: Path) -> None:
    invocations = (
        "bash scripts/run-quality.sh",
        "bash ./scripts/run-quality.sh --read-only",
        "CHARNESS_RUNTIME_REGIME=docs-only ./scripts/run-quality.sh --read-only",
    )
    for invocation in invocations:
        repo = _write_workflow(
            tmp_path / invocation.replace("/", "-").replace(" ", "-"),
            f"""name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: {invocation}
      - run: required-after-runner
""",
        )

        result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")

        assert result.returncode == 0, result.stderr
        payload = yaml.safe_load(result.stdout)
        assert [issue["run"] for issue in payload["parity_issues"]] == ["required-after-runner"]
        assert payload["jobs_without_canonical_gate"] == []


def test_default_patterns_ignore_non_invocation_runner_mentions(tmp_path: Path) -> None:
    mentions = (
        "echo ./scripts/run-quality.sh",
        "test -x ./scripts/run-quality.sh",
        "RUNNER=./scripts/run-quality.sh",
        "# ./scripts/run-quality.sh",
        "./scripts/run-quality.sh.bak",
        "./scripts/run-quality.shx",
    )
    for mention in mentions:
        repo = _write_workflow(
            tmp_path / mention.replace("/", "-").replace(" ", "-"),
            f"""name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: |
          {mention}
          required-after-mention
""",
        )

        result = run_script(
            SCRIPT,
            "--repo-root",
            str(repo),
            "--require-canonical-gate-match",
            "--detail",
        )

        assert result.returncode == 1, result.stderr
        payload = yaml.safe_load(result.stdout)
        assert payload["parity_issues"] == []
        assert payload["jobs_without_canonical_gate"] == [
            {"workflow": str(repo / ".github/workflows/verify.yml"), "jobs": ["verify"]}
        ]


def test_no_run_quality_runner_remains_advisory_without_opt_in_refusal(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: lint-only
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint
      - run: npm run typecheck
""",
    )
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--require-empty-parity-issues",
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["parity_issues"] == []
    assert payload["workflows"][0]["jobs"] == []
    assert payload["jobs_without_canonical_gate"] == [
        {"workflow": str(repo / ".github/workflows/verify.yml"), "jobs": ["lint"]}
    ]


def test_require_canonical_gate_match_returns_nonzero(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: lint-only
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: hatch run quality
""",
    )
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--require-canonical-gate-match",
    )
    assert result.returncode == 1, result.stdout
    assert "no-canonical-gate" in result.stdout


def test_uses_last_canonical_gate_when_multiple(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm ci
      - run: npm run verify
      - run: cache-warm.sh
      - run: npm run verify
      - run: npm run coverage:floor:check
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    issues = sorted(issue["run"] for issue in payload["parity_issues"])
    assert issues == ["npm run coverage:floor:check"]


def test_artifact_actions_classified_as_setup(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
      - uses: actions/upload-artifact@v4
      - uses: actions/download-artifact@v4
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    classifications = sorted(
        entry["classification"]
        for workflow in payload["workflows"]
        for job in workflow["jobs"]
        for entry in job["subsequent"]
    )
    assert classifications == ["setup", "setup"]
    assert payload["parity_issues"] == []


def test_failure_message_names_three_exits(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
      - run: npm run lint:strict
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "canonical local/pre-push gate" in result.stdout
    assert "CI-only quality gates are not an acceptable waiver" in result.stdout
    assert "maintainer-local-enforcement.md" in result.stdout


@pytest.mark.boundary_contract(
    reason="target spawns git and this test observes the real repository listing contract"
)
def test_real_repo_workflows_or_zero_parity_issues(tmp_path: Path) -> None:
    """Real-repo watchdog, with charness's ACTUAL posture pinned.

    The docstring here used to say "charness has no .github/workflows/ today",
    which stopped being true: there are two, and BOTH carry a
    `# charness:gate-policy` exemption marker. So the gate evaluates zero jobs in
    its own repo and the old `jobs_without_canonical_gate == []` assertion was
    trivially true forever — a watchdog that could not bark. The posture is now
    asserted directly, so a third workflow (exempt or not) fires this test, which
    is the signal #137 actually asked for.
    """
    result = run_script(SCRIPT, "--repo-root", str(REPO_ROOT), "--detail", real_inventory=True)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["parity_issues"] == []
    assert payload["jobs_without_canonical_gate"] == []
    assert payload["jobs_gate_match_unestablished"] == []
    # Counts, not absolute filenames: pinning the exact paths would fail on a
    # rename with an opaque set diff, while the posture — every workflow exempt —
    # is what this test is actually about.
    assert payload["workflows_scanned"] == 2
    assert len(payload["exempt_workflows"]) == payload["workflows_scanned"]
    assert payload["workflows_not_exempt"] == 0
    # The uncomfortable fact, pinned rather than left implicit: charness's own
    # parity gate establishes nothing about charness. See D45 for the open
    # question of whether run-quality.sh should arm --require-evaluated-scope.
    assert payload["jobs_evaluated"] == 0


def test_unreadable_job_shapes_land_in_the_unestablished_bucket(tmp_path: Path) -> None:
    """Two job shapes this reader cannot open must be NAMED, not silently skipped.

    Both used to fall into no bucket at all, which made "could not establish"
    indistinguishable from "checked and passed" (S26). They reach different arms:
    a truthy non-mapping job never gets as far as `steps`, while a `steps:` list
    whose members are all unreadable has steps declared and none usable.
    """
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  string_job: just-a-string
  bare_step_job:
    runs-on: ubuntu-latest
    steps:
      - a bare string step
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    unestablished = payload["jobs_gate_match_unestablished"]
    assert len(unestablished) == 1
    assert sorted(unestablished[0]["jobs"]) == ["bare_step_job", "string_job"]
    # Neither shape may be reported as a job that passed: `jobs_evaluated` is the
    # denominator, and counting an unopenable job in it is the defect itself.
    assert payload["jobs_evaluated"] == 0
    assert payload["jobs_without_canonical_gate"] == []
    assert payload["parity_issues"] == []


def test_a_falsy_non_mapping_job_is_absent_not_unreadable(tmp_path: Path) -> None:
    """The control for the arm above: `if job:` is a real distinction, not noise.

    An empty job value is nothing to read, so naming it "could not establish"
    would inflate the unestablished bucket with jobs that say nothing at all.
    """
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  empty_job:
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)

    assert payload["jobs_gate_match_unestablished"] == []
    assert payload["jobs_evaluated"] == 0


def test_named_scope_refusal_survives_summary_mode(tmp_path: Path) -> None:
    """The refusal payload must stay readable in `--summary`, not only in full mode.

    Summary mode has its own key set, so a consumer keyed on `parity_issue_count`
    used to raise on the raw refusal — "cannot tell refused from crashed" one
    register down from the defect the refusal payload exists to fix. The three
    refusal-only keys must survive summarization alongside the summary counts.
    """
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
""",
    )
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--workflow-glob",
        ".github/workflows/*.toml",
        "--summary",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    # The summary key set is present, so a summary consumer does not raise.
    assert payload["parity_issue_count"] == 0
    assert payload["jobs_evaluated"] == 0
    # And the refusal is still legible as a refusal rather than an empty pass.
    assert payload["status"] == "named-scope-empty"
    assert payload["named_workflow_globs"] == [".github/workflows/*.toml"]
    assert "matched no workflow file" in payload["reason"]


def test_named_scope_refusal_summary_yaml_names_the_glob(tmp_path: Path) -> None:
    """Summary mode carries the refusal keys needed by its consumer."""
    repo = _write_workflow(
        tmp_path,
        """name: verify
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: npm run verify
""",
    )
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--workflow-glob",
        ".github/workflows/nope-*.yml",
        "--summary",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "status: named-scope-empty" in result.stdout
    assert "nope-*.yml" in result.stdout
    assert "matched no workflow file" in result.stdout


def test_repo_does_not_reintroduce_pytest_ci_only_marker() -> None:
    mark_literal = "pytest.mark." + "ci_only"
    pyproject_literal = '"ci' + "_only:"
    offenders: list[str] = []
    for path in [REPO_ROOT / "pyproject.toml", *sorted((REPO_ROOT / "tests").rglob("*.py"))]:
        text = path.read_text(encoding="utf-8")
        if mark_literal in text or pyproject_literal in text:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())
    assert offenders == []


# The lib is loaded by PATH here, not only through the CLI above. Two reasons:
# the default pattern tuple is a shipped surface no test read, and the dotted
# `import_repo_module` form the CLI uses is invisible to the changed-line
# selector, so edits to skills/public/quality/scripts/ci_local_gate_parity_lib.py
# went unmapped locally while the remote broad mirror judged them.
_parity_lib = import_repo_module(
    REPO_ROOT / "skills/public/quality/scripts/ci_local_gate_parity_lib.py",
    "skills.public.quality.scripts.ci_local_gate_parity_lib",
)


def _charness_subcommands_named_by(patterns) -> set[str]:
    return {
        match.group(1).replace("\\s+", " ").split()[0]
        for pattern in patterns
        for match in [re.search(r"charness((?:\\s\+|\s)+[a-z0-9-]+)", pattern)]
        if match
    }


def _declared_subcommands() -> set[str]:
    help_text = subprocess.run(
        [sys.executable, "charness", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "COLUMNS": "200", "LC_ALL": "C", "LANGUAGE": ""},
    ).stdout
    return _argparse_surface.subcommand_choices(help_text)


@pytest.mark.boundary_contract(
    reason="__main__ dispatch smoke: the root charness CLI must provide its real subcommand help"
)
def test_the_dead_charness_pattern_that_shipped_would_now_be_refused() -> None:
    """The tripwire, run against the list as it SHIPPED.

    `\\bcharness\\s+verify\\b` sat in the default tuple naming a subcommand the
    CLI has never declared, so it could not match any workflow -- dead teeth that
    read as coverage. The guard below goes vacuous the moment no pattern names a
    charness subcommand, which is true today, so it is asserted here against the
    pre-repair list instead of only against the live one.
    """
    shipped = (r"\bbash\s+scripts/run-quality\.sh\b", r"\bcharness\s+verify\b")
    named = _charness_subcommands_named_by(shipped)
    assert named == {"verify"}
    assert named - _declared_subcommands() == {"verify"}


@pytest.mark.boundary_contract(
    reason="__main__ dispatch smoke: the root charness CLI must provide its real subcommand help"
)
def test_no_default_canonical_gate_pattern_names_a_charness_subcommand_that_does_not_exist() -> (
    None
):
    """Derived from `charness --help` rather than pinned to a list, so it stays
    true through a rename instead of needing a hand edit."""
    named = _charness_subcommands_named_by(_parity_lib.DEFAULT_CANONICAL_GATE_PATTERNS)
    undeclared = named - _declared_subcommands() if named else set()
    assert not undeclared, (
        f"default canonical-gate pattern(s) name non-subcommand(s): {sorted(undeclared)}"
    )


def test_default_canonical_gate_patterns_match_this_repo_s_own_local_gate() -> None:
    """A default list that matches nothing real is the failure mode above, one
    level up. charness's own canonical gate is `bash scripts/run-quality.sh`."""
    assert any(
        re.search(pattern, "bash scripts/run-quality.sh")
        for pattern in _parity_lib.DEFAULT_CANONICAL_GATE_PATTERNS
    )


def test_default_canonical_gate_patterns_cover_shipped_runner_forms() -> None:
    for invocation in (
        "bash scripts/run-quality.sh",
        "bash ./scripts/run-quality.sh --read-only",
        "CHARNESS_RUNTIME_REGIME=docs-only ./scripts/run-quality.sh --read-only",
    ):
        assert any(
            re.search(pattern, invocation)
            for pattern in _parity_lib.DEFAULT_CANONICAL_GATE_PATTERNS
        ), invocation
