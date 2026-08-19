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
import sys
from pathlib import Path

import pytest

from .support import ROOT

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
    return subprocess.run(
        [sys.executable, str(ROOT / SCANNER), "--repo-root", str(repo), *args],
        capture_output=True,
        text=True,
    )


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
        # quality is one of six resolvers that let a parser refusal's ValueError out (#673).
        assert "Traceback" in result.stderr, result.stderr
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
