"""Five quality-skill readers refuse an unhonored adapter declaration instead of
reporting the OPPOSITE of what the repo declared.

Rows 14-18 of slice 5. Three of these five do not merely degrade — they emit
advisory-shaped findings asserting the repo configured nothing, on the surface that
decides whether a gate's cost is visible at all.

Measured on the real CLIs at `00c50ed3f`, one repo declaring `output_dir: docs/mine-q`, a
`startup_probes` entry and a `runtime_budgets` label:

    measure_startup_probes  "No startup probes matched the selected class."
    resolve_quality_artifact artifact_path: charness-artifacts/quality/latest.md
    check_runtime_budget    "quality adapter has no effective runtime budget …"
                            "quality adapter has no startup_probes"
    render_runtime_summary  "runtime visibility: weak due to
                             `runtime_visibility_missing_budgets`,
                             `runtime_visibility_missing_startup_probes`"
    inventory_ci_recoverable_gates
                            "0 cost-ranked gate(s)" + "configure `runtime_budgets`"

All at exit 0.

THE FIRST CUT OF THESE STIMULI HAD A CONTROL THAT COULD NOT FAIL, and it is worth keeping
visible because it is the second time in this slice. The fixture declared
`startup_probes: [{id, command: <string>}]` and a bare `runtime_budgets` label — shapes
this contract does not honor — so the speakable-version control produced the SAME output
as the refused one, and the "flip" was unproven for two of the five. Re-measured on the
shapes `adapter_validators.startup_probes` and `runtime_profile_lib` actually read.

`runtime_budget_lib` and `runtime_budget_sizing_lib` take their loader INJECTED and so
cannot know which adapter they are reading or refuse for it. That seam is deliberate, so
the guard lives in each caller and those two stay classified unguarded rather than credited
with a property their callers supply.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

# Literal, so `suggest_mutation_coverage_command` can map these tests to their sources.
READERS = (
    "skills/public/quality/scripts/measure_startup_probes.py",
    "skills/public/quality/scripts/resolve_quality_artifact.py",
    "skills/public/quality/scripts/check_runtime_budget.py",
    "skills/public/quality/scripts/render_runtime_summary.py",
    "skills/public/quality/scripts/inventory_ci_recoverable_gates.py",
)

# The shapes this contract actually honors. A fixture that declares anything else makes
# the polarity control below unable to fail, which is how two of these rows were first
# measured wrong.
DECLARED = """version: {v}
repo: demo
output_dir: docs/mine-q
startup_probes:
  - label: probe-one
    command:
      - python3
      - "-c"
      - "pass"
    class: standing
    startup_mode: warm
    surface: direct
runtime_budgets:
  pytest: 70000
"""


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "quality-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(rel: str, repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / rel), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("rel", READERS, ids=[Path(r).stem for r in READERS])
@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_an_unhonored_declaration_refuses(tmp_path: Path, rel: str, version: str) -> None:
    result = _run(rel, _repo(tmp_path, DECLARED.format(v=version)))
    assert result.returncode != 0, result.stdout
    if version == "9":
        assert "quality-adapter.yaml" in result.stderr, result.stderr
        assert "does not speak" in result.stderr, result.stderr
    else:
        # The quality resolver lets a parser refusal's `ValueError` out rather than
        # recording it in `errors` — `quality_adapter_lib` calls `load_yaml_file` with no
        # handler, unlike `simple_skill_adapter_lib`. So this door refuses with a raw
        # TRACEBACK for the whole quality family. It stops and reports nothing inverted,
        # which is this row's claim; the stack trace is the same named residual the
        # scaffold rows record, not a new one, and fixing that resolver is a different
        # change than these rows make.
        assert "Traceback" in result.stderr, result.stderr
        assert "unsupported YAML construct" in result.stderr, result.stderr
    # The inverted finding must not be reported alongside the refusal.
    assert "has no startup_probes" not in result.stdout
    assert "charness-artifacts/quality" not in result.stdout


@pytest.mark.parametrize(
    ("rel", "expected"),
    [
        (READERS[0], "probe-one"),
        (READERS[1], "docs/mine-q/latest.md"),
        (READERS[2], "budget 70000ms"),
        (READERS[3], "runtime visibility: configured."),
        (READERS[4], "1 cost-ranked gate(s)"),
    ],
    ids=[Path(r).stem for r in READERS],
)
def test_a_speakable_version_reports_what_the_repo_declared(
    tmp_path: Path, rel: str, expected: str
) -> None:
    """The polarity control, and the one that failed to fail on the first cut.

    Each expectation is a value that appears ONLY when the declaration was honored:
    the probe's own label, the declared output directory, the declared budget in
    milliseconds, `configured` rather than `weak`, and a non-zero cost-ranked count.
    """
    result = _run(rel, _repo(tmp_path, DECLARED.format(v="1")))
    assert result.returncode == 0, result.stderr
    assert expected in result.stdout, result.stdout


@pytest.mark.parametrize("rel", READERS, ids=[Path(r).stem for r in READERS])
def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path, rel: str) -> None:
    """Opt-in surfaces. A repo that declared nothing is not a repo whose declaration could
    not be read, and the `missing_budgets` / `missing_startup_probes` advisories are the
    correct answer for it — they are only wrong over a repo that declared."""
    result = _run(rel, _repo(tmp_path, None))
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("rel", READERS, ids=[Path(r).stem for r in READERS])
def test_an_ordinary_invalid_field_is_not_refused(tmp_path: Path, rel: str) -> None:
    """The polarity a bounded review noted this module did not pin.

    `valid: false` from one bad field beside honored ones must NOT refuse — that is the
    distinction `adapter_version_verdict`'s docstring exists to make, and widening the
    predicate to `not valid` would break every consumer with a typo'd unrelated key. The
    release-family tests pinned it; this family did not.
    """
    adapter = DECLARED.format(v="1").replace(
        "output_dir: docs/mine-q", "output_dir: docs/mine-q\npreset_version: 3"
    )
    result = _run(rel, _repo(tmp_path, adapter))
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("rel", READERS, ids=[Path(r).stem for r in READERS])
def test_a_silently_dropped_declaration_is_the_documented_blind_arm(
    tmp_path: Path, rel: str
) -> None:
    """The THIRD state, pinned as a known gap rather than left to make the claim read
    wider than it is.

    `quality_adapter_lib` calls `adapter_lib.load_yaml_file`, which discards the
    uninterpreted-line sink `load_yaml_file_report` returns. So an over-indented line is
    dropped with `errors: []` and `valid: True`, and no predicate over `errors` — which is
    what `declarations_unhonored` is — can see it. Measured: one stray indent restores the
    charness default at exit 0, with the guard in place.

    This test asserts the CURRENT behavior so the gap is visible and so closing it
    (#673) is a deliberate test change rather than a silent one. It is NOT an assertion
    that the current behavior is correct.
    """
    repo = _repo(tmp_path, "version: 1\nrepo: demo\n  output_dir: docs/mine-q\n")
    result = _run(rel, repo)
    assert result.returncode == 0, result.stderr
    assert "docs/mine-q" not in result.stdout
