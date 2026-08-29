from __future__ import annotations

import contextlib
import importlib
import io
import sys
from pathlib import Path
from typing import NamedTuple

import yaml

from .support import ROOT

# Advisory-interpretation contract rollout (#322): the length warn band / headroom
# near-limit signal is inference-layer (a length *smell*), so it self-declares the
# 4 fields. The hard over-limit file gate is a verified deterministic fact and
# must NEVER carry the declaration — these tests guard that cardinal-error
# boundary in both directions. Driven in-process via main() (not a
# subprocess) to stay on the testability-dsl-initiative in-process convention.
PYTHON_LENGTHS = importlib.import_module("scripts.check_code_lengths")


class _Result(NamedTuple):
    returncode: int
    stdout: str


def _run(*args: str) -> _Result:
    out = io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["check_code_lengths.py", *args]
    try:
        with contextlib.redirect_stdout(out):
            code = PYTHON_LENGTHS.main()
    finally:
        sys.argv = saved_argv
    return _Result(returncode=code, stdout=out.getvalue())


def _write(repo: Path, rel: str, lines: int) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"print({i})" for i in range(lines)) + "\n", encoding="utf-8")


def test_warn_band_emits_interpretation_self_declaration(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    # 340 code lines: inside the skill-helper warn band [330, 360], below the limit.
    _write(repo, "skills/public/demo/scripts/helper.py", 340)

    result = _run("--repo-root", str(repo))

    assert result.returncode == 0
    assert "INTERPRETATION" in result.stdout
    assert "Consumer must answer first" in result.stdout
    assert "intentional" in result.stdout  # the load-bearing blind spot
    # As a standing run-quality.sh gate, a passing gate's output is only surfaced
    # when a line starts with WARNING|WARN|WEAK|ADVISORY. Lock that the declaration
    # carries a surfaced prefix so it is not logged-but-hidden on a warn-band pass.
    assert any(
        line.startswith("ADVISORY:") and "INTERPRETATION" in line
        for line in result.stdout.splitlines()
    )


def test_clean_pass_does_not_attach_interpretation(tmp_path: Path) -> None:
    # A clean pass is a verified fact ("Validated ... file(s)."); the inference-layer
    # declaration must not ride it (low-noise: no banner on a green verified result).
    repo = tmp_path / "repo"
    _write(repo, "skills/public/demo/scripts/small.py", 1)

    result = _run("--repo-root", str(repo))

    assert result.returncode == 0
    assert "INTERPRETATION" not in result.stdout


def test_hard_over_limit_failure_never_attaches_interpretation(tmp_path: Path) -> None:
    # The cardinal error guard: an over-limit file is a verified deterministic fact
    # (main() reports every hard failure and returns 1). The distrust declaration
    # must never attach.
    repo = tmp_path / "repo"
    _write(repo, "skills/public/demo/scripts/over.py", 361)

    out = io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["check_code_lengths.py", "--repo-root", str(repo)]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()) as err:
            code = PYTHON_LENGTHS.main()
    finally:
        sys.argv = saved_argv
    assert code == 1
    assert "exceed limit 360" in err.getvalue()
    assert "INTERPRETATION" not in out.getvalue()


def test_headroom_payload_carries_interpretation_only_when_near_limit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo, "skills/public/demo/scripts/band.py", 340)  # near-limit
    near = _run(
        "--repo-root", str(repo), "--headroom",
        "--paths", "skills/public/demo/scripts/band.py",
    )
    assert near.returncode == 0
    interpretation = yaml.safe_load(near.stdout)["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)

    # A file with comfortable headroom is a plain exact-fact report — no declaration.
    _write(repo, "skills/public/demo/scripts/roomy.py", 10)
    roomy = _run(
        "--repo-root", str(repo), "--headroom",
        "--paths", "skills/public/demo/scripts/roomy.py",
    )
    assert roomy.returncode == 0
    assert "interpretation" not in yaml.safe_load(roomy.stdout)


def test_length_interpretation_has_paired_consumer_requirement() -> None:
    reference = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    assert "check_code_lengths.py" in reference
    assert "length smell" in reference
