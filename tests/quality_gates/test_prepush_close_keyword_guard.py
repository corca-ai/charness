"""The blocking pre-push floor over close keywords a push RANGE would fire.

The regression this file exists for is a real irreversible act, not a hypothetical:
a commit body wrapped the sentence "... because S7 closes\n#626/#627/#631 ..." so the
refs landed on a line beginning with `#`. The commit-msg carrier strips `^\\s*#` lines
as git comments -- right for an editor message, wrong for the `-m` message actually
stored -- so it scanned text the repository never held, reported `not_applicable`, and
GitHub read the stored message and closed #626.

Two surfaces are pinned here. The guard, which reads stored messages and so has no
model of git's cleanup to be wrong about, and the carrier's own repair.
"""

from __future__ import annotations

import importlib
import io
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.closeout_authorization_world import CROSSWALK_REL, PROTECTED, build_protected_world
from tests.quality_gates.prepush_close_keyword_fixtures import (
    commit as _commit,
)
from tests.quality_gates.prepush_close_keyword_fixtures import (
    git as _git,
)
from tests.quality_gates.prepush_close_keyword_fixtures import (
    head as _head,
)
from tests.quality_gates.prepush_close_keyword_fixtures import (
    repo_seed as prepush_close_keyword_seed,
)
from tests.quality_gates.prepush_close_keyword_fixtures import (
    tree_snapshot as _tree_snapshot,
)
from tests.quality_gates.support import ROOT
from tests.script_main import load_script_module, run_loaded_script_main

GUARD = load_script_module(
    "prepush_close_keyword_guard", ROOT / "scripts" / "prepush_close_keyword_guard.py"
)
# The reading half: range resolution and close-keyword detection. Addressed directly
# rather than through the guard's re-export, because a `monkeypatch` of the guard's
# imported copy would not reach the module that actually reads the constant.
# Imported under the package name the guard itself imports. Loading it by path under
# a different module name produced a SECOND module object, so a `monkeypatch` here
# left the copy the guard actually calls untouched and the test asserted nothing.
SCAN = importlib.import_module("scripts.prepush_close_keyword_scan")
CARRIER = load_script_module(
    "check_issue_closeout_commit_msg_for_guard_tests",
    ROOT / "scripts" / "gates" / "check_issue_closeout_commit_msg.py",
)
ZERO = "0" * 40

# Close verb on one line, issue ref starting the next with `#`. Slash is not
# GitHub's comma grammar, so only the first number is a close target.
WRAPPED_HASH_REF = "closes\n#42/#43/#44 on the strength of that gate.\n"
REFUSED_CLOSE = "Closes #42.\n"

BODY_VALID_CLOSEOUT = "\n\n".join(
    [
        "fix(release): close #42 — the resume lane runs the notes-file preflight",
        "JTBD: resolve GitHub issues end-to-end.",
        "Root cause: the issue closeout carrier was prose-only.",
        "Debug artifact: charness-artifacts/debug/latest.md.",
        "Siblings: issue closeout | decision: same carrier bug | proof: commit-msg hook.",
        "Prevention: commit-msg blocks missing closeout carriers.",
        "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
        "Behavior #42: behavior test exercises the fix (distinct channel from CLOSED)",
        "Probe record #42: local-only-by-contract",
        "AI-provenance: agent-drafted; human-audited per the resolution critique",
    ]
)


@pytest.fixture
def repo(tmp_path: Path, repo_seed: Path) -> Path:
    shutil.copytree(repo_seed, tmp_path, dirs_exist_ok=True)
    return tmp_path


@pytest.fixture(scope="session")
def repo_seed() -> Path:
    return prepush_close_keyword_seed()


def test_cached_repo_seed_is_never_mutated_by_a_test_clone(tmp_path: Path, repo_seed: Path) -> None:
    before_seed = _tree_snapshot(repo_seed)
    clone = tmp_path / "clone"
    shutil.copytree(repo_seed, clone)

    _commit(clone, "docs: mutate only the disposable clone\n", "clone-only.txt")

    assert _tree_snapshot(repo_seed) == before_seed


def test_head_reads_the_checked_out_commit_from_git_files(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git_verbs: list[str] = []
    original = subprocess.run

    def wrapped(argv: object, *args: object, **kwargs: object) -> object:
        if isinstance(argv, (list, tuple)) and argv and Path(str(argv[0])).name == "git":
            git_verbs.append(str(argv[1]))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", wrapped)
    sha = _head(repo)
    assert sha == (repo / ".git" / "refs" / "heads" / "main").read_text(encoding="ascii").strip()
    assert git_verbs == []


def _finding(repo: Path, body: str, files: dict[str, str] | None = None) -> dict | None:
    """Classify one already-observed stored message and tree, without a unique commit."""
    planted = files or {}
    verify = CARRIER._load_issue_verify_closeout()
    return GUARD._judge(
        repo,
        "corca-ai/charness",
        "a" * 40,
        CARRIER,
        verify,
        body=body,
        list_paths=lambda _root: list(planted),
        read_file=lambda _root, path: planted[path],
    )


def _run(*args: str, stdin: str | None = None) -> tuple[int, dict]:
    saved = sys.stdin
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        result = run_loaded_script_main("prepush_close_keyword_guard.py", GUARD, *args)
    finally:
        sys.stdin = saved
    return result.returncode, yaml.safe_load(result.stdout or "{}")


# --- the regression: what the guard must refuse -----------------------------------


def test_refuses_a_close_keyword_whose_issue_ref_starts_a_hash_line(repo: Path) -> None:
    base = _head(repo)
    head = _commit(repo, WRAPPED_HASH_REF, "work.txt")

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 1
    assert payload["status"] == "refused"
    finding = payload["close_keyword_commits"][0]
    assert finding["commit"] == head
    assert finding["numbers"] == [42]
    assert finding["ok"] is False
    assert "not undoable" in payload["summary"]
    assert "reword" in payload["remediation"]
    assert GUARD.cli(["--repo-root", str(repo), "--range", f"{base}..{head}"]) == 1


def test_a_close_keyword_with_a_valid_closeout_ledger_passes(repo: Path) -> None:
    finding = _finding(repo, BODY_VALID_CLOSEOUT)
    assert finding is not None
    assert finding["ok"] is True
    assert finding["numbers"] == [42]


def test_a_range_with_no_close_keyword_is_not_applicable(repo: Path) -> None:
    assert _finding(repo, "docs: ordinary commit about issue 42\n") is None


def test_a_close_keyword_qualified_to_another_repo_is_not_a_target(repo: Path) -> None:
    # GitHub cannot close a foreign issue from here, so no LEDGER floor applies and
    # the push is not refused: folding it in would refuse over an impossible close
    # while pushing the author toward the unqualified form that would close THIS
    # repo's #77.
    finding = _finding(repo, "fix: closes acme/other-repo#77 upstream\n")
    assert finding is not None
    # The commit IS still carried into the finding, with no ledger report, because
    # protected-target authorization has to see a foreign target to refuse it --
    # dropping the ref before authorization ran was a measured escape.
    assert finding["numbers"] == [77]
    assert finding["reports"] == []
    assert finding["closeout_authorization"]["authorized"] is True


# --- range resolution -------------------------------------------------------------


def test_a_ref_deletion_lands_no_commits_and_scans_none(repo: Path) -> None:
    head = _head(repo)
    assert SCAN.range_commits(repo, ZERO, head) == []


def test_a_ref_with_no_local_sha_is_skipped_without_resolving_a_range(repo: Path) -> None:
    """`evaluate` is exported and ships to consuming repos, so a hook shim calling it
    directly is a real caller, and that is the only caller this guard is reachable from.
    `parse_push_stdin` CAN emit an empty `local_sha` -- its all-dropped sentinel sets all
    four fields empty, pinned by `test_parses_the_pre_push_stdin_grammar...` below -- but
    that sentinel always carries `dropped_lines > 0`, and `evaluate` returns the
    no-verdict payload before the loop on any drop, so it never reaches here. `--range`
    refuses an empty side outright.

    The remote sha is deliberately BEHIND head with a commit in between, and that is the
    whole test. `range_commits` interpolates the empty local sha on the RIGHT
    (`f"{remote_sha}..{local_sha}"`), and git reads a missing right side as `HEAD` and
    exits 0 -- so with the remote sha at head, deleting the skip scans an empty range and
    every assertion here still passes. With the remote sha behind, deleting it scans the
    commits between, which the count below refuses. An empty local sha names no commit and
    proposes no landing, so judging anything for that ref is judging commits it never
    offered.
    """
    base = _head(repo)
    head = _commit(repo, "docs: a commit the empty-sha ref never proposed to land\n", "later.txt")
    refs = [
        {"local_ref": "", "local_sha": "", "remote_ref": "refs/heads/main", "remote_sha": base},
        {
            "local_ref": "refs/heads/main",
            "local_sha": head,
            "remote_ref": "refs/heads/main",
            "remote_sha": head,
        },
    ]

    payload = GUARD.evaluate(repo, refs, "corca-ai/charness", "origin")

    assert payload["ok"] is True
    assert payload["status"] == "not_applicable"
    assert payload["commits_scanned"] == 0, (
        "the empty-sha ref must contribute no commits, and the second ref is already at "
        "the remote; a nonzero count here means the skip was removed and `base..HEAD` "
        "was resolved for a ref that proposed nothing"
    )


@pytest.mark.boundary_contract(
    reason="exercise close-keyword range resolution against real git refs and commits"
)
def test_a_new_ref_is_bounded_by_what_origin_already_has(repo: Path, tmp_path: Path) -> None:
    origin = tmp_path.parent / "origin.git"
    _git(repo, "init", "--bare", str(origin))
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "--no-verify", "origin", "main")
    published = _head(repo)
    _git(repo, "checkout", "-q", "-b", "feature")
    unpublished = _commit(repo, "docs: unpublished\n", "feature.txt")

    commits = SCAN.range_commits(repo, unpublished, ZERO)

    # The commit origin already carries is NOT re-judged; only the unpublished one is.
    # Falling back to full history here would make the guard's cost unbounded on a
    # fresh branch, which is how a guard gets disabled.
    assert commits == [unpublished]
    assert published not in commits


def test_an_unreadable_range_exits_two_rather_than_zero(repo: Path) -> None:
    code, payload = _run("--repo-root", str(repo), "--range", f"{ZERO}..deadbeef")

    # 2, never 0: the guard judged nothing, and an unusable run must not be readable
    # as a pass at an irreversible boundary.
    assert code == GUARD.NO_VERDICT_EXIT
    assert payload["status"] == "no-verdict"


def test_an_unparseable_range_argument_exits_two(repo: Path) -> None:
    code, _ = _run("--repo-root", str(repo), "--range", "not-a-range")
    assert code == GUARD.NO_VERDICT_EXIT


# --- git's pre-push stdin ---------------------------------------------------------


def test_parses_the_pre_push_stdin_grammar_and_drops_malformed_lines() -> None:
    refs = SCAN.parse_push_stdin(
        "refs/heads/main aaa refs/heads/main bbb\n"
        "\n"
        "garbage line\n"
        "refs/heads/topic ccc refs/heads/topic ddd\n"
    )
    assert [ref["local_sha"] for ref in refs] == ["aaa", "ccc"]
    assert [ref["remote_sha"] for ref in refs] == ["bbb", "ddd"]


def test_reads_the_range_from_stdin_and_refuses(repo: Path) -> None:
    base = _head(repo)
    head = _commit(repo, REFUSED_CLOSE, "work.txt")

    code, payload = _run(
        "--repo-root", str(repo), stdin=f"refs/heads/main {head} refs/heads/main {base}\n"
    )

    assert code == 1
    assert payload["close_keyword_commits"][0]["numbers"] == [42]


def test_a_commit_reachable_from_two_pushed_refs_is_judged_once(repo: Path) -> None:
    base = _head(repo)
    head = _commit(repo, REFUSED_CLOSE, "work.txt")
    _git(repo, "branch", "mirror", head)

    code, payload = _run(
        "--repo-root",
        str(repo),
        stdin=(
            f"refs/heads/main {head} refs/heads/main {base}\n"
            f"refs/heads/mirror {head} refs/heads/mirror {base}\n"
        ),
    )

    assert code == 1
    # One finding, not two. A duplicated finding reads as two separate accidental
    # closes and inflates what the operator thinks they are looking at.
    assert len(payload["close_keyword_commits"]) == 1
    assert payload["commits_scanned"] == 1


def test_no_refs_on_stdin_is_reported_as_no_refs(repo: Path) -> None:
    code, payload = _run("--repo-root", str(repo), stdin="")
    assert code == 0
    assert payload["status"] == "no-refs"


# --- the carrier repair (the root cause of the #626 close) ------------------------


def test_the_carrier_now_sees_a_close_keyword_whose_ref_line_starts_with_hash(
    tmp_path: Path,
) -> None:
    message = tmp_path / "message.txt"
    message.write_text(WRAPPED_HASH_REF, encoding="utf-8")
    report = CARRIER.evaluate(
        tmp_path,
        message,
        "corca-ai/charness",
        list_paths=lambda _root: [],
        read_file=lambda _root, path: "",
    )
    payload = CARRIER.report_payload(report)

    assert report["ok"] is False
    assert payload["bare_close_numbers"] == [42]


def test_the_carrier_scan_text_keeps_both_bodies() -> None:
    raw = "feat: work\n\n# not a git comment, it is the ref line\n"
    sanitized = CARRIER._strip_commit_comments(raw)
    scan = CARRIER._close_keyword_scan_text(raw, sanitized)

    # Both halves, not the raw one alone: the sanitized body is still what the ledger
    # floors parse, and a scan that dropped it would change which fields are read.
    assert "# not a git comment" in scan
    assert sanitized in scan


def test_a_git_comment_block_alone_does_not_trigger_the_carrier(tmp_path: Path) -> None:
    message = tmp_path / "message.txt"
    message.write_text(
        "docs: ordinary commit\n"
        "\n"
        "# Please enter the commit message for your changes. Lines starting\n"
        "# with '#' will be ignored, and an empty message aborts the commit.\n"
        "#\n"
        "# On branch main\n"
        "# Changes to be committed:\n"
        "#\tmodified:   scripts/gates/check_issue_closeout_commit_msg.py\n",
        encoding="utf-8",
    )
    report = CARRIER.evaluate(
        tmp_path,
        message,
        "corca-ai/charness",
        list_paths=lambda _root: [],
        read_file=lambda _root, path: "",
    )

    # Honest about its own strength: this arm kills no mutant of the widening, because
    # it also passes with the widening reverted. It constrains a FUTURE edit that
    # widens detection far enough to catch git's own template, which is the realistic
    # shape of a false refusal here. Do not count it as coverage of the repair.
    assert report["ok"] is True
    assert report["status"] == "not_applicable"


# --- what round 1 of the bounded review found ------------------------------------


QUESTION_ARTIFACT = (
    "# Closeout for #700\n"
    "\n"
    "Closes #700\n"
    "\n"
    "Classification: question\n"
    "\n"
    "Answer: the lane already behaves this way; nothing to repair.\n"
    "\n"
    "AI-provenance: agent-drafted; human-audited\n"
)


QUESTION_MESSAGE = (
    "docs: answer #700\n"
    "\n"
    "Closes #700\n"
    "\n"
    "JTBD: answer the operator's question about the lane.\n"
    "\n"
    "Answer: the lane already behaves this way; nothing to repair.\n"
    "\n"
    "AI-provenance: agent-drafted; human-audited\n"
)


def test_a_classification_declared_only_in_the_artifact_is_honored(repo: Path) -> None:
    """The guard must read the commit's TREE, not just its message.

    Re-deriving classification from the message alone defaults to `bug`, so this
    commit was refused with a demand for `Root cause:` / `Prevention:` / `Behavior
    #700:` -- fabricating exactly the repair claims a `question` disposition exists to
    refuse, on a commit the deployed commit-msg floor had already passed.
    """
    finding = _finding(
        repo,
        QUESTION_MESSAGE,
        {"charness-artifacts/issue/2026-08-16-issue-700-closeout.md": QUESTION_ARTIFACT},
    )
    assert finding is not None and finding["ok"] is True
    report = finding["reports"][0]
    assert report["classification"] == "question"
    assert report["source_artifact"].endswith("issue-700-closeout.md")


def test_the_same_message_without_the_artifact_is_classified_bug_and_refused(repo: Path) -> None:
    """The negative arm that makes the test above mean something.

    Byte-identical message, artifact removed: classification falls back to `bug` and
    the floor demands root-cause/prevention claims. Without this arm, the passing case
    above would also pass with the artifact parse deleted entirely.
    """
    finding = _finding(repo, QUESTION_MESSAGE)
    assert finding is not None and finding["ok"] is False
    report = finding["reports"][0]
    assert report["classification"] == "bug"
    assert report["source_artifact"] is None
    assert "root_cause" in report["missing_fields"]


def test_every_close_keyword_commit_carries_its_authorization_record(repo: Path) -> None:
    """The carrier's protected-target authorization runs here too.

    Omitting it was a false green with a concrete path: a `--no-verify` commit that
    close-keywords a crosswalk-protected issue WITH a complete ledger cleared this
    guard while the commit-msg carrier would have refused it. This repo's fixture has
    no crosswalk, so what is pinned is that the check RAN and its verdict is in the
    payload -- a payload without it cannot be audited after the fact.
    """
    finding = _finding(repo, BODY_VALID_CLOSEOUT)
    assert finding is not None
    authorization = finding["closeout_authorization"]
    assert "authorized" in authorization
    assert authorization["carrier_source"] == "commit-msg"


SCANNER = load_script_module(
    "issue_verify_closeout_body_for_guard_tests",
    ROOT / "skills" / "public" / "issue" / "scripts" / "issue_verify_closeout_body.py",
).iter_close_keyword_refs


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("fix: closes GH-700\n", [(None, 700)]),
        (
            "fix: closes https://github.com/corca-ai/charness/issues/700\n",
            [("corca-ai/charness", 700)],
        ),
        ("fix: closes #700\n", [(None, 700)]),
        # The comma-list form applies to every spelling, not only to `#N`. Reporting
        # only the first left the guard narrower than GitHub on the one surface whose
        # job is to be at least as wide.
        ("fix: closes GH-700, GH-701\n", [(None, 700), (None, 701)]),
        (
            "fix: closes #700, https://github.com/corca-ai/charness/issues/701\n",
            [(None, 700), ("corca-ai/charness", 701)],
        ),
        # Not a close: a bare mention cross-references on GitHub but closes nothing,
        # and refusing over it would stop every commit that cites an issue.
        ("fix: see GH-700 and https://github.com/corca-ai/charness/issues/701\n", []),
        # A word ending in `GH-`-like text must not bind.
        ("fix: closes HIGH-700\n", []),
        # A pull URL is not an issue URL.
        ("fix: closes https://github.com/corca-ai/charness/pull/700\n", []),
        # UNFILTERED by repo: authorization must see a foreign target to refuse it.
        ("fix: closes https://github.com/acme/other/issues/700\n", [("acme/other", 700)]),
        ("fix: closes acme/other#700\n", [("acme/other", 700)]),
    ],
)
def test_close_targets_covers_the_spellings_github_closes_on(body: str, expected: list) -> None:
    assert SCAN.close_targets(body, SCANNER) == expected


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("fix: closes GH-700\n", [(None, 700)]),
        (
            "fix: closes https://github.com/corca-ai/charness/issues/700\n",
            [("corca-ai/charness", 700)],
        ),
        ("fix: closes GH-700, GH-701\n", [(None, 700), (None, 701)]),
        ("fix: closes #700\n", [(None, 700)]),
        ("fix: see GH-700\n", []),
        ("fix: closes HIGH-700\n", []),
        ("fix: closes https://github.com/corca-ai/charness/pull/700\n", []),
        # The CASE axis, unpinned until a review round found it. The launch pattern is
        # case-insensitive and the ref extractor was not, so `gh-700` launched and then
        # extracted nothing: the scanner classified a span as a close and reported no
        # target for it. Unreachable while `#` -- which has no case -- was the only ref
        # literal, and reachable the moment `GH-`/`github.com` arrived on one side only.
        ("fix: closes gh-700\n", [(None, 700)]),
        ("fix: CLOSES Gh-700\n", [(None, 700)]),
        (
            "fix: closes https://GitHub.com/corca-ai/charness/issues/700\n",
            [("corca-ai/charness", 700)],
        ),
        (
            "fix: closes HTTPS://GITHUB.COM/corca-ai/charness/ISSUES/700\n",
            [("corca-ai/charness", 700)],
        ),
    ],
)
def test_the_canonical_scanner_itself_sees_every_spelling(body: str, expected: list) -> None:
    """The SHARED function, not the pre-push guard's private union over it.

    `GH-N` and the full issue URL were GitHub close spellings only the guard matched,
    so the commit-msg carrier, `verify_closeout`, and the release closeout message all
    scanned a body clean while GitHub closed an issue on it. Asserted directly against
    `iter_close_keyword_refs` because `close_targets` unions the guard's own copy over
    it -- reading the widening through that union would pass with the shared scanner
    still narrow, which is exactly the blindness under repair.
    """
    assert SCANNER(body) == expected


def test_local_numbers_is_what_narrows_to_this_repo() -> None:
    qualified = SCAN.close_targets("fix: closes #700, acme/other#701\n", SCANNER)
    # Two separate questions, deliberately: the LEDGER floor applies only to closes
    # GitHub can fire from here, but authorization is handed the unfiltered set --
    # filtering before it ran let a crosswalk-protected foreign target escape.
    assert qualified == [(None, 700), ("acme/other", 701)]
    assert SCAN.local_numbers(qualified, "corca-ai/charness") == {700}


def test_a_gh_dash_close_without_a_ledger_is_refused(repo: Path) -> None:
    finding = _finding(repo, "chore: tidy the lane\n\nIncidentally closes GH-700.\n")
    assert finding is not None and finding["ok"] is False
    assert finding["numbers"] == [700]


@pytest.mark.boundary_contract(
    reason="exercise close-keyword remote selection against real git remotes and refs"
)
def test_the_creation_arm_bounds_by_the_remote_actually_being_pushed_to(
    repo: Path, tmp_path: Path
) -> None:
    """`--remotes=origin` is a default, not an assumption.

    Hard-coding `origin` excluded commits the TARGET remote had never seen: pushing a
    new branch to `upstream` in a fork layout skipped every commit `origin` already
    carried, which is exactly the set under review.
    """
    origin = tmp_path.parent / "guard-origin.git"
    upstream = tmp_path.parent / "guard-upstream.git"
    _git(repo, "init", "--bare", str(origin))
    _git(repo, "init", "--bare", str(upstream))
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "remote", "add", "upstream", str(upstream))
    _git(repo, "push", "-q", "--no-verify", "origin", "main")
    on_origin_only = _commit(repo, "chore: pushed to the fork\n", "fork.txt")
    _git(repo, "push", "-q", "--no-verify", "origin", "main")
    _git(repo, "fetch", "-q", "origin")

    assert on_origin_only in SCAN.range_commits(repo, on_origin_only, ZERO, "upstream")
    assert on_origin_only not in SCAN.range_commits(repo, on_origin_only, ZERO, "origin")


@pytest.mark.boundary_contract(
    reason="exercise close-keyword fallback behavior against a real git remote without tracking refs"
)
def test_a_remote_with_no_tracking_refs_excludes_nothing(repo: Path, tmp_path: Path) -> None:
    """No exclusion, NOT "every remote-tracking ref".

    Falling back to `--remotes` is the false green itself: it excludes commits some
    OTHER remote carries and the target has never seen. Scanning the whole branch is
    the honest cost of not being able to ask the target anything.
    """
    origin = tmp_path.parent / "guard-fallback.git"
    _git(repo, "init", "--bare", str(origin))
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "--no-verify", "origin", "main")
    _git(repo, "fetch", "-q", "origin")
    published = _head(repo)

    # A `rev-list --count` probe answers `0` (exit 0) for a pattern matching no refs,
    # so it reports every remote name as usable and this branch would never be taken.
    assert SCAN._published_exclusions(repo, "no-such-remote") == []
    assert published in SCAN.range_commits(repo, published, ZERO, "no-such-remote")


def test_dropped_stdin_lines_are_counted_rather_than_absorbed() -> None:
    refs = SCAN.parse_push_stdin("garbage\nrefs/heads/main aaa refs/heads/main bbb\n")
    assert refs[0]["dropped_lines"] == 1

    only_garbage = SCAN.parse_push_stdin("garbage\nmore garbage\n")
    # A malformed-only stdin must not read as "nothing to push": the payload has to
    # carry a nonzero drop count so `commits_scanned: 0` is not mistaken for coverage.
    assert only_garbage[0]["dropped_lines"] == 2
    assert only_garbage[0]["local_sha"] == ""


@pytest.mark.boundary_contract(
    reason="assert the close-keyword guard's exact crash exit and stderr contract from a partial installed layout"
)
def test_a_crash_exits_two_rather_than_the_refusal_code(repo: Path, tmp_path: Path) -> None:
    """A partial install (scripts without the issue skill) must not report a verdict.

    `main` catches only `RangeUnreadable`; everything else would leave Python's own
    exit 1, which is this guard's documented REFUSAL code. The operator would then
    reword an innocent commit message to answer a crash.
    """
    lonely = tmp_path.parent / "guard-lonely" / "scripts"
    lonely.mkdir(parents=True, exist_ok=True)
    for name in (
        "prepush_close_keyword_guard.py",
        "prepush_close_keyword_scan.py",
        "check_issue_closeout_commit_msg.py",
        "commit_msg_closeout_authorization.py",
        "runtime_bootstrap.py",
        "yaml_output.py",
    ):
        shutil.copy2(ROOT / "scripts" / name, lonely / name)
    base = _head(repo)
    head = _commit(repo, "chore: extra commit\n", "work.txt")

    result = subprocess.run(
        [
            sys.executable,
            str(lonely / "prepush_close_keyword_guard.py"),
            "--repo-root",
            str(repo),
            "--range",
            f"{base}..{head}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == GUARD.NO_VERDICT_EXIT, result.stdout + result.stderr
    assert "crashed" in result.stderr


# --- what round 2 of the bounded review found ------------------------------------


def test_a_commit_that_only_edits_a_closeout_artifact_is_not_a_close(repo: Path) -> None:
    """A close KEYWORD is the trigger, not a touched artifact.

    `--diff-filter=ACM` means MODIFYING an old `charness-artifacts/issue/*.md` put the
    commit into the finding set, so a `docs: fix a link in the #626 closeout` commit
    brought in by a merge was refused with a summary asserting it "close-keywords a
    GitHub issue" and a remedy telling the author to reword a verb the message does
    not contain.
    """
    finding = _finding(
        repo,
        "docs: fix a broken link in the #700 closeout artifact\n",
        {
            "charness-artifacts/issue/2026-08-16-issue-700-closeout.md": QUESTION_ARTIFACT
            + "\nSee also: docs/index.md\n"
        },
    )
    assert finding is None


def test_the_unbounded_creation_scan_is_capped(repo: Path, monkeypatch) -> None:
    """No exclusion is not the same as no bound.

    An unbounded walk on a URL push costs two subprocesses per historical commit AND
    applies today's floor to every one of them, including old closes whose cited
    evidence has since moved. Those refusals have no author-side fix, so the guard
    would be uninstalled rather than satisfied.
    """
    for index in range(3):
        _commit(repo, f"chore: commit {index}\n", f"c{index}.txt")
    head = _head(repo)
    monkeypatch.setattr(SCAN, "MAX_UNBOUNDED_CREATION_SCAN", 2)

    # No remote at all, so `_published_exclusions` returns [] and the cap is what
    # bounds the walk.
    assert SCAN._published_exclusions(repo, "origin") == []
    assert len(SCAN.range_commits(repo, head, ZERO, "origin")) == 2


def test_partition_closeout_carriers_splits_pause_briefs_by_the_unfiltered_set() -> None:
    brief = {"numbers": [77], "pause_brief": True}
    live = {"numbers": [42], "pause_brief": False}

    # The pause overlap is tested against the UNFILTERED mention set: passing the
    # repo-filtered one made a `Closes acme/other#77` overlap invisible, so the brief
    # kept its exemption and produced no report at all.
    kept, briefs, bare = CARRIER.partition_closeout_carriers([brief, live], {77, 42}, {42})
    assert briefs == []
    assert kept == [brief, live]
    assert bare == []

    kept, briefs, bare = CARRIER.partition_closeout_carriers([brief, live], {42}, {42, 99})
    assert briefs == [brief]
    assert kept == [live]
    assert bare == [99]


def test_an_unsatisfiable_close_keyword_is_named_for_both_channels(tmp_path: Path) -> None:
    """Both channels, not only the `#`-line one.

    Detection reads raw text; the ledger floors read the sanitized body with code
    fences stripped. A fenced `Fixes #123` and a `#`-leading `#123` both produce a
    number GitHub acts on and the ledger reports missing, and neither clears by adding
    a ledger. Covering only the first left the second with the unfollowable remedy.
    """
    message = tmp_path / "message.txt"
    message.write_text(
        "chore: quote the failing log\n\nThe CI log said:\n\n```\nFixes #123\n```\n",
        encoding="utf-8",
    )
    report = CARRIER.evaluate(
        tmp_path,
        message,
        "corca-ai/charness",
        list_paths=lambda _root: [],
        read_file=lambda _root, path: "",
    )
    payload = CARRIER.report_payload(report)

    assert report["ok"] is False
    assert payload["unsatisfiable_close_numbers"] == [123]
    assert "no ledger you add will clear this" in payload["unsatisfiable_close_note"]


def test_a_satisfiable_close_keyword_gets_no_unsatisfiable_note(tmp_path: Path) -> None:
    message = tmp_path / "message.txt"
    message.write_text("chore: work\n\nFixes #123\n", encoding="utf-8")
    report = CARRIER.evaluate(
        tmp_path,
        message,
        "corca-ai/charness",
        list_paths=lambda _root: [],
        read_file=lambda _root, path: "",
    )
    payload = CARRIER.report_payload(report)

    # Refused for a missing ledger, which IS followable -- so the note must be absent,
    # or it would tell an author to reword a message whose remedy is a ledger.
    assert report["ok"] is False
    assert payload["unsatisfiable_close_numbers"] == []
    assert "unsatisfiable_close_note" not in payload


def test_the_creation_cap_is_reported_not_silent(repo: Path, monkeypatch) -> None:
    for index in range(3):
        _commit(repo, f"chore: commit {index}\n", f"c{index}.txt")
    head = _head(repo)
    monkeypatch.setattr(SCAN, "MAX_UNBOUNDED_CREATION_SCAN", 2)

    code, payload = _run(
        "--repo-root", str(repo), stdin=f"refs/heads/main {head} refs/heads/main {ZERO}\n"
    )

    assert code == 0
    # A silent truncation reads as "the whole range came back clean", which is the
    # one way this payload could claim coverage it does not have.
    assert payload["commits_scanned"] == 2
    assert any("capped at 2 commits" in note for note in payload["coverage_notes"])


# --- the arms the changed-line proof found unproven --------------------------------


def test_the_crash_mapping_is_reachable_in_process(repo: Path, capsys) -> None:
    """`cli` maps a crash to exit 2 without a subprocess.

    Left inline in the `__main__` guard, these lines were unreachable from every
    in-process run, so the branch a blocking hook falls back to was proven only by a
    subprocess that coverage never watched.
    """

    def explode(*_args, **_kwargs):
        raise RuntimeError("the issue skill is missing")

    original = GUARD.evaluate
    GUARD.evaluate = explode
    try:
        code = GUARD.cli(["--repo-root", str(repo), "--range", "HEAD~1..HEAD"])
    finally:
        GUARD.evaluate = original

    assert code == GUARD.NO_VERDICT_EXIT
    assert "crashed" in capsys.readouterr().err


def test_the_scan_module_docstring_names_the_stale_clone_caveat() -> None:
    """The published release record sends readers to this MODULE docstring for it.

    It was reachable only from ``range_commits``'s function docstring, so the pointer
    was true about the repo and false about where a reader would look. Pinned as a
    value rather than left as prose: a caveat deleted from the module docstring turns
    a published sentence into a false one with nothing red.
    """
    module_doc = SCAN.__doc__ or ""
    assert "STALE CLONE" in module_doc
    assert "remote-tracking refs" in module_doc
    # The published sentence says "named ONLY in the latter", so re-stating the caveat in
    # the guard's own `Not claimed:` list would make it false with nothing red. Scoped to
    # that LIST, not to the whole guard docstring: the exit-code block must be free to
    # disclose the stale-range coverage hole, which is a statement about what exit 0
    # means rather than a second home for the caveat. A review round found the
    # whole-docstring form both under-specific and blocking that disclosure.
    guard_doc = GUARD.__doc__ or ""
    not_claimed = guard_doc.split("Not claimed:", 1)[1].split("Exit codes:", 1)[0]
    assert "stale" not in not_claimed.lower()


def test_a_malformed_only_stdin_is_a_no_verdict_not_a_pass(repo: Path) -> None:
    code, payload = _run("--repo-root", str(repo), stdin="garbage\nmore garbage\n")

    # Exit 0 here was the guard reporting a clean scan over a push it never read: the
    # sentinel ref carries no sha, every ref is skipped, and `commits_scanned: 0` is
    # indistinguishable from "this push lands nothing". A judged-nothing run owes the
    # no-verdict code, which is the same contract a `RangeUnreadable` gets.
    assert code == GUARD.NO_VERDICT_EXIT
    assert payload["status"] == "no-verdict"
    assert payload["commits_scanned"] == 0
    assert payload["dropped_stdin_lines"] == 2


def test_a_partly_malformed_stdin_is_a_no_verdict_even_though_a_ref_parsed(
    repo: Path,
) -> None:
    """The dropped line names a ref nothing can recover, so the parsed one is not the push."""
    base = _head(repo)
    head = _commit(repo, "docs: an innocent commit\n", "work.txt")

    code, payload = _run(
        "--repo-root",
        str(repo),
        stdin=f"garbage\nrefs/heads/main {head} refs/heads/main {base}\n",
    )

    # Judging only the readable ref and exiting 0 would report coverage of a push whose
    # other ref could carry an unfloored close keyword.
    assert code == GUARD.NO_VERDICT_EXIT
    assert payload["status"] == "no-verdict"
    assert payload["dropped_stdin_lines"] == 1


def test_evaluate_itself_fails_closed_on_a_dropped_line(repo: Path) -> None:
    """The decision lives in the EXPORTED function, not only in the CLI.

    `evaluate` ships to consuming repos in `__all__`. A consumer hook shim that calls
    it and branches on `ok` would otherwise keep the exact pre-repair false green --
    `ok: true` over a push whose refs were never read -- while this repo's own suite
    stayed green, because the repo only ever exercises the CLI.
    """
    refs = SCAN.parse_push_stdin("garbage\nmore garbage\n")
    result = GUARD.evaluate(repo, refs, "corca-ai/charness", "origin")

    assert result["ok"] is False
    assert result["status"] == "no-verdict"
    assert result["dropped_stdin_lines"] == 2


def test_report_payload_does_not_dress_a_no_verdict_as_a_refusal() -> None:
    """`ok: False` means two things now, and the refusal remedy fits only one of them.

    Keyed on `not ok`, a consumer shim printing `report_payload(evaluate(...))` told an
    operator to rebase and reword a commit that close-keywords an issue -- over a run
    that judged nothing and named no commit.
    """
    payload = GUARD.report_payload(GUARD.no_verdict_payload("stdin was unreadable"))

    assert "summary" not in payload
    assert "remediation" not in payload


def test_every_no_verdict_payload_carries_the_same_keys(repo: Path) -> None:
    """Three conditions produce a no-verdict; a reader of one must not KeyError on another."""
    expected = set(GUARD.no_verdict_payload("x"))

    _, dropped = _run("--repo-root", str(repo), stdin="garbage\nmore garbage\n")
    _, unparseable_range = _run("--repo-root", str(repo), "--range", "not-a-range")

    assert set(dropped) == expected
    assert set(unparseable_range) == expected


def test_a_bare_interactive_run_is_a_no_verdict_rather_than_no_refs(
    repo: Path, monkeypatch
) -> None:
    """No `--range` and a tty on stdin means this run was handed no push at all."""
    monkeypatch.setattr(GUARD.sys.stdin, "isatty", lambda: True)

    # `status: no-refs` + exit 0 here was a pass manufactured out of missing input.
    assert GUARD.main(["--repo-root", str(repo)]) == GUARD.NO_VERDICT_EXIT


def test_a_git_timeout_is_a_no_verdict_not_a_pass(repo: Path, monkeypatch) -> None:
    def timeout(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            ["git", "rev-list"], SCAN.GIT_TIMEOUT_SECONDS, "", "timed out"
        )

    monkeypatch.setattr(SCAN, "run_process", timeout)
    with pytest.raises(SCAN.RangeUnreadable) as excinfo:
        SCAN.range_commits(repo, "HEAD", "HEAD~1")

    # Fail-closed: a git call that never answered must not degrade to an empty range,
    # which the guard would report as a clean scan.
    assert "timed out" in str(excinfo.value)


def test_the_hook_mode_import_fallback_binds(monkeypatch) -> None:
    """The `except ModuleNotFoundError` arm, forced rather than assumed.

    In a git hook `scripts/` is `sys.path[0]` and `scripts.<mod>` is not importable,
    so the guard falls back to flat imports. That arm is invisible from a test process
    where the package form resolves. Filtering `sys.path` would not force it either --
    the modules are already in `sys.modules`. A `meta_path` finder that refuses the
    package spelling is what actually selects the arm.
    """
    import importlib.util
    import sys

    class RefuseScriptsPackage:
        def find_spec(self, name, path=None, target=None):
            if name.startswith("scripts."):
                raise ModuleNotFoundError(f"No module named {name!r}")
            return None

    finder = RefuseScriptsPackage()
    monkeypatch.setattr(sys, "meta_path", [finder, *sys.meta_path])
    for name in [n for n in list(sys.modules) if n.startswith("scripts.")]:
        monkeypatch.delitem(sys.modules, name, raising=False)
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))

    spec = importlib.util.spec_from_file_location(
        "prepush_close_keyword_guard_hook_mode", ROOT / "scripts" / "prepush_close_keyword_guard.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # The names the fallback binds are the ones the guard cannot run without.
    assert module.close_targets("fix: closes #7\n", SCANNER) == [(None, 7)]
    assert module.emit_yaml is not None


def test_a_protected_target_is_refused_by_authorization_before_any_ledger(
    repo: Path,
) -> None:
    """The branch that made omitting authorization a false green.

    A commit close-keywording a crosswalk-protected issue WITH a complete ledger
    cleared the guard while the commit-msg carrier would have refused it -- reachable
    through every escape this guard exists for (`--no-verify`, cherry-pick, a merge of
    branch whose hooks never ran).
    """
    build_protected_world(repo)
    base = _head(repo)
    head = _commit(
        repo,
        BODY_VALID_CLOSEOUT.replace("#42", f"#{PROTECTED[0]}"),
        "work.txt",
        extra={
            rel: (repo / rel).read_text(encoding="utf-8")
            for rel in [CROSSWALK_REL]
            if (repo / rel).is_file()
        },
    )

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 1
    finding = payload["close_keyword_commits"][0]
    # Refused by AUTHORIZATION, not by the ledger floor: the ledger is complete here,
    # which is exactly why the missing check could not be caught by a ledger test.
    assert finding["refused_by"] == "closeout_authorization"
    assert finding["closeout_authorization"]["authorized"] is False
    assert finding["reports"] == []


def test_cli_lets_argparse_exit_through(repo: Path) -> None:
    # argparse raises SystemExit(2) for a bad flag. The crash mapping must re-raise it
    # rather than converting it into a payload-less return, or a usage error would be
    # indistinguishable from a git failure.
    with pytest.raises(SystemExit) as excinfo:
        GUARD.cli(["--repo-root", str(repo), "--not-a-flag"])
    assert excinfo.value.code == 2
