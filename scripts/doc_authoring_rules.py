#!/usr/bin/env python3
"""The doc-authoring RULES, rendered with no target to check.

`check_doc_authoring_preflight.py` forecasts the constraints on a document you
have already written. This module answers the other half of the same question --
what are the constraints, before a line exists -- which is what its two sibling
preflights already do (`describe_goal_closeout_shape.py` with no `--goal-path`,
`check_skill_surface_preflight.py` describing by default). The general-docs
surface was the only one that could not, so an author met a rule only by
breaking it first and one rework cycle was structurally guaranteed.

Every rule here is RENDERED, never restated. Each row is the owning validator's
own constant, or the verdict that validator returns when this module PROBES it
with a sample. A rule that changes upstream changes here; a rule deleted
upstream stops being printed. There is no second copy of any rule text.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_preflight = import_repo_module(__file__, "scripts.check_doc_authoring_preflight")
_doc_links = import_repo_module(__file__, "scripts.check_doc_links")
_inline_code = import_repo_module(__file__, "scripts.check_markdown_inline_code")
_handoff = import_repo_module(__file__, "scripts.validate_handoff_artifact")
_markdown_scan = import_repo_module(__file__, "scripts.markdown_doc_scan")

# Re-exported so a caller catches the class THIS module actually raises. Run as
# `__main__`, the preflight script defines its own copy of the exception, and a
# caller catching that copy would miss the one raised through this import path.
PreflightError = _preflight.PreflightError

_PROBE_DOC_NAME = "<doc-authoring-preflight-probe>.md"


def _probe_doc(repo_root: Path) -> Path:
    """A path that is never created: only its PARENT is used, to resolve the
    relative-link probes the way a repo-root-level document would."""
    return repo_root / _PROBE_DOC_NAME


def _strip_doc_prefix(message: str, doc: Path) -> str:
    prefix = f"{doc}: "
    return message[len(prefix):] if message.startswith(prefix) else message


def collect_link_shape_rules(repo_root: Path, sample: str) -> list[dict[str, Any]]:
    """Render the link-form rule by asking `validate_link` about each shape.

    The shape vocabulary comes from `markdown_doc_scan.classify_link_shape`, and
    the verdict is the gate's own message (or `ok`), so this cannot disagree with
    the gate about which forms are accepted.
    """
    doc = _probe_doc(repo_root)
    rows: list[dict[str, Any]] = []
    for target in (f"./{sample}", sample, f"/{sample}", "./no-such-file.md"):
        try:
            _doc_links.validate_link(repo_root, doc, target)
            verdict = "ok"
        except _doc_links.ValidationError as exc:
            verdict = _strip_doc_prefix(str(exc), doc)
        rows.append(
            {
                "target": target,
                "shape": _markdown_scan.classify_link_shape(target),
                "verdict": verdict,
            }
        )
    return rows


def _portable_package_probe(known_repo: set[str]) -> tuple[Path, Path] | None:
    """A live portable skill package to classify a token INSIDE.

    The tree-marker rule (`unmarked-tree` / `portable-absolute`) fires only
    within a portable package, so a probe that always passes
    `portable_package_root=None` can never render it -- and that is the class
    whose mis-remediation costs two gate cycles.
    """
    for rel in sorted(known_repo):
        parts = Path(rel).parts
        if len(parts) >= 4 and parts[0] == "skills" and parts[1] in _doc_links.PORTABLE_SKILL_KINDS:
            package_relative = Path(*parts[:3])
            return package_relative, package_relative
    return None


def collect_backtick_rules(repo_root: Path, sample: str) -> list[dict[str, Any]]:
    """Render the backticked-file-reference rule by classifying live tokens.

    The reason tags and the remedy sentence are the gate's own
    (`classify_backtick_token`, `TREE_MARKER_REMEDY` / `LINK_FORM_REMEDY`).
    """
    _root, known_repo, unique_basename, known_dirs, canonical = _preflight._doc_link_indices(repo_root)
    probes: list[tuple[str, tuple[Path, Path] | None]] = [
        (sample, None),
        (f"./{Path(sample).parent.as_posix()}", None),
        ("not-a-repo-path", None),
    ]
    probes.extend((token, None) for token in sorted(canonical)[:1])
    package = _portable_package_probe(known_repo)
    if package is not None:
        probes.append((sample, package))
    rows: list[dict[str, Any]] = []
    for token, package_probe in probes:
        package_root, package_root_relative = package_probe or (None, None)
        reason = _doc_links.classify_backtick_token(
            token, known_repo, unique_basename, known_dirs, canonical,
            package_root, package_root_relative,
        )
        remedy = None
        if reason is not None:
            remedy = (
                _doc_links.TREE_MARKER_REMEDY
                if reason in _doc_links.TREE_MARKER_REASONS
                else _doc_links.LINK_FORM_REMEDY
            )
        rows.append({
            "token": token,
            "reason": reason,
            "remedy": remedy,
            "inside_package": None if package_probe is None else package_root_relative.as_posix(),
        })
    return rows


def collect_reference_form_rules() -> list[dict[str, Any]]:
    """The two remaining `check_doc_links` classes, rendered from its own remedy
    constants: a bare internal markdown ref in prose, and a documented command
    naming a script that does not exist. Both block a doc that never contained a
    backtick or a link."""
    return [
        {"kind": "bare-internal-ref", "remedy": _doc_links.BARE_INTERNAL_REF_REMEDY},
        {"kind": "unresolved-command-target", "remedy": _doc_links.MISSING_COMMAND_TARGET_REMEDY},
    ]


def collect_inline_code_rules() -> list[dict[str, Any]]:
    """Render the inline-code rule by running the real checker on a sample that
    breaks both of its classes, so the reason tags are the checker's own."""
    sample = "a `span that\nwraps a line` here, and one `odd backtick\n"
    return [
        {"line": lineno, "snippet": snippet, "reason": reason}
        for lineno, snippet, reason in _inline_code.find_inline_code_violations(sample)
    ]


def collect_length_rule(repo_root: Path, as_surface: str | None) -> dict[str, Any]:
    surfaces = _preflight._length_surfaces(repo_root)
    surface = _preflight._resolve_length_surface(repo_root, "", as_surface) if as_surface else None
    known = [s.name for s in surfaces]
    if surface is None:
        return {"surface": None, "cap": None, "counted_by": None, "known_surfaces": known}
    module = _preflight._surface_module(surface)
    return {
        "surface": surface.name,
        "cap": int(getattr(module, surface.constant)),
        "counted_by": surface.count_attr or "raw file lines",
        "label": surface.label,
        "source": f"{surface.module}.{surface.constant}",
        "known_surfaces": known,
    }


def _regenerable_verdict() -> str | None:
    """The rule sentence the handoff validator itself raises, obtained by giving
    it a document that breaks the rule. The rationale (`a fact a command can
    regenerate goes stale in place`) lives only inside that message, so writing a
    headline here instead would be the one restatement in this module."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as handle:
        handle.write("# Probe\n\nShipped in v1.2.3 today.\n")
        probe = Path(handle.name)
    try:
        _handoff.validate_no_regenerable_facts(probe)
    except _handoff.ValidationError as exc:
        return str(exc)
    finally:
        probe.unlink(missing_ok=True)
    return None


def collect_regenerable_rules(repo_root: Path, as_surface: str | None) -> dict[str, Any]:
    """The literal classes the handoff validator refuses, rendered from its own
    `REGENERABLE_PATTERNS` table. Scoped to the surface that enforces them."""
    if (as_surface or "") != "handoff":
        return {"verdict": None, "classes": []}
    return {
        "verdict": _regenerable_verdict(),
        "classes": [
            {"label": label, "replacement": replacement}
            for _pattern, label, replacement in _handoff.REGENERABLE_PATTERNS
        ],
    }


def _probe_sample(repo_root: Path) -> str | None:
    """A real repo-relative path to probe the classifiers with.

    This module's own path, when it is vendored inside the target repo -- a
    sample that cannot rot, because it is the file doing the asking. A consuming
    repo running an out-of-tree copy falls back to its first tracked path-shaped
    file, so the probes still classify something REAL. Returns None when the repo
    offers neither: inventing a path here would render every link verdict as
    `broken relative link`, teaching an author that no link form is accepted.
    """
    try:
        return Path(__file__).resolve().relative_to(repo_root).as_posix()
    except ValueError:
        _root, known_repo, *_rest = _preflight._doc_link_indices(repo_root)
        tracked = sorted(p for p in known_repo if "/" in p and "." in p.rsplit("/", 1)[1])
        return tracked[0] if tracked else None


def build_rules(repo_root: Path, as_surface: str | None) -> dict[str, Any]:
    sample = _probe_sample(repo_root)
    return {
        "mode": "rules",
        "surface": as_surface,
        "probe_sample": sample,
        "length": collect_length_rule(repo_root, as_surface),
        "regenerable_facts": collect_regenerable_rules(repo_root, as_surface),
        "link_shapes": collect_link_shape_rules(repo_root, sample) if sample else [],
        "backticked_refs": collect_backtick_rules(repo_root, sample) if sample else [],
        "reference_forms": collect_reference_form_rules(),
        "inline_code": collect_inline_code_rules(),
        "markdownlint": {"available": _preflight._resolve_markdownlint_cmd() is not None},
    }


def format_rules_human(rules: dict[str, Any]) -> str:
    surface = rules["surface"]
    lines = [
        "doc-authoring-preflight: RULES"
        + (f" for surface `{surface}`" if surface else " (no surface selected)")
    ]

    length = rules["length"]
    if length["surface"] is None:
        known = ", ".join(length["known_surfaces"]) or "(none)"
        lines.append(f"length: no capped surface selected; pass --as-surface <{known}>")
    else:
        lines.append(
            f"length: <= {length['cap']} lines on the {length['label']}, "
            f"counted by {length['counted_by']} (live from {length['source']})"
        )

    regenerable = rules["regenerable_facts"]
    if regenerable["classes"]:
        # No verdict means the probe stopped tripping the rule (a class narrowed
        # or dropped upstream). Render the classes alone rather than the literal
        # word `None` above three correct rows.
        if regenerable["verdict"]:
            lines.append(f"regenerable-facts: {regenerable['verdict']}")
        else:
            lines.append("regenerable-facts: the classes this surface refuses")
        for row in regenerable["classes"]:
            lines.append(f"  - {row['label']}: carry the command instead: {row['replacement']}")
    else:
        lines.append("regenerable-facts: no literal class is refused on this surface")

    if rules["probe_sample"] is None:
        lines.append(
            "link form / backticked file references: not probed -- this repo has no "
            "tracked path-shaped file to classify, and an invented one would teach the wrong rule"
        )
    else:
        lines.append("link form:")
        for row in rules["link_shapes"]:
            lines.append(f"  - `{row['target']}` ({row['shape']}): {row['verdict']}")

        lines.append("backticked file references:")
        for row in rules["backticked_refs"]:
            where = f" inside `{row['inside_package']}`" if row["inside_package"] else ""
            if row["reason"] is None:
                lines.append(f"  - `{row['token']}`{where}: allowed as written")
            else:
                lines.append(f"  - `{row['token']}`{where} ({row['reason']}): {row['remedy']}")

    lines.append("other reference forms:")
    for row in rules["reference_forms"]:
        lines.append(f"  - {row['kind']}: {row['remedy']}")

    lines.append("inline code:")
    for row in rules["inline_code"]:
        lines.append(f"  - {row['reason']}: a span like ...{row['snippet']}... is refused")

    if not rules["markdownlint"]["available"]:
        lines.append("markdownlint: binary unavailable here; the markdown gate still runs it")
    else:
        lines.append("markdownlint: run with --path <draft> to forecast the rule findings")

    lines.append(
        "(rules only -- pass --path <draft.md> to check a real target against them.)"
    )
    return "\n".join(lines)


