from __future__ import annotations

import re
from pathlib import Path

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "public" / "retro" / "scripts"


def _help(script: str) -> str:
    module = load_script_module(f"retro_help_{Path(script).stem}", SCRIPTS / script)
    result = run_loaded_script_main(script, module, "--help")
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return result.stdout


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


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
        },
    )
    # Output is no longer a mode the operator picks: packet files are always
    # written and the receipt is always the structured payload. The help must not
    # advertise an output-mode flag that no longer exists -- offering one and
    # having argparse reject it is worse than saying nothing.
    assert "--json" not in output
