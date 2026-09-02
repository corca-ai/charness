from __future__ import annotations

import importlib.util
import re
import runpy
import shutil
import sys
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from scripts.gates import check_artifact_surface_preflight as preflight
from scripts.plugin_export import export_plugin as export_plugin_module
from skills.public.critique.scripts.verification_retry import build_retry_key
from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT


def _minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        (ROOT / "AGENTS.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return repo


# --- registry / surface resolution (pure) -------------------------------------


def test_surface_for_path_maps_prefix_families() -> None:
    assert (
        preflight.surface_for_path("charness-artifacts/critique/x.md").artifact_type == "critique"
    )
    assert (
        preflight.surface_for_path("charness-artifacts/ideation/x.md").artifact_type == "ideation"
    )
    assert preflight.surface_for_path("charness-artifacts/retro/x.md").artifact_type == "retro"
    # unknown / non-md / out-of-family -> None
    assert preflight.surface_for_path("charness-artifacts/spec/x.md") is None
    assert preflight.surface_for_path("scripts/x.py") is None
    assert preflight.surface_for_path("charness-artifacts/critique/x.txt") is None


def test_retro_surface_excludes_rolled_up_and_history() -> None:
    # the retro validator skips recent-lessons.md and history/, so the commit-
    # boundary arm must not block on them either.
    assert preflight.surface_for_path("charness-artifacts/retro/recent-lessons.md") is None
    assert preflight.surface_for_path("charness-artifacts/retro/history/2026-01-01-x.md") is None
    assert (
        preflight.surface_for_path("charness-artifacts/retro/2026-06-08-x.md").artifact_type
        == "retro"
    )


def test_critique_surface_excludes_append_only_round_records() -> None:
    # Round records are evidence written by record_round_findings.py. They have
    # a receipt/findings shape, not the final critique shape; routing them to the
    # critique validator made a valid reviewer round fail only at commit time.
    assert preflight.surface_for_path("charness-artifacts/critique/rounds/2026-08-21-w.md") is None
    assert (
        preflight.surface_for_path("charness-artifacts/critique/2026-08-21-w.md").artifact_type
        == "critique"
    )
    assert preflight.surface_for_path("charness-artifacts/critique/../outside.md") is None


def test_surface_for_path_maps_adapter_scoped_quality() -> None:
    # debug/quality are the remaining adapter-scoped artifact families.
    assert preflight.surface_for_path("charness-artifacts/debug/x.md").artifact_type == "debug"
    assert preflight.surface_for_path("charness-artifacts/quality/x.md").artifact_type == "quality"
    assert preflight.surface_for_path("docs/other.md") is None
    # adapter-scoped validators validate-all (no --paths) and are author-time-only
    # (NOT in the fail-fast commit-boundary sweep — a validate-all gate there would
    # block a commit on pre-existing siblings the author never touched).
    quality = preflight.surface_for_type("quality")
    assert quality.paths_arg is False
    assert quality.commit_boundary is False
    # debug left that tier once its validator gained `--paths` (#454 follow-up): its
    # shape was previously discoverable only at the RELEASE gate, which cost ~10
    # round trips. Changed-scoped, it is a commit-boundary peer of critique/retro.
    assert preflight.surface_for_type("debug").paths_arg is True
    assert preflight.surface_for_type("debug").commit_boundary is True


def test_surface_for_type_unknown_is_none() -> None:
    assert preflight.surface_for_type("nope") is None


def test_extract_section_pulls_named_block() -> None:
    text = "intro\n## A\nbody a\n## B\nbody b\n"
    assert preflight._extract_section(text, "## A").strip() == "## A\nbody a"
    assert "not found" in preflight._extract_section(text, "## Z")


# --- commit-boundary grouping + blocking (logic, no real validators) ----------


def _fake_run(rc_for):
    def runner(repo_root, script, args):
        import subprocess

        command = [str(script), *args]
        joined = " ".join(command)
        return subprocess.CompletedProcess(command, rc_for(joined), stdout="out\n", stderr="err\n")

    return runner


def test_changed_artifacts_groups_by_validator_and_passes(monkeypatch) -> None:
    monkeypatch.setattr(preflight, "_run_repo_script", _fake_run(lambda _cmd: 0))
    report = preflight.changed_artifacts(
        ROOT,
        [
            "charness-artifacts/critique/a.md",
            "charness-artifacts/critique/b.md",
            "charness-artifacts/critique/rounds/2026-08-21-round.md",
            "charness-artifacts/critique/release-packet.md",
            "charness-artifacts/ideation/c.md",
            "charness-artifacts/retro/recent-lessons.md",  # excluded -> ignored
            "scripts/x.py",  # out-of-family -> ignored
        ],
    )
    assert report["status"] == "ok"
    # two owning validators (critique + ideation); the critique one carries both paths
    checked = {row["validator"]: row["paths"] for row in report["checked"]}
    assert "scripts/validate_critique_artifacts.py" in checked
    assert checked["scripts/validate_critique_artifacts.py"] == [
        "charness-artifacts/critique/a.md",
        "charness-artifacts/critique/b.md",
        "charness-artifacts/critique/release-packet.md",
    ]
    assert "scripts/gates/validate_ideation_artifact.py" in checked
    # recent-lessons + scripts produced no group
    assert "scripts/gates/validate_retro_artifact.py" not in checked


def test_changed_artifacts_refuses_malformed_paths_instead_of_silently_omitting() -> None:
    report = preflight.changed_artifacts(
        ROOT,
        ["charness-artifacts/critique/../../../../etc/hostname"],
    )
    assert report["status"] == "blocked"
    assert report["blocked"] == ["path-resolution"]
    assert "malformed repo-relative path" in report["path_error"]


def test_changed_artifacts_blocks_when_owning_validator_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        preflight, "_run_repo_script", _fake_run(lambda cmd: 1 if "critique" in cmd else 0)
    )
    report = preflight.changed_artifacts(
        ROOT,
        ["charness-artifacts/critique/bad.md", "charness-artifacts/ideation/ok.md"],
    )
    assert report["status"] == "blocked"
    assert report["blocked"] == ["scripts/validate_critique_artifacts.py"]


def test_changed_artifacts_skips_author_time_only_surfaces(monkeypatch) -> None:
    # debug/quality are author-time-only (commit_boundary=False), so the
    # commit-boundary arm must NOT run them even when their paths change — the broad
    # gate is their enforcement, and the fail-fast sweep stays changed-scoped.
    captured: list[list[str]] = []

    def fake_run(repo_root, script, args):
        import subprocess

        captured.append([str(script), *args])
        return subprocess.CompletedProcess([str(script), *args], 0, stdout="", stderr="")

    monkeypatch.setattr(preflight, "_run_repo_script", fake_run)
    report = preflight.changed_artifacts(
        ROOT,
        ["charness-artifacts/quality/b.md"],
    )
    assert report["status"] == "ok"
    assert report["checked"] == []  # neither adapter-scoped surface runs at the commit boundary
    assert captured == []


def test_changed_artifacts_noop_for_unrelated_paths(monkeypatch) -> None:
    monkeypatch.setattr(preflight, "_run_repo_script", _fake_run(lambda _cmd: 1))
    report = preflight.changed_artifacts(ROOT, ["docs/x.md", "scripts/y.py"])
    assert report["status"] == "ok"
    assert report["checked"] == []


# --- in-process integration against the real repo -----------------------------
# Called in-process (not via subprocess) on purpose: the dispatcher is import-safe,
# so the test exercises its callable behavior directly. The dispatcher
# still subprocesses the real scaffold/validator internally, so these remain honest
# end-to-end checks of the shape source + the relocated verdict.


def test_emit_stub_critique_carries_required_sections() -> None:
    text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("critique"))
    assert code == 0
    # the scaffold stub must carry the validator-required sections by construction
    assert "## Reviewer Tier Evidence" in text
    assert "## Structured Findings" in text


def test_exported_preflight_resolves_flattened_scaffold_and_refuses_invalid_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The installed dispatcher must use its package, not the consumer cwd.

    The source registry intentionally keeps ``skills/public/...`` paths, while
    an exported plugin only carries ``skills/...``. A missing or duplicated
    candidate is a broken package shape, not permission to fall back to a
    consumer-owned path.
    """
    export_root = tmp_path / "export"
    manifest = export_plugin_module.load_manifest(ROOT, "charness")
    plugin_root = export_plugin_module.export_plugin(
        ROOT,
        export_root,
        manifest,
        "codex",
        with_marketplace=False,
    )
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    dispatcher = plugin_root / "scripts" / "check_artifact_surface_preflight.py"
    dispatcher_module = load_script_module("exported_check_artifact_surface_preflight", dispatcher)

    def run_dispatcher():
        return run_loaded_script_main(
            str(dispatcher),
            dispatcher_module,
            "--repo-root",
            str(consumer),
            "--type",
            "critique",
            "--emit-stub",
        )

    monkeypatch.chdir(consumer)
    positive = run_dispatcher()
    assert positive.returncode == 0, positive.stderr
    assert "## Reviewer Tier Evidence" in positive.stdout
    assert "## Structured Findings" in positive.stdout

    flattened_scaffold = (
        plugin_root / "skills" / "critique" / "scripts" / "scaffold_critique_artifact.py"
    )
    scaffold_backup = tmp_path / "scaffold_critique_artifact.py"
    shutil.copy2(flattened_scaffold, scaffold_backup)
    flattened_scaffold.unlink()
    missing = run_dispatcher()
    assert missing.returncode == 1
    missing_output = missing.stdout + missing.stderr
    assert "missing shape source" in missing_output
    assert "flattened-installed=" in missing_output

    flattened_scaffold.parent.mkdir(parents=True, exist_ok=True)
    canonical_scaffold = (
        plugin_root / "skills" / "public" / "critique" / "scripts" / "scaffold_critique_artifact.py"
    )
    canonical_scaffold.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(scaffold_backup, canonical_scaffold)
    shutil.copy2(scaffold_backup, flattened_scaffold)
    ambiguous = run_dispatcher()
    assert ambiguous.returncode == 1
    ambiguous_output = ambiguous.stdout + ambiguous.stderr
    assert "ambiguous shape source" in ambiguous_output
    assert "canonical=" in ambiguous_output and "flattened-installed=" in ambiguous_output


def test_describe_quality_binds_artifact_path_never_paths() -> None:
    # An adapter-scoped surface (paths_arg=False) must NOT get --paths — its validator
    # has no such flag. It used to fall through to a surface-level validate-all verdict;
    # The verdict is about the file the author is holding.
    target = "charness-artifacts/quality/2026-07-25-quality-review.md"
    out = preflight.describe(ROOT, preflight.surface_for_type("quality"), target_rel=target)
    assert "owning validator: python3 scripts/gates/validate_quality_artifact.py --repo-root ." in out
    assert "--paths" not in out
    assert f"--artifact-path {target}" in out
    assert f"current verdict on {target}:" in out


def test_describe_debug_is_changed_scoped_after_gaining_paths() -> None:
    # debug moved to the changed-scoped tier, so describe must now bind --paths to
    # the target rather than reporting a whole-corpus verdict.
    out = preflight.describe(
        ROOT, preflight.surface_for_type("debug"), target_rel="charness-artifacts/debug/latest.md"
    )
    assert "--paths charness-artifacts/debug/latest.md" in out


def test_changed_artifacts_passes_scaffold_roundtrip(
    tmp_path: Path,
) -> None:
    repo = _minimal_repo(tmp_path)
    # the critique scaffold's own render must pass its validator at the commit
    # boundary (round-trip), proving the shape-by-construction arm is real.
    stub_text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("critique"))
    assert code == 0
    # The stub's typed floors (`## Fresh-Eye Satisfaction`, the Boundary
    # Ownership `Verdict:` line) are deliberately NOT pre-filled (an unedited
    # stub must not satisfy them — a same-observer rubber stamp for free), so
    # round-trip here fills them in PLACE, keeping every later stub section,
    # proving the shape an author actually submits. A truncating fill would
    # silently drop any floor section added after Fresh-Eye (that drift shipped
    # once: the Boundary Ownership floor landed and this test stayed truncating).
    head, heading, rest = stub_text.partition("## Fresh-Eye Satisfaction")
    assert heading, "critique stub must still carry the Fresh-Eye Satisfaction heading"
    _body, sep, tail = rest.partition("\n## ")
    filled_in_stub = f"{head}{heading}\n\nparent-delegated\n{sep}{tail}"
    verdict_lines = [
        line for line in filled_in_stub.splitlines() if line.startswith("- Verdict: TODO")
    ]
    assert verdict_lines, "critique stub must still carry the Boundary Ownership Verdict TODO"
    filled_in_stub = filled_in_stub.replace(verdict_lines[0], "- Verdict: single-surface")
    # The tier block is the third thing an author fills, and leaving it at its
    # scaffold defaults made the asserted-green shape a `parent-delegated` claim
    # over a record stating no reviewer was ever spawned — the same truncating-fill
    # drift this test's comment above records, one floor further down.
    for stub_line, filled in (
        ("- Requested tier: TODO", "- Requested tier: bounded-reviewer"),
        ("- Requested spawn fields: TODO", "- Requested spawn fields: model, reasoning effort"),
        ("- Application state: TODO", "- Application state: n/a"),
        (
            "- Host exposure state: pending-parent-spawn",
            "- Host exposure state: requested_fields_sent",
        ),
        ("- Delivery state: pending-parent-spawn", "- Delivery state: findings-received"),
    ):
        matches = [line for line in filled_in_stub.splitlines() if line.startswith(stub_line)]
        assert matches, f"critique stub must still carry `{stub_line}`"
        filled_in_stub = filled_in_stub.replace(matches[0], filled)
    scope_values = {
        "Claim under test": "the scaffolded critique record binds its retry decision",
        "Changed surfaces": "critique scaffold and its validator consumer",
        "Minimum sufficient proof": "validator recomputes the retry key",
        "Deliberately omitted checks": "the subject suite is outside this fixture",
        "Verifier contract": "critique artifact validator reads this section",
        "Failure classification": "none",
        "Negative control": "none with rationale: fixture has no verifier-only claim",
        "Subject identity": "sha256:" + "1" * 64,
        "Verifier identity": "sha256:" + "2" * 64,
        "Input identity": "sha256:" + "3" * 64,
        "Failure identity": "stable:gate-failed",
        "Evidence identity": "none",
        "Retry disposition": "first-attempt",
    }
    for field, value in scope_values.items():
        filled_in_stub, replacements = re.subn(
            rf"^- {re.escape(field)}:.*$",
            f"- {field}: {value}",
            filled_in_stub,
            count=1,
            flags=re.MULTILINE,
        )
        assert replacements == 1, f"critique stub must still carry `- {field}: TODO`"
    retry_key = build_retry_key(
        subject=scope_values["Subject identity"],
        verifier=scope_values["Verifier identity"],
        input_identity=scope_values["Input identity"],
        failure=scope_values["Failure identity"],
    )
    filled_in_stub, replacements = re.subn(
        r"^- Retry key:.*$",
        f"- Retry key: {retry_key}",
        filled_in_stub,
        count=1,
        flags=re.MULTILINE,
    )
    assert replacements == 1, "critique stub must still carry `- Retry key: TODO`"
    target = repo / "charness-artifacts" / "critique" / "_preflight_roundtrip_selftest.md"
    target.parent.mkdir(parents=True)
    target.write_text(filled_in_stub, encoding="utf-8")
    rel = target.relative_to(repo).as_posix()

    report = preflight.changed_artifacts(repo, [rel])
    assert report["status"] == "ok", report


def test_main_errors_on_unknown_surface(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["x", "--path", "charness-artifacts/spec/x.md"])
    assert preflight.main() == 2
    assert "no registered surface" in capsys.readouterr().err


# --- #335: cover the changed-line gaps v0.28.0 left in this dispatcher ---------


def test_resolve_returns_raw_for_out_of_repo_path() -> None:
    # _resolve's ValueError arm: a path that does not live under the repo root is
    # returned verbatim (it can never map to a surface, but must not crash).
    assert preflight._resolve(ROOT, "/nonexistent/outside/x.md") == "/nonexistent/outside/x.md"


def test_shape_text_handles_each_missing_shape_source() -> None:
    critique = preflight.surface_for_type("critique")
    # scaffold render failure -> the "(could not render scaffold ...)" arm
    bad_scaffold = replace(critique, scaffold="scripts/does_not_exist_scaffold.py")
    assert "could not render scaffold" in preflight._shape_text(ROOT, bad_scaffold)
    # template-section source that points at a missing template -> "(template ... not found)"
    bad_template = replace(critique, scaffold=None, template_section="nope/missing.md|## Heading")
    assert "not found" in preflight._shape_text(ROOT, bad_template)
    # no shape source at all -> "(no shape source registered)"
    no_source = replace(critique, scaffold=None, template_section=None)
    assert preflight._shape_text(ROOT, no_source) == "(no shape source registered)"


def test_emit_stub_scaffold_failure_returns_code_one() -> None:
    bad = replace(
        preflight.surface_for_type("critique"), scaffold="scripts/does_not_exist_scaffold.py"
    )
    text, code = preflight.emit_stub(ROOT, bad)
    assert code == 1
    assert text  # surfaces the scaffold's stderr/stdout, not silence


def test_describe_prefix_surface_includes_paths_and_failure_detail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # critique is paths_arg=True: describe must pass --paths AND, when the file
    # fails its owning validator, echo the failure detail. Force the FAIL arm via
    # a stubbed repo-script runner (independent of the critique validator's enforce-when-present
    # rules), which exercises describe's --paths/verdict/detail lines.
    import subprocess

    def failing_run(repo_root, script, args):
        return subprocess.CompletedProcess(
            [str(script), *args], 1, stdout="", stderr="missing reviewer-tier section"
        )

    monkeypatch.setattr(preflight, "_run_repo_script", failing_run)
    repo = _minimal_repo(tmp_path)
    target = repo / "charness-artifacts" / "critique" / "_preflight_describe_selftest.md"
    target.parent.mkdir(parents=True)
    target.write_text("# not a real critique\n", encoding="utf-8")
    rel = target.relative_to(repo).as_posix()
    out = preflight.describe(repo, preflight.surface_for_type("critique"), target_rel=rel)
    assert f"--paths {rel}" in out
    assert "current verdict on" in out and "FAIL" in out
    assert "missing reviewer-tier section" in out


def test_changed_artifacts_report_carries_the_verdict_and_the_blocked_remedy() -> None:
    """Was `test_format_changed_renders_ok_and_blocked_reports`, before the YAML migration.

    `_format_changed` is gone with the text channel, and `changed_artifacts_report` is
    what the `--changed-artifacts` arm now emits. Of the three things the text renderer
    carried, two were already derivable from the report (`[ok]`/`[BLOCK]` is `returncode`,
    the echoed detail is the row's own `stderr`/`stdout`) and one was NOT: what an
    operator does about a block. So this asserts the derivable pair survives the fold
    unaltered, and that the remedy — the only added information — is on the payload,
    on the blocked report and only there.
    """
    ok_report = {
        "status": "ok",
        "checked": [
            {
                "validator": "scripts/validate_critique_artifacts.py",
                "paths": ["a.md"],
                "returncode": 0,
                "stdout": "",
                "stderr": "",
            },
        ],
    }
    ok_payload = preflight.changed_artifacts_report(ok_report)
    assert ok_payload["status"] == "ok"
    assert ok_payload["checked"][0]["returncode"] == 0
    # An `ok` report carries no remedy: there is nothing to remedy, and a remedy line
    # printed beside a passing verdict is the misleading-verdict class this arm avoids.
    assert "remedy" not in ok_payload

    blocked_report = {
        "status": "blocked",
        "checked": [
            {
                "validator": "scripts/validate_critique_artifacts.py",
                "paths": ["bad.md"],
                "returncode": 1,
                "stdout": "",
                "stderr": "missing section X",
            },
        ],
    }
    blocked_payload = preflight.changed_artifacts_report(blocked_report)
    assert blocked_payload["status"] == "blocked"
    assert blocked_payload["checked"][0]["returncode"] == 1
    assert blocked_payload["checked"][0]["stderr"] == "missing section X"
    assert "owning validator failed at the commit boundary" in blocked_payload["remedy"]
    # The fold must not mutate its input: the arm emits a report it also returns to
    # `main` for the exit code, and an in-place `remedy` would leak into that report.
    assert "remedy" not in blocked_report


def test_main_changed_artifacts_emits_the_blocked_report(monkeypatch, capsys) -> None:
    """Was `test_main_changed_artifacts_text_and_json`: there is one channel now.

    The old test ran `main` twice — once for the text arm, once for `--json` — because
    the arm branched on the flag. `--json` is deleted and output is unconditionally
    YAML, so the second run would be a re-run of the first; what is kept is the pair
    the two runs jointly proved: the blocked exit code, and a machine-readable
    document that names the failing validator and its detail.
    """
    blocked = {
        "status": "blocked",
        "blocked": ["scripts/validate_critique_artifacts.py"],
        "checked": [
            {
                "validator": "scripts/validate_critique_artifacts.py",
                "paths": ["bad.md"],
                "returncode": 1,
                "stdout": "",
                "stderr": "boom",
            },
        ],
    }
    monkeypatch.setattr(preflight, "changed_artifacts", lambda repo_root, paths: blocked)
    monkeypatch.setattr(
        sys, "argv", ["x", "--changed-artifacts", "charness-artifacts/critique/bad.md"]
    )
    assert preflight.main() == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["status"] == "blocked"
    assert payload["blocked"] == ["scripts/validate_critique_artifacts.py"]
    # The `[BLOCK]` marker and the echoed stderr the text arm printed, on the payload.
    assert payload["checked"][0]["returncode"] == 1
    assert payload["checked"][0]["stderr"] == "boom"
    assert "owning validator failed at the commit boundary" in payload["remedy"]


def test_main_changed_artifacts_ok_returns_zero(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["x", "--changed-artifacts", "docs/unrelated.md"])
    assert preflight.main() == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["checked"] == []


def test_main_emit_stub_writes_stub(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["x", "--type", "critique", "--emit-stub"])
    assert preflight.main() == 0
    assert "## Reviewer Tier Evidence" in capsys.readouterr().out


def test_main_requires_one_selector(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["x"])
    with pytest.raises(SystemExit) as exc:  # parser.error exits 2
        preflight.main()
    assert exc.value.code == 2


def test_module_main_guard_executes(monkeypatch) -> None:
    # cover `sys.exit(main())` (the __main__ guard) in-process via runpy, not a
    # subprocess, so the dispatcher stays on its in-process callable path.
    monkeypatch.setattr(sys, "argv", ["x", "--type", "critique"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(
            str(ROOT / "scripts" / "check_artifact_surface_preflight.py"), run_name="__main__"
        )
    assert exc.value.code == 0


# --- closeout-draft author-time surface -----------------------------------------


def _load_describe(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _option_help_block(output: str, option: str) -> str:
    """Return one wrapped option block from argparse output, not usage text."""
    lines = output.splitlines()
    options_start = lines.index("options:")
    option_line = re.compile(rf"^  {re.escape(option)}(?:\s|$)")
    start = next(i for i in range(options_start + 1, len(lines)) if option_line.match(lines[i]))
    next_option = re.compile(r"^  --[a-z0-9][a-z0-9-]*(?:\s|$)")
    end = next((i for i in range(start + 1, len(lines)) if next_option.match(lines[i])), len(lines))
    return " ".join(" ".join(lines[start:end]).split())


def test_closeout_draft_surface_is_author_time_shape_only() -> None:
    s = preflight.surface_for_type("closeout-draft")
    assert s is not None
    assert s.validator is None  # a verdict needs the full validate-closeout-draft command
    assert s.scaffold is None
    assert s.commit_boundary is False  # author-time shape only; the validator stays enforcement
    assert s.shape_command == ("skills/public/issue/scripts/describe_closeout_draft_shape.py",)
    out = preflight.describe(ROOT, s, target_rel=None)
    # the owner line names the real validator command, not the complete-flip default
    assert "validate-closeout-draft" in out


def test_closeout_draft_describe_emits_the_named_required_fields() -> None:
    out = preflight.describe(ROOT, preflight.surface_for_type("closeout-draft"), target_rel=None)
    # the four fields the goal names + the carrier-body-source trap
    assert "resolution_critique" in out and "tool signal:" in out
    assert "COMMIT MESSAGE" in out and "direct-commit" in out
    assert "Closes #N" in out  # close keyword
    assert "Classification ledger fields" in out


def test_closeout_draft_describe_help_describes_repo_root(capsys) -> None:
    desc = _load_describe(
        "skills/public/issue/scripts/describe_closeout_draft_shape.py", "help_dccs"
    )
    with pytest.raises(SystemExit) as exc:
        desc.main(["--help"])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "Repository root accepted by artifact-surface preflight" in _option_help_block(
        output, "--repo-root"
    )


def test_closeout_draft_shape_pins_live_verifier_constants() -> None:
    # drift guard: every enforced enum/field the verifier checks appears in the
    # surfaced shape, rendered from the live constants (never a stale hand copy).
    desc = _load_describe("skills/public/issue/scripts/describe_closeout_draft_shape.py", "dccs")
    shape = desc.required_shape()
    for value in (
        *desc._VERIFY.CLASSIFICATIONS,
        *desc._VERIFY.CARRIERS,
        *desc._VERIFY.MANUAL_FALLBACK_REASONS,
        *desc._CRITIQUE.CRITIQUE_REQUIRED_CLASSIFICATIONS,
    ):
        assert value in shape, value
    for classification in desc._VERIFY.CLASSIFICATIONS:
        for field_id, _aliases in desc._BODY._classification_requirements(classification):
            assert field_id in shape or f"{field_id.title()}:" in shape, field_id


def test_closeout_draft_shape_observes_consolidated_carrier_and_readback_boundaries() -> None:
    """A describe-first surface must not prescribe a body its own gate refuses."""
    desc = _load_describe(
        "skills/public/issue/scripts/describe_closeout_draft_shape.py", "dccs_consolidated"
    )
    shape = desc.required_shape("consolidated")
    classification = desc._CONSOLIDATED.CLASSIFICATION
    probe = "Closes #5\nJtbd: move the work\nConsolidated into: #6\n"
    refused = [
        carrier
        for carrier in desc._VERIFY.CARRIERS
        if desc._BODY._missing_ledger_fields(probe, classification, carrier=carrier)
    ]

    assert "Consolidated disposition (consolidated)" in shape
    assert f"Do not use draft carriers {', '.join(refused)}" in shape
    assert f"--reason {desc._CONSOLIDATED.REQUIRED_CLOSE_REASON!r}" in shape
    for fact in desc._CONSOLIDATED.evaluate("Jtbd: move the work\nConsolidated into: #6\n")[
        "not_checked_here"
    ]:
        assert fact in shape
    assert "claim Implementation, Prevention, Resolution brief" in shape
    assert "before comment/close mutation" in shape
    assert "neutral `Closes #N` is non-operative" in shape
    assert any(
        "auto-closes" in problem
        for problem in desc._BODY._missing_ledger_fields(
            probe, classification, carrier="direct-commit"
        )
    )
    assert "Carrier (--carrier" not in shape
    assert "Close keyword (not required" not in shape


def test_closeout_draft_shape_can_render_the_selected_consolidated_guide(capsys) -> None:
    desc = _load_describe(
        "skills/public/issue/scripts/describe_closeout_draft_shape.py", "dccs_consolidated_cli"
    )
    assert desc.main(["--classification", "consolidated"]) == 0
    shape = capsys.readouterr().out
    assert "required shape for classification `consolidated`" in shape
    assert "Carrier (--carrier" not in shape


def test_closeout_draft_stub_body_satisfies_the_real_validator_helpers() -> None:
    # round-trip drift guard: a body built from the SURFACED headers passes the
    # validator's own ledger/keyword helpers for every classification, proving the
    # surfaced fields ARE the enforced ones (not a drifted copy).
    desc = _load_describe("skills/public/issue/scripts/describe_closeout_draft_shape.py", "dccs2")
    body = desc._BODY
    for classification in desc._VERIFY.CLASSIFICATIONS:
        lines = ["Closes #5"]
        for field_id, aliases in body._classification_requirements(classification):
            # Field-shaped stubs: `siblings` owes a decision/proof pair and
            # `consolidated_into` owes an issue ANCHOR, not arbitrary prose.
            value = {
                "siblings": "a decision and proof",
                "consolidated_into": "#600",
            }.get(field_id, "x")
            lines.append(f"{aliases[0].title()}: {value}")
        text = "\n".join(lines)
        assert body._missing_ledger_fields(text, classification) == [], classification
        assert body._missing_close_keywords(text, [5], "o/r") == [], classification


def test_closeout_draft_emit_stub_renders_a_starter_body() -> None:
    text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("closeout-draft"))
    assert code == 0
    assert "Closes #N" in text
    assert "Behavior #N:" in text
    assert "Critique #N:" not in text
    template = (
        ROOT / "skills" / "public" / "issue" / "scripts" / "templates" / "closeout_draft_stub.txt"
    )
    assert template.read_text(encoding="utf-8") == text


def test_run_shape_command_reports_render_failure() -> None:
    bad = replace(
        preflight.surface_for_type("closeout-draft"),
        shape_command=("scripts/does_not_exist_shape.py",),
    )
    text, code = preflight._run_shape_command(ROOT, bad, stub=False)
    assert code == 1
    assert "could not render shape source" in text


def test_emit_stub_no_source_arm() -> None:
    # a (hypothetical) surface with no scaffold/template/shape_command reports the
    # no-stub-source arm rather than crashing — cover the defensive branch.
    bare = replace(
        preflight.surface_for_type("closeout-draft"),
        scaffold=None,
        template_section=None,
        shape_command=None,
    )
    text, code = preflight.emit_stub(ROOT, bare)
    assert code == 0
    assert "no stub source registered" in text


@pytest.mark.parametrize(
    "rel",
    [
        "skills/public/issue/scripts/describe_closeout_draft_shape.py",
    ],
)
def test_describe_script_main_renders_shape_and_stub(rel: str, capsys) -> None:
    desc = _load_describe(rel, f"main_{Path(rel).stem}")
    assert desc.main([]) == 0
    shape_out = capsys.readouterr().out
    assert desc.main(["--stub"]) == 0
    stub_out = capsys.readouterr().out
    assert shape_out.strip() and stub_out.strip()
    assert shape_out != stub_out  # shape and stub are distinct surfaces


@pytest.mark.parametrize(
    "rel",
    [
        "skills/public/issue/scripts/describe_closeout_draft_shape.py",
    ],
)
def test_describe_script_main_guard_executes(rel: str, monkeypatch) -> None:
    # cover `raise SystemExit(main())` (the __main__ guard) in-process via runpy.
    monkeypatch.setattr(sys, "argv", ["x"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(ROOT / rel), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.parametrize(
    "rel,loader,sibling",
    [
        (
            "skills/public/issue/scripts/describe_closeout_draft_shape.py",
            "_load_local",
            "issue_verify_closeout_body",
        ),
    ],
)
def test_describe_sibling_loader_fails_closed_when_spec_missing(
    rel, loader, sibling, monkeypatch
) -> None:
    # fail-closed: the sibling loader raises ImportError when the spec cannot be
    # built (mirrors the repo's established loader-coverage pattern).
    desc = _load_describe(rel, f"loaderfail_{Path(rel).stem}")
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    with pytest.raises(ImportError):
        getattr(desc, loader)(sibling)


def test_every_shape_producer_is_reachable_from_its_owning_skill() -> None:
    """A registered producer is not a discoverable producer.

    #456's producer was registered here, and pinned by a test, and STILL cost the
    reporter 13 tool calls — because registration is not reachability. An agent
    discovers a shape through the surfaces it actually runs: the skill body, the
    planner payload, or a reference the planner routes it to. If the producer is
    named in none of those, the only remaining path is failing the validator and
    reading its source, which is the recurrence class this pins shut.

    Registry-only naming would pass a check over REGISTRY itself, so this asserts
    the other direction: the producer's basename must appear somewhere inside its
    owning skill package.
    """
    for surface in preflight.REGISTRY:
        if not surface.shape_command:
            continue
        producer = Path(surface.shape_command[0])
        skill_dir = ROOT / producer.parent.parent  # skills/public/<skill>/
        assert skill_dir.is_dir(), (
            f"{surface.artifact_type}: cannot locate owning skill for {producer}"
        )
        reachable = [
            path
            for path in skill_dir.rglob("*")
            if path.is_file()
            and path.suffix in {".md", ".py"}
            and path.name != producer.name
            and producer.name in path.read_text(encoding="utf-8", errors="ignore")
        ]
        assert reachable, (
            f"{surface.artifact_type}: `{producer.name}` is registered but named nowhere in "
            f"{skill_dir.relative_to(ROOT)} — an agent can only reach it by failing the validator. "
            "Name it in the planner payload, the SKILL body, or a reference the planner routes to."
        )


def test_adapter_scoped_surfaces_judge_the_authors_file_not_the_pointer_target() -> None:
    """The verdict named a surface and judged a DIFFERENT file.

    `quality` validates all by default, so without an explicit artifact path it can
    print a PASS about whatever `latest.md` points at while the author holds a dated
    draft. The whole point of an author-time preflight is a verdict about the thing
    being authored.
    """
    surface = preflight.surface_for_type("quality")
    assert surface.paths_arg is False
    assert surface.artifact_path_arg is True

    target = "charness-artifacts/quality/2026-07-25-quality-review.md"
    out = preflight.describe(ROOT, preflight.surface_for_type("quality"), target_rel=target)

    # the command shown, and the scope of the verdict, both name the author's file
    assert f"--artifact-path {target}" in out
    assert f"current verdict on {target}:" in out
    assert "(validate-all)" not in out


def test_a_prefix_surface_without_the_arg_still_reports_validate_all_scope() -> None:
    """Falsifiable counterpart: the honest `validate-all` wording must survive for any
    surface whose validator cannot be pointed at one file, or the fix would trade a
    misleading PASS for a misleading scope claim."""
    surface = replace(preflight.surface_for_type("quality"), artifact_path_arg=False)
    out = preflight.describe(
        ROOT, surface, target_rel="charness-artifacts/quality/2026-07-25-quality-review.md"
    )
    assert "(validate-all)" in out
    assert "--artifact-path" not in out


def test_closeout_draft_shape_renders_the_floors_its_validator_blocks_on() -> None:
    """A shape producer that omits a rule its own validator hard-blocks on hands the
    author a document built to fail. These three were absent while
    `evaluate_behavioral_verdict` / `evaluate_ai_provenance` / the HOTL lead pattern
    refused on them."""
    out = preflight.describe(ROOT, preflight.surface_for_type("closeout-draft"), target_rel=None)

    assert "Behavior #N:" in out and "AI-provenance:" in out
    # Rendered FROM the verifier's live constants, not restated beside them.
    assert "bug, feature, deferred-work" in out
    assert "resolution_critique (required for classifications: bug)" in out
    # The HOTL vocabulary is expanded from the anchored pattern and checked back
    # against it, so a status the verifier would refuse cannot be advertised here.
    for status in ("blocked-needs-operator", "blocked-needs-capability", "local-only-by-contract"):
        assert status in out
    assert "(?:" not in out, "the regex group leaked into operator-facing text"
