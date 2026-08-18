#!/usr/bin/env python3
"""Behavioral probe engine for the closeout floor x classification x carrier matrix.

`#586` names a class of check that exists, is correct, and is wired to one carrier
but not to the one a disposition requires. Six rung-1 closeout floors compose into a
close verdict, each declaring its own applicability rule in a different module, and
no surface states them together -- so learning which floors a light close actually
reaches takes reading five modules.

**This engine never greps and never imports a floor to ask what it says.** For each
`(carrier, classification)` it runs the REAL closeout ingress twice: once on a body
built to pass every floor, and once on the same body with exactly one floor's input
broken. A floor `fires` for that pair iff the ingress's own verdict flips. That is
what the CALLER gets, which is the only question `#586` is about -- a matrix built by
reading the modules would assert what the code SAYS and would itself be a check that
never fires on the wired path.

`fires` requires TWO things: the verdict flipped, AND the carrier's own report
attributes the refusal to the floor whose input was broken. Without the second, a
floor could be unwired from a carrier entirely and still read `fires` as long as some
other check refused the same broken body. A refusal that cannot be attributed is
`refused-elsewhere`, which no declared state accepts.

WHAT THE PROBE CANNOT SEE. It observes `fires` / `inert` / `input-refused`. Whether an
inert floor is `skipped-by-design`, `not-applicable`, or an `undispositioned` gap is a
JUDGMENT the declaration carries and this engine does not verify. Cell reasons are
prose and are never checked against behavior.

ENTER WHERE THE CALLER ENTERS. `close-with-comment` is probed through
`issue_close.evaluate_close_comment_carrier` -- the pre-mutation segment of the real
close path, extracted for exactly this reason -- not through the floor function it
calls, because the readback wiring that decides whether the consolidation facts reach
the verdict lives in the caller. The release lane is probed at
`preflight_release_issues` for the same reason and at real cost: entering one layer
lower measured the OPPOSITE answer for two cells, because that lane runs its own
behavioral-verdict floor first with a fixed classification.

The hermetic world every probe runs inside lives in `closeout_floor_matrix_world`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

import yaml

from scripts.closeout_floor_matrix_world import (
    DESTINATION,
    NUMBER,
    REPO,
    ProbeWorld,
    skill_module,
)

# The six rung-1 floors that compose a close verdict. `closeout_authorization` is
# deliberately ABSENT and the artifact records why: its protected-target instance was
# retired by operator ruling on 2026-08-10, so no probe can make it fire, and a row
# that can never fire is the very shape `#586` exists to remove.
FLOORS = (
    "source_preservation",
    "behavioral_verdict",
    "hotl_dispositions",
    "ai_provenance",
    "resolution_critique",
    "consolidation_readback",
    # Added 2026-08-18: one rung below `behavioral_verdict`. That floor refuses SILENCE
    # about behavior; this one refuses a behavioral CLAIM that no probe record
    # establishes. Declaring it here is what makes its per-carrier reach measured rather
    # than asserted -- the gate re-derives every cell by running the real ingresses.
    "probe_record",
)

# Findings are hoisted to the front of the refusal detail, so this cap only ever
# truncates trailing context -- never the signature a declaration pins.
REFUSAL_DETAIL_CHARS = 4000

# Every ingress that renders a closeout verdict. `commit-msg` and `release-draft` are
# separate carriers even though both delegate to `verify_closeout`, because each adds
# its own decisions on the way in -- and those decisions are what a reader gets wrong.
CARRIERS = (
    "direct-commit",
    "pr-body",
    "manual-fallback",
    "close-with-comment",
    "commit-msg",
    "release-draft",
)


_LEDGER: dict[str, tuple[str, ...]] = {
    "bug": (
        "JTBD: keep every closeout floor's applicability legible on one surface.",
        "Root cause: each floor declared its own applicability in a different module.",
        "Debug artifact: charness-artifacts/debug/closeout-floor-matrix.md",
        "Siblings: decision: swept every closeout carrier; proof: scripts/check_closeout_floor_matrix.py",
        "Prevention: the behavioral matrix validator refuses an undeclared cell.",
    ),
    "feature": (
        "JTBD: keep every closeout floor's applicability legible on one surface.",
        "Boundary: the matrix says where a floor RUNS, never whether it is sufficient.",
        "Resolution brief: charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md",
        "Implementation: scripts/closeout_floor_matrix_lib.py probes each ingress twice.",
        "Prevention: the behavioral matrix validator refuses an undeclared cell.",
    ),
    "question": (
        "JTBD: learn which floors a light close actually skips.",
        "Answer: four of six, on the consolidated disposition.",
    ),
    "decision-needed": (
        "JTBD: decide whether the consolidated skips stay.",
        "Decision: recorded in the matrix artifact, one cell at a time.",
    ),
    "consolidated": (
        "JTBD: fold this probe issue into the umbrella that now owns the work.",
        f"Consolidated into: #{DESTINATION}",
    ),
}
_LEDGER["deferred-work"] = _LEDGER["feature"]

# One line per floor whose input is a body field. Removing (or, for HOTL, untyping)
# the line is how that floor's input is broken.
_FLOOR_LINE = {
    "behavioral_verdict": (
        "Behavior: confirmed through the matrix probe's own carrier run, "
        "a channel distinct from the close itself"
    ),
    "hotl_dispositions": "HOTL: local-only-by-contract - this probe body has no live human loop",
    "ai_provenance": "AI-provenance: authored by an agent session.",
    "resolution_critique": (
        "Critique: blocked the probe host does not spawn a bounded reviewer for a fixture body"
    ),
    # The matrix probe body's `Behavior:` line CLAIMS a verification, so the probe-record
    # floor is live on it. A fixture body has no real measurement behind it, so it answers
    # in the floor's own typed vocabulary -- and deleting this line is exactly how the
    # floor's input gets broken, no special case needed.
    "probe_record": (
        "Probe record: local-only-by-contract - the matrix probe body carries no real measurement"
    ),
}
# The HOTL floor is presence-GATED: deleting the line makes it inert rather than
# refused, so breaking it means an entry that mentions a status without leading with
# one -- the undispositioned shape the floor exists to catch.
_HOTL_BROKEN = "HOTL: not verified yet, the runner was red when this probe body was written"
# The source-preservation floor is presence-gated the other way round: a body with no
# `Source origin:` is inert, so breaking it means ADDING an external origin with none
# of the three preservation forms.
_SOURCE_BROKEN = "Source origin: a Slack thread in the operator's workspace"
# Lines the `consolidated` disposition counts as REPAIR CLAIMS. A consolidated close
# asserts a move, not a fix, so a carrier that carries these is refused outright --
# which means the baseline cannot carry them and these floors' inputs cannot exist on
# a consolidated body at all. Measured, not assumed: `observe` confirms the refusal.
_REPAIR_CLAIM_FLOORS = ("behavioral_verdict", "hotl_dispositions", "resolution_critique", "probe_record")


def probe_body(classification: str, carrier: str, broken_floor: str | None) -> str:
    """The carrier body for one probe: baseline when `broken_floor` is None."""
    lines = [f"Closes #{NUMBER}", "", f"Classification: {classification}"]
    lines.extend(_LEDGER[classification])
    if carrier == "manual-fallback":
        lines.append("Manual close reason: operator-directed-manual-close")
    for floor, line in _FLOOR_LINE.items():
        if classification == "consolidated" and floor in _REPAIR_CLAIM_FLOORS:
            continue
        if floor == broken_floor:
            if floor == "hotl_dispositions":
                lines.append(_HOTL_BROKEN)
            continue
        lines.append(line)
    if broken_floor == "source_preservation":
        lines.append(_SOURCE_BROKEN)
    return "\n".join(lines) + "\n"


def _verify(world: ProbeWorld, carrier: str, classification: str, body: str) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if carrier == "direct-commit":
        kwargs["commit_ref"] = world.commit(body)
    else:
        kwargs["body_file"] = world.write("carrier-body.md", body)
    if carrier == "manual-fallback":
        kwargs["manual_fallback_reason"] = "operator-directed-manual-close"
    return world.verifier.verify_closeout(
        repo_root=world.root, repo=REPO, numbers=[NUMBER],
        classification=classification, carrier=carrier, backend=world.backend, **kwargs
    )


def _close_with_comment(
    world: ProbeWorld, classification: str, body: str, broken: str | None
) -> dict[str, Any]:
    reason = "not planned" if classification == "consolidated" else "completed"
    return world.closer.evaluate_close_comment_carrier(
        REPO, NUMBER, body, repo_root=world.root, classification=classification,
        backend=world.backend, reason=reason,
    )


def _release_draft(
    world: ProbeWorld, classification: str, body: str, broken: str | None
) -> dict[str, Any]:
    """The release family's ingress, entered at `preflight_release_issues`.

    Entering one layer lower -- at `validate_release_closeout_commit_message`, which
    is where the release message helper does the issue-owned checks -- measured the
    WRONG answer, and round-1 review caught it. `preflight_release_issues` runs its
    own behavioral-verdict floor first, over a SEPARATE input channel
    (`--close-issue-behavior`, not the carrier body) and with a FIXED classification
    (`_RELEASE_BEHAVIORAL_CLASSIFICATION = "feature"`), so on this carrier the floor
    applies to `question` and `decision-needed` too. Probed from below, those cells
    read `skipped-by-design` while a real release close is refused -- an instance of
    the exact `#586` shape, asserted backwards inside the artifact built to expose it.
    """
    closeout = skill_module(world.source_root, "release", "release_issue_closeout")
    carrier_file = world.write("release-carrier.md", body)
    # The behavioral verdict travels BESIDE the carrier on this lane (`--close-issue-
    # behavior`), not inside it -- so the channel is driven by which floor is being
    # broken, never derived from the body. Round 2 caught the derived version: for
    # `consolidated`, whose body cannot carry a `Behavior:` line at all, deriving from
    # the body emptied the CLI channel too, and the declaration then recorded that
    # probe artifact as a fact about the carrier. A real operator supplies the flag
    # regardless of what the carrier file says.
    behavior_lines = [] if broken == "behavioral_verdict" else [_FLOOR_LINE["behavioral_verdict"]]
    # The probe record reaches this lane the same way the behavioral verdict does -- as a
    # CLI-shaped argument, not from the carrier file -- so the baseline must supply it or
    # the release lane refuses a body built to pass every floor.
    probe_lines = [] if broken == "probe_record" else [_FLOOR_LINE["probe_record"]]
    payload: dict[str, Any] = {
        "commit_message": "chore(release): closeout floor matrix probe",
        "tag_name": "v0.0.0-closeout-floor-matrix-probe",
        "quality_command": "bash scripts/run-quality.sh",
    }
    try:
        closeout.preflight_release_issues(
            world.root, repo=REPO, issue_numbers=[NUMBER], payload=payload,
            run=world.run_backend, behavior_lines=behavior_lines,
            probe_record_lines=probe_lines,
            classification=classification, carrier_file=carrier_file,
            carrier_source="closeout-floor-matrix-probe",
        )
    except SystemExit as exc:
        # This lane refuses by RAISING, and a raise carries no per-floor attribution --
        # so every release cell read `refused-elsewhere`. The attribution is already in
        # `payload`: each floor's record is written there BEFORE its refusal raises.
        # Read the structured record rather than parsing the exit message.
        report = dict(payload.get("issue_closeout_draft_validation") or {})
        report["ok"] = False
        verdict = payload.get("issue_closeout_behavioral_verdict")
        if isinstance(verdict, dict) and not verdict.get("ok", True):
            report["behavioral_verdict"] = verdict
        probe = payload.get("issue_closeout_probe_record")
        if isinstance(probe, dict) and not probe.get("ok", True):
            report["probe_record"] = probe
        report["release_refusal"] = str(exc)[:400]
        return report
    return payload["issue_closeout_draft_validation"]


def _commit_msg(
    world: ProbeWorld, classification: str, body: str, broken: str | None
) -> dict[str, Any]:
    """The commit-msg hook, run as the subprocess a git hook actually runs.

    PATH-shimmed rather than injected: this carrier hardcodes ``backend={"id": "gh"}``,
    so an injected backend would probe a path the hook does not have.
    """
    path = world.write("commit-msg.txt", body)
    env = dict(os.environ)
    env["PATH"] = f"{world.bin}{os.pathsep}{env.get('PATH', '')}"
    result = subprocess.run(
        [
            sys.executable,
            str(world.source_root / "scripts" / "check_issue_closeout_commit_msg.py"),
            "--repo-root", str(world.root),
            "--commit-msg-file", str(path),
            "--repo", REPO,
        ],
        cwd=world.root, env=env, capture_output=True, text=True,
    )
    try:
        verdict = yaml.safe_load(result.stdout)
    except yaml.YAMLError as exc:
        raise RuntimeError(
            f"commit-msg carrier produced no readable verdict (exit={result.returncode}): "
            f"{result.stdout[-400:]!r} {result.stderr[-400:]!r}"
        ) from exc
    if not isinstance(verdict, dict):
        # `yaml.safe_load` returns a scalar where `json.loads` raised, so the mapping
        # check keeps a non-payload stdout a refusal rather than a silent bad verdict.
        raise RuntimeError(
            f"commit-msg carrier produced no readable verdict (exit={result.returncode}): "
            f"{result.stdout[-400:]!r} {result.stderr[-400:]!r}"
        )
    return verdict


INGRESSES: dict[str, Callable[[ProbeWorld, str, str, "str | None"], dict[str, Any]]] = {
    "direct-commit": lambda w, c, b, _f: _verify(w, "direct-commit", c, b),
    "pr-body": lambda w, c, b, _f: _verify(w, "pr-body", c, b),
    "manual-fallback": lambda w, c, b, _f: _verify(w, "manual-fallback", c, b),
    "close-with-comment": _close_with_comment,
    "commit-msg": _commit_msg,
    "release-draft": _release_draft,
}


def run_ingress(
    world: ProbeWorld, carrier: str, classification: str, body: str, broken: str | None = None
) -> tuple[bool, str, set[str]]:
    """`(verdict_ok, refusal_detail, floors_that_refused)` from the real ingress.

    A raise is a REFUSAL, not a probe error: `close-with-comment` refuses a
    `consolidated` close with the wrong `--reason` by raising, and the release lane
    refuses by `SystemExit`. Swallowing those as engine failures would hide
    carrier-level refusals behind a stack trace -- but a raise carries no per-floor
    attribution, so the third element is empty and the caller must treat the cell as
    unattributed rather than as this floor firing.
    """
    try:
        report = INGRESSES[carrier](world, classification, body, broken)
    except (RuntimeError, SystemExit) as exc:
        return False, f"{exc.__class__.__name__}: {exc}"[:REFUSAL_DETAIL_CHARS], set()
    if report.get("ok"):
        return True, "", set()
    return (
        False,
        json.dumps(_refusal_detail(report), default=str)[:REFUSAL_DETAIL_CHARS],
        _refusing_floors(report),
    )


def _sections(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Every verdict record in a carrier's report, including the per-issue reports the
    commit-msg hook nests one level down."""
    nested = report.get("reports")
    return [report] + [item for item in (nested or []) if isinstance(item, dict)]


def _refusing_floors(report: dict[str, Any]) -> set[str]:
    """WHICH floors refused, read from the carrier's own report.

    Without this, `fires` means only "the carrier refused a body in which this floor's
    input was broken" -- so deleting a floor from a carrier's composition would still
    read `fires` as long as any OTHER check happened to refuse the same body. The
    attribution was already being computed for the human-facing detail and thrown
    away; round-1 review named it, and it is what the cell's meaning rests on.
    """
    refusing: set[str] = set()
    for section in _sections(report):
        preservation = section.get("source_preservation")
        if isinstance(preservation, dict) and preservation.get("missing"):
            refusing.add("source_preservation")
        # `probe_record` reports the same `applies`/`ok` shape as these three, so it reads
        # here rather than needing its own clause. Omitting it made every cell
        # `refused-elsewhere`: the carrier DID refuse the broken body, but could not say
        # the probe-record floor was why -- which is exactly the unattributed refusal this
        # function exists to refuse to count.
        for floor in ("behavioral_verdict", "hotl_dispositions", "ai_provenance", "probe_record"):
            record = section.get(floor)
            if isinstance(record, dict) and record.get("applies") and not record.get("ok", True):
                refusing.add(floor)
        # Two spellings, because the carriers disagree: `verify_closeout` reports
        # `resolution_critique_check`, the close-comment floor reports
        # `resolution_critique`. Reading only one is how attribution goes quiet.
        for key in ("resolution_critique_check", "resolution_critique"):
            record = section.get(key)
            if isinstance(record, dict) and not record.get("ok", True):
                refusing.add("resolution_critique")
        fields = list(section.get("missing_fields") or []) + list(
            section.get("missing_ledger_fields") or []
        )
        if any(str(field).startswith("consolidation:") for field in fields):
            refusing.add("consolidation_readback")
    return refusing


def _refusal_detail(report: dict[str, Any]) -> dict[str, Any]:
    """The refusal, with everything a reader (or the gate's `refusal_signature`) needs
    HOISTED to the front.

    The commit-msg hook keeps its findings inside a nested per-issue report, several
    hundred characters in behind a temp path whose length depends on `$TMPDIR` -- so a
    signature match against a truncated blob was passing or failing by accident of the
    host's temp directory. Every nested finding is lifted here instead.
    """
    detail: dict[str, Any] = {"refusing_floors": sorted(_refusing_floors(report))}
    for key in ("status", "missing_fields", "missing_close_keywords", "missing_ledger_fields"):
        values = [
            value
            for section in _sections(report)
            for value in (section.get(key) or ([section[key]] if isinstance(section.get(key), str) else []))
        ]
        if values:
            detail[key] = values
    detail.setdefault("status", report.get("status"))
    for nested in ("reports", "consolidation_readback"):
        if report.get(nested):
            detail[nested] = report[nested]
    return detail


def observe(world: ProbeWorld, carrier: str, classification: str) -> dict[str, Any]:
    """The differential observation for one `(carrier, classification)` pair.

    Baseline first. A baseline the ingress REFUSES is not a failed probe -- it is a
    pair the carrier does not accept at all (a `consolidated` close on a carrier that
    auto-closes via keyword), and every floor there is unobservable rather than inert.
    """
    # No destination reset here: `ProbeWorld` starts OPEN and `destination_closed` is
    # now the only thing that sets CLOSED, restoring on the way out. One owner for the
    # invariant beats a defensive reset that would hide a leak rather than prevent it.
    baseline = probe_body(classification, carrier, None)
    baseline_ok, baseline_detail, _ = run_ingress(world, carrier, classification, baseline, None)
    if not baseline_ok:
        return {"baseline": "refused", "refusal_detail": baseline_detail, "floors": {}}
    floors: dict[str, str] = {}
    for floor in FLOORS:
        if floor == "consolidation_readback":
            floors[floor] = _readback_outcome(world, carrier, classification)
            continue
        broken = probe_body(classification, carrier, floor)
        if broken == baseline and not _channel_floor(carrier, floor):
            # The baseline never carried this floor's input, so removing it proves
            # nothing. Add it instead: a carrier that REFUSES the input is a carrier
            # where the floor's input cannot exist, which is a different fact from a
            # floor that reads the input and ignores it.
            forced_ok, _, _ = run_ingress(world, carrier, classification, _with_line(baseline, floor))
            floors[floor] = "inert" if forced_ok else "input-refused"
            continue
        floors[floor] = _outcome(
            run_ingress(world, carrier, classification, broken, floor), floor
        )
    return {"baseline": "passes", "floors": floors}


def _readback_outcome(world: ProbeWorld, carrier: str, classification: str) -> str:
    """The consolidation readback, probed on a body that ACTUALLY carries a destination.

    This floor's input is not one body line but a pair: a `Consolidated into:` anchor
    AND the destination's tracker state. Round 2 found the first version breaking only
    the second half, on bodies whose classification never emits the first -- so
    `destinations(body)` was empty, the readback returned early regardless of its
    applicability gate, and all 30 non-consolidated cells were unmovable. A row that
    can never fire is the shape this artifact excludes `closeout_authorization` for;
    it must not be smuggled back in as thirty cells.

    So every classification gets the anchor here. Nothing else refuses it: the
    consolidated ledger's extra checks run only for `consolidated`
    (`issue_closeout_classification_ledger.build_extra_checks`), and a `bug` body
    carrying the line is simply never read -- which is exactly the claim the cell makes.
    """
    body = probe_body(classification, carrier, None)
    if f"#{DESTINATION}" not in body:
        body = body.rstrip("\n") + f"\nConsolidated into: #{DESTINATION}\n"
    control_ok, control_detail, _ = run_ingress(world, carrier, classification, body)
    if not control_ok:
        # The anchor itself was refused, so the CLOSED run would prove nothing.
        return "input-refused" if control_detail else "refused-elsewhere"
    with world.destination_closed():
        return _outcome(
            run_ingress(world, carrier, classification, body), "consolidation_readback"
        )


def _outcome(observation: tuple[bool, str, set[str]], floor: str) -> str:
    """`fires` only when THIS floor is the one that refused.

    A refusal the carrier cannot attribute to this floor is `refused-elsewhere`, a
    state no declaration accepts -- so a probe that breaks (or a mutation that flips
    the verdict through some other check) surfaces as a gate failure instead of
    quietly reading as a firing floor.
    """
    ok, _detail, refusing = observation
    if ok:
        return "inert"
    return "fires" if floor in refusing else "refused-elsewhere"


def _channel_floor(carrier: str, floor: str) -> bool:
    """True when this floor's input reaches the carrier BESIDE the body.

    `release-draft` takes the behavioral verdict through `--close-issue-behavior`, so
    an identical body does NOT mean the input was absent -- the `broken == baseline`
    shortcut would misread it as `input-refused` on a consolidated body.
    """
    return carrier == "release-draft" and floor in ("behavioral_verdict", "probe_record")


def _with_line(body: str, floor: str) -> str:
    return body.rstrip("\n") + "\n" + _FLOOR_LINE[floor] + "\n"


def observe_matrix(source_root: Path, root: Path | None = None) -> dict[str, Any]:
    """Every `(carrier, classification)` pair, observed. Classifications are read
    LIVE from the verifier, so a seventh classification breaks totality here rather
    than shipping an unmeasured disposition."""
    with tempfile.TemporaryDirectory(prefix="closeout-floor-matrix-") as tmp:
        world = ProbeWorld(source_root, Path(root) if root else Path(tmp) / "world")
        classifications = list(world.verifier.CLASSIFICATIONS)
        return {
            "classifications": classifications,
            "carriers": list(CARRIERS),
            "floors": list(FLOORS),
            "pairs": {
                f"{carrier}|{classification}": observe(world, carrier, classification)
                for carrier in CARRIERS
                for classification in classifications
            },
        }
