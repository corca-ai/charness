from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

DEFAULT_REVIEW_PROMPTS = [
    "Keep `SKILL.md` core concise; push nuance and payload into references or scripts.",
    "Check progressive disclosure honesty: core owns selection and sequencing, references deepen rather than fork the workflow.",
    "Treat unnecessary user-facing modes or options as pressure to simplify with stronger defaults and inference.",
    "Check trigger overlap or undertrigger risk against nearby public skills; a smart model still needs an honest invocation boundary.",
    "When the skill repeats prose ritual, prefer a repo-owned helper script over another paragraph.",
    "Check installed-bundle portability: prose helper paths should not read like cwd-relative runtime commands when `$SKILL_DIR` is required.",
    "Keep issue-number and dated incident anchors out of public `SKILL.md` core; move historical provenance to references, tests, or retro artifacts.",
    "Review concrete issue anchors across the whole public/support package; generic issue-workflow placeholders and version fields are not project-history leakage.",
]
RUNTIME_INSTALL_REVIEW_PROMPTS = [
    "Keep `SKILL.md` core concise; push nuance and payload into references or scripts.",
    "Check progressive disclosure honesty: core owns selection and sequencing, references deepen rather than fork the workflow.",
    "Treat unnecessary user-facing modes or options as pressure to simplify with stronger defaults and inference.",
    "Check runtime-install portability: prose helper paths should match the worker-resolved skill-installer path, not the harness `$SKILL_DIR` form, since the runtime worker has no `$SKILL_DIR` in its environment.",
]
MODE_TERMS_RE = re.compile(r"\bmode(?:s)?\b", re.IGNORECASE)
OPTION_TERMS_RE = re.compile(r"\boption(?:s)?\b", re.IGNORECASE)
BARE_HELPER_PATH_RE = re.compile(r"`scripts/[A-Za-z0-9._/-]+\.(?:py|sh|bash|zsh|js|ts|rb|pl|lua)`")
SOURCE_TREE_FILE_PATH_RE = re.compile(r"`skills/(?:public|support)/[A-Za-z0-9._-]+/[A-Za-z0-9._/-]+\.(?:md|py|sh|bash|zsh|js|ts|rb|pl|lua|yaml|yml|json)`")
ISSUE_ANCHOR_RE = re.compile(
    r"(?:"
    r"\b[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+\b|"
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+\b|"
    r"\bissues/\d+\b|"
    r"\bissue-\d+\b|"
    r"\b(?:issue|bug|pr|pull request)s?\s+#\d+\b|"
    r"(?<![A-Za-z0-9_])#\d{3,}\b"
    r")",
    re.IGNORECASE,
)
DATED_INCIDENT_RE = re.compile(
    r"(?:20\d{2}-\d{2}-\d{2}.{0,80}\b(?:incident|miss|regression|trap|failure|bug|closeout|lesson)s?\b|"
    r"\b(?:incident|miss|regression|trap|failure|bug|closeout|lesson)s?\b.{0,80}20\d{2}-\d{2}-\d{2})",
    re.IGNORECASE,
)
PRESSURE_EXEMPT_H2_SECTIONS = {"Load-Bearing Anchors", "References"}
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
PACKAGE_TEXT_SUFFIXES = {
    ".bash",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}
PACKAGE_TEXT_FILENAMES = {"SKILL.md"}
ISSUE_VERSION_FIELD_RE = re.compile(r"defaults_version\b.*\bissue-\d+\b", re.IGNORECASE)
PLACEHOLDER_ISSUE_URL_RE = re.compile(r"\.\.\./issues/\d+\b")


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
    return any(ISSUE_ANCHOR_RE.search(line) for line in lines)


def _is_package_text_file(path: Path) -> bool:
    return path.name in PACKAGE_TEXT_FILENAMES or path.suffix in PACKAGE_TEXT_SUFFIXES


def _iter_package_text_files(skill_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in skill_dir.rglob("*")
        if path.is_file()
        and _is_package_text_file(path)
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
    )


def _excerpt(line: str) -> str:
    return line.strip()[:160]


def is_allowed_issue_anchor_context(line: str) -> bool:
    return bool(ISSUE_VERSION_FIELD_RE.search(line) or PLACEHOLDER_ISSUE_URL_RE.search(line))


def issue_anchor_package_findings(repo_root: Path, skill_dir: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in _iter_package_text_files(skill_dir):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines, start=1):
            if not ISSUE_ANCHOR_RE.search(line):
                continue
            if is_allowed_issue_anchor_context(line):
                continue
            findings.append(
                {
                    "heuristic": "portable_package_issue_anchor",
                    "path": str(path.relative_to(repo_root)),
                    "line": index,
                    "excerpt": _excerpt(line),
                }
            )
    return findings


def has_dated_incident_in_core(lines: list[str]) -> bool:
    return any(DATED_INCIDENT_RE.search(line) for line in lines)


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
    package_issue_findings = (
        issue_anchor_package_findings(repo_root, skill_dir)
        if skill_type in {"public", "support"}
        else []
    )
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
    review_prompts = RUNTIME_INSTALL_REVIEW_PROMPTS if skill_type == "runtime_install" else DEFAULT_REVIEW_PROMPTS
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
        "heuristics": heuristics,
        "review_prompts": review_prompts,
    }


def scope_status(scanned: int, requested: list[str], adapter_paths: list[str]) -> dict[str, str]:
    if scanned > 0:
        return {"status": "clean", "scope_status": "scanned"}
    if requested:
        return {
            "status": "clean",
            "scope_status": "empty_requested_scope",
            "reason": "Explicit --skill-path arguments yielded no SKILL.md files.",
        }
    if not adapter_paths:
        return {
            "status": "unconfigured",
            "scope_status": "unconfigured_no_skill_surface",
            "reason": "skill_ergonomics_skill_paths is empty in quality-adapter.yaml; no SKILL.md files were found at default fallback paths skills/, skills/public/, or skills/support/.",
        }
    return {
        "status": "unconfigured",
        "scope_status": "configured_scope_empty",
        "reason": "skill_ergonomics_skill_paths in quality-adapter.yaml resolved to no SKILL.md files.",
    }


def prose_review_advisory(status: str) -> list[dict[str, str]]:
    if status == "required":
        return [
            {
                "advisory_id": "skill_ergonomics_prose_review_required",
                "message": "Heuristic findings are present; a human/model prose review result is still required before quality closeout.",
                "next_action": "Record an explicit prose review result that covers trigger boundaries, progressive disclosure, and judgment-only skill risks.",
            }
        ]
    if status == "still_required":
        return [
            {
                "advisory_id": "skill_ergonomics_prose_review_still_required",
                "message": "No heuristic findings were found, but the inventory is not a substitute for prose review.",
                "next_action": "Record an explicit prose review result or state why the prose review is out of scope for this quality pass.",
            }
        ]
    return []


def finding_status(skills: list[dict[str, object]]) -> dict[str, object]:
    heuristic_count = sum(len(skill.get("heuristics", [])) for skill in skills)
    package_issue_anchor_count = sum(int(skill.get("package_issue_anchor_count", 0)) for skill in skills)
    if not skills:
        return {
            "checked_skill_count": 0,
            "heuristic_finding_count": 0,
            "package_issue_anchor_count": 0,
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
            "finding_status": "heuristics_present",
            "prose_review_status": prose_status,
            "advisories": prose_review_advisory(prose_status),
        }
    prose_status = "still_required"
    return {
        "checked_skill_count": len(skills),
        "heuristic_finding_count": 0,
        "package_issue_anchor_count": package_issue_anchor_count,
        "finding_status": "zero_heuristic_findings",
        "prose_review_status": prose_status,
        "advisories": prose_review_advisory(prose_status),
    }
