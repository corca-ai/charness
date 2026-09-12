"""Build a small, identity-bound follow-up context for a prior review."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

import yaml


def _load_context_module():
    path = Path(__file__).with_name("review_followup_context.py")
    spec = importlib.util.spec_from_file_location("charness_review_followup_context", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load follow-up context helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTEXT = _load_context_module()
MAX_CONTEXT_BYTES = CONTEXT.MAX_CONTEXT_BYTES

def _load_selection_module():
    path = Path(__file__).with_name("review_followup_selection.py")
    spec = importlib.util.spec_from_file_location("charness_review_followup_selection", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load follow-up selection helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SELECTION = _load_selection_module()


def _load_provenance_module():
    path = Path(__file__).with_name("review_followup_provenance.py")
    spec = importlib.util.spec_from_file_location("charness_review_followup_provenance", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load follow-up provenance helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PROVENANCE = _load_provenance_module()


def _load_identity_verification():
    for ancestor in (Path(__file__).resolve(), *Path(__file__).resolve().parents):
        candidate = ancestor / "scripts/review/reviewed_input_verification.py"
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location("charness_followup_identity_verification", candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ImportError("canonical reviewed-input verification is unavailable")


IDENTITY_VERIFICATION = _load_identity_verification()


class FollowupError(ValueError):
    """A prior review cannot safely seed a bounded follow-up."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_safe(root: Path, value: str, *, label: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise FollowupError("path-invalid", f"{label} must be repository-relative: {value}")
    lexical = root / candidate
    if lexical.is_symlink():
        raise FollowupError("path-invalid", f"{label} must not be a symlink: {value}")
    resolved = lexical.resolve(strict=False)
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise FollowupError("path-invalid", f"{label} resolves outside --repo-root: {value}") from exc
    return resolved


def _load_mapping(path: Path) -> dict[str, Any]:
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
        else:
            value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise FollowupError("prior-review-unreadable", f"prior review is not readable: {path}") from exc
    if not isinstance(value, dict):
        raise FollowupError("prior-review-invalid", f"prior review must contain a mapping: {path}")
    return value


def _source_path(root: Path, value: str) -> Path:
    path = _relative_safe(root, value, label="follow-up source")
    if path.is_dir():
        for name in ("partial-result.json", "result.json", "worker-report.yaml"):
            candidate = path / name
            if candidate.is_file() and not candidate.is_symlink():
                return candidate
        raise FollowupError(
            "prior-review-missing",
            f"follow-up directory has no reusable review carrier: {path}",
        )
    if not path.is_file():
        raise FollowupError("prior-review-missing", f"follow-up source does not exist: {path}")
    return path


def _result_payload(raw: dict[str, Any]) -> dict[str, Any]:
    for key in ("reviewer_result", "partial_result", "bounded_review", "result"):
        value = raw.get(key)
        if isinstance(value, dict) and ("findings" in value or "verdict" in value):
            return value
    return raw


_clip = CONTEXT.clip
_compact_findings = CONTEXT.compact_findings
_context_bytes = CONTEXT.context_bytes


def _bound_context(context: dict[str, Any]) -> dict[str, Any]:
    return CONTEXT.bound_context(context, FollowupError)


def _packet_for_prior(root: Path, source: Path, raw: dict[str, Any]) -> tuple[dict[str, Any] | None, Path | None]:
    plan = source.parent / "run-plan.json"
    plan_payload = _load_mapping(plan) if plan.is_file() and not plan.is_symlink() else {}
    packet_value = plan_payload.get("packet_path") or raw.get("packet_path")
    if not isinstance(packet_value, str) or not packet_value:
        return None, None
    packet = _relative_safe(root, packet_value, label="prior packet")
    if not packet.is_file():
        return None, None
    payload = _load_mapping(packet)
    if payload.get("kind") != "charness.critique_prepare_packet":
        raise FollowupError("prior-packet-invalid", f"prior packet has the wrong kind: {packet}")
    return payload, packet


def _verify_prior_semantic_carriers(
    *, root: Path, source: Path, identity: dict[str, Any]
) -> dict[str, Any]:
    manifest_path = source.parent / "semantic-input" / "manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise FollowupError(
            "prior-semantic-input-unavailable",
            "prior review has no retained semantic-input manifest",
        )
    manifest = _load_mapping(manifest_path)
    entries = manifest.get("entries")
    expected = {
        item.get("path"): item.get("content_sha256")
        for item in identity.get("reviewed_content", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    if not isinstance(entries, list) or {
        item.get("path") for item in entries if isinstance(item, dict)
    } != set(expected):
        raise FollowupError(
            "prior-semantic-input-mismatch",
            "prior semantic-input manifest paths do not match the packet identity",
        )
    durable_dir = source.parent / "semantic-input"
    verified_count = 0
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise FollowupError("prior-semantic-input-invalid", "prior semantic-input entry is malformed")
        candidate = durable_dir / Path(str(entry.get("carrier_path", ""))).name
        if not candidate.is_file() or candidate.is_symlink():
            raise FollowupError(
                "prior-semantic-input-unavailable",
                f"prior semantic carrier is not retained: {entry.get('path')}",
            )
        content = candidate.read_bytes()
        if entry.get("content_sha256") != expected.get(entry["path"]):
            raise FollowupError(
                "prior-semantic-input-tampered",
                f"prior semantic manifest does not match `{entry['path']}`",
            )
        valid, reason = IDENTITY_VERIFICATION.verify_semantic_carrier_entry(
            identity, entry, content
        )
        if not valid:
            raise FollowupError(
                "prior-semantic-input-tampered",
                f"prior semantic carrier bytes do not match `{entry['path']}`: {reason}",
            )
        verified_count += 1
    return {"status": "verified", "entries": verified_count}


def _verify_prior_result_carrier(
    *, root: Path, source: Path, raw: dict[str, Any], plan: dict[str, Any], identity: dict[str, Any]
) -> dict[str, Any]:
    return PROVENANCE.verify_result_carrier(
        root=root,
        source=source,
        raw=raw,
        plan=plan,
        identity=identity,
        load_mapping=_load_mapping,
        sha256=_sha256,
        error=FollowupError,
    )
def _verify_prior_packet_binding(
    *,
    root: Path,
    source: Path,
    raw: dict[str, Any],
    plan: dict[str, Any],
    packet: dict[str, Any] | None,
    packet_path: Path | None,
) -> dict[str, Any]:
    """Verify the carrier's packet and identity before reusing its path set.

    A follow-up is a delta of a particular prior review, not merely a delta of
    whatever path list happens to be present in a stale packet.  The carrier
    and its run plan therefore have to agree with the packet bytes and the
    packet's own reviewed-input identity before those paths can seed selection.
    """
    if packet is None or packet_path is None:
        return {"status": "unavailable", "reason": "prior packet was not recorded"}

    expected_packet = raw.get("packet_sha256") or plan.get("packet_sha256")
    expected_identity = (
        raw.get("reviewed_input_identity_sha256")
        or plan.get("reviewed_input_identity_sha256")
    )
    actual_packet = _sha256(packet_path)
    packet_identity = packet.get("reviewed_input_identity")
    actual_identity = packet_identity.get("identity_sha256") if isinstance(packet_identity, dict) else None
    details = {
        "packet_path": packet_path.relative_to(root).as_posix(),
        "expected_packet_sha256": expected_packet,
        "actual_packet_sha256": actual_packet,
        "expected_reviewed_input_identity_sha256": expected_identity,
        "actual_reviewed_input_identity_sha256": actual_identity,
    }
    if not isinstance(expected_packet, str) or actual_packet != expected_packet:
        raise FollowupError(
            "prior-packet-tampered",
            "prior packet bytes do not match the carrier's recorded packet identity",
            details=details,
        )
    if not isinstance(expected_identity, str) or actual_identity != expected_identity:
        raise FollowupError(
            "prior-identity-mismatch",
            "prior packet reviewed-input identity does not match the carrier",
            details=details,
        )
    if not isinstance(packet_identity, dict) or packet_identity.get("status") != "captured":
        raise FollowupError(
            "prior-identity-unavailable",
            "prior packet has no captured reviewed-input identity",
            details=details,
        )
    ok, reason = IDENTITY_VERIFICATION.verify_packet_binding(
        repo_root=root,
        packet_path=packet_path.relative_to(root).as_posix(),
        packet_sha256=actual_packet,
        identity_sha256=actual_identity,
        expected_kind="charness.critique_prepare_packet",
        check_current=False,
    )
    if not ok:
        raise FollowupError(
            "prior-packet-invalid",
            f"canonical prior packet verification failed: {reason}",
            details=details,
        )
    recorded_ok, recorded_reason = IDENTITY_VERIFICATION.verify_recorded_reviewed_input_identity(
        packet_identity
    )
    if not recorded_ok:
        raise FollowupError(
            "prior-identity-invalid",
            f"canonical prior identity verification failed: {recorded_reason}",
            details=details,
        )
    carrier_binding = _verify_prior_semantic_carriers(
        root=root, source=source, identity=packet_identity
    )
    result_binding = _verify_prior_result_carrier(
        root=root, source=source, raw=raw, plan=plan, identity=packet_identity
    )
    return {
        "status": "verified",
        "attempt_id": result_binding["attempt_id"],
        "packet_sha256": actual_packet,
        "reviewed_input_identity_sha256": actual_identity,
        "packet_verification": "canonical-integrity-only",
        "identity_verification": "recorded-self-digest",
        "semantic_input": carrier_binding,
        "result_carrier": result_binding,
    }


def build_followup(
    *,
    repo_root: Path,
    source_value: str,
    explicit_paths: list[str] | None,
    build_identity: Callable[..., dict[str, Any]],
    substrate_mode: str | None = None,
    changed_ref: str | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """Return changed follow-up paths and a compact prior-finding context.

    With no explicit paths, only previously reviewed working-tree paths whose
    bound bytes changed are selected. A committed-ref review cannot be safely
    narrowed by comparing unlike hash framings, so it requires explicit paths.
    """
    source = _source_path(repo_root, source_value)
    raw = _load_mapping(source)
    prior = _result_payload(raw)
    packet, packet_path = _packet_for_prior(repo_root, source, raw)
    plan = _load_mapping(source.parent / "run-plan.json") if (source.parent / "run-plan.json").is_file() else {}
    prior_binding = _verify_prior_packet_binding(
        root=repo_root,
        source=source,
        raw=raw,
        plan=plan,
        packet=packet,
        packet_path=packet_path,
    )
    identity = packet.get("reviewed_input_identity") if isinstance(packet, dict) else None
    identity = identity if isinstance(identity, dict) else {}
    prior_paths = [path for path in identity.get("reviewed_paths", []) if isinstance(path, str)]
    prior_mode = identity.get("substrate_mode") or identity.get("mode")
    current_mode = substrate_mode or "working-tree"
    paths, selection, comparison, selection_receipt = SELECTION.select_paths(
        repo_root=repo_root,
        identity=identity,
        prior_paths=prior_paths,
        explicit_paths=explicit_paths,
        prior_mode=prior_mode,
        current_mode=current_mode,
        changed_ref=changed_ref,
        build_identity=build_identity,
        prior_binding=prior_binding,
        error=FollowupError,
    )

    findings, omitted, _ = _compact_findings(prior.get("findings"))
    context = {
        "kind": "charness.review_followup_context.v1",
        "source": source.relative_to(repo_root).as_posix(),
        "source_sha256": _sha256(source),
        "prior_attempt_id": prior_binding["attempt_id"],
        "prior_verdict": prior.get("verdict") or prior.get("review_verdict") or "unknown",
        "prior_scope": _clip(prior.get("scope") or plan.get("scope") or "", 600),
        "prior_lens": _clip(prior.get("lens") or plan.get("lens") or "", 600),
        "prior_packet_path": packet_path.relative_to(repo_root).as_posix() if packet_path else None,
        "prior_packet_sha256": prior.get("packet_sha256") or plan.get("packet_sha256"),
        "prior_reviewed_input_identity_sha256": (
            prior.get("reviewed_input_identity_sha256")
            or plan.get("reviewed_input_identity_sha256")
        ),
        "selection": selection,
        "selected_paths": paths,
        "prior_reviewed_paths": len(prior_paths),
        "comparison": comparison,
        "selection_receipt": selection_receipt,
        "prior_findings": findings,
        "omitted_finding_ids": omitted,
        "prior_next_move": _clip(prior.get("next_move") or "", 900),
        "prior_non_claims": [
            _clip(item, 600) for item in (prior.get("non_claims") or []) if isinstance(item, str)
        ][:12],
        "approval_rule": (
            "This is prior evidence only. Reuse findings as hypotheses; do not treat a prior "
            "block, defer, timeout, or partial result as approval. The new reviewer must bind "
            "the new packet and current selected paths independently."
        ),
    }
    if omitted:
        context["context_truncated"] = True
    return paths, _bound_context(context)


def bind_final_identity(context: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]:
    return CONTEXT.bind_final_identity(context, identity, FollowupError)
