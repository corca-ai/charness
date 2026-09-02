from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.adapter_lib import (  # noqa: E402
    declared_fields_after_version_check,
    load_yaml_file_report,
    normalize_adapter_result,
    parse_failure_error,
    read_failure_error,
    uninterpreted_warnings,
)
from scripts.adapters.adapter_field_application import apply_optional_fields  # noqa: E402
from scripts.adapters.adapter_version_verdict import declarations_unhonored  # noqa: E402
from scripts.artifacts.artifact_naming_lib import ARTIFACT_CLASSES, RECORD_PATTERN  # noqa: E402

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from")
# `(field_name, minimum)` pairs a skill opts into; see `validate_simple_adapter_data`.
IntFields = tuple[tuple[str, int], ...]
# `(retired_name, replacement_name, why)` triples a skill opts into. A field this loader
# stopped reading is INVISIBLE to every other refusal channel: `parse_failure_error` and
# the uninterpreted-line sink report what the PARSER dropped, and a well-formed key the
# SCHEMA no longer reads parses perfectly. Without this, a consuming repo's declared
# setting goes inert under a `valid: true` payload -- the same silent-inertness this
# repo already measured when a coordination floor recognized only one repo's names.
RetiredFields = tuple[tuple[str, str, str], ...]
ValidateAdapter = Callable[[dict[str, Any], Path], tuple[dict[str, Any], list[str], list[str]]]
InferDefaults = Callable[[Path], dict[str, Any]]
ExtraPayload = Callable[[dict[str, Any], dict[str, Any], bool], dict[str, Any]]


def adapter_candidates(skill_id: str) -> tuple[Path, ...]:
    return (Path(f".agents/{skill_id}-adapter.yaml"),)


def searched_adapter_paths(repo_root: Path, skill_id: str) -> list[str]:
    return [str((repo_root / candidate).resolve()) for candidate in adapter_candidates(skill_id)]


def find_adapter(repo_root: Path, skill_id: str) -> Path | None:
    return next(
        (repo_root / candidate for candidate in adapter_candidates(skill_id) if (repo_root / candidate).is_file()),
        None,
    )


def artifact_path(output_dir: str, artifact_filename: str) -> str:
    return str(Path(output_dir) / artifact_filename)


def record_artifact_pattern(output_dir: str) -> str:
    return str(Path(output_dir) / RECORD_PATTERN)


def load_adapter_contract(
    repo_root: Path,
    *,
    skill_id: str,
    infer_defaults: InferDefaults,
    validate_adapter_data: ValidateAdapter,
    missing_warnings: tuple[str, ...],
    artifact_filename: str | None = None,
    artifact_class_key: str | None = "artifact_class",
    extra_payload: ExtraPayload | None = None,
) -> dict[str, Any]:
    searched_paths = searched_adapter_paths(repo_root, skill_id)
    adapter_path = find_adapter(repo_root, skill_id)

    def _payload(
        *,
        found: bool,
        data: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        raw_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Every return from this function, built once. The three paths — no adapter on
        disk, an adapter the parser refused outright, and a parsed one — differ only in
        `found`, the resolved `data`, and which list carries the reason."""
        payload: dict[str, Any] = {
            "found": found,
            "valid": not errors,
            "path": str(adapter_path) if found else None,
            "data": data,
            "errors": errors,
            "warnings": warnings,
            "searched_paths": searched_paths,
        }
        _add_artifact_payload(payload, data, artifact_filename, artifact_class_key)
        if extra_payload is not None:
            # `raw_data` is the file as parsed, and three skills build `field_state` from
            # it -- the unset-vs-explicitly-empty distinction. Under a version this reader
            # cannot speak, `data` honors nothing the file declared, so handing the file
            # through here would report `configured` for a field whose value was refused:
            # the resolved payload and the state map beside it disagreeing about one
            # adapter. The containment has to reach BOTH or it reaches neither.
            contained_raw = {} if declarations_unhonored(errors) else (raw_data or {})
            payload.update(extra_payload(data, contained_raw, found))
        return normalize_adapter_result(payload, skill_id=skill_id)

    if adapter_path is None:
        return _payload(
            found=False, data=infer_defaults(repo_root), errors=[],
            warnings=list(missing_warnings),
        )

    # Report the lines the parser could not interpret (sweep row S24). All NINE skills
    # sharing this loader — release, hotl, hitl, debug, retro, impl, gather,
    # setup — used to read
    # a malformed adapter as a clean one: a missing colon on `packaging_manifest_path`
    # or on `required_release_surfaces` produced the inferred default with
    # `valid: true, errors: [], warnings: []`, which is how a typo silently disarms a
    # release surface check. Warnings rather than errors because the consumer-authored
    # adapter population is not measurable from this repository.
    try:
        raw, uninterpreted = load_yaml_file_report(adapter_path)
    except (OSError, UnicodeError, ValueError) as exc:
        # An unsupported construct (anchor, alias, an unsupported block-scalar header) used
        # to escape here as an uncaught traceback — neither a refusal nor a pass, and
        # invisible to every caller that branches on `valid`. `current_release.build_payload`
        # calls this first thing, so the S35 drift check died instead of reporting drift.
        error = read_failure_error(exc) if isinstance(exc, (OSError, UnicodeError)) else parse_failure_error(exc)
        return _payload(
            found=True, data=infer_defaults(repo_root),
            errors=[error], warnings=[],
        )
    raw_data = raw if isinstance(raw, dict) else {}
    warnings = uninterpreted_warnings(uninterpreted)
    # `load_yaml` always returns a dict, so this guard can never fire; the uninterpreted
    # report above is what actually surfaces a non-mapping document now. Kept because
    # removing it would be a behavior claim this slice has not proven for every caller.
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return _payload(
        found=True, data=data, errors=errors, warnings=warnings, raw_data=raw_data,
    )


def _add_artifact_payload(
    payload: dict[str, Any],
    data: dict[str, Any],
    artifact_filename: str | None,
    artifact_class_key: str | None,
) -> None:
    if artifact_filename is None:
        return
    payload["artifact_filename"] = artifact_filename
    if artifact_class_key and artifact_class_key in data:
        payload["artifact_class"] = data[artifact_class_key]
    payload["artifact_path"] = artifact_path(data["output_dir"], artifact_filename)
    payload["record_artifact_pattern"] = record_artifact_pattern(data["output_dir"])


def infer_simple_adapter_defaults(repo_root: Path, *, output_dir: str) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": output_dir,
    }


def validate_simple_adapter_data(
    data: dict[str, Any],
    *,
    repo_root: Path,
    output_dir: str,
    int_fields: IntFields = (),
    retired_fields: RetiredFields = (),
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_simple_adapter_defaults(repo_root, output_dir=output_dir)

    # This site already contained its siblings, by early return; it now says so with the
    # same construct the other 15 families adopted, so "which arm is the contract" is
    # readable from one name instead of inferred from a control-flow difference. The two
    # are equivalent here only because every key this function derives is already seeded
    # by `infer_simple_adapter_defaults` -- which is NOT true at the sites that had to
    # take the empty-mapping form.
    data = declared_fields_after_version_check(data, validated, errors)

    # Numeric fields are OPT-IN per skill, unlike STRING_FIELDS. Nine skills share this
    # loader; accepting a numeric field for all of them would advertise a knob that only
    # one skill's gate reads, and a repo that set it on the other eight would get a
    # clean `valid: true` for a setting nothing enforces -- the silent-typo class this
    # loader's own uninterpreted-line report exists to close.
    apply_optional_fields(data, validated, errors, string_fields=STRING_FIELDS, int_fields=int_fields)

    # An ERROR, not a warning. A warning here would let the adapter resolve `valid: true`
    # while the repo's declared bar did nothing, which is the state this check exists to
    # make impossible. Keyed on PRESENCE of the key, not on its value: a retired field set
    # to anything at all -- including the value that used to be correct -- is a statement
    # the loader can no longer honor.
    for retired, replacement, why in retired_fields:
        if retired in data:
            errors.append(
                f"`{retired}` was retired and is no longer read; use `{replacement}` instead. {why}"
            )

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")

    return validated, errors, warnings


def load_simple_adapter(
    repo_root: Path,
    *,
    skill_id: str,
    artifact_filename: str,
    default_output_dir: str,
    artifact_class: str = "history",
    missing_warnings: tuple[str, ...],
    int_fields: IntFields = (),
    retired_fields: RetiredFields = (),
) -> dict[str, Any]:
    if artifact_class not in ARTIFACT_CLASSES:
        raise ValueError(f"artifact_class must be one of: {', '.join(sorted(ARTIFACT_CLASSES))}")
    def infer_defaults(root: Path) -> dict[str, Any]:
        data = infer_simple_adapter_defaults(root, output_dir=default_output_dir)
        data["artifact_class"] = artifact_class
        return data

    def validate(data: dict[str, Any], root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
        validated, errors, warnings = validate_simple_adapter_data(
            data,
            repo_root=root,
            output_dir=default_output_dir,
            int_fields=int_fields,
            retired_fields=retired_fields,
        )
        validated["artifact_class"] = artifact_class
        if errors:
            return validated, errors, warnings
        configured_artifact_class = data.get("artifact_class")
        if isinstance(configured_artifact_class, str) and configured_artifact_class in ARTIFACT_CLASSES:
            validated["artifact_class"] = configured_artifact_class
        elif configured_artifact_class is not None:
            errors.append("artifact_class must be one of: current, history, rolling")
        return validated, errors, warnings

    return load_adapter_contract(
        repo_root,
        skill_id=skill_id,
        infer_defaults=infer_defaults,
        validate_adapter_data=validate,
        missing_warnings=missing_warnings,
        artifact_filename=artifact_filename,
    )
