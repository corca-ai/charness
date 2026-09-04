"""How the critique runner spells a DECLARED reviewed path.

Separate from the identity tests, which own what a path BINDS. This owns the step
before: turning a manifest line into the name the packet declares. The two must
agree, and they did not — the runner refused symlinks the identity had just been
taught to bind, then renamed the ones it allowed.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _support():
    spec = importlib.util.spec_from_file_location(
        "run_review_support", ROOT / "skills/public/critique/scripts/run_review_support.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pointer_repo(tmp_path: Path) -> Path:
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "2026-08-30-record.md").write_text("# Record\n", encoding="utf-8")
    (records / "latest.md").symlink_to("2026-08-30-record.md")
    return tmp_path


def test_a_declared_current_pointer_keeps_its_own_name(tmp_path: Path) -> None:
    """`.resolve()` renamed the pointer to the record it points at.

    The declared set then carried the target while the reviewed range carried the
    pointer, so `changed-ref-path-mismatch` fired forever on any range that
    touched a `latest.md` — which is every range that files a record.
    """
    support = _support()
    root = _pointer_repo(tmp_path)

    resolved = support.repo_path(
        root, "charness-artifacts/quality/latest.md", label="reviewed path", allow_symlink=True
    )

    assert support.relative(root, resolved) == "charness-artifacts/quality/latest.md"


def test_hold_out_hides_the_path_during_the_run_and_restores_it(tmp_path: Path) -> None:
    support = _support()
    target = tmp_path / "in-progress.md"
    target.write_text("TODO\n", encoding="utf-8")
    seen_inside: list[bool] = []

    with support.hold_out(tmp_path, ["in-progress.md"]):
        seen_inside.append(target.exists())

    assert seen_inside == [False]
    assert target.read_text(encoding="utf-8") == "TODO\n"


def test_hold_out_refuses_a_missing_path(tmp_path: Path) -> None:
    support = _support()
    with pytest.raises(support.RunReviewError, match="hold-out path does not exist"):
        with support.hold_out(tmp_path, ["gone.md"]):
            pass


def test_hold_out_restores_the_path_after_a_failed_run(tmp_path: Path) -> None:
    support = _support()
    target = tmp_path / "in-progress.md"
    target.write_text("TODO\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="boom"):
        with support.hold_out(tmp_path, ["in-progress.md"]):
            raise RuntimeError("boom")

    assert target.read_text(encoding="utf-8") == "TODO\n"


def test_promote_worker_report_copies_only_the_combined_report(tmp_path: Path) -> None:
    support = _support()
    runtime = tmp_path / ".charness" / "reviewer-round-attempt-1"
    runtime.mkdir(parents=True)
    (runtime / "worker-report.yaml").write_text("schema_version: charness.reviewer_worker_report.v1\n", encoding="utf-8")
    (runtime / "runner.stderr").write_text("noise\n", encoding="utf-8")

    dest = support.promote_worker_report(tmp_path, "attempt-1", runtime / "worker-report.yaml")

    assert dest == tmp_path / "charness-artifacts" / "critique" / "workers" / "attempt-1" / "worker-report.yaml"
    assert dest.read_text(encoding="utf-8") == "schema_version: charness.reviewer_worker_report.v1\n"
    assert not (dest.parent / "runner.stderr").exists()
    assert support.promote_worker_report(tmp_path, "attempt-1", runtime / "missing.yaml") is None
    with pytest.raises(support.RunReviewError, match="overwrite existing durable worker report"):
        support.promote_worker_report(tmp_path, "attempt-1", runtime / "worker-report.yaml")


def test_load_and_promote_report_rewrites_the_emitted_report_path(tmp_path: Path) -> None:
    support = _support()
    runtime = tmp_path / ".charness" / "reviewer-round-ok"
    runtime.mkdir(parents=True)
    report = runtime / "worker-report.yaml"
    report.write_text("schema_version: v1\napproval_eligible: true\n", encoding="utf-8")
    paths = {"report": report}
    context = {"paths": {"report": ".charness/reviewer-round-ok/worker-report.yaml"}}

    loaded = support.load_and_promote_report(tmp_path, "ok", paths, context)

    assert loaded is not None and loaded["approval_eligible"] is True
    cited = "charness-artifacts/critique/workers/ok/worker-report.yaml"
    assert context["paths"]["report"] == cited
    assert context["paths"]["durable_report"] == cited
    assert context["paths"]["runtime_report"] == ".charness/reviewer-round-ok/worker-report.yaml"


def test_load_and_promote_report_skips_a_non_approval_report(tmp_path: Path) -> None:
    support = _support()
    runtime = tmp_path / ".charness" / "reviewer-round-no"
    runtime.mkdir(parents=True)
    report = runtime / "worker-report.yaml"
    report.write_text("schema_version: v1\napproval_eligible: false\n", encoding="utf-8")
    context = {"paths": {"report": ".charness/reviewer-round-no/worker-report.yaml"}}

    support.load_and_promote_report(tmp_path, "no", {"report": report}, context)

    assert context["paths"] == {"report": ".charness/reviewer-round-no/worker-report.yaml"}
    assert not (tmp_path / "charness-artifacts" / "critique" / "workers" / "no").exists()


def test_a_file_the_runner_opens_still_refuses_a_symlink(tmp_path: Path) -> None:
    """The discriminator: `allow_symlink` must not leak to the read paths.

    A packet or manifest behind a link could be swapped underneath the runner, so
    that refusal is correct where it applies and must survive this change.
    """
    support = _support()
    root = _pointer_repo(tmp_path)

    with pytest.raises(support.RunReviewError, match="must not be a symlink"):
        support.repo_path(root, "charness-artifacts/quality/latest.md", label="packet-file")


def test_an_ordinary_path_is_unaffected(tmp_path: Path) -> None:
    support = _support()
    root = _pointer_repo(tmp_path)

    resolved = support.repo_path(
        root, "charness-artifacts/quality/2026-08-30-record.md", label="reviewed path"
    )

    assert support.relative(root, resolved) == "charness-artifacts/quality/2026-08-30-record.md"


def test_a_symlink_escaping_the_repo_root_is_still_refused(tmp_path: Path) -> None:
    """Allowing symlinks must not open the boundary `.resolve()` was guarding."""
    support = _support()
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.md").write_text("secret\n", encoding="utf-8")
    (root / "escape.md").symlink_to(outside / "secret.md")

    with pytest.raises(support.RunReviewError, match="resolves outside"):
        support.repo_path(root, "escape.md", label="reviewed path", allow_symlink=True)
