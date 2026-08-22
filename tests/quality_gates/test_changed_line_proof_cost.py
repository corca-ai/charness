"""Proof-cost pins for the changed-line gate (#696).

Two defects, one slice. Both are about what the gate COSTS rather than what it
decides, and both were invisible to every existing test because a verdict computed
expensively is byte-identical to the same verdict computed cheaply.

1. The probe collected per-test `dynamic_context` data that this gate has no
   reader for, gated on `--write-fresh-marker` -- a flag about stamping the
   freshness marker. Measured on the authoring repo, same coverage data with the
   export flag as the only difference: 8.22 GB vs 12.25 MB, and 37.2s / 20.4 GB
   peak RSS vs 0.13s / 0.06 GB just to load it.
2. When the gate could not USE the coverage it found, its structured payload named
   only the whole-corpus rebuild (measured 11-15 min) and not the incremental lane
   (measured ~24s for a single-commit slice). The cheap route existed and was
   reachable only by reading the source.

A separate module from `test_changed_line_mutation_coverage.py` on purpose: that
file is inside the advisory length warn band, and the repo's rule is to separate a
concept rather than append to a file near its cap.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from .support import ROOT, run_script

_TEETH = "scripts/check_changed_line_mutation_coverage.py"


def _load_teeth():
    spec = importlib.util.spec_from_file_location(
        "check_changed_line_mutation_coverage", ROOT / _TEETH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _probe_args(**overrides):
    base = {
        "reuse_coverage": False,
        "config": Path("cosmic-ray.toml"),
        "write_fresh_marker": False,
        "test_command": "python3 -m pytest -q",
        "collect_test_contexts": False,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _record_probe(monkeypatch, teeth) -> dict:
    seen: dict = {}

    def fake_probe(repo_root, command, coverage_json, *, dynamic_context=True) -> None:
        seen["dynamic_context"] = dynamic_context

    monkeypatch.setattr(teeth, "run_test_coverage", fake_probe)
    monkeypatch.setattr(teeth, "write_coverage_fingerprint_marker", lambda *a, **k: "fp")
    return seen


# --------------------------------------------------------------------------- #
# 1. contexts are OFF by default and no longer ride on --write-fresh-marker
# --------------------------------------------------------------------------- #


def test_the_context_flag_exists_and_parses(monkeypatch) -> None:
    """Pins that the FLAG EXISTS. Without this, the behavioural tests below stay
    green against a tree where `--collect-test-contexts` was never added, because
    they build the args namespace themselves and never go through argparse."""
    teeth = _load_teeth()
    monkeypatch.setattr(sys, "argv", ["teeth", "--collect-test-contexts"])

    assert teeth.parse_args().collect_test_contexts is True


def test_the_context_flag_defaults_off(monkeypatch) -> None:
    teeth = _load_teeth()
    monkeypatch.setattr(sys, "argv", ["teeth"])

    assert teeth.parse_args().collect_test_contexts is False


def test_the_default_probe_collects_no_contexts(tmp_path: Path, monkeypatch) -> None:
    teeth = _load_teeth()
    seen = _record_probe(monkeypatch, teeth)

    teeth._ensure_coverage(_probe_args(), tmp_path, tmp_path / "cov.json", "abc123")

    assert seen["dynamic_context"] is False


def test_the_opt_in_flag_restores_context_collection(tmp_path: Path, monkeypatch) -> None:
    """The cosmic-ray sampler is the one real reader of the `contexts` block, so the
    capability stays reachable -- it just stops being the default nobody asked for."""
    teeth = _load_teeth()
    seen = _record_probe(monkeypatch, teeth)

    teeth._ensure_coverage(
        _probe_args(collect_test_contexts=True), tmp_path, tmp_path / "cov.json", "abc123"
    )

    assert seen["dynamic_context"] is True


def test_the_marker_flag_no_longer_governs_context_collection(tmp_path: Path, monkeypatch) -> None:
    """THE decoupling pin, and the one that would catch a revert.

    `--write-fresh-marker` used to decide both things: it stamped the freshness
    marker AND silently chose the cheap probe, which left the other arm paying 671x
    for a column no reader consults. Both marker arms must now answer the context
    question the same way, because the marker has nothing to do with it.
    """
    teeth = _load_teeth()
    answers = {}
    for marker in (False, True):
        seen = _record_probe(monkeypatch, teeth)
        teeth._ensure_coverage(
            _probe_args(write_fresh_marker=marker), tmp_path, tmp_path / "cov.json", "abc123"
        )
        answers[marker] = seen["dynamic_context"]

    assert answers == {False: False, True: False}


# --------------------------------------------------------------------------- #
# 2. the route back to a usable verdict is in the STRUCTURED payload
# --------------------------------------------------------------------------- #


def _skip_payload(tmp_path: Path, *, stale: bool) -> dict:
    """Drive the real script to a coverage-source skip and read its YAML payload.

    Uses the seeding helpers' shape rather than importing them: this module owns a
    single-purpose repo where one eligible pool file changed, which is the only
    state in which the skip branch is reachable (an empty changed set returns
    earlier).
    """
    import subprocess

    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=repo, check=True, capture_output=True, text=True
        ).stdout.strip()

    git("init", "-q")
    foo = repo / "scripts" / "foo.py"
    foo.write_text("def a():\n    return 1\n", encoding="utf-8")
    git("add", "-A")
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    foo.write_text("def a():\n    return 1\n\n\ndef b():\n    return 2\n", encoding="utf-8")
    git("add", "-A")
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "head")
    head = git("rev-parse", "HEAD")

    cov = repo / "cov.json"
    args = ["--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
            "--reuse-coverage", "--coverage-json", str(cov)]
    if stale:
        # A coverage JSON WITH a fingerprint marker that does not match the current
        # changed-pool content: the stale branch, which is the one that used to name
        # only the 11-15 minute rebuild.
        cov.write_text('{"files": {}}', encoding="utf-8")
        (repo / "cov.json.fingerprint").write_text("stale-marker\n", encoding="utf-8")
        args.append("--require-fresh-coverage")
    else:
        args.append("--skip-if-no-coverage")

    result = run_script(_TEETH, *args)
    return yaml.safe_load(result.stdout)


def test_the_stale_branch_publishes_a_copyable_resume_command(tmp_path: Path) -> None:
    payload = _skip_payload(tmp_path, stale=True)

    assert "stale" in payload["reason"]
    assert "prepush_focused_changed_line_coverage.py" in payload["resume_command"]
    assert "--base-sha" in payload["resume_command"]


def test_the_absent_coverage_branch_publishes_the_same_route(tmp_path: Path) -> None:
    """Both branches reach the same dead end, so both must name the same way out.
    They used to answer with two different costs."""
    payload = _skip_payload(tmp_path, stale=False)

    assert "prepush_focused_changed_line_coverage.py" in payload["resume_command"]


def test_the_route_names_the_cheap_lane_before_the_rebuild(tmp_path: Path) -> None:
    """ORDER is the finding, not mere presence. The broad producer was always
    named; naming it FIRST -- as the only option -- is what cost the rebuilds."""
    payload = _skip_payload(tmp_path, stale=True)
    route = payload["resume_route"]

    assert route.index("prepush_focused_changed_line_coverage.py") < route.index(
        "run_slice_closeout.py"
    ), route


def test_the_resume_command_does_not_redirect_the_focused_corpus(tmp_path: Path) -> None:
    """A safety pin, not an ergonomics one.

    The incremental lane's own `--coverage-json` default is deliberately NOT the
    canonical corpus: its coverage comes from a test SUBSET, and parking that at the
    broad producer's path with a VALID freshness marker would make every
    `--require-fresh-coverage` consumer read freshness as breadth. If this route
    ever grows a `--coverage-json` argument, it hands the operator the command that
    does exactly that.
    """
    payload = _skip_payload(tmp_path, stale=True)

    assert "--coverage-json" not in payload["resume_command"]
