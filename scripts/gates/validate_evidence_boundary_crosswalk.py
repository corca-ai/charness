#!/usr/bin/env python3
"""Validate the evidence-boundary crosswalk.

Two states, two very different bars.

`bootstrap` is the pre-0 shape: protected targets and a bound source identity, with
no acceptance matrix yet. It must be internally consistent and MUST NOT authorize any
close — validated so the bootstrap artifact cannot quietly acquire teeth it has not
earned.

`complete` is the Slice 0 shape and is where the row-set floor bites: every protected
issue present, a non-empty criterion set per issue, every criterion mapped to at least
one source clause AND at least one coverage row, every coverage row mapped back to a
criterion, every source clause carrying exactly one disposition, and every clause id
resolving against the frozen inventory. An incomplete row set is refused rather than
partially accepted, because a matrix missing the rows for one issue is exactly how
that issue's criteria stop being able to fail.

    python3 scripts/gates/validate_evidence_boundary_crosswalk.py --repo-root .
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


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

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)
_crosswalk = import_repo_module(__file__, "scripts.evidence_boundary_crosswalk")
_freeze_lib = import_repo_module(__file__, "scripts.issue_source_freeze_lib")
_refusal_lib = import_repo_module(__file__, "scripts.closeout_refusal_lib")

CrosswalkError = _crosswalk.CrosswalkError
DEFAULT_CROSSWALK_PATH = _crosswalk.DEFAULT_CROSSWALK_PATH
DEPENDENCY_VALUES = _crosswalk.DEPENDENCY_VALUES
MATRIX_STATES = _crosswalk.MATRIX_STATES
OWNER_VALUES = _crosswalk.OWNER_VALUES

DISPOSITIONS = ("criterion", "non-goal", "evidence-only")


def _fail(code: str, detail: str) -> None:
    raise CrosswalkError(code, detail)


def _validate_shape(crosswalk: dict[str, Any]) -> None:
    if crosswalk.get("matrix_state") not in MATRIX_STATES:
        _fail("invalid_matrix_state", f"matrix_state must be one of {MATRIX_STATES}")
    if not crosswalk.get("current_repository"):
        _fail("missing_current_repository", "the crosswalk must declare its current repository")
    protected = crosswalk.get("protected_issues") or []
    if not protected:
        _fail("empty_protected_set", "the crosswalk protects no issues, so it authorizes nothing")
    # Type floor. Issue numbers are compared against `int`s produced by
    # `normalize_target`, so a string-typed protected set can never match anything: the
    # gate silently stops applying to every issue while this validator reports ok. That
    # is a one-character-per-line artifact edit that disarms the whole thing with no
    # refusal anywhere, which is precisely what this validator exists to prevent.
    for number in protected:
        if not isinstance(number, int) or isinstance(number, bool):
            _fail(
                "non_integer_protected_issue",
                f"protected_issues contains {number!r} ({type(number).__name__}); issue numbers must be "
                "JSON integers or the protected set silently matches nothing",
            )
    for row in crosswalk.get("issues") or []:
        if not isinstance(row.get("number"), int) or isinstance(row.get("number"), bool):
            _fail(
                "non_integer_row_number",
                f"an issues[] row has number {row.get('number')!r}; issue numbers must be JSON integers",
            )
    rows = {row.get("number") for row in crosswalk.get("issues") or []}
    missing = sorted(set(protected) - rows)
    if missing:
        _fail("incomplete_row_set", f"protected issues without a row: {missing}")
    extra = sorted(rows - set(protected))
    if extra:
        _fail("unprotected_row", f"rows for issues that are not protected: {extra}")
    for row in crosswalk["issues"]:
        if row.get("owner") not in OWNER_VALUES:
            _fail("invalid_owner", f"#{row.get('number')} owner={row.get('owner')!r}, allowed {OWNER_VALUES}")
        if row.get("projection_dependency") not in DEPENDENCY_VALUES:
            _fail(
                "invalid_projection_dependency",
                f"#{row.get('number')} projection_dependency={row.get('projection_dependency')!r}",
            )
        if row.get("owner") == "re-scoped" and not row.get("replacement"):
            _fail("unnamed_rescope", f"#{row.get('number')} is re-scoped without naming a replacement owner")


def _clause_index(repo_root: Path, crosswalk: dict[str, Any]) -> dict[int, set[str]]:
    snapshot_rel = (crosswalk.get("source_identity") or {}).get("snapshot_path")
    if not snapshot_rel:
        _fail("missing_source_identity", "the crosswalk declares no snapshot path")
    snapshot = _freeze_lib.load_json(repo_root, snapshot_rel, _freeze_lib.SNAPSHOT_SCHEMA)
    return {
        issue["number"]: {clause["source_clause_id"] for unit in issue["source_units"] for clause in unit["clauses"]}
        for issue in snapshot["clause_inventory"]["issues"]
    }


def _validate_bootstrap(crosswalk: dict[str, Any]) -> None:
    """A bootstrap crosswalk must be inert."""
    for row in crosswalk["issues"]:
        if row.get("criteria") or row.get("coverage"):
            _fail(
                "bootstrap_carries_matrix",
                f"#{row['number']} carries matrix rows while matrix_state=bootstrap; promote the state or "
                "drop the rows rather than leaving a half-built matrix that reads as either",
            )
        if row.get("projection_dependency") != "undecided":
            _fail(
                "bootstrap_decides_dependency",
                f"#{row['number']} declares projection_dependency={row.get('projection_dependency')!r} "
                "before Slice 0 has decided the seam",
            )
    if (crosswalk.get("shared_projection") or {}).get("status") != "undecided":
        _fail("bootstrap_decides_projection", "shared_projection status is decided while matrix_state=bootstrap")


def _validate_complete(repo_root: Path, crosswalk: dict[str, Any]) -> None:
    clause_ids = _clause_index(repo_root, crosswalk)
    for row in crosswalk["issues"]:
        number = row["number"]
        criteria = row.get("criteria") or []
        coverage = row.get("coverage") or []
        clauses = row.get("source_clauses") or []
        if not criteria:
            _fail("empty_criteria", f"#{number} has no criterion; an issue with no criteria can never fail one")
        if not coverage:
            _fail("empty_coverage", f"#{number} has no executable coverage row")
        criterion_ids = [item["criterion_id"] for item in criteria]
        if len(set(criterion_ids)) != len(criterion_ids):
            _fail("duplicate_criterion_id", f"#{number} repeats a criterion_id")
        coverage_ids = [item["coverage_id"] for item in coverage]
        if len(set(coverage_ids)) != len(coverage_ids):
            _fail("duplicate_coverage_id", f"#{number} repeats a coverage_id")
        _validate_clause_dispositions(number, clauses, clause_ids.get(number, set()))
        # Only `criterion`-dispositioned clauses may back a criterion. Passing every
        # declared clause here let a matrix mark its whole source `non-goal` and then
        # assert criteria "sourced" from those non-goals — the closure check below only
        # guards the other direction, so nothing caught it and the matrix read complete.
        criterion_clause_ids = {
            item["source_clause_id"] for item in clauses if item.get("disposition") == "criterion"
        }
        _validate_criteria(number, criteria, criterion_clause_ids, set(coverage_ids))
        _validate_coverage(number, coverage, set(criterion_ids))
        _validate_criterion_clause_closure(number, clauses, criteria)
        if row.get("projection_dependency") == "undecided":
            _fail("undecided_dependency", f"#{number} is still undecided while matrix_state=complete")


def _validate_clause_dispositions(number: int, clauses: list[dict], frozen_ids: set[str]) -> None:
    seen: set[str] = set()
    for clause in clauses:
        clause_id = clause.get("source_clause_id")
        if clause_id not in frozen_ids:
            _fail(
                "dangling_source_clause",
                f"#{number} cites clause {clause_id!r}, which is not in the frozen inventory — the matrix is "
                "built against source that was never captured, or against a superseded freeze",
            )
        if clause_id in seen:
            _fail("duplicate_clause_disposition", f"#{number} dispositions clause {clause_id!r} more than once")
        seen.add(clause_id)
        if clause.get("disposition") not in DISPOSITIONS:
            _fail("invalid_disposition", f"#{number} clause {clause_id!r} disposition={clause.get('disposition')!r}")
        if clause["disposition"] in {"non-goal", "evidence-only"} and not (clause.get("reason") and clause.get("owner")):
            _fail(
                "unowned_exclusion",
                f"#{number} clause {clause_id!r} is excluded as {clause['disposition']} without a bounded "
                "reason and owner; an unexplained exclusion is how a real criterion disappears",
            )
    unmapped = sorted(frozen_ids - seen)
    if unmapped:
        _fail(
            "undispositioned_clause",
            f"#{number} leaves {len(unmapped)} frozen clause(s) with no disposition, e.g. {unmapped[:3]}",
        )


def _validate_criteria(number: int, criteria: list[dict], clause_ids: set[str], coverage_ids: set[str]) -> None:
    for criterion in criteria:
        cid = criterion["criterion_id"]
        sources = criterion.get("source_clause_ids") or []
        covers = criterion.get("coverage_ids") or []
        if not sources:
            _fail("unsourced_criterion", f"#{number} criterion {cid} maps to no source clause")
        if not covers:
            _fail("uncovered_criterion", f"#{number} criterion {cid} maps to no executable coverage row")
        for source in sources:
            if source not in clause_ids:
                _fail(
                    "dangling_criterion_source",
                    f"#{number} criterion {cid} cites {source!r}, which is not a clause dispositioned "
                    "`criterion` in this row (it is missing, or excluded as non-goal/evidence-only)",
                )
        for cover in covers:
            if cover not in coverage_ids:
                _fail("dangling_criterion_coverage", f"#{number} criterion {cid} cites unknown coverage {cover!r}")
        for field in ("producer", "invocation", "expected", "artifact_path", "final_reader_route", "non_claim"):
            if not criterion.get(field):
                _fail("incomplete_criterion", f"#{number} criterion {cid} is missing {field!r}")


def _validate_coverage(number: int, coverage: list[dict], criterion_ids: set[str]) -> None:
    for row in coverage:
        cid = row["coverage_id"]
        criteria = row.get("criterion_ids") or []
        if not criteria:
            _fail("orphan_coverage", f"#{number} coverage {cid} maps to no criterion")
        for criterion in criteria:
            if criterion not in criterion_ids:
                _fail("dangling_coverage_criterion", f"#{number} coverage {cid} cites unknown criterion {criterion!r}")
        shared = row.get("shared")
        # `isinstance(..., bool)`, not `in {True, False}`: `0 in {True, False}` is True
        # because `0 == False`, while `0 is False` is not — so `"shared": 0` passed the
        # presence check and then slipped past the `is False` guard below, declaring
        # nothing and being held to nothing.
        if not isinstance(shared, bool):
            _fail(
                "undeclared_sharing",
                f"#{number} coverage {cid} does not declare whether it is shared "
                f"(got {shared!r}; must be a JSON true/false)",
            )
        if shared is False and len(criteria) != 1:
            _fail(
                "unshared_multi_criterion_coverage",
                f"#{number} coverage {cid} serves {len(criteria)} criteria but declares shared=false; a coverage "
                "row may only span criteria when it explicitly claims identical invocation/result semantics",
            )


def _validate_criterion_clause_closure(number: int, clauses: list[dict], criteria: list[dict]) -> None:
    mapped = {source for criterion in criteria for source in criterion.get("source_clause_ids") or []}
    for clause in clauses:
        if clause["disposition"] == "criterion" and clause["source_clause_id"] not in mapped:
            _fail(
                "unclaimed_criterion_clause",
                f"#{number} clause {clause['source_clause_id']!r} is dispositioned `criterion` but no criterion "
                "claims it; the acceptance claim it states would silently go unbuilt",
            )


def _authorization_status(repo_root: Path, rel: str, crosswalk: dict[str, Any]) -> dict[str, Any]:
    """Report authorization by ASKING THE GATE, per issue, not by restating matrix_state.

    `matrix_state == "complete"` is necessary and nowhere near sufficient — the gate also
    requires a non-consumer owner, a decided projection dependency, a matching frozen
    source, a singleton aggregate, and an in-scope carrier. Deriving this surface from
    `matrix_state` alone made the validator assert a verdict ABOUT the gate that the gate
    itself would contradict.

    The answer is reported PER REAL CARRIER, not for a synthetic probe. A single
    probe under an invented carrier name could never hit `carrier_out_of_scope`, so a
    crosswalk that every release and PR carrier refuses would still have printed one
    cheerful `true` — a narrower version of the same overclaim. Each field name says
    exactly what it covers: one issue, one in-scope carrier, one target. Nothing here
    speaks for a multi-issue carrier, which the gate refuses by the singleton rule.
    """
    carriers = ("commit-msg", "close-with-comment", "release", "pr-body")
    per_issue: dict[int, dict[str, Any]] = {}
    for row in crosswalk["issues"]:
        number = row["number"]
        by_carrier = {
            carrier: _crosswalk.authorize_closeout(
                [{"repository": crosswalk["current_repository"], "issue_number": number, "source": "validator-probe"}],
                [],
                carrier,
                repo_root=repo_root,
                crosswalk_path=rel,
            )
            for carrier in carriers
        }
        per_issue[number] = {
            "owner": row["owner"],
            "projection_dependency": row["projection_dependency"],
            "by_carrier": {
                carrier: {"authorized": probe["authorized"], "refusal": probe.get("refusal")}
                for carrier, probe in by_carrier.items()
            },
            "authorized_by_any_carrier": any(probe["authorized"] for probe in by_carrier.values()),
        }
    return {
        "single_issue_close_authorized_by_some_in_scope_carrier": {
            number: item["authorized_by_any_carrier"] for number, item in per_issue.items()
        },
        "authorizes_protected_close": all(item["authorized_by_any_carrier"] for item in per_issue.values()),
        "probed_carriers": list(carriers),
        "not_probed": "multi-issue carriers (always refused by the singleton rule) and the "
        "close-with-comment manual-target-declaration requirement",
        "per_issue": per_issue,
        "owners": {row["number"]: row["owner"] for row in crosswalk["issues"]},
        "projection_dependency": {row["number"]: row["projection_dependency"] for row in crosswalk["issues"]},
    }


def run(repo_root: Path, rel: str) -> dict[str, Any]:
    crosswalk = _crosswalk.load_crosswalk(repo_root, rel)
    _validate_shape(crosswalk)
    _crosswalk.verify_frozen_source(repo_root, crosswalk)
    if crosswalk["matrix_state"] == "bootstrap":
        _validate_bootstrap(crosswalk)
    else:
        _validate_complete(repo_root, crosswalk)
    return {
        "ok": True,
        "crosswalk_path": rel,
        "matrix_state": crosswalk["matrix_state"],
        "protected_issues": sorted(crosswalk["protected_issues"]),
        "source_status": {
            "frozen": True,
            "source_snapshot_sha256": crosswalk["source_identity"]["source_snapshot_sha256"],
            "clause_inventory_identity": crosswalk["source_identity"]["clause_inventory_identity"],
        },
        "authorization_status": _authorization_status(repo_root, rel, crosswalk),
        "shared_projection_status": crosswalk.get("shared_projection", {}).get("status"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK_PATH)
    args = parser.parse_args()
    return _refusal_lib.run_cli(
        "validate_evidence_boundary_crosswalk",
        lambda: run(args.repo_root.resolve(), args.crosswalk),
        refusals=(CrosswalkError, _freeze_lib.FreezeError),
    )


if __name__ == "__main__":
    raise SystemExit(main())
