from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "public" / "retro" / "scripts"


def _help(script: str) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script), "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_mine_closeout_telemetry_help_explains_stream_inputs() -> None:
    output = _help("mine_closeout_telemetry.py")
    _assert_help_pairs(
        output,
        {
            "--repo-root": "resolve the closeout-telemetry stream path.",
            "--stream-path": "JSONL path relative to --repo-root.",
            "--recur-min": "marks a waste item as recurring.",
        },
    )


def test_plan_retro_run_help_explains_repo_root_resolution() -> None:
    output = _help("plan_retro_run.py")
    _assert_help_pairs(
        output,
        {
            "--repo-root": "resolve adapter state, artifacts, and changed paths.",
        },
    )


def test_prepare_packet_help_explains_packet_scope_and_output() -> None:
    output = _help("prepare_packet.py")
    _assert_help_pairs(
        output,
        {
            "--repo-root": "resolve the retro adapter and packet output path.",
            "--prepared-for": "when no explicit changed ref is supplied.",
            "--changed-ref": "Single Git ref whose changed files should define the packet scope.",
            "--commit": "Single commit whose changed files should define the packet scope.",
            "--range": "revision range whose changed files should define the packet scope.",
            "--slug": "defaults to the current UTC timestamp.",
            "--json": "instead of writing packet files.",
        },
    )
