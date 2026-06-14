"""Unit tests for the aggregate doc-authoring preflight (scripts/check_doc_authoring_preflight.py).

The preflight forecasts, in one pass, the constraints an author otherwise
discovers by failing one commit gate at a time. These tests pin three
properties the goal requires:

  - a broken fixture surfaces every violation class in ONE call;
  - a clean fixture is silent;
  - the forecast does NOT drift from the real gates (it reuses them);
  - it stays a non-blocking affordance (absent from the blocking commit gate).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = "scripts/check_doc_authoring_preflight.py"
_pf = import_repo_module(__file__, "scripts.check_doc_authoring_preflight")
_handoff = import_repo_module(__file__, "scripts.validate_handoff_artifact")
_doc_links = import_repo_module(__file__, "scripts.check_doc_links")
_inline_code = import_repo_module(__file__, "scripts.check_markdown_inline_code")

_BROKEN_FIXTURE = (
    "# Demo Handoff\n"
    "\n"
    "- dash bullet\n"
    "+ plus bullet\n"  # MD004: inconsistent list marker
    "\n"
    "See `scripts/real_target.py` for the entrypoint.\n"  # backticked pathy ref
    "\n"
    "A wrapped `inline code\n"
    "span` here.\n"  # wrapped inline-code span
    "\n"
) + "".join(f"filler line {i}\n" for i in range(1, 71))  # push well past the 70-line cap

_CLEAN_FIXTURE = (
    "# Demo Handoff\n"
    "\n"
    "A clean paragraph with no wrapped spans, no mixed bullets, and no\n"
    "backticked file references.\n"
    "\n"
    "- one bullet\n"
    "- two bullet\n"
)


def _seed_repo(tmp_path: Path, body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(ROOT / ".markdownlint-cli2.jsonc", repo / ".markdownlint-cli2.jsonc")
    # A real tracked file so the backticked pathy ref resolves to an artifact.
    (repo / "scripts" / "real_target.py").write_text("x\n", encoding="utf-8")
    (repo / "docs" / "handoff.md").write_text(body, encoding="utf-8")
    return repo


def _run_script(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(ROOT / PREFLIGHT), "--repo-root", str(repo), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_broken_fixture_surfaces_all_classes_in_one_pass(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _BROKEN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")

    rules = {row["rule"] for row in report.markdownlint["findings"]}
    assert "MD004" in rules, f"markdownlint should forecast MD004; saw {rules}"
    assert report.wrapped_inline_code, "wrapped inline-code span not surfaced"
    assert any(
        row["kind"] == "backticked-ref" and row["detail"] == "scripts/real_target.py"
        for row in report.doc_links
    ), f"backticked pathy ref not surfaced: {report.doc_links}"
    assert report.length["over"], "length cap breach not surfaced"
    assert report.blocked


def test_length_cap_is_read_live_from_the_owning_validator(tmp_path: Path) -> None:
    # No-drift: the forecast cap must equal the gate's live constant, never a
    # hand-copied number.
    repo = _seed_repo(tmp_path, _BROKEN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")
    assert report.length["cap"] == _handoff.MAX_ARTIFACT_LINES


def test_clean_fixture_is_silent(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")
    assert not report.blocked
    assert not report.markdownlint["findings"]
    assert not report.wrapped_inline_code
    assert not report.doc_links
    assert not report.length["over"]


def test_general_doc_has_no_enforced_length_cap(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    (repo / "docs" / "guide.md").write_text(_CLEAN_FIXTURE, encoding="utf-8")
    report = _pf.build_report(repo, "docs/guide.md", None)
    assert report.length["surface"] is None
    assert report.length["over"] is False


def _gate_verdict_in_process(module: object, argv: list[str]) -> int:
    """Run a gate's real ``main()`` IN-PROCESS (no subprocess boundary) and
    return its verdict (0 pass / 1 fail). This is the independent gate path the
    no-drift cross-check compares the forecast against, while staying in-process
    so it is not a boundary-bypass candidate."""
    saved = sys.argv
    sys.argv = argv
    try:
        return module.main()  # type: ignore[attr-defined]
    except _doc_links.ValidationError:
        return 1
    finally:
        sys.argv = saved


def _real_gate_doc_links(repo: Path) -> int:
    return _gate_verdict_in_process(_doc_links, ["check_doc_links", "--repo-root", str(repo)])


def _real_gate_inline_code(repo: Path) -> int:
    return _gate_verdict_in_process(
        _inline_code, ["check_markdown_inline_code", "--repo-root", str(repo), "--path", "docs/handoff.md"]
    )


def _real_gate_markdownlint(repo: Path) -> int | None:
    cmd = _pf._resolve_markdownlint_cmd()
    if cmd is None:
        return None
    return subprocess.run(
        [*cmd, "--no-globs", "docs/handoff.md"],
        cwd=repo, check=False, capture_output=True, text=True,
    ).returncode


def test_no_drift_broken_fixture_matches_real_gate_verdicts(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _BROKEN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")

    # doc-link forecast fires iff the real check_doc_links gate fails.
    assert bool(report.doc_links) == (_real_gate_doc_links(repo) != 0)
    # wrapped-inline forecast fires iff the real inline-code gate fails.
    assert bool(report.wrapped_inline_code) == (_real_gate_inline_code(repo) != 0)
    # markdownlint forecast fires iff the real markdownlint engine fails.
    ml = _real_gate_markdownlint(repo)
    if ml is not None:
        assert bool(report.markdownlint["findings"]) == (ml != 0)
    # length forecast fires iff the file exceeds the gate's live cap.
    lines = (repo / "docs" / "handoff.md").read_text(encoding="utf-8").splitlines()
    assert report.length["over"] == (len(lines) > _handoff.MAX_ARTIFACT_LINES)


def test_no_drift_clean_fixture_passes_every_real_gate(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")
    assert not report.blocked
    assert _real_gate_doc_links(repo) == 0
    assert _real_gate_inline_code(repo) == 0
    ml = _real_gate_markdownlint(repo)
    if ml is not None:
        assert ml == 0


def test_cli_exit_code_blocks_on_broken_silent_on_clean(tmp_path: Path) -> None:
    broken = _seed_repo(tmp_path / "b", _BROKEN_FIXTURE)
    assert _run_script(broken, "--path", "docs/handoff.md", "--as-surface", "handoff").returncode == 1
    clean = _seed_repo(tmp_path / "c", _CLEAN_FIXTURE)
    assert _run_script(clean, "--path", "docs/handoff.md", "--as-surface", "handoff").returncode == 0


def test_non_blocking_affordance_guard() -> None:
    # The preflight must stay an affordance, never a precondition: it cannot be
    # wired into the blocking commit-gate plan. (An ADVISORY pointer in the slice
    # closeout is fine; a blocking gate member is not.) Guards Boundaries: "a
    # goal/doc must still commit without running it."
    gate_plan = (ROOT / "scripts" / "staged_commit_gate_plan.py").read_text(encoding="utf-8")
    assert "check_doc_authoring_preflight" not in gate_plan, (
        "doc-authoring preflight must not be a blocking commit-gate member"
    )
    doc = (_pf.__doc__ or "").lower()
    assert "affordance" in doc and "not a gate" in doc
