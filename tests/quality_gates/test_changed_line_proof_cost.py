"""Proof-cost pins for the changed-line gate (#696).

Two defects, one slice. Both are about what the gate COSTS rather than what it
decides, and both were invisible to every existing test because a verdict computed
expensively is byte-identical to the same verdict computed cheaply.

1. The probe collected per-test `dynamic_context` data that this gate has no
   reader for, gated on `--write-fresh-marker` -- a flag about stamping the
   freshness marker. Measured on the authoring repo, same coverage data with the
   export flag as the only difference: 8.22 GB vs 12.26 MB, and 36.5s / 20.44 GiB
   peak RSS vs 0.13s / 0.06 GiB just to load it.
2. When the gate could not USE the coverage it found, its structured payload named
   only the whole-corpus rebuild (measured 11-15 min) and not the incremental lane
   (measured ~24s for a single-commit slice). The cheap route existed and was
   reachable only by reading the source.

A separate module from `test_changed_line_mutation_coverage.py` on purpose: that
file is inside the advisory length warn band, and the repo's rule is to separate a
concept rather than append to a file near its cap.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from .seeding_support import load_module
from .support import ROOT, run_script

_TEETH = "scripts/check_changed_line_mutation_coverage.py"


def _load_teeth():
    return load_module("check_changed_line_mutation_coverage", ROOT / _TEETH)


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


_FOO_BASE = "def a():\n    return 1\n"
_FOO_HEAD = "def a():\n    return 1\n\n\ndef b():\n    return 2\n"


def _two_commit_foo(tmp_path: Path) -> tuple[Path, str, str]:
    from .repo_shapes import install_two_commit_repo

    return install_two_commit_repo(
        tmp_path / "repo",
        {"scripts/foo.py": _FOO_BASE},
        {"scripts/foo.py": _FOO_HEAD},
    )


def _skip_payload(tmp_path: Path, *, stale: bool) -> dict:
    """Drive the real script to a coverage-source skip and read its YAML payload.

    Uses the seeding helpers' shape rather than importing them: this module owns a
    single-purpose repo where one eligible pool file changed, which is the only
    state in which the skip branch is reachable (an empty changed set returns
    earlier).
    """
    repo, base, head = _two_commit_foo(tmp_path)

    cov = repo / "cov.json"
    args = ["--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
            "--reuse-coverage", "--coverage-json", str(cov)]
    if stale:
        # A coverage JSON WITH a fingerprint marker that does not match the current
        # changed-pool content: the stale branch, which is the one that used to name
        # only the 11-15 minute rebuild.
        cov.write_text('{"files": {}}', encoding="utf-8")
        (repo / "cov.json.changed-line.fingerprint").write_text("stale-marker\n", encoding="utf-8")
        args.append("--require-fresh-coverage")
    else:
        args.append("--skip-if-no-coverage")

    result = run_script(_TEETH, *args)
    return yaml.safe_load(result.stdout)


def test_the_stale_branch_publishes_a_copyable_resume_command(tmp_path: Path) -> None:
    payload = _skip_payload(tmp_path, stale=True)

    assert "stale" in payload["reason"]
    assert "release_changed_line_coverage.py" in payload["resume_command"]
    assert "--base-sha" in payload["resume_command"]


def test_the_absent_coverage_branch_publishes_the_same_route(tmp_path: Path) -> None:
    """Both branches reach the same dead end, so both must name the same way out.
    They used to answer with two different costs."""
    payload = _skip_payload(tmp_path, stale=False)

    assert "release_changed_line_coverage.py" in payload["resume_command"]


def test_the_resume_command_does_not_redirect_the_focused_corpus(tmp_path: Path) -> None:
    """A safety pin, not an ergonomics one.

    The release producer's own `--coverage-json` default is deliberately NOT the
    canonical corpus: its coverage comes from a test SUBSET, and parking that at the
    broad mutation report's path with a VALID freshness marker would make every
    `--require-fresh-coverage` consumer read freshness as breadth. If this route
    ever grows a `--coverage-json` argument, it hands the operator the command that
    does exactly that.
    """
    payload = _skip_payload(tmp_path, stale=True)

    assert "--coverage-json" not in payload["resume_command"]


# --------------------------------------------------------------------------- #
# 3. a corpus written by the OTHER consumer is declined cheaply
#
# The sampler needs `contexts` and defaults to the same canonical path this
# lane's producer writes, so whichever ran last decides whether the other works.
# Fixing the write side does not close that; the freshness marker fingerprints
# changed-pool CONTENT, not the writer, so a sampler-written corpus still carries
# a marker that validates. The read side has to notice.
# --------------------------------------------------------------------------- #


def _reuse_payload(tmp_path: Path, *, show_contexts) -> dict:
    repo, base, head = _two_commit_foo(tmp_path)

    cov = repo / "cov.json"
    meta = {"format": 3, "show_contexts": show_contexts} if show_contexts is not None else {"format": 3}
    cov.write_text(json.dumps({
        "meta": meta,
        "files": {"scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}},
    }), encoding="utf-8")

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov),
    )
    return yaml.safe_load(result.stdout)


def test_a_context_bearing_corpus_is_declined_with_the_route(tmp_path: Path) -> None:
    payload = _reuse_payload(tmp_path, show_contexts=True)

    assert "per-test `contexts`" in payload["reason"]
    assert "release_changed_line_coverage.py" in payload["resume_command"]


def test_declining_is_a_skip_and_never_a_blocker(tmp_path: Path) -> None:
    """The corpus being wrong for this READER says nothing about whether the
    changed lines are covered. Manufacturing a blocker from that would be the
    substitution this lane exists to refuse."""
    payload = _reuse_payload(tmp_path, show_contexts=True)

    assert payload["ok"] is True
    assert payload["blocking"] == []


def test_a_plain_corpus_is_still_used(tmp_path: Path) -> None:
    """The guard must not fire on this lane's own producer output, or it disables
    the reuse path it was added to protect."""
    payload = _reuse_payload(tmp_path, show_contexts=False)

    assert "per-test `contexts`" not in str(payload.get("reason", ""))
    assert payload["changed_pool_files"] == ["scripts/foo.py"]


def test_an_unreadable_header_proceeds_exactly_as_before(tmp_path: Path) -> None:
    """`None` means unknown, not suspicious. Gating on an absence would refuse
    every corpus written by a coverage version that ordered its keys differently
    -- a new refusal built on a fact nobody established."""
    payload = _reuse_payload(tmp_path, show_contexts=None)

    assert "per-test `contexts`" not in str(payload.get("reason", ""))
    assert payload["changed_pool_files"] == ["scripts/foo.py"]


def test_an_unreadable_coverage_header_is_unknown_not_context_bearing() -> None:
    """The `OSError` arm of the header probe. `None` must mean "unknown, proceed",
    because gating on an absence would refuse every corpus written by a coverage
    version that ordered its keys differently."""
    from runtime_bootstrap import import_repo_module

    sampling = import_repo_module(
        "scripts/mutation_sampling_lib.py", "scripts.mutation_sampling_lib"
    )

    assert sampling.coverage_is_context_bearing(Path("/nonexistent/never/here.json")) is None
