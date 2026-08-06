"""Validate the evidence inputs used by the final-bundle preflight plan."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from runtime_bootstrap import import_repo_module

_binding = import_repo_module(__file__, "scripts.critique_reviewed_input_binding")
_packet = import_repo_module(__file__, "scripts.critique_packet_lib")

BEHAVIOR_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_PREFIX = "charness-artifacts/"


def _block(code: str, subject: str, message: str, remediation: str) -> dict[str, str]:
    return {
        "code": code,
        "subject": subject,
        "message": message,
        "remediation": remediation,
    }


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _classify_artifact(path: str) -> str:
    if "/fixtures/" in path or path.startswith("charness-artifacts/goals/fixtures/"):
        return "fixture"
    for prefix, kind in (
        ("charness-artifacts/goals/", "goal"),
        ("charness-artifacts/spec/", "spec"),
        ("charness-artifacts/critique/", "critique"),
        ("charness-artifacts/quality/", "quality"),
    ):
        if path.startswith(prefix):
            return kind
    return "other"


def artifact_inventory(repo_root: Path, changed_paths: list[str]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for relative in sorted(set(changed_paths)):
        if not relative.startswith(ARTIFACT_PREFIX):
            continue
        candidate = repo_root / relative
        row: dict[str, Any] = {
            "path": relative,
            "kind": _classify_artifact(relative),
            "exists": candidate.exists() or candidate.is_symlink(),
        }
        if candidate.is_file() and not candidate.is_symlink():
            row["sha256"] = _sha256_file(candidate)
        inventory.append(row)
    return inventory


def _strip_markup(value: str) -> str:
    return value.strip().strip("`*_ ")


def critique_inventory(
    repo_root: Path,
    paths: list[str],
    safe_relative: Callable[[str], str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    rows: list[dict[str, Any]] = []
    blockers: list[dict[str, str]] = []
    if not paths:
        blockers.append(
            _block(
                "missing_critique",
                "critique-path",
                "no durable critique artifact was supplied",
                "supply at least one reviewed Markdown critique artifact",
            )
        )
        return rows, blockers
    for relative in sorted(set(paths)):
        try:
            relative = safe_relative(relative)
        except ValueError as exc:
            blockers.append(
                _block(
                    "unsafe_critique_path",
                    relative,
                    str(exc),
                    "use a repo-relative critique path",
                )
            )
            continue
        candidate = repo_root / relative
        row: dict[str, Any] = {"path": relative, "status": "invalid"}
        if not candidate.is_file() or candidate.suffix != ".md":
            blockers.append(
                _block(
                    "invalid_critique_artifact",
                    relative,
                    "final-bundle critique input must be an existing Markdown review artifact",
                    "pass the durable `charness-artifacts/critique/*.md` review, not a prepare packet",
                )
            )
            rows.append(row)
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
            fields = _binding._binding_fields(text)
            _binding.validate_reviewed_input_binding(candidate, text, None, check_current=True)
            packet_path = _strip_markup(fields["packet path"])
            packet_sha = _strip_markup(fields["packet sha256"])
            identity_sha = _strip_markup(fields["identity sha256"])
            packet_candidate = repo_root / safe_relative(packet_path)
            packet_md = packet_candidate.with_suffix(".md")
            if not packet_candidate.is_file() or not packet_md.is_file():
                raise ValueError("bound prepare packet or its Markdown rendering is missing")
            if not SHA256_RE.fullmatch(packet_sha) or _sha256_file(packet_candidate) != packet_sha:
                raise ValueError("bound prepare packet bytes do not match the declared SHA-256")
            packet_data = json.loads(packet_candidate.read_text(encoding="utf-8"))
            identity = packet_data.get("reviewed_input_identity")
            if not isinstance(identity, dict) or identity.get("identity_sha256") != identity_sha:
                raise ValueError("bound prepare packet does not carry the declared reviewed-input identity")
            rendered = _packet.render_markdown(packet_data)
            if packet_md.read_text(encoding="utf-8") != rendered:
                raise ValueError("prepare packet Markdown is not the deterministic rendering of its JSON")
            declared_md_sha = fields.get("packet markdown sha256")
            if declared_md_sha and _strip_markup(declared_md_sha) != _sha256_file(packet_md):
                raise ValueError("critique artifact declares a stale prepare-packet Markdown SHA-256")
            row.update(
                {
                    "status": "current",
                    "packet_path": packet_path,
                    "packet_sha256": packet_sha,
                    "identity_sha256": identity_sha,
                    "reviewed_paths": list(identity.get("reviewed_paths", [])),
                }
            )
        except (
            OSError,
            KeyError,
            TypeError,
            ValueError,
            _binding.ValidationError,
            json.JSONDecodeError,
        ) as exc:
            blockers.append(
                _block(
                    "unbound_critique",
                    relative,
                    f"durable critique input is not bound to a current prepare packet: {exc}",
                    "regenerate the critique packet/review binding and rerun the preflight",
                )
            )
        else:
            row["status"] = "current"
        rows.append(row)
    return rows, blockers


def _parse_behavior(raw: str) -> tuple[dict[str, str] | None, dict[str, str] | None]:
    identifier, separator, command = raw.partition("=")
    if not separator or not BEHAVIOR_ID_RE.fullmatch(identifier):
        return None, _block(
            "invalid_behavior_channel",
            raw,
            "behavior channel must use `<lowercase-id>=<command>`",
            "use a unique id matching [a-z][a-z0-9_-]{0,63}",
        )
    if not command.strip() or any(ord(char) < 32 or ord(char) == 127 for char in command):
        return None, _block(
            "invalid_behavior_channel",
            identifier,
            "behavior command must be non-empty and contain no control characters",
            "supply one copyable single-line command",
        )
    return {"id": identifier, "command": command, "claim": "operator-declared behavior proof"}, None


def behavior_inventory(
    raw_channels: list[str], verify_commands: list[str]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    blockers: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in raw_channels:
        row, error = _parse_behavior(raw)
        if error:
            blockers.append(error)
            continue
        assert row is not None
        if row["id"] in seen:
            blockers.append(
                _block(
                    "duplicate_behavior_channel",
                    row["id"],
                    "behavior channel id is repeated",
                    "use one unique id per planned behavior command",
                )
            )
            continue
        seen.add(row["id"])
        if row["command"] in verify_commands:
            blockers.append(
                _block(
                    "behavior_is_validator",
                    row["id"],
                    "behavior channel exactly duplicates a selected surface validator",
                    "name a distinct behavior exercise or record the channel as not applicable",
                )
            )
        rows.append(row)
    if not rows and not blockers:
        blockers.append(
            _block(
                "missing_behavior_channel",
                "behavior-channel",
                "no behavior proof channel was named",
                "supply at least one explicit behavior channel command",
            )
        )
    return rows, blockers
