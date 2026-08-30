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

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

sys.path.insert(0, str(ROOT))

from scripts.artifact_quantities import (  # noqa: E402
    inconsistent_quantities,
    quantity_sites,
    render,
)
from scripts.artifact_referents import (  # noqa: E402
    bad_issue_refs,
    check_disposition_referents,
    is_placeholder_line,
    missing_paths,
    unresolvable_shas,
)

GATE = ROOT / "scripts" / "check_artifact_referents.py"


# --------------------------------------------------------------------------
# The exact defect that survived four rounds
# --------------------------------------------------------------------------


def test_the_hash_N_that_passed_every_gate_is_caught() -> None:
    """THE regression. `issue #N` shipped inside a release bundle pointing at
    nothing, because `#N` is not in the form floor's placeholder vocabulary
    (`TODO|TBD|<...>|FIXME`) and `issue #N` is a well-formed disposition."""
    assert bad_issue_refs("Structural follow-up: issue #N (recurs: ...)") == ["N"]


def test_a_real_issue_number_passes() -> None:
    assert bad_issue_refs("Structural follow-up: issue #700 (novel: ...)") == []
    assert bad_issue_refs("`tracked issue: #701.`") == []


@pytest.mark.parametrize("token", ["TBD", "todo", "x", "nnn"])
def test_other_placeholder_shapes_are_caught_too(token: str) -> None:
    assert bad_issue_refs(f"applied: issue #{token}") == [token]


# --------------------------------------------------------------------------
# False positives -- a gate authors learn to skip is worse than no gate
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prose",
    [
        "the issue closeout floor was not run",
        "issue carrier is absent",
        "no issue anchors in a portable package",
        "the issue names two invariants",
    ],
)
def test_prose_about_issues_is_not_an_issue_reference(prose: str) -> None:
    """`issue <word>` is ordinary English about this repo's own machinery and
    appears in dozens of checked-in goals. Requiring `#` or digits is what keeps
    this gate credible."""
    assert bad_issue_refs(prose) == []


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


@pytest.mark.parametrize("word", ["defaced", "acceded", "effaced"])
def test_hex_looking_english_is_not_a_sha(word: str) -> None:
    """Every parameter must be >= 7 chars, or `SHA_RE`'s `{7,40}` bound excludes
    it before `_HEX_WORDS` is consulted and the test passes with the filter
    deleted. The earlier version had two 6-char words doing exactly that."""
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


@pytest.mark.parametrize(
    "content_label",
    [
        "packet",
        "packet identity",
        "packet_identity:",
        "reviewed-input identity:",
        "reviewed_input_identity:",
        "input identity:",
        "findings identity:",
        "findings_identity:",
        "identity_sha256:",
    ],
)
def test_a_typed_content_identity_does_not_hide_a_commit_candidate(
    content_label: str,
) -> None:
    from scripts.artifact_referents import sha_candidates

    line = f"{content_label} `6015111c...`; commit `deadbee1234`"

    assert sha_candidates(line) == ["deadbee1234"]


def test_a_git_commit_identity_remains_a_commit_candidate() -> None:
    from scripts.artifact_referents import sha_candidates

    assert sha_candidates("Git commit identity: `c2db5e7cd1e6`") == ["c2db5e7cd1e6"]


def test_uuid_components_are_not_commit_candidates_but_a_sibling_sha_is() -> None:
    from scripts.artifact_referents import sha_candidates

    line = (
        'Retired evaluation: {"run_id":"2026-08-24-'
        '01a032f5-c64c-7ad2-a838-8eb738d99824"} commit `4dc3fb851`'
    )

    assert sha_candidates(line) == ["4dc3fb851"]


def test_malformed_uuid_components_remain_commit_candidates() -> None:
    from scripts.artifact_referents import sha_candidates

    assert sha_candidates("2026-08-24-01a032f5-c64c-7ad2-a838-8eb738d9982") == [
        "01a032f5",
        "8eb738d9982",
    ]


def test_a_uuid_component_repeated_outside_the_uuid_remains_a_candidate() -> None:
    from scripts.artifact_referents import sha_candidates

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
# End to end
# --------------------------------------------------------------------------


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GATE), "--repo-root", str(ROOT), *args],
        capture_output=True, text=True, timeout=180,
    )


def test_the_gate_blocks_on_a_dated_artifact_with_a_bad_referent(tmp_path: Path) -> None:
    artifact = tmp_path / "2026-08-25-control.md"
    artifact.write_text("Structural follow-up: issue #N (novel: x)\n", encoding="utf-8")

    result = _run("--path", str(artifact))

    assert result.returncode == 1
    assert "unresolvable-issue-ref" in result.stdout


def test_the_gate_passes_the_same_artifact_once_repaired(tmp_path: Path) -> None:
    artifact = tmp_path / "2026-08-25-control.md"
    artifact.write_text("Structural follow-up: issue #700 (novel: x)\n", encoding="utf-8")

    result = _run("--path", str(artifact))

    assert result.returncode == 0
    assert "status: clean" in result.stdout


def test_an_out_of_tree_path_does_not_crash_the_gate(tmp_path: Path) -> None:
    """`Path.relative_to` RAISES on a path outside the root rather than
    returning something, and a checker that crashes on an out-of-tree input is
    one whose negative control cannot be written. Found while writing that
    control."""
    # The fixture must PRODUCE A FINDING: `_display_path` is only reached while
    # constructing one, so a clean fixture never exercises the ValueError this
    # test is named for. A reviewer caught the earlier version passing for the
    # wrong reason.
    artifact = tmp_path / "2026-08-25-outside.md"
    artifact.write_text("Structural follow-up: issue #N (novel: x)\n", encoding="utf-8")

    result = _run("--path", str(artifact))

    assert "Traceback" not in result.stderr
    assert result.returncode == 1
    assert str(artifact) in result.stdout


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
    grandfathered = int(re.search(r"grandfathered \(reported, not rewritten\): (\d+)", result.stdout).group(1))

    assert scanned > 500, "the corpus collapsed; a clean verdict here proves nothing"
    assert dispositions > 100, "the disposition regex stopped matching corpus-wide"
    assert grandfathered > 0, "frozen history should be reported, not silently absent"


# --------------------------------------------------------------------------
# The enforcement asymmetry -- had ZERO tests until a reviewer said so
# --------------------------------------------------------------------------


def test_an_undatable_artifact_is_fail_closed_for_issue_refs(tmp_path: Path) -> None:
    """`#N` was never valid, so an undated filename must not buy an exemption."""
    artifact = tmp_path / "recent-lessons.md"
    artifact.write_text("Structural follow-up: issue #N (novel: x)\n", encoding="utf-8")

    result = _run("--path", str(artifact))

    assert result.returncode == 1
    assert "unresolvable-issue-ref" in result.stdout


def test_an_undatable_artifact_is_NOT_fail_closed_for_shas(tmp_path: Path) -> None:
    """The asymmetry. A SHA can be correct when written and stop resolving when
    history is rewritten, so blocking an undated rolling digest would punish an
    author for a change made after they wrote it -- and the only remedy would be
    editing frozen memory so a checker goes green."""
    artifact = tmp_path / "recent-lessons.md"
    artifact.write_text("landed at `deadbee1234`\n", encoding="utf-8")

    result = _run("--path", str(artifact))

    # Assert the COUNT, not the label. `grandfathered (reported, not rewritten):`
    # prints unconditionally, so `"grandfathered" in stdout` passed with zero
    # findings, with a broken SHA_RE, and with the fixture never opened -- the
    # render-identically-either-way shape this gate refuses, reintroduced by the
    # repair that added these very tests.
    assert result.returncode == 0
    assert "grandfathered (reported, not rewritten): 1" in result.stdout
    assert "non-durable-commit-ref" in result.stdout


def test_a_pre_cutoff_artifact_reports_without_blocking(tmp_path: Path) -> None:
    artifact = tmp_path / "2026-01-01-frozen.md"
    artifact.write_text("Structural follow-up: issue #N (novel: x)\n", encoding="utf-8")

    result = _run("--path", str(artifact))

    assert result.returncode == 0
    assert "grandfathered (reported, not rewritten): 1" in result.stdout


# --------------------------------------------------------------------------
# A clean verdict must mean "nothing was wrong", never "nothing was looked at"
# --------------------------------------------------------------------------


def test_a_path_that_does_not_exist_is_an_input_error_not_a_pass() -> None:
    """`scanned` used to count a file the gate never opened, so a typo in a
    wiring line was indistinguishable from a passing run."""
    result = _run("--path", "/tmp/definitely-not-here-9f3a.md")

    assert result.returncode == 1
    assert "UNREADABLE" in result.stdout


def test_a_directory_argument_is_an_input_error_not_a_pass(tmp_path: Path) -> None:
    result = _run("--path", str(tmp_path))

    assert result.returncode == 1
    assert "UNREADABLE" in result.stdout


def test_an_empty_corpus_blocks_rather_than_reporting_clean(tmp_path: Path) -> None:
    """Both adjacent gates in run-quality.sh carry an empty-corpus guard. Without
    one, a renamed artifact directory reads as a pass."""
    result = subprocess.run(
        [sys.executable, str(GATE), "--repo-root", str(tmp_path)],
        capture_output=True, text=True, timeout=60,
    )

    assert result.returncode == 1
    assert "EMPTY CORPUS" in result.stdout


def test_the_exit_code_follows_the_printed_status() -> None:
    """The status line and the exit code must not disagree: the runner believes
    the code and the human believes the message. An earlier version printed
    `status: blocked` and exited 0."""
    result = _run("--path", "/tmp/definitely-not-here-9f3a.md")

    assert ("status: blocked" in result.stdout) == (result.returncode == 1)


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
    from scripts.artifact_referents import ResolverUnavailable, git_commit_reachable_from_head

    assert git_commit_reachable_from_head("96ba78f7f", ROOT) is True
    with pytest.raises(ResolverUnavailable):
        git_commit_reachable_from_head("96ba78f7f", Path("/tmp"))


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _build_side_branch_repo_seed(seed: Path) -> None:
    repo = seed / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Charness Test")
    _git(repo, "config", "user.email", "charness-test@example.invalid")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "base.txt")
    _git(repo, "commit", "-m", "base")
    _git(repo, "switch", "-c", "local-lane")
    (repo / "lane.txt").write_text("local\n", encoding="utf-8")
    _git(repo, "add", "lane.txt")
    _git(repo, "commit", "-m", "local lane")
    local_sha = _git(repo, "rev-parse", "HEAD")
    _git(repo, "switch", "main")
    (seed / "side-branch-commit").write_text(f"{local_sha}\n", encoding="utf-8")


def _repo_with_side_branch_commit(tmp_path: Path) -> tuple[Path, str]:
    from tests.seed_cache import get_or_build

    seed = get_or_build(
        "artifact-referents-side-branch-repo-seed", _build_side_branch_repo_seed
    )
    repo = shutil.copytree(seed / "repo", tmp_path / "repo")
    local_sha = (seed / "side-branch-commit").read_text(encoding="utf-8").strip()
    return repo, local_sha


def test_side_branch_seed_copies_are_private(tmp_path: Path) -> None:
    from scripts.artifact_referents import git_commit_reachable_from_head

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


def test_an_object_visible_only_on_a_side_branch_is_not_durable(tmp_path: Path) -> None:
    """Same tracked HEAD must answer identically in a clean and authoring clone."""
    from scripts.artifact_referents import git_commit_reachable_from_head

    repo, local_sha = _repo_with_side_branch_commit(tmp_path)

    assert _git(repo, "cat-file", "-t", local_sha) == "commit"
    assert git_commit_reachable_from_head(local_sha, repo) is False


def test_absent_and_noncommit_objects_are_typed_negative(tmp_path: Path) -> None:
    from scripts.artifact_referents import git_commit_reachable_from_head

    repo, _local_sha = _repo_with_side_branch_commit(tmp_path)
    blob_sha = _git(repo, "rev-parse", "HEAD:base.txt")

    assert git_commit_reachable_from_head("deadbee1234", repo) is False
    assert git_commit_reachable_from_head(blob_sha, repo) is False


def test_shallow_history_is_unestablished_not_a_missing_commit(tmp_path: Path) -> None:
    from scripts.artifact_referents import ResolverUnavailable, reachable_head_commits

    repo, _local_sha = _repo_with_side_branch_commit(tmp_path)
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "--depth=1", f"file://{repo}", str(shallow)],
        capture_output=True, text=True, check=True,
    )

    with pytest.raises(ResolverUnavailable, match="shallow"):
        reachable_head_commits(shallow)


def test_failed_head_ancestry_read_is_unestablished(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.artifact_referents import ResolverUnavailable, reachable_head_commits

    results = iter(
        [
            subprocess.CompletedProcess([], 0, "false\n", ""),
            subprocess.CompletedProcess([], 2, "", "rev-list failed"),
        ]
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: next(results))

    with pytest.raises(ResolverUnavailable, match="rev-list failed"):
        reachable_head_commits(ROOT)


def test_exact_local_context_declaration_is_visible_and_stale_checked(tmp_path: Path) -> None:
    import hashlib
    import json

    repo, local_sha = _repo_with_side_branch_commit(tmp_path)
    artifact_rel = "charness-artifacts/goals/2026-08-30-local-context.md"
    artifact = repo / artifact_rel
    artifact.parent.mkdir(parents=True)
    line = f"local lane `{local_sha[:10]}`"
    artifact.write_text(f"{line}\n", encoding="utf-8")
    declarations = repo / "scripts" / "artifact-referent-local-context.json"
    declarations.parent.mkdir()
    entry = {
        "artifact": artifact_rel,
        "line": 1,
        "token": local_sha[:10],
        "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
        "reason": "frozen local shaping context",
    }
    declarations.write_text(json.dumps([entry]), encoding="utf-8")
    _git(repo, "add", str(declarations.relative_to(repo)))
    command = [
        sys.executable, str(GATE), "--repo-root", str(repo), "--path", artifact_rel,
    ]

    accepted = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert accepted.returncode == 0, accepted.stdout
    assert "declared local context (reported, exact): 1" in accepted.stdout
    assert "declared-local-commit-ref" in accepted.stdout

    artifact.write_text(f"changed context, same token `{local_sha[:10]}`\n", encoding="utf-8")
    changed_line = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert changed_line.returncode == 1
    assert "stale-local-context-declaration" in changed_line.stdout
    artifact.write_text(f"{line}\n", encoding="utf-8")

    entry["line"] = 2
    declarations.write_text(json.dumps([entry]), encoding="utf-8")
    _git(repo, "add", str(declarations.relative_to(repo)))
    stale = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert stale.returncode == 1
    assert "stale-local-context-declaration" in stale.stdout
    assert "non-durable-commit-ref" in stale.stdout


@pytest.mark.parametrize(
    "mutation",
    [
        {"reason": ""},
        {"line": 0},
        {"token": "not-a-sha"},
        {"line_sha256": "not-a-fingerprint"},
        {"extra": "second owner"},
    ],
)
def test_malformed_local_context_declarations_block(
    tmp_path: Path, mutation: dict[str, object]
) -> None:
    import hashlib
    import json

    repo, local_sha = _repo_with_side_branch_commit(tmp_path)
    artifact_rel = "charness-artifacts/goals/2026-08-30-local-context.md"
    artifact = repo / artifact_rel
    artifact.parent.mkdir(parents=True)
    line = f"local lane `{local_sha[:10]}`"
    artifact.write_text(f"{line}\n", encoding="utf-8")
    declarations = repo / "scripts" / "artifact-referent-local-context.json"
    declarations.parent.mkdir()
    entry: dict[str, object] = {
        "artifact": artifact_rel,
        "line": 1,
        "token": local_sha[:10],
        "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
        "reason": "why",
    }
    entry.update(mutation)
    declarations.write_text(json.dumps([entry]), encoding="utf-8")
    _git(repo, "add", str(declarations.relative_to(repo)))

    result = subprocess.run(
        [sys.executable, str(GATE), "--repo-root", str(repo), "--path", artifact_rel],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 1
    assert "malformed-local-context-declaration" in result.stdout


def test_untracked_local_context_declaration_cannot_change_the_verdict(tmp_path: Path) -> None:
    import hashlib
    import json

    repo, local_sha = _repo_with_side_branch_commit(tmp_path)
    artifact_rel = "charness-artifacts/goals/2026-08-30-local-context.md"
    artifact = repo / artifact_rel
    artifact.parent.mkdir(parents=True)
    line = f"local lane `{local_sha[:10]}`"
    artifact.write_text(f"{line}\n", encoding="utf-8")
    declarations = repo / "scripts" / "artifact-referent-local-context.json"
    declarations.parent.mkdir()
    declarations.write_text(json.dumps([{
        "artifact": artifact_rel,
        "line": 1,
        "token": local_sha[:10],
        "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
        "reason": "unreviewed local bytes",
    }]), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(GATE), "--repo-root", str(repo), "--path", artifact_rel],
        capture_output=True, text=True, timeout=60,
    )
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


def test_declaration_index_read_error_blocks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.check_artifact_referents import load_local_context_declarations

    repo, _data = _declaration_bytes(tmp_path, [_valid_declaration()])

    def fail_index_read(*args, **kwargs):
        raise OSError("index unavailable")

    monkeypatch.setattr("scripts.check_artifact_referents.subprocess.run", fail_index_read)
    declarations, defects = load_local_context_declarations(repo)

    assert declarations == []
    assert defects[0]["kind"] == "unbound-local-context-declaration"
    assert "index unavailable" in str(defects[0]["detail"])


@pytest.mark.parametrize(
    ("raw", "expected_kind"),
    [
        (b"{not json", "malformed-local-context-declaration"),
        (None, "malformed-local-context-declaration"),
        ("duplicate", "duplicate-local-context-declaration"),
    ],
)
def test_invalid_declaration_file_shapes_block(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    raw: bytes | None | str,
    expected_kind: str,
) -> None:
    from scripts.check_artifact_referents import load_local_context_declarations

    if raw == "duplicate":
        payload: object = [_valid_declaration(), _valid_declaration()]
        repo, data = _declaration_bytes(tmp_path, payload)
    elif raw is None:
        repo, data = _declaration_bytes(tmp_path, _valid_declaration())
    else:
        repo = tmp_path / "repo"
        path = repo / "scripts/artifact-referent-local-context.json"
        path.parent.mkdir(parents=True)
        path.write_bytes(raw)
        data = raw

    indexed = subprocess.CompletedProcess([], 0, data, b"")
    monkeypatch.setattr(
        "scripts.check_artifact_referents.subprocess.run", lambda *args, **kwargs: indexed
    )
    declarations, defects = load_local_context_declarations(repo)

    if raw == "duplicate":
        assert declarations == [_valid_declaration()]
    else:
        assert declarations == []
    assert expected_kind in [str(defect["kind"]) for defect in defects]


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


@pytest.mark.parametrize(
    "documentation",
    [
        "the floor accepts `applied: <what>` / `issue #N` / `none — <reason>`",
        "(`issue #N`/`applied:`/`accepted-risk:`/`out-of-scope:`) accepts it.",
    ],
)
def test_the_gate_can_be_documented_inside_its_own_corpus(documentation: str) -> None:
    """Otherwise the next retro explaining this gate is its own first false
    positive. The discriminator is ENUMERATION, not backticks -- the real v6.3.0
    defect was itself inside a code span."""
    assert check_disposition_referents(documentation, ROOT) == []


@pytest.mark.parametrize(
    "real_defect",
    [
        "Decision: `issue #N (recurs: the release flow already solves this)`",
        "Structural follow-up: issue #N (novel: something specific)",
        "- **applied**: issue #N",
    ],
)
def test_a_committed_disposition_is_still_caught_inside_backticks(real_defect: str) -> None:
    """A backtick exemption would have exempted the exact defect this exists for."""
    assert len(check_disposition_referents(real_defect, ROOT)) == 1


@pytest.mark.parametrize(
    "spelling",
    [
        "Disposition: **applied** — see scripts/does_not_exist_here.py",
        "- **applied**: scripts/does_not_exist_here.py",
    ],
)
def test_this_repos_other_disposition_spellings_are_seen(spelling: str) -> None:
    """`Disposition:` appears 75 times across 28 checked-in goals, and `**applied**`
    puts bold markers between the word and the colon."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("gate", GATE)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)

    assert gate.disposition_lines(spelling) != []


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


def test_a_refusing_resolver_exits_unestablished_not_pass(tmp_path: Path) -> None:
    """The B3 repair turned a false-positive storm into a SILENT false negative:
    the gate exited 0, run-quality printed PASS, and the passing phase's log --
    carrying the only explanation -- is deleted at EXIT. Exit 3 is the runner's
    own byte for "ran, established nothing"."""
    artifact = tmp_path / "2026-08-25-nogit.md"
    artifact.write_text("landed at `deadbee1234`\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(GATE), "--repo-root", str(tmp_path), "--path", str(artifact)],
        capture_output=True, text=True, timeout=60,
    )

    assert result.returncode == 3, result.stdout
    assert "WARNING" in result.stdout, "run-quality only prints a passing gate's log on this token"
    assert "STOOD DOWN" in result.stdout


def test_shas_resolved_counts_tokens_not_lines() -> None:
    """M1: the counter incremented once per LINE, so it stayed at the corpus
    line count even if SHA_RE stopped matching entirely -- structurally unable
    to show the collapse it was added to detect."""
    from scripts.artifact_referents import sha_candidates

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


def test_git_failing_to_run_at_all_raises_rather_than_answering() -> None:
    """The OSError arm. A missing or unexecutable git is "cannot answer", not
    "this SHA is absent" -- answering would report every SHA in the corpus as
    unresolvable."""
    from scripts.artifact_referents import ResolverUnavailable, git_commit_reachable_from_head

    with pytest.raises(ResolverUnavailable):
        git_commit_reachable_from_head("96ba78f7f", Path("/nonexistent-root-9f3a/deeper"))

    # And the OSError arm specifically: git absent from PATH entirely.
    import subprocess as _sp

    def _boom(*args, **kwargs):
        raise OSError("no git here")

    real = _sp.run
    _sp.run = _boom
    try:
        with pytest.raises(ResolverUnavailable, match="could not be run"):
            git_commit_reachable_from_head("96ba78f7f", ROOT)
    finally:
        _sp.run = real


def test_an_inconsistent_quantity_is_reported_with_its_first_site(tmp_path: Path) -> None:
    """The quantity findings are assembled in the gate, not the library, and
    that assembly had no test: the release gate named both of its lines
    uncovered."""
    artifact = tmp_path / "2026-08-25-quantities.md"
    artifact.write_text(
        "Found {{q:total=27}} blockers.\n\nOf the {{q:total=21}} above ...\n", encoding="utf-8"
    )

    result = _run("--path", str(artifact))

    assert result.returncode == 1
    assert "inconsistent-quantity" in result.stdout
    assert ":1 " in result.stdout, "should anchor on the FIRST site"
