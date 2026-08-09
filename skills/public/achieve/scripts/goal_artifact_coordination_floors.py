"""Presence-only coordination closeout floors for goal artifacts.

The floors cover gather, release, and issue-closeout boundaries. Each is
clone-safe, section-scoped, grandfathered by ``Created``, and satisfied by a
real step line or explicit opt-out in ``## Coordination Cues``.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# The floors landed around 2026-05-30; the cutoff grandfathers same-day in-flight goals.
COORDINATION_FLOOR_RULE_DATE = date(2026, 5, 31)
ISSUE_CLOSEOUT_FLOOR_RULE_DATE = date(2026, 6, 2)
# A goal that ends without designing its successor spends the session's most
# expensive asset -- what it just learned about this repo's real shape -- and then
# drops it. Unlike the three floors above, this one is UNCONDITIONAL in scope: the
# trigger is "a goal is closing", not "this goal touched a boundary". The opt-out
# is where "do not design one" gets said out loud, which is the only form of that
# instruction that survives the session it was given in.
SUCCESSOR_GOAL_FLOOR_RULE_DATE = date(2026, 8, 7)


COORDINATION_SECTION = "Coordination Cues"
CONTEXT_SOURCES_SECTION = "Context Sources"
RECORDED_WORK_SECTIONS = ("Slice Log", "Final Verification")

_EXTERNAL_URL = re.compile(r"https?://\S", re.IGNORECASE)


# Deliberately precise; the bare word "release" would over-trigger.
#
# ECOSYSTEM-STANDARD IDENTIFIERS, not this repo's house style. The first version
# of this list held only `bump_version`, `publish_release`, `marketplace.json`
# and `charness-artifacts/release/` -- four names belonging to THIS repo. In any
# consuming repo none of them ever appears, so `release_triggered` returned False
# for every goal, the release coordination floor never fired, and a goal that
# bumped a version closed with no release evidence and no line saying the check
# had not applied. A floor that is silently inert everywhere but its authoring
# repo is worse than no floor: it reads as coverage.
#
# What is listed now are version manifests and publish commands whose names are
# fixed by their ecosystems, so matching them is matching a declared convention
# rather than a writing style. Repo-specific surfaces belong in the adapter's
# `release_surface_tokens`, not here.
_RELEASE_SURFACE_TOKENS = (
    # this repo's own surfaces, kept so its behavior is unchanged
    "bump_version",
    "publish_release",
    "marketplace.json",
    "charness-artifacts/release/",
    # version manifests
    "pyproject.toml",
    "package.json",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "setup.py",
    "setup.cfg",
    "version.txt",
    "changelog.md",
    # publish commands
    "npm publish",
    "cargo publish",
    "twine upload",
    "gh release",
    "git tag",
    "poetry publish",
    "goreleaser",
)


_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
# `MIN_OPTOUT_REASON` and `_classify_step` are RE-EXPORTS, not used in this
# module: both moved into the shared grammar, and this module stays their
# published name for existing callers and the floor's own tests. The match loop
# uses `classify_cue_line`, which wraps the classifier with markup stripping and
# inert-value demotion.
from goal_artifact_floor_grammar import MIN_OPTOUT_REASON as MIN_OPTOUT_REASON  # noqa: E402
from goal_artifact_floor_grammar import SATISFYING_CUE_KINDS as _SATISFYING  # noqa: E402
from goal_artifact_floor_grammar import classify_cue_line as _classify_cue_line  # noqa: E402
from goal_artifact_floor_grammar import classify_cue_step as _classify_step  # noqa: E402,F401
from goal_artifact_floor_grammar import cue_pattern as _cue_pattern  # noqa: E402
from goal_artifact_floor_grammar import (  # noqa: E402
    is_floor_in_scope,
    issue_closeout_triggered,
)
from goal_artifact_floor_grammar import joined_section_body as _joined_section_body  # noqa: E402
from goal_artifact_floor_grammar import parse_created_date as goal_created_date  # noqa: E402
from goal_artifact_floor_grammar import section_body as _section_body  # noqa: E402
from goal_artifact_floor_grammar import section_span as _section_span  # noqa: E402
from goal_artifact_markdown import mask_fences as _mask_fences  # noqa: E402

# Step lines are anchored so inline examples never satisfy a floor, and compiled
# through the shared cue grammar so all four stay markup-tolerant together: the
# backtick blindness that made a filled `` `Gather: …` `` cue invisible was
# identical in every one of them, because every one was cloned from the same line.
_GATHER_REF = _cue_pattern("Gather")
_RELEASE_REF = _cue_pattern("Release")
_ISSUE_CLOSEOUT_REF = _cue_pattern(r"Issue\s+closeout")
_SUCCESSOR_GOAL_REF = _cue_pattern(r"Successor\s+goal")


def coordination_floors_apply(text: str) -> bool:
    """Whether the gather/release floors fire for this goal (grandfather-by-
    ``Created``-date). Fail-CLOSED: a missing/malformed ``Created`` is in-scope."""
    return is_floor_in_scope(goal_created_date(text), COORDINATION_FLOOR_RULE_DATE)


def successor_goal_floor_applies(text: str) -> bool:
    """Whether the successor-goal floor fires for this goal.

    Scope only, not a trigger test: once in scope this floor is ALWAYS triggered,
    because every closing goal has learned something and the question is only
    whether the next one gets it.
    """
    return is_floor_in_scope(goal_created_date(text), SUCCESSOR_GOAL_FLOOR_RULE_DATE)


def issue_closeout_floor_applies(text: str) -> bool:
    """Whether the issue-closeout floor fires for this goal."""
    return is_floor_in_scope(goal_created_date(text), ISSUE_CLOSEOUT_FLOOR_RULE_DATE)


def gather_triggered(text: str) -> bool:
    """True when ``## Context Sources`` names an external (http/https) source."""
    body = _section_body(_mask_fences(text), CONTEXT_SOURCES_SECTION)
    if not body:
        return False
    return _EXTERNAL_URL.search(body) is not None


def release_triggered(text: str, repo_root: Path | None = None) -> bool:
    """True when the goal's recorded work names a release-surface token.

    The Coordination Cues span is blanked before the scan so a ``Release:``
    reference value (e.g. ``charness-artifacts/release/...``) or a seeded example
    in that section never counts as release work — only the *rest* of the body
    (Slice Plan / Slice Log / etc., where the run records what it changed) does.

    ``repo_root`` is optional and additive: when given, the consuming repo's
    achieve adapter may declare extra ``release_surface_tokens`` for a release
    surface the built-in ecosystem list does not name. Resolution is graceful, so
    a missing or broken adapter simply leaves the built-in list in force.
    """
    masked = _mask_fences(text)
    span = _section_span(masked, COORDINATION_SECTION)
    if span is not None:
        masked = masked[: span[0]] + (" " * (span[1] - span[0])) + masked[span[1] :]
    low = masked.lower()
    tokens = list(_RELEASE_SURFACE_TOKENS)
    if repo_root is not None:
        try:
            from achieve_adapter_policy import resolve_release_surface_tokens

            tokens.extend(resolve_release_surface_tokens(repo_root))
        except Exception:
            # An adapter problem must not decide a floor. Falling back to the
            # built-in list keeps the floor armed rather than silently inert,
            # which is the failure this whole repair is about.
            pass
    return any(token in low for token in tokens)


def _parse_step(section_body: str | None, ref_re: "re.Pattern[str]") -> tuple[str | None, str | None]:
    """Classify the gather/release step line(s) inside the Coordination Cues body.

    Returns ``(kind, value)`` — ``None`` when no step line exists at all. When
    several step lines are present the **first satisfying** one wins (a real
    ``ref`` or a valid ``optout``), so a stray short opt-out above a real
    reference does not shadow it into a false refusal; only when none satisfies
    does the first non-satisfying classification surface (for the diagnostic).
    Presence-only: a real reference is never inspected further.
    """
    if not section_body:
        return None, None
    first: tuple[str | None, str | None] = (None, None)
    for match in ref_re.finditer(section_body):
        kind, value = _classify_cue_line(match.group(1))
        if kind is None:
            continue  # empty or still-a-placeholder reference: not a step line
        if kind in _SATISFYING:
            return kind, value
        if first[0] is None:
            first = (kind, value)
    return first


def apply_coordination_floors(report: dict[str, Any], text: str) -> None:
    """Attach the gather/release/issue floor verdicts to ``report``.

    For an in-scope goal (grandfather-by-``Created``): if a floor is *triggered*
    (external source / release-surface token / issue-closeout signal)
    and the Coordination Cues section carries no satisfying step line (a real
    reference or a ≥30-char ``n/a — <reason>`` opt-out),
    refuse the flip. Presence/binding-only — a real reference's content is never
    judged. Grandfathered goals are inert.
    """
    created = goal_created_date(text)
    in_scope = coordination_floors_apply(text)
    report["coordination_scope"] = {
        "in_scope": in_scope,
        "created": created.isoformat() if created else None,
        "rule_date": COORDINATION_FLOOR_RULE_DATE.isoformat(),
        "reason": (
            "Created >= rule date (or undatable; fail-closed): coordination floors apply"
            if in_scope
            else "Created < rule date: grandfathered, coordination floors inert"
        ),
    }
    if not in_scope:
        return
    # Joined section body so a `Gather:`/`Release:`/`Issue closeout:` step whose
    # value wrapped onto a continuation line is matched, not false-rejected.
    section = _joined_section_body(text, COORDINATION_SECTION)
    missing: list[dict[str, str]] = []

    g_trig = gather_triggered(text)
    g_kind, _ = _parse_step(section, _GATHER_REF)
    g_ok = (not g_trig) or g_kind in _SATISFYING
    report["gather_floor"] = {"triggered": g_trig, "satisfied": g_ok, "evidence": g_kind}
    if g_trig and not g_ok:
        reason = (
            "`## Context Sources` names an external source (a URL — Slack/Notion/Docs/Drive "
            "links and bare web URLs all qualify) but `## Coordination Cues` records no "
            "`Gather: <ref>` step and no `Gather: n/a — <reason>` opt-out (>=30 chars); route "
            "the external source through `gather` or record the opt-out before flipping to complete"
        )
        report["gather_floor"]["reason"] = reason
        missing.append({"floor": "gather", "reason": reason})

    r_trig = release_triggered(text)
    r_kind, _ = _parse_step(section, _RELEASE_REF)
    r_ok = (not r_trig) or r_kind in _SATISFYING
    report["release_floor"] = {"triggered": r_trig, "satisfied": r_ok, "evidence": r_kind}
    if r_trig and not r_ok:
        reason = (
            "this run's recorded work names a release surface (a version bump or install-manifest "
            "edit) but `## Coordination Cues` records no `Release: <ref>` step and no "
            "`Release: n/a — <reason>` opt-out (>=30 chars); cut or verify the release through "
            "`release` or record the opt-out before flipping to complete"
        )
        report["release_floor"]["reason"] = reason
        missing.append({"floor": "release", "reason": reason})

    i_scope = issue_closeout_floor_applies(text)
    i_trig = i_scope and issue_closeout_triggered(text)
    i_kind, _ = _parse_step(section, _ISSUE_CLOSEOUT_REF)
    i_ok = (not i_trig) or i_kind in _SATISFYING
    report["issue_closeout_floor"] = {
        "in_scope": i_scope,
        "rule_date": ISSUE_CLOSEOUT_FLOOR_RULE_DATE.isoformat(),
        "triggered": i_trig,
        "satisfied": i_ok,
        "evidence": i_kind,
    }
    if i_trig and not i_ok:
        reason = (
            "this goal names tracked issue closeout work but `## Coordination Cues` records no "
            "`Issue closeout: <ref>` step and no `Issue closeout: n/a — <reason>` opt-out "
            "(>=30 chars); stage the close through `issue` and record the verifier proof before "
            "flipping to complete"
        )
        report["issue_closeout_floor"]["reason"] = reason
        missing.append({"floor": "issue_closeout", "reason": reason})

    s_scope = successor_goal_floor_applies(text)
    s_kind, _ = _parse_step(section, _SUCCESSOR_GOAL_REF)
    s_ok = (not s_scope) or s_kind in _SATISFYING
    report["successor_goal_floor"] = {
        "in_scope": s_scope,
        "rule_date": SUCCESSOR_GOAL_FLOOR_RULE_DATE.isoformat(),
        "triggered": s_scope,
        "satisfied": s_ok,
        "evidence": s_kind,
    }
    if s_scope and not s_ok:
        reason = (
            "this goal is closing without designing its successor: `## Coordination Cues` "
            "records no `Successor goal: <path-or-ref>` line and no "
            "`Successor goal: n/a — <reason>` opt-out (>=30 chars). Design the next goal from "
            "THIS run's measured lessons, patterns, and structural findings -- the operator "
            "asked for the closeout to end there -- or say out loud why none is wanted"
        )
        report["successor_goal_floor"]["reason"] = reason
        missing.append({"floor": "successor_goal", "reason": reason})

    if missing:
        report["coordination_missing"] = missing
        report["ok"] = False


# The coordination floors each satisfy independently, and `MIN_OPTOUT_REASON`
# guards each `n/a — <reason>` on its own. Nothing counted them, so a goal that
# opted out of four of its six coordination obligations rendered EXACTLY like one
# that routed every single one. The per-floor verdicts were all individually
# legitimate; the pattern across them -- this run declined most of its
# coordination -- was the fact no surface carried, and it is the fact a
# disposition reviewer needs. Non-blocking by construction: each opt-out already
# passed its own floor, so re-refusing here would punish a valve the contract
# deliberately provides. This reports; the reviewer judges.
_AGGREGATE_FLOOR_KEYS = (
    ("gather", "gather_floor"),
    ("release", "release_floor"),
    ("issue_closeout", "issue_closeout_floor"),
    ("successor_goal", "successor_goal_floor"),
)


def _routing_aggregate_kind(routing: dict[str, Any]) -> str | None:
    """Collapse the per-skill routing evidence into ONE obligation's verdict.

    `_parse_routing_step` answers per queried skill, and a single blanket
    ``Routing: n/a — <reason>`` line returns ``optout`` for EVERY required route.
    Counting those separately reported four opt-outs for one authored decision
    and inflated both sides of the census — the headline number stopped being a
    count of decisions, which is the only thing it is for. `## Coordination Cues`
    carries one `Routing:` cue, so it contributes one obligation.

    ``None`` when routing was never triggered.
    """
    if not routing.get("triggered"):
        return None
    evidence = routing.get("evidence")
    if not isinstance(evidence, dict) or not evidence:
        # Triggered but with no evidence map is a malformed payload. Every sibling
        # floor fails CLOSED on one; dropping the obligation from the denominator
        # instead would quietly shrink the census.
        return "unsatisfied"
    # Read the floor's OWN verdict first. A set-equality collapse got this wrong
    # in both directions: a goal that routed `impl` explicitly and covered the
    # rest with a blanket opt-out has evidence `{"impl": "ref", "quality":
    # "optout"}` and SATISFIES the floor, but `{"ref","optout"}` matched neither
    # equality and was censused `unsatisfied` — telling the reviewer an
    # obligation was unmet on a floor that passed, and dropping the authored
    # opt-out from the count so no advisory was raised at all. Worse, it was
    # ORDER-DEPENDENT: putting the opt-out line first makes `_parse_routing_step`
    # answer `optout` for every skill, so the same two decisions censused
    # differently based only on which line the author typed first.
    if not routing.get("satisfied"):
        return "unsatisfied"
    if any(kind == "optout" for kind in evidence.values()):
        return "optout"
    return "ref"


def apply_coordination_optout_aggregate(report: dict[str, Any]) -> None:
    """Attach the cross-floor opt-out census to ``report``. Never blocks.

    Reads the verdicts the coordination and phase-routing floors already wrote,
    so it must run AFTER both. Counts only obligations that actually FIRED: an
    untriggered floor was never an obligation, and counting it would inflate the
    denominator and make a disciplined goal look evasive.

    ``routed`` is counted from real ``ref`` evidence rather than by subtracting
    opt-outs from the total. Subtraction silently reported an UNMET floor (no cue
    line at all, or a below-floor opt-out) as ``routed`` — telling a reviewer the
    goal had routed the very obligation it never met, on exactly the refusal report
    where they are most likely to read it.
    """
    eligible: list[str] = []
    opted_out: list[str] = []
    routed: list[str] = []
    unsatisfied: list[str] = []

    def _record(name: str, kind: str | None) -> None:
        eligible.append(name)
        if kind == "optout":
            opted_out.append(name)
        elif kind == "ref":
            routed.append(name)
        else:
            unsatisfied.append(name)

    for name, key in _AGGREGATE_FLOOR_KEYS:
        floor = report.get(key)
        if not isinstance(floor, dict) or not floor.get("triggered"):
            continue
        _record(name, floor.get("evidence"))

    routing = report.get("phase_routing_floor")
    if isinstance(routing, dict):
        routing_kind = _routing_aggregate_kind(routing)
        if routing_kind is not None:
            _record("routing", routing_kind)

    scope = report.get("coordination_scope")
    in_scope = scope.get("in_scope") if isinstance(scope, dict) else None
    aggregate: dict[str, Any] = {
        # A grandfathered goal short-circuits before any floor key is written, so
        # a bare `eligible: 0` was indistinguishable from an in-scope goal that
        # triggered nothing. The census is the thing handed to a reviewer, so it
        # carries its own scope rather than making them find `coordination_scope`.
        "coordination_in_scope": in_scope,
        "eligible": len(eligible),
        "opted_out": len(opted_out),
        "routed": len(routed),
        "unsatisfied": len(unsatisfied),
        "eligible_obligations": eligible,
        "opted_out_obligations": opted_out,
        "unsatisfied_obligations": unsatisfied,
    }
    if opted_out:
        aggregate["reason"] = (
            f"this goal opted out of {len(opted_out)} of its {len(eligible)} triggered "
            "coordination obligation(s) ("
            + ", ".join(opted_out)
            + "). Each opt-out passed its own floor; the disposition review owns whether "
            "declining this many coordination boundaries was the right call for this run"
        )
    report["coordination_optout_aggregate"] = aggregate
