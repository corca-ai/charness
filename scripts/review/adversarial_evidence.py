"""Validate the conditional evidence-led review record shared by critique/debug."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

DISPOSITIONS = frozenset({"reproduced", "disconfirmed", "unproven", "not-applicable"})
PROOFS = frozenset(
    {"static scan only", "local payload proof", "executable fixture", "runtime/provider roundtrip"}
)
REQUIRED_RECORD_FIELDS = (
    "finding",
    "source",
    "expected",
    "stimulus",
    "disposition",
    "observed",
    "proof",
    "handoff",
    "next move",
    "receipt",
    "receipt sha256",
)
PLACEHOLDERS = frozenset({"", "todo", "tbd", "missing", "n/a", "na"})
REPORT_IDENTITY_RE = re.compile(r"^[^:\s|]+:[^|#\s]+#sha256:[0-9a-f]{64}$")
EVIDENCE_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SOURCE_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDER_MARKER_RE = re.compile(r"(?i)(?:\b(?:todo|tbd)\b|<[^>\n]+>)")
RECEIPT_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RECEIPT_SCHEMA = "charness.adversarial-evidence.receipt.v1"


class EvidenceValidationError(ValueError):
    """A conditional evidence-led section is malformed."""


def _section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == heading) + 1
    except StopIteration:
        return []
    end = next(
        (i for i in range(start, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return lines[start:end]


def _field_value(lines: list[str], name: str) -> str | None:
    prefix = f"- {name}:"
    for line in lines:
        if line.strip().lower().startswith(prefix.lower()):
            return line.split(":", 1)[1].strip()
    return None


def _non_placeholder(value: str | None) -> bool:
    return (
        value is not None
        and value.strip().lower() not in PLACEHOLDERS
        and not PLACEHOLDER_MARKER_RE.search(value)
    )


def _ids(value: str) -> set[str]:
    if value is None or value.strip().lower() in {"none", "n/a", "na", "-"}:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def _record(line: str) -> dict[str, str]:
    if not line.strip().startswith("- Finding:"):
        return {}
    values: dict[str, str] = {}
    for item in line.strip()[2:].split("|"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        values[key.strip().lower()] = value.strip()
    return values


def _receipt_candidate(
    repo_root: Path, receipt_path: str, receipt_sha256: str, *, artifact_label: str, index: int
) -> Path:
    receipt = Path(receipt_path)
    if receipt.is_absolute() or ".." in receipt.parts or not receipt_path:
        raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt must be repo-relative")
    if not RECEIPT_SHA256_RE.fullmatch(receipt_sha256):
        raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt sha256 is invalid")
    candidate = (repo_root / receipt_path).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt escapes repo root") from exc
    if not candidate.is_file():
        raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt does not exist: {receipt_path}")
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != receipt_sha256:
        raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt sha256 is stale or tampered")
    return candidate


def _validate_receipt_payload(
    candidate: Path, record: dict[str, str], *, artifact_label: str, index: int
) -> None:
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt is not valid JSON") from exc
    if not isinstance(payload, dict) or payload.get("schema") != RECEIPT_SCHEMA:
        raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt schema is invalid")
    for field in ("finding", "source", "expected", "stimulus", "disposition", "observed"):
        if payload.get(field) != record[field]:
            raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt does not bind {field}")
    for field in ("command", "fixture", "final_consumer"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt is missing {field}")
    if payload.get("executed") is not True or payload.get("final_consumer_observed") is not True:
        raise EvidenceValidationError(
            f"{artifact_label}: finding record {index} receipt must assert executed final-consumer observation"
        )
    if not isinstance(payload.get("returncode"), int):
        raise EvidenceValidationError(f"{artifact_label}: finding record {index} receipt returncode must be an integer")


def _validate_receipt(
    record: dict[str, str],
    *,
    repo_root: Path | None,
    artifact_label: str,
    index: int,
) -> None:
    disposition = record["disposition"].lower()
    receipt_path = record["receipt"].strip()
    receipt_sha256 = record["receipt sha256"].strip().lower()
    if disposition in {"unproven", "not-applicable"}:
        if receipt_path.lower() not in {"none", "n/a", "na"} or receipt_sha256 not in {"none", "n/a", "na"}:
            raise EvidenceValidationError(
                f"{artifact_label}: finding record {index} non-claim must use receipt: none and receipt sha256: none"
            )
        return
    if record["proof"].lower() not in {"executable fixture", "runtime/provider roundtrip"}:
        raise EvidenceValidationError(
            f"{artifact_label}: {disposition} finding needs executable fixture or runtime/provider roundtrip proof"
        )
    if repo_root is None:
        if receipt_path.lower() in {"none", "n/a", "na"} or not RECEIPT_SHA256_RE.fullmatch(receipt_sha256):
            raise EvidenceValidationError(f"{artifact_label}: {disposition} finding needs a receipt path and sha256")
        return
    _validate_receipt_payload(
        _receipt_candidate(repo_root, receipt_path, receipt_sha256, artifact_label=artifact_label, index=index),
        record,
        artifact_label=artifact_label,
        index=index,
    )


def _external_source(source: str) -> bool:
    normalized = source.strip().lower()
    return "://" in normalized or normalized.startswith(("http:", "https:", "external:")) or normalized.split("/", 1)[0] in {"external", "url"}


def _metadata(text: str, artifact_label: str) -> tuple[int, dict[str, str | None]]:
    values = {
        name: _field_value(_section(text, "## Evidence Disposition"), name)
        for name in (
            "Report Identity",
            "Reported Findings",
            "Dispositioned Findings",
            "Missing Findings",
            "Evidence Digest",
            "Report Source",
            "Report Source SHA256",
        )
    }
    missing = [
        name
        for name, value in values.items()
        if value is None or (name != "Missing Findings" and not _non_placeholder(value))
    ]
    if missing:
        raise EvidenceValidationError(f"{artifact_label}: evidence disposition is missing {', '.join(missing)}")
    report_identity = values["Report Identity"] or ""
    if not REPORT_IDENTITY_RE.fullmatch(report_identity):
        raise EvidenceValidationError(
            f"{artifact_label}: `Report Identity` must be `<source>:<id>#sha256:<64 lowercase hex>`"
        )
    evidence_digest = values["Evidence Digest"] or ""
    if not EVIDENCE_DIGEST_RE.fullmatch(evidence_digest):
        raise EvidenceValidationError(
            f"{artifact_label}: `Evidence Digest` must be `sha256:<64 lowercase hex>`"
        )
    source_path = values["Report Source"] or ""
    source_sha256 = values["Report Source SHA256"] or ""
    if not SOURCE_SHA256_RE.fullmatch(source_sha256):
        raise EvidenceValidationError(
            f"{artifact_label}: `Report Source SHA256` must be 64 lowercase hex characters"
        )
    identity_sha256 = report_identity.rsplit("#sha256:", 1)[1]
    if identity_sha256 != source_sha256:
        raise EvidenceValidationError(
            f"{artifact_label}: Report Identity SHA256 must equal Report Source SHA256"
        )
    if not source_path or Path(source_path).is_absolute() or ".." in Path(source_path).parts:
        raise EvidenceValidationError(
            f"{artifact_label}: `Report Source` must be a repo-relative path without `..`"
        )
    try:
        count = int(values["Reported Findings"] or "")
    except ValueError as exc:
        raise EvidenceValidationError(f"{artifact_label}: `Reported Findings` must be a non-negative integer") from exc
    if count < 0:
        raise EvidenceValidationError(f"{artifact_label}: `Reported Findings` cannot be negative")
    return count, values


def _records(
    text: str,
    artifact_label: str,
    expected_count: int,
    *,
    repo_root: Path | None,
) -> tuple[list[str], str, list[str]]:
    record_lines = [line.strip() for line in _section(text, "## Adversarial Verification") if _record(line)]
    records = [_record(line) for line in record_lines]
    if len(records) != expected_count:
        raise EvidenceValidationError(
            f"{artifact_label}: reported finding count {expected_count} does not match typed records {len(records)}"
        )
    ids: list[str] = []
    dispositions: list[str] = []
    for index, record in enumerate(records, 1):
        missing = [field for field in REQUIRED_RECORD_FIELDS if not _non_placeholder(record.get(field))]
        if missing:
            raise EvidenceValidationError(f"{artifact_label}: finding record {index} is missing {', '.join(missing)}")
        disposition, proof = record["disposition"].lower(), record["proof"].lower()
        if disposition not in DISPOSITIONS:
            raise EvidenceValidationError(f"{artifact_label}: unknown disposition `{disposition}`")
        if proof not in PROOFS:
            raise EvidenceValidationError(f"{artifact_label}: unknown proof `{proof}`")
        if disposition in {"reproduced", "disconfirmed"} and proof == "static scan only":
            raise EvidenceValidationError(
                f"{artifact_label}: {disposition} finding cannot use static scan only proof"
            )
        if disposition == "reproduced":
            if record["handoff"].strip().lower() in {"none", "n/a", "na"}:
                raise EvidenceValidationError(f"{artifact_label}: reproduced finding needs a debug handoff")
            if record["next move"].strip().lower() in {"none", "n/a", "na"}:
                raise EvidenceValidationError(f"{artifact_label}: reproduced finding needs a named next move")
        _validate_receipt(record, repo_root=repo_root, artifact_label=artifact_label, index=index)
        ids.append(record["finding"])
        dispositions.append(disposition)
    if len(set(ids)) != len(ids):
        raise EvidenceValidationError(f"{artifact_label}: finding IDs must be unique")
    digest = hashlib.sha256("\n".join(record_lines).encode("utf-8")).hexdigest()
    return ids, f"sha256:{digest}", dispositions


def _validate_coverage(values: dict[str, str | None], ids: list[str], count: int, artifact_label: str) -> None:
    dispositioned, missing = _ids(values["Dispositioned Findings"]), _ids(values["Missing Findings"])
    if dispositioned != set(ids):
        raise EvidenceValidationError(f"{artifact_label}: dispositioned IDs must equal typed record IDs")
    if missing & dispositioned:
        raise EvidenceValidationError(f"{artifact_label}: a finding cannot be both dispositioned and missing")
    if len(dispositioned | missing) != count:
        raise EvidenceValidationError(f"{artifact_label}: dispositioned plus missing IDs must cover the reported count")


def _validate_source_binding(
    values: dict[str, str | None],
    *,
    dispositions: list[str],
    repo_root: Path | None,
    artifact_label: str,
) -> None:
    if _external_source(values["Report Source"] or ""):
        if any(disposition in {"reproduced", "disconfirmed"} for disposition in dispositions):
            raise EvidenceValidationError(
                f"{artifact_label}: external Report Source cannot be verified without repo_root; record unproven"
            )
        return
    if repo_root is None:
        return
    source = (repo_root / (values["Report Source"] or "")).resolve()
    try:
        source.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise EvidenceValidationError(f"{artifact_label}: Report Source escapes repo root") from exc
    if not source.is_file():
        raise EvidenceValidationError(f"{artifact_label}: Report Source does not exist: {values['Report Source']}")
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != values["Report Source SHA256"]:
        raise EvidenceValidationError(f"{artifact_label}: Report Source SHA256 is stale or tampered")


def validate(
    text: str,
    *,
    artifact_label: str = "artifact",
    evidence_mode: bool = False,
    repo_root: Path | None = None,
) -> None:
    """Validate evidence-led sections when a caller activates that mode."""
    has_disposition = "## Evidence Disposition" in text
    has_verification = "## Adversarial Verification" in text
    if not evidence_mode and not has_disposition and not has_verification:
        return
    if has_disposition != has_verification:
        raise EvidenceValidationError(f"{artifact_label}: evidence-led mode requires both evidence headings")
    if evidence_mode and not has_disposition:
        raise EvidenceValidationError(
            f"{artifact_label}: --evidence-led requires Evidence Disposition and Adversarial Verification"
        )
    count, values = _metadata(text, artifact_label)
    dispositioned = _ids(values["Dispositioned Findings"])
    ids, digest, dispositions = _records(text, artifact_label, len(dispositioned), repo_root=repo_root)
    _validate_source_binding(
        values,
        dispositions=dispositions,
        repo_root=repo_root,
        artifact_label=artifact_label,
    )
    if values["Evidence Digest"] != digest:
        raise EvidenceValidationError(f"{artifact_label}: Evidence Digest does not match typed records")
    _validate_coverage(values, ids, count, artifact_label)


def validate_or_raise(
    text: str,
    *,
    artifact_label: str,
    evidence_mode: bool = False,
    repo_root: Path | None = None,
) -> None:
    validate(text, artifact_label=artifact_label, evidence_mode=evidence_mode, repo_root=repo_root)


def validate_for_artifact(
    text: str,
    *,
    artifact_label: str,
    evidence_mode: bool = False,
    repo_root: Path | None = None,
    error_cls: type[Exception] = EvidenceValidationError,
) -> None:
    try:
        validate(text, artifact_label=artifact_label, evidence_mode=evidence_mode, repo_root=repo_root)
    except EvidenceValidationError as exc:
        raise error_cls(str(exc)) from exc
