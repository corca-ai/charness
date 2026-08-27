from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scripts import run_slice_closeout as closeout


def test_slice_closeout_reports_only_changed_durable_artifacts(monkeypatch, tmp_path: Path) -> None:
    seen: list[tuple[Path, list[str]]] = []
    base_calls: dict[str, str] = {}

    def record(repo_root: Path, paths: list[str]) -> None:
        seen.append((repo_root, paths))

    def record_base(name: str):
        def record(*_args, **kwargs) -> None:
            base_calls[name] = kwargs.get("base", kwargs.get("against"))

        return record

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
        monkeypatch.setattr(closeout, name, record_base(name))
    monkeypatch.setattr(closeout, "advise_repair_parity", record_base("parity"))
    monkeypatch.setattr(closeout, "_maybe_block_on_unmatched", lambda *args, **kwargs: None)
    monkeypatch.setattr(closeout, "_maybe_block_on_risk_interrupt", lambda *args, **kwargs: None)

    payload = {"changed_paths": ["charness-artifacts/current.md", "scripts/change.py"]}
    args = SimpleNamespace(
        plan_only=False,
        allow_unmatched=False,
        ack_skill_review=True,
    )

    assert (
        closeout._run_preexecution_blocks(
            tmp_path,
            payload,
            args,
            risk_interrupt_paths=payload["changed_paths"],
            base="campaign-base",
        )
        is None
    )
    assert seen == [(tmp_path, payload["changed_paths"])]
    assert {name: value for name, value in base_calls.items() if value is not None} == {
        "advise_new_pool_module": "campaign-base",
        "parity": "campaign-base",
        "advise_removed_name_consumers": "campaign-base",
        "advise_floor_addition_restraint": "campaign-base",
        "attach_new_proof_surface_advisory": "campaign-base",
        "advise_close_keyword_leakage": "campaign-base",
    }
