"""Repository I/O and provenance-chain checks for worker report carriers."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def _load_delivery_fields():
    candidate = Path(__file__).resolve().with_name("reviewer_delivery_fields.py")
    if not candidate.is_file():
        raise ImportError(f"package-local delivery-fields helper not found: {candidate}")
    spec = importlib.util.spec_from_file_location("charness_reviewer_delivery_fields", candidate)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load package-local helper: {candidate}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PARENT_RECEIPT_ID_RE


PARENT_RECEIPT_ID_RE = _load_delivery_fields()
EXPECTED_PACKET_KIND = "charness.critique_prepare_packet"


def _load_result_contract():
    here = Path(__file__).resolve()
    for ancestor in (here.parent, *here.parents):
        candidate = ancestor / "reviewer_result_contract.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("charness_reviewer_result_contract", candidate)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    raise ImportError("package reviewer_result_contract.py not found")


def _load_capability_contract():
    candidate = Path(__file__).resolve().with_name("reviewer_capability.py")
    module_name = "charness_reviewer_capability"
    spec = importlib.util.spec_from_file_location(module_name, candidate)
    if spec is None or spec.loader is None:
        raise ImportError(f"package reviewer_capability.py not found: {candidate}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
    return module


def _load_delivery_attempt_parser():
    package_dir = Path(__file__).resolve().parent
    aliases = {
        "reviewer_delivery_fields": package_dir / "reviewer_delivery_fields.py",
        "reviewer_delivery_history": package_dir / "reviewer_delivery_history.py",
        "reviewer_delivery_schema": package_dir / "reviewer_delivery_schema.py",
        "reviewer_delivery_attempt_codec": package_dir / "reviewer_delivery_attempt_codec.py",
        "reviewer_delivery_attempt": package_dir / "reviewer_delivery_attempt.py",
    }
    saved: dict[str, object] = {}
    loaded: dict[str, object] = {}
    try:
        for public_name, path in aliases.items():
            spec = importlib.util.spec_from_file_location(f"charness_{public_name}", path)
            if spec is None or spec.loader is None:
                raise ImportError(f"unable to load package-local helper: {path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"charness_{public_name}"] = module
            saved[public_name] = sys.modules.get(public_name)
            sys.modules[public_name] = module
            spec.loader.exec_module(module)
            loaded[public_name] = module
        return loaded["reviewer_delivery_attempt"].DeliveryAttempt
    finally:
        for public_name, previous in saved.items():
            if previous is None:
                sys.modules.pop(public_name, None)
            else:
                sys.modules[public_name] = previous


def _load_identity_verifier():
    for ancestor in list(Path(__file__).resolve().parents)[:6]:
        candidate = ancestor / "scripts" / "review" / "reviewed_input_verification.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("charness_reviewed_input_verification", candidate)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    return None


class WorkerCarrierError(ValueError):
    """The supplied artifact cannot prove a delivered worker approval."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


HIDDEN_RUNTIME_ROOTS = frozenset({".charness", ".artifacts"})


def _hidden_runtime_relative(rel: Path) -> bool:
    """True when the carrier sits in Variable Hidden Knowledge (`docs/artifact-policy.md`)."""
    return bool(rel.parts) and rel.parts[0] in HIDDEN_RUNTIME_ROOTS


def _report_path(repo_root: Path, value: str, *, allow_hidden: bool = False) -> Path:
    report_path = Path(value.strip().strip("`"))
    if not report_path.is_absolute() and ".." in report_path.parts:
        raise WorkerCarrierError("worker report path must be a safe repo-relative path without traversal, or an absolute path resolved inside the repository")
    resolved_root = repo_root.resolve()
    report_file = (report_path if report_path.is_absolute() else resolved_root / report_path).resolve()
    try:
        rel = report_file.relative_to(resolved_root)
    except ValueError as exc:
        raise WorkerCarrierError(f"worker report carrier path resolves outside the repository: {value}") from exc
    cited_hidden = (not report_path.is_absolute() and _hidden_runtime_relative(report_path)) or _hidden_runtime_relative(rel)
    if cited_hidden and not allow_hidden:
        raise WorkerCarrierError(
            f"worker report carrier is hidden runtime, not a durable tracked copy: {value}. "
            "Promote worker-report.yaml under charness-artifacts/critique/workers/<attempt>/ and cite that path."
        )
    if not report_file.is_file():
        raise WorkerCarrierError(f"worker report carrier does not exist inside the repository: {value}")
    return report_file


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkerCarrierError(f"{label} is not readable JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorkerCarrierError(f"{label} must contain a mapping")
    return payload


def _validate_packet_binding(
    *,
    repo_root: Path,
    artifact_binding_fields: dict[str, str],
    required_issue_numbers: list[int] | None = None,
    required_repository: str | None = None,
) -> None:
    packet_path = artifact_binding_fields.get("packet path", "").strip().strip("`")
    if not packet_path:
        raise WorkerCarrierError("worker-delivered requires the Reviewed Input Identity packet path")
    verifier = _load_identity_verifier()
    if verifier is None:
        raise WorkerCarrierError("package reviewed-input verifier is unavailable")
    try:
        packet = _read_json(_report_path(repo_root, packet_path), "reviewed packet")
        ok, reason = verifier.verify_packet_binding(
            repo_root=repo_root,
            packet_path=packet_path,
            packet_sha256=artifact_binding_fields.get("packet sha256", "").strip().lower(),
            identity_sha256=artifact_binding_fields.get("identity sha256", "").strip().lower(),
            expected_kind=EXPECTED_PACKET_KIND,
            check_current=True,
        )
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise WorkerCarrierError(f"reviewed packet binding could not be verified: {exc}") from exc
    if not ok:
        raise WorkerCarrierError(f"reviewed packet binding is not current: {reason}")
    if required_issue_numbers:
        repository = (required_repository or "").strip().lower()
        for number in required_issue_numbers:
            expected = f"{repository}#{number}" if repository else f"issue#{number}"
            prepared_for = str(packet.get("prepared_for", "")).lower()
            if not prepared_for.startswith(expected) or (
                len(prepared_for) > len(expected) and prepared_for[len(expected)].isalnum()
            ):
                raise WorkerCarrierError(f"reviewed packet prepared_for does not bind exactly to {expected}")
        packet_repository = str(packet.get("repo", "")).strip().lower()
        accepted = {repository, repository.rsplit("/", 1)[-1]}
        if not packet_repository or packet_repository not in accepted:
            raise WorkerCarrierError(f"reviewed packet repo does not bind exactly to {repository}")


def _validate_receipt_and_result(
    *, repo_root: Path, report: dict[str, Any], require_pass: bool = True
) -> tuple[dict[str, Any], dict[str, Any], str]:
    receipt_value = report.get("receipt_path")
    if not isinstance(receipt_value, str):
        raise WorkerCarrierError("worker report has no repo-readable receipt path")
    receipt = _read_json(_report_path(repo_root, receipt_value, allow_hidden=True), "worker receipt")
    if receipt.get("schema_version") != "charness.reviewer_worker.v1":
        raise WorkerCarrierError("worker receipt has the wrong schema")
    if receipt.get("status") != "succeeded" or receipt.get("terminal") is not True:
        raise WorkerCarrierError("worker receipt is not a terminal succeeded receipt")
    if receipt.get("exit_code") != 0 or receipt.get("output_fresh") is not True:
        raise WorkerCarrierError("worker receipt does not prove a fresh successful result")
    try:
        capability_contract = _load_capability_contract()
        capability_contract.validate_receipt_capabilities(
            receipt, attempt_id=str(report.get("attempt_id", ""))
        )
    except (ImportError, ValueError) as exc:
        raise WorkerCarrierError(f"worker receipt capability envelope is not valid: {exc}") from exc
    output_value = receipt.get("output_file")
    if not isinstance(output_value, str):
        raise WorkerCarrierError("worker receipt has no output file")
    output = _report_path(repo_root, output_value, allow_hidden=True)
    output_hash = _sha256(output)
    if output_hash != receipt.get("output_sha256") or output.stat().st_size != receipt.get("output_size"):
        raise WorkerCarrierError("worker output does not match the typed receipt hash/size")
    try:
        result = _load_result_contract().validate_bounded_result(
            output,
            packet_identity=str(report.get("packet_identity", "")),
            reviewed_input_identity=str(report.get("reviewed_input_identity", "")),
            require_pass=require_pass,
        )
    except (ImportError, ValueError) as exc:
        raise WorkerCarrierError(str(exc)) from exc
    try:
        capability_contract.validate_result_capability_non_claims(result, receipt)
    except (ImportError, ValueError) as exc:
        raise WorkerCarrierError(f"worker result capability non-claims are not approval-eligible: {exc}") from exc
    for field in ("capability_non_claims", "capability_non_claims_sha256"):
        if report.get(field) != receipt.get(field):
            raise WorkerCarrierError(f"worker report {field} does not match the worker receipt")
    if report.get("findings_identity") != output_hash or report.get("receipt_output_sha256") != output_hash:
        raise WorkerCarrierError("worker findings identity does not match the typed result")
    return receipt, result, output_hash


def _validate_joined_fields(
    *, attempt: Any, report: dict[str, Any], receipt: dict[str, Any], provenance: dict[str, Any]
) -> None:
    joined_fields = (
        "attempt_id", "scope", "packet_identity", "reviewed_input_identity",
        "parent_receipt_identity", "boundary_mode", "boundary_fingerprint", "execution_mode",
        "backend", "prompt_sha256", "schema_sha256",
        "capability_launch_envelope_sha256",
    )
    if report.get("attempt_id") != provenance.get("attempt_id"):
        raise WorkerCarrierError("delivery chain attempt_id does not match report provenance")
    if provenance.get("capability_non_claims_sha256") != report.get("capability_non_claims_sha256"):
        raise WorkerCarrierError("delivery chain capability non-claim digest does not match report provenance")
    for field in joined_fields:
        expected = provenance.get(field) if field == "attempt_id" else report.get(field)
        actual = getattr(attempt, field, None)
        if field == "boundary_fingerprint" and expected is None:
            if actual is not None or receipt.get(field) is not None or provenance.get(field) is not None:
                raise WorkerCarrierError(
                    "delivery chain boundary_fingerprint is present for a boundary mode that does not require it"
                )
            continue
        observed_receipt = receipt.get(field)
        if field == "boundary_mode" and observed_receipt is None and receipt.get("boundary_fingerprint") is not None:
            observed_receipt = "shared-tree-fingerprint"
        if expected is None or actual != expected or observed_receipt != expected:
            raise WorkerCarrierError(f"delivery chain {field} does not match report, receipt, and ledger attempt")
        if field != "attempt_id" and provenance.get(field) != expected:
            raise WorkerCarrierError(f"delivery chain {field} does not match report provenance")


def _validate_ledger(
    *, repo_root: Path, report: dict[str, Any], receipt: dict[str, Any], output_hash: str
) -> None:
    ledger_value = report.get("ledger_path")
    provenance = report.get("provenance")
    if not isinstance(ledger_value, str):
        raise WorkerCarrierError("worker report has no repo-readable ledger path")
    if not isinstance(provenance, dict) or not provenance.get("attempt_id"):
        raise WorkerCarrierError("worker report has no typed attempt provenance")
    ledger = _read_json(_report_path(repo_root, ledger_value, allow_hidden=True), "delivery ledger")
    if ledger.get("schema_version") != "charness.reviewer_delivery.v1":
        raise WorkerCarrierError("delivery ledger has the wrong schema")
    attempts = ledger.get("attempts")
    if not isinstance(attempts, list):
        raise WorkerCarrierError("delivery ledger has no attempts list")
    raw_attempt = next((item for item in attempts if isinstance(item, dict) and item.get("attempt_id") == provenance["attempt_id"]), None)
    if raw_attempt is None:
        raise WorkerCarrierError("delivery ledger does not contain the report attempt")
    try:
        attempt = _load_delivery_attempt_parser().from_dict(raw_attempt)
    except (ImportError, ValueError, TypeError, KeyError) as exc:
        raise WorkerCarrierError(f"delivery ledger canonical history is invalid: {exc}") from exc
    _validate_joined_fields(attempt=attempt, report=report, receipt=receipt, provenance=provenance)
    aliases = {
        "attempt_scope": report.get("scope"),
        "attempt_packet_identity": report.get("packet_identity"),
        "attempt_parent_receipt_identity": report.get("parent_receipt_identity"),
        "result_packet_identity": report.get("packet_identity"),
        "result_reviewed_input_identity": report.get("reviewed_input_identity"),
    }
    mismatches = [key for key, expected in aliases.items() if provenance.get(key) != expected]
    if mismatches:
        raise WorkerCarrierError(f"delivery chain provenance aliases do not match the report: {mismatches}")
    if attempt.state != "findings-received" or attempt.terminal is not True or not attempt.findings_identity:
        raise WorkerCarrierError("delivery ledger does not prove findings-received completion")
    if attempt.findings_identity != output_hash:
        raise WorkerCarrierError("delivery ledger findings identity does not match the result")


def _validate_delivery_chain(
    *, repo_root: Path, report: dict[str, Any], require_pass: bool = True
) -> tuple[dict[str, Any], dict[str, Any], str]:
    receipt, result, output_hash = _validate_receipt_and_result(
        repo_root=repo_root, report=report, require_pass=require_pass
    )
    _validate_ledger(repo_root=repo_root, report=report, receipt=receipt, output_hash=output_hash)
    return receipt, result, output_hash


def validate_delivered_worker_report(
    *, repo_root: Path, report: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Validate a delivered typed result without converting it into approval.

    A critique round records findings, so a typed ``block`` or ``defer`` is a
    valid delivered result even though the approval consumer must reject it.
    The report remains delivery evidence; the typed result bytes remain the
    findings carrier. Requiring this chain makes a same-context raw text file
    impossible to submit as a reviewer round.
    """
    expected = {
        "schema_version": "charness.reviewer_worker_report.v1",
        "delivery_state": "findings-received",
        "collection_ready": True,
        "provenance_ok": True,
        "receipt_ok": True,
        "ledger_ok": True,
        "result_schema_ok": True,
    }
    mismatches = [
        f"{field}={report.get(field)!r} (expected {value!r})"
        for field, value in expected.items()
        if report.get(field) != value
    ]
    if mismatches:
        raise WorkerCarrierError(
            "worker report is not a delivered typed result: " + "; ".join(mismatches)
        )
    if report.get("execution_mode") not in ("file-backed-worker", "typed-subagent"):
        raise WorkerCarrierError("worker report has no supported distinct execution mode")
    for field in (
        "attempt_id",
        "producer_run_id",
        "scope",
        "packet_identity",
        "reviewed_input_identity",
        "parent_receipt_identity",
        "boundary_mode",
        "findings_identity",
        "receipt_output_sha256",
    ):
        if not isinstance(report.get(field), str) or not report[field].strip():
            raise WorkerCarrierError(f"worker report has no explicit {field}")
    return _validate_delivery_chain(repo_root=repo_root, report=report, require_pass=False)
