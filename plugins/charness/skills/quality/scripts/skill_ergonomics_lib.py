from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import skill_text_quality_lib as tqlib

DEFAULT_REVIEW_TOPIC_PROMPTS = [
    ("concise_core", "Keep `SKILL.md` core concise; push nuance and payload into references or scripts."),
    ("progressive_disclosure_honesty", "Check progressive disclosure honesty: core owns selection and sequencing, references deepen rather than fork the workflow."),
    ("helper_owned_workflow_packet", "If deterministic helpers already know the workflow, consider a planner/report packet instead of keeping gate order as prose."),
    ("concept_split_references", "If a reference carries multiple concepts, split the concepts rather than moving SKILL.md overflow into one larger reference."),
    ("mode_option_pressure", "Treat unnecessary user-facing modes or options as pressure to simplify with stronger defaults and inference."),
    ("trigger_boundary", "Check trigger overlap or undertrigger risk against nearby public skills; a smart model still needs an honest invocation boundary."),
    ("prose_ritual_helper", "When the skill repeats prose ritual, prefer a repo-owned helper script over another paragraph."),
    ("installed_bundle_portability", "Check installed-bundle portability: prose helper paths should not read like cwd-relative runtime commands when `$SKILL_DIR` is required."),
    ("public_core_history_leak", "Keep issue-number and dated incident anchors out of public `SKILL.md` core; move historical provenance to references, tests, or retro artifacts."),
    ("package_history_leak", "Review concrete issue anchors across the whole public/support package; generic issue-workflow placeholders and version fields are not project-history leakage."),
    ("host_surface_reference", "Review dated incident wording, host-surface references, and unlisted reference files as package-level portability signals."),
]
REVIEW_PROMPT_BY_TOPIC = dict(DEFAULT_REVIEW_TOPIC_PROMPTS)
REVIEW_PROMPT_BY_TOPIC["runtime_install_portability"] = (
    "Check runtime-install portability: prose helper paths should match the "
    "worker-resolved skill-installer path, not the harness `$SKILL_DIR` form, "
    "since the runtime worker has no `$SKILL_DIR` in its environment."
)
DEFAULT_REVIEW_TOPIC_IDS = [topic_id for topic_id, _prompt in DEFAULT_REVIEW_TOPIC_PROMPTS]
DEFAULT_REVIEW_PROMPTS = [prompt for _topic_id, prompt in DEFAULT_REVIEW_TOPIC_PROMPTS]
RUNTIME_INSTALL_REVIEW_TOPIC_IDS = [
    "concise_core",
    "progressive_disclosure_honesty",
    "helper_owned_workflow_packet",
    "concept_split_references",
    "mode_option_pressure",
    "runtime_install_portability",
]
RUNTIME_INSTALL_REVIEW_PROMPTS = [
    REVIEW_PROMPT_BY_TOPIC[topic_id] for topic_id in RUNTIME_INSTALL_REVIEW_TOPIC_IDS
]
MODE_TERMS_RE = re.compile(r"\bmode(?:s)?\b", re.IGNORECASE)
OPTION_TERMS_RE = re.compile(r"\boption(?:s)?\b", re.IGNORECASE)
BARE_HELPER_PATH_RE = re.compile(r"`scripts/[A-Za-z0-9._/-]+\.(?:py|sh|bash|zsh|js|ts|rb|pl|lua)`")
SOURCE_TREE_FILE_PATH_RE = re.compile(r"`skills/(?:public|support)/[A-Za-z0-9._-]+/[A-Za-z0-9._/-]+\.(?:md|py|sh|bash|zsh|js|ts|rb|pl|lua|yaml|yml|json)`")
PRESSURE_EXEMPT_H2_SECTIONS = {"Load-Bearing Anchors", "References"}
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def count_files(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(1 for path in directory.rglob("*") if path.is_file())


def remove_pressure_exempt_sections(lines: list[str]) -> list[str]:
    kept: list[str] = []
    skip = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip()
            skip = section in PRESSURE_EXEMPT_H2_SECTIONS
            if skip:
                continue
        if not skip:
            kept.append(line)
    return kept


def has_portable_path_ambiguity(lines: list[str]) -> bool:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- `scripts/"):
            continue
        if "$SKILL_DIR/scripts/" in line or "$SKILL_DIR/../" in line:
            continue
        if BARE_HELPER_PATH_RE.search(line) or SOURCE_TREE_FILE_PATH_RE.search(line):
            return True
    return False


def has_issue_anchor_in_core(lines: list[str]) -> bool:
    return any(tqlib.ISSUE_ANCHOR_RE.search(line) for line in lines)


def has_dated_incident_in_core(lines: list[str]) -> bool:
    return any(tqlib.DATED_INCIDENT_RE.search(line) for line in lines)


def strip_inline_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", text)


def classify_skill_type(relative_skill: Path, is_runtime_install: Callable[[str], bool]) -> str:
    if is_runtime_install(relative_skill.as_posix()):
        return "runtime_install"
    if "support" in relative_skill.parts:
        return "support"
    return "public"


def inventory_skill(
    repo_root: Path,
    skill_path: Path,
    *,
    max_core_lines: int,
    is_runtime_install: Callable[[str], bool],
    markdown_helpers: dict,
) -> dict[str, object]:
    skill_dir = skill_path.parent
    relative_skill = skill_dir.relative_to(repo_root)
    skill_type = classify_skill_type(relative_skill, is_runtime_install)
    body = markdown_helpers["strip_frontmatter"](skill_path.read_text(encoding="utf-8"))
    body_lines = remove_pressure_exempt_sections(body.splitlines())
    nonempty_lines = [line for line in body_lines if line.strip()]
    prose_lines = markdown_helpers["strip_fenced_lines"](body_lines)
    prose = strip_inline_code("\n".join(prose_lines))
    bootstrap_lines = markdown_helpers["extract_h2_section_lines"](body, "Bootstrap")
    code_fence_count = sum(1 for line in body_lines if line.strip().startswith("```"))
    bootstrap_fence_count = markdown_helpers["count_fence_blocks"](bootstrap_lines)
    reference_count = count_files(skill_dir / "references")
    script_count = count_files(skill_dir / "scripts")
    package_issue_findings: list[dict[str, object]] = []
    package_dated_findings: list[dict[str, object]] = []
    host_surface_findings: list[dict[str, object]] = []
    reference_findings: list[dict[str, object]] = []
    if skill_type in {"public", "support"}:
        package_issue_findings = tqlib.issue_anchor_package_findings(repo_root, skill_dir)
        package_dated_findings = tqlib.dated_incident_package_findings(repo_root, skill_dir)
        host_surface_findings = tqlib.host_surface_reference_findings(repo_root, skill_dir)
        reference_findings = tqlib.reference_discoverability_findings(repo_root, skill_path, body)
    heuristics: list[str] = []
    if len(nonempty_lines) > max_core_lines:
        heuristics.append("long_core")
    if reference_count == 0 and script_count == 0 and len(nonempty_lines) > 80:
        heuristics.append("progressive_disclosure_risk")
    if len(MODE_TERMS_RE.findall(prose)) >= 2:
        heuristics.append("mode_pressure_terms_present")
    if len(OPTION_TERMS_RE.findall(prose)) >= 2:
        heuristics.append("option_pressure_terms_present")
    if bootstrap_fence_count >= 3 and script_count == 0:
        heuristics.append("code_fence_without_helper_script")
    if skill_type != "runtime_install" and has_portable_path_ambiguity(prose_lines):
        heuristics.append("portable_helper_path_ambiguity")
    if skill_type == "public" and has_issue_anchor_in_core(prose.splitlines()):
        heuristics.append("issue_anchor_in_core")
    if skill_type == "public" and has_dated_incident_in_core(prose.splitlines()):
        heuristics.append("dated_incident_in_core")
    if skill_type in {"public", "support"} and package_issue_findings:
        heuristics.append("portable_package_issue_anchor")
    if skill_type in {"public", "support"} and package_dated_findings:
        heuristics.append("portable_package_dated_incident")
    if skill_type in {"public", "support"} and host_surface_findings:
        heuristics.append("portable_package_host_surface_reference")
    if skill_type in {"public", "support"} and reference_findings:
        heuristics.append("reference_discoverability_gap")
    subcheck_counts = {
        "core_overfill": 1 if "long_core" in heuristics else 0,
        "mode_option_pressure": (
            int("mode_pressure_terms_present" in heuristics)
            + int("option_pressure_terms_present" in heuristics)
        ),
        "prose_ritual": 1 if "code_fence_without_helper_script" in heuristics else 0,
        "path_ambiguity": 1 if "portable_helper_path_ambiguity" in heuristics else 0,
        "package_issue_anchor": len(package_issue_findings),
        "package_dated_incident": len(package_dated_findings),
        "host_surface_reference": len(host_surface_findings),
        "reference_discoverability": len(reference_findings),
    }
    review_prompts = RUNTIME_INSTALL_REVIEW_PROMPTS if skill_type == "runtime_install" else DEFAULT_REVIEW_PROMPTS
    review_topic_ids = (
        RUNTIME_INSTALL_REVIEW_TOPIC_IDS
        if skill_type == "runtime_install"
        else DEFAULT_REVIEW_TOPIC_IDS
    )
    return {
        "skill_id": skill_dir.name,
        "skill_type": skill_type,
        "skill_path": str(skill_path.relative_to(repo_root)),
        "core_nonempty_lines": len(nonempty_lines),
        "reference_file_count": reference_count,
        "script_file_count": script_count,
        "code_fence_count": code_fence_count,
        "bootstrap_fence_count": bootstrap_fence_count,
        "package_issue_anchor_count": len(package_issue_findings),
        "package_issue_anchor_findings": package_issue_findings,
        "package_dated_incident_count": len(package_dated_findings),
        "package_dated_incident_findings": package_dated_findings,
        "host_surface_reference_count": len(host_surface_findings),
        "host_surface_reference_findings": host_surface_findings,
        "unlisted_reference_count": len(reference_findings),
        "unlisted_reference_files": reference_findings,
        "subcheck_counts": subcheck_counts,
        "heuristics": heuristics,
        "review_topic_ids": review_topic_ids,
        "review_prompts": review_prompts,
    }


def scope_status(scanned: int, requested: list[str], adapter_paths: list[str]) -> dict[str, str]:
    if scanned > 0:
        return {"status": "clean", "scope_status": "scanned"}
    if requested:
        return _scope_status_payload(
            "clean",
            "empty_requested_scope",
            "Explicit --skill-path arguments yielded no SKILL.md files.",
        )
    if not adapter_paths:
        return _scope_status_payload(
            "unconfigured",
            "unconfigured_no_skill_surface",
            "skill_ergonomics_skill_paths is empty in quality-adapter.yaml; no SKILL.md files were found at default fallback paths skills/, skills/public/, or skills/support/.",
        )
    return _scope_status_payload(
        "unconfigured",
        "configured_scope_empty",
        "skill_ergonomics_skill_paths in quality-adapter.yaml resolved to no SKILL.md files.",
    )


def _scope_status_payload(status: str, scope_status_name: str, reason: str) -> dict[str, str]:
    return {"status": status, "scope_status": scope_status_name, "reason": reason}


def prose_review_advisory(status: str) -> list[dict[str, str]]:
    if status == "required":
        return [_prose_advisory(
            "skill_ergonomics_prose_review_required",
            "Heuristic findings are present; a human/model prose review result is still required before quality closeout.",
            "Record an explicit prose review result that covers trigger boundaries, progressive disclosure, and judgment-only skill risks.",
        )]
    if status == "still_required":
        return [_prose_advisory(
            "skill_ergonomics_prose_review_still_required",
            "No heuristic findings were found, but the inventory is not a substitute for prose review.",
            "Record an explicit prose review result or state why the prose review is out of scope for this quality pass.",
        )]
    return []


def _prose_advisory(advisory_id: str, message: str, next_action_text: str) -> dict[str, str]:
    return {"advisory_id": advisory_id, "message": message, "next_action": next_action_text}


def finding_status(skills: list[dict[str, object]]) -> dict[str, object]:
    heuristic_count = sum(len(skill.get("heuristics", [])) for skill in skills)
    subcheck_counts: dict[str, int] = {}
    for skill in skills:
        for name, count in dict(skill.get("subcheck_counts", {})).items():
            subcheck_counts[name] = subcheck_counts.get(name, 0) + int(count)
    package_issue_anchor_count = subcheck_counts.get("package_issue_anchor", 0)
    if not skills:
        return {
            "checked_skill_count": 0,
            "heuristic_finding_count": 0,
            "package_issue_anchor_count": 0,
            "subcheck_counts": {},
            "finding_status": "not_evaluated",
            "prose_review_status": "not_started",
            "advisories": [],
        }
    if heuristic_count:
        prose_status = "required"
        return {
            "checked_skill_count": len(skills),
            "heuristic_finding_count": heuristic_count,
            "package_issue_anchor_count": package_issue_anchor_count,
            "subcheck_counts": subcheck_counts,
            "finding_status": "heuristics_present",
            "prose_review_status": prose_status,
            "advisories": prose_review_advisory(prose_status),
        }
    prose_status = "still_required"
    return {
        "checked_skill_count": len(skills),
        "heuristic_finding_count": 0,
        "package_issue_anchor_count": package_issue_anchor_count,
        "subcheck_counts": subcheck_counts,
        "finding_status": "zero_heuristic_findings",
        "prose_review_status": prose_status,
        "advisories": prose_review_advisory(prose_status),
    }
