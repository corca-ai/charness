from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_plan_module() -> ModuleType:
    script = ROOT / "skills" / "public" / "debug" / "scripts" / "plan_debug_run.py"
    spec = importlib.util.spec_from_file_location("debug_plan_run_under_test", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_plan(repo: Path) -> dict[str, object]:
    return json.loads(json.dumps(load_plan_module().build_plan(repo.resolve())))


def write_adapter(repo: Path) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/debug",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_debug_plan_scaffolds_when_current_artifact_is_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo)

    assert payload["schema_version"] == "debug.run_plan.v1"
    assert payload["mode"] == "fresh-investigation"
    assert payload["artifact"]["status"] == "missing"
    assert payload["next_action"]["kind"] == "scaffold-debug-artifact"
    assert payload["artifact"]["write_path"] == "charness-artifacts/debug/latest.md"
    assert "template" not in payload["scaffold"]

    required_paths = {read["path"] for read in payload["required_reads"]}
    assert "scripts/scaffold_debug_artifact.py" in required_paths
    assert "references/five-steps.md" in required_paths
    assert "references/debug-memory.md" in required_paths
    packet_ids = {packet["id"] for packet in payload["gate_packets"]}
    assert "debug-artifact-scaffold" in packet_ids
    assert "debug-artifact-shape" in packet_ids


def test_debug_plan_missing_adapter_adds_adapter_contract_read(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    payload = run_plan(repo)

    assert payload["ok"] is True
    assert payload["adapter"]["found"] is False
    required_paths = {read["path"] for read in payload["required_reads"]}
    assert "references/adapter-contract.md" in required_paths


def test_debug_plan_reports_missing_skill_runtime_bootstrap(monkeypatch) -> None:
    module = load_plan_module()

    class MissingBootstrapPath:
        def __init__(self, _path: object) -> None:
            pass

        def resolve(self) -> object:
            return type("ResolvedPath", (), {"parents": []})()

    monkeypatch.setattr(module, "Path", MissingBootstrapPath)

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        module._load_skill_runtime_bootstrap()


def test_debug_plan_continues_existing_current_artifact(tmp_path: Path) -> None:
    # A current pointer with NO `Resolution:` field defaults to OPEN: legacy and
    # in-progress artifacts keep continuing, so same-investigation resume is
    # preserved (only an explicit `Resolution: resolved` demotes the pointer).
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text("# Current Debug\n\n## Problem\n\nTODO\n", encoding="utf-8")

    payload = run_plan(repo)

    assert payload["mode"] == "continue-existing-artifact"
    assert payload["artifact"]["status"] == "current_pointer_exists"
    assert payload["artifact"]["resolution"] == "open"
    assert payload["artifact"]["line_count"] == 5
    assert payload["next_action"]["kind"] == "continue-existing-artifact"
    required_paths = [read["path"] for read in payload["required_reads"]]
    assert required_paths[0] == "charness-artifacts/debug/latest.md"


def test_debug_plan_continues_explicit_open_resolution(tmp_path: Path) -> None:
    # The genuine OPEN case: an in-progress artifact that explicitly declares
    # `Resolution: open` still routes to continue-existing-artifact. This is the
    # regression floor that the resolved-state guard must NOT break.
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text(
        "# Current Debug\n\n## Interrupt Decision\n\n- Resolution: open\n\n## Problem\n\nTODO\n",
        encoding="utf-8",
    )

    payload = run_plan(repo)

    assert payload["artifact"]["resolution"] == "open"
    assert payload["mode"] == "continue-existing-artifact"
    assert payload["next_action"]["kind"] == "continue-existing-artifact"
    required_paths = [read["path"] for read in payload["required_reads"]]
    assert required_paths[0] == "charness-artifacts/debug/latest.md"


def test_debug_plan_resolved_pointer_routes_fresh_with_prior_memory(tmp_path: Path) -> None:
    # The mis-fire fix: a current pointer that explicitly declares
    # `Resolution: resolved` is a CLOSED prior incident, not an open continuation.
    # A fresh bug must route to a fresh investigation with the canonical required
    # reads (five-steps + debug-memory) surfaced unburied, and the resolved
    # pointer offered as prior memory — not silently continued.
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text(
        "# Current Debug\n\n## Interrupt Decision\n\n- Resolution: resolved\n",
        encoding="utf-8",
    )

    payload = run_plan(repo)

    assert payload["artifact"]["resolution"] == "resolved"
    assert payload["mode"] == "fresh-investigation-with-prior-memory"
    assert payload["next_action"]["kind"] == "scaffold-debug-artifact"
    required_paths = [read["path"] for read in payload["required_reads"]]
    assert "scripts/scaffold_debug_artifact.py" in required_paths
    assert "references/five-steps.md" in required_paths
    assert "references/debug-memory.md" in required_paths
    # the resolved pointer is preserved as a prior-memory read, not lost
    assert "charness-artifacts/debug/latest.md" in required_paths


def test_debug_plan_unknown_resolution_value_fails_safe_to_continue(tmp_path: Path) -> None:
    # Fail-safe direction: any non-`resolved` value (incl. an unknown/typo'd one)
    # is read as open and continues, so the guard never wrongly DEMOTES an
    # in-progress artifact. The validator separately rejects non-enum values from
    # a valid `latest.md`, so this only governs the planner's defensive read.
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text(
        "# Current Debug\n\n## Interrupt Decision\n\n- Resolution: closed\n\n## Problem\n\nTODO\n",
        encoding="utf-8",
    )

    payload = run_plan(repo)

    assert payload["artifact"]["resolution"] == "open"
    assert payload["mode"] == "continue-existing-artifact"


def test_debug_plan_preserves_symlinked_current_pointer_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    target = debug_dir / "debug-2026-05-06-demo.md"
    target.write_text("# Demo Debug\n", encoding="utf-8")
    (debug_dir / "latest.md").symlink_to(target.name)

    payload = run_plan(repo)

    assert payload["artifact"]["status"] == "current_pointer_target_exists"
    assert payload["artifact"]["write_path"] == "charness-artifacts/debug/debug-2026-05-06-demo.md"
    assert payload["artifact"]["current_pointer_symlink_target"] == "debug-2026-05-06-demo.md"
    assert payload["next_action"]["write_artifact_path"] == "charness-artifacts/debug/debug-2026-05-06-demo.md"


def test_debug_plan_resolved_symlinked_latest_scaffolds_new_record_and_refresh(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    target = debug_dir / "debug-2026-05-06-demo.md"
    target.write_text(
        "# Demo Debug\n\n## Interrupt Decision\n\n- Resolution: resolved\n\n## Problem\n\nTODO\n",
        encoding="utf-8",
    )
    (debug_dir / "latest.md").symlink_to(target.name)

    payload = run_plan(repo)

    assert payload["mode"] == "fresh-investigation-with-prior-memory"
    assert payload["artifact"]["status"] == "current_pointer_target_exists"
    assert payload["artifact"]["resolution"] == "resolved"
    assert payload["scaffold"]["intent"] == "record"
    assert payload["scaffold"]["write_artifact_role"] == "durable_record"
    assert payload["scaffold"]["write_artifact_path"] != payload["artifact"]["write_path"]
    assert payload["next_action"]["command"].endswith("scaffold_debug_artifact.py --repo-root .")
    scaffold_gate = next(packet for packet in payload["gate_packets"] if packet["id"] == "debug-artifact-scaffold")
    assert scaffold_gate["command"] == payload["next_action"]["command"]
    assert payload["next_action"]["write_artifact_path"] == payload["scaffold"]["write_artifact_path"]
    assert payload["next_action"]["update_current_pointer_after_write"] is True
    assert "refresh_current_pointer.py" in payload["next_action"]["refresh_current_pointer_command"]
    assert "refresh the current pointer" in payload["next_action"]["instruction"]


def test_debug_plan_surfaces_prior_incidents_as_conditional_reads(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    old_prior = debug_dir / "debug-2026-04-01-provider-timeout.md"
    old_prior.write_text("# Old Provider Timeout Debug\n", encoding="utf-8")
    new_prior = debug_dir / "2026-06-01-provider-timeout.md"
    new_prior.write_text("# New Provider Timeout Debug\n", encoding="utf-8")
    os.utime(old_prior, (100, 100))
    os.utime(new_prior, (200, 200))

    payload = run_plan(repo)

    assert payload["mode"] == "fresh-investigation-with-prior-memory"
    assert payload["prior_incidents"][0]["path"] == "charness-artifacts/debug/2026-06-01-provider-timeout.md"
    assert payload["prior_incidents"][0]["title"] == "New Provider Timeout Debug"
    required_paths = {read["path"] for read in payload["required_reads"]}
    assert "charness-artifacts/debug/2026-06-01-provider-timeout.md" in required_paths
    assert "charness-artifacts/debug/debug-2026-04-01-provider-timeout.md" in required_paths


def test_debug_plan_caps_prior_incidents_and_allows_missing_titles(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    for index in range(7):
        path = debug_dir / f"debug-2026-06-0{index}-case.md"
        path.write_text("No markdown title here\n", encoding="utf-8")
        os.utime(path, (100 + index, 100 + index))

    payload = run_plan(repo)

    assert len(payload["prior_incidents"]) == 5
    assert payload["prior_incidents"][0]["path"] == "charness-artifacts/debug/debug-2026-06-06-case.md"
    assert payload["prior_incidents"][0]["title"] is None


def test_debug_plan_missing_prior_title_file_returns_none(tmp_path: Path) -> None:
    module = load_plan_module()

    assert module._title_for(tmp_path / "missing.md") is None


def test_debug_plan_interrupts_external_seam_risk_before_impl(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text(
        "\n".join(
            [
                "# Current Debug",
                "",
                "## Seam Risk",
                "",
                "- Risk Class: external-seam",
                "",
                "## Interrupt Decision",
                "",
                "- Next Step: spec",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = run_plan(repo)

    assert payload["mode"] == "risk-interrupt"
    assert payload["artifact"]["requires_interrupt"] is True
    assert payload["next_action"]["kind"] == "interrupt-to-spec"
    required_paths = {read["path"] for read in payload["required_reads"]}
    assert "references/document-seams.md" in required_paths
    assert "references/invariant-first-review.md" in required_paths


def test_debug_plan_main_emits_yaml(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    module = load_plan_module()
    monkeypatch.setattr(
        "sys.argv",
        [
            "plan_debug_run.py",
            "--repo-root",
            str(repo),
        ],
    )

    assert module.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["schema_version"] == "debug.run_plan.v1"


def test_debug_plan_help_includes_repo_root_help(monkeypatch, capsys) -> None:
    module = load_plan_module()
    monkeypatch.setattr("sys.argv", ["plan_debug_run.py", "--help"])

    with pytest.raises(SystemExit) as exc:
        module.main()

    assert exc.value.code == 0
    help_text = capsys.readouterr().out
    assert "--repo-root" in help_text
    assert "Repository root to analyze" in help_text
    assert "--json" not in help_text


def test_debug_plan_uses_canonical_forced_risk_taxonomy(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text(
        "\n".join(
            [
                "# Current Debug",
                "",
                "## Seam Risk",
                "",
                "- Risk Class: repeated-symptom",
                "- Generalization Pressure: none",
                "",
                "## Interrupt Decision",
                "",
                "- Next Step: impl",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = run_plan(repo)

    assert payload["mode"] == "risk-interrupt"
    assert payload["artifact"]["risk_classes"] == ["repeated-symptom"]
    assert payload["artifact"]["requires_interrupt"] is True
    assert payload["next_action"]["kind"] == "interrupt-to-spec"


def write_seam_risk_artifact(repo: Path, body: list[str]) -> None:
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text("\n".join([*body, ""]), encoding="utf-8")


SEAM_RISK_BODY = (
    "## Seam Risk",
    "",
    "- Interrupt ID: I1",
    "- Risk Class: external-seam",
    "- Generalization Pressure: factor-now",
    "",
    "## Interrupt Decision",
    "",
    "- Next Step: spec",
)


def test_debug_plan_ignores_fenced_template_quote_above_real_seam_risk(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_seam_risk_artifact(
        repo,
        [
            "# Current Debug",
            "",
            "The scaffold template declares:",
            "",
            "```",
            "- Risk Class: none",
            "- Generalization Pressure: none",
            "```",
            "",
            *SEAM_RISK_BODY,
        ],
    )

    payload = run_plan(repo)

    assert payload["artifact"]["risk_classes"] == ["external-seam"]
    assert payload["artifact"]["generalization_pressure"] == "factor-now"
    assert payload["artifact"]["requires_interrupt"] is True
    assert payload["mode"] == "risk-interrupt"
    assert payload["next_action"]["kind"] == "interrupt-to-spec"


def test_debug_plan_reads_unfenced_declaration_as_authoritative(tmp_path: Path) -> None:
    """Control: prose that is not fenced still declares state, including `none`."""
    repo = tmp_path / "repo"
    write_seam_risk_artifact(
        repo,
        [
            "# Current Debug",
            "",
            "## Seam Risk",
            "",
            "- Risk Class: none",
            "- Generalization Pressure: none",
        ],
    )

    payload = run_plan(repo)

    assert payload["artifact"]["risk_classes"] == ["none"]
    assert payload["artifact"]["requires_interrupt"] is False
    assert payload["mode"] == "continue-existing-artifact"
    assert payload["next_action"]["kind"] == "continue-existing-artifact"


def test_debug_plan_interrupts_when_forced_class_shares_line_with_unknown_token(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_seam_risk_artifact(
        repo,
        [
            "# Current Debug",
            "",
            "## Seam Risk",
            "",
            "- Interrupt ID: I1",
            "- Risk Class: external-seam, bogus",
            "- Generalization Pressure: none",
        ],
    )

    payload = run_plan(repo)

    assert payload["artifact"]["risk_classes"] == ["external-seam"]
    assert "bogus" in payload["artifact"]["risk_parse_error"]
    assert payload["artifact"]["requires_interrupt"] is True
    assert payload["mode"] == "risk-interrupt"
    assert payload["next_action"]["kind"] == "interrupt-to-spec"


def test_debug_plan_routes_unparseable_risk_line_to_repair(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_seam_risk_artifact(
        repo,
        [
            "# Current Debug",
            "",
            "## Seam Risk",
            "",
            "- Interrupt ID: I1",
            "- Risk Class: bogus",
            "- Generalization Pressure: none",
        ],
    )

    payload = run_plan(repo)

    assert payload["artifact"]["risk_scope_established"] is False
    assert payload["mode"] == "repair-risk-declaration"
    assert payload["next_action"]["kind"] == "repair-risk-declaration"
    assert "bogus" in payload["next_action"]["risk_parse_error"]


def test_debug_plan_legacy_artifact_without_seam_risk_still_continues(tmp_path: Path) -> None:
    """Control: a pre-taxonomy artifact declares no risk line and must not be refused."""
    repo = tmp_path / "repo"
    write_seam_risk_artifact(repo, ["# Legacy Debug", "", "## Problem", "", "something broke"])

    payload = run_plan(repo)

    assert payload["artifact"]["risk_scope_established"] is True
    assert payload["artifact"]["requires_interrupt"] is False
    assert payload["mode"] == "continue-existing-artifact"
    assert payload["next_action"]["kind"] == "continue-existing-artifact"


def test_a_risk_line_hidden_behind_an_unclosed_fence_is_unestablished(tmp_path: Path) -> None:
    """The S18 repair's own escape, wearing the opposite coat.

    Ignoring fenced content stops a quoted template being read as the author's
    declaration — and an UNCLOSED fence then makes every later line fenced, so the
    REAL declaration is dropped with it. The first cut fell through to the legacy
    `no risk line at all` carve-out and emitted `continue`, requires_interrupt
    False, risk_scope_established True, over a declared `external-seam`. Pre-fix
    code interrupted correctly on that input, so it was a regression, and nothing
    downstream catches it: `validate_debug_artifact` is byte-blind to fencing and
    passes the artifact clean.
    """
    repo = tmp_path / "repo"
    write_seam_risk_artifact(
        repo,
        [
            "# Current Debug",
            "",
            "```text",
            "- Risk Class: none",
            "- Generalization Pressure: none",
            "",
            "## Seam Risk",
            "",
            "- Interrupt ID: I1",
            "- Risk Class: external-seam",
            "- Generalization Pressure: factor-now",
        ],
    )

    payload = run_plan(repo)

    assert payload["artifact"]["risk_scope_established"] is False
    assert payload["mode"] == "repair-risk-declaration"
    assert "unclosed code fence" in str(payload["next_action"])


def test_a_closed_template_fence_above_the_real_declaration_still_interrupts(tmp_path: Path) -> None:
    """The paired control for the test above and for S18 itself.

    Same artifact with the template fence CLOSED: the quoted example is inert, the
    real declaration is read, and the forced class interrupts. Without this, the
    test above would also pass against a planner that refused every fenced artifact.
    """
    repo = tmp_path / "repo"
    write_seam_risk_artifact(
        repo,
        [
            "# Current Debug",
            "",
            "```text",
            "- Risk Class: none",
            "- Generalization Pressure: none",
            "```",
            "",
            "## Seam Risk",
            "",
            "- Interrupt ID: I1",
            "- Risk Class: external-seam",
            "- Generalization Pressure: factor-now",
        ],
    )

    payload = run_plan(repo)

    assert payload["artifact"]["risk_scope_established"] is True
    assert payload["artifact"]["risk_classes"] == ["external-seam"]
    assert payload["mode"] == "risk-interrupt"


def test_the_shape_packet_validates_the_artifact_this_run_writes(tmp_path: Path) -> None:
    """The emitted command must answer the question the packet's own label asks.

    `debug-artifact-shape` calls itself a schema gate for the current artifact and
    emitted the whole-corpus command, so its exit code reported the state of the entire
    historical debug directory instead. A consumer wrote a valid record, saw it reported
    validated, and still got exit 1 from unrelated legacy debt -- with nothing in the exit
    code to say the failure was not theirs.

    Asserted against the scaffold's own write path rather than a literal, so a scaffold
    that routes the write elsewhere (the resolved-followup and subject-refusal arms both
    do) cannot leave the gate pointed at a file nothing writes.
    """
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo)

    write_path = payload["scaffold"]["write_artifact_path"]
    shape = next(p for p in payload["gate_packets"] if p["id"] == "debug-artifact-shape")
    assert shape["command"].endswith(f"--paths {write_path}")
    # The scaffold packet's own validator command names the same artifact. Two packets in
    # one plan disagreeing about what is being judged is the state this repairs.
    scaffold_packet = next(p for p in payload["gate_packets"] if p["id"] == "debug-artifact-scaffold")
    assert scaffold_packet["validator_command"].endswith(f"--paths {write_path}")
