#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script


class ValidationError(Exception):
    pass


REFERENCE_CONTRACT_SUFFIXES = {".md", ".txt"}


# The checks below are representative contract guards, not prose snapshots.
# Keep selection/routing promises in CORE_CONTRACTS, where the exact phrase must
# stay in SKILL.md. Move detail-heavy, reference-worthy promises to
# PACKAGE_CONTRACTS, where they may live in SKILL.md or references/*. This keeps
# the gate useful during skill compression without forcing SKILL.md to carry an
# ever-growing anchor catalog.
#
# Disciplined pin-deletion test (operator-agreed; piloted on quality, swept
# harness-wide 2026-06-21). A pin earns deletion ONLY when:
#   (a) it FREEZES WORDING — a redundant restatement (a doubled phrase, or a
#       sub-fragment of a sentence) whose rule a SURVIVING pin already proves, so
#       deleting it loses no behavioral proof; or
#   (b) the behavior is OWNED CANONICALLY ELSEWHERE that genuinely fails closed
#       (another gate/validator, a checked-in reference the gate already pins, or
#       always-loaded CLAUDE.md) — prove the owner catches the failure before
#       deleting, never assume it.
# KEEP otherwise. Keep destructive-boundary guards (cautilus point-of-use,
# "Do not push, tag, or announce a release without explicit user confirmation")
# even when owned elsewhere — point-of-use teeth stay. Keep pins that prove a
# distinct behavioral rule or anchor a required Output Shape.
# Deleting a pin removes its row here (and, if it froze DOUBLED prose, distill
# that prose in the SKILL.md). This is JUDGMENT, not a count game: fewer pins is
# not the goal and bulk deletion is a north-star failure signature — the metric
# is concept clarity and genuine-redundancy removal. So it is a documented
# discipline, never a self-classifying gate.
CORE_CONTRACTS: dict[str, tuple[str, ...]] = {
    "skills/public/critique/SKILL.md": (
        "Task-completing repo work always records critique before closeout.",
        "Scale the\npass, not the obligation",
        "When this standalone `critique` skill runs, it always means a fresh bounded\nsubagent review.",
        "There\nis no same-agent or local standalone `critique` variant.",
        "If the host blocks the canonical subagent path before execution, report",
        "- `Execution`",
    ),
    "skills/public/handoff/SKILL.md": (
        "mention-only pickup",
        "Run a bounded misunderstanding critique when the handoff changed materially.",
        "Assume a competent next operator can follow one good link",
        "The handoff should usually contain:",
        "- `Workflow Trigger`",
        "- `Current State`",
        "- `Next Session`",
        "- `Discuss`",
        "- `References`",
    ),
    "skills/public/gather/SKILL.md": (
        "Prefer primary sources.",
        "Refresh in place when the source identity matches.",
        "local files before external summaries",
        "browser-mediated fallback through `agent-browser`",
        "- `Requested Facts`",
        "- `Open Gaps`",
    ),
    "skills/public/create-skill/SKILL.md": (
        "public skill: one user-facing concept",
        "support skill: teaches tool usage without becoming product philosophy",
        "Freeze the current consumer contract before editing an existing public skill",
        "decide whether the slice claims `preserve` or `improve`",
        "name the capability failure before changing the core trigger or behavior contract",
        "run a customer-of-this-skill critique",
        "the customer repo's first prompt before trusting producer-side checks",
        "if an upstream support skill already exists, prefer reference, sync, or a",
        "Treat public-skill frontmatter and generated AGENTS hints as classifier input",
    ),
    "skills/public/spec/SKILL.md": (
        "## Contract Shaping",
        "Choose the lightest honest contract shape.",
        "run success criteria review so future-success claims",
        "call `critique` for non-trivial contract decisions",
        "probe-friendly and visible instead of inventing a user-facing taxonomy choice.",
        "- `Fixed Decisions`",
        "- `Probe Questions`",
        "- `Deferred Decisions`",
        "- `Acceptance Checks`",
        "- `First Implementation Slice`",
    ),
    "skills/public/impl/SKILL.md": (
        "impl adapter resolution and verification survey",
        "risk interrupt planner reports a forced interrupt",
        "best self-verification path before you code and again before you stop",
        "re-read `Fixed Decisions` and named acceptance checks",
        "reflected in the delivered slice or explicitly",
        "Do not call a same-agent review a critique.",
        "plain implementation until the named spec handoff says this slice may",
    ),
    "skills/public/debug/SKILL.md": (
        "classify seam risk explicitly",
        "set the next step to `spec`",
        "structured handoff fields",
        "Do not run critique before the facts needed for diagnosis exist.",
        "before closing task-completing debug work or handing off a repair",
        "- `Seam Risk`",
        "- `Interrupt Decision`",
    ),
    "skills/public/quality/SKILL.md": (
        "When the next quality move is repo-local, deterministic, and low-risk",
        "If you stop short of an obvious repo-owned deterministic gate",
        "Do not stop at producer-side validators alone when the risk is public-skill routing or durable artifact behavior",
        "Before invoking any `cautilus evaluate ...` subcommand, consult the planner-consult contract",
        "route the call through the repo-owned wrapper instead of bare `cautilus evaluate`",
    ),
    "skills/public/setup/SKILL.md": (
        "normalize",
        "AGENTS.md",
        "CLAUDE.md",
        "into one explicit host-facing policy",
        "optional Charness seams",
        "bootstrap-seams.md",
        "runtime ownership",
        "already delegated",
    ),
    "skills/public/issue/SKILL.md": (
        "GitHub is the source of truth for issue identity",
        "context, but they do not select or verify an issue.",
        "`issue resolve [repo] [number|start-end]` resolves one or more issues.",
        "If no selector was supplied, select the newest open GitHub issue through the\n   backend.",
        "unless the user explicitly asks to review first.",
    ),
    "skills/public/narrative/SKILL.md": (
        "map the current source-of-truth surface",
        "rewrite the durable docs so the current story is honest in one place",
        "If the idea is still under-shaped, use `ideation` first.",
        "keep it audience-neutral by default",
        "when the repo adapter declares `brief_template`, use that ordered skeleton",
        "Hand off to `announcement` only when the user explicitly wants human-facing",
    ),
    "skills/public/release/SKILL.md": (
        "maintainer-facing workflow",
        "Choose the lightest honest bump",
        "patch for bug fixes, copy fixes, and behavior repairs",
        "Do not hand-edit generated plugin manifests",
        "Do not push, tag, or announce a release without explicit user confirmation",
        "Every task-completing release slice records critique before closeout.",
    ),
    "skills/public/retro/SKILL.md": (
        "If the user correctly points out a missed issue",
        "`Persisted`: whether the retro was written to a durable artifact",
        "never stop without stating `Persisted: yes: <path>` or `Persisted: no: <reason>`",
        "Trigger a short `session` retro automatically when a user correction exposes a",
    ),
}

PACKAGE_CONTRACTS: dict[str, tuple[str, ...]] = {
    "skills/public/handoff/SKILL.md": (
        "one reference to the owning artifact for metrics, history, or proof detail",
        "always-loaded host instruction surfaces out of `References` by",
    ),
    "skills/public/gather/SKILL.md": (
        "official API/export docs before browser automation",
        # gather-provider.md adapter-slot contract: keep the per-source
        # read-mode boundary and the host-mediated stop-with-explanation
        # promise pinned so silent regressions in the reference are caught.
        "resolves a per-source provider mode from the adapter",
        "Modes that the\nhost does not expose should be declared",
    ),
    "skills/public/create-skill/SKILL.md": (
        "For `evaluator-required` skills, treat maintained scenario coverage and",
        "metadata rich enough to reveal capability kind and supported access modes",
        "express them as manifest readiness checks",
        "If a skill needs the same bootstrap, adapter resolution, artifact upsert, or",
        'python3 "$SKILL_DIR/../quality/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>',
        # Binary Preflight Philosophy — preserves the lazy "declare, detect,
        # ask" contract while allowing the details to move into references.
        "## Binary Preflight Philosophy",
        "Public skills must not silently assume non-baseline binaries",
        "CHARNESS_BASELINE",
        "Preflight is lazy, not eager",
        "CHARNESS_BINARY_PREFLIGHT=degraded",
        "Auto-install is forbidden",
        "Silent skip is forbidden",
    ),
    "skills/public/spec/SKILL.md": (
        "public executable contract",
        "maintenance lint / implementation guard",
        'python3 "$SKILL_DIR/../../../scripts/plan_risk_interrupt.py" --repo-root . --json 2>/dev/null || true',
        "risk interrupt planner reports a forced debug interrupt",
        "`Interrupt Source`, `Seam Summary`, `Chosen Next Step`, `Impl Status`",
    ),
    "skills/public/impl/SKILL.md": (
        'python3 "$SKILL_DIR/../../../scripts/plan_risk_interrupt.py" --repo-root . --json 2>/dev/null || true',
        "$SKILL_DIR/../retro/scripts/check_auto_trigger.py",
        "`Critique: short <scope>`",
        "`Critique: full <artifact-or-subagent-status>`",
        "`Critique: not-applicable <reason>`",
        "`Critique: blocked <host-signal>`",
    ),
    "skills/public/quality/SKILL.md": (
        "$SKILL_DIR/scripts/inventory_public_spec_quality.py",
        "duplicated at the wrong layer",
        'scaffold one consumer-side dogfood case with `python3 "$SKILL_DIR/scripts/suggest_public_skill_dogfood.py" --repo-root . --skill-id <skill-id>`',
    ),
    "skills/public/release/SKILL.md": (
        "`publish_release.py --execute` refuses unless exactly one",
        "`--critique-artifact <path>`",
        "`--critique-blocked <host-signal>`",
        "A refusal leaves the release mutation unstarted.",
    ),
    "skills/public/retro/SKILL.md": (
        "`Trends vs Last Retro`: for `weekly`, compare against the last durable weekly retro when one exists",
        "Only write a weekly snapshot when the adapter gives an explicit `snapshot_path`",
    ),
}

PACKAGE_CONTRACT_SOURCE_PATHS: dict[str, tuple[str, ...]] = {
    "skills/public/release/SKILL.md": (
        "references/critique-boundary.md",
        "scripts/publish_release_preflight.py",
    ),
}

# Backward-compatible rollup for tests and diagnostics that need to copy all
# representative skill files into a fixture repo.
REPRESENTATIVE_CONTRACTS: dict[str, tuple[str, ...]] = {
    rel_path: (*CORE_CONTRACTS.get(rel_path, ()), *PACKAGE_CONTRACTS.get(rel_path, ()))
    for rel_path in sorted({*CORE_CONTRACTS, *PACKAGE_CONTRACTS})
}

FORBIDDEN_SNIPPETS: dict[str, tuple[str, ...]] = {
    "skills/public/critique/SKILL.md": (
        "short bounded local pass",
    ),
    "skills/public/release/SKILL.md": (
        "local critique",
    ),
}


def _package_text(path: Path) -> str:
    if not path.exists():
        raise ValidationError(f"missing representative contract file `{path}`")
    parts = [path.read_text(encoding="utf-8")]
    path_text = path.as_posix()
    active_sources = next(
        (
            sources
            for rel_path, sources in PACKAGE_CONTRACT_SOURCE_PATHS.items()
            if path_text == rel_path or path_text.endswith(f"/{rel_path}")
        ),
        None,
    )
    if active_sources is not None:
        for source in active_sources:
            source_path = path.parent / source
            if not source_path.is_file():
                raise ValidationError(f"missing package contract source `{source_path}`")
            parts.append(source_path.read_text(encoding="utf-8", errors="ignore"))
        return "\n".join(parts)
    references_dir = path.parent / "references"
    if references_dir.is_dir():
        for reference in sorted(references_dir.rglob("*")):
            if reference.is_file() and reference.suffix in REFERENCE_CONTRACT_SUFFIXES:
                parts.append(reference.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def _read_contract_text(path: Path) -> str:
    if not path.exists():
        raise ValidationError(f"missing representative contract file `{path}`")
    return path.read_text(encoding="utf-8")


def _assert_snippet_membership(
    path: Path, contents: str, snippets: tuple[str, ...], *, forbidden: bool, message: str
) -> None:
    violations = [snippet for snippet in snippets if (snippet in contents) == forbidden]
    if violations:
        formatted = ", ".join(f"`{snippet}`" for snippet in violations)
        raise ValidationError(f"{path}: {message}: {formatted}")


def validate_core_contract(path: Path, snippets: tuple[str, ...]) -> None:
    _validate_contract(
        path,
        snippets,
        text_loader=_read_contract_text,
        forbidden=False,
        message="missing required core contract snippet(s)",
    )


def validate_package_contract(path: Path, snippets: tuple[str, ...]) -> None:
    _validate_contract(
        path,
        snippets,
        text_loader=_package_text,
        forbidden=False,
        message="missing required package contract snippet(s)",
    )


def validate_forbidden_snippets(path: Path, snippets: tuple[str, ...]) -> None:
    _validate_contract(
        path,
        snippets,
        text_loader=_read_contract_text,
        forbidden=True,
        message="forbidden contract snippet(s) present",
    )


def _validate_contract(
    path: Path,
    snippets: tuple[str, ...],
    *,
    text_loader,
    forbidden: bool,
    message: str,
) -> None:
    _assert_snippet_membership(path, text_loader(path), snippets, forbidden=forbidden, message=message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=repo_root_from_script(__file__))
    args = parser.parse_args()

    root = args.repo_root.resolve()
    for rel_path, snippets in CORE_CONTRACTS.items():
        validate_core_contract(root / rel_path, snippets)
    for rel_path, snippets in PACKAGE_CONTRACTS.items():
        validate_package_contract(root / rel_path, snippets)
    for rel_path, snippets in FORBIDDEN_SNIPPETS.items():
        validate_forbidden_snippets(root / rel_path, snippets)

    print(
        f"Validated {len(CORE_CONTRACTS)} core skill contracts, "
        f"{len(PACKAGE_CONTRACTS)} package skill contracts, "
        f"and {len(FORBIDDEN_SNIPPETS)} forbidden-snippet rules."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
