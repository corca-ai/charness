from __future__ import annotations

import re
import runpy
from argparse import Namespace
from pathlib import Path
from typing import Any, Callable

_load_local = runpy.run_path(str(Path(__file__).resolve().with_name("issue_local_import.py")))[
    "sibling_loader"
](__file__)
ISSUE_RESOLUTION_SCOPE_PREFIX = _load_local("issue_worker_targets").ISSUE_RESOLUTION_SCOPE_PREFIX

_REPOSITORY_RE = re.compile(r"[^\s/#]+/[^\s/#]+\Z")


def _load_package_script(skill: str, name: str) -> Any:
    """Load a canonical script from this source or installed package layout."""
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise RuntimeError("skill_runtime_bootstrap.py not found")
    runtime = runpy.run_path(str(bootstrap))
    package_root = runtime["repo_root_from_skill_script"](__file__)
    layout = runtime["load_repo_module_from_skill_script"](__file__, "scripts.core.repo_layout")
    load_path_module = runtime["load_repo_module_from_skill_script"](
        __file__, "scripts.skill_runtime_bootstrap"
    ).load_path_module
    if skill == "critique":
        script = layout.public_skills_dir(package_root) / skill / "scripts" / name
    else:
        script = layout.repo_script(package_root, name)
    if not script.is_file():
        raise RuntimeError(f"package-owned script is unavailable: {script}")
    return load_path_module(f"charness_issue_tool_{skill}_{Path(name).stem}", script)


def _refusal(
    *,
    emit: Callable[[dict[str, Any]], None],
    repo: str,
    scope: str,
    lens: str,
    reason_code: str,
    error: str,
    details: dict[str, Any] | None = None,
) -> int:
    emit(
        {
            "ok": False,
            "status": "runner-invalid",
            "execution_state": "preflight-blocked",
            "lifecycle_state": "preflight-blocked",
            "reviewer_started": False,
            "delivery_state": "none",
            "verdict_state": "not-applicable",
            "approval_eligible": False,
            "reason_code": reason_code,
            "error": error,
            "details": details or {},
            "repo": repo,
            "scope": scope,
            "lens": lens,
        }
    )
    return 2


def _inputs(args: Namespace) -> tuple[list[str], list[Path]]:
    repo = str(args.repo).strip()
    if _REPOSITORY_RE.fullmatch(repo) is None:
        raise ValueError("--repo must be an owner/repo repository identity")
    numbers = list(args.number or [])
    if not numbers:
        raise ValueError("at least one --number is required")
    if any(type(number) is not int or number <= 0 for number in numbers):
        raise ValueError("--number values must be positive integers")
    if len(numbers) != len(set(numbers)):
        raise ValueError("--number values must be distinct")
    raw_paths = list(args.reviewed_path or [])
    if not raw_paths or any(not str(path).strip() for path in raw_paths):
        raise ValueError("at least one non-empty --reviewed-path is required")
    if len(raw_paths) != len(set(raw_paths)):
        raise ValueError("--reviewed-path values must be distinct")
    lens = str(args.lens).strip()
    if not lens:
        raise ValueError("--lens must be non-empty")

    root = Path(args.repo_root).expanduser().resolve()
    selected_paths: list[Path] = []
    for raw_path in raw_paths:
        path = Path(raw_path).expanduser()
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"--reviewed-path must be repository-relative: {raw_path}")
        lexical = root / path
        resolved = lexical.resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"--reviewed-path resolves outside --repo-root: {raw_path}") from exc
        selected_paths.append(lexical if lexical.is_symlink() else resolved)
    targets = [f"{repo}#{number}" for number in numbers]
    return targets, selected_paths


def _selected_violations(root: Path, selected_paths: list[Path]) -> list[str]:
    durability = _load_package_script("scripts", "gates/check_spec_evidence_durability.py")
    try:
        return durability.selected_doc_violations(root, selected_paths)
    except durability.ValidationError as exc:
        raise ValueError(str(exc)) from exc


def command_review_resolution(args: Namespace, *, emit: Callable[[dict[str, Any]], None]) -> int:
    scope = (
        f"{ISSUE_RESOLUTION_SCOPE_PREFIX}: review resolution/recurrence and "
        "per-target behavioral observations"
    )
    lens = (
        "Assess the resolution and recurrence protection for each target, with "
        "an evidence-backed behavioral verdict. Pass only when the repair is "
        "supported; block or defer when it is not. Diagnosis alone is insufficient. "
        "Additional caller focus: "
        f"{str(args.lens).strip()}"
    )
    try:
        targets, selected_paths = _inputs(args)
    except ValueError as exc:
        return _refusal(
            emit=emit,
            repo=str(args.repo),
            scope=scope,
            lens=lens,
            reason_code="input-invalid",
            error=str(exc),
        )

    root = Path(args.repo_root).expanduser().resolve()
    try:
        violations = _selected_violations(root, selected_paths)
    except (OSError, ValueError, RuntimeError) as exc:
        return _refusal(
            emit=emit,
            repo=str(args.repo),
            scope=scope,
            lens=lens,
            reason_code="evidence-durability",
            error=str(exc),
            details={"reviewed_paths": list(args.reviewed_path or [])},
        )
    if violations:
        return _refusal(
            emit=emit,
            repo=str(args.repo),
            scope=scope,
            lens=lens,
            reason_code="evidence-durability",
            error="selected review evidence is not durable:\n" + "\n".join(violations),
            details={
                "reviewed_paths": list(args.reviewed_path or []),
                "violations": violations,
                "remedy": "Repair the cited evidence or mark the citation as reproduction-source, then rerun.",
            },
        )

    runner = _load_package_script("critique", "run_review.py")
    argv = [
        "--repo-root",
        str(root),
        "--scope",
        f"{scope} for {', '.join(targets)}; do not merely diagnose causes",
        "--lens",
        lens,
    ]
    for reviewed_path in args.reviewed_path:
        argv.extend(("--reviewed-path", reviewed_path))
    for target in targets:
        argv.extend(("--prepared-target", target))
    if args.attempt_id is not None:
        argv.extend(("--attempt-id", args.attempt_id))
    if args.goal_lineage_file is not None:
        argv.extend(("--goal-lineage-file", args.goal_lineage_file))
    if args.dry_run:
        argv.append("--dry-run")
    return runner.main(argv)
