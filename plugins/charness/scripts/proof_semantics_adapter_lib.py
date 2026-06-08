"""Proof-semantics adapter loader + validator (the #339 adapter boundary).

Charness asks; the adapter answers. The portable residual/disposition ledger
(``scripts/disposition_form.py``) stays presence/form-enum-only and learns NO
domain concept. The DOMAIN proof semantics live entirely in this OPTIONAL adapter,
which declares:

- ``proof_levels`` — the ordered backbone of proof strength, weakest -> strongest.
- ``incomparable`` — unordered level pairs that do NOT satisfy each other despite
  their backbone rank (a partial order, not a chain). Each pair is a delimited
  ``"a, b"`` (or ``"a|b"``) string (parser-friendly) or an ``[a, b]`` list.
- ``acceptance_map`` — acceptance-class -> the MINIMUM proof level satisfying it.
- ``verifier_refs`` — proof-level -> a free-form verifier/artifact reference.
- ``gap_policy`` — which acceptance-class gaps are ``acceptable`` / ``out_of_scope``,
  and whether an unclassified gap ``needs_issue``.

Charness only ever does generic lookups + a rank/incomparability comparison over
these declared tokens (``level_satisfies``, ``min_level_for_acceptance``,
``gap_disposition_for``); it never hard-codes a domain proof level or acceptance
class. The adapter is OPTIONAL and degrades, never absent: a repo with no adapter
still gets the portable presence/form ledger floor, and proof-mismatch detection
degrades to "no domain map available -> require a ledger disposition" rather than
silently passing. A found-but-INVALID adapter fails closed so a repo cannot ship a
broken proof map.

Shared, cross-surface: lives in top-level ``scripts/`` (like ``disposition_form``)
so achieve and issue closeout both parent-walk/import it via ``scripts.``.

Schema, resolution, degradation, and the three closeout-blocking conditions are
documented in ``docs/proof-semantics-adapter.md``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file

ADAPTER_CANDIDATES = (
    Path(".agents/proof-semantics-adapter.yaml"),
    Path(".codex/proof-semantics-adapter.yaml"),
    Path(".claude/proof-semantics-adapter.yaml"),
    Path("docs/proof-semantics-adapter.yaml"),
    Path("proof-semantics-adapter.yaml"),
)
STRING_FIELDS = ("repo", "language")


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "proof_levels": [],
        "incomparable": [],
        "acceptance_map": {},
        "verifier_refs": {},
        "gap_policy": {"acceptable": [], "out_of_scope": [], "needs_issue": True},
    }


def _validate_proof_levels(data: dict[str, Any], errors: list[str]) -> list[str]:
    raw = data.get("proof_levels")
    if raw is None:
        return []
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        errors.append("proof_levels must be a list of strings")
        return []
    seen: set[str] = set()
    levels: list[str] = []
    for level in raw:
        if level in seen:
            errors.append(f"proof_levels contains a duplicate level `{level}`")
            continue
        seen.add(level)
        levels.append(level)
    return levels


def _normalize_pair(raw: Any) -> tuple[str, str] | None:
    """Accept a ``[a, b]`` list OR an ``"a, b"`` / ``"a|b"`` string -> ``(a, b)``.

    The repo's minimal YAML loader cannot parse a nested/flow list, so the
    parser-friendly form is the delimited string; the list form is accepted too so
    a host that swaps in a full YAML loader still validates. Returns ``None`` for
    any other shape.
    """
    if isinstance(raw, list) and len(raw) == 2 and all(isinstance(item, str) for item in raw):
        return raw[0].strip(), raw[1].strip()
    if isinstance(raw, str):
        for separator in ("|", ","):
            if separator in raw:
                parts = [part.strip() for part in raw.split(separator)]
                if len(parts) == 2 and all(parts):
                    return parts[0], parts[1]
    return None


def _validate_incomparable(data: dict[str, Any], levels: list[str], errors: list[str]) -> list[list[str]]:
    raw = data.get("incomparable")
    if raw is None:
        return []
    if not isinstance(raw, list):
        errors.append("incomparable must be a list of level pairs (`a, b` strings or [a, b] lists)")
        return []
    known = set(levels)
    pairs: list[list[str]] = []
    for index, entry in enumerate(raw):
        field = f"incomparable[{index}]"
        pair = _normalize_pair(entry)
        if pair is None:
            errors.append(f"{field} must be a level pair (`a, b` string or [a, b] list)")
            continue
        first, second = pair
        if first == second:
            errors.append(f"{field} pairs a level with itself (`{first}`)")
            continue
        for level in (first, second):
            if level not in known:
                errors.append(f"{field} references undeclared proof level `{level}`")
        pairs.append([first, second])
    return pairs


def _validate_acceptance_map(data: dict[str, Any], levels: list[str], errors: list[str]) -> dict[str, str]:
    raw = data.get("acceptance_map")
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        errors.append("acceptance_map must be a mapping of acceptance-class -> proof level")
        return {}
    if raw and not levels:
        errors.append("acceptance_map is declared but proof_levels is empty")
        return {}
    known = set(levels)
    result: dict[str, str] = {}
    for acceptance_class, level in raw.items():
        field = f"acceptance_map.{acceptance_class}"
        if not isinstance(level, str):
            errors.append(f"{field} must name a proof level (string)")
            continue
        if level not in known:
            errors.append(f"{field} references undeclared proof level `{level}`")
            continue
        result[str(acceptance_class)] = level
    return result


def _validate_verifier_refs(data: dict[str, Any], levels: list[str], errors: list[str]) -> dict[str, str]:
    raw = data.get("verifier_refs")
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        errors.append("verifier_refs must be a mapping of proof level -> reference string")
        return {}
    known = set(levels)
    result: dict[str, str] = {}
    for level, ref in raw.items():
        field = f"verifier_refs.{level}"
        if level not in known:
            errors.append(f"{field} references undeclared proof level `{level}`")
            continue
        text = _string(ref, field, errors)
        if text is not None:
            result[str(level)] = text
    return result


def _validate_gap_policy(data: dict[str, Any], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    policy: dict[str, Any] = {"acceptable": [], "out_of_scope": [], "needs_issue": True}
    raw = data.get("gap_policy")
    if raw is None:
        return policy
    if not isinstance(raw, dict):
        errors.append("gap_policy must be a mapping")
        return policy
    for field in ("acceptable", "out_of_scope"):
        value = raw.get(field)
        if value is None:
            continue
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(f"gap_policy.{field} must be a list of acceptance-class strings")
            continue
        policy[field] = list(value)
    overlap = sorted(set(policy["acceptable"]) & set(policy["out_of_scope"]))
    if overlap:
        warnings.append(
            "gap_policy lists class(es) in both `acceptable` and `out_of_scope`: "
            + ", ".join(overlap) + "; `acceptable` wins"
        )
    needs_issue = raw.get("needs_issue")
    if needs_issue is not None:
        if not isinstance(needs_issue, bool):
            errors.append("gap_policy.needs_issue must be a boolean")
        else:
            policy["needs_issue"] = needs_issue
    return policy


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)
    version = data.get("version")
    if version is not None:
        if isinstance(version, int):
            validated["version"] = version
        else:
            errors.append("version must be an integer")
    for field in STRING_FIELDS:
        value = _string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value
    levels = _validate_proof_levels(data, errors)
    validated["proof_levels"] = levels
    validated["incomparable"] = _validate_incomparable(data, levels, errors)
    validated["acceptance_map"] = _validate_acceptance_map(data, levels, errors)
    validated["verifier_refs"] = _validate_verifier_refs(data, levels, errors)
    validated["gap_policy"] = _validate_gap_policy(data, errors, warnings)
    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    for candidate in ADAPTER_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path
    return None


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    if adapter_path is None:
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": infer_repo_defaults(repo_root),
            "errors": [],
            "warnings": [
                "No proof-semantics adapter found. The portable residual/disposition "
                "ledger floor still fires; proof-mismatch detection degrades to "
                "requiring a ledger disposition (no domain proof map available).",
            ],
            "searched_paths": searched_paths,
        }
    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    canonical = repo_root / ".agents" / "proof-semantics-adapter.yaml"
    if adapter_path.resolve() != canonical.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical}.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


# --- Generic proof-semantics queries (domain-blind: only the adapter's tokens) ---


def proof_level_rank(data: dict[str, Any], level: str) -> int | None:
    """The backbone rank of ``level`` (index in ``proof_levels``), or ``None`` when
    the level is undeclared."""
    levels = data.get("proof_levels", [])
    return levels.index(level) if level in levels else None


def levels_incomparable(data: dict[str, Any], first: str, second: str) -> bool:
    """Whether ``{first, second}`` is a declared incomparable pair (order-insensitive)."""
    pair = {first, second}
    return any(pair == set(declared) for declared in data.get("incomparable", []))


def level_satisfies(data: dict[str, Any], reached: str, required: str) -> bool | None:
    """Does ``reached`` satisfy ``required`` under the adapter's partial order?

    Generic and domain-blind: equal levels satisfy; a declared-incomparable pair
    never satisfies (in either direction); otherwise ``reached`` satisfies
    ``required`` iff its backbone rank is >= ``required``'s. Returns ``None`` when
    either level is undeclared, so the caller treats an unknown level as a degraded
    / no-map case instead of a silent pass.
    """
    if reached == required:
        return True
    rank_reached = proof_level_rank(data, reached)
    rank_required = proof_level_rank(data, required)
    if rank_reached is None or rank_required is None:
        return None
    if levels_incomparable(data, reached, required):
        return False
    return rank_reached >= rank_required


def acceptance_classes(data: dict[str, Any]) -> list[str]:
    """The declared acceptance classes (``acceptance_map`` keys), in declaration
    order. Slice-3 condition (i) — a declared acceptance class with no evaluated
    proof entry — reads the boundary through this accessor rather than indexing
    adapter internals."""
    return list(data.get("acceptance_map", {}).keys())


def min_level_for_acceptance(data: dict[str, Any], acceptance_class: str) -> str | None:
    """The minimum proof level that satisfies ``acceptance_class``, or ``None`` when
    the class is not mapped (no domain map for it)."""
    return data.get("acceptance_map", {}).get(acceptance_class)


def gap_disposition_for(data: dict[str, Any], acceptance_class: str) -> str:
    """How the adapter says a gap for ``acceptance_class`` may be dispositioned:
    ``acceptable`` / ``out-of-scope`` / ``needs-issue``. Defaults to ``needs-issue``
    for an unclassified class when ``gap_policy.needs_issue`` is true, else
    ``acceptable``."""
    policy = data.get("gap_policy", {})
    if acceptance_class in policy.get("acceptable", []):
        return "acceptable"
    if acceptance_class in policy.get("out_of_scope", []):
        return "out-of-scope"
    return "needs-issue" if policy.get("needs_issue", True) else "acceptable"


def acceptance_map_available(adapter: dict[str, Any]) -> bool:
    """The degradation signal Slice-3 closeout keys on: a VALID adapter carrying a
    non-empty ``acceptance_map``. When ``False``, proof-mismatch detection has no
    domain map and must degrade to requiring a ledger disposition rather than
    passing silently."""
    if not adapter.get("valid", False):
        return False
    return bool(adapter.get("data", {}).get("acceptance_map"))
