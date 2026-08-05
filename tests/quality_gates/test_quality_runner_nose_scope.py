from __future__ import annotations

import json
from pathlib import Path

from .support import clone_quality_runner_repo, run_shell_script, write_executable


def test_nose_inventory_unproven_scope_is_not_measured(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    write_executable(
        repo / "skills/public/quality/scripts/inventory_nose_clones.py",
        "#!/usr/bin/env python3\nprint('SCOPE: partial scan; missing requested roots')\nraise SystemExit(4)\n",
    )
    receipt_path = repo / "receipt.json"
    env["CHARNESS_QUALITY_LABELS"] = "inventory-nose-clones,check-markdown"
    env["CHARNESS_QUALITY_RECEIPT_JSON"] = str(receipt_path)

    result = run_shell_script(repo / "scripts/run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "UNPROVEN inventory-nose-clones" in result.stdout
    assert "PASS inventory-nose-clones" not in result.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "unestablished"
    assert receipt["unproven_subjects"] == ["inventory-nose-clones"]
    assert receipt["measured_scope"] == ["check-markdown"]


def test_missing_nose_inventory_helper_is_unproven_and_not_measured(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / "skills/public/quality/scripts/inventory_nose_clones.py").unlink()
    receipt_path = repo / "receipt.json"
    env["CHARNESS_QUALITY_LABELS"] = "inventory-nose-clones,check-markdown"
    env["CHARNESS_QUALITY_RECEIPT_JSON"] = str(receipt_path)

    result = run_shell_script(repo / "scripts/run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "UNPROVEN inventory-nose-clones" in result.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["unproven_subjects"] == ["inventory-nose-clones"]
    assert receipt["measured_scope"] == ["check-markdown"]
