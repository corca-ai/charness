"""Resolve host-reported skill paths only after Charness admission checks.

The host can report a path that still exists after a cache rotation while its
bytes belong to an older (or locally modified) plugin.  A path is therefore
only *admitted* after the package version and the skill content identity both
match the package-owned expectation.  ``resolved_path`` is intentionally
empty for a mismatch so callers cannot accidentally execute an unverified
candidate.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

BOUNDARY_CONTRACT_ID = "skill_manifest_selection"

_RECOVERY = {
    "kind": "refresh-plugin-install",
    "command": "charness update --detail",
    "message": (
        "Refresh the Charness plugin, restart the host session, then resolve "
        "the skill again. Do not run the reported path while this admission is refused."
    ),
}


def _version_key(path: Path) -> tuple[int, ...]:
    values = [int(item) for item in re.findall(r"\d+", path.name)]
    return tuple(values) if values else (0,)


def _cache_candidates(
    codex_home: Path, skill_id: str, marketplace: str, plugin: str
) -> list[tuple[str, Path]]:
    root = codex_home / "plugins" / "cache" / marketplace / plugin
    if not root.is_dir():
        return []
    source = (
        "codex-versioned-cache"
        if (marketplace, plugin) == ("local", "charness")
        else "codex-plugin-cache"
    )
    versions = sorted(
        (item for item in root.iterdir() if item.is_dir()),
        key=lambda item: (_version_key(item), item.stat().st_mtime, item.name),
        reverse=True,
    )
    return [(source, version / "skills" / skill_id / "SKILL.md") for version in versions]


def _owner_root() -> Path:
    """Return the checkout/package root owning this resolver."""

    # Marker walk, not a depth count: this file sits at scripts/adapters/ in the
    # authoring tree and wherever an installed layout copies it.
    return next(
        p for p in Path(__file__).resolve().parents if (p / "scripts" / "adapter_lib.py").is_file()
    )


def _manifest_version(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    value = data.get("version")
    return value if isinstance(value, str) and value else None


def _manifest_error(path: Path) -> str | None:
    """Return a typed error for an existing candidate manifest, if malformed."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return f"unreadable manifest: {exc}"
    if not isinstance(data, dict):
        return "manifest must contain an object"
    version = data.get("version")
    if not isinstance(version, str) or not version:
        return "manifest has no readable version"
    return None


def _candidate_manifest_error(path: Path) -> str | None:
    for parent in (path.parent, *path.parents):
        for manifest in (
            parent / ".codex-plugin" / "plugin.json",
            parent / "plugins" / "charness" / ".codex-plugin" / "plugin.json",
        ):
            error = _manifest_error(manifest)
            if error is not None:
                return f"{manifest}: {error}"
    return None


def _manifest_observation(path: Path) -> tuple[bool, str | None, str | None]:
    """Observe every existing manifest; malformed input is not absence."""
    if not path.exists():
        return False, None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return True, None, f"unreadable manifest: {exc}"
    version = data.get("version") if isinstance(data, dict) else None
    if not isinstance(version, str) or not version:
        return True, None, "manifest has no readable version"
    return True, version, None


def _package_expectation(*, skill_id: str, marketplace: str, plugin: str) -> dict[str, Any]:
    """Build the package-owned version/content expectation.

    Source checkouts have ``skills/public`` and ``plugins/charness/skills``;
    installed plugin roots have only ``skills``.  When both source and export
    are present, disagreement is itself a refusal rather than a choice.
    """

    if (marketplace, plugin) != ("local", "charness"):
        return {
            "status": "unavailable",
            "reason_code": "unsupported-package-expectation",
            "reason": "only the Charness local plugin has a package-owned admission contract",
        }
    root = _owner_root()
    manifest_candidates = [
        root / "plugins" / "charness" / ".codex-plugin" / "plugin.json",
        root / ".codex-plugin" / "plugin.json",
    ]
    observations = {path: _manifest_observation(path) for path in manifest_candidates}
    malformed = [
        (path, observation[2])
        for path, observation in observations.items()
        if observation[0] and observation[2] is not None
    ]
    if malformed:
        return {
            "status": "unavailable",
            "reason_code": "package-manifest-invalid",
            "reason": "an existing Charness manifest is unreadable or malformed",
            "paths": [str(path) for path, _reason in malformed],
            "details": [str(reason) for _path, reason in malformed],
        }
    versions = {version for _path, (_exists, version, _error) in observations.items() if version}
    source_path = root / "skills" / "public" / skill_id / "SKILL.md"
    plugin_path = root / "plugins" / "charness" / "skills" / skill_id / "SKILL.md"
    installed_path = root / "skills" / skill_id / "SKILL.md"
    source_candidates = [
        path for path in (source_path, plugin_path, installed_path) if path.is_file()
    ]
    if not versions:
        return {
            "status": "unavailable",
            "reason_code": "package-version-unavailable",
            "reason": "the Charness plugin manifest has no readable version",
        }
    if len(versions) != 1:
        return {
            "status": "mismatch",
            "reason_code": "package-version-mismatch",
            "reason": "Charness source and plugin manifests disagree on version",
            "versions": sorted(versions),
        }
    if not source_candidates:
        return {
            "status": "unavailable",
            "reason_code": "skill-expectation-unavailable",
            "reason": f"no package-owned SKILL.md exists for `{skill_id}`",
            "version": next(iter(versions)),
        }
    digests = {hashlib.sha256(path.read_bytes()).hexdigest() for path in source_candidates}
    if len(digests) != 1:
        return {
            "status": "mismatch",
            "reason_code": "source-plugin-parity-mismatch",
            "reason": "Charness source and exported skill bytes are not identical",
            "version": next(iter(versions)),
            "paths": [str(path) for path in source_candidates],
            "digests": sorted(digests),
        }
    return {
        "status": "ready",
        "version": next(iter(versions)),
        "skill_sha256": next(iter(digests)),
        "source_path": str(source_candidates[0]),
        "paths": [str(path) for path in source_candidates],
    }


def _candidate_version(path: Path, source: str) -> str | None:
    """Read a candidate's manifest version or infer a versioned cache segment."""

    for parent in (path.parent, *path.parents):
        manifest = parent / ".codex-plugin" / "plugin.json"
        version = _manifest_version(manifest)
        if version:
            return version
        managed_manifest = parent / "plugins" / "charness" / ".codex-plugin" / "plugin.json"
        version = _manifest_version(managed_manifest)
        if version:
            return version
    if source in {"codex-versioned-cache", "codex-plugin-cache"}:
        # .../<plugin>/<version>/skills/<skill>/SKILL.md
        parts = path.parts
        try:
            skills_index = len(parts) - 3
            if parts[skills_index] == "skills":
                return parts[skills_index - 1]
        except (IndexError, ValueError):
            pass
    # The canonical source/public tree itself has no manifest beside SKILL.md.
    # Only paths inside this resolver's own package root may inherit that
    # package version; a consumer's same-named local file must provide its own
    # manifest evidence instead of borrowing ours.
    root = _owner_root()
    canonical_roots = (
        root / "skills" / "public",
        root / "plugins" / "charness" / "skills",
        root / "skills",
    )
    if any(path.is_relative_to(candidate_root) for candidate_root in canonical_roots):
        for manifest in (
            root / "plugins" / "charness" / ".codex-plugin" / "plugin.json",
            root / ".codex-plugin" / "plugin.json",
        ):
            version = _manifest_version(manifest)
            if version:
                return version
    return None


def _candidate_record(source: str, path: Path, expectation: dict[str, Any]) -> dict[str, Any]:
    expanded = path.expanduser().resolve()
    exists = expanded.is_file()
    manifest_error = _candidate_manifest_error(expanded) if exists else None
    observed_version = _candidate_version(expanded, source) if exists else None
    try:
        observed_digest = hashlib.sha256(expanded.read_bytes()).hexdigest() if exists else None
    except OSError:
        observed_digest = None
        exists = False
    mismatch: str | None = None
    if manifest_error is not None:
        mismatch = "package-manifest-invalid"
    elif not exists:
        mismatch = "missing"
    elif expectation.get("status") != "ready":
        mismatch = str(expectation.get("reason_code", "expectation-unavailable"))
    elif observed_version != expectation.get("version"):
        mismatch = "skill-version-mismatch"
    elif observed_digest != expectation.get("skill_sha256"):
        mismatch = "skill-content-mismatch"
    return {
        "source": source,
        "path": str(expanded),
        "exists": exists,
        "observed_version": observed_version,
        "manifest_error": manifest_error,
        "content_sha256": observed_digest,
        "admissible": mismatch is None,
        "mismatch": mismatch,
    }


def resolve_skill_path(
    *,
    skill_id: str,
    repo_root: Path,
    home: Path,
    codex_home: Path,
    reported_path: Path | None,
    marketplace: str = "local",
    plugin: str = "charness",
) -> dict[str, Any]:
    is_charness = (marketplace, plugin) == ("local", "charness")
    candidates: list[tuple[str, Path]] = []
    if reported_path is not None:
        candidates.append(("reported", reported_path))
    if is_charness:
        candidates.extend(
            [
                (
                    "codex-stable-plugin",
                    codex_home / "plugins/charness/skills" / skill_id / "SKILL.md",
                ),
                (
                    "repo-plugin-export",
                    repo_root / "plugins/charness/skills" / skill_id / "SKILL.md",
                ),
                ("repo-public-skill", repo_root / "skills/public" / skill_id / "SKILL.md"),
                ("repo-support-skill", repo_root / "skills/support" / skill_id / "SKILL.md"),
                (
                    "repo-synced-support-skill",
                    repo_root / "skills/support/generated" / skill_id / "SKILL.md",
                ),
            ]
        )
    candidates.extend(_cache_candidates(codex_home, skill_id, marketplace, plugin))
    if is_charness:
        candidates.extend(
            [
                (
                    "managed-checkout-plugin",
                    home / ".agents/src/charness/plugins/charness/skills" / skill_id / "SKILL.md",
                ),
                (
                    "managed-checkout-public",
                    home / ".agents/src/charness/skills/public" / skill_id / "SKILL.md",
                ),
            ]
        )
    expectation = _package_expectation(skill_id=skill_id, marketplace=marketplace, plugin=plugin)
    candidate_records = [
        _candidate_record(source, path, expectation) for source, path in candidates
    ]
    invalid_candidates = [
        record for record in candidate_records if record["mismatch"] == "package-manifest-invalid"
    ]
    admitted = [record for record in candidate_records if record["admissible"]]
    selected = None if invalid_candidates else (admitted[0] if admitted else None)
    resolved_source = selected["source"] if selected else None
    resolved = Path(selected["path"]) if selected else None
    reported_exists = reported_path.expanduser().is_file() if reported_path is not None else None
    reported_record = next(
        (item for item in candidate_records if item["source"] == "reported"), None
    )
    reported_admitted = bool(reported_record and reported_record["admissible"])
    if selected is not None:
        status = (
            "reported-ok"
            if reported_admitted
            else "stale-reported-path"
            if reported_path is not None
            else "ok"
        )
        admission_status = "admitted"
        reason_code = "reported-path-admitted" if reported_admitted else "reported-path-recovered"
    elif invalid_candidates:
        status = "mismatch"
        admission_status = "refused"
        reason_code = "package-manifest-invalid"
    elif expectation.get("status") == "mismatch":
        status = "mismatch"
        admission_status = "refused"
        reason_code = str(expectation.get("reason_code"))
    elif expectation.get("status") != "ready":
        status = "missing"
        admission_status = "refused"
        reason_code = str(expectation.get("reason_code", "skill-expectation-unavailable"))
    elif any(item["exists"] for item in candidate_records):
        status = "mismatch"
        admission_status = "refused"
        reason_code = next(
            (
                item["mismatch"]
                for item in candidate_records
                if item["exists"] and item["mismatch"] == "skill-content-mismatch"
            ),
            next(
                (
                    item["mismatch"]
                    for item in candidate_records
                    if item["exists"] and item["mismatch"] not in {None, "missing"}
                ),
                "skill-content-mismatch",
            ),
        )
    else:
        status = "missing"
        admission_status = "recovery-required"
        reason_code = "skill-missing"
    warnings: list[str] = []
    if reported_path is not None and not reported_admitted and resolved is not None:
        warnings.append(
            "Reported host skill path was not admitted; a current skill path was found."
        )
    if resolved_source in {"codex-versioned-cache", "codex-plugin-cache"}:
        warnings.append(
            "Resolved to a versioned cache path; prefer a stable plugin path when available."
        )
    if resolved is None:
        warnings.append(
            "No installed or repo-local skill path was admitted for the requested skill id."
        )
    next_step = (
        f"Read `{resolved}` and continue from that admitted skill."
        if resolved
        else _RECOVERY["message"]
    )
    return {
        "schema_version": 2,
        "skill_id": skill_id,
        "marketplace": marketplace,
        "plugin": plugin,
        "reported_path": str(reported_path) if reported_path else None,
        "reported_exists": reported_exists,
        "status": status,
        "admission_status": admission_status,
        "reason_code": reason_code,
        "expectation": expectation,
        "resolved_source": resolved_source,
        "resolved_path": str(resolved) if resolved else None,
        "candidates": candidate_records,
        "warnings": warnings,
        "recovery": None if resolved else dict(_RECOVERY),
        "next_step": next_step,
    }
