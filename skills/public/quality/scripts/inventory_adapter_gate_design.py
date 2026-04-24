#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

FINDING_CLASSES = {
    "structural_fact",
    "contextual_recommendation",
    "acknowledgement_gap",
    "migration_gap",
    "brittle_hard_gate_smell",
}
ENFORCEMENT_TIERS = {"AUTO_EXISTING", "AUTO_CANDIDATE", "NON_AUTOMATABLE"}
QUALITY_ADAPTER_CANDIDATES = (
    Path(".agents/quality-adapter.yaml"),
    Path(".codex/quality-adapter.yaml"),
    Path(".claude/quality-adapter.yaml"),
    Path("docs/quality-adapter.yaml"),
    Path("quality-adapter.yaml"),
)
DEFAULT_REVIEW_GLOBS = (
    ".agents/*-adapter.yaml",
    "skills/public/*/adapter.example.yaml",
    "scripts/*.py",
)


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _finding(
    *,
    finding_id: str,
    path: str,
    finding_class: str,
    tier: str,
    confidence: str,
    evidence: list[str],
    suggested_action: str,
) -> dict[str, object]:
    return {
        "id": finding_id,
        "path": path,
        "finding_class": finding_class,
        "enforcement_tier": tier,
        "confidence": confidence,
        "evidence": evidence,
        "suggested_action": suggested_action,
    }


def _top_level_string_list(text: str, field: str) -> list[str]:
    lines = text.splitlines()
    values: list[str] = []
    for index, raw in enumerate(lines):
        if raw.strip() in {f"{field}: []", f"{field}: []"}:
            return []
        if raw.strip() != f"{field}:":
            continue
        for nested in lines[index + 1 :]:
            if nested and not nested.startswith((" ", "\t", "-")):
                break
            stripped = nested.strip()
            if not stripped or not stripped.startswith("- "):
                continue
            values.append(stripped[2:].strip().strip("'\""))
        return values
    return []


def _review_globs(repo_root: Path) -> tuple[list[str], str]:
    adapter_path = next((repo_root / candidate for candidate in QUALITY_ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        return list(DEFAULT_REVIEW_GLOBS), "default"
    text = adapter_path.read_text(encoding="utf-8", errors="replace")
    configured = [
        *_top_level_string_list(text, "adapter_review_sources"),
        *_top_level_string_list(text, "gate_design_review_globs"),
    ]
    return (configured, _relative(adapter_path, repo_root)) if configured else (list(DEFAULT_REVIEW_GLOBS), "default")


def _review_paths(repo_root: Path) -> tuple[list[Path], str]:
    globs, source = _review_globs(repo_root)
    paths: list[Path] = []
    for pattern in globs:
        matches = sorted(repo_root.glob(pattern))
        paths.extend(path for path in matches if path.is_file())
    unique = sorted({path.resolve(): path for path in paths}.values())
    return unique, source


def _inventory_adapter(path: Path, repo_root: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = _relative(path, repo_root)
    findings: list[dict[str, object]] = []
    if "version:" not in text:
        findings.append(
            _finding(
                finding_id="adapter.version_missing",
                path=rel,
                finding_class="structural_fact",
                tier="AUTO_EXISTING",
                confidence="high",
                evidence=["adapter has no version field"],
                suggested_action="Add a version field or remove the stale adapter surface.",
            )
        )
    if rel.endswith("quality-adapter.yaml") or rel.endswith("quality/adapter.example.yaml"):
        missing = [
            field
            for field in (
                "recommendation_defaults_version",
                "adapter_review_sources",
                "acknowledged_recommendations",
                "gate_design_review_globs",
            )
            if field not in text
        ]
        if missing:
            findings.append(
                _finding(
                    finding_id="quality_adapter.review_fields_missing",
                    path=rel,
                    finding_class="migration_gap",
                    tier="AUTO_CANDIDATE",
                    confidence="medium",
                    evidence=[f"missing fields: {', '.join(missing)}"],
                    suggested_action="Resolve quality adapters with safe empty review defaults, then backfill examples.",
                )
            )
    has_acknowledgement_items = re.search(
        r"acknowledged(?:_recommendations)?[ \t]*:[ \t]*\n[ \t]*-[ \t]+",
        text,
    ) is not None
    if has_acknowledgement_items and "reason" not in text:
        findings.append(
            _finding(
                finding_id="adapter.acknowledgement_reason_missing",
                path=rel,
                finding_class="acknowledgement_gap",
                tier="NON_AUTOMATABLE",
                confidence="low",
                evidence=["adapter contains acknowledgement-like state without an adjacent reason"],
                suggested_action="Review whether acknowledgements should include rationale before suppressing recommendations.",
            )
        )
    return findings


def _inventory_script(path: Path, repo_root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = _relative(path, repo_root)
    if "FRESH_EYE_MARKERS" in text or "missing_required_snippets" in text:
        findings.append(
            _finding(
                finding_id="script.brittle_review_phrase_detector",
                path=rel,
                finding_class="brittle_hard_gate_smell",
                tier="NON_AUTOMATABLE",
                confidence="medium",
                evidence=["script includes phrase-detector review policy terms"],
                suggested_action="Keep phrase detectors advisory unless adapter policy sources make the recommendation reviewable.",
            )
        )
    if "recommendations" in text and "enforcement_tier" in text:
        findings.append(
            _finding(
                finding_id="script.review_queue_present",
                path=rel,
                finding_class="contextual_recommendation",
                tier="AUTO_CANDIDATE",
                confidence="medium",
                evidence=["script emits recommendation-like records with enforcement tier"],
                suggested_action="Keep review queues structured and validate their artifact consumers.",
            )
        )
    return findings


def inventory(repo_root: Path) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    review_paths, scope_source = _review_paths(repo_root)
    for path in review_paths:
        if path.name.endswith("-adapter.yaml") or path.name == "adapter.example.yaml":
            findings.extend(_inventory_adapter(path, repo_root))
        elif path.suffix == ".py":
            findings.extend(_inventory_script(path, repo_root))
    return {
        "repo": repo_root.name,
        "review_scope_source": scope_source,
        "reviewed_paths": [_relative(path, repo_root) for path in review_paths],
        "finding_classes": sorted(FINDING_CLASSES),
        "enforcement_tiers": sorted(ENFORCEMENT_TIERS),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    payload = inventory(args.repo_root.resolve())
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
