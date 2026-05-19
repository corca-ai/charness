"""Acceptance checks for the mutation_testing adapter block + propose probe.

Implementation contract:
charness-artifacts/spec/quality-mutation-testing-adapter-block.md.
Cases a1-a5 + a7 live here. a6 (sync_root_plugin_manifests git-diff clean) is
exercised by repo-level CI and is asserted in the closeout flow instead.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.check_mutation_score import (  # noqa: E402
    iter_dump_records,
    summarize_survived_mutations,
)
from scripts.filter_cosmic_ray_mutants import is_function_annotation_union  # noqa: E402
from scripts.quality_adapter_lib import (  # noqa: E402
    infer_quality_defaults,
    load_quality_adapter,
    validate_quality_adapter_data,
)
from scripts.quality_policy_defaults import DEFAULT_MUTATION_TESTING  # noqa: E402

PROPOSE_SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "propose_mutation_testing.py"
TEMPLATE_PATH = ROOT / "skills" / "public" / "quality" / "scripts" / "templates" / "mutation-tests.yml"


# ---------------------------------------------------------------------------
# adapter fixture writers


def _write_adapter(repo: Path, body: str) -> Path:
    target = repo / ".agents" / "quality-adapter.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


_ADAPTER_HEADER = dedent(
    """\
    version: 1
    repo: testrepo
    language: en
    output_dir: charness-artifacts/quality
    """
)

_FULL_BLOCK = dedent(
    """\
    mutation_testing:
      commands:
        dry_run: "npm run test:mutation:dry-run"
        full: "npm run test:mutation"
        sample: "npm run test:mutation:sample"
        summary: "npm run test:mutation:ci-summary"
      score_break: 60
      schedule_cron: "17 */3 * * *"
      changed_quota: 5
      max_files: 10
      auto_issue:
        enabled: true
        label: mutation-test
        title: Mutation test regression on main
        marker_token: mutation-test-regression
      workflow_path: .github/workflows/mutation-tests.yml
      report_paths:
        summary_md: reports/mutation/summary.md
        sample_md: reports/mutation/sample.md
        log: reports/mutation/run.log
      declined: false
    """
)

_PARTIAL_BLOCK = dedent(
    """\
    mutation_testing:
      commands:
        full: "npm run test:mutation"
    """
)

_DECLINED_BLOCK = dedent(
    """\
    mutation_testing:
      declined: true
    """
)

_UNKNOWN_SUBKEY_BLOCK = dedent(
    """\
    mutation_testing:
      commands:
        full: "npm run test:mutation"
      weird: "x"
    """
)


def _resolve(repo: Path) -> dict:
    return load_quality_adapter(repo)


# ---------------------------------------------------------------------------
# a1 (5 fixtures) + a2 (type error)


def test_a1_full_block_valid_and_complete(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER + _FULL_BLOCK)
    payload = _resolve(repo)
    assert payload["valid"], payload["errors"]
    mt = payload["data"]["mutation_testing"]
    assert mt["commands"]["full"] == "npm run test:mutation"
    assert mt["commands"]["sample"] == "npm run test:mutation:sample"
    assert mt["auto_issue"]["enabled"] is True
    assert mt["auto_issue"]["marker_token"] == "mutation-test-regression"
    assert mt["report_paths"]["log"] == "reports/mutation/run.log"


def test_a1_partial_block_valid_other_slots_default(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER + _PARTIAL_BLOCK)
    payload = _resolve(repo)
    assert payload["valid"], payload["errors"]
    mt = payload["data"]["mutation_testing"]
    assert mt["commands"]["full"] == "npm run test:mutation"
    assert mt["commands"]["dry_run"] == ""
    assert mt["score_break"] == DEFAULT_MUTATION_TESTING["score_break"]


def test_a1_declined_block_valid(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER + _DECLINED_BLOCK)
    payload = _resolve(repo)
    assert payload["valid"], payload["errors"]
    assert payload["data"]["mutation_testing"]["declined"] is True


def test_a1_no_block_at_all_no_errors_no_warnings(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER)
    payload = _resolve(repo)
    assert payload["valid"], payload["errors"]
    assert payload["errors"] == []
    new_warnings = [w for w in payload["warnings"] if "mutation_testing" in w]
    assert new_warnings == []
    assert payload["data"]["mutation_testing"]["commands"]["full"] == ""


def test_a1_unknown_subkey_warns_does_not_error(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER + _UNKNOWN_SUBKEY_BLOCK)
    payload = _resolve(repo)
    assert payload["valid"], payload["errors"]
    assert any("unknown mutation_testing sub-key: weird" == w for w in payload["warnings"])
    assert payload["data"]["mutation_testing"]["commands"]["full"] == "npm run test:mutation"


def test_a2_score_break_wrong_type_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(
        repo,
        _ADAPTER_HEADER + dedent(
            """\
            mutation_testing:
              score_break: "high"
            """
        ),
    )
    payload = _resolve(repo)
    assert not payload["valid"]
    assert any("score_break must be an integer" in e for e in payload["errors"])


def test_a2_unknown_commands_subkey_warns(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(
        repo,
        _ADAPTER_HEADER + dedent(
            """\
            mutation_testing:
              commands:
                full: "x"
                bogus: "y"
            """
        ),
    )
    payload = _resolve(repo)
    assert payload["valid"], payload["errors"]
    assert any("unknown mutation_testing.commands sub-key: bogus" == w for w in payload["warnings"])


def test_a2_auto_issue_enabled_wrong_type_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(
        repo,
        _ADAPTER_HEADER + dedent(
            """\
            mutation_testing:
              auto_issue:
                enabled: "yes"
            """
        ),
    )
    payload = _resolve(repo)
    assert not payload["valid"]
    assert any("auto_issue.enabled must be a boolean" in e for e in payload["errors"])


# ---------------------------------------------------------------------------
# a3 propose probe (5 cases)


def _run_propose(repo: Path, execute: bool = False) -> dict:
    args = ["python3", str(PROPOSE_SCRIPT), "--repo-root", str(repo)]
    if execute:
        args.append("--execute")
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_a3_missing_no_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    out = _run_propose(repo)
    assert out["status"] == "missing"


def test_a3_missing_empty_commands(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER)
    out = _run_propose(repo)
    assert out["status"] == "missing"


def test_a3_installed(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER + _PARTIAL_BLOCK)
    out = _run_propose(repo)
    assert out["status"] == "installed"


def test_a3_declined(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER + _DECLINED_BLOCK)
    out = _run_propose(repo)
    assert out["status"] == "declined"


def test_a3_recovery_after_removing_declined(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    adapter = _write_adapter(repo, _ADAPTER_HEADER + _DECLINED_BLOCK)
    assert _run_propose(repo)["status"] == "declined"
    adapter.write_text(_ADAPTER_HEADER, encoding="utf-8")
    out = _run_propose(repo)
    assert out["status"] == "missing"


def test_a3_execute_appends_and_installs(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER)
    out = _run_propose(repo, execute=True)
    assert out["status"] == "installed"
    adapter_text = (repo / ".agents" / "quality-adapter.yaml").read_text(encoding="utf-8")
    assert "mutation_testing (charness propose)" in adapter_text
    assert "mutation_testing:" in adapter_text
    workflow_path = repo / ".github" / "workflows" / "mutation-tests.yml"
    assert workflow_path.is_file()
    workflow_text = workflow_path.read_text(encoding="utf-8")
    # F1: cron placeholder must be substituted at install time so the workflow
    # has a valid schedule.cron value GitHub Actions can parse.
    assert "MUTATION_SCHEDULE_CRON_PLACEHOLDER" not in workflow_text
    assert 'cron: "17 */3 * * *"' in workflow_text


def test_a3_execute_idempotent(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _write_adapter(repo, _ADAPTER_HEADER)
    _run_propose(repo, execute=True)
    workflow_path = repo / ".github" / "workflows" / "mutation-tests.yml"
    workflow_mtime = workflow_path.stat().st_mtime
    out2 = _run_propose(repo, execute=True)
    assert out2["status"] == "installed"
    assert any("already present" in applied for applied in out2["applied"])
    assert workflow_path.stat().st_mtime == workflow_mtime


def test_a3_execute_refuses_without_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    # No adapter file exists. --execute would produce a broken header-less file.
    result = subprocess.run(
        ["python3", str(PROPOSE_SCRIPT), "--repo-root", str(repo), "--execute"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "init_adapter" in result.stderr or "init_adapter" in result.stdout


# ---------------------------------------------------------------------------
# a4 template smoke + negative grep


def test_a4_template_exists() -> None:
    assert TEMPLATE_PATH.is_file()


def test_a4_template_has_required_steps() -> None:
    body = TEMPLATE_PATH.read_text(encoding="utf-8")
    for required_step in (
        "name: Resolve mutation_testing adapter slots",
        "name: Plan run",
        "name: Run mutation",
        "name: Summarize mutation report",
        "name: Open or update mutation issue",
        "name: Close recovered mutation issue",
        "name: Fail workflow on mutation failure",
    ):
        assert required_step in body, f"missing step: {required_step}"


def test_a4_template_does_not_summarize_dry_run_without_dump() -> None:
    body = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert (
        "steps.plan.outputs.mode == 'full' && steps.adapter.outputs.cmd_summary != ''"
        in body
    )


def test_a4_template_rotates_scheduled_sample_seed() -> None:
    body = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "MUTATION_SAMPLE_SEED: ${{ github.run_id }}:" in body


def test_a4_template_samples_only_full_runs_with_sample_command() -> None:
    body = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert (
        "steps.plan.outputs.mode == 'full' && steps.adapter.outputs.cmd_sample != ''"
        in body
    )


def test_checked_in_mutation_workflow_rotates_scheduled_sample_seed() -> None:
    body = (ROOT / ".github" / "workflows" / "mutation-tests.yml").read_text(encoding="utf-8")
    assert "MUTATION_SAMPLE_SEED: ${{ github.run_id }}:" in body


def test_checked_in_mutation_workflow_samples_only_full_runs_with_sample_command() -> None:
    body = (ROOT / ".github" / "workflows" / "mutation-tests.yml").read_text(encoding="utf-8")
    assert (
        "steps.plan.outputs.mode == 'full' && steps.adapter.outputs.cmd_sample != ''"
        in body
    )


def test_a4_template_has_no_stack_literal_run_lines() -> None:
    """SC 7: no hardcoded stack tool literal in run: lines."""
    body = TEMPLATE_PATH.read_text(encoding="utf-8")
    forbidden_literals = ("npm ", "yarn ", "pnpm ", "stryker", "mutmut", "cosmic-ray", "pitest")
    for lineno, line in enumerate(body.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("run:") and "run: " not in stripped:
            continue
        for literal in forbidden_literals:
            assert literal not in line.lower(), (
                f"line {lineno} contains stack literal `{literal}`: {line!r}"
            )


# ---------------------------------------------------------------------------
# a5 yq parse simulation (skipped when yq unavailable)


def _yq_available() -> bool:
    return shutil.which("yq") is not None


@pytest.mark.skipif(not _yq_available(), reason="yq not installed locally; CI Ubuntu image provides it")
def test_a5_yq_parses_all_four_slots(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    adapter = _write_adapter(repo, _ADAPTER_HEADER + _FULL_BLOCK)
    expected = {
        "dry_run": "npm run test:mutation:dry-run",
        "full": "npm run test:mutation",
        "sample": "npm run test:mutation:sample",
        "summary": "npm run test:mutation:ci-summary",
    }
    for slot, want in expected.items():
        result = subprocess.run(
            ["yq", "-r", f".mutation_testing.commands.{slot}", str(adapter)],
            check=True,
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == want, f"yq parse mismatch for {slot}"


# ---------------------------------------------------------------------------
# a7 plugin export exists


def test_a7_propose_script_mirrors_to_plugin_export() -> None:
    plugin_script = ROOT / "plugins" / "charness" / "skills" / "quality" / "scripts" / "propose_mutation_testing.py"
    assert plugin_script.is_file(), f"plugin export missing: {plugin_script}"


def test_a7_workflow_template_mirrors_to_plugin_export() -> None:
    plugin_template = (
        ROOT
        / "plugins"
        / "charness"
        / "skills"
        / "quality"
        / "scripts"
        / "templates"
        / "mutation-tests.yml"
    )
    assert plugin_template.is_file(), f"plugin export missing: {plugin_template}"


# ---------------------------------------------------------------------------
# infer_quality_defaults sanity (no fixture, just inference)


def test_infer_defaults_includes_mutation_testing(tmp_path: Path) -> None:
    defaults = infer_quality_defaults(tmp_path)
    assert "mutation_testing" in defaults
    assert defaults["mutation_testing"]["commands"]["full"] == ""
    assert defaults["mutation_testing"]["score_break"] == 60


def test_validate_data_with_empty_dict_includes_mutation_testing(tmp_path: Path) -> None:
    validated, errors, warnings = validate_quality_adapter_data({}, tmp_path)
    assert errors == []
    assert "mutation_testing" in validated


def test_repo_quality_adapter_enables_mutation_sample_command() -> None:
    payload = load_quality_adapter(ROOT)
    assert payload["data"]["mutation_testing"]["commands"]["sample"] == (
        "python3 scripts/sample_mutation_files.py --repo-root ."
    )


def test_cosmic_ray_summary_reports_actionable_survivors(tmp_path: Path) -> None:
    source = tmp_path / "demo.py"
    source.write_text("def demo():\n    return 1\n", encoding="utf-8")
    dump = tmp_path / "dump.jsonl"
    dump.write_text(
        "\n".join(
            [
                json.dumps(
                    [
                        {
                            "job_id": "a",
                            "mutations": [
                                {
                                    "module_path": "demo.py",
                                    "operator_name": "core/NumberReplacer",
                                    "start_pos": [2, 11],
                                    "definition_name": "demo",
                                }
                            ],
                        },
                        {"worker_outcome": "normal", "test_outcome": "survived"},
                    ]
                ),
                json.dumps(
                    [
                        {
                            "job_id": "b",
                            "mutations": [
                                {
                                    "module_path": "demo.py",
                                    "operator_name": "core/AddNot",
                                    "start_pos": [2, 4],
                                    "definition_name": "demo",
                                }
                            ],
                        },
                        {"worker_outcome": "normal", "test_outcome": "killed"},
                    ]
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    details = summarize_survived_mutations(iter_dump_records(dump), tmp_path)

    assert details["definitions"] == [("demo", 1)]
    assert details["operators"] == [("core/NumberReplacer", 1)]
    assert details["locations"] == [
        ("demo.py", 2, "demo", "core/NumberReplacer", "return 1")
    ]


def test_check_mutation_score_writes_survivor_details(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "quality-adapter.yaml").write_text(
        _ADAPTER_HEADER
        + dedent(
            """\
            mutation_testing:
              score_break: 50
              report_paths:
                summary_md: reports/mutation/summary.md
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "demo.py").write_text("def demo():\n    return 1\n", encoding="utf-8")
    dump = tmp_path / "dump.jsonl"
    dump.write_text(
        json.dumps(
            [
                {
                    "job_id": "a",
                    "mutations": [
                        {
                            "module_path": "demo.py",
                            "operator_name": "core/NumberReplacer",
                            "start_pos": [2, 11],
                            "definition_name": "demo",
                        }
                    ],
                },
                {"worker_outcome": "normal", "test_outcome": "survived"},
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "scripts/check_mutation_score.py",
            "--repo-root",
            str(tmp_path),
            "--stats",
            str(dump),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    summary = (tmp_path / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "## Survived Mutants" in summary
    assert "- `demo`: 1" in summary
    assert "- `core/NumberReplacer`: 1" in summary
    assert "- `demo.py:2` `demo` `core/NumberReplacer` - return 1" in summary


def test_cosmic_ray_filter_identifies_function_annotation_unions() -> None:
    assert is_function_annotation_union(
        "def read_lock(repo_root: Path, tool_id: str) -> dict[str, Any] | None:",
        61,
    )
    assert is_function_annotation_union(
        "def upsert_lock(repo_root: Path, *, support: dict[str, Any] | None = None) -> Path:",
        65,
    )
    assert not is_function_annotation_union("value = left | right", 13)
    assert not is_function_annotation_union("def plain(repo_root: Path) -> Path:", 0)


def test_run_cosmic_ray_mutation_invokes_filter_after_init(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "cosmic-ray.toml").write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["demo.py"]
            test-command = "python3 -m pytest"
            """
        ),
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_cosmic = bin_dir / "cosmic-ray"
    fake_cosmic.write_text(
        dedent(
            """\
            #!/usr/bin/env python3
            import os
            import sys
            from pathlib import Path

            log = Path(os.environ["FAKE_COSMIC_LOG"])
            log.write_text(log.read_text() + " ".join(sys.argv[1:]) + "\\n" if log.exists() else " ".join(sys.argv[1:]) + "\\n")
            if sys.argv[1] == "init":
                Path(sys.argv[3]).touch()
            if sys.argv[1] == "dump":
                print("")
            """
        ),
        encoding="utf-8",
    )
    fake_cosmic.chmod(0o755)
    fake_filter = repo / "filter.py"
    fake_filter.write_text(
        "from pathlib import Path\n"
        "Path('filter-called').write_text('yes\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_COSMIC_LOG": str(tmp_path / "cosmic.log")}

    result = subprocess.run(
        [
            "python3",
            "scripts/run_cosmic_ray_mutation.py",
            "--repo-root",
            str(repo),
            "--mode",
            "dry-run",
            "--filter-script",
            str(fake_filter),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert (repo / "filter-called").read_text(encoding="utf-8") == "yes\n"
    assert result.stdout.index("+ cosmic-ray init") < result.stdout.index("+ python3")
