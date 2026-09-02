#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
# The required-fields / unique-id / typed-enum loop over a structured-entry
# section, shared with the critique `## Structured Findings` floor.
_structured_entry_floor = import_repo_module(__file__, "scripts.structured_entry_floor")
ValidationError = _artifact_validator.ValidationError
report_validation_failure = _artifact_validator.report_validation_failure
run_changed_artifact_validator = _artifact_validator.run_changed_artifact_validator
git_changed_paths = _artifact_validator.git_changed_paths
_quality_adapter = import_repo_module(__file__, "scripts.quality_adapter_lib")
load_quality_adapter = _quality_adapter.load_quality_adapter
_quality_universes = import_repo_module(__file__, "scripts.quality_universes_lib")
DEFAULT_ARTIFACT_ROOTS = _quality_universes.DEFAULT_ARTIFACT_ROOTS
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe

IDEATION_ARTIFACT_ROOT = DEFAULT_ARTIFACT_ROOTS["ideation"]
IDEATION_ARTIFACT_PREFIX = f"{IDEATION_ARTIFACT_ROOT}/"
STRUCTURED_QUESTIONS_HEADING = "## Structured Questions"
STRUCTURED_URGENCY = frozenset({"must-resolve", "probe-in-impl", "defer"})
STRUCTURED_ACTIONS = frozenset({"spec", "impl", "hold"})
STRUCTURED_REQUIRED_FIELDS = ("urgency", "depends-on", "action", "note")


def changed_paths(repo_root: Path) -> list[str]:
    return git_changed_paths(repo_root, artifact_label="ideation")


def _ideation_universe(repo_root: Path):
    return resolve_universe(
        load_quality_adapter(repo_root),
        "artifact_roots.ideation",
        default=IDEATION_ARTIFACT_ROOT,
    )


def _ideation_prefix(repo_root: Path) -> str:
    patterns = _ideation_universe(repo_root).patterns
    return f"{patterns[0].rstrip('/')}/" if patterns else IDEATION_ARTIFACT_PREFIX


def _resolved_ideation_scope(repo_root: Path) -> list[Path]:
    universe = _ideation_universe(repo_root)
    files = [path for path in matching_files(repo_root, universe) if path.suffix.lower() == ".md"]
    refusal = refuse_if_declared_and_empty(universe, files, "validate-ideation-artifact")
    if refusal:
        raise ValidationError(refusal)
    return files


def candidate_paths(repo_root: Path, paths: list[str], *, all_artifacts: bool) -> list[Path]:
    if all_artifacts:
        files = _resolved_ideation_scope(repo_root)
        if not files:
            print(
                "Discovered empty ideation artifact universe: no Markdown artifacts "
                "matched the configured scope."
            )
        return files
    candidates: list[Path] = []
    prefix = _ideation_prefix(repo_root)
    for relpath in paths:
        if relpath.startswith(prefix) and relpath.endswith(".md"):
            path = repo_root / relpath
            if path.is_file():
                candidates.append(path)
    return sorted(candidates)


def validate_structured_questions(path: Path, text: str) -> None:
    _structured_entry_floor.validate_structured_entries(
        path,
        text,
        heading=STRUCTURED_QUESTIONS_HEADING,
        required_fields=STRUCTURED_REQUIRED_FIELDS,
        enum_fields={"urgency": STRUCTURED_URGENCY, "action": STRUCTURED_ACTIONS},
    )


def validate_ideation_artifact(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    validate_structured_questions(path, text)


def main() -> int:
    # `validate_ideation_artifact` runs a single rule, so one-pass here means
    # across ARTIFACTS: aborting on the first bad one hides the rest of a
    # multi-artifact batch behind one edit.
    return run_changed_artifact_validator(
        default_repo_root=REPO_ROOT,
        all_help="Validate every checked ideation artifact.",
        artifact_label="ideation artifact",
        changed_paths_fn=changed_paths,
        candidate_paths_fn=candidate_paths,
        validate_factory=lambda _run: validate_ideation_artifact,
        fail_fast_help=(
            "Stop at the first failing artifact instead of reporting every failure in one pass."
        ),
        owned_prefix=_ideation_prefix,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        raise SystemExit(report_validation_failure(str(exc), artifact_type="ideation"))
