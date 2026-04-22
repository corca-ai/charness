from __future__ import annotations

import re
from pathlib import Path

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
find_index = _scripts_artifact_validator_module.find_index
read_lines = _scripts_artifact_validator_module.read_lines


FORCED_RISK_CLASSES = frozenset(
    {
        "external-seam",
        "host-disproves-local",
        "repeated-symptom",
    }
)
ALLOWED_RISK_CLASSES = FORCED_RISK_CLASSES | {"operator-visible-recovery", "contract-freeze-risk", "none"}
ALLOWED_GENERALIZATION_PRESSURE = frozenset({"none", "monitor", "factor-now"})
ALLOWED_SPEC_NEXT_STEPS = frozenset({"impl", "premortem", "factor-first", "hitl"})
ALLOWED_IMPL_STATUS = frozenset({"allowed", "blocked"})
DEBUG_INTERRUPT_REQUIRED_SECTIONS = ("## Seam Risk", "## Interrupt Decision")
SPEC_PREMORTEM_HEADING_RE = re.compile(r"^#{1,2}\s+Premortem\s*$")
NEXT_HEADING_RE = re.compile(r"^#{1,2}\s+\S")


def _load_debug_adapter(repo_root: Path) -> dict[str, object] | None:
    candidates = (
        repo_root / "skills" / "public" / "debug" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "debug" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            module = load_path_module("risk_interrupt_debug_resolve_adapter", candidate)
            return module.load_adapter(repo_root)
    adapter_path = repo_root / ".agents" / "debug-adapter.yaml"
    if adapter_path.is_file():
        output_dir: str | None = None
        for raw_line in adapter_path.read_text(encoding="utf-8").splitlines():
            if raw_line.startswith("output_dir:"):
                output_dir = raw_line.split(":", 1)[1].strip()
                break
        if output_dir:
            return {"data": {"output_dir": output_dir}}
    return None


def current_debug_artifact_path(repo_root: Path) -> Path | None:
    adapter = _load_debug_adapter(repo_root)
    if adapter is None:
        return None
    data = adapter.get("data") if isinstance(adapter.get("data"), dict) else {}
    output_dir = data.get("output_dir")
    if not isinstance(output_dir, str) or not output_dir:
        return None
    return repo_root / output_dir / "latest.md"


def _section_lines(lines: list[str], heading: str, allowed_headings: tuple[str, ...]) -> list[str]:
    start = find_index(lines, heading) + 1
    end = len(lines)
    for candidate in allowed_headings:
        if candidate == heading:
            continue
        try:
            index = find_index(lines, candidate)
        except ValidationError:
            continue
        if index > start and index < end:
            end = index
    return [line.strip() for line in lines[start:end] if line.strip()]


def _extract_prefixed_values(lines: list[str], prefixes: tuple[str, ...]) -> dict[str, str]:
    values: dict[str, str] = {}
    for prefix in prefixes:
        match = next((line for line in lines if line.startswith(prefix)), None)
        if match is None:
            raise ValidationError(f"missing required line `{prefix}...`")
        value = match[len(prefix) :].strip()
        if not value:
            raise ValidationError(f"`{prefix}...` must not be empty")
        values[prefix] = value
    return values


def _parse_risk_classes(raw_value: str) -> tuple[str, ...]:
    parts = tuple(part.strip() for part in raw_value.split(",") if part.strip())
    if not parts:
        raise ValidationError("`Risk Class` must list at least one value")
    invalid = [value for value in parts if value not in ALLOWED_RISK_CLASSES]
    if invalid:
        rendered = ", ".join(f"`{value}`" for value in invalid)
        raise ValidationError(f"`Risk Class` contains unknown value(s): {rendered}")
    if "none" in parts and len(parts) > 1:
        raise ValidationError("`Risk Class: none` cannot be combined with other values")
    return parts


def parse_debug_interrupt(artifact_path: Path) -> dict[str, object]:
    lines = read_lines(artifact_path)
    missing_sections = [heading for heading in DEBUG_INTERRUPT_REQUIRED_SECTIONS if heading not in lines]
    if missing_sections:
        return {
            "present": False,
            "artifact_path": str(artifact_path),
            "reason": "debug artifact has no risk interrupt sections yet",
        }

    seam_lines = _section_lines(lines, "## Seam Risk", ("## Seam Risk", "## Interrupt Decision", "## Prevention"))
    interrupt_lines = _section_lines(
        lines,
        "## Interrupt Decision",
        ("## Seam Risk", "## Interrupt Decision", "## Prevention", "## Related Prior Incidents"),
    )
    seam_values = _extract_prefixed_values(
        seam_lines,
        (
            "- Interrupt ID: ",
            "- Risk Class: ",
            "- Seam: ",
            "- Disproving Observation: ",
            "- What Local Reasoning Cannot Prove: ",
            "- Generalization Pressure: ",
        ),
    )
    interrupt_values = _extract_prefixed_values(
        interrupt_lines,
        (
            "- Premortem Required: ",
            "- Next Step: ",
            "- Handoff Artifact: ",
        ),
    )

    risk_classes = _parse_risk_classes(seam_values["- Risk Class: "])
    generalization_pressure = seam_values["- Generalization Pressure: "]
    if generalization_pressure not in ALLOWED_GENERALIZATION_PRESSURE:
        raise ValidationError(
            "`Generalization Pressure` must be one of "
            + ", ".join(f"`{value}`" for value in sorted(ALLOWED_GENERALIZATION_PRESSURE))
        )
    premortem_required = interrupt_values["- Premortem Required: "]
    if premortem_required not in {"yes", "no"}:
        raise ValidationError("`Premortem Required` must be `yes` or `no`")
    next_step = interrupt_values["- Next Step: "]
    if next_step not in {"impl", "spec"}:
        raise ValidationError("`Next Step` must be `impl` or `spec`")

    forced = bool(set(risk_classes) & FORCED_RISK_CLASSES or generalization_pressure == "factor-now")
    if forced and premortem_required != "yes":
        raise ValidationError("forced risk interrupt must record `Premortem Required: yes`")
    if forced and next_step != "spec":
        raise ValidationError("forced risk interrupt must record `Next Step: spec`")

    handoff_artifact = interrupt_values["- Handoff Artifact: "]
    if forced:
        if handoff_artifact == "none":
            raise ValidationError("forced risk interrupt must name a spec handoff artifact")
        if not handoff_artifact.startswith("charness-artifacts/spec/") or not handoff_artifact.endswith(".md"):
            raise ValidationError("forced risk interrupt handoff must point at `charness-artifacts/spec/*.md`")

    return {
        "present": True,
        "artifact_path": str(artifact_path),
        "interrupt_id": seam_values["- Interrupt ID: "],
        "risk_classes": list(risk_classes),
        "seam": seam_values["- Seam: "],
        "disproving_observation": seam_values["- Disproving Observation: "],
        "what_local_reasoning_cannot_prove": seam_values["- What Local Reasoning Cannot Prove: "],
        "generalization_pressure": generalization_pressure,
        "premortem_required": premortem_required == "yes",
        "next_step": next_step,
        "handoff_artifact": handoff_artifact,
        "forced": forced,
    }


def _premortem_section_lines(spec_path: Path) -> list[str]:
    lines = spec_path.read_text(encoding="utf-8").splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if SPEC_PREMORTEM_HEADING_RE.match(line.strip()):
            start = index + 1
            break
    if start is None:
        raise ValidationError("spec artifact must contain a `Premortem` section")
    end = len(lines)
    for index in range(start, len(lines)):
        if NEXT_HEADING_RE.match(lines[index].strip()):
            end = index
            break
    return [line.strip() for line in lines[start:end] if line.strip()]


def parse_spec_interrupt_resolution(spec_path: Path, *, interrupt_id: str) -> dict[str, object]:
    if not spec_path.is_file():
        raise ValidationError(f"missing spec handoff artifact `{spec_path}`")
    values = _extract_prefixed_values(
        _premortem_section_lines(spec_path),
        (
            "- Interrupt Source: ",
            "- Seam Summary: ",
            "- Chosen Next Step: ",
            "- Impl Status: ",
            "- Impl Status Reason: ",
            "- What Disproving Observation Is Resolved: ",
        ),
    )
    if values["- Interrupt Source: "] != interrupt_id:
        raise ValidationError("spec handoff interrupt source does not match debug interrupt id")
    next_step = values["- Chosen Next Step: "]
    if next_step not in ALLOWED_SPEC_NEXT_STEPS:
        raise ValidationError(
            "`Chosen Next Step` must be one of "
            + ", ".join(f"`{value}`" for value in sorted(ALLOWED_SPEC_NEXT_STEPS))
        )
    impl_status = values["- Impl Status: "]
    if impl_status not in ALLOWED_IMPL_STATUS:
        raise ValidationError("`Impl Status` must be `allowed` or `blocked`")
    return {
        "spec_path": str(spec_path),
        "interrupt_source": values["- Interrupt Source: "],
        "seam_summary": values["- Seam Summary: "],
        "chosen_next_step": next_step,
        "impl_status": impl_status,
        "impl_status_reason": values["- Impl Status Reason: "],
        "resolved_observation": values["- What Disproving Observation Is Resolved: "],
    }


def plan_risk_interrupt(repo_root: Path, changed_paths: list[str] | None = None) -> dict[str, object]:
    changed = changed_paths or []
    artifact_path = current_debug_artifact_path(repo_root)
    if artifact_path is None or not artifact_path.is_file():
        return {
            "status": "not-applicable",
            "required": False,
            "reason": "no current debug artifact",
        }

    try:
        interrupt = parse_debug_interrupt(artifact_path)
    except ValidationError as exc:
        return {
            "status": "blocked",
            "required": True,
            "artifact_path": str(artifact_path.relative_to(repo_root)),
            "next_action": "repair the current debug interrupt artifact before ordinary impl continues",
            "reasons": [str(exc)],
        }
    if not interrupt.get("present"):
        return {
            "status": "not-applicable",
            "required": False,
            "reason": interrupt.get("reason", "no risk interrupt data"),
            "artifact_path": str(artifact_path.relative_to(repo_root)),
        }

    rel_artifact_path = str(artifact_path.relative_to(repo_root))
    slice_affine = not changed or rel_artifact_path in changed or str(interrupt["handoff_artifact"]) in changed
    if changed and not slice_affine:
        return {
            "status": "not-applicable",
            "required": False,
            "artifact_path": rel_artifact_path,
            "interrupt_id": interrupt["interrupt_id"],
            "risk_classes": interrupt["risk_classes"],
            "reason": "current debug interrupt was not refreshed in this slice",
        }

    forced = bool(interrupt["forced"])
    if not forced:
        return {
            "status": "not-applicable",
            "required": False,
            "artifact_path": rel_artifact_path,
            "interrupt_id": interrupt["interrupt_id"],
            "risk_classes": interrupt["risk_classes"],
            "reason": "current debug artifact does not require a forced interrupt",
        }

    handoff_artifact = str(interrupt["handoff_artifact"])
    handoff_path = repo_root / handoff_artifact
    spec_changed = handoff_artifact in changed
    try:
        resolution = parse_spec_interrupt_resolution(handoff_path, interrupt_id=str(interrupt["interrupt_id"]))
    except ValidationError as exc:
        resolution = None
        resolution_error = str(exc)
    else:
        resolution_error = None
        if resolution["seam_summary"] != interrupt["seam"]:
            resolution = None
            resolution_error = "spec handoff seam summary does not match debug seam"

    if not spec_changed or resolution is None:
        reasons: list[str] = []
        if not spec_changed:
            reasons.append("forced interrupt requires a refreshed spec handoff in the current slice")
        if resolution_error is not None:
            reasons.append(resolution_error)
        return {
            "status": "blocked",
            "required": True,
            "artifact_path": rel_artifact_path,
            "interrupt_id": interrupt["interrupt_id"],
            "risk_classes": interrupt["risk_classes"],
            "next_action": f"refresh `{handoff_artifact}` with interrupt carry-forward before ordinary impl continues",
            "handoff_artifact": handoff_artifact,
            "reasons": reasons,
        }

    return {
        "status": "handoff-recorded",
        "required": True,
        "artifact_path": rel_artifact_path,
        "interrupt_id": interrupt["interrupt_id"],
        "risk_classes": interrupt["risk_classes"],
        "handoff_artifact": handoff_artifact,
        "chosen_next_step": resolution["chosen_next_step"],
        "impl_status": resolution["impl_status"],
        "impl_status_reason": resolution["impl_status_reason"],
        "resolved_observation": resolution["resolved_observation"],
        "reasons": [
            "forced interrupt is preserved in the refreshed spec artifact"
        ],
    }
