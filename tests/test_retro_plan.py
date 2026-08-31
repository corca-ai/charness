from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest
import yaml

from tests.quality_gates.git_fixture_support import init_git_repo

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relpath: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RETRO_OUTPUT_DIR_LIB = _load(
    "retro_output_dir_lib_plan_test", "scripts/retro_output_dir_lib.py"
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _init_git_repo_with_commit(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    init_git_repo(repo)
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
    assert {
        rule["id"] for rule in payload["date_activated_rules"]["rules"]  # type: ignore[index]
    } == {"north-star-alignment", "recurrence-lineage", "persisted-form"}

    paths = required_paths(payload)
    assert "references/expert-lens.md" in paths
    assert "scripts/scaffold_retro_artifact.py" in paths

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

    payload = run_plan(repo, changed_paths=["evals/fixture.json", "scripts/x.py"])

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
    trigger = next(item for item in unknown["gate_packets"] if item["id"] == "auto-session-trigger")
    assert trigger["trigger_scope"] == []
    assert trigger["trigger_scope_source"] == "explicit_paths"
    assert trigger["trigger_scope_status"] == "not-established"
    assert unknown["trigger_scope"] == []
    assert unknown["trigger_scope_status"] == "not-established"


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


def test_retro_plan_has_no_mode_concept(tmp_path: Path) -> None:
    """`weekly` was removed and `session` went with it: with one shape, a mode field
    that always holds the same value is noise, not information. Nothing read it."""
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo, changed_paths=["src/app.py"])

    assert "mode" not in payload
    assert "mode_reason" not in payload


def test_retro_plan_missing_adapter_adds_adapter_contract_read(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)

    payload = run_plan(repo, changed_paths=["src/app.py"])

    # No adapter file -> not found -> the adapter-contract repair read is added.
    assert "references/adapter-contract.md" in required_paths(payload)


def test_retro_plan_reads_summary_when_present(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    summary = repo / "charness-artifacts" / "retro" / "recent-lessons.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text("# Recent Lessons\n", encoding="utf-8")

    payload = run_plan(repo, changed_paths=["src/app.py"])

    assert "charness-artifacts/retro/recent-lessons.md" in required_paths(payload)


def test_retro_plan_promotes_adapter_evidence_with_path_status(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    adapter_path = repo / ".agents" / "retro-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "evidence_paths:\n"
        + "  - evidence/file.md\n"
        + "  - evidence/directory\n"
        + "  - evidence/missing.md\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "directory").mkdir(parents=True)
    (repo / "evidence" / "file.md").write_text("# Evidence\n", encoding="utf-8")

    payload = run_plan(repo, changed_paths=["src/app.py"])
    evidence = [read for read in payload["required_reads"] if read.get("kind") == "evidence"]  # type: ignore[index]

    assert [item["path"] for item in evidence] == [
        "evidence/file.md",
        "evidence/directory",
        "evidence/missing.md",
    ]
    assert [(item["available"], item["path_kind"]) for item in evidence] == [
        (True, "file"),
        (True, "directory"),
        (False, "missing"),
    ]
    assert evidence[0]["size_bytes"] > 0
    assert evidence[2]["unavailable_reason"] == "missing"
    # The directory row is the ONE place `available` and the measurement disagree by
    # design -- the path is there to open, and it is not a file to size. It was the
    # only row with no measurement assertion, which is how the pre-repair double
    # disclosure hid here. Round 2 named it.
    assert evidence[1]["measurement_state"] == "unavailable"
    assert evidence[1]["unavailable_reason"] == "not-a-file"
    assert "size_bytes" not in evidence[1]


def test_retro_plan_preserves_empty_adapter_evidence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo, changed_paths=["src/app.py"])

    assert [read for read in payload["required_reads"] if read.get("kind") == "evidence"] == []  # type: ignore[index]


def test_retro_plan_surfaces_adapter_metrics_after_persistence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    adapter_path = repo / ".agents" / "retro-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "metrics_commands:\n"
        + "  - python3 scripts/check_custom_metric.py --repo-root .\n",
        encoding="utf-8",
    )

    payload = run_plan(repo, changed_paths=["src/app.py"])
    metric = next(packet for packet in payload["gate_packets"] if packet["id"] == "adapter-metric-1")  # type: ignore[index]

    assert metric["command"] == "python3 scripts/check_custom_metric.py --repo-root ."
    assert metric["run_when"] == "after the retro artifact is written and persisted, before closeout"


def test_retro_plan_scaffold_uses_repo_declared_artifact_sections(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    adapter_path = repo / ".agents" / "retro-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "artifact_sections:\n"
        + "  - '## Repo Evaluation'\n"
        + "  - ''\n"
        + "  - 'Repo evaluation: TODO'\n",
        encoding="utf-8",
    )

    payload = run_plan(repo, changed_paths=["src/app.py"])
    scaffold = next(packet for packet in payload["gate_packets"] if packet["id"] == "retro-artifact-scaffold")  # type: ignore[index]
    template = load_plan_module().scaffold_retro_artifact.payload_for(repo, title=None)["template"]

    assert payload["adapter"]["valid"] is True  # type: ignore[index]
    assert scaffold["write_artifact_path"].endswith("-session-retro.md")
    assert "## Repo Evaluation" in template


def test_retro_plan_infers_work_paths_from_recent_commits(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    _init_git_repo_with_commit(repo)  # clean worktree after commit

    payload = run_plan(repo)  # no changed_paths -> infer from repo state

    assert payload["work_paths_source"] == "recent_commits"
    assert payload["work_class"] in {"ordinary", "system-improving", "docs", "unknown"}
    packet = next(item for item in payload["gate_packets"] if item["id"] == "auto-session-trigger")  # type: ignore[index]
    assert packet["command"].endswith("--base-ref HEAD^ --head-ref HEAD")
    assert packet["trigger_scope"] == "HEAD^..HEAD"
    assert packet["trigger_scope_source"] == "recent_commits"
    assert payload["trigger_scope"] == "HEAD^..HEAD"
    assert payload["trigger_scope_source"] == "recent_commits"
    assert payload["trigger_scope_status"] == "established"


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


def test_retro_plan_main_emits_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    module = load_plan_module()
    monkeypatch.setattr(
        "sys.argv",
        ["plan_retro_run.py", "--repo-root", str(repo), "--changed-paths", "src/app.py"],
    )

    assert module.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
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


def test_retired_weekly_keys_pass_through_without_error(tmp_path: Path) -> None:
    """Upgrade safety for the `weekly` deletion: a consumer adapter still carrying
    `default_mode` / `weekly_window_days` / `snapshot_path` must resolve clean. The
    resolver validates only known fields, so unknown keys are ignored rather than
    rejected — without this named test the only proof is an incidental fixture line."""
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/retro",
                "default_mode: weekly",
                "weekly_window_days: 7",
                "snapshot_path: .charness/retro/weekly-latest.json",
                "summary_path: charness-artifacts/retro/recent-lessons.md",
                "evidence_paths: []",
                "metrics_commands: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = run_plan(repo, changed_paths=["src/app.py"])

    adapter_packet = next(p for p in payload["gate_packets"] if p["id"] == "adapter-readiness")
    assert adapter_packet["errors"] == []
    assert adapter_packet["status"] == "pass"
def test_the_retro_shape_packet_is_scoped_to_the_artifact_this_run_writes(
    tmp_path: Path,
) -> None:
    """Scoping this packet was landed, REVERSED on release eve, and is now restored.

    The reversal's reason was real: `validate_retro_artifact` keyed its candidate filter
    and its owned prefix on the literal `charness-artifacts/retro/`, while the path this
    packet names comes from the adapter's `output_dir`. Where a consumer declared a
    different directory the two disagreed, and the scoped command printed "Validated 0
    retro artifact(s)." and exited 0 -- a schema gate reporting green having opened
    nothing. That validator now resolves its prefix through retro's own adapter.

    Asserted against the scaffold's OWN `write_artifact_path`, never a literal: a gate
    pointed at a file nothing writes is the failure this scoping can produce, and a
    literal here could not see it.
    """
    repo = tmp_path / "repo"
    # A CUSTOM output_dir, because that is the configuration the repair is about. Written
    # against the default, this test passed identically before the fix while its docstring
    # narrated a consumer "that declared a different directory" -- a test measuring nothing
    # the paragraph above it claims.
    write_adapter(repo)
    adapter = repo / ".agents" / "retro-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8").replace(
            "output_dir: charness-artifacts/retro", "output_dir: artifacts/retros"
        ),
        encoding="utf-8",
    )

    payload = run_plan(repo)

    shape = next(p for p in payload["gate_packets"] if p["id"] == "retro-artifact-shape")
    scaffold = next(p for p in payload["gate_packets"] if p["id"] == "retro-artifact-scaffold")
    assert scaffold["write_artifact_path"].startswith("artifacts/retros/")
    assert f'--paths {scaffold["write_artifact_path"]}' in shape["command"]
    assert "after the retro artifact is written" in shape["run_when"]
    # The path the packet names is the one the validator would own for THIS repo.
    prefix = RETRO_OUTPUT_DIR_LIB.retro_artifact_prefix(repo)
    assert scaffold["write_artifact_path"].startswith(prefix)


# --- summary_path opt-out: unset / configured / explicit-null ------------------
#
# A consumer whose lesson ledger is the sole lesson surface could not decline the
# Markdown projection: the contract called the field optional, but omitting it and
# nulling it both resolved to the same default, so the next retro silently
# recreated a second lesson owner the repo had deliberately removed.


def _retro_repo(tmp_path, adapter_body: str):
    from pathlib import Path

    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(adapter_body, encoding="utf-8")
    return Path(repo)


def _resolved(repo):
    import importlib

    module = importlib.import_module("skills.public.retro.scripts.resolve_adapter")
    return module.load_adapter(repo)


def test_omitting_summary_path_keeps_the_default_projection(tmp_path) -> None:
    repo = _retro_repo(tmp_path, "version: 1\nrepo: consumer\n")
    resolved = _resolved(repo)
    assert resolved["data"]["summary_path"] == "charness-artifacts/retro/recent-lessons.md"
    assert resolved["field_state"]["summary_path"] == "unset"


def test_declaring_summary_path_null_disables_the_projection(tmp_path) -> None:
    repo = _retro_repo(tmp_path, "version: 1\nrepo: consumer\nsummary_path: null\n")
    resolved = _resolved(repo)
    # The two states a `.get`-based validator could not tell apart.
    assert resolved["data"]["summary_path"] is None
    assert resolved["field_state"]["summary_path"] == "explicit-null"


def test_a_declared_summary_path_still_wins(tmp_path) -> None:
    repo = _retro_repo(tmp_path, "version: 1\nrepo: consumer\nsummary_path: docs/lessons.md\n")
    resolved = _resolved(repo)
    assert resolved["data"]["summary_path"] == "docs/lessons.md"
    assert resolved["field_state"]["summary_path"] == "configured"


def test_an_empty_string_is_not_the_opt_out_spelling(tmp_path) -> None:
    """It stays a string and resolves to the repository root, which is why null is the spelling."""
    repo = _retro_repo(tmp_path, "version: 1\nrepo: consumer\nsummary_path: ''\n")
    resolved = _resolved(repo)
    assert resolved["data"]["summary_path"] == ""
    assert resolved["field_state"]["summary_path"] == "configured"


def _planned_read_paths(repo, resolved) -> list[str]:
    import importlib

    plan = importlib.import_module("skills.public.retro.scripts.plan_retro_run")
    reads = plan._required_reads(
        repo_root=repo,
        adapter=resolved,
        artifact={"exists": False},
        lens_brief={"why": "test lens brief"},
    )
    return [str(item["path"]) for item in reads]


def test_the_planner_reads_no_digest_when_the_projection_is_disabled(tmp_path) -> None:
    """A digest ON DISK must still not be read once the repo declared it is not the owner."""
    disabled = _retro_repo(tmp_path, "version: 1\nrepo: consumer\nsummary_path: null\n")
    digest = disabled / "charness-artifacts" / "retro" / "recent-lessons.md"
    digest.write_text("# stale projection\n", encoding="utf-8")
    assert all("recent-lessons.md" not in path for path in _planned_read_paths(disabled, _resolved(disabled)))

    # Control: the SAME on-disk digest is read when the projection is not disabled,
    # so the assertion above is about the opt-out and not about the fixture.
    enabled = _retro_repo(tmp_path / "other", "version: 1\nrepo: consumer\n")
    (enabled / "charness-artifacts" / "retro" / "recent-lessons.md").write_text("# live\n", encoding="utf-8")
    assert any("recent-lessons.md" in path for path in _planned_read_paths(enabled, _resolved(enabled)))
