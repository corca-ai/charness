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

import re
from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module

_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _artifact_validator.ValidationError

REVIEWER_TIER_HEADING = "## Reviewer Tier Evidence"
REVIEWER_TIER_REQUIRED_FIELDS = (
    "requested tier",
    "requested spawn fields",
    "host exposure state",
    "application state",
)
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
DELIVERY_STATE_VALUES_SUMMARY = (
    "`findings-received` / `findings-recovered-from-transcript <signal>` / "
    "`spawn-accepted-no-delivery <signal>` / `pending-parent-spawn`"
)
_NO_DELIVERY = "spawn-accepted-no-delivery"
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
