"""Consumer-owned runtime-label discovery for #546."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT, run_script, seed_runtime_budget_repo
from .seeding_support import load_module

SCRIPT = "skills/public/quality/scripts/check_runtime_budget.py"
UNIVERSE_LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "runtime_budget_universe_lib.py"
QUALITY_SCRIPTS_DIR = str(UNIVERSE_LIB.parent)
if QUALITY_SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, QUALITY_SCRIPTS_DIR)
runtime_budget_universe = load_module("runtime_budget_universe_under_test", UNIVERSE_LIB)
from skills.public.quality.scripts.runtime_visibility_lib import (  # noqa: E402
    UNENFORCEABLE_BUDGET_ADVISORY_REASON,
)


def _add_universe_command(repo: Path, body: str) -> None:
    emitter = repo / "list-labels.sh"
    emitter.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8")
    emitter.chmod(0o755)
    adapter = repo / ".agents" / "quality-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8")
        + "runtime_budget_universe:\n"
        + "  command: ./list-labels.sh\n",
        encoding="utf-8",
    )


def _detail(repo: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    return result, yaml.safe_load(result.stdout)


def test_absent_consumer_universe_stays_non_blocking(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"pytest": 22000},
        signals={"commands": {"pytest": {"latest": {"elapsed_ms": 1000}}}},
    )

    result, payload = _detail(repo)

    assert result.returncode == 0, result.stderr
    assert payload["runtime_budget_universe"]["status"] == "not-declared"
    assert payload["runtime_budget_universe"]["configured"] is False
    assert payload["profile_config_errors"] == []


def test_consumer_universe_reconciles_every_budget_block(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"alpha-gate": 1000},
        budget_profiles={"ci": {"budgets": {"beta-gate": 1000}}},
        signals={"commands": {"alpha-gate": {"latest": {"elapsed_ms": 10}}}},
    )
    _add_universe_command(repo, "printf '%s\\n' beta-gate alpha-gate spare-gate\n")

    result, payload = _detail(repo)

    assert result.returncode == 0, result.stderr
    universe = payload["runtime_budget_universe"]
    assert universe["status"] == "resolved"
    assert universe["labels"] == ["alpha-gate", "beta-gate", "spare-gate"]
    assert universe["missing_labels"] == []
    assert universe["unbudgeted_labels"] == ["spare-gate"]


def test_missing_budgeted_consumer_label_is_not_a_green_claim(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"alpha-gate": 1000},
        budget_profiles={"ci": {"budgets": {"beta-gate": 1000}}},
        signals={"commands": {"alpha-gate": {"latest": {"elapsed_ms": 10}}}},
    )
    _add_universe_command(repo, "printf '%s\\n' alpha-gate\n")

    result, payload = _detail(repo)

    assert result.returncode == 1
    universe = payload["runtime_budget_universe"]
    assert universe["status"] == "mismatch"
    assert universe["missing_labels"] == ["beta-gate"]
    assert any("missing budgeted label(s): beta-gate" in error for error in payload["profile_config_errors"])

    summary = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--summary",
        "--runtime-profile",
        "default",
    )
    assert summary.returncode == 1
    assert yaml.safe_load(summary.stdout)["status"] == "configuration-error"


@pytest.mark.parametrize(
    ("body", "needle"),
    [
        ("exit 7\n", "exited 7"),
        ("printf 'alpha-gate\\nalpha-gate\\n'\n", "duplicate label `alpha-gate`"),
        ("", "emitted no labels"),
    ],
)
def test_declared_consumer_universe_refuses_unestablished_output(
    tmp_path: Path, body: str, needle: str
) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets={"alpha-gate": 1000}, signals=None)
    _add_universe_command(repo, body)

    result, payload = _detail(repo)

    assert result.returncode == 1
    assert payload["runtime_budget_universe"]["status"] == "unestablished"
    assert any(needle in error for error in payload["runtime_budget_universe"]["errors"])


def test_universe_reader_handles_invalid_config_and_runner_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    labels, errors = runtime_budget_universe._parse_labels("\nalpha-gate\n")
    assert labels == ["alpha-gate"]
    assert errors == []

    invalid_mapping = runtime_budget_universe.read(
        Path.cwd(),
        {"runtime_budget_universe": "broken"},
        {"alpha-gate": ["runtime_budgets"]},
    )
    assert invalid_mapping["status"] == "unestablished"
    assert invalid_mapping["errors"] == ["runtime_budget_universe must be a mapping"]

    invalid = runtime_budget_universe.read(
        Path.cwd(),
        {"runtime_budget_universe": {"command": 7}},
        {"alpha-gate": ["runtime_budgets"]},
    )
    assert invalid["status"] == "unestablished"
    assert "must be a non-empty string" in invalid["errors"][0]

    def raise_os_error(*_args, **_kwargs):
        raise OSError("runner unavailable")

    monkeypatch.setattr(runtime_budget_universe.subprocess, "run", raise_os_error)
    failed = runtime_budget_universe.read(
        Path.cwd(),
        {"runtime_budget_universe": {"command": "./list-labels.sh"}},
        {"alpha-gate": ["runtime_budgets"]},
    )
    assert failed["status"] == "unestablished"
    assert "runner unavailable" in failed["errors"][0]
    assert "runtime_budget_universe" in UNENFORCEABLE_BUDGET_ADVISORY_REASON
