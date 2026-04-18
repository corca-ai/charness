from __future__ import annotations

import json
from pathlib import Path

from .test_quality_artifact import run_script

ROOT = Path(__file__).resolve().parents[1]


def test_eval_cautilus_chatbot_compare_writes_summary(tmp_path: Path) -> None:
    output_dir = tmp_path / "chatbot-benchmark"
    result = run_script(
        "scripts/eval_cautilus_chatbot_compare.py",
        "--repo-root",
        str(ROOT),
        "--baseline-repo",
        str(ROOT),
        "--candidate-repo",
        str(ROOT),
        "--output-dir",
        str(output_dir),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["baseline"]["candidate_count"] == payload["candidate"]["candidate_count"]
    assert payload["baseline"]["proposal_keys"] == payload["candidate"]["proposal_keys"]
    assert payload["diff"]["added_candidate_keys"] == []
    assert payload["diff"]["removed_candidate_keys"] == []
    assert payload["diff"]["added_proposal_keys"] == []
    assert payload["diff"]["removed_proposal_keys"] == []
    assert (output_dir / "latest.json").is_file()
    assert (output_dir / "latest.md").is_file()
