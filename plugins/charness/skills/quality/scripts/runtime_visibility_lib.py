from __future__ import annotations

from typing import Any

# Advisory, and the reason is not squeamishness. Absence of a sample has three
# causes and only one is a defect: a fresh machine has recorded nothing yet, a
# conditional gate did not run this time, and a renamed or abandoned label will
# never record again. Failing on plain absence blocks the first two -- a repair
# keyed on sample history was built, measured defective and REVERTED for exactly
# that (it hard-failed a fresh machine's first run and permanently failed six
# legitimately conditional labels, with `--no-verify` as the only escape). The
# decidable cause -- a label the runner no longer names at all -- is decidable only
# against a specific runner, so no gate installed WITH this library can decide it: a
# consumer's label universe is whatever its own runner declares, and a reader that
# only understands one runner would either refuse every consumer budget or no-op.
# What was missing here was neither a refusal nor another warning line: it was the
# COUNT. The reason string says exactly that and names no gate, because naming one
# would point a consumer at a file their install does not contain -- which is the
# same "a bar reads as protection while nothing enforces it" shape, restated as a
# reassuring sentence in the output.
UNENFORCEABLE_BUDGET_ADVISORY_REASON = (
    "a budgeted label with no sample in this profile cannot fail on this machine; "
    "absence alone does not distinguish a fresh machine from a conditional gate that "
    "did not run from an abandoned bar, so this is a COUNT and not a verdict -- "
    "reconciling budgeted labels against the labels your runner can actually queue "
    "is a repo-owned check, and this report does not perform it"
)


def runtime_visibility_findings(adapter_data: dict[str, Any], budgets: dict[str, int]) -> list[dict[str, str]]:
    """Return review-visible gaps, not runtime-budget verdict inputs.

    These findings describe absent observability configuration.  A correct command
    run cannot repair that configuration, so failing this command would turn an
    advisory review gap into a false execution failure.  The quality-summary
    renderer is the final consumer and preserves the `weak` severity plus action.
    """
    findings: list[dict[str, str]] = []
    if not budgets:
        findings.append(
            {
                "type": "runtime_visibility_missing_budgets",
                "severity": "weak",
                "message": (
                    "quality adapter has no effective runtime budget for the selected profile; "
                    "runtime reviews cannot budget standing-gate cost centers."
                ),
                "recommended_action": (
                    "Add budgets for dominant standing-gate phases once structured runtime samples exist."
                ),
            }
        )
    if not adapter_data.get("startup_probes"):
        findings.append(
            {
                "type": "runtime_visibility_missing_startup_probes",
                "severity": "weak",
                "message": (
                    "quality adapter has no startup_probes; repeated CLI or process startup cost "
                    "will remain invisible to quality review."
                ),
                "recommended_action": "Add at least one standing startup probe for agent-facing CLI or adapter startup.",
            }
        )
    return findings


def unenforceable_budgets(missing_samples: list[str], budgets_configured: int) -> dict[str, Any]:
    """The COUNT of bars that cannot fail on this machine, and the contract around it.

    A budgeted label with no sample renders one `WARN` line that scrolls past inside an
    ~85-gate run, so "how many committed bars are unenforceable here" was unanswerable
    without reading the report by hand -- and an unenforceable bar reads as protection
    forever. This is the number that makes the population legible; it is deliberately
    NOT an exit-code input.

    NO label list here, and no pointer to one either. A second copy of the list is a
    second thing that can drift; a `labels_key` POINTER is worse, because the two
    surfaces that carry this dict spell and bound that list differently
    (`missing_samples` in the detail report, `missing_samples_sample` after
    `bounded_list` in the summary), so one fixed key name dangles in whichever surface
    it did not name. The count travels; the list stays owned by whatever key the
    surrounding payload already uses.
    """
    return {
        "count": len(missing_samples),
        "budgets_configured": budgets_configured,
        "severity": "advisory",
        "reason": UNENFORCEABLE_BUDGET_ADVISORY_REASON,
    }
