"""Promote a gitignored worker-report.yaml into visible knowledge."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path
from typing import Any

DURABLE_WORKER_REPORTS = Path("charness-artifacts") / "critique" / "workers"


def _support() -> Any:
    for name in ("charness_run_review_support", "run_review_support"):
        module = sys.modules.get(name)
        if module is not None:
            return module
    path = Path(__file__).with_name("run_review_support.py")
    spec = importlib.util.spec_from_file_location("charness_run_review_support", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load run_review_support: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["charness_run_review_support"] = module
    spec.loader.exec_module(module)
    return module


def promote_worker_report(root: Path, attempt: str, runtime_report: Path) -> Path | None:
    """Copy the combined report into visible knowledge so a clean clone can cite it.

    The run directory stays gitignored. Only `worker-report.yaml` is promoted.
    """
    if not runtime_report.is_file():
        return None
    dest_dir = (root / DURABLE_WORKER_REPORTS / attempt).resolve()
    try:
        dest_dir.relative_to(root.resolve())
    except ValueError as exc:
        raise _support().RunReviewError(
            "path-invalid", "durable worker report directory escaped repository root"
        ) from exc
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "worker-report.yaml"
    if dest.exists() or dest.is_symlink():
        raise _support().RunReviewError(
            "stale-artifact-refused",
            f"refusing to overwrite existing durable worker report: {dest}",
        )
    shutil.copyfile(runtime_report, dest)
    return dest


def load_and_promote_report(
    root: Path, attempt: str, paths: dict[str, Path], context: dict[str, Any]
) -> dict[str, Any] | None:
    support = _support()
    report = support.load_mapping(paths["report"])
    if not (isinstance(report, dict) and report.get("approval_eligible") is True):
        return report
    durable = promote_worker_report(root, attempt, paths["report"])
    if durable is not None:
        cited = support.relative(root, durable)
        context["paths"]["runtime_report"] = context["paths"]["report"]
        context["paths"]["report"] = cited
        context["paths"]["durable_report"] = cited
    return report
