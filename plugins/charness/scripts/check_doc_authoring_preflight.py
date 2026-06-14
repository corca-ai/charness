#!/usr/bin/env python3
"""Aggregate author-time preflight for general doc/markdown surfaces.

Given a target ``docs/**/*.md`` (or the handoff artifact), forecast in ONE pass
the deterministic constraints an author otherwise discovers by failing one
commit gate at a time:

  - markdownlint-cli2 rules (``MD004`` list-marker style, trailing space, ...),
    the same engine and config the markdown gate runs;
  - wrapped inline-code spans (a single-backtick span that breaks across a
    newline), via ``check_markdown_inline_code``;
  - doc-link / pathy-ref form (relative-link form, bare internal markdown refs,
    backticked file references), via ``check_doc_links``;
  - the surface length cap (e.g. the handoff artifact's line cap), read live
    from the owning validator's constant.

It REUSES each real validator -- it never forks their logic, so the forecast
cannot drift from what the gate enforces. This mirrors the SKILL.md one-shot
preflight (``check_skill_surface_preflight.py --run-checks``) and the
goal-closeout describe-first preflight (``describe_goal_closeout_shape.py``),
extended to the general-docs surface class those two do not cover.

It is an AFFORDANCE, not a gate: a doc still commits without it, and the
existing gates (``check_doc_links.py``, ``check-markdown.sh``, the artifact
length validators) stay the enforcement. It is intentionally absent from the
blocking commit-gate plan; a non-blocking guard test keeps it that way.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_doc_links = import_repo_module(__file__, "scripts.check_doc_links")
_inline_code = import_repo_module(__file__, "scripts.check_markdown_inline_code")
_handoff = import_repo_module(__file__, "scripts.validate_handoff_artifact")
_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")

# A markdownlint-cli2 per-violation line: ``<file>:<line>[:<col>] error MDxxx/rule desc``.
_MARKDOWNLINT_LINE_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+)(?::(?P<col>\d+))?\s+(?:error\s+)?(?P<rule>MD\d+)/(?P<name>\S+)\s*(?P<desc>.*)$"
)


class PreflightError(Exception):
    pass


@dataclass(frozen=True)
class LengthSurface:
    """A doc surface that carries an enforced line cap.

    ``module``/``constant`` name the OWNING validator's live cap constant so the
    forecast reads the same number the gate enforces (no hand-copied limit), and
    ``matches`` resolves the surface from a repo-relative path.
    """

    name: str
    module: str
    constant: str
    label: str
    matches: Callable[[str], bool]


def _handoff_rel(repo_root: Path) -> str | None:
    try:
        adapter = _handoff.load_adapter(repo_root)
    except Exception:  # noqa: BLE001 -- a missing/broken adapter just means "no handoff surface here"
        return None
    rel = adapter.get("artifact_path")
    return Path(rel).as_posix() if rel else None


def _length_surfaces(repo_root: Path) -> tuple[LengthSurface, ...]:
    handoff_rel = _handoff_rel(repo_root)
    surfaces: list[LengthSurface] = []
    if handoff_rel is not None:
        surfaces.append(
            LengthSurface(
                name="handoff",
                module="scripts.validate_handoff_artifact",
                constant="MAX_ARTIFACT_LINES",
                label="handoff artifact",
                matches=lambda rel, _h=handoff_rel: rel == _h,
            )
        )
    return tuple(surfaces)


def _resolve_length_surface(
    repo_root: Path, rel: str, as_surface: str | None
) -> LengthSurface | None:
    surfaces = _length_surfaces(repo_root)
    if as_surface is not None:
        match = next((s for s in surfaces if s.name == as_surface), None)
        if match is None:
            known = ", ".join(s.name for s in surfaces) or "(none)"
            raise PreflightError(f"unknown --as-surface {as_surface!r}; known capped surfaces: {known}")
        return match
    return next((s for s in surfaces if s.matches(rel)), None)


def _surface_cap(repo_root: Path, surface: LengthSurface) -> int:
    module = import_repo_module(__file__, surface.module)
    return int(getattr(module, surface.constant))


# --- per-class collectors (each reuses the owning validator, no fork) --------


def _resolve_markdownlint_cmd() -> list[str] | None:
    """Mirror ``check-markdown.sh``: prefer the ``markdownlint-cli2`` binary, then
    ``npm exec``. Returns None when neither is available."""
    if shutil.which("markdownlint-cli2"):
        return ["markdownlint-cli2"]
    if shutil.which("npm"):
        return ["npm", "exec", "--", "markdownlint-cli2"]
    return None


def collect_markdownlint(repo_root: Path, rel: str) -> dict[str, Any]:
    """Run markdownlint-cli2 on the single target file, parsing its findings.

    The same engine + ``.markdownlint-cli2.jsonc`` config the markdown gate uses
    (config is auto-discovered from ``repo_root``). markdownlint-cli2 writes the
    banner to stdout and per-violation lines to stderr; scan both for the target.

    Single-file scope (``--no-globs rel``) is verdict-equivalent to the gate's
    full-list lint because every markdownlint rule in the repo config is
    per-file; a hypothetical cross-file rule (e.g. link-reciprocity) would need
    this to widen to the linked set.
    """
    cmd = _resolve_markdownlint_cmd()
    if cmd is None:
        return {"available": False, "findings": []}
    proc = subprocess.run(
        [*cmd, "--no-globs", rel],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    findings: list[dict[str, Any]] = []
    for stream in (proc.stderr, proc.stdout):
        for line in stream.splitlines():
            match = _MARKDOWNLINT_LINE_RE.match(line.strip())
            if not match or match.group("file") != rel:
                continue
            findings.append(
                {
                    "line": int(match.group("line")),
                    "col": int(match.group("col")) if match.group("col") else None,
                    "rule": match.group("rule"),
                    "name": match.group("name"),
                    "desc": match.group("desc").strip(),
                }
            )
    return {"available": True, "findings": findings}


def collect_wrapped_inline_code(doc: Path) -> list[dict[str, Any]]:
    text = doc.read_text(encoding="utf-8")
    return [
        {"line": lineno, "snippet": snippet}
        for lineno, snippet in _inline_code.find_wrapped_inline_code(text)
    ]


def collect_doc_links(repo_root: Path, doc: Path) -> list[dict[str, Any]]:
    """Reuse ``check_doc_links``' per-doc functions on the single target.

    Builds the same path indices the gate's ``main()`` builds (filesystem walk),
    then runs each per-doc check and collects every violation instead of
    fail-fast, so the form constraints (relative-link form, bare internal md
    refs, backticked file refs) all surface in one pass.
    """
    root = repo_root.resolve()
    known_md = _doc_links.iter_known_markdown_paths(root)
    known_repo = _doc_links.iter_known_repo_paths(root)
    unique_basename = _doc_links.build_unique_basename_index(known_repo)
    known_dirs = _doc_links.build_known_directories(known_repo)
    canonical = _doc_links.load_canonical_markdown_surfaces(root)

    findings: list[dict[str, Any]] = []
    text = doc.read_text(encoding="utf-8")
    for target in _doc_links.LINK_RE.findall(text):
        try:
            _doc_links.validate_link(root, doc, target)
        except _doc_links.ValidationError as exc:
            findings.append({"kind": "link", "detail": str(exc)})
    for ref in _doc_links.iter_bare_internal_doc_refs(root, doc, known_md, canonical):
        findings.append({"kind": "bare-internal-ref", "detail": ref})
    for lineno, candidate, reason in _doc_links.iter_backticked_file_refs(
        root, doc, known_repo, unique_basename, known_dirs, canonical
    ):
        findings.append(
            {"kind": "backticked-ref", "line": lineno, "detail": candidate, "reason": reason}
        )
    return findings


def collect_length(
    repo_root: Path, doc: Path, rel: str, as_surface: str | None
) -> dict[str, Any]:
    """Forecast the surface line cap by reusing the owning validator's constant
    and ``validate_max_lines`` (the exact gate path), when the target maps to a
    capped surface. A general doc with no registered cap reports no floor."""
    surface = _resolve_length_surface(repo_root, rel, as_surface)
    if surface is None:
        return {"surface": None, "cap": None, "current": None, "over": False, "detail": None}
    cap = _surface_cap(repo_root, surface)
    lines = doc.read_text(encoding="utf-8").splitlines()
    detail: str | None = None
    try:
        _artifact_validator.validate_max_lines(lines, max_lines=cap, artifact_label=surface.label)
    except _artifact_validator.ValidationError as exc:
        detail = str(exc)
    return {
        "surface": surface.name,
        "cap": cap,
        "current": len(lines),
        "over": detail is not None,
        "detail": detail,
    }


# --- report assembly ---------------------------------------------------------


@dataclass
class Report:
    target: str
    markdownlint: dict[str, Any]
    wrapped_inline_code: list[dict[str, Any]]
    doc_links: list[dict[str, Any]]
    length: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return bool(
            self.markdownlint["findings"]
            or self.wrapped_inline_code
            or self.doc_links
            or self.length["over"]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "blocked" if self.blocked else "ok",
            "target": self.target,
            "markdownlint": self.markdownlint,
            "wrapped_inline_code": self.wrapped_inline_code,
            "doc_links": self.doc_links,
            "length": self.length,
            "warnings": self.warnings,
        }


def build_report(repo_root: Path, raw_path: str, as_surface: str | None) -> Report:
    doc = Path(raw_path)
    if not doc.is_absolute():
        doc = repo_root / doc
    doc = doc.resolve()
    try:
        rel = doc.relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise PreflightError(f"{raw_path} is outside repo root {repo_root}") from exc
    if not doc.is_file():
        raise PreflightError(f"{rel} is not a file")
    if doc.suffix != ".md":
        raise PreflightError(f"{rel} is not a markdown (.md) file")

    warnings: list[str] = []
    markdownlint = collect_markdownlint(repo_root, rel)
    if not markdownlint["available"]:
        warnings.append(
            "markdownlint-cli2 (and npm) unavailable: the markdownlint rule class was "
            "not forecast; the markdown gate still runs it at commit time."
        )
    return Report(
        target=rel,
        markdownlint=markdownlint,
        wrapped_inline_code=collect_wrapped_inline_code(doc),
        doc_links=collect_doc_links(repo_root, doc),
        length=collect_length(repo_root, doc, rel, as_surface),
        warnings=warnings,
    )


def format_human(report: Report) -> str:
    lines = [f"doc-authoring-preflight: {report.target} [{report.to_dict()['status']}]"]
    for warning in report.warnings:
        lines.append(f"WARN: {warning}")

    ml = report.markdownlint
    if not ml["available"]:
        lines.append("markdownlint: not forecast (binary unavailable)")
    elif ml["findings"]:
        lines.append(f"markdownlint: {len(ml['findings'])} finding(s)")
        for row in ml["findings"]:
            loc = f"{row['line']}" + (f":{row['col']}" if row["col"] else "")
            lines.append(f"  - {report.target}:{loc} {row['rule']}/{row['name']} {row['desc']}".rstrip())
    else:
        lines.append("markdownlint: clean")

    if report.wrapped_inline_code:
        lines.append(f"wrapped-inline-code: {len(report.wrapped_inline_code)} finding(s)")
        for row in report.wrapped_inline_code:
            lines.append(f"  - line {row['line']}: ...{row['snippet']}...")
    else:
        lines.append("wrapped-inline-code: clean")

    if report.doc_links:
        lines.append(f"doc-links: {len(report.doc_links)} finding(s)")
        for row in report.doc_links:
            if row["kind"] == "backticked-ref":
                lines.append(f"  - backticked file ref `{row['detail']}` (line {row['line']}, {row['reason']})")
            elif row["kind"] == "bare-internal-ref":
                lines.append(f"  - bare internal markdown ref `{row['detail']}`")
            else:
                lines.append(f"  - {row['detail']}")
    else:
        lines.append("doc-links: clean")

    length = report.length
    if length["surface"] is None:
        lines.append("length: no enforced cap on this surface")
    elif length["over"]:
        lines.append(f"length: BLOCK ({length['current']}/{length['cap']} lines on {length['surface']})")
        lines.append(f"  - {length['detail']}")
    else:
        lines.append(f"length: {length['current']}/{length['cap']} lines on {length['surface']} (ok)")

    lines.append(
        "(affordance only -- the gates `check_doc_links.py`, `check-markdown.sh`, and the "
        "artifact length validators stay the enforcement.)"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--path", required=True, help="Target docs/**/*.md (or handoff) path")
    parser.add_argument(
        "--as-surface",
        help="Forecast a specific capped surface's length floor on a draft/fixture path (e.g. handoff)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    try:
        report = build_report(repo_root, args.path, args.as_surface)
    except PreflightError as exc:
        print(f"doc-authoring-preflight: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(format_human(report))
    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
