"""Behavior pins for reporter/preflight surfaces whose attention states, refusal
arms, and degraded-environment fallbacks had no executed test.

Each test below names one operator-visible behavior: an attention state a
reporter must report rather than crash on, a refusal that must arrive as a
verdict instead of a traceback, or a scan that must survive one unreadable file
rather than abandon the rest of the tree. They are grouped by the module under
test; the module loaders at the top follow the loader each module's existing
suite already uses so a second copy does not end up on a different sys.path
entry from the one under test.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from runtime_bootstrap import import_repo_module
from scripts import check_skill_cut_safety as csafety
from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]

_ANCHOR = str(ROOT / "scripts" / "x.py")
EXPORT_LIB = import_repo_module(_ANCHOR, "scripts.export_self_sufficiency_lib")

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
ARTIFACT_PREFLIGHT = importlib.import_module("check_artifact_surface_preflight")
SKILL_PREFLIGHT = importlib.import_module("check_skill_surface_preflight")
MUTATION_PRODUCER = importlib.import_module("mutation_coverage_producer")

NARRATIVE_GATE = load_script_module(
    "publish_release_narrative_gate_batch6",
    ROOT / "skills/public/release/scripts/publish_release_narrative_gate.py",
)
NORMALIZER = load_script_module(
    "normalize_goal_closeout_batch6",
    ROOT / "skills/public/achieve/scripts/normalize_goal_closeout.py",
)
DISPOSITION_AUDIT = load_script_module(
    "audit_disposition_corpus_batch6",
    ROOT / "skills/public/achieve/scripts/audit_disposition_corpus.py",
)
BYPASS_VALIDATOR = load_script_module(
    "validate_boundary_bypass_payload_batch6",
    ROOT / "skills/public/quality/scripts/validate_boundary_bypass_payload.py",
)
CHATBOT_COMPARE = load_script_module(
    "eval_cautilus_chatbot_compare_batch6",
    ROOT / "scripts" / "eval_cautilus_chatbot_compare.py",
)

USAGE_EPISODES_SCRIPT = ROOT / "scripts" / "report_usage_episodes.py"
PRODUCT_REVIEW_SCRIPT = ROOT / "scripts" / "report_usage_product_review.py"
QUALITY_RESOLVER_SCRIPT = ROOT / "skills/public/quality/scripts/resolve_quality_artifact.py"
NORMALIZER_SCRIPT = ROOT / "skills/public/achieve/scripts/normalize_goal_closeout.py"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


# --- check_artifact_surface_preflight: structured-stdout parsing ----------------


def test_a_scripts_unparseable_stdout_is_read_as_unstructured_not_raised() -> None:
    """A delegated shape source that prints something which is not a document
    must fall through to its raw text, not abort the preflight.

    The preflight runs OTHER scripts and reads their stdout. If a malformed
    emission escaped as a parser exception, one broken scaffold would take down
    the preflight for every surface instead of degrading to raw text for one.
    """
    assert ARTIFACT_PREFLIGHT._parse_structured_stdout("status: ok\nvalue: 2\n") == {
        "status": "ok",
        "value": 2,
    }
    assert ARTIFACT_PREFLIGHT._parse_structured_stdout("key: [unterminated\n") is None


def test_without_pyyaml_the_preflight_still_reads_the_json_a_producer_emits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`yaml_output` falls back to compact JSON when PyYAML is absent, so the
    consumer has to be able to read JSON in exactly that environment.

    Pinning both halves matters: a reader that only understood YAML would leave
    every delegated shape source unreadable on a no-PyYAML host while still
    reporting a clean preflight over raw text.
    """
    monkeypatch.setitem(sys.modules, "yaml", None)

    assert ARTIFACT_PREFLIGHT._parse_structured_stdout('{"status": "ok"}') == {"status": "ok"}
    # Non-JSON in that same environment is unstructured, not an exception.
    assert ARTIFACT_PREFLIGHT._parse_structured_stdout("# a plain markdown heading") is None


# --- export_self_sufficiency_lib ------------------------------------------------


def _module_tree(source: str):
    import ast

    return ast.parse(source).body[0].value


def test_a_path_chain_rooted_in_a_string_literal_keeps_its_root_segment() -> None:
    """`"skills" / "public"` names `skills/public`, not `public`.

    The root of a chain is an ordinary literal segment; dropping it would make
    every finding report a path one level shallower than the source names, and
    the shipped-or-not verdict would then be rendered against the wrong path.
    """
    segments, complete = EXPORT_LIB._chain_segments(_module_tree('"skills" / "public" / "demo"'))

    assert segments == ["skills", "public", "demo"]
    assert complete is True


def test_a_path_naming_an_unshipped_repo_root_entry_is_reported(tmp_path: Path) -> None:
    """The defect this arm exists for: exported source referencing a repo-root
    directory the export does not ship."""
    export_root = tmp_path / "export"
    (export_root / "scripts").mkdir(parents=True)
    (export_root / "scripts" / "run.py").write_text(
        "from pathlib import Path\nP = Path('.') / 'packaging' / 'bootstrap.json'\n",
        encoding="utf-8",
    )

    findings = EXPORT_LIB.unshipped_path_findings(
        export_root, repo_root_entries={"packaging"}, relative_to=export_root
    )

    assert [(f["segment"], f["literal"]) for f in findings] == [("packaging", "packaging/bootstrap.json")]


def test_a_single_literal_spelling_a_subpath_is_reported_like_the_two_literal_one(
    tmp_path: Path,
) -> None:
    """Both spellings of the same absent target are reported. DECIDED, having been
    pinned as an open boundary by the previous version of this test.

    The guard used to count AST chain LINKS, so `'packaging/gone.json'` written as one
    literal was skipped while `'packaging' / 'gone.json'` was reported -- the verdict
    turned on how the path was typed rather than on what it names, and the one-link
    spelling is how the omission that opened this class was actually written. It now
    counts PATH segments, so the two spellings agree. What the depth rule still buys is
    below it: a depth-1 literal under a shipped root claims nothing about a file inside
    that root.
    """
    export_root = tmp_path / "export"
    (export_root / "packaging").mkdir(parents=True)
    (export_root / "packaging" / "shipped.json").write_text("{}\n", encoding="utf-8")
    (export_root / "one.py").write_text(
        "from pathlib import Path\nP = Path('.') / 'packaging/gone.json'\n", encoding="utf-8"
    )

    one_literal = EXPORT_LIB.unshipped_path_findings(
        export_root, repo_root_entries={"packaging"}, relative_to=export_root
    )
    assert [f["literal"] for f in one_literal] == ["packaging/gone.json"]

    (export_root / "one.py").write_text(
        "from pathlib import Path\nP = Path('.') / 'packaging' / 'gone.json'\n", encoding="utf-8"
    )
    two_literals = EXPORT_LIB.unshipped_path_findings(
        export_root, repo_root_entries={"packaging"}, relative_to=export_root
    )
    assert [f["literal"] for f in two_literals] == ["packaging/gone.json"]

    # The depth rule's remaining job: naming the shipped root itself is not a claim
    # about anything inside it, at either spelling.
    (export_root / "one.py").write_text(
        "from pathlib import Path\nP = Path('.') / 'packaging'\n", encoding="utf-8"
    )
    assert (
        EXPORT_LIB.unshipped_path_findings(
            export_root, repo_root_entries={"packaging"}, relative_to=export_root
        )
        == []
    )


def test_only_docs_and_adapters_declare_a_documented_entrypoint(tmp_path: Path) -> None:
    """A `$SKILL_DIR/scripts/x.py` string inside PYTHON source is not a consumer
    instruction.

    This arm answers "what is a consumer TOLD to run". Counting the same string
    in source would inflate the entrypoint set with internal references and put
    the dependency-guard arm to work on scripts nobody is told to invoke.
    """
    export_root = tmp_path / "export"
    (export_root / "skills").mkdir(parents=True)
    (export_root / "skills" / "SKILL.md").write_text(
        "Run `$SKILL_DIR/scripts/documented.py --repo-root .`\n", encoding="utf-8"
    )
    (export_root / "skills" / "internal.py").write_text(
        'COMMAND = "$SKILL_DIR/scripts/internal_only.py"\n', encoding="utf-8"
    )

    assert EXPORT_LIB.documented_entrypoint_names(export_root) == {"documented.py"}


def test_one_undecodable_doc_does_not_abandon_the_rest_of_the_scan(tmp_path: Path) -> None:
    """A single non-UTF-8 markdown file must not blind the entrypoint scan.

    An export can carry a stray binary blob with a doc suffix. Aborting there
    would report zero documented entrypoints for the whole export, and the
    dependency guard would then pass by measuring nothing.
    """
    export_root = tmp_path / "export"
    export_root.mkdir()
    (export_root / "binary.md").write_bytes(b"\xff\xfe not utf-8 $SKILL_DIR/scripts/hidden.py")
    (export_root / "good.md").write_text("`$SKILL_DIR/scripts/real.py`\n", encoding="utf-8")

    assert EXPORT_LIB.documented_entrypoint_names(export_root) == {"real.py"}


def test_one_unparseable_module_does_not_abandon_the_rest_of_the_tree(tmp_path: Path) -> None:
    """A Python file that will not parse is skipped; the other modules are still
    analyzed.

    Same property one layer down: a template or a py2 leftover in the export must
    not turn a self-sufficiency verdict into "no findings" for every other file.
    """
    export_root = tmp_path / "export"
    export_root.mkdir()
    (export_root / "broken.py").write_text("def (:\n", encoding="utf-8")
    (export_root / "good.py").write_text(
        "from pathlib import Path\nP = Path('.') / 'packaging' / 'x.json'\n", encoding="utf-8"
    )

    findings = EXPORT_LIB.unshipped_path_findings(
        export_root, repo_root_entries={"packaging"}, relative_to=export_root
    )

    assert [f["path"] for f in findings] == ["good.py"]


def test_blank_and_comment_only_requirement_lines_declare_nothing(tmp_path: Path) -> None:
    """Comments and blank lines are not declared distributions.

    The declared set is compared against the export's third-party imports; an
    empty string entering it would make an undeclared import look declared.
    """
    export_root = tmp_path / "export"
    export_root.mkdir()
    (export_root / "requirements.txt").write_text(
        "# a comment\n\n   \nPyYAML>=6.0\njsonschema  # trailing comment\n", encoding="utf-8"
    )

    assert EXPORT_LIB.declared_distributions(export_root) == {"pyyaml", "jsonschema"}


# --- report_usage_episodes / report_usage_product_review attention states -------


def _write_adapter(repo: Path, body: str) -> Path:
    target = repo / ".agents" / "usage-episodes-adapter.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def test_an_unreadable_usage_adapter_is_a_named_invalid_verdict_not_a_traceback(
    tmp_path: Path,
) -> None:
    """A malformed adapter must fail the report with `invalid_adapter` and the
    parser's own message.

    The reporter's exit-0 attention states are how an operator learns capture is
    off. An adapter that does not parse is a DIFFERENT state -- something is
    configured and broken -- so it must exit non-zero and say so, not be folded
    into "no records".
    """
    _write_adapter(tmp_path, "version: 1\nenabled: [unterminated\n")

    result = _run(USAGE_EPISODES_SCRIPT, "--repo-root", str(tmp_path))

    assert result.returncode == 1, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "invalid_adapter"
    assert payload["valid"] is False
    assert payload["errors"], "the parse failure must be reported, not swallowed"


def test_a_records_path_outside_the_repo_is_refused_by_both_usage_reporters(
    tmp_path: Path,
) -> None:
    """`--records-path` pointing outside the repo root is refused.

    The records path is operator-supplied and is read as repo-relative in every
    payload it appears in. Accepting an outside path would emit a report whose
    portable path is a lie and would read a file the repo does not own.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_adapter(repo, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    outside = tmp_path / "outside" / "usage_episode.jsonl"
    outside.parent.mkdir()
    outside.write_text("", encoding="utf-8")

    for script in (USAGE_EPISODES_SCRIPT, PRODUCT_REVIEW_SCRIPT):
        result = _run(script, "--repo-root", str(repo), "--records-path", str(outside))

        assert result.returncode == 1, f"{script.name}: {result.stdout}{result.stderr}"
        payload = yaml.safe_load(result.stdout)
        assert payload["status"] == "invalid_records_path"
        assert payload["errors"] == ["records_path must stay under repo_root"]


def test_the_product_review_reports_a_missing_adapter_as_an_exit_zero_state(
    tmp_path: Path,
) -> None:
    """No adapter is "capture was never opted into", not a failure.

    A non-zero exit here would make an unconfigured repo look broken to whatever
    runs the product review on a schedule.
    """
    result = _run(PRODUCT_REVIEW_SCRIPT, "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "no_adapter"
    assert payload["valid"] is True


def test_the_product_review_reports_a_disabled_adapter_as_an_exit_zero_state(
    tmp_path: Path,
) -> None:
    """A deliberately disabled adapter is an attention state, not an error.

    It has to stay distinguishable from `no_adapter`: one repo declined capture,
    the other never configured it, and the operator remedy differs.
    """
    _write_adapter(tmp_path, "version: 1\nenabled: false\n")

    result = _run(PRODUCT_REVIEW_SCRIPT, "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "disabled"
    assert payload["valid"] is True


def test_the_product_review_reports_an_enabled_adapter_with_no_records_yet(
    tmp_path: Path,
) -> None:
    """Enabled-but-empty is its own state, and it names where the file will land.

    Reporting this as an error would flag every repo between enabling capture and
    the first emitted episode.
    """
    _write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")

    result = _run(PRODUCT_REVIEW_SCRIPT, "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "no_records"
    assert payload["records_path"] == ".charness/usage-episodes/usage_episode.jsonl"


def test_the_product_review_reports_an_invalid_adapter_as_a_failure(tmp_path: Path) -> None:
    """A configured-but-unparseable adapter fails the product review loudly."""
    _write_adapter(tmp_path, "version: 1\nenabled: [unterminated\n")

    result = _run(PRODUCT_REVIEW_SCRIPT, "--repo-root", str(tmp_path))

    assert result.returncode == 1, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "invalid_adapter"
    assert payload["valid"] is False
    assert payload["non_claims"], "the review's non-claims must survive a failure payload"


def test_a_schema_invalid_episode_fails_the_review_and_counts_the_valid_rest(
    tmp_path: Path,
) -> None:
    """A record that does not match the episode schema fails the product review,
    and the payload still says how many records WERE valid.

    Without `valid_count` an operator cannot tell one malformed line from a
    wholly corrupt file, and the two have different remedies.
    """
    _write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    records = tmp_path / ".charness" / "usage-episodes"
    records.mkdir(parents=True)
    (records / "usage_episode.jsonl").write_text(
        json.dumps({"episode_id": "missing-everything-else"}) + "\n", encoding="utf-8"
    )

    result = _run(PRODUCT_REVIEW_SCRIPT, "--repo-root", str(tmp_path))

    assert result.returncode == 1, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "invalid_records"
    assert payload["valid"] is False
    assert payload["valid_count"] == 0
    assert payload["errors"], "the schema failure must name what was wrong"


def test_an_unparseable_review_window_is_its_own_exit_code(tmp_path: Path) -> None:
    """A bad `--window-start` exits 2 with `invalid_window`.

    A distinct code from the data failures (exit 1) is what lets a caller tell
    "you typed the window wrong" apart from "the recorded episodes are invalid";
    collapsing them would send an operator to inspect records over a typo.
    """
    _write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    records = tmp_path / ".charness" / "usage-episodes"
    records.mkdir(parents=True)
    (records / "usage_episode.jsonl").write_text("", encoding="utf-8")

    result = _run(PRODUCT_REVIEW_SCRIPT, "--repo-root", str(tmp_path), "--window-start", "not-a-time")

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "invalid_window"
    assert payload["records_path"] == ".charness/usage-episodes/usage_episode.jsonl"


# --- normalize_goal_closeout ----------------------------------------------------

_DIRTY_GOAL = (
    "Status: active\n\n"
    "## Operator Decision Queue\n\n"
    "Record decisions, confirmations, credential actions, manual proof steps.\n\n"
    "- Decision: operator-only decision or confirmation needed\n\n"
    "## Coordination Cues\n\n"
    "- Routing: quality — used the quality planner.\n\n"
    "## Final Verification\n\n"
    "Retro: `charness-artifacts/retro/2026-07-09-demo.md`\n"
    "Host log probe: `charness-artifacts/probe/2026-07-09-demo.json`\n"
    "Disposition review: `charness-artifacts/retro/2026-07-09-demo-disposition.md`\n\n"
    "## Auto-Retro\n\n"
    "Retro dispositions: `charness-artifacts/retro/2026-07-09-demo-disposition.md` PASS -- done\n"
)

_CLEAN_GOAL = (
    "Status: complete\n\n"
    "## Operator Decision Queue\n\n"
    "none — no operator-only decision remains for this completed local goal.\n\n"
    "## Auto-Retro\n\n"
    "Retro dispositions: applied: shipped the follow-up.\n"
)


def test_the_closeout_normalizer_defaults_to_a_dry_run_that_writes_nothing(
    tmp_path: Path,
) -> None:
    """Without `--write` the artifact on disk is untouched and the payload says
    `would change`.

    `changed: true, written: false` is a dry run, and an author who reads it as a
    completed write leaves the artifact unfixed -- so the verdict WORD has to be
    in the payload alongside the two booleans.
    """
    goal = tmp_path / "goal.md"
    goal.write_text(_DIRTY_GOAL, encoding="utf-8")

    result = _run(NORMALIZER_SCRIPT, "--goal-path", str(goal), "--complete")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "would change"
    assert payload["changed"] is True
    assert payload["written"] is False
    assert payload["fixes"], "a dry run must still name what it would fix"
    assert goal.read_text(encoding="utf-8") == _DIRTY_GOAL


def test_the_closeout_normalizer_writes_only_when_asked(tmp_path: Path) -> None:
    """`--write` applies the fixes and reports `wrote`."""
    goal = tmp_path / "goal.md"
    goal.write_text(_DIRTY_GOAL, encoding="utf-8")

    result = _run(NORMALIZER_SCRIPT, "--goal-path", str(goal), "--complete", "--write")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "wrote"
    assert payload["changed"] is True
    assert payload["written"] is True
    assert "Status: complete" in goal.read_text(encoding="utf-8")


def test_the_closeout_normalizer_reports_unchanged_for_a_clean_artifact(
    tmp_path: Path,
) -> None:
    """A clean artifact is `unchanged` with no fixes, even under `--write`.

    An affordance that reported a write it did not perform would train authors to
    ignore its verdict entirely.
    """
    goal = tmp_path / "goal.md"
    goal.write_text(_CLEAN_GOAL, encoding="utf-8")

    result = _run(NORMALIZER_SCRIPT, "--goal-path", str(goal), "--write")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "unchanged"
    assert payload["changed"] is False
    assert payload["written"] is False
    assert payload["fixes"] == []
    assert goal.read_text(encoding="utf-8") == _CLEAN_GOAL


def test_a_skill_script_without_its_runtime_bootstrap_says_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Installed outside any layout carrying `skill_runtime_bootstrap.py`, the
    loader raises a NAMED ImportError.

    The alternative is a `StopIteration` or an `AttributeError` on `None` several
    frames later, which tells an operator nothing about the missing file.
    """
    monkeypatch.setattr(NORMALIZER, "__file__", str(tmp_path / "scripts" / "normalize.py"))

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        NORMALIZER._load_skill_runtime_bootstrap()


def test_a_skill_script_without_the_repo_yaml_emitter_says_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same contract for the audit script's own ancestor walk to
    `scripts/yaml_output.py`, which it resolves without the bootstrap."""
    monkeypatch.setattr(DISPOSITION_AUDIT, "__file__", str(tmp_path / "scripts" / "audit.py"))

    with pytest.raises(ImportError, match="scripts/yaml_output.py not found"):
        DISPOSITION_AUDIT._load_yaml_output()


# --- eval_cautilus_chatbot_compare ---------------------------------------------


def test_a_proposal_summary_that_is_not_a_yaml_mapping_is_an_eval_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The compare eval reads a repo-owned CLI's stdout as YAML, and both
    non-YAML and non-mapping output are refused as `EvalError`.

    `EvalError` is the type the eval's own entrypoint turns into an operator
    message. A raw `yaml.YAMLError`, or an `AttributeError` from indexing a list
    as a mapping, would surface as a traceback and name the wrong cause.
    """

    def _fake_run(argv, **kwargs):
        return SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    monkeypatch.setattr(CHATBOT_COMPARE.subprocess, "run", _fake_run)

    stdout = "summary: [unterminated\n"
    with pytest.raises(CHATBOT_COMPARE.EvalError, match="did not emit valid YAML"):
        CHATBOT_COMPARE._run_proposal_summary(tmp_path / "repo", tmp_path / "out")

    stdout = "- one\n- two\n"
    with pytest.raises(CHATBOT_COMPARE.EvalError, match="must be a YAML mapping"):
        CHATBOT_COMPARE._run_proposal_summary(tmp_path / "repo", tmp_path / "out")


# --- publish_release_narrative_gate --------------------------------------------


def _release_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    return repo


def test_an_unreadable_release_adapter_does_not_disarm_the_derived_claim_rule(
    tmp_path: Path,
) -> None:
    """An adapter that does not parse is NOT a declared opt-out.

    Reading it as one would put the strength of a publish gate behind whether a
    YAML file happened to parse: a typo in the adapter would silently disarm the
    claim requirement at exactly the boundary that cannot be undone.
    """
    repo = _release_repo(tmp_path)
    # The opt-out line IS present, so a loader that read a rejected adapter's
    # data anyway would disarm the rule here.
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "version: 9\nrepo: demo\noutput_dir: charness-artifacts/release\n"
        "require_derived_release_claims: false\n",
        encoding="utf-8",
    )
    assert NARRATIVE_GATE.load_adapter(repo)["valid"] is False

    assert NARRATIVE_GATE.derived_claims_required(repo) is True


def test_a_tree_that_cannot_be_listed_is_an_unresolvable_finding_not_a_traceback(
    tmp_path: Path,
) -> None:
    """When the shipped tree cannot be measured, the gate REFUSES and says why.

    Nothing read the tree, so no claim in the notes was checked. Refusing is
    correct, but a `SystemExit` traceback where a verdict belongs hides the cause
    from the operator, and `RepoFileListingError` subclasses `SystemExit` so an
    `except Exception` guard would never have caught it.
    """
    repo = _release_repo(tmp_path)  # deliberately NOT a git repo
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/release\n", encoding="utf-8"
    )
    notes = repo / "charness-artifacts" / "release" / "notes.md"
    notes.write_text("# 0.1.0\n\nSome release prose.\n", encoding="utf-8")

    blockers = NARRATIVE_GATE.notes_claim_blockers(repo, notes)

    assert len(blockers) == 1
    assert blockers[0].startswith("[unresolvable] tree-listing-failed:")
    assert "nothing in these notes was checked" in blockers[0]


# --- check_skill_surface_preflight ---------------------------------------------


def test_the_skill_preflight_emits_a_structured_payload_for_a_real_surface() -> None:
    """The single-surface preflight reports headroom for a checked-in SKILL.md
    and exits 0 when nothing is blocked.

    This is the command an author runs BEFORE editing; if it stopped emitting a
    machine-readable payload, the commit-boundary ratchet would be the first
    thing to tell them the surface is out of room.
    """
    result = _run(
        ROOT / "scripts" / "check_skill_surface_preflight.py",
        "--path",
        "skills/public/quality/SKILL.md",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["label"] == "skill-surface-preflight"
    assert payload["status"] == "ok"
    assert payload["target"]["path"] == "skills/public/quality/SKILL.md"
    assert payload["headroom"]["skill_md_total"]["blocked"] is False
    assert "check_results" not in payload, "no checks were requested, so none may be reported"


def test_each_run_check_carries_a_pass_fail_reading_of_its_return_code() -> None:
    """With checks run, every row gets an explicit PASS/FAIL.

    A raw `returncode` was the only verdict after the human renderer was deleted.
    An author scanning six rows for a non-zero integer is how a failed targeted
    validator gets missed, which is the round-trip this preflight exists to end.
    """
    report = SKILL_PREFLIGHT.build_report(ROOT, "skills/public/quality/SKILL.md", 0, False)
    ok = subprocess.run([sys.executable, "-c", ""], capture_output=True, text=True)
    bad = subprocess.run([sys.executable, "-c", "raise SystemExit(3)"], capture_output=True, text=True)
    report["checks"] = [
        SKILL_PREFLIGHT._check_result("passing", ["python3", "-c", ""], ok),
        SKILL_PREFLIGHT._check_result("failing", ["python3", "-c", "raise SystemExit(3)"], bad),
    ]

    payload = SKILL_PREFLIGHT.preflight_payload(report)

    assert [(row["id"], row["status"]) for row in payload["check_results"]] == [
        ("passing", "PASS"),
        ("failing", "FAIL"),
    ]
    assert payload["check_results"][1]["returncode"] == 3


# --- check_skill_cut_safety -----------------------------------------------------


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_a_blocked_cut_carries_the_blocked_remedy(tmp_path: Path, monkeypatch) -> None:
    """A blocked cut-safety verdict names what to do about it, and names
    something different from the review-only remedy.

    The payload is the whole operator surface. A blocked status with no remedy
    leaves an author guessing whether to restore the line or argue with the pin,
    and the review remedy ("confirm each line") is the wrong instruction for a
    broken contract pin.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    skill_dir = repo / "skills" / "public" / "demo"
    (skill_dir / "references").mkdir(parents=True)
    pin = "Always prefer the primary source over a cached summary."
    (skill_dir / "SKILL.md").write_text(f"---\nname: demo\n---\n\n# Demo\n\n{pin}\n", encoding="utf-8")
    (repo / "tests").mkdir()
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base")
    monkeypatch.setattr(csafety._contracts, "CORE_CONTRACTS", {"skills/public/demo/SKILL.md": (pin,)})
    monkeypatch.setattr(csafety._contracts, "PACKAGE_CONTRACTS", {"skills/public/demo/SKILL.md": ()})
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n\nPrimary source is usually nicer.\n", encoding="utf-8"
    )

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    payload = csafety.report_payload(report)

    assert report["status"] == "blocked"
    assert payload["remedy"] == csafety._BLOCKED_REMEDY
    assert payload["remedy"].strip(), "a blocked verdict must not carry an empty remedy"
    assert payload["kind_meaning"], "the blocking kinds must be explained, not left as bare ids"


# --- mutation_coverage_producer -------------------------------------------------


def test_a_consumer_whose_stdout_is_not_a_mapping_yields_no_report() -> None:
    """The producer reads the consumer's structured verdict, and refuses to
    invent one when the stdout is not a mapping.

    The producer must not derive a second coverage policy from garbage. Returning
    `None` is what makes the caller fall back to the consumer's exit code instead
    of reading a verdict that was never emitted.
    """
    assert MUTATION_PRODUCER._consumer_report({"stdout": "status: ok\n"}) == {"status": "ok"}
    assert MUTATION_PRODUCER._consumer_report({"stdout": "status: [unterminated\n"}) is None
    assert MUTATION_PRODUCER._consumer_report({"stdout": "- a\n- b\n"}) is None
    assert MUTATION_PRODUCER._consumer_report({}) is None


# --- validate_boundary_bypass_payload -------------------------------------------

_BYPASS_EXAMPLE = ROOT / "skills/public/quality/references/boundary-bypass-payload.example.json"


def test_the_bypass_validator_reports_ok_with_the_derived_summary(tmp_path: Path) -> None:
    """A valid payload exits 0 and echoes the summary counts it verified.

    Echoing the counts is what makes the pass auditable: a bare `ok: true` proves
    the file parsed, not that the ratchet numbers were the ones checked.
    """
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(_BYPASS_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run(
        ROOT / "skills/public/quality/scripts/validate_boundary_bypass_payload.py",
        "--input",
        str(payload_path),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["summary"] == BYPASS_VALIDATOR.validate_payload(
        json.loads(_BYPASS_EXAMPLE.read_text(encoding="utf-8"))
    )


def test_the_bypass_validator_reports_the_failure_on_stdout_and_exits_one(
    tmp_path: Path,
) -> None:
    """A drifted summary count exits 1 with the offending field named in the
    structured payload.

    The ratchet consumer reads stdout. A refusal that exited non-zero with an
    empty payload would leave the caller unable to say WHICH count drifted.
    """
    payload = json.loads(_BYPASS_EXAMPLE.read_text(encoding="utf-8"))
    payload["summary"]["convertible_count"] = 99
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    result = _run(
        ROOT / "skills/public/quality/scripts/validate_boundary_bypass_payload.py",
        "--input",
        str(payload_path),
    )

    assert result.returncode == 1, result.stdout
    reported = yaml.safe_load(result.stdout)
    assert reported["ok"] is False
    assert "summary.convertible_count" in reported["error"]


# --- resolve_quality_artifact ---------------------------------------------------


def test_the_quality_resolver_reports_the_dated_record_and_the_pointer_refresh(
    tmp_path: Path,
) -> None:
    """A `record` resolution names the dated write target AND the command that
    must repoint `latest.md` afterwards.

    The resolver is the single owner of quality artifact paths. If it emitted the
    write path without the pointer-refresh command, every quality run would leave
    `latest.md` aimed at the previous record while reporting success.
    """
    result = _run(
        QUALITY_RESOLVER_SCRIPT,
        "--repo-root",
        str(tmp_path),
        "--intent",
        "record",
        "--slug",
        "Batch Six Review",
        "--date",
        "2026-04-15",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["skill_id"] == "quality"
    assert payload["slug"] == "batch-six-review"
    assert payload["record_artifact_path"] == "charness-artifacts/quality/2026-04-15-batch-six-review.md"
    assert payload["write_artifact_path"] == payload["record_artifact_path"]
    assert payload["write_artifact_role"] == "durable_record"
    assert payload["update_current_pointer_after_write"] is True
    assert "refresh_current_pointer.py" in payload["refresh_current_pointer_command"]
