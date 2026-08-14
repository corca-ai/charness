"""Collect the on-disk lesson-evaluation records, and route the retro that owes one.

Two callers read the same facts and used to have no shared way to get them:

- `check_lesson_evaluation_continuity.py`, the GATE, which turns an unclaimed
  receipted session into an `unclaimed-emission` violation; and
- `skills/public/retro/scripts/plan_retro_run.py`, the ROUTER, which must send the
  retro author to exactly that session so it stops being unclaimed.

Before this module the gate owned the retro scan and the receipt scan inline, so a
router would have had to grow a second copy of both. A router that disagrees with
its gate about which sessions exist is worse than no router: it silently skips the
session the gate later fails the repo over. The scan lives here once; the shared
membership rule lives once in `lesson_evaluation_continuity_lib`.

This module reads. It never writes to the ledger, and never appends a score --
`record_lesson_score.py` is the only append path, and it runs by operator/agent
command at retro time, before the disposition line asserts the count.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import lesson_ledger_lib as ledger_lib
from scripts.prepare_packet_markdown_kind import file_is_prepare_packet_markdown_kind

RETRO_OUTPUT_RELATIVE = "charness-artifacts/retro"
SUMMARY_FILENAME = "recent-lessons.md"
LEDGER_BOOTSTRAP_SCRIPT = "init_lesson_ledger.py"
SCORE_SCRIPT = "record_lesson_score.py"

_PACKET_TITLE = re.compile(r"^# Retro Prepare Packet(?:\s+—\s+\S.*)?$")

STATE_EVALUATED = "evaluated"
STATE_NOT_CONFIGURED = "not-configured"
STATE_NOT_ESTABLISHED = "not-established"

# The questions the ledger contract FIXED and nothing ever asked (#627). Scoring
# was designed as a human judgment on purpose -- the spec refuses to infer it from
# score volume -- but a judgment that is never solicited is never made, which is
# how `effect-recorded=0` sat under `violations=0` over a loop that had never
# closed.
#
# WHAT A SCORE DOES AND DOES NOT DO. It moves the lesson's value/uncertainty
# statistic in `lesson_selection_preview_lib`, so it changes the WEIGHT at which a
# lesson is drawn. It does NOT revise the lesson's text: wording is rebuilt from
# the retro bullet corpus in `recent_lessons_lib`, which never reads a score, and
# the ledger contract's Eighth Slice is explicit that no score value creates an
# event. What a score leaves behind is an ANCHOR, and the anchor is what
# `render_lesson_lifecycle_review.py` gives `quality` to judge rewrite-in-place
# against. So the honest chain is score -> anchor -> a human disposition, never
# score -> rewrite; do not promise the second one here.
#
# `harmful` is asked FIRST and by name because the contract says `-3` is asked for
# explicitly: actively harmful is the most valuable and least volunteered signal,
# and an author walking a list of lessons volunteers praise long before blame.
#
# Kept here, in repo-owned evidence, rather than in the public retro skill: the
# skill core stays evaluator-generic and routes a contract it does not define.
SCORE_SOLICITATION = {
    "harmful": (
        "Which of these pushed you toward a WRONG action, or cost a read that returned "
        "nothing? Score those negative, `-3` for actively harmful. This is the least "
        "volunteered and most valuable signal; answer it before the positive ones."
    ),
    "changed_an_action": (
        "Which of these changed a specific action you took? Name the anchor: the decision, "
        "file, or command where it changed one."
    ),
    "read_and_failed": (
        "Which of these you READ and did not act on, in a session that then committed the "
        "class the lesson names? That is a negative score with an anchor, not a skip. An "
        "unscored miss leaves no anchor, and the anchor is the ledger's only record of WHY a "
        "lesson did not land -- recurrence count cannot distinguish a lesson that needs rewriting "
        "from one that was simply never consulted."
    ),
    "presented_before_the_work": (
        "Score only lessons from a list presented BEFORE the work they affected. Reading a "
        "lesson's wording here, at retro time, is not presentation and does not justify a "
        "score; if presentation is absent or uncertain, append nothing and use the "
        "`presentation-unproven` disposition."
    ),
    "anchor_rule": (
        "A score of magnitude 2 or more requires an anchor and is refused without one. "
        "Unanchored judgments belong at -1, 0, or +1."
    ),
    "no_score_is_valid": (
        "Scoring every lesson is NOT the goal and a high score count is not a health "
        "measure. Leave a lesson unscored when nothing observable happened, and record the "
        "affirmative `no-effect` disposition when that is true of the whole list."
    ),
}


def retro_output_dir(repo_root: Path) -> Path:
    return repo_root / RETRO_OUTPUT_RELATIVE


def summary_path(repo_root: Path) -> Path:
    return retro_output_dir(repo_root) / SUMMARY_FILENAME


def repo_or_installed_command(repo_root: Path, script_name: str, *args: str) -> str:
    """The runnable command for THIS layout, not for one repo's spelling.

    A consuming repo has no `scripts/` of its own -- it gets one beside this module
    inside the installed plugin. Emitting a bare `scripts/<name>.py` would tell a
    consuming author to run a file they do not have, the same "names a path nothing
    creates" defect that put the retro scaffold's north star line on the reported
    list. Repo-local wins when present, mirroring
    `scaffold_artifact_lib.validator_command`'s resolution order so a consumer cites
    the same script its broad gate would.
    """
    tail = " ".join(args)
    if (repo_root / "scripts" / script_name).is_file():
        return f"python3 scripts/{script_name} {tail}".rstrip()
    installed = Path(__file__).resolve().parent / script_name
    return f"python3 {installed} {tail}".rstrip()


def load_validated_ledger(repo_root: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Validate the ledger, then return `(sessions by id, score events)`.

    ONE read path for the gate and the router. They cannot agree about which
    sessions are UNCLAIMED until they agree about which sessions EXIST, and
    validation is not skippable on the way: an unvalidated payload can carry a
    session whose snapshot digest no receipt could ever match, which would then be
    reported as a receipt failure rather than as the ledger corruption it is.
    """
    output_dir = retro_output_dir(repo_root)
    ledger_lib.validate_lesson_ledger(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path(repo_root)
    )
    payload = json.loads(ledger_lib.lesson_ledger_path(output_dir).read_text(encoding="utf-8"))
    return (
        {event["session_id"]: event for event in payload["session_events"]},
        list(payload["score_events"]),
    )


def collect_retro_candidates(repo_root: Path) -> list[tuple[str, str]]:
    """Every eligible durable retro artifact, as `(repo-relative path, text)`.

    The generated digest and prepare packets are excluded because neither is a
    retro: `recent-lessons.md` is rewritten from the durable artifacts on every
    persist, and a packet is pre-retro evidence. Counting either would put a
    disposition duty on a file no author writes one in.
    """
    output_dir = retro_output_dir(repo_root)
    rows: list[tuple[str, str]] = []
    for path in sorted(output_dir.glob("*.md")):
        if path.name == SUMMARY_FILENAME or file_is_prepare_packet_markdown_kind(
            path,
            expected_kind="charness.retro_prepare_packet",
            expected_title_re=_PACKET_TITLE,
        ):
            continue
        text = path.read_text(encoding="utf-8")
        if continuity.is_eligible_retro(path, text):
            rows.append((path.relative_to(repo_root).as_posix(), text))
    return rows


def collect_dispositions(
    candidates: list[tuple[str, str]],
) -> tuple[list[tuple[str, dict[str, Any]]], list[dict[str, str]]]:
    """Parse one disposition per eligible retro; unparseable rows become violations."""
    dispositions: list[tuple[str, dict[str, Any]]] = []
    violations: list[dict[str, str]] = []
    for relpath, text in candidates:
        try:
            dispositions.append((relpath, continuity.parse_disposition(text)))
        except ValueError as exc:
            identifier = "missing-disposition" if "found 0" in str(exc) else "invalid-disposition"
            violations.append(continuity.violation(identifier, path=relpath, detail=str(exc)))
    return dispositions, violations


def collect_receipts(
    *, output_dir: Path, sessions: dict[str, dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    """Load and fully validate every emission receipt on disk.

    Validation is not optional here: `validate_receipt` re-digests the on-disk
    bundle against the receipt and the receipt against the ledger's frozen
    snapshot, which is what makes `score-without-emission-proof` mean something. A
    receipt that fails becomes an `invalid-receipt` violation and is NOT counted as
    proof of emission.
    """
    receipts: dict[str, dict[str, Any]] = {}
    violations: list[dict[str, str]] = []
    directory = continuity.receipt_directory(output_dir)
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        session_id = path.stem
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if raw.get("session_id") != session_id:
                raise continuity.LessonEvaluationError(
                    "receipt filename does not match session_id"
                )
            receipts[session_id] = continuity.validate_receipt(
                raw, sessions=sessions, output_dir=output_dir
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            violations.append(
                continuity.violation("invalid-receipt", session_id=session_id, detail=str(exc))
            )
    return receipts, violations


def disposition_references(
    dispositions: list[tuple[str, dict[str, Any]]],
) -> dict[str, list[str]]:
    """`session_id -> retro paths citing it`, skipping the `none` sentinel.

    Built the same way `reconcile_records` builds it, and handed to the same
    `unclaimed_receipted_sessions` helper, so the router's notion of "claimed"
    cannot drift from the gate's.
    """
    references: dict[str, list[str]] = {}
    for path, disposition in dispositions:
        session_id = disposition["session_id"]
        if session_id != "none":
            references.setdefault(session_id, []).append(path)
    return references


def _score_command_template(repo_root: Path, session_id: str, lesson_id: str, source_retro: str) -> str:
    return repo_or_installed_command(
        repo_root,
        SCORE_SCRIPT,
        "--repo-root",
        ".",
        "--event-id",
        f"{session_id}-{lesson_id}",
        "--session-id",
        session_id,
        "--lesson-id",
        lesson_id,
        "--source-retro",
        source_retro,
        "--score",
        "<-3..3>",
    )


def _bundle_lesson_texts(
    receipt: dict[str, Any] | None, *, sessions: dict[str, dict[str, Any]], output_dir: Path
) -> dict[str, str]:
    """`lesson_id -> the wording that was actually emitted`, from the frozen bundle.

    The ledger snapshot freezes IDs only, so a router that lists bare slugs asks an
    author to score `premise-not-checked-against-source` from its name. That is the
    re-derivation a loaded context skips, and skipping it is how a lesson gets a
    ceremonial score instead of a judged one.

    The bundle rather than a re-render: `load_session_bundle` re-digests the file
    against the receipt, so this returns the bytes that were emitted, not what the
    same seed would select today. Those differ as soon as any score lands, and
    showing today's selection under a past session's id would be a quiet lie about
    what was presented.

    Best-effort by design. A missing or unreadable bundle drops the texts and keeps
    the IDs; the receipt violation is already reported by the caller, and losing the
    convenience text must never turn into losing the routing.
    """
    if receipt is None:
        return {}
    try:
        content = continuity.load_session_bundle(
            receipt, sessions=sessions, output_dir=output_dir
        ).decode("utf-8")
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    texts: dict[str, str] = {}
    for line in content.splitlines():
        # The bundle's own emitted shape: `- <lesson-id> — <text>`.
        if not line.startswith("- "):
            continue
        lesson_id, separator, text = line[2:].partition(" — ")
        if separator and lesson_id.strip() and text.strip():
            texts[lesson_id.strip()] = text.strip()
    return texts


def _session_row(
    *,
    repo_root: Path,
    session_id: str,
    sessions: dict[str, dict[str, Any]],
    score_events: list[dict[str, Any]],
    output_dir: Path,
    source_retro: str,
    receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    lesson_ids = list(sessions[session_id]["snapshot"]["lesson_ids"])
    existing = [event for event in score_events if event.get("session_id") == session_id]
    scored = {event.get("lesson_id") for event in existing}
    texts = _bundle_lesson_texts(receipt, sessions=sessions, output_dir=output_dir)
    return {
        "session_id": session_id,
        # The FROZEN bundle, not a newest-file guess: `references/lesson-evaluation.md`
        # requires recovering the explicit bundle for the affected work before judging
        # effects, and the bundle is the only artifact whose bytes a receipt attests.
        "bundle_path": continuity.bundle_path(output_dir, session_id)
        .relative_to(repo_root)
        .as_posix(),
        "lesson_ids": lesson_ids,
        "existing_score_event_count": len(existing),
        # The questions, asked. Routing to a session told the author WHERE to score
        # and never WHAT to judge, so a lesson that was read and failed produced no
        # signal, left no anchor for `quality` to judge a rewrite against, and
        # returned at the same weight (#627). `solicitation` is the ask; `lessons`
        # is what it is asked about.
        "solicitation": dict(SCORE_SOLICITATION),
        "lessons": [
            {
                "lesson_id": lesson_id,
                # Absent when the bundle could not be read; never re-rendered from
                # current state, so a missing text reads as missing rather than as a
                # different lesson's wording.
                **({"lesson_text": texts[lesson_id]} if lesson_id in texts else {}),
                "already_scored": lesson_id in scored,
                "score_command_template": _score_command_template(
                    repo_root, session_id, lesson_id, source_retro
                ),
            }
            for lesson_id in lesson_ids
        ],
        "unscored_lesson_ids": [
            lesson_id for lesson_id in lesson_ids if lesson_id not in scored
        ],
        "score_command_templates": [
            _score_command_template(repo_root, session_id, lesson_id, source_retro)
            for lesson_id in lesson_ids
        ],
    }


def _not_configured(repo_root: Path) -> dict[str, Any]:
    return {
        "state": STATE_NOT_CONFIGURED,
        "configuration_status": "no-evaluator-declared",
        "reason": (
            "this repo declares no lesson evaluator, so the disposition floor is inert and no "
            "retro owes a `Lesson evaluation:` line"
        ),
        "opt_in_command": repo_or_installed_command(
            repo_root, LEDGER_BOOTSTRAP_SCRIPT, "--repo-root", "."
        ),
        "sessions": [],
    }


def lesson_session_routing(repo_root: Path, *, source_retro: str | None = None) -> dict[str, Any]:
    """Which declared lesson session, if any, THIS retro owes a score and disposition for.

    Three states, spelled the way `check_auto_trigger.py` spells them:

    - `not-configured`: no ledger. The floor is inert; nothing is owed.
    - `not-established`: a ledger exists but no receipted session is unclaimed --
      or the ledger could not be read at all. Either way this retro has no
      presented list to score, so `not-evaluated / missing-start` is the only
      honest disposition and it is emitted here verbatim from the library
      constant rather than retyped.
    - `evaluated`: one or more receipted, unclaimed sessions, each with its frozen
      lesson ids, its bundle path, and a filled-in score command.

    `before=None` on purpose: a session declared THIS MORNING is exactly the one
    tonight's retro must dispose, and the gate's `before=as_of` window would hide
    it from the router while still demanding it tomorrow.
    """
    output_dir = retro_output_dir(repo_root)
    ledger_path = ledger_lib.lesson_ledger_path(output_dir)
    if not ledger_path.is_file():
        return _not_configured(repo_root)
    try:
        sessions, score_events = load_validated_ledger(repo_root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # A ledger that will not validate cannot establish that nothing is owed;
        # reporting `no session` here would be a `triggered: false` for a probe
        # that never ran (#622).
        return {
            "state": STATE_NOT_ESTABLISHED,
            "configuration_status": "ledger-unreadable",
            "reason": "a lesson evaluator is declared but its ledger could not be validated",
            "undetermined": [f"{type(exc).__name__}: {exc}"],
            "sessions": [],
        }
    candidates = collect_retro_candidates(repo_root)
    dispositions, _disposition_violations = collect_dispositions(candidates)
    receipts, receipt_violations = collect_receipts(output_dir=output_dir, sessions=sessions)
    unclaimed = continuity.unclaimed_receipted_sessions(
        receipts=receipts, references=disposition_references(dispositions), before=None
    )
    if not unclaimed:
        payload_out: dict[str, Any] = {
            "state": STATE_NOT_ESTABLISHED,
            "configuration_status": "no-unclaimed-session",
            # NOT "no list was presented": nothing here can observe presentation,
            # and since the SessionStart lesson block ships, a list very often WAS
            # emitted into a session that was never declared. The observable fact
            # is the absence of an unclaimed RECEIPT, and `missing-start` is the
            # honest disposition for exactly that, so say only that much (08-13
            # contract, Non-Goals: never claim stdout was read, used, or
            # beneficial -- which its negation asserts just as unobservably).
            "reason": (
                "a lesson evaluator is declared, but no receipted lesson session is unclaimed by "
                "an eligible retro, so this retro has no declared session whose emission it could "
                "dispose"
            ),
            "honest_disposition": continuity.disposition_line(
                continuity.MISSING_START_DISPOSITION
            ),
            "sessions": [],
        }
        if receipt_violations:
            payload_out["undetermined"] = [item["detail"] for item in receipt_violations]
        return payload_out
    return {
        "state": STATE_EVALUATED,
        "configuration_status": "unclaimed-session-present",
        "reason": (
            "a receipted lesson session is unclaimed; score its frozen lessons BEFORE writing the "
            "disposition line, because the disposition declares the score count and "
            "`score-count-mismatch` fires when it disagrees with the observed events"
        ),
        "sessions": [
            _session_row(
                repo_root=repo_root,
                session_id=session_id,
                sessions=sessions,
                score_events=score_events,
                output_dir=output_dir,
                source_retro=source_retro or "<repo-relative path of the retro being written>",
                receipt=receipts.get(session_id),
            )
            for session_id in unclaimed
        ],
    }
