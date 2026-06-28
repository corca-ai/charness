from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_plan_module() -> ModuleType:
    script = ROOT / "skills" / "public" / "retro" / "scripts" / "plan_retro_run.py"
    spec = importlib.util.spec_from_file_location("retro_plan_run_under_test", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_plan(repo: Path, **kwargs: object) -> dict[str, object]:
    payload = load_plan_module().build_plan(repo.resolve(), **kwargs)
    return json.loads(json.dumps(payload))


def write_adapter(repo: Path) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/retro",
                "default_mode: session",
                "summary_path: charness-artifacts/retro/recent-lessons.md",
                "",
            ]
        ),
        encoding="utf-8",
    )


def required_paths(payload: dict[str, object]) -> set[str]:
    return {read["path"] for read in payload["required_reads"]}  # type: ignore[index]


def test_retro_plan_shape_and_scaffold_when_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo, changed_paths=["skills/public/retro/SKILL.md"])

    assert payload["schema_version"] == "retro.run_plan.v1"
    assert payload["ok"] is True
    assert payload["artifact"]["status"] == "missing"
    assert payload["next_action"]["kind"] == "scaffold-retro-artifact"

    paths = required_paths(payload)
    assert "references/expert-lens.md" in paths
    assert "scripts/scaffold_retro_artifact.py" in paths
    assert "docs/handoff.md" in paths

    packet_ids = {packet["id"] for packet in payload["gate_packets"]}  # type: ignore[index]
    assert {"adapter-readiness", "retro-artifact-scaffold", "retro-artifact-shape", "auto-session-trigger"} <= packet_ids


def test_expert_lens_is_always_a_required_read(tmp_path: Path) -> None:
    """The mandatory counterfactual + non-inlined catalog make expert-lens.md an
    unconditional floor regardless of work class — the planner-anchored fix for the
    failed live capture."""
    repo = tmp_path / "repo"
    write_adapter(repo)

    for changed in (["src/app.py"], ["docs/readme.md"], ["skills/public/x/SKILL.md"], []):
        payload = run_plan(repo, changed_paths=changed)
        assert "references/expert-lens.md" in required_paths(payload)


def test_system_improving_work_briefs_the_engelbart_lens(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo, changed_paths=["evals/cautilus/spec.json", "scripts/x.py"])

    assert payload["work_class"] == "system-improving"
    assert "Engelbart" in payload["lens_brief"]["fitting_lens"]  # type: ignore[index]
    lens_read = next(read for read in payload["required_reads"] if read["path"] == "references/expert-lens.md")  # type: ignore[index]
    assert "Engelbart" in lens_read["why"] or "system-improving" in lens_read["why"]


def test_ordinary_and_docs_work_classes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    ordinary = run_plan(repo, changed_paths=["src/app.py", "lib/util.py"])
    assert ordinary["work_class"] == "ordinary"
    assert "Default Pattern" in ordinary["lens_brief"]["fitting_lens"]  # type: ignore[index]

    docs = run_plan(repo, changed_paths=["docs/readme.md"])
    assert docs["work_class"] == "docs"

    unknown = run_plan(repo, changed_paths=[])
    assert unknown["work_class"] == "unknown"


def test_weekly_mode_adds_weekly_trends_read(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo, invocation_text="weekly retro for this week", changed_paths=["src/app.py"])

    assert payload["mode"] == "weekly"
    assert "references/weekly-trends.md" in required_paths(payload)


def test_clean_valid_adapter_does_not_add_adapter_contract(tmp_path: Path) -> None:
    """A benign warning (e.g. no metrics_commands) must not force the adapter-contract
    read — only a missing/invalid adapter does."""
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo, changed_paths=["src/app.py"])

    assert payload["adapter"]["found"] is True
    assert payload["adapter"]["valid"] is True
    assert "references/adapter-contract.md" not in required_paths(payload)


def test_continue_existing_when_today_artifact_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    first = run_plan(repo, changed_paths=["src/app.py"])
    artifact_rel = first["artifact"]["path"]  # type: ignore[index]
    artifact_path = repo / str(artifact_rel)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text("# Session Retro\n", encoding="utf-8")

    payload = run_plan(repo, changed_paths=["src/app.py"])

    assert payload["artifact"]["status"] == "today_artifact_exists"
    assert payload["next_action"]["kind"] == "continue-existing-retro"
    assert str(artifact_rel) in required_paths(payload)
