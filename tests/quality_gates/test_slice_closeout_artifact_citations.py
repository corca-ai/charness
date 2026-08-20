from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scripts import run_slice_closeout as closeout


def test_slice_closeout_reports_only_changed_durable_artifacts(monkeypatch, tmp_path: Path) -> None:
    seen: list[tuple[Path, list[str]]] = []
    parity_bases: list[str] = []

    def record(repo_root: Path, paths: list[str]) -> None:
        seen.append((repo_root, paths))

    def record_parity(*_args, **kwargs) -> None:
        parity_bases.append(kwargs["base"])

    monkeypatch.setattr(closeout, "advise_artifact_citations", record)
    monkeypatch.setattr(closeout, "block_on_structural_sweep", lambda *args, **kwargs: None)
    monkeypatch.setattr(closeout, "closeout_producer_validation_error", lambda args: None)
    for name in (
        "advise_prose_pin",
        "advise_skill_surface_preflight",
        "advise_doc_surface_preflight",
        "advise_new_pool_module",
        "advise_repair_parity",
        "advise_removed_name_consumers",
        "advise_over_slicing",
        "advise_floor_addition_restraint",
        "attach_new_proof_surface_advisory",
        "advise_close_keyword_leakage",
        "advise_decaying_habits",
    ):
        monkeypatch.setattr(closeout, name, lambda *args, **kwargs: None)
    monkeypatch.setattr(closeout, "advise_repair_parity", record_parity)
    monkeypatch.setattr(closeout, "_maybe_block_on_unmatched", lambda *args, **kwargs: None)
    monkeypatch.setattr(closeout, "_maybe_block_on_cautilus", lambda *args, **kwargs: None)
    monkeypatch.setattr(closeout, "_maybe_block_on_risk_interrupt", lambda *args, **kwargs: None)

    payload = {"changed_paths": ["charness-artifacts/current.md", "scripts/change.py"]}
    args = SimpleNamespace(
        plan_only=False,
        allow_unmatched=False,
        ack_skill_review=True,
        ack_cautilus_skill_review=True,
    )

    assert closeout._run_preexecution_blocks(tmp_path, payload, args) is None
    assert seen == [(tmp_path, payload["changed_paths"])]
    assert parity_bases == ["origin/main"]
