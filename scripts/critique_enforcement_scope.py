"""What a critique-validation run actually evaluated, and over what scope.

Every floor on the critique evidence surface is *conditional* — on a date, on a
selection mode, on a probe config, on a trigger line the artifact itself
supplies. Each of those conditions was independently satisfiable in silence, and
a floor that is off emits nothing by construction, so the surface every other
closeout leans on could report a clean verdict having evaluated almost nothing.

This module owns the one concept behind all of that: the **enforcement scope** —
which condition resolved which way, and what the run therefore did NOT establish.
It is the `scope: evaluated | empty | not-configured` vocabulary already landed
for a shared boundary probe (D7), applied to the critique surface.

Three inputs used to decide a floor's fate from a channel that could not say "I
did not establish this", and each is repaired here rather than at its use site:

- **the artifact's date**, which gates four floors and was read from the body
  first, so a body `Date:` earlier than the filename bought exemption from all
  four. `critique_observed_date` is now the LATER of the two channels: an
  artifact is grandfathered only when both agree it is old.
- **the packet-consumed trigger**, which turns the reviewed-input binding floor
  on and was defined twice with a regex that missed the bullet form the corpus
  actually uses. One definition lives here, and it now reads the `## Packet
  Consumed` heading form too — 46 checked-in critiques declare a packet that way.
- **the cross-surface probe**, whose "no hit" was indistinguishable from "never
  ran". It now resolves to a typed state instead of a bare bool.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module

# One home for "the lines of a markdown section"; this module carried three copies.
_sections = import_repo_module(__file__, "scripts.markdown_sections")
# The base loader library, NOT the injected `adapter_lib` parameter: callers inject the
# CRITIQUE adapter (which owns `load_adapter`), while the rule for reading that loader's
# refusals lives with the loader that produces them.
_adapter_lib_module = import_repo_module(__file__, "scripts.adapter_lib")

# One home for the trigger that turns the reviewed-input binding floor on.
# Accepts the bullet and bold forms the corpus writes, and a path on the FOLLOWING
# line: the flush-and-same-line form was the only match, so the floor was off for
# artifacts that declared a consumed packet in the shapes authors actually use.
#
# A mid-line mention is deliberately still NOT matched, and recorded as residual
# rather than implied closed. Widening a CONTENT trigger is not free — every
# widening also fires on an artifact that merely *discusses* this surface, whose
# remediation (produce a packet SHA for a packet that does not exist) is
# impossible. That is the release-notes over-block class, inverted. The heading
# form no longer needs that trade; see `PACKET_CONSUMED_HEADING_RE` below.
PACKET_CONSUMED_RE = re.compile(
    r"(?im)^[ \t]*(?:[-*][ \t]+)?\*{0,2}packet consumed\*{0,2}[ \t]*:[ \t]*(?P<value>\S+|$)"
)
# A declaration that NO packet was consumed is not a packet binding. The corpus
# writes exactly these as the negative (`- Packet Consumed: n/a (no adapter
# sections)`), and treating them as a trigger demands three SHA256 fields for a
# packet the artifact just said does not exist — a hard refusal of honest work,
# and the over-block twin of the hole this trigger was widened to close.
# `blocked` is in the set because it is the third value the critique skill's own
# result contract teaches (`Packet Consumed — <path>, n/a (...), or
# blocked <reason>`): an honestly skipped packet declared the taught way was
# refused for missing SHAs on a packet just declared absent. A real packet path
# can never spell `blocked` — the corpus's paths all carry `/` or `.md`.
PACKET_ABSENT_VALUES = frozenset({"n/a", "na", "none", "no", "-", "–", "—", "blocked"})
# The heading form, which 46 checked-in release critiques use and the line trigger
# above could never match: `## Packet Consumed` on its own heading line with the
# path on a later line, no colon anywhere. It needs a section parse rather than a
# line parse — and unlike widening a line trigger, it carries no over-block risk,
# because a HEADING cannot be a mid-line prose mention of this surface. The
# declared value is still read (not just the heading's presence), so the corpus's
# `n/a` negative keeps the floor off exactly as it does on the line form.
PACKET_CONSUMED_HEADING_RE = re.compile(r"(?im)^[ \t]*\#{2,}[ \t]*\*{0,2}packet consumed\*{0,2}[ \t]*:?[ \t]*$")
_CRITIQUE_DATE_LINE = re.compile(r"^date:\s*(\d{4}-\d{2}-\d{2})\b")
_MARKUP = " `*_\"'>-.:"

CROSS_SURFACE_NOT_CONFIGURED = "not-configured"
CROSS_SURFACE_NOT_ESTABLISHED = "not-established"
CROSS_SURFACE_NOT_RESOLVED = "not-resolved"
CROSS_SURFACE_EVALUATED = "evaluated"


def packet_consumed(text: str) -> bool:
    """Whether the artifact DECLARES a consumed packet, as opposed to mentioning
    the field or explicitly declaring none.

    A bare trigger match is not a declaration: the value can be `n/a`, or empty
    with the path wrapped onto the next line, or the whole line can be a fenced
    QUOTATION of the form rather than an assertion of it. All three are read here
    so the binding floor turns on for a real declaration and stays off otherwise.

    The fence case is not hypothetical: the surface being tightened is the one
    authors write critiques *about*, and a critique quoting `- Packet consumed:
    <path>` in a fence would be forced to produce three SHA256 fields for a packet
    that does not exist — a refusal with no possible remediation.

    Inline code is deliberately NOT stripped: the corpus writes the path itself as
    `` `some/packet.json` ``, so blanking inline spans would erase the very value
    that proves a declaration.

    Two shapes are read: the `Packet consumed: <path>` LINE (flush, bulleted, bold,
    or wrapped onto the next line) and the `## Packet Consumed` HEADING whose
    section body carries the path. The heading form was the residual C3 left open —
    46 checked-in release critiques use it — and it stayed open because widening
    the line trigger any further would start firing on artifacts that merely
    discuss this surface. A heading is not prose, so it needs no such trade.
    """
    fenceless = strip_display_fences(text)
    for match in PACKET_CONSUMED_RE.finditer(fenceless):
        value = (match.group("value") or "").strip().strip(_MARKUP).lower()
        if not value:
            # Line-wrapped: the path sits on the following line. Take the next
            # non-empty line's first token as the declared value.
            tail = text[match.end() :].lstrip("\n")
            value = tail.split("\n", 1)[0].strip().strip(_MARKUP).lower()
        if value and value not in PACKET_ABSENT_VALUES:
            return True
    return any(
        value not in PACKET_ABSENT_VALUES
        for value in (_packet_heading_values(fenceless))
    )


#: A declared packet is a PATH, and only a path counts as a declaration. Reading
#: the first token of the section's first line unconditionally re-created the
#: over-block this trigger was carefully NOT widened into: two checked-in critiques
#: open the section with prose (`Transient prepare packet generated at ...`,
#: `Inline brief — the review covered ...`), whose first tokens are `transient` and
#: `inline`. Both would have been read as consumed packets, and one of them — a May
#: artifact nobody edited — would then have been refused for missing reviewer tier
#: evidence under `--paths`. Requiring a path shape keeps prose out without another
#: allowlist of words.
_PACKET_PATH_RE = re.compile(r"(?i)^[\w./~-]*(?:/|\.(?:md|json))[\w./~-]*$")


def _packet_heading_values(fenceless_text: str) -> list[str]:
    """The declared PATH under each `## Packet Consumed` heading, lowercased.

    The value is the section's first non-empty line — the shape the corpus writes,
    a bare path (usually inline-code wrapped) one blank line under the heading.

    Two non-declarations yield nothing rather than a value:

    - an EMPTY section: the author wrote the heading and no path, so nothing was
      declared either way, and inventing an `n/a` there would silently turn the
      binding floor off;
    - PROSE: a sentence under the heading is a note about the review, not a packet.
      A declared `n/a` still reaches the caller so the explicit negative keeps
      reading as an explicit negative.
    """
    values: list[str] = []
    for match in PACKET_CONSUMED_HEADING_RE.finditer(fenceless_text):
        tail = fenceless_text[match.end() :].splitlines()
        first = next(iter(_sections.leading_nonempty(_sections.lines_until_next_section(tail), 1)), "")
        # Bulleted section bodies write `- <path>`; the line form's own marker rule.
        first = re.sub(r"^[-*][ \t]+", "", first)
        value = first.split()[0].strip(_MARKUP) if first.split() else ""
        if value and (value in PACKET_ABSENT_VALUES or _PACKET_PATH_RE.match(value)):
            values.append(value)
    return values


_FENCE_RE = re.compile(r"(?ms)^[ \t]*(`{3,}|~{3,}).*?(?:^[ \t]*\1[ \t]*$|\Z)")


def strip_display_fences(text: str) -> str:
    """``text`` with fenced blocks blanked out, line count preserved.

    Content rendered AS CODE is shown to the reader, not asserted by the author.
    This surface reads the artifact's own claims out of its prose, so a critique
    that QUOTES the canonical form — overwhelmingly likely in a critique *of this
    validator* — otherwise has the quotation read as its claim.

    Twin implementation: `skills/public/release/scripts/audit_public_release_narrative.py`
    has the same helper plus inline-code stripping. Deliberately not shared: that
    file is a portable public skill whose helpers must live in the copy the caller
    invokes (the absent-guard-not-dead-guard lesson), and importing repo `scripts/`
    into it would reintroduce exactly that coupling. Unifying them is a
    boundary-ownership call, recorded rather than taken mid-slice.
    """
    return _FENCE_RE.sub(lambda match: "\n" * match.group(0).count("\n"), text)


def declared_fresh_eye_status(text: str, *, section_reader, line_reader) -> str | None:
    """The artifact's OWN `Fresh-eye satisfaction` claim.

    Two corrections over reading the first line that mentions the phrase:

    - fences are stripped first, so a quoted example is not read as the claim;
    - the canonical `## Fresh-Eye Satisfaction` SECTION wins over any earlier
      inline mention. Taking the first match let a sentence in `## Decision Under
      Review` shadow the real section below it, which silently disarmed the
      claim-vs-record consistency check (its trigger is the claim's text) while a
      human reader saw the contradiction plainly. The inline fallback stays,
      because much of the corpus writes `- Fresh-Eye Satisfaction: <value>` as a
      metadata bullet and never opens a section.
    """
    stripped = strip_display_fences(text)
    return section_reader(stripped) or line_reader(stripped)


FRESH_EYE_HEADING = "## Fresh-Eye Satisfaction"


def _fresh_eye_section_status(text: str) -> str | None:
    """The body under the canonical heading, joined — `None` when absent."""
    body = _sections.section_lines(text, FRESH_EYE_HEADING, case_insensitive=True)
    return " ".join(_sections.leading_nonempty(body, 3)) or None


def fresh_eye_satisfaction_status(text: str) -> str | None:
    return declared_fresh_eye_status(
        text, section_reader=_fresh_eye_section_status, line_reader=_fresh_eye_line_status
    )


def _fresh_eye_line_status(text: str) -> str | None:
    lines = text.splitlines()
    for index, raw in enumerate(lines):
        lowered = raw.strip().lower()
        if "fresh-eye satisfaction" not in lowered and "fresh-eye satisfaction" not in lowered.replace("_", "-"):
            continue
        if ":" in lowered:
            return lowered.split(":", 1)[1].strip()
        # A bare mention with no colon: the status wrapped onto the following lines.
        # Bounded to the same 3 as the section reader, and stopping at the next `## `
        # for the same reason — the next section's prose is not this status.
        return " ".join(_sections.leading_nonempty(_sections.lines_until_next_section(lines[index + 1 :]), 3))
    return None


def date_from_filename(path: Path) -> date | None:
    """The leading ``YYYY-MM-DD`` of the artifact filename, ``None`` when absent."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def date_from_body(text: str) -> date | None:
    """The in-body ``Date: YYYY-MM-DD`` line (first 5 lines), ``None`` when absent."""
    for line in text.splitlines()[:5]:
        match = _CRITIQUE_DATE_LINE.match(line.strip().lower())
        if match:
            try:
                return date.fromisoformat(match.group(1))
            except ValueError:
                return None
    return None


def observed_date(path: Path, text: str) -> date | None:
    """The artifact's effective date for grandfathering: the LATER of the in-body
    ``Date:`` line and the leading ``YYYY-MM-DD`` of the filename.

    Not a fallback chain. Every floor here grandfathers on ``date < RULE_DATE``,
    so whichever channel reads EARLIER is the one that buys exemption — and the
    body line is author-written, so reading it first let an artifact date itself
    out of the fresh-eye, boundary-ownership, delivery-state and reviewed-input
    binding floors at once. Taking the later date means that when BOTH channels
    parse, an artifact is exempt only if they agree it is old.

    Does NOT establish, stated rather than implied:

    - When only ONE channel parses, that channel decides alone — corroboration is
      unavailable, not achieved. An undated filename with a back-dated body is
      therefore still exempt. Measured: one checked-in artifact has a body date
      and no filename date, and the scaffold always emits both.
    - An artifact whose filename AND body are both back-dated is exempt. That is a
      deliberate forgery of both channels rather than one self-declared field
      overriding an independent one, and it is not decidable from the artifact.

    See `date_channel_disagreement` for the signal a run surfaces regardless.

    ``None`` when neither channel parses. Callers must NOT treat ``None`` as
    fail-open by default: only the explicit legacy allowlists are grandfathered on
    absence; every other undatable artifact is enforced as if post-cutoff.
    """
    channels = [value for value in (date_from_body(text), date_from_filename(path)) if value is not None]
    return max(channels) if channels else None


#: The critique surface's name for the same concept, kept so its call sites read
#: in their own vocabulary. The rule is NOT critique-specific — every dated
#: artifact family grandfathers the same way — and forking it per family is what
#: left the retro floors on the body-first `or` chain this replaced, back-dateable
#: for a month after the critique half was fixed.
critique_observed_date = observed_date


def date_channel_disagreement(path: Path, text: str) -> tuple[date, date] | None:
    """``(body, filename)`` when both dates parse and disagree, else ``None``.

    Reported rather than refused: the corpus carries one honest past-midnight
    off-by-one, and `critique_observed_date` already removes the exemption a
    disagreement could buy, so failing here would cost a real artifact to close a
    hole that is already closed.
    """
    body, filename = date_from_body(text), date_from_filename(path)
    if body is None or filename is None or body == filename:
        return None
    return body, filename


@dataclass(frozen=True)
class CrossSurfaceScope:
    """The cross-surface probe's typed outcome.

    ``hit`` alone cannot carry this: ``False`` meant "configured, resolved, no
    match", "configured but handed no changed scope", and "not configured at all"
    indistinguishably, so the #408 objective override was silently absent
    whenever `merge-base origin/main HEAD` failed and the caller passed an empty
    ``--changed-ref``.
    """

    state: str
    hit: bool
    # What the verdict was computed over, so a reader can tell WHICH question
    # produced it. Without these two the widened scope was invisible in the
    # report: the same tree can arm or disarm the tooth depending on whether the
    # working tree was included, and that is exactly what this row repaired.
    scanned_paths: int = 0
    worktree_included: bool = False
    matched_path: str | None = None

    @property
    def overrides(self) -> bool:
        """Whether this scope may reject a bare ``single-surface`` verdict — only
        an EVALUATED probe that actually matched. An unestablished scope makes a
        claim about nothing."""
        return self.state == CROSS_SURFACE_EVALUATED and self.hit


def resolve_cross_surface_scope(
    repo_root: Path,
    changed_ref: str | None,
    changed_path: list[str] | None,
    *,
    probe_lib,
    adapter_lib,
    include_worktree: bool = False,
) -> CrossSurfaceScope:
    """Resolve the probe to a typed state without shelling out when it cannot run.

    Config is read first and cheaply: a repo that configures no globs and no
    surfaces is opt-out by design (spec DBD-4) and must not be reported the same
    way as a configured probe that was handed nothing to look at.

    An adapter the loader REFUSED is a third thing again. Its keys were dropped, so
    the config reads empty and the opt-out branch below would answer
    `not-configured` -- an opt-out this repo never declared, over a file that failed
    to parse. This is the critique validator's own cross-surface consumer, and it
    must not disagree with the shared probe about the same adapter.
    """
    adapter = adapter_lib.load_adapter(repo_root)
    probe = probe_lib.probe_config_from_adapter(adapter["data"])
    if _adapter_lib_module.unreadable_reasons(adapter):
        return CrossSurfaceScope(CROSS_SURFACE_NOT_ESTABLISHED, False)
    if not probe["globs"] and not probe["surfaces"]:
        return CrossSurfaceScope(CROSS_SURFACE_NOT_CONFIGURED, False)
    if not changed_ref and not changed_path and not include_worktree:
        return CrossSurfaceScope(CROSS_SURFACE_NOT_ESTABLISHED, False)
    hit, changed, resolved_probe = probe_lib.resolve_hit(
        repo_root,
        changed_path=changed_path,
        changed_ref=changed_ref,
        include_worktree=include_worktree,
    )
    # `resolved_probe`, not the outer `probe`: `resolve_hit` re-reads the adapter
    # through its OWN module-level binding, so scoring the witness against the
    # injected adapter's config could disagree with the `hit` it is explaining and
    # render ``match on `None` ``. Same config, one decision.
    matched = (
        next(
            (
                path
                for path in changed
                if probe_lib.cross_surface_hit(
                    repo_root,
                    [path],
                    surfaces=resolved_probe["surfaces"],
                    globs=resolved_probe["globs"],
                )
            ),
            None,
        )
        if hit
        else None
    )
    if not changed:
        # The state is decided by the RESOLVED path list, not by which flags were
        # passed. A scope that resolved to nothing was not evaluated: reporting
        # `evaluated (no match)` over zero paths is the same "no hit is
        # indistinguishable from never ran" defect this vocabulary exists to kill,
        # and `--include-worktree` reintroduced it (empty base + clean tree) until
        # the condition moved off the flags. `overrides` is False either way, so
        # this changes no verdict -- only whether the report makes a claim it
        # cannot support.
        return CrossSurfaceScope(
            CROSS_SURFACE_NOT_ESTABLISHED, False, 0, include_worktree, None
        )
    return CrossSurfaceScope(
        CROSS_SURFACE_EVALUATED, hit, len(changed), include_worktree, matched
    )


_CROSS_SURFACE_NOTE = {
    CROSS_SURFACE_NOT_CONFIGURED: "not-configured (this repo declares no cross-surface globs or surfaces)",
    CROSS_SURFACE_NOT_ESTABLISHED: (
        "not-established (probe is configured but no changed scope resolved; "
        "the #408 objective override did NOT run)"
    ),
    CROSS_SURFACE_NOT_RESOLVED: "not-resolved (no critique artifact was in scope, so no floor ran at all)",
}


def _cross_surface_note(cross_surface: CrossSurfaceScope | None) -> str:
    if cross_surface is None:
        return _CROSS_SURFACE_NOTE[CROSS_SURFACE_NOT_RESOLVED]
    if cross_surface.state == CROSS_SURFACE_NOT_ESTABLISHED and cross_surface.worktree_included:
        # A ref AND the worktree were both supplied and the union still resolved to
        # nothing. Rendering the generic "no --changed-ref/--changed-path resolved"
        # here would state a cause that is false: the probe ran and found an empty
        # scope, which is a different fact from never being handed one.
        return (
            "not-established (a ref and the worktree both resolved 0 path(s); "
            "nothing to probe, so the #408 objective override did NOT run)"
        )
    if cross_surface.state == CROSS_SURFACE_EVALUATED:
        # Hit and miss are different facts, and only the hit changes a verdict
        # (it rejects a bare `single-surface`). Rendering both as `evaluated`
        # hides the one state that does something.
        scope_note = (
            f"{cross_surface.scanned_paths} path(s)"
            + (", worktree included" if cross_surface.worktree_included else ", committed scope only")
        )
        if cross_surface.hit:
            return (
                f"evaluated over {scope_note} (match on `{cross_surface.matched_path}` "
                "— #408 override active)"
            )
        return f"evaluated over {scope_note} (no match)"
    # An unrecognized state must NOT default to the strongest reading; the whole
    # point of typing this was that an unknown outcome is not a clean one.
    return _CROSS_SURFACE_NOTE.get(cross_surface.state, f"unknown ({cross_surface.state})")


def add_cross_surface_args(parser) -> None:
    parser.add_argument(
        "--changed-ref",
        help="Git ref/range whose changed paths are tested against the repo cross-surface probe; "
        "a hit rejects a bare `single-surface` boundary verdict (#408 override).",
    )
    parser.add_argument(
        "--changed-path",
        nargs="*",
        help=(
            "Explicit changed paths for the cross-surface probe (bypasses git; wins "
            "over --changed-ref). With --include-worktree the working tree is unioned "
            "in, so these paths win but are not the whole scope."
        ),
    )
    parser.add_argument(
        "--include-worktree",
        action="store_true",
        help=(
            "Union the working tree into the probe's changed paths. Verify precedes "
            "commit, so the slice under critique is on disk and invisible to a "
            "committed range alone; pass this from a pre-commit/pre-push quality run "
            "so the probe judges the change under review rather than the previous one."
        ),
    )


def report_enforcement_scope(run, artifacts, cross_surface: CrossSurfaceScope | None, disagreements) -> None:
    """Name what the run evaluated, so `Validated N critique artifact(s).` stops
    reading as coverage it never claimed.

    Takes the ALREADY-RESOLVED probe scope and the disagreements collected during
    validation rather than recomputing either: a report that recomputes what it
    describes can disagree with the run it reports on, which is the defect shape
    this module exists to close — and re-reading 650 artifacts to render one line
    doubles the sweep's file I/O for a line that changes no verdict.

    `cross_surface is None` means the probe was never resolved at all, because
    nothing was in scope to judge. That is its own state and gets its own name:
    the first cut fell back to `not-established`, so a run that passed a perfectly
    good `--changed-ref` and simply had no critique artifact to check printed
    "no --changed-ref/--changed-path resolved" — an assertion about a resolution
    that never ran, which is precisely this module's own subject matter. It was
    the common `run-quality.sh` path.
    """
    mode = "--all" if run.args.all else ("--paths" if run.explicit_paths else "changed")
    print(
        render_scope_record(
            artifact_count=len(artifacts),
            mode=mode,
            cross_surface=cross_surface,
            binding_currency_enabled=not run.args.all,
            date_disagreements=list(disagreements),
        )
    )


def render_scope_record(
    *,
    artifact_count: int,
    mode: str,
    cross_surface: CrossSurfaceScope | None,
    binding_currency_enabled: bool,
    date_disagreements: list[str],
) -> str:
    """One line naming what this run evaluated, and what it did not establish.

    Printed beside the artifact count because the count alone reads as coverage:
    `Validated 650 critique artifact(s).` was equally true of a sweep that skipped
    reviewer-tier evidence, delivery state, binding currency and the cross-surface
    probe for every one of them.

    `binding-currency-check` reports whether the check is ENABLED for this run,
    which is a fact about the invocation. It deliberately does not say
    "evaluated": binding currency is reached only for an artifact that declares a
    packet and is dated into the binding floor, so "evaluated" would assert work
    over artifacts that declared no binding at all — the same overclaim the bare
    artifact count made, one line further down.
    """
    entries = [
        f"mode={mode}",
        f"cross-surface-probe={_cross_surface_note(cross_surface)}",
        "binding-currency-check="
        + (
            "enabled"
            if binding_currency_enabled
            else "disabled (a full sweep re-reads historical bindings that are stale by design; "
            "packet identity and integrity are still checked)"
        ),
    ]
    if date_disagreements:
        shown = ", ".join(date_disagreements[:3])
        more = f" (+{len(date_disagreements) - 3} more)" if len(date_disagreements) > 3 else ""
        entries.append(f"date-channel-disagreement={len(date_disagreements)}: {shown}{more}")
    return f"enforcement scope over {artifact_count} artifact(s): " + " | ".join(entries)
