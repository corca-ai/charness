"""Validate replayed contract membership, proposals, and retention evidence."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.contract_unit_inventory_lib import (
    UNIT_PATHS,
    build_contract_units,
    unit_id,
)
from scripts.contract_unit_inventory_lib import (
    heading_slug as heading_slug,
)
from scripts.lesson_ledger_lib import lesson_ledger_path, validate_lesson_ledger
from scripts.recent_lessons_lib import retro_artifact_paths

REGISTER_FILENAME = "contract-register.json"
KIND = "charness.contract-register"
SCHEMA_VERSION = 2
TOP_LEVEL_KEYS = {
    "kind",
    "schema_version",
    "unit_budget",
    "seed_units",
    "units",
    "retired_units",
    "citation_events",
    "catch_events",
    "graduation_proposals",
    "applied_transitions",
}
UNIT_KEYS = {"unit_id", "path", "heading"}
RETIRED_UNIT_KEYS = UNIT_KEYS | {
    "retired_by",
    "successor_unit_ids",
    "disposition",
}
CITATION_KEYS = {"event_id", "source_retro", "unit_id", "anchor"}
PROPOSAL_KEYS = {
    "proposal_id",
    "lesson_id",
    "source_retro",
    "evidence_session_ids",
    "target_path",
    "target_heading",
    "proposed_unit_id",
    "rationale",
    "displacement_unit_ids",
}
TRANSITION_COMMON_KEYS = {"sequence", "event_id", "action", "approval_ref", "rationale"}
GRADUATION_TRANSITION_KEYS = TRANSITION_COMMON_KEYS | {"proposal_id"}
RETIREMENT_TRANSITION_KEYS = TRANSITION_COMMON_KEYS | {
    "retired_unit_ids",
    "successor_unit_ids",
    "disposition",
}
NO_BINDING_BEHAVIOR = "no-remaining-binding-behavior"


def contract_register_path(output_dir: Path) -> Path:
    return output_dir / REGISTER_FILENAME


def _fail(message: str) -> None:
    raise ValueError(f"contract register invalid: {message}")


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def initial_contract_register(repo_root: Path) -> dict[str, Any]:
    units = build_contract_units(repo_root)
    return {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "unit_budget": len(units),
        "seed_units": units,
        "units": units,
        "retired_units": [],
        "citation_events": [],
        "catch_events": [],
        "graduation_proposals": [],
        "applied_transitions": [],
    }


def _committed_state(repo_root: Path, path: Path) -> dict[str, Any] | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{path.relative_to(repo_root)}"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        return None
    try:
        previous = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        _fail(f"committed register is invalid JSON: {exc.msg}")
    if not isinstance(previous, dict) or previous.get("kind") != KIND:
        _fail("committed register has an unsupported shape")
    if previous.get("schema_version") != SCHEMA_VERSION or not TOP_LEVEL_KEYS <= set(previous):
        _fail("committed register has an unsupported shape")
    return previous


def _canonical_markdown_ref(repo_root: Path, value: Any) -> bool:
    if not _nonblank(value):
        return False
    path = repo_root / value
    try:
        canonical = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return False
    return value == canonical and path.suffix == ".md" and path.is_file()


def _validate_units(units: Any, label: str) -> list[dict[str, str]]:
    if not isinstance(units, list) or any(
        not isinstance(unit, dict)
        or set(unit) != UNIT_KEYS
        or not all(_nonblank(unit.get(key)) for key in UNIT_KEYS)
        or unit["unit_id"] != unit_id(unit["path"], unit["heading"])
        for unit in units
    ):
        _fail(f"{label} has invalid unit shapes")
    identifiers = [unit["unit_id"] for unit in units]
    if identifiers != sorted(identifiers) or len(identifiers) != len(set(identifiers)):
        _fail(f"{label} must be lexically sorted with unique identities")
    return units


def _lesson_evidence(
    repo_root: Path, output_dir: Path, summary_path: Path
) -> tuple[dict[str, Any], dict[str, set[str]], set[tuple[str, str]]]:
    validate_lesson_ledger(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    ledger = json.loads(lesson_ledger_path(output_dir).read_text(encoding="utf-8"))
    sessions = {
        event["session_id"]: set(event["snapshot"]["lesson_ids"])
        for event in ledger["session_events"]
    }
    scored = {
        (event.get("session_id"), event["lesson_id"])
        for event in ledger["score_events"]
        if _nonblank(event.get("session_id"))
    }
    return ledger["lessons"], sessions, scored


def _validate_proposals(
    proposals: list[Any],
    historical_ids: set[str],
    repo_root: Path,
    output_dir: Path,
    summary_path: Path,
) -> dict[str, dict[str, Any]]:
    lessons: dict[str, Any] = {}
    sessions: dict[str, set[str]] = {}
    scored: set[tuple[str, str]] = set()
    if proposals:
        lessons, sessions, scored = _lesson_evidence(repo_root, output_dir, summary_path)
    proposal_map: dict[str, dict[str, Any]] = {}
    proposed_ids: set[str] = set()
    for index, proposal in enumerate(proposals, start=1):
        if not isinstance(proposal, dict) or set(proposal) != PROPOSAL_KEYS:
            _fail(f"graduation proposal {index} has unexpected or missing fields")
        scalar_keys = PROPOSAL_KEYS - {"displacement_unit_ids", "evidence_session_ids"}
        if not all(_nonblank(proposal.get(key)) for key in scalar_keys):
            _fail(f"graduation proposal {index} needs non-empty string fields")
        proposal_id = proposal["proposal_id"]
        if proposal_id in proposal_map:
            _fail(f"duplicate graduation proposal_id `{proposal_id}`")
        lesson = lessons.get(proposal["lesson_id"])
        if not isinstance(lesson, dict) or lesson.get("source_retro") != proposal["source_retro"]:
            _fail(f"graduation proposal `{proposal_id}` does not cite its seeded lesson source")
        evidence = proposal["evidence_session_ids"]
        if (
            not isinstance(evidence, list)
            or len(evidence) < 2
            or len(evidence) != len(set(evidence))
            or any(not _nonblank(item) for item in evidence)
            or any(
                proposal["lesson_id"] not in sessions.get(session_id, set())
                or (session_id, proposal["lesson_id"]) not in scored
                for session_id in evidence
            )
        ):
            _fail(f"graduation proposal `{proposal_id}` needs two scored evidence sessions")
        target_path = proposal["target_path"]
        if (
            target_path not in UNIT_PATHS
            or proposal["proposed_unit_id"] != unit_id(target_path, proposal["target_heading"])
        ):
            _fail(f"graduation proposal `{proposal_id}` has a non-canonical target unit")
        if proposal["proposed_unit_id"] in historical_ids | proposed_ids:
            _fail(f"graduation proposal `{proposal_id}` reuses a contract unit identity")
        displacements = proposal["displacement_unit_ids"]
        if (
            not isinstance(displacements, list)
            or len(displacements) != len(set(displacements))
            or any(
                not _nonblank(item) or item not in historical_ids | proposed_ids
                for item in displacements
            )
        ):
            _fail(f"graduation proposal `{proposal_id}` has invalid displacement units")
        proposal_map[proposal_id] = proposal
        proposed_ids.add(proposal["proposed_unit_id"])
    return proposal_map


def _retired_projection(
    unit: dict[str, str],
    *,
    event_id: str,
    successors: list[str],
    disposition: str,
) -> dict[str, Any]:
    return {
        **unit,
        "retired_by": event_id,
        "successor_unit_ids": successors,
        "disposition": disposition,
    }


def _apply_graduation(
    event: dict[str, Any],
    active: dict[str, dict[str, str]],
    retired: dict[str, dict[str, Any]],
    proposals: dict[str, dict[str, Any]],
    applied_proposals: set[str],
) -> str:
    event_id = event["event_id"]
    if set(event) != GRADUATION_TRANSITION_KEYS:
        _fail(f"applied graduation `{event_id}` has unexpected or missing fields")
    proposal_id = event.get("proposal_id")
    proposal = proposals.get(proposal_id)
    if proposal is None or proposal_id in applied_proposals:
        _fail(f"applied graduation `{event_id}` names unavailable proposal")
    displacements = proposal["displacement_unit_ids"]
    if any(identifier not in active for identifier in displacements):
        _fail(f"applied graduation `{event_id}` names inactive displacement")
    successor = proposal["proposed_unit_id"]
    if successor in active or successor in retired:
        _fail(f"applied graduation `{event_id}` reuses membership identity")
    for identifier in displacements:
        retired[identifier] = _retired_projection(
            active.pop(identifier),
            event_id=event_id,
            successors=[successor],
            disposition="replaced-by-graduation",
        )
    active[successor] = {
        "unit_id": successor,
        "path": proposal["target_path"],
        "heading": proposal["target_heading"],
    }
    return proposal_id


def _apply_retirement(
    event: dict[str, Any],
    active: dict[str, dict[str, str]],
    retired: dict[str, dict[str, Any]],
) -> None:
    event_id = event["event_id"]
    if set(event) != RETIREMENT_TRANSITION_KEYS:
        _fail(f"retirement `{event_id}` has unexpected or missing fields")
    unit_ids = event.get("retired_unit_ids")
    successors = event.get("successor_unit_ids")
    disposition = event.get("disposition")
    if (
        not isinstance(unit_ids, list)
        or not unit_ids
        or len(unit_ids) != len(set(unit_ids))
        or any(identifier not in active for identifier in unit_ids)
        or not isinstance(successors, list)
        or len(successors) != len(set(successors))
        or any(identifier not in active or identifier in unit_ids for identifier in successors)
        or (successors and disposition != "successor-units")
        or (not successors and disposition != NO_BINDING_BEHAVIOR)
    ):
        _fail(f"retirement `{event_id}` has invalid units or disposition")
    for identifier in unit_ids:
        retired[identifier] = _retired_projection(
            active.pop(identifier),
            event_id=event_id,
            successors=successors,
            disposition=disposition,
        )


def _replay_membership(
    seed_units: list[dict[str, str]],
    events: list[Any],
    proposals: dict[str, dict[str, Any]],
    *,
    budget: int,
    repo_root: Path,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], set[str]]:
    active = {unit["unit_id"]: unit for unit in seed_units}
    retired: dict[str, dict[str, Any]] = {}
    event_ids: set[str] = set()
    applied_proposals: set[str] = set()
    for sequence, event in enumerate(events, start=1):
        if not isinstance(event, dict) or type(event.get("sequence")) is not int:
            _fail(f"applied transition {sequence} has invalid shape")
        if event["sequence"] != sequence:
            _fail("applied transition sequences must start at 1 and be contiguous")
        event_id, action = event.get("event_id"), event.get("action")
        if (
            not _nonblank(event_id)
            or event_id in event_ids
            or not _nonblank(event.get("rationale"))
            or not _canonical_markdown_ref(repo_root, event.get("approval_ref"))
        ):
            _fail(f"applied transition {sequence} needs unique identity and reviewed approval")
        if action == "apply-graduation":
            applied_proposals.add(
                _apply_graduation(event, active, retired, proposals, applied_proposals)
            )
        elif action == "retire":
            _apply_retirement(event, active, retired)
        else:
            _fail(f"applied transition `{event_id}` has unknown action")
        if len(active) > budget:
            _fail(f"applied transition `{event_id}` exceeds fixed unit budget")
        event_ids.add(event_id)
    return (
        sorted(active.values(), key=lambda item: item["unit_id"]),
        sorted(retired.values(), key=lambda item: item["unit_id"]),
        applied_proposals,
    )


def _validate_citations(events: list[Any], historical_ids: set[str], repo_root: Path) -> None:
    output_dir = repo_root / "charness-artifacts/retro"
    summary_path = output_dir / "recent-lessons.md"
    session_retros = {path.resolve() for path in retro_artifact_paths(output_dir, summary_path)}
    event_ids: set[str] = set()
    cited: set[tuple[str, str]] = set()
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict) or set(event) != CITATION_KEYS:
            _fail(f"citation event {index} has unexpected or missing fields")
        event_id, source, identifier, anchor = (
            event.get(key) for key in ("event_id", "source_retro", "unit_id", "anchor")
        )
        if not all(_nonblank(value) for value in (event_id, source, identifier, anchor)):
            _fail(f"citation event {index} needs non-empty string fields")
        source_path = repo_root / source
        try:
            canonical_source = source_path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            canonical_source = ""
        if event_id in event_ids or identifier not in historical_ids:
            _fail(f"citation event `{event_id}` has duplicate identity or unknown unit")
        if (
            source != canonical_source
            or not source.startswith("charness-artifacts/retro/")
            or source_path.suffix != ".md"
            or not source_path.is_file()
            or source_path.resolve() not in session_retros
        ):
            _fail(f"citation event `{event_id}` source_retro is not an existing repo retro")
        key = (source, identifier)
        if key in cited:
            _fail(f"duplicate citation for unit `{identifier}` from `{source}`")
        event_ids.add(event_id)
        cited.add(key)


def replay_validated_contract_register_payload(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path,
    path: Path,
    payload: Any,
    require_live_match: bool = True,
) -> dict[str, Any]:
    if (
        not isinstance(payload, dict)
        or payload.get("kind") != KIND
        or payload.get("schema_version") != SCHEMA_VERSION
        or set(payload) != TOP_LEVEL_KEYS
    ):
        _fail(f"expected strict `{KIND}` schema version {SCHEMA_VERSION}")
    seed_units = _validate_units(payload["seed_units"], "seed_units")
    units = _validate_units(payload["units"], "units")
    retired_units = payload["retired_units"]
    budget = payload["unit_budget"]
    citations = payload["citation_events"]
    catches = payload["catch_events"]
    proposals = payload["graduation_proposals"]
    transitions = payload["applied_transitions"]
    if (
        type(budget) is not int
        or budget != len(seed_units)
        or not all(isinstance(value, list) for value in (retired_units, citations, catches, proposals, transitions))
    ):
        _fail("register state has invalid container or fixed budget")
    if catches:
        _fail("catch_events must remain empty until a declared gate-to-unit mapping exists")
    historical_ids = {unit["unit_id"] for unit in seed_units}
    proposal_map = _validate_proposals(
        proposals, historical_ids, repo_root, output_dir, summary_path
    )
    expected_units, expected_retired, applied_proposals = _replay_membership(
        seed_units, transitions, proposal_map, budget=budget, repo_root=repo_root
    )
    if units != expected_units or retired_units != expected_retired:
        _fail("materialized units or retired_units do not equal deterministic replay")
    if any(not isinstance(item, dict) or set(item) != RETIRED_UNIT_KEYS for item in retired_units):
        _fail("retired_units has invalid projection shape")
    if require_live_match and build_contract_units(repo_root) != units:
        _fail("live contract H2 inventory does not equal replayed active units")
    active_ids = {unit["unit_id"] for unit in units}
    for proposal_id, proposal in proposal_map.items():
        if proposal_id in applied_proposals:
            continue
        displacements = proposal["displacement_unit_ids"]
        if any(identifier not in active_ids for identifier in displacements):
            _fail(f"graduation proposal `{proposal_id}` names inactive displacement")
        if len(active_ids) + 1 - len(displacements) > budget:
            _fail(f"graduation proposal `{proposal_id}` exceeds the fixed unit budget")
    historical_ids |= {unit["unit_id"] for unit in retired_units} | {
        unit["unit_id"] for unit in units
    }
    _validate_citations(citations, historical_ids, repo_root)
    committed = _committed_state(repo_root, path)
    if committed is not None:
        if seed_units != committed["seed_units"] or budget != committed["unit_budget"]:
            _fail("committed seed units or fixed unit budget were rewritten")
        for key, label in (
            ("citation_events", "citation events"),
            ("catch_events", "catch events"),
            ("graduation_proposals", "graduation proposals"),
            ("applied_transitions", "applied transitions"),
        ):
            old = committed[key]
            if payload[key][: len(old)] != old:
                _fail(f"committed {label} were rewritten or removed")
    return {
        "units": units,
        "retired_units": retired_units,
        "proposal_map": proposal_map,
        "applied_proposal_ids": applied_proposals,
        "unit_count": len(units),
        "retired_unit_count": len(retired_units),
        "citation_event_count": len(citations),
        "graduation_proposal_count": len(proposals),
        "applied_transition_count": len(transitions),
    }


def validate_contract_register(
    *, repo_root: Path, output_dir: Path, summary_path: Path
) -> dict[str, Any]:
    path = contract_register_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing contract register `{path.relative_to(repo_root)}`")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"invalid JSON: {exc.msg}")
    result = replay_validated_contract_register_payload(
        repo_root=repo_root,
        output_dir=output_dir,
        summary_path=summary_path,
        path=path,
        payload=payload,
    )
    return {**{key: value for key, value in result.items() if key.endswith("_count")}, "path": str(path.relative_to(repo_root))}
