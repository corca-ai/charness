#!/usr/bin/env python3
"""Aggregate author-time preflight for general doc/markdown surfaces.

Given a target ``docs/**/*.md``, forecast in ONE pass
the deterministic constraints an author otherwise discovers by failing one
commit gate at a time:

  - markdownlint-cli2 rules (``MD004`` list-marker style, trailing space, ...),
    the same engine and config the markdown gate runs;
  - wrapped inline-code spans (a single-backtick span that breaks across a
    newline), via ``check_markdown_inline_code``;
  - doc-link / pathy-ref form (relative-link form, bare internal markdown refs,
    backticked file references, fenced commands naming a missing script), via
    ``check_doc_links``;

It REUSES each real validator -- it never forks their logic, so the forecast
cannot drift from what the gate enforces. This mirrors the SKILL.md one-shot
preflight (``check_skill_surface_preflight.py --run-checks``), extended to the
general-docs surface class that it does not cover.

It is an AFFORDANCE, not a gate: a doc still commits without it, and the
existing gates (``check_doc_links.py``, ``check-markdown.sh``, the artifact
length validators) stay the enforcement. It is intentionally absent from the
blocking commit-gate plan; a non-blocking guard test keeps it that way.
"""
from __future__ import annotations

import argparse
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_doc_links = import_repo_module(__file__, "scripts.check_doc_links")
_inline_code = import_repo_module(__file__, "scripts.check_markdown_inline_code")
_path_portability = import_repo_module(__file__, "scripts.core.path_portability_lib")
_markdownlint = import_repo_module(__file__, "scripts.markdownlint_probe")

# Re-exported, not re-implemented. The markdownlint engine adapter moved to its own
# module at this file's length cap; these names are the seam its callers and this
# repo's tests already bind, so they stay bound HERE and forward there.
_resolve_markdownlint_cmd = _markdownlint.resolve_markdownlint_cmd
markdownlint_engine_ran = _markdownlint.markdownlint_engine_ran
collect_markdownlint = _markdownlint.collect_markdownlint


class PreflightError(Exception):
    pass


def _doc_link_indices(repo_root: Path) -> tuple[Path, set[str], dict[str, str], set[str], set[str]]:
    """The path indices `check_doc_links`' own `main()` builds before it can
    classify anything. Both the target check and the rules probe need them."""
    root = repo_root.resolve()
    known_repo = _doc_links.iter_known_repo_paths(root)
    return (
        root,
        known_repo,
        _doc_links.build_unique_basename_index(known_repo),
        _doc_links.build_known_directories(known_repo),
        _doc_links.load_canonical_markdown_surfaces(root),
    )


# --- per-class collectors (each reuses the owning validator, no fork) --------



def collect_wrapped_inline_code(doc: Path) -> list[dict[str, Any]]:
    text = doc.read_text(encoding="utf-8")
    # The reason token has to survive the hop: the back-compat two-tuple shim drops it,
    # and this collector then renders an UNTERMINATED finding under the `wrapped-inline-code`
    # label — the operator misdirection the checker itself split a message for. This
    # consumer also applies no `EXCLUDE_PARTS`, so it can be pointed at the very files the
    # checker's own scope excludes.
    return [
        {"line": lineno, "snippet": snippet, "reason": reason}
        for lineno, snippet, reason in _inline_code.find_inline_code_violations(text)
    ]


def collect_doc_links(repo_root: Path, doc: Path) -> list[dict[str, Any]]:
    """Reuse ``check_doc_links``' per-doc functions on the single target.

    Builds the same path indices the gate's ``main()`` builds (filesystem walk),
    then runs each per-doc check and collects every violation instead of
    fail-fast, so the form constraints (relative-link form, bare internal md
    refs, backticked file refs) all surface in one pass.
    """
    root, known_repo, unique_basename, known_dirs, canonical = _doc_link_indices(repo_root)
    known_md = _doc_links.iter_known_markdown_paths(root)

    findings: list[dict[str, Any]] = []
    text = doc.read_text(encoding="utf-8")
    for target in _doc_links.iter_link_targets(text):
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
    for lineno, candidate in _doc_links.iter_unresolved_command_targets(root, doc, known_repo):
        findings.append(
            {
                "kind": "unresolved-command-target",
                "line": lineno,
                "detail": candidate,
                "reason": "missing-script",
            }
        )
    return findings


# --- report assembly ---------------------------------------------------------


@dataclass
class Report:
    target: str
    markdownlint: dict[str, Any]
    wrapped_inline_code: list[dict[str, Any]]
    doc_links: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)
    #: Classes whose collector could not measure at all, set by `build_report`. A field
    #: rather than a purely derived value BECAUSE the causes are heterogeneous: an engine
    #: that did not run, and an adapter that would not load. The first spelling derived
    #: the whole list from the markdownlint key alone, which made `[]` read as
    #: "everything was measured" on a report where two other classes had silently
    #: collapsed -- a completeness claim this surface had not earned.
    unforecast: tuple[str, ...] = ()

    @property
    def blocked(self) -> bool:
        return bool(
            self.markdownlint["findings"]
            or self.wrapped_inline_code
            or self.doc_links
        )

    @property
    def unforecast_classes(self) -> list[str]:
        """Rule classes this run could not measure at all.

        `blocked` reads FINDINGS, so a class that was never run contributes nothing to
        it and the command exits 0. That is fine as a gate verdict — this command is a
        forecast, and the owning gates still run at commit time — but the former
        aggregate closeout record stored "passed" from that returncode, so an unmeasured
        class was indistinguishable
        from a clean one in the durable artifact. The exit code is deliberately NOT changed
        (it would turn every machine without a local markdownlint into a failing closeout);
        what changes is that the payload says so in a field, not only in prose inside a
        truncated stdout blob.

        Known-incomplete, stated rather than implied: a markdownlint run whose findings a
        consumer's `outputFormatters` redirected reports `available: True` having measured
        nothing (see `markdownlint_probe.markdownlint_engine_ran`), and this list cannot
        see it. `[]` means "no class reported itself unmeasured", not "everything was
        measured" — the strongest claim the collectors actually support.
        """
        unforecast = list(self.unforecast)
        if not self.markdownlint["available"]:
            unforecast.append("markdownlint")
        return sorted(set(unforecast))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "blocked" if self.blocked else "ok",
            "unforecast_classes": self.unforecast_classes,
            "target": self.target,
            "markdownlint": self.markdownlint,
            "wrapped_inline_code": self.wrapped_inline_code,
            "doc_links": self.doc_links,
            "warnings": self.warnings,
        }


def build_report(repo_root: Path, raw_path: str) -> Report:
    doc = Path(raw_path)
    if not doc.is_absolute():
        doc = repo_root / doc
    doc = doc.resolve()
    rel = _path_portability.resolve_within_repo(repo_root, raw_path)
    if rel is None:
        raise PreflightError(f"{raw_path} is outside repo root {repo_root}")
    if not doc.is_file():
        raise PreflightError(f"{rel} is not a file")
    if doc.suffix != ".md":
        raise PreflightError(f"{rel} is not a markdown (.md) file")

    warnings: list[str] = []
    markdownlint = collect_markdownlint(repo_root, rel)
    if not markdownlint["available"]:
        # Two distinct causes, two distinct remedies. The original message named the
        # only cause that existed when it was written; emitting it unchanged on the
        # resolved-but-unrun branch sends the operator to install npm when npm is
        # already there and `npm install` / PATH is the actual fix.
        resolved = markdownlint.get("resolved_command")
        if resolved:
            warnings.append(
                f"markdownlint-cli2 resolved as `{shlex.join(resolved)}` but produced no "
                "engine output, so the markdownlint rule class was not forecast; a local "
                "install (`npm ci`, or markdownlint-cli2 on PATH) is what this needs. "
                "`check-markdown.sh` resolves the same three tiers and REFUSES at commit "
                "time until one of them runs, so this is not a forecast you can skip."
            )
        else:
            warnings.append(
                "markdownlint-cli2 (and npm) unavailable: the markdownlint rule class was not "
                "forecast. `check-markdown.sh` resolves the same three tiers and exits 1 "
                "when none of them resolves, so install the engine (`npm ci`, or "
                "markdownlint-cli2 on PATH) rather than waiting for the commit gate."
            )
    unforecast: list[str] = []
    return Report(
        target=rel,
        markdownlint=markdownlint,
        wrapped_inline_code=collect_wrapped_inline_code(doc),
        doc_links=collect_doc_links(repo_root, doc),
        unforecast=tuple(unforecast),
        warnings=warnings,
    )


#: What this command is, on EVERY report it emits. It rode on the text rendering
#: only, and it is the one line that keeps a `status: ok` from reading as a
#: commit-gate verdict: this is a forecast, and the named gates do the enforcing.
AFFORDANCE_NOTE = (
    "affordance only -- the gates `check_doc_links.py` and `check-markdown.sh` "
    "stay the enforcement."
)
#: Per-finding-kind remedies the text rendering added from the owning validator's
#: live constant. The rows themselves carry only `kind`/`detail`/`line`, so
#: emitting the bare report would have dropped the only statement of what to DO.
_DOC_LINK_REMEDIES = {
    "unresolved-command-target": _doc_links.MISSING_COMMAND_TARGET_REMEDY,
}


def report_payload(report: Report) -> dict[str, Any]:
    """The emitted document: the report, plus what only the renderer used to say."""
    payload = report.to_dict()
    payload["note"] = AFFORDANCE_NOTE
    kinds = {row["kind"] for row in report.doc_links}
    remedies = {kind: text for kind, text in _DOC_LINK_REMEDIES.items() if kind in kinds}
    if remedies:
        payload["doc_link_remedies"] = remedies
    return payload


def rules_payload(rules: dict[str, Any]) -> dict[str, Any]:
    """The emitted rules document, plus the guidance only the renderer used to say.

    This is the only rules surface now. `doc_authoring_rules.format_rules_human`
    rendered the same guidance until the 2026-08-14 YAML migration stopped calling
    it; it was deleted rather than left as a second, test-only copy of these
    sentences, free to drift from the one an operator actually reads.
    """
    payload = dict(rules)
    payload["note"] = "rules only -- pass --path <draft.md> to check a real target against them."
    if rules["probe_sample"] is None:
        payload["probe_note"] = (
            "link form / backticked file references were NOT probed -- this repo has no "
            "tracked path-shaped file to classify, and an invented one would teach the wrong rule"
        )
    # "resolves", not "is available": this lane never ran the engine, and a resolved
    # `npm exec --no` refuses. Saying so keeps the hint from promising a forecast that
    # the --path run it recommends may then report as unforecast.
    payload["markdownlint_hint"] = (
        "a markdownlint command resolves here; run with --path <draft> to forecast the "
        "rule findings, which is also what proves the engine actually runs"
        if rules["markdownlint"]["resolves"]
        else "binary unavailable here; `check-markdown.sh` refuses at commit time until it "
        "resolves, so install it (`npm ci`, or markdownlint-cli2 on PATH)"
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--path",
        help="Target docs/**/*.md path; omit it to print the RULES with no target",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    if args.path is None:
        # Rules with no target: the other half of the same question, owned by
        # `doc_authoring_rules` and imported here so one command answers both.
        rules_module = import_repo_module(__file__, "scripts.doc_authoring_rules")
        try:
            rules = rules_module.build_rules(repo_root)
        except rules_module.PreflightError as exc:
            print(f"doc-authoring-preflight: {exc}", file=sys.stderr)
            return 2
        emit_yaml(rules_payload(rules))
        return 0
    try:
        report = build_report(repo_root, args.path)
    except PreflightError as exc:
        print(f"doc-authoring-preflight: {exc}", file=sys.stderr)
        return 2

    emit_yaml(report_payload(report))
    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
