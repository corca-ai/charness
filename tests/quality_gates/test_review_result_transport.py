"""Focused contract for the review lifecycle payload transport."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.quality_gates.test_semantic_review_command import (
    _fake_codex,
    _install_cached_working_tree_packet,
    _payload,
    _repo,
    _run,
)

pytestmark = pytest.mark.boundary_contract(
    reason="observe actual semantic review wrapper stdout and lifecycle file transport"
)


def _assert_transport(repo: Path, payload: dict, stdout: str) -> None:
    lifecycle_path = repo / payload["paths"]["summary"]
    assert lifecycle_path.read_text(encoding="utf-8") == stdout

    plan = json.loads((repo / payload["paths"]["plan"]).read_text(encoding="utf-8"))
    full_input = plan["semantic_input"]
    expected = dict(full_input)
    expected["entries"] = [
        {key: value for key, value in entry.items() if key != "prompt_content"}
        for entry in full_input["entries"]
    ]
    assert payload["semantic_input"] == expected
    assert all("prompt_content" not in entry for entry in payload["semantic_input"]["entries"])
    assert all("prompt_content" in entry for entry in full_input["entries"])
    prompt = (repo / payload["paths"]["prompt"]).read_text(encoding="utf-8")
    assert '"prompt_content": "base\\n"' in prompt


@pytest.mark.parametrize("verdict, dry_run", [("pass", True), ("pass", False), ("block", False)])
def test_dry_and_live_lifecycle_results_share_metadata_only_transport(
    tmp_path: Path, verdict: str, dry_run: bool
) -> None:
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")
    packet_file = _install_cached_working_tree_packet(tmp_path)

    result = _run(
        tmp_path,
        bin_dir,
        f"transport-{verdict}-{dry_run}",
        verdict=verdict,
        dry_run=dry_run,
        packet_file=packet_file,
    )
    payload = _payload(result)

    assert result.returncode == (0 if dry_run or verdict == "pass" else 1), result.stderr
    if verdict == "block":
        assert payload["approval_eligible"] is False
        assert payload["verdict_state"] == "block"
    _assert_transport(tmp_path, payload, result.stdout)
