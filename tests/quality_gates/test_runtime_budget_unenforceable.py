"""How many committed bars cannot fail on this machine, and where that number lives.

A budgeted runtime label with no sample rendered one `WARN` line that scrolled past
inside an ~85-gate run, and the gate never rendered the total -- so "how many committed
bars are unenforceable here" was unanswerable without reading the report by hand, and a
deliberately sized bar read as protection forever.

The count is advisory on purpose. Absence of a sample has three causes and only one is
a defect: a fresh machine has recorded nothing yet, a conditional gate did not run this
time, and a renamed or abandoned label never will. A repair keyed on sample history was
built, measured defective and reverted for exactly that. Reconciling budgeted labels
against the labels a runner can actually queue is a repo-owned check this report does
not perform, and the reason string says so rather than naming a gate a consumer's
install does not contain.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .support import run_script, seed_runtime_budget_repo

SCRIPT = "skills/public/quality/scripts/check_runtime_budget.py"


def test_runtime_budget_gate_counts_the_bars_that_cannot_fail_on_this_machine(tmp_path: Path) -> None:
    """The gate rendered N warnings and never rendered N.

    "How many committed bars are unenforceable on this machine" was unanswerable
    without reading an ~85-gate report by hand, which is how a deliberately sized bar
    reads as protection forever. The count is the measurement; it stays advisory
    because absence alone does not separate a fresh machine from an abandoned bar.
    """
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"pytest": 22000, "check-markdown": 9000, "check-secrets": 3000},
        signals={"commands": {"pytest": {"latest": {"elapsed_ms": 1000}}}},
    )

    detail = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert detail.returncode == 0, detail.stderr
    unenforceable = yaml.safe_load(detail.stdout)["unenforceable_budgets"]
    assert unenforceable["count"] == 2
    assert unenforceable["budgets_configured"] == 3
    assert unenforceable["severity"] == "advisory"
    # ONE owner for the list. A second copy inside this dict is not a second
    # measurement, only a second thing that can drift -- and the two consumer-facing
    # summaries would then bound it differently and disagree about which bars are
    # unenforceable. The dict names where the list lives instead of restating it.
    assert "labels" not in unenforceable
    # No POINTER either. The two surfaces spell and bound the list differently
    # (`missing_samples` here, `missing_samples_sample` after `bounded_list` in the
    # summary), so one fixed key name would dangle in whichever surface it did not name
    # -- and the summary is the one a reviewer actually reads.
    assert "labels_key" not in unenforceable
    assert yaml.safe_load(detail.stdout)["missing_samples"] == ["check-markdown", "check-secrets"]

    summary = run_script(SCRIPT, "--repo-root", str(repo), "--summary", "--runtime-profile", "default")
    assert summary.returncode == 0, summary.stderr
    summary_payload = yaml.safe_load(summary.stdout)
    assert summary_payload["unenforceable_budgets"]["count"] == 2
    # Bounded like every other list in the summary, count included.
    assert summary_payload["missing_samples_count"] == 2
    assert summary_payload["missing_samples_sample"] == ["check-markdown", "check-secrets"]
    assert summary_payload["missing_samples_truncated"] is False

    human = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert human.returncode == 0, human.stderr
    aggregate = [line for line in human.stdout.splitlines() if line.startswith("UNENFORCEABLE")]
    assert len(aggregate) == 1, human.stdout
    assert "2 of 3 budgeted label(s)" in aggregate[0]


def test_runtime_budget_gate_reports_no_unenforceable_count_when_every_bar_is_measured(
    tmp_path: Path,
) -> None:
    """The count must be absent from the human render when it is zero.

    A permanent `UNENFORCEABLE 0 of N` line is noise that trains a reader to skip the
    line, which is the same failure mode as the per-label warnings it replaces.
    """
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"pytest": 22000},
        signals={"commands": {"pytest": {"latest": {"elapsed_ms": 1000}}}},
    )
    human = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert human.returncode == 0, human.stderr
    assert "UNENFORCEABLE" not in human.stdout

    detail = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert yaml.safe_load(detail.stdout)["unenforceable_budgets"]["count"] == 0


def test_every_key_the_advisory_dict_names_resolves_in_the_payload_carrying_it() -> None:
    """A pointer that dangles in the surface a reviewer reads is worse than no pointer.

    The dict ships in three payloads with different list spellings. This asserts it
    claims no key at all, so there is nothing to resolve wrongly.
    """
    import sys
    from pathlib import Path as _Path

    sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / "skills/public/quality/scripts"))
    import runtime_visibility_lib

    payload = runtime_visibility_lib.unenforceable_budgets(["a", "b"], 5)

    assert set(payload) == {"count", "budgets_configured", "severity", "reason"}
    assert payload["count"] == 2
    assert not any(key.endswith("_key") for key in payload)
