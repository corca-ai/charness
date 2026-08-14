from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.script_main import load_script_module

from .test_quality_artifact import cautilus_supports, run_script

ROOT = Path(__file__).resolve().parents[1]
requires_cautilus = pytest.mark.skipif(
    not (
        cautilus_supports("discover", "scenarios", "propose")
        and cautilus_supports("evaluate", "comparison", "prepare")
    ),
    reason="cautilus with the `discover scenarios propose` and `evaluate comparison prepare` surfaces is required for live chatbot comparison eval tests",
)

_CHATBOT_COMPARE = load_script_module(
    "eval_cautilus_chatbot_compare_for_test",
    Path(__file__).resolve().parents[1] / "scripts" / "eval_cautilus_chatbot_compare.py",
)


def test_chatbot_compare_prepare_requests_json_output(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({
                "baseline": {"path": str(tmp_path / "baseline")},
                "candidate": {"path": str(tmp_path / "candidate")},
            }),
            stderr="",
        )

    monkeypatch.setattr(_CHATBOT_COMPARE.subprocess, "run", fake_run)
    baseline, candidate = _CHATBOT_COMPARE.resolve_repo_pair(
        repo_root=tmp_path,
        baseline_repo=None,
        candidate_repo=None,
        baseline_ref="HEAD",
    )

    assert baseline == (tmp_path / "baseline").resolve()
    assert candidate == (tmp_path / "candidate").resolve()
    # `cautilus` is the THIRD-PARTY binary: its `--json` is its own native API and
    # is untouched by the repo-owned YAML migration.
    assert captured["argv"][0] == "cautilus"
    assert captured["argv"][-1] == "--json"


@requires_cautilus
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
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["baseline"]["candidate_count"] == payload["candidate"]["candidate_count"]
    assert payload["baseline"]["proposal_keys"] == payload["candidate"]["proposal_keys"]
    assert payload["baseline"]["attention_view"]["proposal_keys"] == payload["candidate"]["attention_view"]["proposal_keys"]
    assert payload["diff"]["added_candidate_keys"] == []
    assert payload["diff"]["removed_candidate_keys"] == []
    assert payload["diff"]["added_proposal_keys"] == []
    assert payload["diff"]["removed_proposal_keys"] == []
    assert payload["diff"]["added_attention_proposal_keys"] == []
    assert payload["diff"]["removed_attention_proposal_keys"] == []
    assert (output_dir / "latest.json").is_file()
    assert (output_dir / "latest.md").is_file()
    # The retired "Wrote ... to <dir>" line was the only place a reader learned
    # where the benchmark landed; the artifact's own schema does not carry it, so
    # the emitted payload has to.
    assert payload["output_dir"]
