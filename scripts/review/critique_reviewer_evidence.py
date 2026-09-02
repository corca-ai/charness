"""Artifact-side validation for what a parent recorded about the reviewer it spawned.

One cohesive concern, two claims that are routinely confused:

- *tier* evidence — which reviewer the parent asked the host for, and whether the
  host is known to have applied that request (`requested_fields_sent` is a send,
  not an application);
- *delivery* state — whether that reviewer's findings actually reached the parent.

They are separated deliberately. A reviewer can be spawned at the right tier, run
correctly, keep a clean rail-1 boundary, and still deliver nothing the parent can
read: the spawn call shape selects the delivery channel, and the losing channel
strands a complete review in a mailbox the parent has no tool to open. A closeout
that recorded `Fresh-eye satisfaction: parent-delegated` plus clean tier evidence
asserted exactly that false confidence, so delivery gets its own typed field
rather than riding boundary or tier state.

Both floors are presence + typed-value only. Whether the findings were *good*
stays reviewer judgment, the same boundary the fresh-eye and boundary-ownership
floors hold. See the `Result Delivery` section of
skills/shared/references/fresh-eye-subagent-review.md.
"""

from __future__ import annotations

import importlib.util
import re
from datetime import date
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_artifact_validator = import_repo_module(__file__, "scripts.artifacts.artifact_validator")
ValidationError = _artifact_validator.ValidationError


def _load_worker_carrier():
    """Load the package-owned carrier without consumer PYTHONPATH imports."""
    here = Path(__file__).resolve()
    for ancestor in (here.parent, *here.parents):
        for candidate in (
            ancestor / "shared" / "scripts" / "reviewer_worker_carrier.py",
            ancestor / "skills" / "shared" / "scripts" / "reviewer_worker_carrier.py",
        ):
            if not candidate.is_file():
                continue
            spec = importlib.util.spec_from_file_location(
                "charness_reviewer_worker_carrier", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("package reviewer_worker_carrier.py not found")


_worker_carrier = _load_worker_carrier()

WORKER_REPORT_FIELDS = _worker_carrier.WORKER_REPORT_FIELDS
WorkerCarrierError = _worker_carrier.WorkerCarrierError
validate_worker_report_carrier = _worker_carrier.validate_worker_report_carrier

REVIEWER_TIER_HEADING = "## Reviewer Tier Evidence"
REVIEWER_TIER_REQUIRED_FIELDS = (
    "requested tier",
    "requested spawn fields",
    "host exposure state",
    "application state",
)
REVIEWER_EXECUTION_MODE_FIELD = "execution mode"
REVIEWER_EXECUTION_MODE_VALUES = ("file-backed-worker", "typed-subagent")
DEFAULT_REVIEWER_EXECUTION_MODE = REVIEWER_EXECUTION_MODE_VALUES[0]
TYPED_SUBAGENT_EXECUTION_MODE = "typed-subagent"
REVIEWER_TIER_HOST_STATES = frozenset(
    {
        "pending-parent-spawn",
        "requested_fields_sent",
        "metadata-hidden",
        "host-defaulted",
        "unsupported",
        "applied",
    }
)

# `RULE_DATE = landing_day + 1` grandfather shape (lands 2026-07-25, enforced the
# next day), mirroring the fresh-eye and boundary-ownership floors. Clone-safe:
# an in-file constant, not mtime.
DELIVERY_STATE_RULE_DATE = date(2026, 7, 26)
DELIVERY_STATE_FIELD = "delivery state"
DELIVERY_STATE_VALUES = (
    "findings-received",
    "findings-recovered-from-transcript",
    "spawn-accepted-no-delivery",
    "pending-parent-spawn",
)
TYPED_REVIEWER_TIER_FIELDS = REVIEWER_TIER_REQUIRED_FIELDS + (
    DELIVERY_STATE_FIELD,
    REVIEWER_EXECUTION_MODE_FIELD,
)
DELIVERY_STATE_VALUES_SUMMARY = (
    "`findings-received` / `findings-recovered-from-transcript <signal>` / "
    "`spawn-accepted-no-delivery <signal>` / `pending-parent-spawn`"
)
_NO_DELIVERY = "spawn-accepted-no-delivery"
# The scaffold's own defaults for the spawn record: no reviewer requested yet, no
# reviewer spawned yet. They are the right defaults — an unedited scaffold must
# not claim a review happened — but nothing read them back against the artifact's
# `Fresh-eye satisfaction:` claim, so an author who edited only that one line
# shipped `parent-delegated` (a COMPLETED delegation) over a record stating the
# parent had not spawned anything. See `validate_delegation_consistency`.
_PENDING_SPAWN = "pending-parent-spawn"
# `TODO`/`TBD` in a required tier field is an unedited scaffold stub, not a
# record. Only these two: the corpus writes `n/a` 72 times as an HONEST answer
# ("this host exposes no tier to request"), and refusing it would demand a
# fabricated value for a thing that does not exist — the same misreading the
# issue-ledger `N/A` floor already corrected. Mirrors the `todo`-in-remainder
# rejection that `opens_with_typed_value` applies to the typed floors.
_STUB_VALUE_RE = re.compile(r"^(todo|tbd)\b")
# Both typed values assert a delegation that COMPLETED, so both are contradicted
# by a spawn record that says nothing was spawned.
COMPLETED_DELEGATION_CLAIMS = ("parent-delegated", "nested-delegated")
# Transcript recovery is a delivery FAILURE that happened to be salvageable, not a
# clean delivery. Without its own value it would be recorded as `findings-received`
# and the diagnostic path would quietly become the normal one — enforcement rather
# than framing, which is what the reviewer-result helper needs to not erode the
# spawn-shape discipline. Signal-bearing like its sibling: name what dropped it.
_RECOVERED = "findings-recovered-from-transcript"
# Mirrors `validate_critique_artifacts._LEADING_MARKUP_RE` so the typed check and
# the signal check normalize identically; see the comment at the use site.
_LEADING_MARKUP_RE = re.compile(r"^[\s`*_\"'>\-]+")


def validate_reviewer_tier_evidence(
    path: Path,
    text: str,
    *,
    section_field_map,
) -> None:
    fields = section_field_map(text, REVIEWER_TIER_HEADING)
    missing = [field for field in REVIEWER_TIER_REQUIRED_FIELDS if not fields.get(field)]
    if missing:
        raise ValidationError(f"{path}: reviewer tier evidence missing fields: {missing}")
    # Presence was tested with bare truthiness, so the scaffold's own
    # `Requested tier: TODO the fresh-eye reviewer tier requested.` satisfied the
    # floor permanently — the block's defaults validated themselves.
    # Normalize leading markup FIRST, exactly as `_opens_with_typed_value` and the
    # delivery-signal check below already do. `_section_field_map` strips only
    # backticks, so testing the raw value let `**TODO**`, `_TBD_` and `> TODO`
    # through — the unedited stub wearing three characters of markup, which is how
    # this surface has been defeated before.
    stubs = [
        field
        for field in REVIEWER_TIER_REQUIRED_FIELDS
        if _STUB_VALUE_RE.match(_LEADING_MARKUP_RE.sub("", fields[field].strip().lower()))
    ]
    if stubs:
        raise ValidationError(
            f"{path}: reviewer tier evidence fields {stubs} still carry the unedited scaffold "
            "`TODO`/`TBD` placeholder; record what was actually requested and what the host "
            "actually reported (`n/a` is a valid answer when the host exposes no such control)."
        )
    execution_mode = fields.get(REVIEWER_EXECUTION_MODE_FIELD)
    if execution_mode and execution_mode not in REVIEWER_EXECUTION_MODE_VALUES:
        raise ValidationError(
            f"{path}: reviewer tier `{REVIEWER_EXECUTION_MODE_FIELD}` `{execution_mode}` must be one of "
            f"{REVIEWER_EXECUTION_MODE_VALUES}"
        )
    state = fields["host exposure state"]
    if state not in REVIEWER_TIER_HOST_STATES:
        raise ValidationError(
            f"{path}: reviewer tier host exposure state `{state}` must be one of "
            f"{sorted(REVIEWER_TIER_HOST_STATES)}"
        )
    if state == "applied" and not fields["application state"].lower().startswith("host-confirmed:"):
        raise ValidationError(
            f"{path}: reviewer tier evidence may use `applied` only with "
            "`Application state: host-confirmed: <signal>`"
        )


def validate_delegation_consistency(
    path: Path,
    text: str,
    fresh_eye_status: str,
    *,
    section_field_map,
) -> None:
    """Refuse a `parent-delegated` claim the artifact's OWN spawn record contradicts.

    Every floor on this surface reads one field and judges it alone, so the two
    halves of the same fact were never compared: `Fresh-eye satisfaction:
    parent-delegated` asserts a completed delegation, while `Host exposure state:
    pending-parent-spawn` states no reviewer was ever spawned and `Delivery state:
    pending-parent-spawn` states no findings ever arrived. An artifact could carry
    both and validate green — the #386 same-observer rubber stamp with the
    disproof sitting six lines below the claim.

    This is not a new floor. It is the read-back the existing floors imply: both
    fields were already required and already typed, and nothing consumed them
    together. Correctness of a delegation that IS internally consistent stays
    reviewer judgment, the same boundary the sibling floors hold.

    Covers `nested-delegated` as well as `parent-delegated`. Both assert a
    delegation that COMPLETED; keying only on the parent spelling let the same
    false confidence through under the other typed value the scaffold offers as a
    co-equal choice. (The presence floor's separate, accepted gap — that
    `nested-delegated` links to no downstream evidence — is about which evidence
    is required, not about accepting a record that contradicts the claim.)

    Ungrandfathered deliberately: a sweep of the checked-in critique artifacts
    found zero instances, so there is no legacy population to exempt, and adding a
    RULE_DATE would buy a hole rather than compatibility. That sweep covers the
    artifacts this validator actually reaches — prepare packets are excluded by
    `candidate_paths` on content kind, and ~219 of them DO carry
    `pending-parent-spawn` as a field value, so the zero is a property of the
    validated population, not of the directory.
    """
    status = (fresh_eye_status or "").lower()
    if not any(claim in status for claim in COMPLETED_DELEGATION_CLAIMS):
        return
    fields = section_field_map(text, REVIEWER_TIER_HEADING)
    if not fields:
        # Absence is the tier-evidence floor's own call (it knows the selection
        # mode and the enforce-from date); claiming it here would double-report.
        return
    contradictions = []
    if _LEADING_MARKUP_RE.sub("", fields.get("host exposure state", "").strip().lower()).startswith(_PENDING_SPAWN):
        contradictions.append(f"`Host exposure state: {_PENDING_SPAWN}` (no reviewer was spawned)")
    if _LEADING_MARKUP_RE.sub("", fields.get(DELIVERY_STATE_FIELD, "").strip().lower()).startswith(_PENDING_SPAWN):
        contradictions.append(f"`Delivery state: {_PENDING_SPAWN}` (no findings reached the parent)")
    if contradictions:
        raise ValidationError(
            f"{path}: this artifact's `Fresh-eye satisfaction` claims a completed delegation, but its own "
            f"reviewer tier evidence records {' and '.join(contradictions)}. Either the "
            "reviewer ran — update the spawn record to what the host reported — or it did not, and the "
            "fresh-eye line must say so (`blocked <host-signal>`), which is the honest, accepted outcome."
        )


def validate_delivery_state(
    path: Path,
    text: str,
    observed_date: date | None,
    *,
    section_field_map,
    opens_with_typed_value,
    legacy_undatable: frozenset[str],
) -> None:
    """Require a typed delivery state alongside reviewer tier evidence.

    Grandfather matches the fresh-eye typed-presence floor exactly: a dated
    artifact before the cutoff is exempt, an undatable one is exempt ONLY via the
    explicit legacy allowlist, and every other undatable artifact is enforced as
    if dated after the cutoff — an undatable NEW artifact is itself the anomaly,
    not a safe default.

    `legacy_undatable` is the boundary floor's allowlist rather than the
    fresh-eye one: this floor attaches to the reviewer tier evidence block, and
    the one extra legacy file that set carries is precisely an undatable
    pre-floor artifact that has tier evidence but predates any delivery record.
    """
    if observed_date is not None and observed_date < DELIVERY_STATE_RULE_DATE:
        return
    if observed_date is None and path.name in legacy_undatable:
        return
    value = section_field_map(text, REVIEWER_TIER_HEADING).get(DELIVERY_STATE_FIELD, "")
    if not value:
        raise ValidationError(
            f"{path}: reviewer tier evidence has no `Delivery state:` line; record one of "
            f"{DELIVERY_STATE_VALUES_SUMMARY}. A clean boundary fingerprint proves only that the "
            "reviewer did not mutate the tree — it says nothing about whether the findings ever "
            "reached the parent."
        )
    lowered = value.lower()
    if not opens_with_typed_value(lowered, DELIVERY_STATE_VALUES):
        raise ValidationError(
            f"{path}: `Delivery state` value `{value[:80]}` does not open with one of "
            f"{DELIVERY_STATE_VALUES_SUMMARY}, or still carries an unedited `todo` after the "
            "typed value — either way it is not a real record."
        )
    # Normalize ONCE for both checks. `opens_with_typed_value` strips leading
    # markup, so testing the raw string here would let `**spawn-accepted-no-delivery**`
    # satisfy the typed check and then skip the signal requirement entirely —
    # ceremony with no recorded cause, which is what this floor exists to stop.
    token = _LEADING_MARKUP_RE.sub("", lowered).strip()
    for typed in (_NO_DELIVERY, _RECOVERED):
        if token.startswith(typed) and not token[len(typed) :].strip(" :-*_`"):
            raise ValidationError(
                f"{path}: `{typed}` must name the concrete channel or host signal that "
                "dropped the findings, so the next session inherits the cause instead of "
                "re-deriving it."
            )


def validate_worker_delivery_evidence(
    path: Path,
    text: str,
    fresh_eye_status: str,
    *,
    section_field_map,
    repo_root: Path | None = None,
    artifact_binding_fields: dict[str, str] | None = None,
) -> None:
    """Bind ``worker-delivered`` to the combined worker report carrier.

    The ordinary delivery-state floor proves only that a parent recorded a
    findings event. ``worker-delivered`` is a stronger public claim: it may be
    written only when the durable report says the receipt, ledger, and result
    hash joined successfully. The fields stay intentionally small and typed so
    artifact validation cannot mistake media/process success for approval.
    """
    if not (fresh_eye_status or "").lower().startswith("worker-delivered"):
        return
    if repo_root is None:
        raise ValidationError(
            f"{path}: worker-delivered cannot be validated without the repository root needed to read its report carrier."
        )
    fields = section_field_map(text, REVIEWER_TIER_HEADING)
    try:
        validate_worker_report_carrier(
            artifact_label=str(path),
            fields=fields,
            repo_root=repo_root,
            artifact_binding_fields=artifact_binding_fields,
        )
    except WorkerCarrierError as exc:
        raise ValidationError(f"{path}: {exc}") from exc
