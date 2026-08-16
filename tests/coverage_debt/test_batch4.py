"""Behavior pins for command-surface edges that changed without a test reading them.

Every test here names a behavior an operator depends on: a refusal that must stay
loud, a payload that must stay machine-readable on stdout, or an exit code that
must keep meaning what the caller reads it as. The shared property across the
file is that these surfaces are all *reporting* surfaces -- a silent regression
in one of them does not crash, it produces a plausible-looking answer, which is
the failure mode this repo treats as worse than a crash.
"""

from __future__ import annotations

import json
import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]

LINT_RELEASE_NARRATIVE_PATH = ROOT / "skills/public/release/scripts/lint_release_narrative.py"
CHUNKED_ROUTING_CLI_PATH = ROOT / "skills/public/handoff/scripts/chunked_routing_cli.py"

LINT = load_script_module("batch4_lint_release_narrative", LINT_RELEASE_NARRATIVE_PATH)
DRIFT = load_script_module("batch4_check_upstream_support_drift", ROOT / "scripts/check_upstream_support_drift.py")
ROUTING_CLI = load_script_module("batch4_chunked_routing_cli", CHUNKED_ROUTING_CLI_PATH)
CLASSIFY_PUSH_DIFF = load_script_module("batch4_classify_push_diff", ROOT / "scripts/classify_push_diff.py")
GATHER = load_script_module("batch4_gather_public_url", ROOT / "skills/public/gather/scripts/gather_public_url.py")
PRESCRIBED = load_script_module("batch4_check_prescribed_skill_executed", ROOT / "scripts/check_prescribed_skill_executed.py")
PREPUSH = load_script_module("batch4_prepush_focused", ROOT / "scripts/prepush_focused_changed_line_coverage.py")
WORKTREE_AUDIT = load_script_module("batch4_worktree_audit", ROOT / "scripts/worktree_audit.py")
BOOTSTRAP_RUNTIME = load_script_module("batch4_bootstrap_runtime", ROOT / "scripts/bootstrap_runtime.py")
QUALITY_HANDOFF = load_script_module("batch4_inventory_quality_handoff", ROOT / "scripts/inventory_quality_handoff.py")
UPDATE_TOOLS = load_script_module("batch4_update_tools", ROOT / "scripts/update_tools.py")
BOOTSTRAP_PREVIEW = load_script_module(
    "batch4_bootstrap_markdown_preview", ROOT / "skills/public/quality/scripts/bootstrap_markdown_preview.py"
)
RENDER_PREVIEW = load_script_module(
    "batch4_render_markdown_preview", ROOT / "skills/support/markdown-preview/scripts/render_markdown_preview.py"
)


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _seed_git_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git("init", "--initial-branch=main", cwd=path)
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    _git("add", "README.md", cwd=path)
    _git("commit", "-m", "seed", cwd=path)
    return path


def _load_copy_of(script: Path, tmp_path: Path, module_name: str):
    """Load a byte-identical copy of ``script`` from a directory with no repo above it.

    This is how the "installed somewhere the helper is missing" layout is
    reproduced without editing the real tree: the scripts locate their helpers by
    walking ancestors, so the ancestor chain IS the input under test.
    """
    destination = tmp_path / script.name
    shutil.copy2(script, destination)
    return load_script_module(module_name, destination)


# --------------------------------------------------------------------------- #
# skills/public/release/scripts/lint_release_narrative.py
# --------------------------------------------------------------------------- #


def test_release_lint_refuses_to_load_without_its_runtime_bootstrap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A layout that ships the linter without `skill_runtime_bootstrap.py` must fail
    loudly, naming the missing file. The alternative -- a partially initialized module
    whose `REPO_ROOT` and `emit_yaml` are absent -- surfaces later as an AttributeError
    inside a release gate, where the reader has no way to tell that the export, not the
    note, is what is broken.

    Asserted twice on purpose: once through a real import of a copy stranded outside
    the repo (proving the failure happens at import, before anything can use the
    module), and once by pointing the shipped module's own anchor at that same
    directory (proving THIS file's resolver, not the copy's, is what refuses)."""
    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        _load_copy_of(LINT_RELEASE_NARRATIVE_PATH, tmp_path, "batch4_lint_release_narrative_stranded")

    monkeypatch.setattr(LINT, "__file__", str(tmp_path / "lint_release_narrative.py"))
    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        LINT._load_skill_runtime_bootstrap()


def test_release_lint_ignores_a_bare_v_version_exemption() -> None:
    """A caller that passes `v` (or an empty string) as a release version must not
    buy a blanket exemption. Each version becomes a regex that MASKS matching text
    before the rule runs, and `v` strips to an empty version whose pattern would be
    `v?` -- a zero-width match that is not a version at all. Dropping it keeps the
    exemption list to versions someone actually named."""
    assert LINT._version_patterns(("v",)) == []
    assert LINT._version_patterns(("",)) == []
    assert [pattern.pattern for pattern in LINT._version_patterns(("v1.2.3",))] == [r"v?1\.2\.3"]

    kinds = [finding["kind"] for finding in LINT.lint_text("We fixed twelve bugs.\n", versions=("v",))]
    assert "bare-quantity" in kinds


def test_release_lint_reports_an_unclosed_fence_and_stops_trusting_its_masking() -> None:
    """A fence left open at end of file exempts everything below it from the rule.
    So the linter reports the fence AND stops masking, surfacing the claims that the
    broken fence had hidden. The closed-fence control is what makes this a real
    signal: the same prose inside a properly closed fence is code, and stays exempt."""
    unclosed = "```\nWe fixed twelve bugs.\n"
    closed = "```\nWe fixed twelve bugs.\n```\n"

    spans, mispaired = LINT._fence_spans(unclosed)
    assert spans == []
    assert mispaired == 1

    assert [finding["kind"] for finding in LINT.lint_text(unclosed)] == [
        "unbalanced-code-fence",
        "bare-quantity",
    ]
    assert LINT.lint_text(closed) == []


def test_release_lint_run_as_a_script_exits_nonzero_with_a_yaml_finding_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The release gate consumes this as a command: a blocking finding has to reach
    the caller as a nonzero exit AND as a structured report on stdout. Driven through
    the `__main__` entrypoint because that is the surface the gate invokes -- calling
    `main()` directly would not prove the script exits with the code it returns."""
    notes = tmp_path / "notes.md"
    notes.write_text("We fixed twelve bugs and every gate is green.\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["lint_release_narrative.py", "--notes-file", str(notes)])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(LINT_RELEASE_NARRATIVE_PATH), run_name="__main__")

    assert excinfo.value.code == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["notes_file"] == str(notes)
    assert payload["status"] == "contained-claim-required"
    assert payload["blocking_count"] == 1
    # The advisory is reported but does NOT drive the exit code; a rule an author
    # cannot get to zero is one they learn to ignore.
    assert payload["advisory_count"] == 1
    assert payload["finding_count"] == 2
    assert [finding["token"] for finding in payload["findings"]] == ["twelve", "every"]


def test_release_lint_reports_clean_and_exits_zero_for_a_grounded_note(tmp_path: Path) -> None:
    """The discriminating control for the test above: a note with no ungrounded
    quantity reports `clean` and exits 0, and a version the caller declared is
    exempt. Without this, a linter that blocked unconditionally would pass."""
    notes = tmp_path / "notes.md"
    notes.write_text("Rolled back to v1.2.3 after the gate refused.\n", encoding="utf-8")

    result = run_loaded_script_main(
        "lint_release_narrative.py", LINT, "--notes-file", str(notes), "--version", "1.2.3"
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "clean"
    assert payload["blocking_count"] == 0
    assert payload["findings"] == []


# --------------------------------------------------------------------------- #
# scripts/check_upstream_support_drift.py
# --------------------------------------------------------------------------- #


def _seed_drift_manifest(repo_root: Path, *, ref: str, path: str) -> None:
    tools = repo_root / "integrations" / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1",
        "tool_id": "demo",
        "upstream_repo": "demo/upstream",
        "support_skill_source": {"source_type": "upstream_repo", "path": path, "ref": ref},
    }
    (tools / "demo.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def test_drift_record_label_names_a_probe_block_as_skipped_not_drift() -> None:
    """`status: error` means the probe could not run (no token, no network), which is
    NOT drift -- and a raw `error` in the payload reads as the failure it is not. The
    label carries the operator-facing word, and it carries the reason with it so
    `skipped` never hides which block occurred."""
    assert DRIFT.record_label({"status": "exists"}) == "ok"
    assert DRIFT.record_label({"status": "missing"}) == "DRIFT"
    assert DRIFT.record_label({"status": "error", "reason": "github-forbidden"}) == "skipped (github-forbidden)"
    assert DRIFT.record_label({"status": "error"}) == "skipped (unknown)"
    # An unmodelled status passes through rather than being laundered into a word.
    assert DRIFT.record_label({"status": "surprising"}) == "surprising"


def test_drift_main_emits_labelled_records_and_counts_only_missing_as_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The payload is what a CI nightly reads: every probed record carries its label,
    and `drift_count` counts ONLY `missing`. A probe-blocked target inflating that
    count would turn every tokenless CI run into a false drift alarm."""
    _seed_drift_manifest(tmp_path, ref="v0.15.0", path="skills/cautilus-agent")
    fixtures = tmp_path / "fixtures.json"
    fixtures.write_text(
        json.dumps({"demo/upstream:v0.15.0:skills/cautilus-agent": "error:github-forbidden"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("CHARNESS_UPSTREAM_SUPPORT_PROBE_FIXTURES", str(fixtures))
    monkeypatch.setenv("CHARNESS_UPSTREAM_SUPPORT_PROBE_NO_GH", "1")

    result = run_loaded_script_main(
        "check_upstream_support_drift.py", DRIFT, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["schema_version"] == 1
    assert payload["target_count"] == 1
    assert payload["drift_count"] == 0
    record = payload["checked"][0]
    assert record["tool_id"] == "demo"
    assert record["manifest_path"] == "integrations/tools/demo.json"
    assert record["label"] == "skipped (github-forbidden)"


def test_drift_main_fails_when_a_pinned_support_path_is_gone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The corca-ai/cautilus#32 prevention itself: a `ref` bump to a release where the
    declared path no longer exists must exit nonzero with a DRIFT label, not report a
    green sync. This is the arm the `skipped` test above must not be able to satisfy."""
    _seed_drift_manifest(tmp_path, ref="v0.15.0", path="skills/cautilus-agent")
    fixtures = tmp_path / "fixtures.json"
    fixtures.write_text(
        json.dumps({"demo/upstream:v0.15.0:skills/cautilus-agent": "missing"}), encoding="utf-8"
    )
    monkeypatch.setenv("CHARNESS_UPSTREAM_SUPPORT_PROBE_FIXTURES", str(fixtures))
    monkeypatch.setenv("CHARNESS_UPSTREAM_SUPPORT_PROBE_NO_GH", "1")

    result = run_loaded_script_main(
        "check_upstream_support_drift.py", DRIFT, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["drift_count"] == 1
    assert payload["checked"][0]["label"] == "DRIFT"


# --------------------------------------------------------------------------- #
# skills/public/handoff/scripts/chunked_routing_cli.py
# --------------------------------------------------------------------------- #


def _read_payload(module, raw: str, tmp_path: Path, name: str = "stage-input.yaml"):
    source = tmp_path / name
    source.write_text(raw, encoding="utf-8")
    return module.read_pipeline_json(str(source), stage="prepare_ranker_packet", expects="a chunk packet")


def _refusal_from(excinfo, capsys) -> dict:
    assert excinfo.value.code == 2
    return yaml.safe_load(capsys.readouterr().err)


def test_routing_cli_refuses_to_load_without_the_repo_yaml_emitter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every pipeline stage loads this module as a plain sibling, so a layout that
    does not ship `scripts/yaml_output.py` has to fail at import naming that file.
    Otherwise the first stage to refuse would itself die rendering its refusal.

    Asserted both through a real import of a copy stranded outside the repo and by
    pointing the shipped module's own anchor at that directory, so the refusal is
    pinned on THIS file's ancestor walk rather than on the copy's."""
    with pytest.raises(ImportError, match="scripts/yaml_output.py not found"):
        _load_copy_of(CHUNKED_ROUTING_CLI_PATH, tmp_path, "batch4_chunked_routing_cli_stranded")

    monkeypatch.setattr(ROUTING_CLI, "__file__", str(tmp_path / "chunked_routing_cli.py"))
    with pytest.raises(ImportError, match="scripts/yaml_output.py not found"):
        ROUTING_CLI._load_yaml_output()


def test_routing_cli_names_the_interpreter_when_pyyaml_cannot_read_the_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Non-JSON input falls back to YAML, so on an interpreter without PyYAML the
    stage must say WHICH interpreter is missing it and why JSON was rejected. A bare
    `ModuleNotFoundError` traceback here sends the reader looking for a bad payload
    when the real defect is the interpreter running the pipeline."""
    monkeypatch.setitem(sys.modules, "yaml", None)

    with pytest.raises(SystemExit) as excinfo:
        _read_payload(ROUTING_CLI, "entries:\n  - id: a\n", tmp_path)

    payload = _refusal_from(excinfo, capsys)
    assert payload["ok"] is False
    assert payload["stage"] == "prepare_ranker_packet"
    assert payload["expects"] == "a chunk packet"
    assert "PyYAML is not importable" in payload["error"]
    assert sys.executable in payload["error"]


def test_routing_cli_refuses_argparse_usage_text_before_yaml_can_launder_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`usage: prog [-h]` followed by `prog: error: ...` is a valid YAML mapping, so
    the YAML fallback would otherwise turn a wrong upstream `--flag` into a readable
    payload and a plausible EMPTY result. The guard reads the raw text, so the
    refusal fires at the stage that read it and names the upstream invocation."""
    usage = "usage: prepare_ranker_packet.py [-h] [--input INPUT]\nprepare_ranker_packet.py: error: unrecognized arguments: --nope\n"

    with pytest.raises(SystemExit) as excinfo:
        _read_payload(ROUTING_CLI, usage, tmp_path)

    payload = _refusal_from(excinfo, capsys)
    assert payload["error"] == "input is argparse usage text, not a stage payload"
    assert "check the previous stage's invocation" in payload["hint"]


@pytest.mark.parametrize(
    ("raw", "expected_error"),
    [
        ("", "input is empty"),
        ("just a stray line\n", "input parsed as a bare str, not a payload"),
    ],
)
def test_routing_cli_refuses_a_non_payload_structurally(
    raw: str, expected_error: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Empty stdout is the normal shape when an upstream stage exits nonzero and
    writes nothing, and a stray line parses to a scalar. Both used to reach
    `payload.get(...)` and die with an AttributeError traceback -- the opposite of
    the named-stage refusal this module promises. The check is structural, not a
    prefix denylist, so it also covers contaminants nobody has met yet."""
    with pytest.raises(SystemExit) as excinfo:
        _read_payload(ROUTING_CLI, raw, tmp_path)

    payload = _refusal_from(excinfo, capsys)
    assert payload["error"] == expected_error
    assert "check its" in payload["hint"]


def test_routing_cli_refuses_an_upstream_stage_refusal_forwarded_as_input(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A refusal payload parses perfectly and carries none of the fields the next
    stage reads, so redirecting a failing stage's stderr onward would produce a
    plausible empty result instead of an error. The refusal names the upstream stage
    that actually failed."""
    refusal = yaml.safe_dump({"ok": False, "stage": "propose_merges", "error": "input file not found"})

    with pytest.raises(SystemExit) as excinfo:
        _read_payload(ROUTING_CLI, refusal, tmp_path)

    payload = _refusal_from(excinfo, capsys)
    assert payload["error"] == "input is a refusal payload from stage `propose_merges`, not a stage payload"
    assert "Fix the upstream failure" in payload["hint"]


def test_routing_cli_accepts_a_real_stage_payload(tmp_path: Path) -> None:
    """The discriminating control: the refusals above narrowed the accepted input,
    they did not close it. A genuine YAML mapping still parses through unchanged."""
    assert _read_payload(ROUTING_CLI, "entries:\n  - id: a\n", tmp_path) == {"entries": [{"id": "a"}]}


# --------------------------------------------------------------------------- #
# scripts/classify_push_diff.py
# --------------------------------------------------------------------------- #


def test_classify_push_diff_forces_a_full_gate_when_there_is_no_upstream(tmp_path: Path) -> None:
    """A branch with no tracking branch gives no diff range, and an unknown range
    must fail SAFE: the pre-push hook reads this to decide whether to skip the broad
    quality gate, so `no range` has to mean `full gate`, never `nothing changed`."""
    repo = _seed_git_repo(tmp_path / "repo")

    result = run_loaded_script_main(
        "classify_push_diff.py", CLASSIFY_PUSH_DIFF, "--repo-root", str(repo)
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["classification"] == "full-gate-required"
    assert payload["files"] == []
    assert "no upstream tracking branch" in payload["reason"]


def test_classify_push_diff_forces_a_full_gate_and_exits_2_when_git_fails(tmp_path: Path) -> None:
    """An unresolvable diff range is an ERROR, not a classification: the payload
    still says `full-gate-required` so a caller that only reads stdout fails safe,
    and exit 2 lets a caller that reads the code tell the error apart from a
    successful full-gate verdict."""
    repo = _seed_git_repo(tmp_path / "repo")

    result = run_loaded_script_main(
        "classify_push_diff.py",
        CLASSIFY_PUSH_DIFF,
        "--repo-root",
        str(repo),
        "--diff-range",
        "no-such-ref..HEAD",
    )

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert payload["classification"] == "full-gate-required"
    assert payload["files"] == []
    assert payload["reason"].startswith("git diff failed; full gate forced:")


def test_classify_push_diff_echoes_the_range_it_actually_judged(tmp_path: Path) -> None:
    """The classification is only auditable if the payload says which range produced
    it -- otherwise a `docs-artifact-only` verdict computed over the wrong range is
    indistinguishable from a correct one. A docs-only commit is also the arm that
    proves the skip verdict still exists."""
    repo = _seed_git_repo(tmp_path / "repo")
    (repo / "docs").mkdir()
    (repo / "docs" / "note.md").write_text("note\n", encoding="utf-8")
    _git("add", "docs/note.md", cwd=repo)
    _git("commit", "-m", "docs", cwd=repo)

    result = run_loaded_script_main(
        "classify_push_diff.py",
        CLASSIFY_PUSH_DIFF,
        "--repo-root",
        str(repo),
        "--diff-range",
        "HEAD~1..HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["diff_range"] == "HEAD~1..HEAD"
    assert payload["files"] == ["docs/note.md"]
    assert payload["classification"] == "docs-artifact-only"


# --------------------------------------------------------------------------- #
# skills/public/gather/scripts/gather_public_url.py
# --------------------------------------------------------------------------- #


def _stdout_script(tmp_path: Path, body: str) -> list[str]:
    script = tmp_path / "fake_stage.py"
    script.write_text(f"import sys\nsys.stdout.write({body!r})\n", encoding="utf-8")
    return [sys.executable, str(script)]


def test_gather_refuses_a_helper_whose_stdout_is_not_parseable(tmp_path: Path) -> None:
    """A helper that exits 0 but writes unparseable stdout must become a refusal that
    names the command. Gather chains helper commands, so an unreadable payload passed
    onward would fail several steps later against a record that was never built."""
    command = _stdout_script(tmp_path, "{[not: yaml\n")

    with pytest.raises(SystemExit) as excinfo:
        GATHER._run_json(command)

    assert "did not emit a readable payload" in str(excinfo.value)
    assert "fake_stage.py" in str(excinfo.value)


def test_gather_refuses_a_helper_whose_stdout_is_a_bare_scalar(tmp_path: Path) -> None:
    """`yaml.safe_load` returns a scalar where `json.loads` raised, so a helper that
    prints a log line instead of a payload parses successfully into a string. Without
    the mapping check that string reaches `payload[...]` and dies as an AttributeError
    far from its cause."""
    command = _stdout_script(tmp_path, "fetching...\n")

    with pytest.raises(SystemExit) as excinfo:
        GATHER._run_json(command)

    assert "did not emit a readable payload" in str(excinfo.value)


def test_gather_accepts_a_helper_that_emits_a_mapping(tmp_path: Path) -> None:
    """The discriminating control: a helper emitting a real mapping still returns it."""
    command = _stdout_script(tmp_path, "status: ok\nurl: https://example.com\n")

    assert GATHER._run_json(command) == {"status": "ok", "url": "https://example.com"}


# --------------------------------------------------------------------------- #
# scripts/check_prescribed_skill_executed.py
# --------------------------------------------------------------------------- #


def test_prescribed_gate_refuses_a_run_with_nothing_required() -> None:
    """A closeout gate invoked with no `--require` names would otherwise report `ok`
    while proving nothing -- the exact "green gate that checked nothing" shape the
    prescribed-skill contract exists to prevent. It exits 2, distinct from the exit 1
    a real missing-evidence failure uses."""
    result = run_loaded_script_main("check_prescribed_skill_executed.py", PRESCRIBED)

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["error"] == "no --require names supplied"


def test_prescribed_gate_refuses_a_malformed_evidence_argument(tmp_path: Path) -> None:
    """`--evidence` is `NAME:PATH`; a value missing the separator cannot be bound to a
    required name. Reporting the parse error as a structured refusal on stdout (exit
    2) keeps it distinguishable from an evidence-missing failure, so a caller cannot
    read a typo as a genuine closeout gap."""
    result = run_loaded_script_main(
        "check_prescribed_skill_executed.py",
        PRESCRIBED,
        "--repo-root",
        str(tmp_path),
        "--require",
        "critique",
        "--evidence",
        "no-separator-here",
    )

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["error"]


# --------------------------------------------------------------------------- #
# scripts/prepush_focused_changed_line_coverage.py
# --------------------------------------------------------------------------- #


def test_prepush_unparseable_consumer_stdout_is_a_no_verdict() -> None:
    """A consumer that exits 0 while writing stdout no YAML reader can parse has
    proven nothing, so its exit code must not be laundered into `clean`. The parse
    error is caught rather than raised because a crash here would take down the whole
    pre-push lane over a malformed report."""
    status, reason = PREPUSH._verdict_from_consumer(
        SimpleNamespace(returncode=0, stdout="{[unbalanced: yaml\n", stderr="")
    )

    assert status == "no-verdict"
    assert "stands for nothing" in reason


def test_prepush_a_readable_clean_report_is_still_clean() -> None:
    """The discriminating control: catching the parse error did not swallow real
    verdicts."""
    status, _ = PREPUSH._verdict_from_consumer(
        SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"ok": True, "blocking": [], "changed_pool_files": ["scripts/a.py"]}),
            stderr="",
        )
    )

    assert status == "clean"


# --------------------------------------------------------------------------- #
# scripts/worktree_audit.py
# --------------------------------------------------------------------------- #


def test_worktree_audit_prune_emits_a_second_yaml_document_behind_a_start_marker(
    tmp_path: Path,
) -> None:
    """A `--prune` run writes a SECOND payload to the same stdout. Two concatenated
    mappings are not one YAML document, so without the explicit `---` start marker the
    combined output is unreadable to every YAML consumer. Parsed with `safe_load_all`
    here because that is what a caller must do."""
    repo = _seed_git_repo(tmp_path / "repo")

    result = run_loaded_script_main(
        "worktree_audit.py", WORKTREE_AUDIT, "--repo-root", str(repo), "--prune"
    )

    assert result.returncode == 0, result.stderr
    documents = list(yaml.safe_load_all(result.stdout))
    assert len(documents) == 2
    audit, prune = documents
    assert audit["status"] == WORKTREE_AUDIT.PASS
    assert audit["summary"]["primary"] == 1
    assert prune["status"] == WORKTREE_AUDIT.PASS
    assert "remaining_after_prune" in prune


# --------------------------------------------------------------------------- #
# scripts/bootstrap_runtime.py
# --------------------------------------------------------------------------- #


def test_bootstrap_runtime_main_emits_the_runtime_payload_as_yaml(tmp_path: Path) -> None:
    """Install/update flows read this payload to find the runtime they must invoke,
    so the whole contract -- which interpreter, which site-packages, which
    requirements file -- has to reach stdout as a parseable mapping. `--print-python`
    is the human/pipe shorthand and must stay a strict projection of the same value."""
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    shutil.copy2(ROOT / "packaging" / "bootstrap-python.json", repo / "packaging" / "bootstrap-python.json")
    shutil.copy2(
        ROOT / "packaging" / "bootstrap-requirements.txt", repo / "packaging" / "bootstrap-requirements.txt"
    )

    result = run_loaded_script_main(
        "bootstrap_runtime.py",
        BOOTSTRAP_RUNTIME,
        "--repo-root",
        str(repo),
        "--base-python",
        sys.executable,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["repo_root"] == str(repo.resolve())
    assert payload["required_modules"] == ["jsonschema", "packaging", "yaml"]
    assert Path(payload["python"]).exists()
    assert payload["created"] is True

    printed = run_loaded_script_main(
        "bootstrap_runtime.py",
        BOOTSTRAP_RUNTIME,
        "--repo-root",
        str(repo),
        "--base-python",
        sys.executable,
        "--print-python",
    )
    assert printed.stdout.strip() == payload["python"]


# --------------------------------------------------------------------------- #
# scripts/inventory_quality_handoff.py
# --------------------------------------------------------------------------- #


def test_quality_handoff_inventory_main_emits_findings_as_yaml(tmp_path: Path) -> None:
    """The advisory is consumed as a payload, not as prose: the retired human line
    was a strict projection of the finding count and each finding's missing fields.
    An operator-supplied `--artifact` is labelled repo-relative so the report names
    the file the way the operator does."""
    artifact = tmp_path / "charness-artifacts" / "quality" / "latest.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-08-16",
                "",
                "## Recommended Next Quality Moves",
                "",
                "- passive `NON_AUTOMATABLE`: decide whether the review stays manual.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "inventory_quality_handoff.py",
        QUALITY_HANDOFF,
        "--repo-root",
        str(tmp_path),
        "--artifact",
        "charness-artifacts/quality/latest.md",
    )

    assert result.returncode == 0, result.stderr
    report = yaml.safe_load(result.stdout)
    assert report["schema_version"] == 1
    assert report["status"] == "advisory"
    assert report["artifact"] == "charness-artifacts/quality/latest.md"
    assert report["findings"][0]["type"] == "missing_hitl_handoff"
    assert "review_question" in report["findings"][0]["missing_fields"]


# --------------------------------------------------------------------------- #
# scripts/update_tools.py
# --------------------------------------------------------------------------- #


def test_update_tools_main_emits_an_empty_yaml_list_for_an_empty_inventory(tmp_path: Path) -> None:
    """A repo with no tool manifests must produce an empty RESULTS PAYLOAD and exit 0,
    not a crash and not silence. The update flow parses this stdout to decide what ran;
    an empty document there would be indistinguishable from a command that died before
    emitting anything."""
    result = run_loaded_script_main("update_tools.py", UPDATE_TOOLS, "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout) == []


# --------------------------------------------------------------------------- #
# skills/public/quality/scripts/bootstrap_markdown_preview.py
# --------------------------------------------------------------------------- #


def test_markdown_preview_bootstrap_dry_run_plans_without_writing_config(tmp_path: Path) -> None:
    """`--dry-run` is only useful if the plan reaches the caller as a payload AND
    nothing is written. Both halves are asserted, because a dry run that emitted a
    correct-looking plan while creating the config is the failure this flag exists to
    make impossible."""
    result = run_loaded_script_main(
        "bootstrap_markdown_preview.py",
        BOOTSTRAP_PREVIEW,
        "--repo-root",
        str(tmp_path),
        "--dry-run",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert isinstance(payload, dict)
    assert payload["config_path"] is None
    assert "execution" not in payload
    assert not (tmp_path / BOOTSTRAP_PREVIEW.DEFAULT_OUTPUT_PATH).exists()


def test_markdown_preview_bootstrap_reports_a_failed_preview_and_propagates_its_code(
    tmp_path: Path,
) -> None:
    """When `--execute` scaffolds successfully but the preview run fails, the payload
    must STILL reach stdout carrying the execution block, and the preview's returncode
    must become this command's exit code. Emitting nothing would leave the operator
    with a nonzero exit and no record of what was scaffolded; exiting 0 would report a
    preview that never rendered as a working one. The failure is real, not simulated:
    `--artifact-dir` names an existing FILE, so the renderer cannot create it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# hi\n", encoding="utf-8")
    (repo / "blocked").write_text("not a directory\n", encoding="utf-8")

    result = run_loaded_script_main(
        "bootstrap_markdown_preview.py",
        BOOTSTRAP_PREVIEW,
        "--repo-root",
        str(repo),
        "--artifact-dir",
        "blocked",
        "--execute",
    )

    assert result.returncode != 0
    payload = yaml.safe_load(result.stdout)
    assert payload["config_status"] == "written"
    assert payload["execution"]["status"] == "failed"
    assert payload["execution"]["returncode"] == result.returncode
    assert payload["execution"]["preview"] is None
    assert payload["execution"]["stderr"]


def test_markdown_preview_bootstrap_refuses_execute_with_dry_run(tmp_path: Path) -> None:
    """`--execute` and `--dry-run` are contradictory instructions; running either
    interpretation silently would either skip a requested preview or write during a
    run the operator asked to be a plan."""
    result = run_loaded_script_main(
        "bootstrap_markdown_preview.py",
        BOOTSTRAP_PREVIEW,
        "--repo-root",
        str(tmp_path),
        "--dry-run",
        "--execute",
    )

    assert result.returncode == 1
    assert "--execute cannot be combined with --dry-run" in result.stderr


# --------------------------------------------------------------------------- #
# skills/support/markdown-preview/scripts/render_markdown_preview.py
# --------------------------------------------------------------------------- #


def test_markdown_preview_render_reports_disabled_instead_of_rendering_nothing(
    tmp_path: Path,
) -> None:
    """A repo that turned markdown preview off must get an explicit `disabled` receipt
    with the config path that turned it off and exit 0. Rendering an empty target list
    instead would look identical to a preview that ran and found no files -- and the
    backend (`glow`) is not even required to be installed in the disabled case."""
    config = tmp_path / "markdown-preview.yaml"
    config.write_text("enabled: false\n", encoding="utf-8")

    result = run_loaded_script_main(
        "render_markdown_preview.py",
        RENDER_PREVIEW,
        "--repo-root",
        str(tmp_path),
        "--config",
        str(config),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "disabled"
    assert payload["repo"] == tmp_path.name
    assert payload["config_path"] == "markdown-preview.yaml"
    assert payload["warnings"] == ["Markdown preview is disabled by config."]
    # Nothing was rendered: no artifact directory, no manifest.
    assert not (tmp_path / "charness-artifacts").exists()
