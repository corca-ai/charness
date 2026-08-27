from __future__ import annotations

from pathlib import Path

import pytest

from scripts.readme_proof_ledger_lib import (
    LedgerEvidenceError,
    claim_ledger_rows,
    validate_ledger_rows,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "readme-proof.md"


def _ledger(evidence: str) -> str:
    return "\n".join(
        [
            "## Claim Ledger",
            "| ID | Source | Claim | Proof owner | Current evidence | Freshness | Status | Gap |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
            f"| README-EXAMPLE | claim | claim | Deterministic | {evidence} | refresh | Partial | gap |",
        ]
    )


def test_current_readme_proof_ledger_has_existing_path_bound_evidence() -> None:
    rows = validate_ledger_rows(SOURCE.read_text(encoding="utf-8"), source_path=SOURCE, repo_root=ROOT)
    assert len(rows) == 10
    assert all(targets for _, targets in rows)


@pytest.mark.parametrize("evidence", ["", "[]()", "missing/path"])
def test_ledger_evidence_refuses_empty_malformed_or_plain_text(evidence: str) -> None:
    with pytest.raises(LedgerEvidenceError, match="Evidence must contain"):
        validate_ledger_rows(_ledger(evidence), source_path=SOURCE, repo_root=ROOT)


def test_ledger_evidence_refuses_a_missing_markdown_target() -> None:
    with pytest.raises(LedgerEvidenceError, match="does not exist"):
        validate_ledger_rows(_ledger("[missing](./no-such-file.md)"), source_path=SOURCE, repo_root=ROOT)


def test_ledger_evidence_refuses_a_fragment_it_does_not_validate() -> None:
    with pytest.raises(LedgerEvidenceError, match="repo-relative"):
        validate_ledger_rows(_ledger("[readme](../README.md#not-a-heading)"), source_path=SOURCE, repo_root=ROOT)


def test_ledger_evidence_allows_a_markdown_title() -> None:
    rows = validate_ledger_rows(_ledger('[readme](../README.md "README")'), source_path=SOURCE, repo_root=ROOT)
    assert rows[0][1] == [ROOT / "README.md"]


def test_ledger_ignores_readme_shaped_rows_outside_the_claim_ledger() -> None:
    text = "\n".join(["| README-NOT-A-LEDGER | plain text |", _ledger("[readme](../README.md)")])
    rows = validate_ledger_rows(text, source_path=SOURCE, repo_root=ROOT)
    assert [row_id for row_id, _ in rows] == ["README-EXAMPLE"]
    assert [cells[0] for cells in claim_ledger_rows(text)] == ["README-EXAMPLE"]


def test_ledger_refuses_an_escaped_target_a_malformed_row_and_an_empty_ledger() -> None:
    with pytest.raises(LedgerEvidenceError, match="escapes the repository"):
        validate_ledger_rows(_ledger("[outside](../../outside.md)"), source_path=SOURCE, repo_root=ROOT)
    with pytest.raises(LedgerEvidenceError, match="Expected eight ledger cells"):
        claim_ledger_rows("## Claim Ledger\n| README-BAD | only | three | cells |")
    with pytest.raises(LedgerEvidenceError, match="Expected one or more"):
        claim_ledger_rows("## Claim Ledger\n\n## Next")
