"""Keep the generic proof-mismatch verdict and issue closeout wiring covered."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.evidence import proof_mismatch as pm

from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]
ISSUE_VERIFY = ROOT / "skills/public/issue/scripts/issue_verify_closeout.py"


def _load_issue_verify():
    return load_module("issue_verify_closeout_under_test", ISSUE_VERIFY)


issue_verify = _load_issue_verify()

ADAPTER = (
    "proof_levels:\n  - lint\n  - smoke\n  - integration\n  - live\n"
    "incomparable:\n  - lint, smoke\n"
    "acceptance_map:\n  reliability: integration\n  safety: live\n"
)


def _repo(tmp_path: Path, adapter: str | None = ADAPTER) -> Path:
    if adapter is not None:
        target = tmp_path / ".agents/proof-semantics-adapter.yaml"
        target.parent.mkdir(parents=True)
        target.write_text(adapter, encoding="utf-8")
    return tmp_path


def _ledger(rows: str) -> str:
    return (
        "# Goal\n\n## Proof Ledger\n\n"
        "| Acceptance Class | Reached Proof | Disposition |\n"
        "| --- | --- | --- |\n" + rows
    )


def test_parser_uses_headers_and_ignores_fenced_tables() -> None:
    body = (
        "| Reached Proof | Acceptance Class | Disposition |\n"
        "| --- | --- | --- |\n| smoke | reliability | accepted-risk: x |\n\n"
        "```\n| Acceptance Class | Reached Proof |\n"
        "| --- | --- |\n| safety | live |\n```\n"
    )

    rows = pm.parse_proof_ledger(body)

    assert rows == [
        {
            "acceptance_class": "reliability",
            "reached": "smoke",
            "disposition": "accepted-risk: x",
            "row": "| smoke | reliability | accepted-risk: x |",
        }
    ]


@pytest.mark.parametrize(
    ("reached", "gap_kind"),
    [("", "no-proof-entry"), ("smoke", "proof-below-acceptance"), ("lint", "proof-below-acceptance")],
)
def test_evaluate_row_identifies_missing_or_insufficient_proof(
    tmp_path: Path, reached: str, gap_kind: str
) -> None:
    data = pm.load_adapter(_repo(tmp_path))["data"]

    row = pm.evaluate_row(
        {"acceptance_class": "reliability", "reached": reached, "disposition": ""},
        data,
        True,
    )

    assert row["gap"] is True
    assert row["gap_kind"] == gap_kind


def test_report_blocks_only_undispositioned_gap(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    blocked = pm.proof_mismatch_report(repo, _ledger("| reliability | smoke | |\n"))
    accepted = pm.proof_mismatch_report(
        repo,
        _ledger("| reliability | smoke | accepted-risk: monitored |\n"),
    )

    assert blocked["problem"] == "mismatch"
    assert accepted["problem"] is None


def test_report_degrades_without_adapter_and_rejects_invalid_adapter(tmp_path: Path) -> None:
    missing = pm.proof_mismatch_report(
        _repo(tmp_path / "missing", adapter=None),
        _ledger("| reliability | live | |\n"),
    )
    invalid = pm.proof_mismatch_report(
        _repo(tmp_path / "invalid", adapter="acceptance_map:\n  reliability: integration\n"),
        _ledger("| reliability | live | |\n"),
    )

    assert missing["problem"] == "mismatch" and missing["degraded"] is True
    assert invalid["problem"] == "invalid-adapter" and invalid["adapter_valid"] is False


def test_apply_floor_flips_verdict_and_records_scope(tmp_path: Path) -> None:
    report = {"ok": True}

    pm.apply_proof_mismatch_floor(
        report,
        _repo(tmp_path),
        _ledger("| reliability | smoke | |\n"),
    )

    assert report["ok"] is False
    assert report["proof_mismatch"]["problem"] == "mismatch"
    assert report["proof_mismatch_scope"]["present"] is True


def test_issue_closeout_loader_cache_and_missing_bootstrap_guard(monkeypatch) -> None:
    loaded = issue_verify._load_proof_mismatch()
    assert issue_verify._load_proof_mismatch() is loaded
    monkeypatch.setattr(issue_verify, "_PROOF_MISMATCH", None)
    monkeypatch.setattr(issue_verify, "_resolve_bootstrap", lambda: None)
    with pytest.raises(ImportError):
        issue_verify._load_proof_mismatch()
    issue_verify._PROOF_MISMATCH = loaded


def test_issue_closeout_folds_proof_gap_into_status(tmp_path: Path) -> None:
    result = {"ok": True, "status": "carrier_verified"}

    issue_verify._fold_proof_mismatch(
        result,
        _repo(tmp_path, adapter=None),
        _ledger("| reliability | smoke | |\n"),
    )

    assert result["ok"] is False
    assert result["status"] == "failed"
    assert result["proof_mismatch"]["problem"] == "mismatch"
