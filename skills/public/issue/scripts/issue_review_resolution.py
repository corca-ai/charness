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
_GOAL_RUN_INPUT = _load_local("issue_goal_run_input", "issue_review_goal_run_input")
_MARKDOWN = _load_local("issue_markdown_lib", "issue_review_markdown")
_FRESH_EYE = _load_local("issue_resolution_observer", "issue_review_fresh_eye")

_REPOSITORY_RE = re.compile(r"[^\s/#]+/[^\s/#]+\Z")
_ADJUDICATION_SECTION_RE = re.compile(
    r"^ {0,3}#{1,6}\s+adjudications?\s*\n(?P<body>.*?)(?=^ {0,3}#{1,6}\s|\Z)",
    re.I | re.M | re.S,
)
_ADJUDICATION_BULLET_RE = re.compile(
    r"^[ \t]*[-*+][ \t]+(.+?)(?=^[ \t]*[-*+][ \t]+|^ {0,3}#{1,6}\s|\Z)", re.M | re.S
)
_ADJUDICATION_VERDICT_RE = re.compile(
    r"^\s*Second observer verdict\s*:\s*corroborated\s*$", re.I | re.M
)


def validate_parent_adjudications(
    repo_root: Path,
    value: dict[str, Any],
    *,
    parent_obligation_path: Path,
    parent_obligation_text: str,
    evidence: list[dict[str, Any]],
    expected_children: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate explicit parent adjudications with the issue fresh-eye contract."""
    claims = _parent_adjudication_claims(parent_obligation_text)
    records = value.get("parent_adjudications", [])
    if not isinstance(records, list):
        raise _GOAL_RUN_INPUT.error(
            "schema-invalid", "final proof index.parent_adjudications must be a list"
        )
    if not claims:
        if records:
            raise _GOAL_RUN_INPUT.error(
                "proof-incomplete",
                "final proof index declares parent adjudications absent from the parent obligation",
            )
        return []
    if len(records) != len(claims):
        raise _GOAL_RUN_INPUT.error(
            "adjudication-uncorroborated",
            "each parent adjudication needs a matching second-observer record or a reasoned override",
        )

    by_role = {item["role"]: item for item in evidence}
    child_numbers = {child["number"] for child in expected_children}
    reviewed: list[dict[str, Any]] = []
    for index, (record, claim) in enumerate(zip(records, claims, strict=True)):
        context = f"final proof index.parent_adjudications[{index}]"
        if not isinstance(record, dict):
            raise _GOAL_RUN_INPUT.error("schema-invalid", f"{context} must be an object")
        _GOAL_RUN_INPUT.fields(
            record,
            {"claim", "child_number", "observer_role", "independent_roles", "override_reason"},
            context,
        )
        child_number, override = _validate_parent_adjudication(
            record, claim, child_numbers=child_numbers, context=context
        )
        if override is not None:
            reviewed.append(
                {
                    "claim": claim,
                    "child_number": child_number,
                    "status": "overridden",
                    "override_reason": override,
                }
            )
            continue
        reviewed.append(
            _corroborate_parent_adjudication(
                repo_root,
                record,
                claim=claim,
                child_number=child_number,
                by_role=by_role,
                parent_obligation_path=parent_obligation_path,
                repo=str(value["repo"]),
                context=context,
            )
        )
    return reviewed


def _parent_adjudication_claims(text: str) -> list[str]:
    plain = "\n".join(_MARKDOWN.strip_code_fences(text))
    section = _ADJUDICATION_SECTION_RE.search(plain)
    if section is None:
        return []
    return [" ".join(item.split()) for item in _ADJUDICATION_BULLET_RE.findall(section["body"])]


def _validate_parent_adjudication(
    record: dict[str, Any],
    claim: str,
    *,
    child_numbers: set[int],
    context: str,
) -> tuple[int, str | None]:
    recorded_claim = record.get("claim")
    if not isinstance(recorded_claim, str) or " ".join(recorded_claim.split()) != claim:
        raise _GOAL_RUN_INPUT.error("evidence-mismatch", f"{context}.claim does not match obligation")
    child_number = _GOAL_RUN_INPUT.positive(record.get("child_number"), f"{context}.child_number")
    if child_number not in child_numbers:
        raise _GOAL_RUN_INPUT.error("parent-mismatch", f"{context}.child_number is not an expected child")
    override = record.get("override_reason")
    if override is not None and (
        not isinstance(override, str) or not override.strip() or len(override.strip()) > 2000
    ):
        raise _GOAL_RUN_INPUT.error("schema-invalid", f"{context}.override_reason must be non-empty")
    return child_number, override.strip() if isinstance(override, str) else None


def _uncorroborated(context: str, detail: str) -> Any:
    return _GOAL_RUN_INPUT.error("adjudication-uncorroborated", f"{context} {detail}")


def _corroborate_parent_adjudication(
    repo_root: Path,
    record: dict[str, Any],
    *,
    claim: str,
    child_number: int,
    by_role: dict[str, dict[str, Any]],
    parent_obligation_path: Path,
    repo: str,
    context: str,
) -> dict[str, Any]:
    observer_role = record.get("observer_role")
    independent_roles = record.get("independent_roles")
    valid_roles = (
        isinstance(observer_role, str)
        and bool(observer_role.strip())
        and isinstance(independent_roles, list)
        and bool(independent_roles)
        and all(isinstance(role, str) and role.strip() for role in independent_roles)
        and len(independent_roles) == len(set(independent_roles))
        and observer_role not in independent_roles
    )
    if not valid_roles:
        raise _uncorroborated(context, "needs distinct observer and evidence roles")
    if observer_role not in by_role or any(role not in by_role for role in independent_roles):
        raise _uncorroborated(context, "cites roles not bound by the final proof index")
    observer = by_role[observer_role]
    independent = [by_role[role] for role in independent_roles]
    parent_path = parent_obligation_path.resolve()
    if Path(observer["path"]).resolve() == parent_path or any(
        Path(item["path"]).resolve() == parent_path for item in independent
    ):
        raise _uncorroborated(context, "cannot use the parent summary as observer evidence")
    try:
        report_text = Path(observer["path"]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise _uncorroborated(context, f"observer report is unreadable: {exc}") from exc
    if (
        not _ADJUDICATION_VERDICT_RE.search(report_text)
        or claim not in report_text
        or any(Path(item["path"]).name not in report_text for item in independent)
    ):
        raise _uncorroborated(context, "report does not support the claim from distinct evidence")
    check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": observer["path"]}]}
    fresh_eye = _FRESH_EYE._observer_disposition(
        repo_root,
        check,
        expected_issue_numbers=[child_number],
        expected_repository=repo,
    )
    if not fresh_eye or fresh_eye.get("disposition") != "delegated":
        raise _uncorroborated(context, f"has no verified distinct observer: {(fresh_eye or {}).get('disposition', 'unavailable')}")
    return {
        "claim": claim,
        "child_number": child_number,
        "status": "corroborated",
        "observer_role": observer_role,
        "observer_report": observer["path"],
        "independent_evidence": [item["path"] for item in independent],
        "fresh_eye_observer": fresh_eye,
    }


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
        "For a parent adjudication in the caller focus, inspect distinct evidence, not its summary, "
        "and do not rerun the lane. Report the exact claim, a corroborated/not-corroborated verdict, "
        "and each independent evidence path. "
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
