"""The inline-prompt bulk scanner refuses an unhonored declaration instead of scanning
nothing and reporting clean.

Row 26 of slice 5. `--from-adapter` exists so the scan uses the repo's own declared
`prompt_asset_policy`; an unhonored declaration empties it, and an empty glob list scans no
files, so the scanner reports `findings: []` — the emptiest possible answer presented as a
result.

Measured at `abbcd9bff`: a repo declaring `source_globs: ["src/**/*.py"]` and
`min_multiline_chars: 40` under `version: 9` scanned `source_globs: []` at
`min_multiline_chars: 400` (both charness defaults) and reported `findings: []`. The same
repo at a speakable version reports findings.

The guard sits only on the `--from-adapter` path. The explicit `--source-glob` /
`--min-multiline-chars` flags exist precisely so a caller can scan without asking the
adapter anything, and a control asserts that arm still works under a refused version.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .support import run_script

SCANNER = "skills/public/quality/references/find_inline_prompt_bulk.py"

DECLARED = """version: {v}
repo: demo
prompt_asset_policy:
  source_globs:
    - "src/**/*.py"
  min_multiline_chars: 40
  exemption_globs: []
"""


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    # A multiline string long enough to trip the DECLARED 40-char bar but not the
    # charness default of 400 — so "scanned with the repo's policy" and "scanned with
    # ours" differ in the FINDINGS, not only in the echoed configuration.
    body = "x" * 60
    (repo / "src" / "a.py").write_text(f'PROMPT = """\n{body}\n"""\n', encoding="utf-8")
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "quality-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return run_script(SCANNER, "--repo-root", str(repo), *args)


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_an_unhonored_policy_refuses_rather_than_scanning_nothing(
    tmp_path: Path, version: str
) -> None:
    result = _run(_repo(tmp_path, DECLARED.format(v=version)), "--from-adapter")
    assert result.returncode != 0, result.stdout
    if version == "9":
        assert "quality-adapter.yaml" in result.stderr, result.stderr
        assert "does not speak" in result.stderr, result.stderr
    else:
        # CONVERGED. `#673` routed the five bare-loader libraries through
        # `adapter_lib.read_declared_adapter`, so every resolver now RECORDS a parse
        # refusal in `errors` instead of raising, and this door renders the same
        # verdict shape everywhere. The traceback branch this replaces was honest
        # about a real gap; keeping it would now pin the gap shut.
        assert "Traceback" not in result.stderr, result.stderr
        assert "quality-adapter.yaml" in result.stderr, result.stderr
        assert "could not be parsed" in result.stderr, result.stderr
    assert "findings: []" not in result.stdout


def test_a_speakable_version_scans_the_declared_policy(tmp_path: Path) -> None:
    """The polarity control, asserting the FINDINGS and not just the echoed globs.

    The declared `min_multiline_chars: 40` catches a 60-character block that the charness
    default of 400 does not, so this arm cannot pass on a scanner that merely echoes its
    configuration back.
    """
    result = _run(_repo(tmp_path, DECLARED.format(v="1")), "--from-adapter")
    assert result.returncode == 0, result.stderr
    assert "src/**/*.py" in result.stdout
    assert "min_multiline_chars: 40" in result.stdout
    assert "findings: []" not in result.stdout


def test_explicit_flags_do_not_ask_the_adapter_anything(tmp_path: Path) -> None:
    """The escape the guard is placed to preserve. `--source-glob` is why this script has
    flags at all; refusing there would break a scan that never consulted a declaration."""
    result = _run(_repo(tmp_path, DECLARED.format(v="9")), "--source-glob", "src/**/*.py")
    assert result.returncode == 0, result.stderr
    assert "src/**/*.py" in result.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    """Opt-in surface. `--from-adapter` against a repo with no adapter yields the empty
    default policy, which is the honest answer for a repo that declared none."""
    result = _run(_repo(tmp_path, None), "--from-adapter")
    assert result.returncode == 0, result.stderr


def test_an_ordinary_invalid_field_is_not_refused(tmp_path: Path) -> None:
    """`valid: false` from an unrelated bad field must NOT refuse, and the declared policy
    must still be honored — both halves asserted."""
    adapter = DECLARED.format(v="1").replace("repo: demo", "repo: demo\npreset_version: 3")
    result = _run(_repo(tmp_path, adapter), "--from-adapter")
    assert result.returncode == 0, result.stderr
    assert "min_multiline_chars: 40" in result.stdout


def test_an_invalid_prompt_policy_refuses_rather_than_scanning_the_default(
    tmp_path: Path,
) -> None:
    """The cheapest input to this row's own headline observable, found by a round-2
    bounded review — and it needs no `version` change at all.

    `source_globs: src/**/*.py` written as a STRING appends
    `prompt_asset_policy.source_globs must be a list of strings`, and
    `merge_prompt_asset_policy` still returns a merged dict carrying the charness default
    `[]`. So the scan covered nothing and reported `findings: []` at `valid: false` that
    nobody reads — verbatim the harm this row exists to close.

    The refusal is CONSUMER-LOCAL and does not widen `adapter_version_verdict`, which
    rightly forbids refusing on ordinary invalidity in general. It rests on this command's
    own contract: `--from-adapter` means "use the policy the repo declared", so a policy
    that failed validation means the declared policy is not in use.
    """
    adapter = "version: 1\nrepo: demo\nprompt_asset_policy:\n  source_globs: src/**/*.py\n  min_multiline_chars: 40\n"
    result = _run(_repo(tmp_path, adapter), "--from-adapter")
    assert result.returncode == 1, result.stdout
    assert "did not honor" in result.stderr, result.stderr
    assert "findings: []" not in result.stdout
