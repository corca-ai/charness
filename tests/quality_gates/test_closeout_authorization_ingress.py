"""Every closeout ingress refuses a protected target BEFORE its first side effect.

`authorized is False` is not the property under test here — the crosswalk's own tests
cover that. What these tests prove is ORDER: that no temp file was written, no comment
posted, no close issued, and no bump run before the refusal. A check that fires after
the mutation is not a gate, and the difference is invisible in a boolean.

The other half is BLAST RADIUS. Each refusal test is paired with a preservation test
showing an unrelated issue still closes exactly as it did. A gate that quietly tightens
every close in the repo gets removed within a week, taking the protection with it.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from tests.closeout_authorization_world import build_protected_world
from tests.quality_gates.seeding_support import _install_empty_git_dir
from tests.script_main import load_script_module, run_loaded_script_main

REPO_ROOT = Path(__file__).resolve().parents[2]
ISSUE_SCRIPTS = REPO_ROOT / "skills" / "public" / "issue" / "scripts"
RELEASE_SCRIPTS = REPO_ROOT / "skills" / "public" / "release" / "scripts"
COMMIT_HOOK = load_script_module(
    "closeout_authorization_commit_hook",
    REPO_ROOT / "scripts" / "check_issue_closeout_commit_msg.py",
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BackendSpy:
    """Records every backend argv. The assertion is almost always `== []`."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, argv):
        self.calls.append(list(argv))
        # ECHO the issue and repository actually asked about. A canned `number: 1` with a
        # placeholder url modelled a backend that answers about a different issue than it was
        # asked for — which the close path's post-close readback now refuses, correctly, as an
        # identity mismatch. A spy that cannot be told apart from that failure cannot be used
        # to prove anything about the paths around it.
        asked = next((part for part in argv if part.isdigit()), "1")
        repo = next(
            (argv[i + 1] for i, part in enumerate(argv[:-1]) if part in {"--repo", "-R"}),
            "corca-ai/charness",
        )
        payload = {
            "number": int(asked),
            "state": "CLOSED",
            "url": f"https://github.com/{repo}/issues/{asked}",
        }
        # JSON, not YAML: this stands in for the BACKEND's reply (`gh ... --json`), a
        # third-party native API the repo's own YAML-only output rule does not touch.
        return subprocess.CompletedProcess(argv, 0, json.dumps(payload), "")


def _body(tmp_path: Path, number: int) -> Path:
    path = tmp_path / "close-body.md"
    path.write_text(
        "\n\n".join(
            [
                f"Resolution for #{number}.",
                "JTBD: close the issue end to end.",
                "Root cause: the carrier was prose-only.",
                "Debug artifact: charness-artifacts/debug/latest.md.",
                "Siblings: none | decision: no siblings | proof: inspected the lane.",
                "Prevention: the authorization gate refuses unevidenced closes.",
                "Critique: blocked synthetic-test-harness: this test spawns no reviewer",
                f"Behavior #{number}: behavior test exercises the fix (distinct channel from CLOSED)",
                f"Probe record #{number}: local-only-by-contract",
                "AI-provenance: agent-drafted; human-audited per the resolution critique",
            ]
        ),
        encoding="utf-8",
    )
    return path


# --- direct close carrier -------------------------------------------------


def test_direct_close_of_a_protected_issue_makes_zero_backend_calls(tmp_path: Path) -> None:
    """Not "the close was refused" — "the COMMENT never happened either".

    `close_with_comment` posts the comment first and its own error path documents
    that the close can fail after the comment has landed. A check placed between them
    would refuse the close having already written to the issue.
    """
    build_protected_world(tmp_path)
    close = _load(ISSUE_SCRIPTS / "issue_close.py", "authz_issue_close")
    spy = BackendSpy()
    close._run_backend = spy

    with pytest.raises(RuntimeError) as excinfo:
        close.close_with_comment(
            "corca-ai/charness",
            514,
            _body(tmp_path, 514),
            repo_root=tmp_path,
            classification="bug",
        )

    assert spy.calls == []
    assert "closeout authorization" in str(excinfo.value)


def test_direct_close_without_a_manual_declaration_is_refused(tmp_path: Path) -> None:
    """The CLI `--number` may not authorize itself.

    This carrier's body has no close keyword, so without a separately written,
    repository-qualified declaration there is nothing the invoked target could
    disagree with — and a check that cannot disagree cannot fail.
    """
    build_protected_world(tmp_path)
    close = _load(ISSUE_SCRIPTS / "issue_close.py", "authz_issue_close_2")
    spy = BackendSpy()
    close._run_backend = spy

    with pytest.raises(RuntimeError) as excinfo:
        close.close_with_comment(
            "corca-ai/charness",
            515,
            _body(tmp_path, 515),
            repo_root=tmp_path,
            classification="bug",
            manual_target_declaration=None,
        )

    assert spy.calls == []
    assert "manual-target-declaration" in str(excinfo.value)


def test_a_manual_declaration_naming_a_different_issue_is_refused(tmp_path: Path) -> None:
    build_protected_world(tmp_path)
    close = _load(ISSUE_SCRIPTS / "issue_close.py", "authz_issue_close_3")
    spy = BackendSpy()
    close._run_backend = spy

    with pytest.raises(RuntimeError) as excinfo:
        close.close_with_comment(
            "corca-ai/charness",
            514,
            _body(tmp_path, 514),
            repo_root=tmp_path,
            classification="bug",
            manual_target_declaration="corca-ai/charness#518",
        )

    assert spy.calls == []
    assert "REFUSED" in str(excinfo.value)
    assert "target_disagreement" in str(excinfo.value)


def test_a_manual_declaration_naming_a_foreign_repo_is_refused(tmp_path: Path) -> None:
    build_protected_world(tmp_path)
    close = _load(ISSUE_SCRIPTS / "issue_close.py", "authz_issue_close_4")
    spy = BackendSpy()
    close._run_backend = spy

    with pytest.raises(RuntimeError):
        close.close_with_comment(
            "corca-ai/charness",
            514,
            _body(tmp_path, 514),
            repo_root=tmp_path,
            classification="bug",
            manual_target_declaration="fork-org/charness#514",
        )

    assert spy.calls == []


def test_an_unrelated_direct_close_still_reaches_the_backend_unchanged(tmp_path: Path) -> None:
    """Preservation: no new mandatory flag for everyone else.

    The exact-identity contract adds a pre-mutation readback, so this remains
    unrelated to authorization while proving the new readback is in the chain.
    """
    build_protected_world(tmp_path)
    close = _load(ISSUE_SCRIPTS / "issue_close.py", "authz_issue_close_5")
    spy = BackendSpy()
    close._run_backend = spy

    result = close.close_with_comment(
        "corca-ai/charness", 9001, _body(tmp_path, 9001), repo_root=tmp_path, classification="bug"
    )

    assert result["ok"] is True
    # The unrelated carrier remains allowed, while the current ingress performs
    # two pre-mutation identity reads and one post-close readback around comment
    # and close. Keep the preservation assertion about the command family, not a
    # retired four-call topology.
    assert [call[1] for call in spy.calls] == ["issue"] * 5
    assert result["closeout_authorization"]["applies"] is False


# --- commit-message carrier -----------------------------------------------


def _init_repo(repo: Path) -> None:
    _install_empty_git_dir(repo, branch="main")


def _stage(repo: Path, rel: str, body: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    subprocess.run(["git", "add", rel], cwd=repo, check=True, capture_output=True, text=True)


def _run_commit_hook(repo: Path, message: str):
    """Run the commit-msg gate and hand back its raw result.

    No output flag: the hook's stdout is unconditionally YAML since `--json` was
    removed, and passing the flag now aborts the run with argparse's exit 2 — which
    would make every refusal assertion below pass for the wrong reason.
    """
    message_file = repo / "COMMIT_EDITMSG"
    message_file.write_text(message, encoding="utf-8")
    result = run_loaded_script_main(
        "scripts/check_issue_closeout_commit_msg.py",
        COMMIT_HOOK,
        "--repo-root",
        str(repo),
        "--commit-msg-file",
        str(message_file),
    )
    return result, message_file


def test_the_commit_hook_refuses_a_protected_close_without_writing_its_temp_carrier(
    tmp_path: Path,
) -> None:
    """The temp carrier is this hook's first side effect, so it must not exist.

    The sanitized `.charness-closeout-body` file is written before any per-issue
    verification runs. Asserting only on the exit code would pass even if the file had
    been written and then cleaned up in `finally` — so the assertion is on the file.
    """
    _init_repo(tmp_path)
    build_protected_world(tmp_path)

    result, message_file = _run_commit_hook(tmp_path, "Repair the boundary\n\nCloses #514\n")

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "refused"
    assert payload["closeout_authorization"]["refusal"] == "matrix_incomplete"
    sanitized = message_file.with_suffix(message_file.suffix + ".charness-closeout-body")
    assert not sanitized.exists()


def test_the_commit_hook_refuses_a_carrier_that_mixes_a_protected_and_another_issue(
    tmp_path: Path,
) -> None:
    """The aggregate rule, on the carrier where it matters most.

    GitHub auto-closes both numbers on push. There is no way to attach the protected
    issue's evidence to only half a commit, so the whole carrier refuses.
    """
    _init_repo(tmp_path)
    build_protected_world(tmp_path)
    _stage(tmp_path, "charness-artifacts/issue/closeout.md", "Closes #9001.\n")

    result, _ = _run_commit_hook(tmp_path, "Mixed carrier\n\nCloses #518\n")

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["closeout_authorization"]["refusal"] == "not_singleton"


def test_the_commit_hook_leaves_an_unrelated_multi_issue_carrier_alone(tmp_path: Path) -> None:
    """Preservation: the singleton rule applies only when a protected target is present.

    Without this the gate would silently forbid every multi-issue closeout commit in
    the repo, which is a policy nobody agreed to.
    """
    _init_repo(tmp_path)
    build_protected_world(tmp_path)

    result, _ = _run_commit_hook(tmp_path, "Two unrelated issues\n\nCloses #9001\nCloses #9002\n")

    payload = yaml.safe_load(result.stdout)
    assert payload.get("status") != "refused"


def test_a_commit_touching_no_issue_is_still_not_applicable(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    build_protected_world(tmp_path)

    result, _ = _run_commit_hook(tmp_path, "Ordinary commit\n")

    assert result.returncode == 0
    assert yaml.safe_load(result.stdout)["status"] == "not_applicable"


# --- draft validation and post-publication readback -----------------------


def test_draft_validation_of_a_protected_issue_cannot_report_draft_verified(tmp_path: Path) -> None:
    """`draft_verified` is the status the close is authorized against.

    If the draft says verified while the close would refuse, the operator finds out at
    the close call — the last checkpoint before an irreversible act, and the worst
    place to learn it.
    """
    build_protected_world(tmp_path)
    draft = _load(ISSUE_SCRIPTS / "issue_validate_closeout_draft.py", "authz_draft")
    verifier = _load(ISSUE_SCRIPTS / "issue_verify_closeout.py", "authz_draft_verifier")
    body = _body(tmp_path, 514)

    result = draft.validate_closeout_draft(
        verifier=verifier,
        repo_root=tmp_path,
        repo="corca-ai/charness",
        numbers=[514],
        classification="bug",
        body_file=None,
        backend={"id": "gh"},
        carrier="direct-commit",
        commit_message_file=body,
    )

    assert result["status"] == "draft_failed"
    assert result["closeout_authorization"]["refusal"] == "matrix_incomplete"


def test_draft_validation_of_an_unrelated_issue_is_unaffected(tmp_path: Path) -> None:
    build_protected_world(tmp_path)
    draft = _load(ISSUE_SCRIPTS / "issue_validate_closeout_draft.py", "authz_draft_2")
    verifier = _load(ISSUE_SCRIPTS / "issue_verify_closeout.py", "authz_draft_verifier_2")

    result = draft.validate_closeout_draft(
        verifier=verifier,
        repo_root=tmp_path,
        repo="corca-ai/charness",
        numbers=[9001],
        classification="bug",
        body_file=None,
        backend={"id": "gh"},
        carrier="direct-commit",
        commit_message_file=_body(tmp_path, 9001),
    )

    # The draft may still fail its ordinary ledger checks — that is this fixture's
    # business, not this gate's. What must hold is that the authorization layer
    # contributed no refusal: an unrelated issue sees exactly the bar it saw before.
    assert result["closeout_authorization"]["applies"] is False
    assert result["closeout_authorization"]["authorized"] is True
    assert not [item for item in result.get("refusals", []) if item.get("refusal")]


def test_the_post_publication_readback_reports_authorization_but_does_not_gate_on_it(
    tmp_path: Path,
) -> None:
    """The one ingress that deliberately does NOT refuse.

    By readback time the close has already landed. Refusing here would suppress the
    only channel that confirms whether the irreversible act succeeded, in exchange for
    a protection with nothing left to protect.
    """
    build_protected_world(tmp_path)
    verifier = _load(ISSUE_SCRIPTS / "issue_verify_closeout.py", "authz_verify")

    result = verifier.verify_closeout(
        repo_root=tmp_path,
        repo="corca-ai/charness",
        numbers=[514],
        classification="bug",
        carrier="pr-body",
        backend={"id": "gh"},
        body_file=_body(tmp_path, 514),
    )

    assert "reported-only" in result["closeout_authorization"]["gating"]
    assert result["closeout_authorization"]["applies"] is True


# --- release carriers -----------------------------------------------------


def _release_module():
    return _load(RELEASE_SCRIPTS / "release_issue_closeout.py", "authz_release_closeout")


def test_release_preflight_refuses_a_protected_issue_before_any_bump_or_publish(
    tmp_path: Path,
) -> None:
    """Release closure is outside this goal, so the release path must not be the
    unwatched route that ships one. The spy proves nothing ran."""
    build_protected_world(tmp_path)
    release = _release_module()
    spy = BackendSpy()

    with pytest.raises(SystemExit) as excinfo:
        release.preflight_release_issues(
            tmp_path,
            repo="corca-ai/charness",
            issue_numbers=[514],
            payload={},
            run=spy,
            classification="bug",
            carrier_file=None,
        )

    assert spy.calls == []
    assert "carrier_out_of_scope" in str(excinfo.value)


def test_release_preflight_refuses_before_it_even_demands_its_own_required_flags(
    tmp_path: Path,
) -> None:
    """Ordering detail worth pinning: the refusal precedes the classification/carrier
    checks, so an operator cannot learn the protected target was acceptable-but-for-a-
    missing-flag and go supply the flag."""
    build_protected_world(tmp_path)
    release = _release_module()

    with pytest.raises(SystemExit) as excinfo:
        release.preflight_release_issues(
            tmp_path,
            repo="corca-ai/charness",
            issue_numbers=[515],
            payload={},
            run=BackendSpy(),
            classification=None,
            carrier_file=None,
        )

    assert "carrier_out_of_scope" in str(excinfo.value)


def test_ensure_release_issues_closed_refuses_before_calling_gh_issue_close(tmp_path: Path) -> None:
    """Re-authorized here rather than trusting the preflight: the resume/recovery
    entrypoints can reach this function without the preflight running first."""
    build_protected_world(tmp_path)
    release = _release_module()
    spy = BackendSpy()

    with pytest.raises(SystemExit):
        release.ensure_release_issues_closed(
            tmp_path,
            repo="corca-ai/charness",
            issue_numbers=[518],
            payload={"tag_name": "v1", "commit_sha": "abc"},
            run=spy,
        )

    assert spy.calls == []


def test_the_release_closeout_message_refuses_before_writing_its_temp_file(tmp_path: Path) -> None:
    """A separately importable owner re-authorizes rather than assuming a caller did."""
    build_protected_world(tmp_path)
    message = _load(RELEASE_SCRIPTS / "release_issue_closeout_message.py", "authz_release_message")
    before = set(Path(tmp_path).rglob("*.commitmsg"))

    with pytest.raises(SystemExit) as excinfo:
        message.validate_release_closeout_commit_message(
            tmp_path,
            repo="corca-ai/charness",
            issue_numbers=[514],
            classification="bug",
            commit_message="Closes #514\n",
        )

    assert "REFUSED" in str(excinfo.value)
    assert set(Path(tmp_path).rglob("*.commitmsg")) == before


def test_a_release_closing_only_unrelated_issues_is_not_blocked(tmp_path: Path) -> None:
    """Preservation: release closeout keeps working for every other issue."""
    build_protected_world(tmp_path)
    release = _release_module()
    payload: dict = {}

    result = release.refuse_unauthorized_release_close(
        tmp_path, repo="corca-ai/charness", issue_numbers=[9001, 9002], carrier_source="release"
    )

    assert result["authorized"] is True
    assert result["applies"] is False
    assert payload == {}


def test_a_repo_without_a_crosswalk_keeps_every_carrier_working(tmp_path: Path) -> None:
    """Consumers who never adopt this artifact must be unaffected.

    The gate's teeth live in the checked-in crosswalk; its absence is reported, never
    treated as a refusal, or installing the plugin would break issue closeout for
    every repo that has no crosswalk — which is all of them.
    """
    release = _release_module()

    result = release.refuse_unauthorized_release_close(
        tmp_path, repo="corca-ai/charness", issue_numbers=[514], carrier_source="release"
    )

    assert result["authorized"] is True
