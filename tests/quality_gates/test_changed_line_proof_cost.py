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

_TEETH = "scripts/mutation/check_changed_line_mutation_coverage.py"


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


def test_context_collection_is_opt_in_and_decoupled_from_the_marker(
    tmp_path: Path, monkeypatch
) -> None:
    teeth = _load_teeth()
    monkeypatch.setattr(sys, "argv", ["teeth", "--collect-test-contexts"])
    assert teeth.parse_args().collect_test_contexts is True
    monkeypatch.setattr(sys, "argv", ["teeth"])
    assert teeth.parse_args().collect_test_contexts is False

    seen = _record_probe(monkeypatch, teeth)
    teeth._ensure_coverage(_probe_args(), tmp_path, tmp_path / "cov.json", "abc123")
    assert seen["dynamic_context"] is False

    seen = _record_probe(monkeypatch, teeth)
    teeth._ensure_coverage(
        _probe_args(collect_test_contexts=True), tmp_path, tmp_path / "cov.json", "abc123"
    )
    assert seen["dynamic_context"] is True

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


def _run_teeth(repo: Path, base: str, head: str, cov: Path, *args: str) -> dict:
    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
        *args,
    )
    return yaml.safe_load(result.stdout)


def test_skip_and_reuse_shapes_on_one_checkout(tmp_path: Path) -> None:
    repo, base, head = _two_commit_foo(tmp_path)
    cov = repo / "cov.json"

    cov.write_text('{"files": {}}', encoding="utf-8")
    (repo / "cov.json.changed-line.fingerprint").write_text("stale-marker\n", encoding="utf-8")
    stale = _run_teeth(repo, base, head, cov, "--require-fresh-coverage")
    assert "stale" in stale["reason"]
    assert "release_changed_line_coverage.py" in stale["resume_command"]
    assert "--base-sha" in stale["resume_command"]
    assert "--coverage-json" not in stale["resume_command"]

    cov.unlink()
    (repo / "cov.json.changed-line.fingerprint").unlink(missing_ok=True)
    absent = _run_teeth(repo, base, head, cov, "--skip-if-no-coverage")
    assert "release_changed_line_coverage.py" in absent["resume_command"]

    def write_corpus(*, show_contexts):
        meta = {"format": 3, "show_contexts": show_contexts} if show_contexts is not None else {"format": 3}
        cov.write_text(
            json.dumps(
                {
                    "meta": meta,
                    "files": {
                        "scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}
                    },
                }
            ),
            encoding="utf-8",
        )

    write_corpus(show_contexts=True)
    declined = _run_teeth(repo, base, head, cov)
    assert "per-test `contexts`" in declined["reason"]
    assert "release_changed_line_coverage.py" in declined["resume_command"]
    assert declined["ok"] is True
    assert declined["blocking"] == []

    write_corpus(show_contexts=False)
    plain = _run_teeth(repo, base, head, cov)
    assert "per-test `contexts`" not in str(plain.get("reason", ""))
    assert plain["changed_pool_files"] == ["scripts/foo.py"]

    write_corpus(show_contexts=None)
    unknown = _run_teeth(repo, base, head, cov)
    assert "per-test `contexts`" not in str(unknown.get("reason", ""))
    assert unknown["changed_pool_files"] == ["scripts/foo.py"]


def test_an_unreadable_coverage_header_is_unknown_not_context_bearing() -> None:
    """The `OSError` arm of the header probe. `None` must mean "unknown, proceed",
    because gating on an absence would refuse every corpus written by a coverage
    version that ordered its keys differently."""
    from runtime_bootstrap import import_repo_module

    sampling = import_repo_module(
        "scripts/mutation/mutation_sampling_lib.py", "scripts.mutation.mutation_sampling_lib"
    )

    assert sampling.coverage_is_context_bearing(Path("/nonexistent/never/here.json")) is None
