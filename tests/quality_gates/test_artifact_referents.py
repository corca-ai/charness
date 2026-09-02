"""The referent floor and the named-quantity floor.

Both exist because of one measured failure: four claims-review rounds on v6.3.0
produced ~14 blockers, not one of them in the shipped code. The dominant classes
were a disposition naming a destination it never reached, and a count restated
with a different value.

The control that makes this worth mechanizing is inside the same session: the
identical authoring mistake was caught in ZERO seconds, three times, by the
release-notes linter -- which re-derives its numbers -- and took four rounds in
the goal/retro artifacts, which had no such machinery.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.script_main import load_script_module

from .support import ROOT, run_script

ARTIFACT_QUANTITIES = load_script_module(
    "artifact_quantities_under_test", ROOT / "scripts" / "artifact_quantities.py"
)
ARTIFACT_REFERENTS = load_script_module(
    "artifact_referents_under_test", ROOT / "scripts" / "artifact_referents.py"
)
ARTIFACT_GATE = load_script_module(
    "artifact_referents_gate_under_test", ROOT / "scripts" / "check_artifact_referents.py"
)

inconsistent_quantities = ARTIFACT_QUANTITIES.inconsistent_quantities
quantity_sites = ARTIFACT_QUANTITIES.quantity_sites
render = ARTIFACT_QUANTITIES.render
bad_issue_refs = ARTIFACT_REFERENTS.bad_issue_refs
check_disposition_referents = ARTIFACT_REFERENTS.check_disposition_referents
is_placeholder_line = ARTIFACT_REFERENTS.is_placeholder_line
missing_paths = ARTIFACT_REFERENTS.missing_paths
unresolvable_shas = ARTIFACT_REFERENTS.unresolvable_shas
ResolverUnavailable = ARTIFACT_REFERENTS.ResolverUnavailable
git_commit_reachable_from_head = ARTIFACT_REFERENTS.git_commit_reachable_from_head
reachable_head_commits = ARTIFACT_REFERENTS.reachable_head_commits
sha_candidates = ARTIFACT_REFERENTS.sha_candidates
load_local_context_declarations = ARTIFACT_GATE.load_local_context_declarations

GATE = ROOT / "scripts" / "check_artifact_referents.py"


# --------------------------------------------------------------------------
# The exact defect that survived four rounds
# --------------------------------------------------------------------------


def test_issue_reference_placeholders_and_prose() -> None:
    """`issue #N` shipped inside a release bundle pointing at nothing, because
    `#N` is not in the form floor's placeholder vocabulary."""
    assert bad_issue_refs("Structural follow-up: issue #N (recurs: ...)") == ["N"]
    assert bad_issue_refs("Structural follow-up: issue #700 (novel: ...)") == []
    assert bad_issue_refs("`tracked issue: #701.`") == []
    for token in ("TBD", "todo", "x", "nnn"):
        assert bad_issue_refs(f"applied: issue #{token}") == [token], token
    for prose in (
        "the issue closeout floor was not run",
        "issue carrier is absent",
        "no issue anchors in a portable package",
        "the issue names two invariants",
    ):
        assert bad_issue_refs(prose) == [], prose


def test_angle_bracket_placeholders_defer_to_the_form_floor() -> None:
    """`#<n>` is this repo's documented placeholder syntax and the form floor's
    vocabulary already contains `<...>`. An author writing it is QUOTING THE
    FORM -- as the reference guidance and this gate's own rationale both do."""
    assert bad_issue_refs("each as an `applied: <what>` or a `tracked issue: #<n>`") == []


def test_a_todo_line_belongs_to_the_form_floor_not_here() -> None:
    """Double-reporting one defect from two gates makes both noisier, and the
    scaffold seeds `issue #N` as literal template text on a `TODO` line."""
    scaffold = "Structural follow-up: TODO — classify as `issue #N (recurs:|novel: <reason>)`"
    assert is_placeholder_line(scaffold) is True
    assert check_disposition_referents(scaffold, ROOT) == []


def test_hex_looking_english_is_not_a_sha() -> None:
    """Every word must be >= 7 chars, or `SHA_RE`'s `{7,40}` bound excludes
    it before `_HEX_WORDS` is consulted and the test passes with the filter
    deleted."""
    for word in ("defaced", "acceded", "effaced"):
        assert len(word) >= 7
        assert unresolvable_shas(f"the {word} of it", ROOT, run=lambda *a: False) == []


def test_a_long_digit_run_is_a_number_not_a_sha() -> None:
    assert unresolvable_shas("8224123144 bytes", ROOT, run=lambda *a: False) == []


# --------------------------------------------------------------------------
# Path and commit referents
# --------------------------------------------------------------------------


def test_a_named_path_that_does_not_exist_is_reported() -> None:
    findings = missing_paths("applied: scripts/does_not_exist_here.py now does it", ROOT)
    assert findings == ["scripts/does_not_exist_here.py"]


def test_a_named_path_that_exists_passes() -> None:
    assert missing_paths("applied: `scripts/artifact_referents.py` owns it", ROOT) == []


def test_an_unresolvable_sha_is_reported() -> None:
    assert unresolvable_shas("see `deadbee1234`", ROOT, run=lambda *a: False) == ["deadbee1234"]


def test_a_typed_content_identity_does_not_hide_a_commit_candidate() -> None:
    for content_label in (
        "packet",
        "packet identity",
        "packet_identity:",
        "reviewed-input identity:",
        "reviewed_input_identity:",
        "input identity:",
        "findings identity:",
        "findings_identity:",
        "identity_sha256:",
    ):
        line = f"{content_label} `6015111c...`; commit `deadbee1234`"
        assert sha_candidates(line) == ["deadbee1234"], content_label


def test_a_git_commit_identity_remains_a_commit_candidate() -> None:
    assert sha_candidates("Git commit identity: `c2db5e7cd1e6`") == ["c2db5e7cd1e6"]


def test_uuid_components_are_not_commit_candidates_but_a_sibling_sha_is() -> None:
    line = (
        'Retired evaluation: {"run_id":"2026-08-24-'
        '01a032f5-c64c-7ad2-a838-8eb738d99824"} commit `4dc3fb851`'
    )

    assert sha_candidates(line) == ["4dc3fb851"]


def test_malformed_uuid_components_remain_commit_candidates() -> None:
    assert sha_candidates("2026-08-24-01a032f5-c64c-7ad2-a838-8eb738d9982") == [
        "01a032f5",
        "8eb738d9982",
    ]


def test_a_uuid_component_repeated_outside_the_uuid_remains_a_candidate() -> None:
    line = "session 01a032f5-c64c-7ad2-a838-8eb738d99824 commit `01a032f5`"

    assert sha_candidates(line) == ["01a032f5"]


def test_git_absence_does_not_invent_a_defect() -> None:
    """Absence of a resolver is not evidence the referent is bad. A gate that
    fails closed on a missing tool reports defects that are not there."""
    assert unresolvable_shas("see `deadbee1234`", ROOT, run=lambda *a: True) == []


# --------------------------------------------------------------------------
# Named quantities
# --------------------------------------------------------------------------


def test_the_same_quantity_stated_twice_with_two_values_is_caught() -> None:
    """The v6.3.0 defect: "ten across the slices" restated after the count had
    become twelve, by the very repair that changed it."""
    text = "Found {{q:total=27}} blockers.\n\nOf the {{q:total=21}} above ..."
    findings = inconsistent_quantities(text)

    assert len(findings) == 1
    assert findings[0]["id"] == "total"
    assert findings[0]["values"] == ["21", "27"]
    assert [s["line"] for s in findings[0]["sites"]] == [1, 3]


def test_agreeing_restatements_pass() -> None:
    text = "{{q:total=27}} blockers; of the {{q:total=27}} above ..."
    assert inconsistent_quantities(text) == []


def test_a_single_site_is_never_a_finding() -> None:
    """Self-consistency, not correctness. One statement cannot disagree with
    itself, and claiming otherwise would be inventing a verdict."""
    assert inconsistent_quantities("{{q:total=27}} blockers") == []


def test_markers_render_to_their_values() -> None:
    assert render("{{q:total=27}} blockers") == "27 blockers"


def test_sites_are_reported_with_line_numbers() -> None:
    sites = quantity_sites("a {{q:x=1}}\nb {{q:y=2}} {{q:x=1}}")
    assert sites == [(1, "x", "1"), (2, "y", "2"), (2, "x", "1")]


# --------------------------------------------------------------------------
# End to end: twelve independent single-artifact gate invocations, one node.
# Each carries its former test's rationale in its own docstring; a failure
# names the exact `_case_*` function in its traceback.
# --------------------------------------------------------------------------


def _run(*args: str) -> subprocess.CompletedProcess:
    return run_script(str(GATE), "--repo-root", str(ROOT), *args)


def _case_gate_blocks_on_dated_artifact_with_bad_referent(case_dir: Path) -> None:
    artifact = case_dir / "2026-08-25-control.md"
    artifact.write_text("Structural follow-up: issue #N (novel: x)\n", encoding="utf-8")
    result = _run("--path", str(artifact))
    assert result.returncode == 1
    assert "unresolvable-issue-ref" in result.stdout


def _case_gate_passes_the_same_artifact_once_repaired(case_dir: Path) -> None:
    artifact = case_dir / "2026-08-25-control.md"
    artifact.write_text("Structural follow-up: issue #700 (novel: x)\n", encoding="utf-8")
    result = _run("--path", str(artifact))
    assert result.returncode == 0
    assert "status: clean" in result.stdout


def _case_out_of_tree_path_does_not_crash(case_dir: Path) -> None:
    """`Path.relative_to` RAISES on a path outside the root rather than
    returning something, and a checker that crashes on an out-of-tree input is
    one whose negative control cannot be written. Found while writing that
    control."""
    # The fixture must PRODUCE A FINDING: `_display_path` is only reached while
    # constructing one, so a clean fixture never exercises the ValueError this
    # case is named for. A reviewer caught the earlier version passing for the
    # wrong reason.
    artifact = case_dir / "2026-08-25-outside.md"
    artifact.write_text("Structural follow-up: issue #N (novel: x)\n", encoding="utf-8")
    result = _run("--path", str(artifact))
    assert "Traceback" not in result.stderr
    assert result.returncode == 1
    assert str(artifact) in result.stdout


def _case_undatable_artifact_fail_closed_for_issue_refs(case_dir: Path) -> None:
    """`#N` was never valid, so an undated filename must not buy an exemption."""
    artifact = case_dir / "recent-lessons.md"
    artifact.write_text("Structural follow-up: issue #N (novel: x)\n", encoding="utf-8")
    result = _run("--path", str(artifact))
    assert result.returncode == 1
    assert "unresolvable-issue-ref" in result.stdout


def _case_undatable_artifact_not_fail_closed_for_shas(case_dir: Path) -> None:
    """The asymmetry. A SHA can be correct when written and stop resolving when
    history is rewritten, so blocking an undated rolling digest would punish an
    author for a change made after they wrote it -- and the only remedy would be
    editing frozen memory so a checker goes green."""
    artifact = case_dir / "recent-lessons.md"
    artifact.write_text("landed at `deadbee1234`\n", encoding="utf-8")
    result = _run("--path", str(artifact))
    # Assert the COUNT, not the label. `grandfathered (reported, not rewritten):`
    # prints unconditionally, so `"grandfathered" in stdout` passed with zero
    # findings, with a broken SHA_RE, and with the fixture never opened -- the
    # render-identically-either-way shape this gate refuses, reintroduced by the
    # repair that added these very cases.
    assert result.returncode == 0
    assert "grandfathered (reported, not rewritten): 1" in result.stdout
    assert "non-durable-commit-ref" in result.stdout


def _case_pre_cutoff_artifact_reports_without_blocking(case_dir: Path) -> None:
    artifact = case_dir / "2026-01-01-frozen.md"
    artifact.write_text("Structural follow-up: issue #N (novel: x)\n", encoding="utf-8")
    result = _run("--path", str(artifact))
    assert result.returncode == 0
    assert "grandfathered (reported, not rewritten): 1" in result.stdout


def _case_path_that_does_not_exist_is_input_error(case_dir: Path) -> None:
    """`scanned` used to count a file the gate never opened, so a typo in a
    wiring line was indistinguishable from a passing run."""
    result = _run("--path", "/tmp/definitely-not-here-9f3a.md")
    assert result.returncode == 1
    assert "UNREADABLE" in result.stdout


def _case_directory_argument_is_input_error(case_dir: Path) -> None:
    result = _run("--path", str(case_dir))
    assert result.returncode == 1
    assert "UNREADABLE" in result.stdout


def _case_empty_corpus_blocks(case_dir: Path) -> None:
    """An undeclared empty universe is a reported discovered-empty no-op."""
    result = run_script(str(GATE), "--repo-root", str(case_dir))
    assert result.returncode == 0
    assert "DISCOVERED EMPTY" in result.stdout


def _case_exit_code_follows_printed_status(case_dir: Path) -> None:
    """The status line and the exit code must not disagree: the runner believes
    the code and the human believes the message. An earlier version printed
    `status: blocked` and exited 0."""
    result = _run("--path", "/tmp/definitely-not-here-9f3a.md")
    assert ("status: blocked" in result.stdout) == (result.returncode == 1)


def _case_refusing_resolver_exits_unestablished(case_dir: Path) -> None:
    """The B3 repair turned a false-positive storm into a SILENT false negative:
    the gate exited 0, run-quality printed PASS, and the passing phase's log --
    carrying the only explanation -- is deleted at EXIT. Exit 3 is the runner's
    own byte for "ran, established nothing"."""
    artifact = case_dir / "2026-08-25-nogit.md"
    artifact.write_text("landed at `deadbee1234`\n", encoding="utf-8")
    result = run_script(str(GATE), "--repo-root", str(case_dir), "--path", str(artifact))
    assert result.returncode == 3, result.stdout
    assert "WARNING" in result.stdout, "run-quality only prints a passing gate's log on this token"
    assert "STOOD DOWN" in result.stdout


def _case_inconsistent_quantity_reported_with_first_site(case_dir: Path) -> None:
    """The quantity findings are assembled in the gate, not the library, and
    that assembly had no test: the release gate named both of its lines
    uncovered."""
    artifact = case_dir / "2026-08-25-quantities.md"
    artifact.write_text(
        "Found {{q:total=27}} blockers.\n\nOf the {{q:total=21}} above ...\n", encoding="utf-8"
    )
    result = _run("--path", str(artifact))
    assert result.returncode == 1
    assert "inconsistent-quantity" in result.stdout
    assert ":1 " in result.stdout, "should anchor on the FIRST site"


_GATE_INVOCATION_CASES = {
    "gate-blocks-on-dated-artifact-with-bad-referent": _case_gate_blocks_on_dated_artifact_with_bad_referent,
    "gate-passes-the-same-artifact-once-repaired": _case_gate_passes_the_same_artifact_once_repaired,
    "out-of-tree-path-does-not-crash": _case_out_of_tree_path_does_not_crash,
    "undatable-artifact-fail-closed-for-issue-refs": _case_undatable_artifact_fail_closed_for_issue_refs,
    "undatable-artifact-not-fail-closed-for-shas": _case_undatable_artifact_not_fail_closed_for_shas,
    "pre-cutoff-artifact-reports-without-blocking": _case_pre_cutoff_artifact_reports_without_blocking,
    "path-that-does-not-exist-is-input-error": _case_path_that_does_not_exist_is_input_error,
    "directory-argument-is-input-error": _case_directory_argument_is_input_error,
    "empty-corpus-blocks": _case_empty_corpus_blocks,
    "exit-code-follows-printed-status": _case_exit_code_follows_printed_status,
    "refusing-resolver-exits-unestablished": _case_refusing_resolver_exits_unestablished,
    "inconsistent-quantity-reported-with-first-site": _case_inconsistent_quantity_reported_with_first_site,
}


def test_gate_invocation_cases(tmp_path: Path) -> None:
    for label, case in _GATE_INVOCATION_CASES.items():
        case_dir = tmp_path / label
        case_dir.mkdir()
        case(case_dir)


def test_the_repo_corpus_is_clean_and_reports_its_grandfathered_set() -> None:
    """The gate must be honest about what it is NOT enforcing. Frozen artifacts
    are counted and named, never rewritten to make a checker green."""
    result = _run()

    assert result.returncode == 0, result.stdout[-2000:]
    # Assert on the NUMBERS, not the label. `grandfathered (reported, not
    # rewritten):` is printed unconditionally, so the earlier version passed
    # when the set was empty, when `scanned` was 0, and when the globs were
    # broken -- the same render-identically-either-way shape this gate exists
    # to refuse, inside the gate's own test.
    scanned = int(re.search(r"scanned: (\d+) artifact", result.stdout).group(1))
    dispositions = int(re.search(r"dispositions_examined: (\d+)", result.stdout).group(1))
    grandfathered = int(
        re.search(r"grandfathered \(reported, not rewritten\): (\d+)", result.stdout).group(1)
    )

    assert scanned > 500, "the corpus collapsed; a clean verdict here proves nothing"
    assert dispositions > 100, "the disposition regex stopped matching corpus-wide"
    assert grandfathered > 0, "frozen history should be reported, not silently absent"


def test_scope_is_reported_as_numbers() -> None:
    """A gate that silently drops its own scope prints the same clean line as one
    with nothing to drop. The excluded count has to be a NUMBER."""
    result = _run()

    assert re.search(r"dispositions_examined: \d+", result.stdout)
    assert re.search(r"shas_resolved: \d+", result.stdout)


# --------------------------------------------------------------------------
# Resolver failure is not a verdict
# --------------------------------------------------------------------------


def test_git_refusing_is_distinguished_from_a_missing_commit() -> None:
    """`exit 128` is what git returns for "not a work tree" and for "dubious
    ownership" -- routine in containers. Treating it as "this SHA is absent"
    would report every SHA in every dated artifact as unresolvable."""
    assert git_commit_reachable_from_head("96ba78f7f", ROOT) is True
    with pytest.raises(ResolverUnavailable):
        git_commit_reachable_from_head("96ba78f7f", Path("/tmp"))


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _build_side_branch_repo_seed(seed: Path) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo

    repo = install_committed_repo(seed / "repo", {"base.txt": "base\n"}, message="base")
    _git(repo, "config", "user.name", "Charness Test")
    _git(repo, "config", "user.email", "charness-test@example.invalid")
    _git(repo, "switch", "-c", "local-lane")
    (repo / "lane.txt").write_text("local\n", encoding="utf-8")
    _git(repo, "add", "lane.txt")
    _git(repo, "commit", "-m", "local lane")
    local_sha = _git(repo, "rev-parse", "HEAD")
    _git(repo, "switch", "main")
    (seed / "side-branch-commit").write_text(f"{local_sha}\n", encoding="utf-8")


def _repo_with_side_branch_commit(tmp_path: Path) -> tuple[Path, str]:
    from tests.seed_cache import get_or_build

    seed = get_or_build("artifact-referents-side-branch-repo-seed", _build_side_branch_repo_seed)
    repo = shutil.copytree(seed / "repo", tmp_path / "repo")
    local_sha = (seed / "side-branch-commit").read_text(encoding="utf-8").strip()
    return repo, local_sha


def test_side_branch_seed_copies_are_private(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first_repo, first_sha = _repo_with_side_branch_commit(first_root)
    second_repo, second_sha = _repo_with_side_branch_commit(second_root)

    (first_repo / "base.txt").write_text("mutated\n", encoding="utf-8")

    assert first_repo != second_repo
    assert first_sha == second_sha
    assert (second_repo / "base.txt").read_text(encoding="utf-8") == "base\n"
    assert git_commit_reachable_from_head(second_sha, second_repo) is False


@pytest.mark.boundary_contract(
    reason="target spawns git and this test observes shallow-repository reachability refusal"
)
def test_reachability_and_history_queries_over_one_side_branch_checkout(tmp_path: Path) -> None:
    """Three read-only questions against one immutable side-branch checkout,
    merged because none of them mutates the repo they observe.

    - "Same tracked HEAD must answer identically in a clean and authoring
      clone" (a commit visible only on a side branch is not durable).
    - Absent and non-commit objects are both typed negative, not durable.
    - A shallow clone cannot answer "reachable from HEAD" at all; it must
      refuse rather than report a missing commit.
    """
    repo, local_sha = _repo_with_side_branch_commit(tmp_path)

    assert _git(repo, "cat-file", "-t", local_sha) == "commit"
    assert git_commit_reachable_from_head(local_sha, repo) is False

    blob_sha = _git(repo, "rev-parse", "HEAD:base.txt")
    assert git_commit_reachable_from_head("deadbee1234", repo) is False
    assert git_commit_reachable_from_head(blob_sha, repo) is False

    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "--depth=1", f"file://{repo}", str(shallow)],
        capture_output=True,
        text=True,
        check=True,
    )
    with pytest.raises(ResolverUnavailable, match="shallow"):
        reachable_head_commits(shallow)


def test_failed_head_ancestry_read_is_unestablished(monkeypatch: pytest.MonkeyPatch) -> None:
    results = iter(
        [
            subprocess.CompletedProcess([], 0, "false\n", ""),
            subprocess.CompletedProcess([], 2, "", "rev-list failed"),
        ]
    )
    monkeypatch.setattr(ARTIFACT_REFERENTS, "run_process", lambda *args, **kwargs: next(results))

    with pytest.raises(ResolverUnavailable, match="rev-list failed"):
        reachable_head_commits(ROOT)


def test_exact_local_context_declaration_is_visible_and_stale_checked(tmp_path: Path) -> None:
    import hashlib
    import json

    repo, local_sha = _repo_with_side_branch_commit(tmp_path)
    artifact_rel = "charness-artifacts/goals/2026-08-30-local-context.md"
    artifact = repo / artifact_rel
    artifact.parent.mkdir(parents=True)
    line = f"local lane `{local_sha}`"
    artifact.write_text(f"{line}\n", encoding="utf-8")
    declarations = repo / "scripts" / "artifact-referent-local-context.json"
    declarations.parent.mkdir()
    entry = {
        "artifact": artifact_rel,
        "line": 1,
        "token": local_sha,
        "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
        "reason": "frozen local shaping context",
    }
    declarations.write_text(json.dumps([entry]), encoding="utf-8")
    _git(repo, "add", str(declarations.relative_to(repo)))
    command = [str(GATE), "--repo-root", str(repo), "--path", artifact_rel]

    accepted = run_script(*command)
    assert accepted.returncode == 0, accepted.stdout
    assert "declared local context (reported, exact): 1" in accepted.stdout
    assert "declared-local-commit-ref" in accepted.stdout

    artifact.write_text(f"changed context, same token `{local_sha}`\n", encoding="utf-8")
    changed_line = run_script(*command)
    assert changed_line.returncode == 1
    assert "stale-local-context-declaration" in changed_line.stdout
    artifact.write_text(f"{line}\n", encoding="utf-8")

    entry["line"] = 2
    declarations.write_text(json.dumps([entry]), encoding="utf-8")
    _git(repo, "add", str(declarations.relative_to(repo)))
    stale = run_script(*command)
    assert stale.returncode == 1
    assert "stale-local-context-declaration" in stale.stdout
    assert "non-durable-commit-ref" in stale.stdout


_MALFORMED_LOCAL_CONTEXT_MUTATIONS = [
    {"reason": ""},
    {"line": 0},
    {"token": "not-a-sha"},
    {"line_sha256": "not-a-fingerprint"},
    {"extra": "second owner"},
]


def test_malformed_local_context_declarations_block(tmp_path: Path) -> None:
    """Five ways a declaration can be malformed, one node.

    Was a `pytest.mark.parametrize` -- five pytest nodes for five variants of
    one otherwise-identical repo build. The wanted shape keeps the git-owning
    checkout construction inside a loop of one node instead.
    """
    import hashlib
    import json

    for index, mutation in enumerate(_MALFORMED_LOCAL_CONTEXT_MUTATIONS):
        repo, local_sha = _repo_with_side_branch_commit(tmp_path / f"case-{index}")
        artifact_rel = "charness-artifacts/goals/2026-08-30-local-context.md"
        artifact = repo / artifact_rel
        artifact.parent.mkdir(parents=True)
        line = f"local lane `{local_sha}`"
        artifact.write_text(f"{line}\n", encoding="utf-8")
        declarations = repo / "scripts" / "artifact-referent-local-context.json"
        declarations.parent.mkdir()
        entry: dict[str, object] = {
            "artifact": artifact_rel,
            "line": 1,
            "token": local_sha,
            "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
            "reason": "why",
        }
        entry.update(mutation)
        declarations.write_text(json.dumps([entry]), encoding="utf-8")
        _git(repo, "add", str(declarations.relative_to(repo)))

        result = run_script(str(GATE), "--repo-root", str(repo), "--path", artifact_rel)
        assert result.returncode == 1, mutation
        assert "malformed-local-context-declaration" in result.stdout, mutation


def test_untracked_local_context_declaration_cannot_change_the_verdict(tmp_path: Path) -> None:
    import hashlib
    import json

    repo, local_sha = _repo_with_side_branch_commit(tmp_path)
    artifact_rel = "charness-artifacts/goals/2026-08-30-local-context.md"
    artifact = repo / artifact_rel
    artifact.parent.mkdir(parents=True)
    line = f"local lane `{local_sha}`"
    artifact.write_text(f"{line}\n", encoding="utf-8")
    declarations = repo / "scripts" / "artifact-referent-local-context.json"
    declarations.parent.mkdir()
    declarations.write_text(
        json.dumps(
            [
                {
                    "artifact": artifact_rel,
                    "line": 1,
                    "token": local_sha,
                    "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
                    "reason": "unreviewed local bytes",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(str(GATE), "--repo-root", str(repo), "--path", artifact_rel)
    assert result.returncode == 1
    assert "unbound-local-context-declaration" in result.stdout


def _declaration_bytes(tmp_path: Path, payload: object) -> tuple[Path, bytes]:
    import json

    repo = tmp_path / "repo"
    path = repo / "scripts/artifact-referent-local-context.json"
    path.parent.mkdir(parents=True)
    data = json.dumps(payload).encode()
    path.write_bytes(data)
    return repo, data


def _valid_declaration() -> dict[str, object]:
    return {
        "artifact": "charness-artifacts/goals/2026-08-30-x.md",
        "line": 1,
        "token": "deadbee",
        "line_sha256": "0" * 64,
        "reason": "intentional local context",
    }


def test_declaration_index_read_error_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _data = _declaration_bytes(tmp_path, [_valid_declaration()])

    def fail_index_read(*args, **kwargs):
        raise OSError("index unavailable")

    monkeypatch.setattr(ARTIFACT_GATE, "run_process", fail_index_read)
    declarations, defects = load_local_context_declarations(repo)

    assert declarations == []
    assert defects[0]["kind"] == "unbound-local-context-declaration"
    assert "index unavailable" in str(defects[0]["detail"])


_INVALID_DECLARATION_FILE_SHAPES = [
    (b"{not json", "malformed-local-context-declaration"),
    (None, "malformed-local-context-declaration"),
    ("duplicate", "duplicate-local-context-declaration"),
]


def test_invalid_declaration_file_shapes_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No real git anywhere in these three: the guard seam is mocked outright.

    Was a `pytest.mark.parametrize`; folded into a loop for the same reason as
    the malformed-declaration cases above, even though this cluster's git count
    was already zero -- the parametrize node-count cost was independent of it.
    """
    for raw, expected_kind in _INVALID_DECLARATION_FILE_SHAPES:
        if raw == "duplicate":
            payload: object = [_valid_declaration(), _valid_declaration()]
            repo, data = _declaration_bytes(tmp_path / "duplicate", payload)
        elif raw is None:
            repo, data = _declaration_bytes(tmp_path / "none", _valid_declaration())
        else:
            repo = tmp_path / "malformed" / "repo"
            path = repo / "scripts/artifact-referent-local-context.json"
            path.parent.mkdir(parents=True)
            path.write_bytes(raw)
            data = raw

        indexed = subprocess.CompletedProcess(
            [], 0, data.decode("utf-8") if isinstance(data, bytes) else json.dumps(data), ""
        )
        monkeypatch.setattr(ARTIFACT_GATE, "run_process", lambda *args, **kwargs: indexed)
        declarations, defects = load_local_context_declarations(repo)

        if raw == "duplicate":
            assert declarations == [_valid_declaration()], raw
        else:
            assert declarations == [], raw
        assert expected_kind in [str(defect["kind"]) for defect in defects], raw


# --------------------------------------------------------------------------
# Evasion and self-documentation
# --------------------------------------------------------------------------


def test_an_unrelated_TODO_elsewhere_on_the_line_does_not_disarm_the_rung() -> None:
    """The placeholder test is scoped to the disposition's VALUE. Searching the
    whole line let any author disarm the rung by leaving one scaffold field
    blank."""
    evasion = "Structural follow-up: issue #N (recurs: x). Owner: TODO"

    assert is_placeholder_line(evasion) is False
    assert len(check_disposition_referents(evasion, ROOT)) == 1


def test_the_gate_can_be_documented_inside_its_own_corpus() -> None:
    """Otherwise the next retro explaining this gate is its own first false
    positive. The discriminator is ENUMERATION, not backticks -- the real v6.3.0
    defect was itself inside a code span."""
    for documentation in (
        "the floor accepts `applied: <what>` / `issue #N` / `none — <reason>`",
        "(`issue #N`/`applied:`/`accepted-risk:`/`out-of-scope:`) accepts it.",
    ):
        assert check_disposition_referents(documentation, ROOT) == [], documentation


def test_a_committed_disposition_is_still_caught_inside_backticks() -> None:
    """A backtick exemption would have exempted the exact defect this exists for."""
    for real_defect in (
        "Decision: `issue #N (recurs: the release flow already solves this)`",
        "Structural follow-up: issue #N (novel: something specific)",
        "- **applied**: issue #N",
    ):
        assert len(check_disposition_referents(real_defect, ROOT)) == 1, real_defect


def test_this_repos_other_disposition_spellings_are_seen() -> None:
    """`Disposition:` appears 75 times across 28 checked-in goals, and `**applied**`
    puts bold markers between the word and the colon."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("gate", GATE)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    for spelling in (
        "Disposition: **applied** — see scripts/does_not_exist_here.py",
        "- **applied**: scripts/does_not_exist_here.py",
    ):
        assert gate.disposition_lines(spelling) != [], spelling


# --------------------------------------------------------------------------
# Round 2: the repairs' own failure modes
# --------------------------------------------------------------------------


def test_a_real_disposition_naming_two_forms_is_still_checked() -> None:
    """`Retro dispositions: applied: ...` is the corpus's DOMINANT spelling and
    names two vocabulary forms while committing to one. Round 1's bare
    two-form count exempted it, which was an evasion on the commonest shape."""
    evasion = "Retro dispositions: applied: filed the follow-up as issue #N"

    assert len(check_disposition_referents(evasion, ROOT)) == 1


def test_an_angle_bracket_anywhere_on_the_line_does_not_exempt_it() -> None:
    """`<ref>`, `<repo-root>`, `<path>` are ordinary repo idiom. Round 1 scoped
    the FORM count to the value and left the SLOT test scanning the whole line,
    reproducing the exact evasion the scoping closed."""
    evasion = "Structural follow-up: issue #N (recurs: reviewers use git show <ref>:<path>)"

    assert len(check_disposition_referents(evasion, ROOT)) == 1


def test_documentation_is_exempt_by_enumeration_without_any_slot() -> None:
    """Pins the ENUMERATION branch specifically. Both earlier documentation
    cases carried a `<slot>`, so only the slot branch was exercised while the
    docstring claimed enumeration was the discriminator."""
    documentation = "(`issue #N`/`applied:`/`accepted-risk:`/`out-of-scope:`) accepts it."

    assert check_disposition_referents(documentation, ROOT) == []


def test_the_documentation_exemption_does_not_cover_paths() -> None:
    """The self-documentation problem is specific to `issue #N` as an example.
    Round 1's blanket early-return also exempted a documentation line naming a
    DELETED file -- wider than its own justification."""
    line = "the floor accepts `applied: <what>` / `issue #N`, see docs/definitely-gone.md"
    findings = check_disposition_referents(line, ROOT)

    assert [f["kind"] for f in findings] == ["missing-path-referent"]


def test_an_inline_disposition_placeholder_defers() -> None:
    """L-b: the fallback's comment described behaviour the code did not have."""
    assert is_placeholder_line("- The retro entry is applied: TODO") is True


def test_shas_resolved_counts_tokens_not_lines() -> None:
    """M1: the counter incremented once per LINE, so it stayed at the corpus
    line count even if SHA_RE stopped matching entirely -- structurally unable
    to show the collapse it was added to detect."""
    assert sha_candidates("no shas here at all") == []
    assert sha_candidates("`96ba78f7f` and `deadbee1234`") == ["96ba78f7f", "deadbee1234"]


def test_the_corpus_run_reports_a_nonzero_sha_count() -> None:
    """A floor, because `shas_resolved: 0` satisfied every earlier assertion."""
    result = _run()

    resolved = int(re.search(r"shas_resolved: (\d+)", result.stdout).group(1))
    assert resolved > 100, "the SHA rung examined almost nothing; a clean verdict proves little"


def test_the_disposition_vocabulary_has_one_owner() -> None:
    """L-c: two near-identical regexes existed. The failure mode is not drift but
    'one grows and the other silently degrades' -- adding a keyword to the gate's
    copy would revert the library to whole-line scoping, reintroducing the M2 and
    M3 evasions at once."""
    gate_source = (ROOT / "scripts" / "check_artifact_referents.py").read_text(encoding="utf-8")

    assert "DISPOSITION_LINE_RE = re.compile" not in gate_source
    assert "INLINE_DISPOSITION_RE = re.compile" not in gate_source


# --------------------------------------------------------------------------
# Changed-line coverage: lines the release gate named as uncovered
# --------------------------------------------------------------------------


def test_a_url_in_a_disposition_is_not_treated_as_a_repo_path() -> None:
    """`PATH_RE` matches `docs/x.md`-shaped tokens, and a URL's tail looks like
    one. Skipping schemed candidates is what stops every external link in a
    disposition being reported as a missing file."""
    line = "applied: see https://example.com/docs/guide.md for the rationale"

    assert missing_paths(line, ROOT) == []


def test_git_failing_to_run_at_all_raises_rather_than_answering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The OSError arm. A missing or unexecutable git is "cannot answer", not
    "this SHA is absent" -- answering would report every SHA in the corpus as
    unresolvable."""
    with pytest.raises(ResolverUnavailable):
        git_commit_reachable_from_head("96ba78f7f", Path("/nonexistent-root-9f3a/deeper"))

    # And the OSError arm specifically: git absent from PATH entirely.
    def _boom(*args, **kwargs):
        raise OSError("no git here")

    monkeypatch.setattr(ARTIFACT_REFERENTS, "run_process", _boom)
    with pytest.raises(ResolverUnavailable, match="could not be run"):
        git_commit_reachable_from_head("96ba78f7f", ROOT)
