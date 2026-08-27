"""Behaviour pins for repo commands whose failure and degradation arms shipped unproven.

Every test here names a behaviour an operator depends on and fails when that
behaviour breaks, not merely when a line stops executing:

* `what_reads_this.py` answers "what reads this?" and the whole point of the tool
  is that its GROUPING and its refusal to under- or over-report are trustworthy.
  The kinds it separates (definition vs attribute-access vs string-literal), the
  copies it must never count (`mutants/**`), the glob shapes it must understand
  (`**`, `?`), and its CLI contract are pinned here.
* The skill scripts' bootstrap loaders must refuse with a NAMED ImportError when
  they run from a tree that owns no charness runtime, instead of dying later on a
  `NameError` that reads as a charness bug.
* The scaffolds' refusal arms must refuse rather than overwrite.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest
import yaml

from scripts import scaffold_artifact_lib
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]

WRT_PATH = ROOT / "scripts" / "what_reads_this.py"
WRT = load_script_module("what_reads_this_batch1", WRT_PATH)
CLASSIFY_T_SIGNAL = load_script_module("classify_t_signal_batch1", ROOT / "scripts" / "classify_t_signal.py")
COLLECT_COMMITS = load_script_module(
    "collect_commits_batch1", ROOT / "skills/public/announcement/scripts/collect_commits.py"
)
MINE_CLOSEOUT = load_script_module(
    "mine_closeout_telemetry_batch1", ROOT / "skills/public/retro/scripts/mine_closeout_telemetry.py"
)
# --------------------------------------------------------------------------
# scripts/what_reads_this.py
# --------------------------------------------------------------------------

_CONSUMER = '''"""Builds a report and loads a numbered fixture family."""


def build_report(config):
    return config.report_limit + config["report_limit"]


def load_cases(root):
    return sorted(root.glob("evals/case-?.json"))


def load_skill_files(root):
    return sorted(root.glob("skills/**"))


def require(config):
    if "report_limit" not in config:
        raise KeyError("report_limit")
'''

_TEST_FILE = '''from consumer import build_report

CASE = "evals/case-1.json"


def test_build_report():
    assert build_report({"report_limit": 1})
'''


def _repo(tmp_path: Path) -> Path:
    """A miniature tree, not this repo.

    An assertion about charness's own consumer counts goes stale on unrelated
    commits, and re-recording the number is not a test.
    """
    repo = tmp_path / "repo"
    for relative in ("scripts", "tests", "evals", ".agents", "skills/public/demo/scripts"):
        (repo / relative).mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "consumer.py").write_text(_CONSUMER, encoding="utf-8")
    (repo / "tests" / "test_consumer.py").write_text(_TEST_FILE, encoding="utf-8")
    (repo / "evals" / "case-1.json").write_text("{}\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "scripts" / "run.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / ".agents" / "demo-adapter.yaml").write_text("version: 1\nreport_limit: 5\n", encoding="utf-8")
    return repo


def _hits(payload: dict[str, object], rel: str) -> list[dict[str, object]]:
    return [entry["hits"] for entry in payload["references"] if entry["file"] == rel][0]


def _kinds_in(payload: dict[str, object], rel: str) -> set[str]:
    return {str(hit["kind"]) for hit in _hits(payload, rel)}


def test_a_definition_and_a_test_consumer_are_separated_by_kind_and_surface(tmp_path: Path) -> None:
    """The grouping is the tool's contribution over a plain grep.

    A reader deciding whether `build_report` is deletable needs "one file defines
    it, one TEST imports it" -- not four undifferentiated lines. If the surface
    label collapsed, a symbol whose only consumer is its own test would read as
    load-bearing production code, which is the exact wrong-deletion call this
    command exists to prevent.
    """
    payload = WRT.build_payload(_repo(tmp_path), target_kind="symbol", target="build_report")

    surfaces = {entry["file"]: entry["surface"] for entry in payload["references"]}
    assert surfaces == {"scripts/consumer.py": "source", "tests/test_consumer.py": "test"}
    assert "definition" in _kinds_in(payload, "scripts/consumer.py")
    assert "import" in _kinds_in(payload, "tests/test_consumer.py")


def test_an_attribute_read_and_a_quoted_name_are_not_reported_as_the_same_kind(tmp_path: Path) -> None:
    """`config.report_limit` and `config["report_limit"]` are different evidence.

    One is a real attribute on an object this file already holds; the other is a
    name in a string that a rename would not follow. Reporting both as
    `direct-name` would hide exactly the occurrences a rename breaks silently.
    """
    payload = WRT.build_payload(_repo(tmp_path), target_kind="symbol", target="report_limit")

    kinds = _kinds_in(payload, "scripts/consumer.py")
    assert "attribute-access" in kinds
    assert "string-literal" in kinds


def test_a_copy_under_mutants_is_never_counted_as_a_consumer(tmp_path: Path) -> None:
    """`mutants/**` holds generated copies of the source being scanned.

    Counting them doubles every answer with references that no rename, no
    deletion, and no reader ever has to act on -- and unlike the `plugins/**`
    mirror, no flag re-includes them, so the exclusion must hold unconditionally.
    """
    repo = _repo(tmp_path)
    (repo / "mutants" / "scripts").mkdir(parents=True)
    (repo / "mutants" / "scripts" / "consumer.py").write_text(_CONSUMER, encoding="utf-8")
    (repo / "scripts" / "__pycache__").mkdir()
    (repo / "scripts" / "__pycache__" / "cached.py").write_text("build_report = 1\n", encoding="utf-8")

    payload = WRT.build_payload(repo, target_kind="symbol", target="build_report")

    assert payload["files_with_references"] == ["scripts/consumer.py", "tests/test_consumer.py"]


def test_a_line_naming_the_whole_path_is_reported_once_as_the_stronger_kind(tmp_path: Path) -> None:
    """A literal path and its basename on ONE line is one consumer, not two.

    The kinds are ranked: `literal-path` is unambiguous, `basename-reference` can
    collide across directories. Emitting both for the same line would inflate the
    count with a weaker duplicate of evidence already reported, and a tool whose
    counts are padded is one nobody checks against.
    """
    repo = _repo(tmp_path)
    (repo / "scripts" / "other.py").write_text('PATH = open("case-1.json")\n', encoding="utf-8")

    payload = WRT.build_payload(repo, target_kind="path", target="evals/case-1.json")

    assert _kinds_in(payload, "tests/test_consumer.py") == {"literal-path"}
    assert _kinds_in(payload, "scripts/other.py") == {"basename-reference"}


def test_a_question_mark_glob_that_opens_the_file_is_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`root.glob("evals/case-?.json")` opens `evals/case-1.json` and never names it.

    This is the recorded trap: a fixture consumed only by a glob looks orphaned to
    every plain grep, and a deletion proposal built on that zero is confidently
    wrong. `?` must consume exactly one character and must not cross a `/`.
    """
    monkeypatch.setattr(WRT, "_GLOB_CACHE", {})
    payload = WRT.build_payload(_repo(tmp_path), target_kind="path", target="evals/case-1.json")

    assert "glob-consumption" in _kinds_in(payload, "scripts/consumer.py")
    assert WRT._glob_regex("evals/case-?.json").match("evals/case-12.json") is None
    assert WRT._glob_regex("case-?.json").match("case-1.json") is not None


def test_a_trailing_double_star_matches_across_directory_levels(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`skills/**` reaches a file several levels down; `skills/*` must not.

    A `*` that silently crossed `/` reported 248 glob consumers for one fixture --
    an answer as unusable as a zero. `**` is the one form that is allowed to
    cross, so the two spellings have to give different answers.
    """
    monkeypatch.setattr(WRT, "_GLOB_CACHE", {})
    target = "skills/public/demo/scripts/run.py"
    payload = WRT.build_payload(_repo(tmp_path), target_kind="path", target=target)

    assert "glob-consumption" in _kinds_in(payload, "scripts/consumer.py")
    assert WRT._glob_regex("skills/**").match(target) is not None
    assert WRT._glob_regex("skills/*").match(target) is None


def test_a_compiled_glob_is_reused_rather_than_recompiled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every scanned line re-asks for the same handful of globs.

    The cache is what keeps a whole-repo path query linear in files rather than in
    lines x globs; losing it is invisible to correctness and very visible to
    anyone waiting for the answer.
    """
    monkeypatch.setattr(WRT, "_GLOB_CACHE", {})
    first = WRT._glob_regex("evals/case-?.json")

    assert WRT._glob_regex("evals/case-?.json") is first


def test_a_config_key_inside_an_error_message_is_reported_as_a_string_literal(tmp_path: Path) -> None:
    """`raise KeyError("report_limit")` is neither a declaration nor a lookup.

    It is still a consumer, and it is the kind a rename breaks into a lying error
    message rather than a crash. Reporting it as `lookup` would tell a reader the
    code READS the key there, which it does not.
    """
    payload = WRT.build_payload(_repo(tmp_path), target_kind="config-key", target="report_limit")

    assert _kinds_in(payload, ".agents/demo-adapter.yaml") == {"key-declaration"}
    consumer_kinds = _kinds_in(payload, "scripts/consumer.py")
    assert "lookup" in consumer_kinds
    assert "string-literal" in consumer_kinds


def _cli(repo: Path, *args: str):
    return run_loaded_script_main("what_reads_this.py", WRT, "--repo-root", str(repo), *args)


def test_the_cli_prints_a_summary_and_only_detail_carries_the_line_numbers(tmp_path: Path) -> None:
    """The default answer must stay readable, and `--detail` must add real lines.

    A whole-repo query emits hundreds of hits; printing them by default is how the
    tool becomes the unreadable grep it replaces. Both shapes still have to carry
    `unscanned_surfaces`, because a count without its scope is what makes a zero
    read as "nothing reads this".
    """
    repo = _repo(tmp_path)

    summary = _cli(repo, "--symbol", "build_report")
    assert summary.returncode == 0, summary.stderr
    summary_payload = yaml.safe_load(summary.stdout)
    assert "references" not in summary_payload
    assert summary_payload["files_with_references"] == ["scripts/consumer.py", "tests/test_consumer.py"]
    assert summary_payload["unscanned_surfaces"]

    detailed = _cli(repo, "--symbol", "build_report", "--detail")
    assert detailed.returncode == 0, detailed.stderr
    detail_payload = yaml.safe_load(detailed.stdout)
    assert detail_payload["references"][0]["hits"][0]["line"] > 0
    assert detail_payload["unscanned_surfaces"] == summary_payload["unscanned_surfaces"]


def test_each_target_flag_selects_its_own_finder_and_they_disagree(tmp_path: Path) -> None:
    """`--symbol`, `--path`, and `--config-key` are three different questions.

    If the CLI routed two of them to one finder the payload would still look
    plausible -- same shape, same keys -- while answering a question nobody asked.
    The kinds each one reports are what makes the routing observable.
    """
    repo = _repo(tmp_path)

    by_path = yaml.safe_load(_cli(repo, "--path", "evals/case-1.json").stdout)
    by_key = yaml.safe_load(_cli(repo, "--config-key", "report_limit").stdout)

    assert by_path["target_kind"] == "path"
    assert "glob-consumption" in by_path["reference_kinds"]
    assert by_key["target_kind"] == "config-key"
    assert "key-declaration" in by_key["reference_kinds"]


def test_the_cli_refuses_with_no_target_and_refuses_a_walk_when_git_is_required(tmp_path: Path) -> None:
    """Two refusals that must not be silent.

    With no target there is no defensible default -- searching for nothing would
    print a confident empty answer. And `--require-git-file-listing` exists because
    a filesystem walk and a git listing disagree exactly over uncommitted files: a
    caller who asked for tracked-file semantics must get a refusal, not a walk
    wearing the same payload shape.
    """
    repo = _repo(tmp_path)

    missing_target = _cli(repo)
    assert missing_target.returncode == 2

    walked = _cli(repo, "--symbol", "build_report")
    assert yaml.safe_load(walked.stdout)["listing"] == "filesystem-walk"

    refused = _cli(repo, "--symbol", "build_report", "--require-git-file-listing")
    assert refused.returncode == 1
    assert "repo file listing failed" in refused.stderr


def test_the_mirror_is_excluded_by_default_and_included_on_request(tmp_path: Path) -> None:
    """"Excluded" must never read as "absent".

    The exported `plugins/**` mirror reads what the source reads, so counting it
    doubles every answer -- but a reference that lives ONLY there has to be
    reported as unscanned rather than as zero, and `--include-mirrors` has to
    actually find it.
    """
    repo = _repo(tmp_path)
    mirrored = repo / "plugins" / "charness" / "scripts"
    mirrored.mkdir(parents=True)
    (mirrored / "only.py").write_text("from x import mirror_only_symbol\n", encoding="utf-8")

    default = yaml.safe_load(_cli(repo, "--symbol", "mirror_only_symbol").stdout)
    assert default["reference_count"] == 0
    assert default["zero_result_caveat"] is not None
    assert any("plugins/**" in line for line in default["unscanned_surfaces"])

    included = yaml.safe_load(_cli(repo, "--symbol", "mirror_only_symbol", "--include-mirrors").stdout)
    assert included["reference_count"] == 1


def test_the_script_runs_as_a_program_and_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`python3 scripts/what_reads_this.py --symbol X` is the documented invocation.

    Every other test here calls `main()` directly, which would keep passing if the
    `__main__` guard stopped propagating the exit status -- a command that always
    exits 0 cannot be used in a script or a hook.
    """
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    monkeypatch.setattr(
        sys, "argv", ["what_reads_this.py", "--repo-root", str(_repo(tmp_path)), "--symbol", "build_report"]
    )

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(WRT_PATH), run_name="__main__")

    assert excinfo.value.code == 0


# --------------------------------------------------------------------------
# scripts/scaffold_artifact_lib.py
# --------------------------------------------------------------------------


def test_a_records_family_refuses_when_every_dated_path_it_derives_is_taken(tmp_path: Path) -> None:
    """A scaffold writes a TEMPLATE, so resolving onto an existing record destroys it.

    Two default-titled critiques on one day already resolved to one file and the
    second destroyed the first while the payload reported `match`. The
    distinguisher tail buys three more names; once those are gone the only safe
    answer is a refusal that names every path tried and the remedy, so the author
    can pick a title instead of losing a record.
    """
    for name in ("2026-08-16-session.md", *(f"2026-08-16-session-{tail}.md" for tail in ("2", "3", "4"))):
        (tmp_path / name).write_text("existing record\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        scaffold_artifact_lib.subject_scoped_record_payload(
            tmp_path,
            output_dir=".",
            date_text="2026-08-16",
            title="Session",
            record_slug="session",
            template="# Session\n",
            validator_command_for=lambda path: f"validate {path}",
            remedy="Pass --title to name this record differently.",
        )

    message = str(excinfo.value)
    assert "./2026-08-16-session.md" in message
    assert "./2026-08-16-session-4.md" in message
    assert "Pass --title" in message


def test_a_records_family_takes_the_first_free_distinguisher(tmp_path: Path) -> None:
    """The refusal above is only honest if the non-refusing arm actually routes.

    A scaffold that refused as soon as the first path was taken would make the
    same-day second record impossible; one that overwrote would lose the first.
    """
    (tmp_path / "2026-08-16-session.md").write_text("existing record\n", encoding="utf-8")

    payload = scaffold_artifact_lib.subject_scoped_record_payload(
        tmp_path,
        output_dir=".",
        date_text="2026-08-16",
        title="Session",
        record_slug="session",
        template="# Session\n",
        validator_command_for=lambda path: f"validate {path}",
        remedy="Pass --title to name this record differently.",
    )

    assert payload["write_artifact_path"] == "./2026-08-16-session-2.md"


def test_the_scaffold_library_names_the_helper_it_could_not_find(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The library is loaded by file path with no package context.

    Dropped into a tree that owns no `scripts/` directory it must say WHICH helper
    is missing at import time. The alternative -- binding `emit_yaml` to nothing --
    surfaces as a `NameError` deep inside a scaffold run and reads as a charness
    bug rather than as a broken install.
    """
    monkeypatch.setattr(scaffold_artifact_lib, "__file__", str(tmp_path / "scaffold_artifact_lib.py"))

    with pytest.raises(ImportError, match=r"scripts/yaml_output\.py not found"):
        scaffold_artifact_lib._load_repo_helper("yaml_output.py")


# --------------------------------------------------------------------------
# skill runtime bootstrap loaders
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module",
    [
        pytest.param(COLLECT_COMMITS, id="announcement-collect-commits"),
        pytest.param(MINE_CLOSEOUT, id="retro-mine-closeout-telemetry"),
    ],
)
def test_a_skill_script_outside_a_charness_tree_names_the_missing_bootstrap(
    module: object, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skill scripts get copied out of the tree; that must fail loudly at load.

    Both scripts bind `emit_yaml` from the bootstrap at import time. Without the
    explicit refusal the ancestor walk simply returns `None` and the failure
    surfaces much later as an `AttributeError` on `None`, at which point the
    operator is debugging the skill instead of their install.
    """
    monkeypatch.setattr(module, "__file__", str(tmp_path / "script.py"))

    with pytest.raises(ImportError, match=r"skill_runtime_bootstrap\.py not found"):
        module._load_skill_runtime_bootstrap()


# --------------------------------------------------------------------------
# scripts/classify_t_signal.py
# --------------------------------------------------------------------------


def test_the_t_signal_cli_prints_a_classification_and_exits_zero_without_git(tmp_path: Path) -> None:
    """This runs inside closeout, where an exit code is a gate result.

    A tree with no git history cannot be classified, and the honest answer is a
    printed `diff_unavailable` with a zero exit -- not a crash, and not silence.
    A caller parsing stdout must always get a payload with the same keys.
    """
    result = run_loaded_script_main(
        "classify_t_signal.py", CLASSIFY_T_SIGNAL, "--repo-root", str(tmp_path)
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["t_status"] == "none"
    assert payload["skipped_reason"] == "diff_unavailable"


# --------------------------------------------------------------------------
# scripts/record_rca_event.py
# --------------------------------------------------------------------------


class _BlockScriptsPackage:
    """Makes `scripts.*` unimportable for the duration of one test, deterministically."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "scripts" or fullname.startswith("scripts."):
            raise ModuleNotFoundError(f"No module named {fullname!r}")
        return None


def test_the_rca_recorder_loads_when_run_as_a_plain_script(monkeypatch: pytest.MonkeyPatch) -> None:
    """`python3 scripts/record_rca_event.py` puts `scripts/` on the path, not the repo root.

    In that layout `from scripts import ...` cannot resolve, and the fallback arm
    is the ONLY thing that binds the ledger library and both YAML helpers. A
    fallback that bound one name and dropped another would import cleanly and then
    fail on the first receipt it tried to render, so all three are asserted.
    """
    # A meta-path finder, not a `sys.path` filter. Filtering the path leaves whether
    # `scripts` is reachable dependent on what other tests have already imported, so
    # this test took the try arm in one run and the fallback in another -- and the
    # fallback arm it exists to cover was not reliably exercised at all. A finder that
    # refuses the name outright does not depend on any of that.
    monkeypatch.setattr(sys, "meta_path", [_BlockScriptsPackage()] + sys.meta_path)
    for name in [name for name in sys.modules if name == "scripts" or name.startswith("scripts.")]:
        monkeypatch.delitem(sys.modules, name)
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))

    before = set(sys.modules)
    try:
        module = load_script_module("record_rca_event_no_package", ROOT / "scripts" / "record_rca_event.py")

        # What THIS module bound, not whether `scripts` happens to be importable in
        # this interpreter. The global probe (`pytest.raises(ImportError)` around
        # `import scripts.rca_ledger_lib`) passed in isolation and failed in the full
        # suite: whether some other test has left the package reachable is not a fact
        # about the layout under test, and asserting it made a correct fallback red.
        # `lib.__name__` is the discriminator: the try arm binds `scripts.rca_ledger_lib`
        # and the fallback binds the bare sibling. `render_yaml.__module__` is NOT usable
        # here -- the repo's bootstrap aliases the two module names, so the same function
        # object carries `scripts.yaml_output` either way.
        assert module.lib.__name__ == "rca_ledger_lib"
        assert module.render_yaml({"converted": True}).strip() == "converted: true"
        assert callable(module.emit_yaml)
        assert module.lib.resolve_ledger_path(ROOT, None) == ROOT / module.lib.LEDGER_PATH
    finally:
        for name in set(sys.modules) - before:
            del sys.modules[name]
