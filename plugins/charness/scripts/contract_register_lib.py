"""Validate the proposal-only register for always-loaded contract units."""

from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

from scripts.lesson_ledger_lib import lesson_ledger_path, validate_lesson_ledger
from scripts.recent_lessons_lib import retro_artifact_paths

REGISTER_FILENAME = "contract-register.json"
KIND = "charness.contract-register"
SCHEMA_VERSION = 1
UNIT_PATHS = (
    "AGENTS.md",
    "docs/conventions/implementation-discipline.md",
    "docs/conventions/operating-contract.md",
)
TOP_LEVEL_KEYS = {"kind", "schema_version", "unit_budget", "units", "citation_events", "catch_events", "graduation_proposals"}
UNIT_KEYS = {"unit_id", "path", "heading"}
CITATION_KEYS = {"event_id", "source_retro", "unit_id", "anchor"}
PROPOSAL_KEYS = {"proposal_id", "lesson_id", "source_retro", "target_path", "target_heading", "proposed_unit_id", "rationale", "displacement_unit_ids"}


def contract_register_path(output_dir: Path) -> Path:
    return output_dir / REGISTER_FILENAME


def _fail(message: str) -> None:
    raise ValueError(f"contract register invalid: {message}")


def heading_slug(heading: str) -> str:
    value = unicodedata.normalize("NFKC", heading).strip().lower()
    value = re.sub(r"[\W_]+", "-", value, flags=re.UNICODE).strip("-")
    if not value:
        _fail("contract heading normalizes to an empty slug")
    return value


def unit_id(path: str, heading: str) -> str:
    return f"{path}#{heading_slug(heading)}"


def _unfenced_h2s(path: Path) -> list[str]:
    fence_character: str | None = None
    fence_length = 0
    headings: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if fence_character is not None:
            if re.match(rf"^[ ]{{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*$", line):
                fence_character = None
                fence_length = 0
            continue
        fence_match = re.match(r"^[ ]{0,3}(`{3,}|~{3,})", line)
        if fence_match:
            fence_character = fence_match.group(1)[0]
            fence_length = len(fence_match.group(1))
            continue
        match = re.match(r"^[ ]{0,3}##[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$", line)
        if match:
            headings.append(match.group(1).strip())
    return headings


def build_contract_units(repo_root: Path) -> list[dict[str, str]]:
    units: list[dict[str, str]] = []
    seen: set[str] = set()
    for relative in UNIT_PATHS:
        path = repo_root / relative
        if not path.is_file():
            _fail(f"missing contract source `{relative}`")
        for heading in _unfenced_h2s(path):
            identifier = unit_id(relative, heading)
            if identifier in seen:
                _fail(f"contract path `{relative}` has colliding H2 identity `{identifier}`")
            seen.add(identifier)
            units.append({"unit_id": identifier, "path": relative, "heading": heading})
    return sorted(units, key=lambda item: item["unit_id"])


def initial_contract_register(repo_root: Path) -> dict[str, Any]:
    units = build_contract_units(repo_root)
    return {"kind": KIND, "schema_version": SCHEMA_VERSION, "unit_budget": len(units), "units": units, "citation_events": [], "catch_events": [], "graduation_proposals": []}


def _committed_state(repo_root: Path, path: Path) -> dict[str, Any] | None:
    result = subprocess.run(["git", "show", f"HEAD:{path.relative_to(repo_root)}"], cwd=repo_root, text=True, capture_output=True, check=False)
    if result.returncode:
        return None
    try:
        previous = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        _fail(f"committed register is invalid JSON: {exc.msg}")
    if not isinstance(previous, dict) or previous.get("kind") != KIND or previous.get("schema_version") != SCHEMA_VERSION:
        _fail("committed register has an unsupported shape")
    required = ("unit_budget", "units", "citation_events", "catch_events", "graduation_proposals")
    if any(key not in previous for key in required):
        _fail("committed register has invalid append-only streams")
    return previous


def _validate_citations(events: list[Any], unit_ids: set[str], repo_root: Path) -> None:
    output_dir = repo_root / "charness-artifacts/retro"
    summary_path = output_dir / "recent-lessons.md"
    session_retros = {path.resolve() for path in retro_artifact_paths(output_dir, summary_path)}
    event_ids: set[str] = set()
    cited: set[tuple[str, str]] = set()
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict) or set(event) != CITATION_KEYS:
            _fail(f"citation event {index} has unexpected or missing fields")
        event_id, source, identifier, anchor = (event.get(key) for key in ("event_id", "source_retro", "unit_id", "anchor"))
        if not all(isinstance(value, str) and value for value in (event_id, source, identifier, anchor)):
            _fail(f"citation event {index} needs non-empty string fields")
        if event_id in event_ids:
            _fail(f"duplicate citation event_id `{event_id}`")
        if identifier not in unit_ids:
            _fail(f"citation event `{event_id}` names unknown active unit `{identifier}`")
        source_path = repo_root / source
        try:
            canonical_source = source_path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            canonical_source = ""
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


def _validate_proposals(proposals: list[Any], unit_ids: set[str], budget: int, repo_root: Path, output_dir: Path, summary_path: Path) -> None:
    lessons: dict[str, Any] = {}
    if proposals:
        validate_lesson_ledger(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
        ledger = json.loads(lesson_ledger_path(output_dir).read_text(encoding="utf-8"))
        lessons = ledger["lessons"]
    proposal_ids: set[str] = set()
    proposed_unit_ids: set[str] = set()
    for index, proposal in enumerate(proposals, start=1):
        if not isinstance(proposal, dict) or set(proposal) != PROPOSAL_KEYS:
            _fail(f"graduation proposal {index} has unexpected or missing fields")
        values = {key: proposal.get(key) for key in PROPOSAL_KEYS}
        if not all(isinstance(values[key], str) and values[key] for key in PROPOSAL_KEYS - {"displacement_unit_ids"}):
            _fail(f"graduation proposal {index} needs non-empty string fields")
        proposal_id = values["proposal_id"]
        if proposal_id in proposal_ids:
            _fail(f"duplicate graduation proposal_id `{proposal_id}`")
        lesson = lessons.get(values["lesson_id"])
        if not isinstance(lesson, dict) or lesson.get("source_retro") != values["source_retro"]:
            _fail(f"graduation proposal `{proposal_id}` does not cite its seeded lesson source retro")
        target_path = values["target_path"]
        if target_path not in UNIT_PATHS or values["proposed_unit_id"] != unit_id(target_path, values["target_heading"]):
            _fail(f"graduation proposal `{proposal_id}` has a non-canonical target unit")
        if values["proposed_unit_id"] in unit_ids:
            _fail(f"graduation proposal `{proposal_id}` proposed unit already exists")
        if values["proposed_unit_id"] in proposed_unit_ids:
            _fail(f"duplicate proposed unit ID `{values['proposed_unit_id']}`")
        displacements = values["displacement_unit_ids"]
        if not isinstance(displacements, list) or any(not isinstance(item, str) or not item for item in displacements):
            _fail(f"graduation proposal `{proposal_id}` displacement_unit_ids must be a string list")
        if len(set(displacements)) != len(displacements) or any(item not in unit_ids for item in displacements):
            _fail(f"graduation proposal `{proposal_id}` has invalid displacement units")
        if len(unit_ids) + 1 - len(displacements) > budget:
            _fail(f"graduation proposal `{proposal_id}` exceeds the fixed unit budget without enough displacement")
        proposal_ids.add(proposal_id)
        proposed_unit_ids.add(values["proposed_unit_id"])


def validate_contract_register(*, repo_root: Path, output_dir: Path, summary_path: Path) -> dict[str, Any]:
    path = contract_register_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing contract register `{path.relative_to(repo_root)}`")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"invalid JSON: {exc.msg}")
    if not isinstance(payload, dict) or payload.get("kind") != KIND or payload.get("schema_version") != SCHEMA_VERSION or set(payload) != TOP_LEVEL_KEYS:
        _fail(f"expected strict `{KIND}` schema version {SCHEMA_VERSION}")
    units, citations, catches, proposals, budget = (payload.get(key) for key in ("units", "citation_events", "catch_events", "graduation_proposals", "unit_budget"))
    if not isinstance(units, list) or not isinstance(citations, list) or not isinstance(catches, list) or not isinstance(proposals, list) or type(budget) is not int:
        _fail("register state has invalid container or budget types")
    expected_units = build_contract_units(repo_root)
    if units != expected_units or budget != len(expected_units):
        _fail("materialized active units or fixed initial budget do not equal the current pre-mutation rebuild")
    if catches:
        _fail("catch_events must remain empty until a declared gate-to-unit mapping exists")
    unit_ids = {unit["unit_id"] for unit in units}
    _validate_citations(citations, unit_ids, repo_root)
    _validate_proposals(proposals, unit_ids, budget, repo_root, output_dir, summary_path)
    committed = _committed_state(repo_root, path)
    if committed is not None:
        if not isinstance(committed["catch_events"], list) or committed["catch_events"]:
            _fail("committed register has an unsupported non-empty catch stream")
        if units != committed["units"] or budget != committed["unit_budget"]:
            _fail("committed active units or fixed unit budget were rewritten")
        old_citations = committed["citation_events"]
        old_proposals = committed["graduation_proposals"]
        if citations[: len(old_citations)] != old_citations or proposals[: len(old_proposals)] != old_proposals:
            _fail("committed citation events or graduation proposals were rewritten or removed")
    return {"unit_count": len(units), "citation_event_count": len(citations), "graduation_proposal_count": len(proposals), "path": str(path.relative_to(repo_root))}
