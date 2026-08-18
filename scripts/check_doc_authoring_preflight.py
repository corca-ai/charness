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
    backticked file references, fenced commands naming a missing script), via
    ``check_doc_links``;
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
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_doc_links = import_repo_module(__file__, "scripts.check_doc_links")
_inline_code = import_repo_module(__file__, "scripts.check_markdown_inline_code")
_handoff = import_repo_module(__file__, "scripts.validate_handoff_artifact")
_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
_version_verdict = import_repo_module(__file__, "scripts.adapter_version_verdict")
_markdown_scan = import_repo_module(__file__, "scripts.markdown_doc_scan")
_path_portability = import_repo_module(__file__, "scripts.path_portability_lib")
_markdownlint = import_repo_module(__file__, "scripts.markdownlint_probe")

# Re-exported, not re-implemented. The markdownlint engine adapter moved to its own
# module at this file's length cap; these names are the seam its callers and this
# repo's tests already bind, so they stay bound HERE and forward there.
_resolve_markdownlint_cmd = _markdownlint.resolve_markdownlint_cmd
markdownlint_engine_ran = _markdownlint.markdownlint_engine_ran
collect_markdownlint = _markdownlint.collect_markdownlint


class PreflightError(Exception):
    pass


@dataclass(frozen=True)
class LengthSurface:
    """A doc surface that carries an enforced line cap.

    ``module``/``constant`` name the OWNING validator's live DEFAULT cap, and
    ``resolver_attr`` names its adapter-aware resolver. Reading the constant alone
    was correct only while the ceiling was fixed: once a consuming repo could raise
    it, this forecast kept rendering `blocked` against a number the gate no longer
    enforced, sending the author to prune lines the gate would have accepted. Prefer
    the resolver; the constant stays the fallback for a surface that has none.
    ``matches`` resolves the surface from a repo-relative path.

    ``count_attr``/``check_attr`` name the validator's own counting and checking
    functions for a surface that does not charge for raw file length. Reusing
    them (rather than reimplementing the rule here) is what keeps the forecast
    from disagreeing with the gate about WHICH lines count, not just how many.
    Left None, the surface falls back to raw line count + ``validate_max_lines``.
    """

    name: str
    module: str
    constant: str
    label: str
    matches: Callable[[str], bool]
    count_attr: str | None = None
    check_attr: str | None = None
    resolver_attr: str | None = None


def surface_cap(repo_root: Path, surface: "LengthSurface") -> int:
    """The ceiling THIS repo enforces for the surface, not the shipped default."""
    module = _surface_module(surface)
    if surface.resolver_attr:
        return int(getattr(module, surface.resolver_attr)(repo_root))
    return int(getattr(module, surface.constant))


def _handoff_rel(repo_root: Path) -> str | None:
    try:
        adapter = _handoff.load_adapter(repo_root)
    except Exception:  # noqa: BLE001 -- a missing/broken adapter just means "no handoff surface here"
        return None
    rel = adapter.get("artifact_path")
    return Path(rel).as_posix() if rel else None


def adapter_load_failed(repo_root: Path) -> bool:
    """Did the handoff adapter exist but refuse to load?

    `_handoff_rel` swallows the failure and returns None, which is right for its callers
    -- no adapter means no capped surface -- but it makes a MALFORMED adapter
    indistinguishable from an absent one. That silence feeds both `_length_surfaces` and
    `collect_regenerable_facts`, so a YAML typo turns two rule classes into
    "measured, nothing found" and the command exits 0 with an empty report. `absent` and
    `broken` are separated here so `unforecast_classes` can name the second.

    A REFUSED VERSION counts as broken, and testing for a raised exception alone missed
    it: a `version: 9` adapter loads cleanly and returns a payload carrying the refusal in
    `errors`, so this answered False and `surface_cap` went on to forecast the shipped
    ceiling to an author whose repo had declared its own. This file already owns the
    "the adapter is broken, say so" decision for exactly that reason, which is why the
    version arm belongs here rather than in a fifth caller-side guard.
    """
    try:
        payload = _handoff.load_adapter(repo_root)
    except Exception:  # noqa: BLE001 -- the point IS that any load failure counts
        return True
    # `declarations_unhonored`, not `version_refused`: round 2 of the slice-5 review
    # found the narrow predicate answering False for a parser refusal, which leaves
    # the same defaults in `data` and so forecast the shipped ceiling to an author
    # whose repo had declared its own -- the exact bug this arm exists for, by the
    # other door.
    return _version_verdict.declarations_unhonored(payload.get("errors"))


def _length_surfaces(repo_root: Path) -> tuple[LengthSurface, ...]:
    handoff_rel = _handoff_rel(repo_root)
    surfaces: list[LengthSurface] = []
    if handoff_rel is not None:
        surfaces.append(
            LengthSurface(
                name="handoff",
                module="scripts.validate_handoff_artifact",
                constant="MAX_CONTENT_LINES",
                label="handoff artifact",
                matches=lambda rel, _h=handoff_rel: rel == _h,
                count_attr="content_lines",
                check_attr="validate_max_content_lines",
                resolver_attr="resolved_max_content_lines",
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


def _surface_module(surface: LengthSurface):
    return import_repo_module(__file__, surface.module)


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


def collect_length(
    repo_root: Path, doc: Path, rel: str, as_surface: str | None
) -> dict[str, Any]:
    """Forecast the surface line cap by reusing the owning validator's constant
    and ``validate_max_lines`` (the exact gate path), when the target maps to a
    capped surface. A general doc with no registered cap reports no floor."""
    surface = _resolve_length_surface(repo_root, rel, as_surface)
    if surface is None:
        return {"surface": None, "cap": None, "current": None, "over": False, "detail": None}
    module = _surface_module(surface)
    cap = surface_cap(repo_root, surface)
    lines = doc.read_text(encoding="utf-8").splitlines()
    counted = getattr(module, surface.count_attr)(lines) if surface.count_attr else lines
    detail: str | None = None
    try:
        if surface.check_attr:
            # The resolved cap is passed IN rather than left to the checker's own
            # default: the checker ships to consumers with the default baked in, and
            # a forecast that let it re-derive the number would reintroduce exactly
            # the disagreement this call site exists to prevent.
            #
            # Positional, with a TypeError fallback, because the checker gained its
            # second parameter in the same release as this call: a mixed-version
            # install (new preflight, vendored older validator) would otherwise raise
            # an uncaught TypeError where the surrounding `except` only catches
            # ValidationError -- a traceback instead of a forecast. The fallback loses
            # the resolved cap for that install, which is the old behavior, not a new
            # wrong one.
            check = getattr(module, surface.check_attr)
            try:
                check(lines, cap)
            except TypeError:
                check(lines)
        else:
            _artifact_validator.validate_max_lines(lines, max_lines=cap, artifact_label=surface.label)
    except _artifact_validator.ValidationError as exc:
        detail = str(exc)
    return {
        "surface": surface.name,
        "cap": cap,
        "current": len(counted),
        "over": detail is not None,
        "detail": detail,
    }


# --- report assembly ---------------------------------------------------------


def collect_regenerable_facts(
    repo_root: Path, doc: Path, rel: str, as_surface: str | None
) -> list[dict[str, Any]]:
    """Version/sha literals the handoff validator refuses, forecast per line.

    The rule lived ONLY in `validate_handoff_artifact`'s error string, so it was
    visible only AFTER writing the thing it forbids -- which is how a version
    literal reached a handoff draft twice. This is the same class the aggregate
    preflight exists for: a constraint enforced at commit time and un-briefed at
    authoring time.

    Reuses `REGENERABLE_PATTERNS` and the validator's own scrubbing regexes rather
    than restating them, so the forecast cannot drift from the gate. It reports
    EVERY hit; the gate raises on the first, which is the one difference and the
    point of a forecast.
    """
    handoff_rel = _handoff_rel(repo_root)
    is_handoff = rel == handoff_rel or (as_surface or "") == "handoff"
    if not is_handoff:
        return []
    findings: list[dict[str, Any]] = []
    for lineno, raw, in_fence in _markdown_scan.iter_doc_lines(doc):
        if in_fence:
            continue
        scrubbed = _handoff.INLINE_CODE_RE.sub(
            "", _handoff.URL_RE.sub("", _handoff.LINK_TARGET_RE.sub("", raw))
        )
        for pattern, label, replacement in _handoff.REGENERABLE_PATTERNS:
            match = pattern.search(scrubbed)
            if match is None:
                continue
            findings.append({
                "line": lineno,
                "literal": match.group(0).strip(),
                "label": label,
                "replacement": replacement,
            })
    return findings


@dataclass
class Report:
    target: str
    markdownlint: dict[str, Any]
    wrapped_inline_code: list[dict[str, Any]]
    doc_links: list[dict[str, Any]]
    regenerable_facts: list[dict[str, Any]]
    length: dict[str, Any]
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
            or self.regenerable_facts
            or self.length["over"]
        )

    @property
    def unforecast_classes(self) -> list[str]:
        """Rule classes this run could not measure at all.

        `blocked` reads FINDINGS, so a class that was never run contributes nothing to
        it and the command exits 0. That is fine as a gate verdict — this command is a
        forecast, and the owning gates still run at commit time — but `closeout_bundle_lib`
        records "passed" from that returncode, so an unmeasured class was indistinguishable
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
            "regenerable_facts": self.regenerable_facts,
            "length": self.length,
            "warnings": self.warnings,
        }


def build_report(repo_root: Path, raw_path: str, as_surface: str | None) -> Report:
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
    if adapter_load_failed(repo_root):
        # The length cap and the regenerable-fact classes BOTH resolve their surface
        # through the handoff adapter, and `_handoff_rel` swallows a load failure. Left
        # silent, a YAML typo renders both as "measured, nothing found" and the command
        # exits 0 -- the durable artifact then records a passed closeout for two classes
        # that never ran.
        unforecast.extend(("length", "regenerable_facts"))
        warnings.append(
            "the handoff adapter exists but did not load, so the length-cap and "
            "regenerable-fact classes were not forecast (they resolve their surface "
            "through it); fix the adapter to get those two classes back."
        )
    return Report(
        target=rel,
        markdownlint=markdownlint,
        wrapped_inline_code=collect_wrapped_inline_code(doc),
        doc_links=collect_doc_links(repo_root, doc),
        regenerable_facts=collect_regenerable_facts(repo_root, doc, rel, as_surface),
        unforecast=tuple(unforecast),
        length=collect_length(repo_root, doc, rel, as_surface),
        warnings=warnings,
    )


#: What this command is, on EVERY report it emits. It rode on the text rendering
#: only, and it is the one line that keeps a `status: ok` from reading as a
#: commit-gate verdict: this is a forecast, and the named gates do the enforcing.
AFFORDANCE_NOTE = (
    "affordance only -- the gates `check_doc_links.py`, `check-markdown.sh`, and the "
    "artifact length validators stay the enforcement."
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
    if rules["length"]["surface"] is None:
        known = ", ".join(rules["length"]["known_surfaces"]) or "(none)"
        payload["length_hint"] = f"no capped surface selected; pass --as-surface <{known}>"
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
    regenerable = rules["regenerable_facts"]
    if regenerable["classes"] and not regenerable["verdict"]:
        # A null verdict means the probe stopped tripping the rule (a class narrowed or
        # dropped upstream), NOT that there is no rule. The retired renderer said so in
        # words; a bare `verdict: null` above three correct rows reads as a missing
        # value instead, so the meaning rides in the payload rather than dying with it.
        payload["regenerable_facts_note"] = "the classes this surface refuses"
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--path",
        help="Target docs/**/*.md (or handoff) path; omit it to print the RULES with no target",
    )
    parser.add_argument(
        "--as-surface",
        help="Forecast a specific capped surface's length floor on a draft/fixture path (e.g. handoff)",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    if args.path is None:
        # Rules with no target: the other half of the same question, owned by
        # `doc_authoring_rules` and imported here so one command answers both.
        rules_module = import_repo_module(__file__, "scripts.doc_authoring_rules")
        try:
            rules = rules_module.build_rules(repo_root, args.as_surface)
        except rules_module.PreflightError as exc:
            print(f"doc-authoring-preflight: {exc}", file=sys.stderr)
            return 2
        emit_yaml(rules_payload(rules))
        return 0
    try:
        report = build_report(repo_root, args.path, args.as_surface)
    except PreflightError as exc:
        print(f"doc-authoring-preflight: {exc}", file=sys.stderr)
        return 2

    emit_yaml(report_payload(report))
    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
