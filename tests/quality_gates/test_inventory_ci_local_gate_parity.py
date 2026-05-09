from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/inventory_ci_local_gate_parity.py"


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


def test_documented_marker_via_step_name(tmp_path: Path) -> None:
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
    assert payload["parity_issues"] == []


def test_documented_marker_via_leading_comment(tmp_path: Path) -> None:
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
    assert payload["parity_issues"] == []


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
    assert "canonical local gate" in result.stdout
    assert "CI-only" in result.stdout
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
    repo_root = Path(__file__).resolve().parents[2]
    result = run_script(SCRIPT, "--repo-root", str(repo_root), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["parity_issues"] == []
    if payload["workflows_scanned"] == 0:
        return
    assert payload["jobs_without_canonical_gate"] == []
