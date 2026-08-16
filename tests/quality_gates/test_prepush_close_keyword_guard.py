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

from tests.quality_gates.support import ROOT
from tests.script_main import load_script_module, run_loaded_script_main

GUARD = load_script_module("prepush_close_keyword_guard", ROOT / "scripts" / "prepush_close_keyword_guard.py")
# The reading half: range resolution and close-keyword detection. Addressed directly
# rather than through the guard's re-export, because a `monkeypatch` of the guard's
# imported copy would not reach the module that actually reads the constant.
# Imported under the package name the guard itself imports. Loading it by path under
# a different module name produced a SECOND module object, so a `monkeypatch` here
# left the copy the guard actually calls untouched and the test asserted nothing.
SCAN = importlib.import_module("scripts.prepush_close_keyword_scan")
CARRIER = load_script_module(
    "check_issue_closeout_commit_msg_for_guard_tests",
    ROOT / "scripts" / "check_issue_closeout_commit_msg.py",
)
ZERO = "0" * 40

# The exact wrapped shape that closed #626: the close verb ends one line and the ref
# starts the next, so the ref line begins with `#`.
BODY_626 = (
    "test(lesson-loop): prove the S3 claims that had no failing test\n"
    "\n"
    "S6 rather than S3 because it changes the disposition GRAMMAR, and before S7\n"
    "rather than after because S7 closes\n"
    "#626/#627/#631 on the strength of that gate.\n"
)

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
        "AI-provenance: agent-drafted; human-audited per the resolution critique",
    ]
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _commit(repo: Path, body: str, name: str, extra: dict[str, str] | None = None) -> str:
    """Commit with `-F`, which is the cleanup mode that made #626 possible: git stores
    a `#`-leading line verbatim under `-m`/`-F` and strips it only in editor mode."""
    (repo / name).write_text(name, encoding="utf-8")
    _git(repo, "add", name)
    for rel, content in (extra or {}).items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        _git(repo, "add", rel)
    message_file = repo / ".commit-message"
    message_file.write_text(body, encoding="utf-8")
    _git(repo, "commit", "-F", str(message_file))
    message_file.unlink()
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-b", "main")
    # Identity is set explicitly rather than inherited: on an image with no global
    # `user.name`/`user.email` every `_commit` here would raise and the whole file
    # would error out for a reason unrelated to what it checks.
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Charness Test")
    _commit(tmp_path, "chore: base commit\n", "base.txt")
    return tmp_path


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


def test_refuses_the_wrapped_close_keyword_that_closed_626(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, BODY_626, "work.txt")

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 1
    assert payload["status"] == "refused"
    finding = payload["close_keyword_commits"][0]
    assert finding["commit"] == head
    # 626 and only 626: the `/` separator is not GitHub's comma grammar, so #627 and
    # #631 never linked and a guard that claimed them would be over-reporting the
    # blast radius of the very act it is describing.
    assert finding["numbers"] == [626]
    assert finding["ok"] is False
    assert "not undoable" in payload["summary"]
    # The remediation has to name the not-intended branch, because that is the branch
    # #626 was on: the fix is rewording, not manufacturing a closeout ledger for an
    # issue the author never meant to close.
    assert "reword" in payload["remediation"]


def test_a_close_keyword_with_a_valid_closeout_ledger_passes(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, BODY_VALID_CLOSEOUT, "work.txt")

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 0, payload
    assert payload["status"] == "verified"
    assert payload["close_keyword_commits"][0]["numbers"] == [42]


def test_a_range_with_no_close_keyword_is_not_applicable(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, "docs: ordinary commit about issue 42\n", "work.txt")

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 0
    assert payload["status"] == "not_applicable"
    assert payload["commits_scanned"] == 1


def test_a_close_keyword_qualified_to_another_repo_is_not_a_target(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, "fix: closes acme/other-repo#77 upstream\n", "work.txt")

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    # GitHub cannot close a foreign issue from here, so no LEDGER floor applies and
    # the push is not refused: folding it in would refuse over an impossible close
    # while pushing the author toward the unqualified form that would close THIS
    # repo's #77.
    assert code == 0
    # Without this the assertion above would also hold if range resolution had
    # scanned nothing at all, which is the one way a green verdict lies.
    assert payload["commits_scanned"] == 1
    # The commit IS still carried into the finding, with no ledger report, because
    # protected-target authorization has to see a foreign target to refuse it --
    # dropping the ref before authorization ran was a measured escape.
    finding = payload["close_keyword_commits"][0]
    assert finding["numbers"] == [77]
    assert finding["reports"] == []
    assert finding["closeout_authorization"]["authorized"] is True


# --- range resolution -------------------------------------------------------------


def test_a_ref_deletion_lands_no_commits_and_scans_none(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    assert SCAN.range_commits(repo, ZERO, head) == []


def test_a_new_ref_is_bounded_by_what_origin_already_has(repo: Path, tmp_path: Path) -> None:
    origin = tmp_path.parent / "origin.git"
    _git(repo, "init", "--bare", str(origin))
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "--no-verify", "origin", "main")
    published = _git(repo, "rev-parse", "HEAD")
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
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, BODY_626, "work.txt")

    code, payload = _run(
        "--repo-root", str(repo), stdin=f"refs/heads/main {head} refs/heads/main {base}\n"
    )

    assert code == 1
    assert payload["close_keyword_commits"][0]["numbers"] == [626]


def test_a_commit_reachable_from_two_pushed_refs_is_judged_once(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, BODY_626, "work.txt")
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
    _git(tmp_path, "init", "-b", "main")
    message = tmp_path / "message.txt"
    message.write_text(BODY_626, encoding="utf-8")

    result = run_loaded_script_main(
        "check_issue_closeout_commit_msg.py",
        CARRIER,
        "--repo-root",
        str(tmp_path),
        "--commit-msg-file",
        str(message),
    )
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 1, result.stdout
    assert payload["bare_close_numbers"] == [626]


def test_the_carrier_scan_text_keeps_both_bodies() -> None:
    raw = "feat: work\n\n# not a git comment, it is the ref line\n"
    sanitized = CARRIER._strip_commit_comments(raw)
    scan = CARRIER._close_keyword_scan_text(raw, sanitized)

    # Both halves, not the raw one alone: the sanitized body is still what the ledger
    # floors parse, and a scan that dropped it would change which fields are read.
    assert "# not a git comment" in scan
    assert sanitized in scan


def test_a_git_comment_block_alone_does_not_trigger_the_carrier(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-b", "main")
    message = tmp_path / "message.txt"
    message.write_text(
        "docs: ordinary commit\n"
        "\n"
        "# Please enter the commit message for your changes. Lines starting\n"
        "# with '#' will be ignored, and an empty message aborts the commit.\n"
        "#\n"
        "# On branch main\n"
        "# Changes to be committed:\n"
        "#\tmodified:   scripts/check_issue_closeout_commit_msg.py\n",
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "check_issue_closeout_commit_msg.py",
        CARRIER,
        "--repo-root",
        str(tmp_path),
        "--commit-msg-file",
        str(message),
    )

    # Honest about its own strength: this arm kills no mutant of the widening, because
    # it also passes with the widening reverted. It constrains a FUTURE edit that
    # widens detection far enough to catch git's own template, which is the realistic
    # shape of a false refusal here. Do not count it as coverage of the repair.
    assert result.returncode == 0, result.stdout
    assert yaml.safe_load(result.stdout)["status"] == "not_applicable"


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
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(
        repo,
        QUESTION_MESSAGE,
        "work.txt",
        extra={"charness-artifacts/issue/2026-08-16-issue-700-closeout.md": QUESTION_ARTIFACT},
    )

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 0, payload
    report = payload["close_keyword_commits"][0]["reports"][0]
    assert report["classification"] == "question"
    assert report["source_artifact"].endswith("issue-700-closeout.md")


def test_the_same_message_without_the_artifact_is_classified_bug_and_refused(repo: Path) -> None:
    """The negative arm that makes the test above mean something.

    Byte-identical message, artifact removed: classification falls back to `bug` and
    the floor demands root-cause/prevention claims. Without this arm, the passing case
    above would also pass with the artifact parse deleted entirely.
    """
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, QUESTION_MESSAGE, "work.txt")

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 1
    report = payload["close_keyword_commits"][0]["reports"][0]
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
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, BODY_VALID_CLOSEOUT, "work.txt")

    _, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    authorization = payload["close_keyword_commits"][0]["closeout_authorization"]
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
        ("fix: closes https://github.com/corca-ai/charness/issues/700\n", [("corca-ai/charness", 700)]),
        ("fix: closes #700\n", [(None, 700)]),
        # The comma-list form applies to every spelling, not only to `#N`. Reporting
        # only the first left the guard narrower than GitHub on the one surface whose
        # job is to be at least as wide.
        ("fix: closes GH-700, GH-701\n", [(None, 700), (None, 701)]),
        ("fix: closes #700, https://github.com/corca-ai/charness/issues/701\n",
         [(None, 700), ("corca-ai/charness", 701)]),
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
    # `GH-N` and the full issue URL are GitHub close spellings the canonical scanner
    # does not match, so a body using either scanned clean while closing an issue.
    assert SCAN.close_targets(body, SCANNER) == expected


def test_local_numbers_is_what_narrows_to_this_repo() -> None:
    qualified = SCAN.close_targets(
        "fix: closes #700, acme/other#701\n", SCANNER
    )
    # Two separate questions, deliberately: the LEDGER floor applies only to closes
    # GitHub can fire from here, but authorization is handed the unfiltered set --
    # filtering before it ran let a crosswalk-protected foreign target escape.
    assert qualified == [(None, 700), ("acme/other", 701)]
    assert SCAN.local_numbers(qualified, "corca-ai/charness") == {700}


def test_a_gh_dash_close_without_a_ledger_is_refused(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, "chore: tidy the lane\n\nIncidentally closes GH-700.\n", "work.txt")

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 1
    assert payload["close_keyword_commits"][0]["numbers"] == [700]


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
    published = _git(repo, "rev-parse", "HEAD")

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
    base = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, BODY_626, "work.txt")

    result = subprocess.run(
        [sys.executable, str(lonely / "prepush_close_keyword_guard.py"),
         "--repo-root", str(repo), "--range", f"{base}..{head}"],
        capture_output=True, text=True, check=False,
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
    base = _git(repo, "rev-parse", "HEAD")
    _commit(
        repo,
        "docs: land the closeout artifact\n",
        "first.txt",
        extra={"charness-artifacts/issue/2026-08-16-issue-700-closeout.md": QUESTION_ARTIFACT},
    )
    head = _commit(
        repo,
        "docs: fix a broken link in the #700 closeout artifact\n",
        "second.txt",
        extra={
            "charness-artifacts/issue/2026-08-16-issue-700-closeout.md":
                QUESTION_ARTIFACT + "\nSee also: docs/handoff.md\n"
        },
    )

    code, payload = _run("--repo-root", str(repo), "--range", f"{base}..{head}")

    assert code == 0, payload
    assert payload["status"] == "not_applicable"
    assert payload["commits_scanned"] == 2
    assert head not in [finding["commit"] for finding in payload["close_keyword_commits"]]


def test_the_unbounded_creation_scan_is_capped(repo: Path, monkeypatch) -> None:
    """No exclusion is not the same as no bound.

    An unbounded walk on a URL push costs two subprocesses per historical commit AND
    applies today's floor to every one of them, including old closes whose cited
    evidence has since moved. Those refusals have no author-side fix, so the guard
    would be uninstalled rather than satisfied.
    """
    for index in range(3):
        _commit(repo, f"chore: commit {index}\n", f"c{index}.txt")
    head = _git(repo, "rev-parse", "HEAD")
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
    _git(tmp_path, "init", "-b", "main")
    message = tmp_path / "message.txt"
    message.write_text(
        "chore: quote the failing log\n\nThe CI log said:\n\n```\nFixes #123\n```\n",
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "check_issue_closeout_commit_msg.py", CARRIER,
        "--repo-root", str(tmp_path), "--commit-msg-file", str(message),
    )
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 1
    assert payload["unsatisfiable_close_numbers"] == [123]
    assert "no ledger you add will clear this" in payload["unsatisfiable_close_note"]


def test_a_satisfiable_close_keyword_gets_no_unsatisfiable_note(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-b", "main")
    message = tmp_path / "message.txt"
    message.write_text("chore: work\n\nFixes #123\n", encoding="utf-8")

    result = run_loaded_script_main(
        "check_issue_closeout_commit_msg.py", CARRIER,
        "--repo-root", str(tmp_path), "--commit-msg-file", str(message),
    )
    payload = yaml.safe_load(result.stdout)

    # Refused for a missing ledger, which IS followable -- so the note must be absent,
    # or it would tell an author to reword a message whose remedy is a ledger.
    assert result.returncode == 1
    assert payload["unsatisfiable_close_numbers"] == []
    assert "unsatisfiable_close_note" not in payload


def test_the_creation_cap_is_reported_not_silent(repo: Path, monkeypatch) -> None:
    for index in range(3):
        _commit(repo, f"chore: commit {index}\n", f"c{index}.txt")
    head = _git(repo, "rev-parse", "HEAD")
    monkeypatch.setattr(SCAN, "MAX_UNBOUNDED_CREATION_SCAN", 2)

    code, payload = _run("--repo-root", str(repo), stdin=f"refs/heads/main {head} refs/heads/main {ZERO}\n")

    assert code == 0
    # A silent truncation reads as "the whole range came back clean", which is the
    # one way this payload could claim coverage it does not have.
    assert payload["commits_scanned"] == 2
    assert any("capped at 2 commits" in note for note in payload["coverage_notes"])
