"""Portable closeout-evidence check shared by achieve/issue/release closeouts.

The lighter self-substitution pattern (#230 + #229) emerges when an agent
inline-paraphrases a prescribed sub-skill (`retro`, `critique`,
`probe_host_logs.py`) instead of executing it. This library is the gate
that the three sibling skills wrap with their own evidence shape; the
contract lives at ``docs/prescribed-skill-closeout-contract.md``.

The library is intentionally policy-free: callers declare the required
evidence names and supply each name's path-or-skip. The library checks
file existence + non-empty content for paths and validates skip reasons
against a small enum so a free-text "host limit" cannot become the new
lighter substitute.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ALLOWED_SKIP_REASONS = frozenset(
    {
        "host-blocked-subagent",
        "host-log-not-exposed",
        "evaluator-unavailable",
    }
)
MIN_SKIP_LENGTH = 40

# Minimum length of the skip *detail* — the text after the enum head and its
# colon — checked alongside ``MIN_SKIP_LENGTH`` on the whole string.
#
# Some callers (``issue_resolution_critique``, ``publish_release_preflight``)
# manufacture the enum head themselves from a shorthand the author wrote. On
# those carriers the enum check validates a constant the caller supplied, so the
# length floor is the only surviving tooth — and the head's own characters were
# paying it down: ``host-blocked-subagent: `` is 23 characters, so the 40-char
# total floor accepted a 17-character signal and skipped a mandatory fresh-eye
# critique on a GitHub issue close (B2). This floor measures only the text the
# author actually chose, so head length can no longer set the bar.
#
# 20, not 40. The pre-fix effective bar for manufactured-head callers was already
# ~17; the repo's own genuine host signals run 24-39 characters, so a 40-char
# detail floor would sit ABOVE observed honest usage and buy padding rather than
# signal. Length is not the real tooth here and cannot be: a fluent 40-character
# excuse passes any length floor. What distinguishes a skipped critique from an
# executed one is that the skip is now LOUD — see ``_skip_advisories`` in
# ``issue_resolution_critique.py``. This floor only refuses terseness.
MIN_SKIP_DETAIL_LENGTH = 20

# NOT a size floor, deliberately -- sweep row S3 asked for one and it does not
# work here. S3 is right that `st_size == 0` is coarse: a 1-byte file satisfied
# this gate. But a byte floor is just as coarse in the direction that matters.
# Two floors were written and both were withdrawn:
#
#   * basename-channel-only (200 bytes), on the argument that a content bind
#     needs no floor "because the token had to be written INTO the artifact".
#     False, and cheaply so: `printf '#466' > x.md` is four bytes and binds by
#     content. The unguarded channel was the cheaper one.
#   * universal (200 bytes). Defensible, but still defeated by 200 bytes of
#     filler, and it failed 34 existing tests -- i.e. it sat above how this
#     repo's own evidence is written, which is the bar-moving shape.
#
# What actually distinguishes a stub from an artifact is SHAPE, and shape is
# per-kind. Be precise about where that leaves things, because "the per-kind
# validators own it" would be misdirection: `validate_critique_artifacts.py` and
# `validate_retro_artifact.py` exist, but they run `--all` from the repo's own
# quality gate (`.agents/surfaces.json`), NOT on this gate's accept path. At the
# release publish boundary the ordering is backwards -- a stub unlocks the
# publish, and the later shape check cannot un-publish it. They also cover 2 of
# the >=5 evidence kinds `check()` is generic over (`host_log_probe`,
# `disposition_review`, and any `NAME:PATH` through the CLI have none), and a
# consuming repo that installs this skill does not get them at all.
#
# So: the stub half of S3 is OPEN on this path. Closing it means wiring a
# per-kind shape check into the accept path, which is a contract change this
# library -- deliberately policy-free and generic over evidence names -- is the
# wrong layer to make unilaterally. Binding (below) is what this layer can
# honestly enforce, and it kills the stale-unrelated-artifact half of S3
# outright. The rest is recorded, not papered over with a number.

# floor-addition-restraint: recorded call. Q1 (closeout-contract weight): YES,
# partly -- it adds no field or section, but the contract's word is "form", and a
# refusal an author meets by failing the flip is a form. That raises the bar to
# add it, and it is why consuming issue/release renderers expose the category:
# a form discovered by failing the flip AND with no message is the churn pattern
# the checklist exists to stop. Standing floors are audited in
# `charness-artifacts/audit/closeout-floors.md`; this one is a `keep` by Q3. Q2 (is advisory enough?): no. The recurrence is recorded:
# sweep row S3, two withdrawn floors, and an xfail checked in against this exact
# accept path. Q3 (preflight absorption): no -- the condition is a property of the
# cited file at check time, not a static artifact shape, so this is a `keep`.
# Scope: it runs wherever identity tokens are available -- either the `tokens=`
# binding path, or `residual_tokens=` for a wrapper that must bind
# out-of-band. A caller that can supply no identity at all still sees no change.
#
# 8, not 20. The teeth are at residual == 0 (the content IS the token); the number
# only guards near-empty residue like `#` or `x`. It is therefore set BELOW every
# measured datapoint rather than between two of them. Both accepted evidence kinds
# are measured, and the measurement is a checked-in script, not an assertion --
# `scripts/gates/measure_evidence_residual.py`, whose recorded run is
# `charness-artifacts/probe/2026-08-01-evidence-residual-floor.json`:
#   markdown artifacts   min residual 337 over 2168 files
#   JSON host-log probes min residual 530 over 83 files
# `_bound_residual_chars` counts alphanumerics only, so a punctuation-heavy JSON
# probe scores lower than prose of the same size; that is why the JSON kind was
# measured separately rather than assumed. 20 would have sat 2 characters under a
# real fixture, which is a knife edge, not a floor.
MIN_BOUND_RESIDUAL_CHARS = 8

# Sweep row S3's stub half. NOT the byte floor S3 asked for, and not the two that
# were withdrawn -- see the note above `MIN_SKIP_DETAIL_LENGTH` for why a size
# number is coarse in the direction that matters.
#
# The precise defect is narrower than "the file is small": `printf '#466' > x.md`
# binds by CONTENT because its content IS the token. So the rule is that evidence
# must say something BEYOND the identity it binds to. Measured before it was
# written, which is what the two withdrawn attempts skipped:
#
#   * the stub's residual after removing its token occurrences is 0 characters;
#   * across all 2168 checked-in `charness-artifacts/**/*.md`, scored against every
#     word of each file's own name as a token, the SMALLEST residual is 337.
#
# That is a 337-to-0 separation, not a threshold on a continuum, and it holds for
# both accepted kinds (see the measurement script named above). Note the
# earlier "it failed 34 existing tests, i.e. it sat above how this repo's own
# evidence is written" reasoning: those 34 were TEST FIXTURES. The artifacts
# themselves start at 427 bytes (p1 = 816, median = 4119), so fixture minimalism
# was standing in for evidence minimalism.
#
# What this does NOT close: a few characters of filler still passes, exactly as any
# floor here would. This refuses a STUB, not a lie. The remaining distance is
# per-kind SHAPE, which this deliberately policy-free layer is still the wrong
# place to decide -- see the note above.
def _bound_residual_chars(text: str, tokens: list[str]) -> int:
    """Alphanumeric characters left after removing every binding token occurrence.

    Case-insensitive and longest-token-first so overlapping tokens (``466`` inside
    ``issue-466``) cannot leave a fragment that counts as content.

    Removal is plain substring, deliberately WIDER than ``_token_matches``, which
    is boundary- and citation-anchored: token ``466`` also erases the ``466``
    inside ``1466``. The asymmetry only ever removes more, so it can make a real
    artifact look thinner but can never let a stub through -- and this predicate's
    job is to refuse, so erring toward "less residual" errs toward refusing, which
    the floor's placement two orders of magnitude below the corpus absorbs.
    """
    residual = text
    for token in sorted({token for token in tokens if token}, key=len, reverse=True):
        residual = re.sub(re.escape(token), " ", residual, flags=re.IGNORECASE)
    return len(re.sub(r"[^0-9A-Za-z]", "", residual))


# Cap how much of an evidence file is scanned for a binding token. A retro or
# probe artifact references its goal/issue/release identity in the first
# screenful when it does at all; reading more buys nothing and risks a large
# file stalling the gate.
_BINDING_CONTENT_SCAN_BYTES = 65536

# A bare numeric-cluster token (e.g. ``230-229`` or ``185``) is matched on
# non-alphanumeric boundaries, not raw substring, so ``185`` does not falsely
# bind a file whose body merely contains ``21850`` or ``0185abc``. Slug tokens
# carry their own distinctiveness and match as substrings.
#
# ``.`` is a cluster separator alongside ``-``/``_`` so a DOTTED release version
# is boundary-matched too. Without it ``2.12.0`` fell to plain substring
# containment and bound any file merely mentioning ``12.12.0`` or ``2.12.01`` --
# a critique that names a dependency version satisfied the mandatory release
# critique gate. The comment above called such tokens "slugs carrying their own
# distinctiveness"; a version is not a slug, and in a consuming repo publishing
# ``1.0.0`` the collision surface is every lockfile line quoted in an artifact.
_NUMERIC_CLUSTER_TOKEN = re.compile(r"^\d+(?:[-_.]\d+)*$")

# A *bare* numeric token (``27``) is far weaker than a compound cluster
# (``230-229``): boundary matching alone still bound it to any standalone digit
# run in the body, so a critique of a different issue bound a #27 closeout
# purely through its ``Date: 2026-07-27`` header (B4), and ``v0.42.1`` /
# ``14:32:05`` bound #42 / #32. In CONTENT a bare number therefore has to be
# CITED, not merely present: ``#27``, ``issue 27``, ``issues/27``, ``gh-27``.
# Every checked-in critique/retro artifact in this repo names its issue that way
# (``Issue: #367``, ``Target: issue #184``, ``Closes #349``,
# ``corca-ai/charness#429``), so the citation requirement refuses coincidence
# without refusing the forms the repo actually writes.
# The separator class admits the markdown a real artifact wraps a citation in
# (``goal **253**``, ``issue `184` ``, ``the fix (#253)``), and the trailing
# citation RUN lets a list inherit its marker: this repo writes
# ``issues 118, 119, and 120`` and ``Resolve issues 356 and 357``, and binding
# only the first member would refuse a correct bundled closeout. A run cannot
# manufacture a coincidence, because it still has to start at a marker --
# ``Date: 2026-07-27`` has none.
_BARE_NUMERIC_TOKEN = re.compile(r"^\d+$")
_CITATION_SEPARATOR = r"[\s#:/_\-*`\[(\"']"
_NUMERIC_CITATION_PREFIX = re.compile(
    r"(?:#"
    rf"|(?:^|[^0-9a-z])(?:issues?|gh|prs?|goal|slice|no\.?|number){_CITATION_SEPARATOR}{{0,3}}"
    rf")(?:(?:\d+|and|&|,|;){_CITATION_SEPARATOR}{{0,3}})*$"
)

# Date/time/timestamp runs carry no closeout identity, but they are digit runs
# on clean boundaries, so they are masked out of a BASENAME before a bare
# numeric token is matched against it: ``2026-05-14-013911-packet.md`` must not
# bind #2026, #14 or #5 while ``2026-05-28-185-foo.md`` still binds #185.
# ``-`` is deliberately NOT a time-tail separator: a bundled-artifact basename
# like ``2026-07-30-12-13-closeout.md`` is this repo's own naming shape, and
# reading ``-12-13`` as a clock would mask away two real issue numbers. Harmless
# here (charness issues are 3-digit) and not harmless in a consuming repo whose
# whole backlog is #1-#99, which is what this skill ships into.
_DATELIKE_RUN = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:[t _]\d{2}[:_]?\d{2}(?:[:_]?\d{2})?)?|\d{6,}"
)


def _boundary_match(token: str, haystack: str, *, allow_v_prefix: bool = False) -> bool:
    """Boundary-anchored search for ``token``.

    ``allow_v_prefix`` admits the ``v`` in ``v2.12.0`` / ``v2-11-2-release-critique.md``,
    which is how this repo names release artifacts: a bare ``(?<![0-9a-z])``
    lookbehind reads that ``v`` as an alphanumeric neighbour and refuses the match.
    The ``v`` must itself be on a boundary, so ``rev2.12.0`` still does not bind.

    OFF by default, and that default is the load-bearing part. Enabling it for
    every token — as the first version of this did — let a BARE issue number bind
    the leading segment of any version-named artifact: token ``2`` matched the
    checked-in ``v2-1-4-release-packet.md``, so closing issue #2 could be
    satisfied by an unrelated release packet. That is the stale-unrelated-artifact
    class this module exists to refuse, re-created one channel over, and it is
    worst in exactly the consuming repos this skill ships into — the ones whose
    whole backlog is #1-#99.
    """
    prefix = "v?" if allow_v_prefix else ""
    return (
        re.search(rf"(?<![0-9a-z]){prefix}{re.escape(token)}(?![0-9a-z])", haystack)
        is not None
    )


def _token_matches(token: str, haystack: str, *, in_name: bool = False) -> bool:
    """True when ``token`` (already lowercased) occurs in ``haystack``.

    Numeric-cluster tokens require non-alphanumeric neighbours so a short issue
    number cannot bind on a coincidental digit run; other tokens use plain
    containment. A bare numeric token additionally must be *cited* when matched
    against file content, and is matched against a date-masked basename, so a
    date/time/version digit run cannot manufacture a binding it did not earn.
    """
    if not _NUMERIC_CLUSTER_TOKEN.match(token):
        return token in haystack
    if not _BARE_NUMERIC_TOKEN.match(token):
        # Compound clusters (``230-229``, ``2.12.0``) are distinctive on their
        # own, and are the only tokens that may carry a `v` release prefix.
        return _boundary_match(token, haystack, allow_v_prefix=True)
    if in_name:
        if len(token) >= 6:
            # A token that is itself timestamp-shaped must not be masked away.
            return _boundary_match(token, haystack)
        masked = _DATELIKE_RUN.sub(lambda m: "." * len(m.group(0)), haystack)
        return _boundary_match(token, masked)
    for match in re.finditer(
        rf"(?<![0-9a-z]){re.escape(token)}(?![0-9a-z])", haystack
    ):
        if _NUMERIC_CITATION_PREFIX.search(haystack[: match.start()]):
            return True
    return False


def _read_binding_text(path: Path) -> tuple[str, bool]:
    """``(text, readable)`` over the same window ``evidence_binds_to_context`` scans.

    ``readable`` is returned rather than folded into an empty string: a file that
    bound by BASENAME but whose content cannot be read (permissions, a race) would
    otherwise score residual 0 and be reported as a stub -- a wrong diagnosis at a
    refusal an operator has to act on.
    """
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.read(_BINDING_CONTENT_SCAN_BYTES), True
    except OSError:
        return "", False


def evidence_binds_to_context(
    path: Path, *, tokens: list[str]
) -> tuple[bool, str]:
    """Return ``(binds, reason)`` for whether an evidence file pertains to its
    closeout context.

    File *presence* is necessary but not sufficient: a closeout can cite any
    pre-existing artifact in the repo and pass the presence check (the #233 F1
    hole). An evidence file *binds* to its context when its basename or its
    content contains at least one distinctive context token (a goal slug, an
    issue number, a release version).

    Token containment is deliberately the binding signal rather than mtime:
    a fresh ``git clone`` resets every file's mtime to checkout time, so an
    ``mtime >= context-date`` rule would pass for every stale file in a cloned
    tree and silently reopen the exact hole this guards. Basename/content
    containment is clone-safe.

    ``tokens`` empty means the caller could not derive a context identity; the
    caller opts out of binding and only the presence check applies.
    """
    if not tokens:
        return True, "no binding tokens supplied"
    lowered = [token.lower() for token in tokens if token]
    if not lowered:
        return True, "no binding tokens supplied"
    name = path.name.lower()
    for token in lowered:
        if _token_matches(token, name, in_name=True):
            return True, f"basename contains {token!r}"
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            content = handle.read(_BINDING_CONTENT_SCAN_BYTES).lower()
    except OSError:
        content = ""
    for token in lowered:
        if _token_matches(token, content):
            return True, f"content contains {token!r}"
    hint = ""
    if any(_BARE_NUMERIC_TOKEN.match(token) for token in lowered):
        hint = (
            " (a bare number must be CITED in the content — e.g. '#27', "
            "'issue 27' — or appear in the basename; a bare digit run inside a "
            "date, time or version does not bind)"
        )
    return False, (
        f"none of the binding tokens {sorted(set(lowered))} appear in the "
        f"evidence basename or content{hint}; the file does not bind to this "
        "closeout"
    )


def parse_evidence_arg(raw: str) -> tuple[str, str]:
    """Parse a ``name:path`` pair. Raises ``ValueError`` on malformed input."""
    if ":" not in raw:
        raise ValueError(f"--evidence value {raw!r} must be NAME:PATH")
    name, _, path = raw.partition(":")
    name = name.strip()
    path = path.strip()
    if not name or not path:
        raise ValueError(f"--evidence value {raw!r} must be NAME:PATH (both non-empty)")
    return name, path


def parse_skip_arg(raw: str) -> tuple[str, str]:
    """Parse a ``name:reason`` pair. Raises ``ValueError`` on malformed input."""
    if ":" not in raw:
        raise ValueError(f"--skip value {raw!r} must be NAME:REASON")
    name, _, reason = raw.partition(":")
    name = name.strip()
    reason = reason.strip()
    if not name or not reason:
        raise ValueError(f"--skip value {raw!r} must be NAME:REASON (both non-empty)")
    return name, reason


def _validate_skip_reason(reason: str) -> tuple[bool, str | None]:
    head, _, detail = reason.partition(":")
    head = head.strip()
    if head not in ALLOWED_SKIP_REASONS:
        return False, (
            f"skip reason must start with one of "
            f"{sorted(ALLOWED_SKIP_REASONS)} followed by ':' and a detail"
        )
    # A repeated head is the same manufactured-constant hole one level down: a
    # caller that prepends ``host-blocked-subagent: `` to an author shorthand
    # that itself begins with an enum head would otherwise let the duplicated
    # head fund the detail floor.
    stripped = detail.strip()
    while True:
        next_head, sep, rest = stripped.partition(":")
        if sep and next_head.strip() in ALLOWED_SKIP_REASONS:
            stripped = rest.strip()
            continue
        break
    if len(reason) < MIN_SKIP_LENGTH:
        return False, (
            f"skip reason too short ({len(reason)} chars; min {MIN_SKIP_LENGTH}); "
            "append the concrete host signal or evaluator condition"
        )
    if len(stripped) < MIN_SKIP_DETAIL_LENGTH:
        return False, (
            f"skip detail too short ({len(stripped)} chars after the "
            f"{head!r} head; min {MIN_SKIP_DETAIL_LENGTH}); the enum head does not "
            "count toward the floor — append the concrete host signal or "
            "evaluator condition"
        )
    return True, None


def _residual_of(path: Path, tokens: list[str]) -> int | None:
    text, readable = _read_binding_text(path)
    return _bound_residual_chars(text, tokens) if readable else None


def _stub_failure(name: str, path: Path, tokens: list[str]) -> dict[str, Any] | None:
    """A stub-evidence entry, or ``None`` when the file says enough (or cannot be read).

    An unreadable file is NOT reported as a stub: that is a different fact, and
    ``evidence_binds_to_context`` may legitimately have bound it by basename.
    """
    residual = _residual_of(path, tokens)
    if residual is None or residual >= MIN_BOUND_RESIDUAL_CHARS:
        return None
    return {
        "name": name,
        "path": str(path),
        "residual_chars": residual,
        "detail": (
            f"evidence says nothing beyond the identity it was checked against "
            f"({residual} character(s) remain after removing "
            f"{sorted(set(tokens))}; {MIN_BOUND_RESIDUAL_CHARS} required). This "
            f"is a stub check, not a binding verdict -- on a presence-only caller "
            f"the file may not have been bound at all."
        ),
    }


def _accept_or_stub(
    name: str, path: Path, tokens: list[str], *, binding: str
) -> dict[str, Any]:
    """The satisfied record, or the stub-evidence record if the file is a stub.

    One home for both the bound and the presence-only branch. They differ only in
    the `binding` string they carry, and writing the stub check plus the accept
    record out twice is how the two drifted apart in the first cut -- the
    presence-only branch got the floor added later and separately.
    """
    stub = _stub_failure(name, path, tokens) if tokens else None
    if stub is not None:
        return stub
    return {
        "name": name,
        "via": "evidence",
        "path": str(path),
        "binding": binding,
        "residual_chars": _residual_of(path, tokens) if tokens else None,
    }


def check(
    *,
    repo_root: Path,
    required: list[str],
    evidence: dict[str, str],
    skips: dict[str, str],
    kind: str | None = None,
    tokens: list[str] | None = None,
    residual_tokens: list[str] | None = None,
) -> dict[str, Any]:
    """Validate that every required evidence name has either a real file or a
    valid skip reason. Returns a structured report.

    ``evidence`` paths resolve relative to ``repo_root`` when not absolute.

    ``tokens`` are the closeout's context identity (goal slug, issue number,
    release version). When supplied, every evidence file must additionally BIND
    to them. Binding lives here, at the shared choke point, rather than only in
    the callers that remembered it: ``evidence_binds_to_context`` existed for
    two releases and ``check()`` never called it, so binding held only where a
    caller wired it by hand. The generic CLI and release publish gate had none,
    and a real critique about an
    unrelated 2026-07-27 topic satisfied an ``issue-resolution`` closeout.

    ``tokens`` empty or omitted still means presence-only -- some callers
    genuinely cannot derive an identity -- but the report now RECORDS that as
    ``binding: not-checked`` per item, so a presence-only pass can no longer be
    read as a bound one.

    ``residual_tokens`` supplies identity for the STUB floor alone, without
    changing binding. Issue resolution binds out-of-band per ISSUE NUMBER because
    one critique line may carry several, while ``tokens=`` here means "bind if ANY
    of these match". Wiring the stub floor through ``tokens`` would therefore
    weaken that rule: measured, a four-byte ``#466`` file
    closed issue #466 through the resolution-critique gate with the floor already
    in the library, because that gate supplies no ``tokens``. This parameter keeps
    the floor at the one choke point instead of copying it into each wrapper,
    which is the mistake ``evidence_binds_to_context`` already made once.
    """
    repo_root = repo_root.resolve()
    satisfied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    missing: list[str] = []
    invalid_skips: list[dict[str, Any]] = []
    missing_evidence_files: list[dict[str, Any]] = []
    unbound_evidence: list[dict[str, Any]] = []
    stub_evidence: list[dict[str, Any]] = []
    binding_tokens = [token for token in (tokens or []) if token]
    stub_tokens = [token for token in (residual_tokens or []) if token] or binding_tokens

    for name in required:
        if name in evidence:
            raw_path = evidence[name]
            resolved = Path(raw_path)
            if not resolved.is_absolute():
                resolved = (repo_root / raw_path).resolve()
            else:
                resolved = resolved.resolve()
            if not resolved.is_file() or resolved.stat().st_size == 0:
                missing_evidence_files.append({"name": name, "path": str(resolved)})
                continue
            if binding_tokens:
                binds, reason = evidence_binds_to_context(resolved, tokens=binding_tokens)
                if not binds:
                    unbound_evidence.append(
                        {"name": name, "path": str(resolved), "detail": reason}
                    )
                    continue
                accepted = _accept_or_stub(name, resolved, stub_tokens, binding=reason)
                (satisfied if "binding" in accepted else stub_evidence).append(accepted)
                continue
            accepted = _accept_or_stub(name, resolved, stub_tokens, binding="not-checked")
            (satisfied if "binding" in accepted else stub_evidence).append(accepted)
            continue
        if name in skips:
            reason = skips[name]
            ok, detail = _validate_skip_reason(reason)
            if not ok:
                invalid_skips.append({"name": name, "reason": reason, "detail": detail})
                continue
            skipped.append({"name": name, "reason": reason})
            continue
        missing.append(name)

    ok = not (
        missing
        or invalid_skips
        or missing_evidence_files
        or unbound_evidence
        or stub_evidence
    )
    return {
        "ok": ok,
        "kind": kind,
        "required": list(required),
        "satisfied": satisfied,
        "skipped": skipped,
        "missing": missing,
        "invalid_skips": invalid_skips,
        "missing_evidence_files": missing_evidence_files,
        "unbound_evidence": unbound_evidence,
        "stub_evidence": stub_evidence,
        # Reported, not inferred: a consumer reading `ok: true` cannot otherwise
        # tell a bound pass from a presence-only one.
        "binding_tokens": sorted(set(binding_tokens)),
        "binding_checked": bool(binding_tokens),
        # The floor runs wherever identity tokens were available -- the bound path,
        # or a presence-only caller that supplied `residual_tokens`. A pass with no
        # identity at all must not read as one that was checked for stub-ness.
        "residual_checked": bool(stub_tokens),
    }
