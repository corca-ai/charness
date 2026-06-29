from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _init_git_repo_with_commit(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "tracked.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "snapshot")


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


def test_retro_plan_session_wording_selects_session_mode(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo, invocation_text="what just happened this session", changed_paths=["src/app.py"])

    assert payload["mode"] == "session"
    assert payload["mode_reason"] == "session wording in invocation"


def test_retro_plan_missing_adapter_adds_adapter_contract_read(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)

    payload = run_plan(repo, changed_paths=["src/app.py"])

    # No adapter file -> not found -> the adapter-contract repair read is added.
    assert "references/adapter-contract.md" in required_paths(payload)


def test_retro_plan_weekly_reads_summary_when_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    summary = repo / "charness-artifacts" / "retro" / "recent-lessons.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text("# Recent Lessons\n", encoding="utf-8")

    payload = run_plan(repo, invocation_text="weekly retro for this week", changed_paths=["src/app.py"])

    assert payload["mode"] == "weekly"
    assert "charness-artifacts/retro/recent-lessons.md" in required_paths(payload)


def test_retro_plan_infers_work_paths_from_recent_commits(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    _init_git_repo_with_commit(repo)  # clean worktree after commit

    payload = run_plan(repo)  # no changed_paths -> infer from repo state

    assert payload["work_paths_source"] == "recent_commits"
    assert payload["work_class"] in {"ordinary", "system-improving", "docs", "unknown"}


def test_retro_plan_infers_work_paths_from_working_tree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    _init_git_repo_with_commit(repo)
    (repo / "tracked.py").write_text("x = 2\n", encoding="utf-8")  # dirty worktree

    payload = run_plan(repo)

    assert payload["work_paths_source"] == "working_tree_diff"


def test_retro_plan_work_paths_falls_back_when_surfaces_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    _init_git_repo_with_commit(repo)
    module = load_plan_module()

    class Boom:
        @staticmethod
        def collect_changed_paths(_repo: Path) -> list[str]:
            raise RuntimeError("surfaces unavailable")

    monkeypatch.setattr(module, "surfaces_lib", Boom)
    payload = json.loads(json.dumps(module.build_plan(repo.resolve())))

    assert payload["work_paths_source"] == "recent_commits"


def test_retro_recent_commit_paths_empty_outside_git(tmp_path: Path) -> None:
    nongit = tmp_path / "nogit"
    nongit.mkdir()
    module = load_plan_module()

    assert module._recent_commit_paths(nongit, 5) == []


def test_retro_recent_commit_paths_handles_subprocess_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_plan_module()

    def boom(*_args: object, **_kwargs: object) -> None:
        raise OSError("git binary missing")

    monkeypatch.setattr(module.subprocess, "run", boom)

    assert module._recent_commit_paths(tmp_path, 5) == []


def test_retro_plan_main_emits_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    module = load_plan_module()
    monkeypatch.setattr(
        "sys.argv",
        ["plan_retro_run.py", "--repo-root", str(repo), "--changed-paths", "src/app.py", "--json"],
    )

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "retro.run_plan.v1"
    assert payload["envelope_version"] == "charness.run_plan_envelope.v1"


def test_retro_plan_bootstrap_reports_missing_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_plan_module()

    class MissingCandidate:
        def is_file(self) -> bool:
            return False

    class Ancestor:
        def __truediv__(self, _name: str) -> MissingCandidate:
            return MissingCandidate()

    class FakePath:
        def __init__(self, _value: str) -> None:
            pass

        def resolve(self) -> "FakePath":
            return self

        @property
        def parents(self) -> list[Ancestor]:
            return [Ancestor()]

    monkeypatch.setattr(module, "Path", FakePath)
    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        module._load_skill_runtime_bootstrap()
