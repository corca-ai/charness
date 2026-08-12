"""No-increase ratchet for the repo-local boundary-bypass inventory."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

RATCHET_SCHEMA_VERSION = "charness.quality.boundary_bypass_ratchet.v2"
CALL_SITE_FINGERPRINT_ALGO_VERSION = "1"
DEFAULT_BASELINE_PATH = Path("scripts/boundary-bypass-baseline.json")
DEFAULT_EXEMPTIONS_PATH = Path("scripts/boundary-bypass-exemptions.txt")
COUNT_FIELDS = (
    "candidate_count",
    "convertible_count",
    "internal_boundary_count",
    "keep_boundary_count",
)
# `candidate_key_count` is deliberately NOT enforced here, and the reason is a proof, not a
# preference. `filtered_summary` derives it by filtering exemptions out of exactly what
# `candidate_keys` returns and `build_baseline` writes. So `current > baseline` on that field means
# the current key set is larger than the baseline's, which means it cannot be a subset of it, which
# means `new_candidate_keys` is non-empty. The arm cannot fire without `new_candidate_keys` firing
# first, for ANY payload, not merely for payloads this repo's generator happens to produce.
#
# The set shape is what makes that unconditional, and it is also what the field is supposed to be:
# `skills/public/quality/references/boundary-bypass-ratchet.md:50` publishes it as "the number of
# UNIQUE derived candidate keys", the portable validator derives it as `len(candidate_keys)`
# (`skills/public/quality/scripts/validate_boundary_bypass_payload.py:104`), and the inventory
# generator builds it from a set comprehension (`scripts/inventory_boundary_bypass_lib.py:225`).
# This function was the one definition of four that summed per-row target counts instead, which
# agreed with the other three only while no payload repeated a key.
#
# The field stays in `filtered_summary` and in the payload; only enforcement drops. The other four
# fields are row-shaped -- they flip with an identical key set -- so none of them is subsumed.
#
# `new_candidate_keys` now carries a call-site-content identity, so a pure test-path move cannot
# mint a key. The baseline also keeps path pairs as advisory metadata for consumers that need to
# locate a subprocess boundary; those pairs do not participate in the verdict.


class RatchetError(ValueError):
    """Raised when ratchet input files are malformed."""


def candidate_key(member_hashes: list[str]) -> str:
    """Return a path-invariant, duplicate-preserving call-site identity."""
    return hashlib.sha256("\n".join(sorted(member_hashes)).encode("utf-8")).hexdigest()[:16]


def _rows_with_targets(payload: dict[str, Any]) -> Iterator[tuple[dict[str, Any], str, list[str], list[str]]]:
    """The one walk over candidate rows, so key derivation cannot fork.

    `candidate_keys` and `filtered_summary` used to walk `candidates` separately and apply their
    own `test_file`/`isinstance` conditions. Two walks that must agree is what let
    `candidate_key_count` drift into a per-row sum while every published definition of it stayed
    set-shaped -- and that agreement is the precondition COUNT_FIELDS now relies on.

    An empty `test_file` RAISES rather than being skipped. Skipping is what the old
    `candidate_keys` did, and unifying on it would have silently lowered all four still-enforced
    counts for such a payload -- and `check_payload` fires only on `current > baseline`, so a
    change that can only lower `current` can only ever MASK the arm. Refusing instead means the
    two walks agree without either of them being able to hide a row, and it matches the published
    payload contract, which already rejects the shape outright
    (`skills/public/quality/scripts/validate_boundary_bypass_payload.py:48-49`).
    """
    for index, row in enumerate(payload.get("candidates", [])):
        test_file = row.get("test_file")
        if not isinstance(test_file, str) or not test_file:
            raise RatchetError(
                f"candidates[{index}].test_file must be a non-empty string, got {test_file!r}"
            )
        targets = [target for target in row.get("import_safe_targets", []) if isinstance(target, str)]
        member_hashes = row.get("call_site_member_hashes")
        if not isinstance(member_hashes, list) or not member_hashes or not all(isinstance(value, str) and value for value in member_hashes):
            raise RatchetError(f"candidates[{index}].call_site_member_hashes must be a non-empty list of strings")
        yield row, test_file, targets, member_hashes


def candidate_keys(payload: dict[str, Any]) -> list[str]:
    return sorted(
        {
            candidate_key(member_hashes)
            for _, _, _, member_hashes in _rows_with_targets(payload)
        }
    )


def load_exemptions(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    exemptions: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, marker, why = line.partition("# why:")
        if not marker or not key.strip() or not why.strip():
            raise RatchetError(f"{path}:{line_number}: exemption must be `<content-fingerprint> # why: <rationale>`")
        rendered_key = key.strip()
        if len(rendered_key) != 16 or any(char not in "0123456789abcdef" for char in rendered_key):
            raise RatchetError(f"{path}:{line_number}: exemption key must be a 16-hex content fingerprint")
        exemptions[rendered_key] = why.strip()
    return exemptions


def filtered_summary(payload: dict[str, Any], exemptions: dict[str, str]) -> dict[str, int]:
    rows = []
    # Derived from `candidate_keys`, not recounted here. `candidate_key_count` is published as the
    # count of UNIQUE keys, and this used to be the one derivation of four that summed per-row
    # target counts instead -- agreeing with the other three only while no payload repeated a key.
    # Reusing the same function that `build_baseline` writes `candidate_keys` from makes the
    # equality COUNT_FIELDS relies on true BY CONSTRUCTION rather than by two implementations
    # happening to agree, and leaves one definition of a key to keep correct.
    key_count = len([key for key in candidate_keys(payload) if key not in exemptions])
    for row, _test_file, row_targets, member_hashes in _rows_with_targets(payload):
        targets = [
            target for target in row_targets if candidate_key(member_hashes) not in exemptions
        ]
        if not targets:
            continue
        clean = [
            target
            for target in row.get("clean_inprocess_targets", [])
            if isinstance(target, str) and target in targets
        ]
        internal = [
            target
            for target in row.get("internal_boundary_targets", [])
            if isinstance(target, str) and target in targets
        ]
        rows.append({"likely_keep_boundary": bool(row.get("likely_keep_boundary")), "clean": clean, "internal": internal})
    keep_boundary = sum(1 for row in rows if row["likely_keep_boundary"])
    return {
        "candidate_count": len(rows),
        "convertible_count": sum(1 for row in rows if (not row["likely_keep_boundary"]) and row["clean"]),
        "internal_boundary_count": sum(1 for row in rows if row["internal"]),
        "keep_boundary_count": keep_boundary,
        "candidate_key_count": key_count,
    }


def build_baseline(payload: dict[str, Any], exemptions: dict[str, str] | None = None) -> dict[str, Any]:
    exemptions = exemptions or {}
    keys = [key for key in candidate_keys(payload) if key not in exemptions]
    return {
        "schemaVersion": RATCHET_SCHEMA_VERSION,
        "policy": "no_increase",
        "inventory_schemaVersion": payload.get("schemaVersion"),
        "call_site_fingerprint_algo_version": payload.get("call_site_fingerprint_algo_version"),
        "summary": filtered_summary(payload, exemptions),
        "candidate_keys": keys,
        "candidate_pairs": [
            {"test_file": test_file, "import_safe_targets": targets}
            for _, test_file, targets, _ in _rows_with_targets(payload)
        ],
    }


def load_baseline(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RatchetError(f"baseline not found: {path}")
    try:
        baseline = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RatchetError(f"{path}: invalid JSON: {exc}") from exc
    if baseline.get("schemaVersion") != RATCHET_SCHEMA_VERSION:
        raise RatchetError(f"{path}: unexpected schemaVersion {baseline.get('schemaVersion')!r}")
    if baseline.get("policy") != "no_increase":
        raise RatchetError(f"{path}: expected policy `no_increase`")
    if baseline.get("call_site_fingerprint_algo_version") != CALL_SITE_FINGERPRINT_ALGO_VERSION:
        raise RatchetError(f"{path}: unexpected call_site_fingerprint_algo_version; regenerate the baseline")
    if not isinstance(baseline.get("summary"), dict) or not isinstance(baseline.get("candidate_keys"), list) or not isinstance(baseline.get("candidate_pairs"), list):
        raise RatchetError(f"{path}: expected `summary`, `candidate_keys`, and `candidate_pairs`")
    # `candidate_keys` is the list `new_candidate_keys` diffs against, so after `candidate_key_count`
    # left COUNT_FIELDS this list carries the whole verdict. A hand-edit that drops a key from it
    # without decrementing the count makes the gate report a phantom new key; the equivalent
    # cross-check has existed for PAYLOADS since
    # `skills/public/quality/scripts/validate_boundary_bypass_payload.py:102-111` and was simply
    # absent for baselines. The disagreement is not hypothetical: at commit `7a43c8a4` this file
    # recorded `candidate_key_count: 151` against 150 keys (`git show 7a43c8a4:scripts/boundary-
    # bypass-baseline.json`). Required, not optional -- `build_baseline` always writes the field,
    # so nothing legitimate omits it, and tolerating absence would let one deleted JSON line
    # disable the check that the hand-edit threat model is the entire reason for.
    recorded_key_count = baseline["summary"].get("candidate_key_count")
    actual_key_count = len(baseline["candidate_keys"])
    if not isinstance(recorded_key_count, int) or isinstance(recorded_key_count, bool):
        raise RatchetError(
            f"{path}: summary.candidate_key_count must be an integer, got "
            f"{recorded_key_count!r}; regenerate the baseline"
        )
    if recorded_key_count != actual_key_count:
        raise RatchetError(
            f"{path}: summary.candidate_key_count {recorded_key_count} disagrees with "
            f"len(candidate_keys) {actual_key_count}; regenerate the baseline rather than "
            "hand-editing one of the two"
        )
    return baseline


def check_payload(payload: dict[str, Any], baseline: dict[str, Any], exemptions: dict[str, str]) -> dict[str, Any]:
    schema_mismatch = None
    baseline_inventory_schema = baseline.get("inventory_schemaVersion")
    current_inventory_schema = payload.get("schemaVersion")
    if baseline_inventory_schema != current_inventory_schema:
        schema_mismatch = {
            "baseline": baseline_inventory_schema,
            "current": current_inventory_schema,
        }
    algorithm_mismatch = baseline.get("call_site_fingerprint_algo_version") != payload.get("call_site_fingerprint_algo_version")
    current_keys = [key for key in candidate_keys(payload) if key not in exemptions]
    baseline_keys = {str(key) for key in baseline.get("candidate_keys", [])}
    current_summary = filtered_summary(payload, exemptions)
    baseline_summary = baseline["summary"]
    count_increases = {
        field: {"baseline": int(baseline_summary.get(field, 0)), "current": current_summary[field]}
        for field in COUNT_FIELDS
        if current_summary[field] > int(baseline_summary.get(field, 0))
    }
    new_keys = sorted(set(current_keys) - baseline_keys)
    return {
        "ok": not schema_mismatch and not algorithm_mismatch and not count_increases and not new_keys,
        "policy": "no_increase",
        "schema_mismatch": schema_mismatch,
        "algorithm_mismatch": algorithm_mismatch,
        "summary": current_summary,
        "baseline_summary": {field: int(baseline_summary.get(field, 0)) for field in COUNT_FIELDS},
        "new_candidate_keys": new_keys,
        "count_increases": count_increases,
        "exempted_count": len(exemptions),
    }
