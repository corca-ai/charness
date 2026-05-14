from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/inventory_ci_local_gate_parity.py"
REPO_ROOT = Path(__file__).resolve().parents[2]


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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {
        "workflows_scanned": 0,
        "workflows": [],
        "parity_issues": [],
        "jobs_without_canonical_gate": [],
        "exempt_workflows": [],
    }


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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["parity_issues"] == []
    assert payload["jobs_without_canonical_gate"] == []
    assert len(payload["exempt_workflows"]) == 1
    assert payload["exempt_workflows"][0]["gate_policy"] == "scheduled-deeper-check"


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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    # Marker buried inside a step body does not exempt: parser stops at the
    # first non-comment line (`name:`).
    assert payload["exempt_workflows"] == []


def test_gate_policy_marker_after_yaml_content_is_ignored(tmp_path: Path) -> None:
    repo = _write_workflow(
        tmp_path,
        """name: verify
# charness:gate-policy scheduled-deeper-check
on: [push]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: mutmut run
""",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    # Marker must come BEFORE non-comment YAML; placement after `name:`
    # does not exempt the workflow.
    assert payload["exempt_workflows"] == []
    assert len(payload["jobs_without_canonical_gate"]) == 1


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
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert [issue["run"] for issue in payload["parity_issues"]] == [
        "extra-required-check"
    ]


def test_does_not_flag_when_canonical_gate_absent(tmp_path: Path) -> None:
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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


def test_real_repo_workflows_or_zero_parity_issues(tmp_path: Path) -> None:
    """Real-repo smoke test: charness has no .github/workflows/ today.

    Pin both branches of the dual contract: either the repo has zero
    workflows scanned (the current charness shape, no dogfood surface) OR,
    once a workflow lands, the helper still reports zero parity-issues.
    The test will start firing the first time a workflow is added without
    aligning the local gate, which is exactly the watchdog signal #137
    asks for.
    """
    result = run_script(SCRIPT, "--repo-root", str(REPO_ROOT), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["parity_issues"] == []
    if payload["workflows_scanned"] == 0:
        return
    assert payload["jobs_without_canonical_gate"] == []


def test_repo_does_not_reintroduce_pytest_ci_only_marker() -> None:
    mark_literal = "pytest.mark." + "ci_only"
    pyproject_literal = '"ci' + '_only:'
    offenders: list[str] = []
    for path in [REPO_ROOT / "pyproject.toml", *sorted((REPO_ROOT / "tests").rglob("*.py"))]:
        text = path.read_text(encoding="utf-8")
        if mark_literal in text or pyproject_literal in text:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())
    assert offenders == []
