"""#367: CI-recoverability triage lens for costly local standing gates.

The counterweight to the local-proof guardrail: it flags costly local gates whose
proof CI fully re-runs (ranked by wall-clock) and must NEVER recommend moving a
gate CI does not re-run (those are keep-local).
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from .support import ROOT, run_script

SKILL_SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))
lens = importlib.import_module("ci_recoverable_gates_lib")

INVENTORY = "skills/public/quality/scripts/inventory_ci_recoverable_gates.py"


def _corpus(*runs: str) -> list[dict[str, object]]:
    return [
        {"workflow": ".github/workflows/quality-core.yml", "data": {"jobs": {"core": {"steps": [
            {"run": run} for run in runs
        ]}}}}
    ]


def _flatten(*runs: str) -> list[dict[str, object]]:
    return lens.ci_step_corpus(_corpus(*runs))


# --- matching + classification -------------------------------------------------


def test_gate_is_candidate_when_ci_reruns_its_script(tmp_path: Path) -> None:
    corpus = _flatten("python3 scripts/check_doc_links.py --repo-root .")
    result = lens.classify_gates([{"label": "check-doc-links", "wall_clock_ms": 5000}], corpus)
    assert [c["label"] for c in result["candidates"]] == ["check-doc-links"]
    assert result["keep_local"] == []


def test_gate_is_keep_local_when_ci_does_not_rerun(tmp_path: Path) -> None:
    corpus = _flatten("python3 scripts/check_doc_links.py")
    result = lens.classify_gates([{"label": "specdown", "wall_clock_ms": 30000}], corpus)
    assert result["candidates"] == []
    assert [g["label"] for g in result["keep_local"]] == ["specdown"]


def test_mixed_gates_split_correctly() -> None:
    corpus = _flatten(
        "ruff check charness scripts tests",
        "python3 scripts/check_doc_links.py",
        "./scripts/check-markdown.sh",
    )
    gates = [
        {"label": "specdown", "wall_clock_ms": 30000},  # not in CI -> keep local
        {"label": "check-doc-links", "wall_clock_ms": 5000},  # in CI -> candidate
        {"label": "check-markdown", "wall_clock_ms": 9000},  # in CI -> candidate
        {"label": "pytest", "wall_clock_ms": 60000},  # not in CI -> keep local
    ]
    result = lens.classify_gates(gates, corpus)
    assert [c["label"] for c in result["candidates"]] == ["check-markdown", "check-doc-links"]
    assert {g["label"] for g in result["keep_local"]} == {"pytest", "specdown"}


def test_candidates_ranked_by_wall_clock_desc_unknown_last() -> None:
    corpus = _flatten("python3 scripts/check_doc_links.py", "python3 scripts/check_markdown.py", "ruff check .")
    gates = [
        {"label": "check-doc-links", "wall_clock_ms": 1000},
        {"label": "check-markdown", "wall_clock_ms": 9000},
        {"label": "ruff-check", "wall_clock_ms": None},
    ]
    result = lens.classify_gates(gates, corpus)
    assert [c["label"] for c in result["candidates"]] == ["check-markdown", "check-doc-links", "ruff-check"]


def test_pytest_tool_label_matches_word_boundary() -> None:
    corpus = _flatten("uv run python -m pytest -q")
    result = lens.classify_gates([{"label": "pytest", "wall_clock_ms": 1000}], corpus)
    assert [c["label"] for c in result["candidates"]] == ["pytest"]


def test_generic_single_word_label_does_not_overmatch() -> None:
    # "node" is too generic; it must not be flagged a candidate just because CI
    # mentions node-version anywhere, since that is not its proof being re-run.
    corpus = _flatten("actions/setup-node sets node-version 22")
    result = lens.classify_gates([{"label": "node", "wall_clock_ms": 1000}], corpus)
    assert result["candidates"] == []
    assert [g["label"] for g in result["keep_local"]] == ["node"]


def test_gate_policy_surfaced_on_candidate() -> None:
    corpus = lens.ci_step_corpus(
        [
            {
                "workflow": ".github/workflows/quality-core.yml",
                "gate_policy": "local-gate-subset-mirror",
                "data": {"jobs": {"core": {"steps": [{"run": "python3 scripts/check_doc_links.py"}]}}},
            }
        ]
    )
    result = lens.classify_gates([{"label": "check-doc-links", "wall_clock_ms": 5000}], corpus)
    assert result["candidates"][0]["ci_gate_policies"] == ["local-gate-subset-mirror"]


def test_uses_only_setup_steps_contribute_no_proof() -> None:
    corpus = lens.ci_step_corpus(
        [{"workflow": "w.yml", "data": {"jobs": {"core": {"steps": [{"uses": "actions/checkout@v6"}]}}}}]
    )
    assert corpus == []


def test_gates_from_runtime_report_merges_hotspots_and_checked() -> None:
    report = {
        "runtime_hotspots": [{"label": "pytest", "median_recent_elapsed_ms": 60000}],
        "checked": [
            {"label": "pytest", "median_recent_elapsed_ms": 60000},  # dedup
            {"label": "specdown", "median_recent_elapsed_ms": None},  # budgeted, no sample
        ],
    }
    gates = {g["label"]: g["wall_clock_ms"] for g in lens.gates_from_runtime_report(report)}
    assert gates == {"pytest": 60000, "specdown": None}


# --- integration through the CLI ----------------------------------------------


def _seed_repo(tmp_path: Path, *, adapter_lines: list[str], workflow: str, log_rows: list[dict] | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".charness" / "quality").mkdir(parents=True)
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")
    (repo / ".github" / "workflows" / "quality-core.yml").write_text(workflow, encoding="utf-8")
    if log_rows is not None:
        (repo / ".charness" / "quality" / "command-timing.jsonl").write_text(
            "\n".join(json.dumps(r) for r in log_rows) + "\n", encoding="utf-8"
        )
    return repo


_WORKFLOW = """name: Quality Core
on:
  push:
    branches: [main]
jobs:
  core:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Validate doc links
        run: python3 scripts/check_doc_links.py --repo-root .
      - name: Lint
        run: ruff check charness scripts tests
"""

_ADAPTER_WITH_LOG = [
    "version: 1",
    "repo: testrepo",
    "output_dir: charness-artifacts/quality",
    "command_timing_log:",
    "  path: .charness/quality/command-timing.jsonl",
    "  format: jsonl",
    "  field_map:",
    "    label: command",
    "    elapsed: elapsed_ms",
]


def test_cli_ranks_recoverable_and_keeps_local(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        adapter_lines=_ADAPTER_WITH_LOG,
        workflow=_WORKFLOW,
        log_rows=[
            {"command": "check-doc-links", "elapsed_ms": 5000},
            {"command": "specdown", "elapsed_ms": 30000},
            {"command": "ruff-check", "elapsed_ms": 800},
        ],
    )
    result = run_script(INVENTORY, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["commands_source"] == "command_timing_log"
    candidate_labels = {c["label"] for c in payload["candidates"]}
    keep_local_labels = {g["label"] for g in payload["keep_local"]}
    # check-doc-links + ruff-check are re-run by CI; specdown is not.
    assert "check-doc-links" in candidate_labels
    assert "ruff-check" in candidate_labels
    assert "specdown" in keep_local_labels
    assert "specdown" not in candidate_labels  # safety: never recommend moving non-recoverable proof


def test_cli_reports_no_cost_signal_when_unranked(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        adapter_lines=["version: 1", "repo: testrepo", "output_dir: charness-artifacts/quality"],
        workflow=_WORKFLOW,
    )
    result = run_script(INVENTORY, "--repo-root", str(repo), "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    assert "no cost-ranked standing gates" in result.stdout
