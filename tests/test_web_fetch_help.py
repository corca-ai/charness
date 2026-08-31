from __future__ import annotations

import re
from pathlib import Path

from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "support" / "web-fetch" / "scripts"


def _help(script: str) -> str:
    result = run_script(str(SCRIPTS / script), "--help", cwd=ROOT)
    assert result.returncode == 0, result.stderr
    return result.stdout


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_acquire_public_url_help_explains_fetch_controls() -> None:
    output = _help("acquire_public_url.py")
    _assert_help_pairs(
        output,
        {
            "--url": "Public URL to acquire.",
            "--repo-root": "Repository root for route and capability resolution.",
            "--intent": "collect-mode fallback stages, including network-recon when supported.",
            "--browser-mode": "always still tries browser fallbacks when they are needed.",
            "--timeout": "Per-command timeout in seconds.",
            "--direct-response-file": "Read a seeded direct response from this file.",
            "--expect-text": "Require literal text as positive proof",
            "--expect-regex": "Require a regex match as positive proof",
            "--expect-json-field": "Require a non-empty JSON field path as proof",
            "--include-selected-content": "when a selected attempt succeeds.",
            "--selected-content-max-chars": "Maximum characters in the selected content excerpt.",
        },
    )


def test_classify_fetch_response_help_explains_input_and_proof() -> None:
    output = _help("classify_fetch_response.py")
    _assert_help_pairs(
        output,
        {
            "--path": "otherwise read stdin.",
            "--expect-text": "Require literal text as positive proof",
            "--expect-regex": "Require a regex match as positive proof",
            "--expect-json-field": "Require a non-empty JSON field path as proof",
            "--intent": "Classification intent: one source or a collection.",
        },
    )


def test_route_public_fetch_help_explains_route_inputs() -> None:
    output = _help("route_public_fetch.py")
    _assert_help_pairs(
        output,
        {
            "--url": "Public URL whose acquisition route should be resolved.",
            "--repo-root": "Repository root for capability and GitHub mode resolution.",
        },
    )
