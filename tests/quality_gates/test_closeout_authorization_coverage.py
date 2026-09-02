"""The authorization layer's own decision surface: refuse, permit, and degrade.

`test_closeout_authorization_ingress.py` proves ORDER — that each carrier refuses
before its first side effect. These tests cover the layer underneath it: the shared
refusal renderer, the module loaders that decide whether the gate is present at all,
and the two answers the gate can give when it is.

The escape each test guards is the same shape: a protected close reaching GitHub
because someone read the wrong signal. A refusal that renders on only one channel is
invisible to whichever consumer was not anticipated. A loader that returns `None`
where it meant to raise turns a broken install into a permissive one. A loader that
raises where it meant to degrade breaks every unrelated close in every consumer repo,
and a gate everyone deletes protects nothing. So each test names which of the two
outcomes is correct for its situation, and asserts the record SAYS which one happened
rather than silently implying it.

No test here contacts GitHub: every backend is a spy whose expected call list is `[]`,
and the worlds are built by `tests/closeout_authorization_world.build_protected_world`
from real freeze/crosswalk artifacts.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.closeout_authorization_world import CROSSWALK_REL, build_protected_world
from tests.quality_gates.seeding_support import _install_empty_git_dir

REPO_ROOT = Path(__file__).resolve().parents[2]
ISSUE_SCRIPTS = REPO_ROOT / "skills" / "public" / "issue" / "scripts"
SCRIPTS = REPO_ROOT / "scripts"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _relocate(monkeypatch: pytest.MonkeyPatch, module, home: Path):
    """Point a real, already-loaded module's `__file__` at a directory of our choosing.

    Every loader under test discovers its collaborators by walking outward from its own
    `__file__`. Moving that anchor is the honest way to reproduce an install where the
    collaborator is genuinely absent — the same bytes, running the same branches, from a
    location where the neighbour it looks for does not exist. Copying the file instead
    would also work, but then the code under test would be the copy.
    """
    home.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(module, "__file__", str(home / Path(module.__file__).name))
    return module


def _null_spec(_name, _location):
    """Stand in for `importlib.util.spec_from_file_location` yielding no usable spec.

    Forced rather than provoked from the filesystem: every candidate these loaders
    build ends in `.py`, so importlib always hands back a loader. The `spec is None or
    spec.loader is None` branches are therefore only reachable this way. They are still
    worth pinning, because the two loaders resolve that same condition in OPPOSITE
    directions and the difference decides whether a broken install refuses or permits.
    """
    return None


# --- the shared refusal shape (scripts/review/closeout_refusal_lib.py) -----------------


def test_a_lane_refusal_names_itself_on_both_channels_and_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """No crosswalk means nothing can authorize a protected close, and both consumers
    must be able to see that.

    The refusal goes to stdout as the YAML payload for a caller that parses, and to
    stderr as a named line for a human watching a terminal. Emitting only one is how a refusal
    becomes invisible to whichever consumer was not anticipated — and an operator who
    sees no complaint reads the run as a pass and proceeds to the close.
    """
    from scripts.gates.validate_evidence_boundary_crosswalk import main as validate_main

    monkeypatch.setattr(
        sys, "argv", ["validate", "--repo-root", str(tmp_path), "--crosswalk", CROSSWALK_REL]
    )

    exit_code = validate_main()

    captured = capsys.readouterr()
    assert exit_code == 1
    payload = yaml.safe_load(captured.out)
    assert payload["ok"] is False
    assert payload["error"] == "crosswalk_missing"
    assert payload["detail"]
    assert "validate_evidence_boundary_crosswalk: REFUSED (crosswalk_missing)" in captured.err


def test_a_verified_crosswalk_returns_its_payload_with_a_silent_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The permitting half of the same shape, which is what makes the refusal legible.

    A validator that wrote to stderr on success too would train its operator to ignore
    stderr, and the refusal line above would be lost in the noise it taught them to
    skip. The payload still reports every protected issue as unauthorized — this is a
    verified ARTIFACT, not an authorized close.
    """
    from scripts.gates.validate_evidence_boundary_crosswalk import main as validate_main

    build_protected_world(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["validate", "--repo-root", str(tmp_path), "--crosswalk", CROSSWALK_REL]
    )

    exit_code = validate_main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    payload = yaml.safe_load(captured.out)
    assert payload["ok"] is True
    assert payload["matrix_state"] == "bootstrap"
    assert payload["authorization_status"]["authorizes_protected_close"] is False


def test_an_undeclared_exception_keeps_its_traceback_instead_of_becoming_a_refusal(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A genuine bug must not be rendered as a tidy refusal.

    `run_cli` takes its refusal types explicitly rather than catching everything. If a
    crash printed as `ok: false` like a policy decision, operators would learn that the
    refusal channel is noisy and start reading past it — and the one refusal that
    mattered would be read past with the rest.
    """
    refusal_lib = _load(SCRIPTS / "review" / "closeout_refusal_lib.py", "coverage_refusal_lib")

    def _boom() -> dict:
        raise ValueError("not a declared refusal")

    with pytest.raises(ValueError):
        refusal_lib.run_cli("tool", _boom, refusals=(refusal_lib.RefusalError,))

    assert capsys.readouterr().out == ""


# --- the commit-msg carrier's authorization loader ------------------------------


def test_the_commit_carrier_finds_the_authorization_module_in_the_exported_layout(
    tmp_path: Path,
) -> None:
    """Both install layouts must reach the same authorizer.

    The root repo ships the helper under `skills/public/issue/`; the exported plugin
    ships it under `skills/issue/`. If only the first were searched, every plugin
    install would silently take the module-absent path and authorize protected closes
    it should refuse — the loader is the difference between a gate and a no-op.
    """
    authz = _load(SCRIPTS / "hooks" / "commit_msg_closeout_authorization.py", "coverage_commit_authz")
    exported = tmp_path / "skills" / "issue" / "scripts"
    exported.mkdir(parents=True)
    shutil.copy2(ISSUE_SCRIPTS / "issue_closeout_authorization.py", exported)

    module = authz.load_authorization_module(tmp_path)

    assert module is not None
    assert callable(module.authorize)


def test_an_install_without_the_issue_skill_reports_the_gate_as_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Absence degrades to permissive, and SAYS SO in the record.

    Refusing here would break ordinary commits in every repo that never installed the
    issue skill, and a gate that breaks unrelated work gets deleted. The escape that
    remains is a permissive answer indistinguishable from an authorized one, so the
    record carries `authorization_module_unavailable` and `applies: False` rather than
    a bare `authorized: True` a reader could mistake for a verdict.
    """
    authz = _load(SCRIPTS / "hooks" / "commit_msg_closeout_authorization.py", "coverage_commit_authz_2")
    assert authz.load_authorization_module(tmp_path) is None

    _relocate(monkeypatch, authz, tmp_path / "install" / "scripts")

    report = authz.authorize_commit_carrier(tmp_path, {("corca-ai/charness", 514)}, [], [])

    assert report == {
        "authorized": True,
        "applies": False,
        "crosswalk_status": "authorization_module_unavailable",
    }


def test_an_unloadable_authorization_candidate_is_skipped_not_half_loaded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A present-but-unloadable candidate must not become a partially-initialized gate.

    The loader keeps searching and ends at the same reported-unavailable answer as a
    missing file. The alternative — returning a module whose loader never ran — would
    put a broken object in front of an irreversible close, where the first attribute
    access decides whether the close is refused or crashes past the check.
    """
    authz = _load(SCRIPTS / "hooks" / "commit_msg_closeout_authorization.py", "coverage_commit_authz_3")
    present = tmp_path / "skills" / "public" / "issue" / "scripts"
    present.mkdir(parents=True)
    shutil.copy2(ISSUE_SCRIPTS / "issue_closeout_authorization.py", present)
    monkeypatch.setattr(importlib.util, "spec_from_file_location", _null_spec)

    assert authz.load_authorization_module(tmp_path) is None


# --- the commit-msg refusal an author actually reads ----------------------------


def test_the_commit_hook_tells_a_blocked_author_what_was_refused_and_what_else_is_safe(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """This text is the only diagnostic an author gets mid-commit.

    The generic closeout-ledger footer would send them to fix a ledger field that is
    not the problem, and the likely next move after an unexplained block is `--no-verify`
    — the exact escape. So the refusal names the code, the detail, the protected set,
    and the two legitimate ways out, and states that unrelated closes are unaffected.
    """
    hook = _load(SCRIPTS / "gates" / "check_issue_closeout_commit_msg.py", "coverage_commit_hook")
    _install_empty_git_dir(tmp_path, branch="main")
    build_protected_world(tmp_path)
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text("Repair the boundary\n\nCloses #514\n", encoding="utf-8")

    report = hook.evaluate(tmp_path, message_file, "corca-ai/charness")
    payload = hook.report_payload(report)

    assert report["status"] == "refused"
    # The prose refusal renderer is gone; the payload the hook emits is the only
    # diagnostic left, so every fact the renderer named has to be IN it.
    assert "REFUSED by the evidence-boundary closeout authorization" in payload["summary"]
    authorization = payload["closeout_authorization"]
    assert authorization["refusal"] == "matrix_incomplete"
    assert authorization["protected_issues"] == [514, 515, 518]
    assert authorization["detail"]
    remediation = "\n".join(payload["remediation"])
    assert "bare `#N` reference" in remediation
    assert "unrelated closes are unaffected" in remediation


def test_the_commit_hook_refuses_to_run_at_all_without_its_authorization_sibling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The one loader in this file that must RAISE rather than degrade.

    `commit_msg_closeout_authorization` is not optional context for this hook — it is
    the hook's authorization. Degrading its absence to permissive, as the consumer-facing
    loaders correctly do, would make a broken install of the gate indistinguishable from
    a passing commit, which is the failure the whole lane exists to prevent.
    """
    hook = _load(SCRIPTS / "gates" / "check_issue_closeout_commit_msg.py", "coverage_commit_hook_2")
    monkeypatch.setattr(importlib.util, "spec_from_file_location", _null_spec)

    with pytest.raises(RuntimeError, match="unable to load sibling module"):
        hook._load_sibling("commit_msg_closeout_authorization")


# --- the issue skill's authorization helper -------------------------------------


def test_without_the_crosswalk_module_every_carrier_is_permissive_and_labelled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`authorize`, `enforce`, and `parse_manual_declaration` agree on the absent case.

    All three are consumed by carriers sitting in front of irreversible GitHub writes,
    so a disagreement between them — one permitting while another raises — would make
    which carrier you used decide whether a close went through. `enforce` returning the
    same permissive record it was given is what keeps the raising variant honest.
    """
    module = _load(
        ISSUE_SCRIPTS / "issue_closeout_authorization.py", "coverage_issue_authz_absent"
    )
    _relocate(monkeypatch, module, tmp_path / "elsewhere")

    record = module.authorize(
        invoked_targets=[{"repository": "corca-ai/charness", "issue_number": 514}],
        carrier_targets=[], carrier_source="close-with-comment", repo_root=tmp_path,
    )
    assert record["applies"] is False
    assert record["authorized"] is True
    assert record["refusal"] is None
    assert record["crosswalk_status"] == "authorization_module_unavailable"

    enforced = module.enforce(
        invoked_targets=[{"repository": "corca-ai/charness", "issue_number": 514}],
        carrier_targets=[], carrier_source="close-with-comment", repo_root=tmp_path,
    )
    assert enforced == record

    assert module.parse_manual_declaration("corca-ai/charness#514", "corca-ai/charness", 514) == []


def test_a_bare_manual_declaration_is_refused_because_it_cannot_disagree(
    tmp_path: Path,
) -> None:
    """The declaration exists to be a second, independent statement of intent.

    A bare `514` normalizes against the CLI's own `--repo`, so it restates the very
    argument it is supposed to cross-check. A check that cannot disagree cannot fail,
    and the escape is an operator who supplies `514`, sees the gate accept it, and
    believes an independent confirmation happened.
    """
    module = _load(
        ISSUE_SCRIPTS / "issue_closeout_authorization.py", "coverage_issue_authz_bare"
    )

    with pytest.raises(RuntimeError, match="repository-qualified"):
        module.parse_manual_declaration("514", "corca-ai/charness", 514)

    with pytest.raises(RuntimeError, match="cannot authorize itself"):
        module.parse_manual_declaration(None, "corca-ai/charness", 514)


def test_an_unloadable_crosswalk_candidate_does_not_stop_the_search(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A candidate that cannot be loaded is skipped, not returned half-built.

    The search walks every ancestor because the same helper ships in the root repo and
    in the exported plugin. Returning a module whose loader never ran would hand a
    carrier an object that answers `authorize` with an AttributeError instead of a
    verdict; ending the search at the reported-unavailable record keeps the outcome one
    a caller already knows how to read.
    """
    monkeypatch.setattr(sys, "path", list(sys.path))
    (tmp_path / "scripts" / "evidence").mkdir(parents=True)
    (tmp_path / "scripts" / "evidence").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "evidence" / "evidence_boundary_crosswalk.py").write_text(
        "", encoding="utf-8"
    )
    module = _load(
        ISSUE_SCRIPTS / "issue_closeout_authorization.py", "coverage_issue_authz_skip"
    )
    _relocate(monkeypatch, module, tmp_path / "skills" / "issue" / "scripts")
    monkeypatch.setattr(importlib.util, "spec_from_file_location", _null_spec)

    assert module._load_crosswalk_module() is None
    assert module._CROSSWALK_CACHE["module"] is None


# --- close-with-comment surfaces the real reason, not a fixable-looking one -----


class BackendSpy:
    """Records every backend argv. The assertion is always `== []`."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, argv):
        self.calls.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, json.dumps({"number": 1, "state": "CLOSED"}), "")


def test_a_definitive_refusal_is_reported_instead_of_a_missing_flag(tmp_path: Path) -> None:
    """When no flag could help, the operator must not be sent to supply one.

    With the matrix complete, #514 still refuses on `undecided_projection_dependency`:
    the seam decision has not been made. If `close-with-comment` demanded its
    `--manual-target-declaration` first, the operator would supply it, be refused
    again, and reasonably conclude the gate is arbitrary — which is how a gate gets
    routed around. The comment is never posted either: the spy stays empty.
    """
    build_protected_world(tmp_path, matrix_state="complete")
    close = _load(ISSUE_SCRIPTS / "issue_close.py", "coverage_issue_close")
    spy = BackendSpy()
    close._run_backend = spy
    body = tmp_path / "close-body.md"
    body.write_text("Resolution for #514.\n\nJTBD: close the issue end to end.\n", encoding="utf-8")

    with pytest.raises(RuntimeError) as excinfo:
        close.close_with_comment(
            "corca-ai/charness", 514, body, repo_root=tmp_path, classification="bug"
        )

    assert spy.calls == []
    assert "undecided_projection_dependency" in str(excinfo.value)
    assert "manual-target-declaration" not in str(excinfo.value)


# --- the two read-only ingresses, when the gate is not installed ----------------


def test_draft_validation_without_its_authorization_sibling_stays_permissive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`draft_verified` must not become unreachable in repos with no gate installed.

    The draft validator is where an operator learns whether the close will be
    authorized. In an install without the helper there is nothing to authorize against,
    so the record reports the gate as unavailable and contributes no refusal — the
    draft still faces its ordinary ledger floors, which is the bar it had before.
    """
    draft = _load(
        ISSUE_SCRIPTS / "issue_validate_closeout_draft.py", "coverage_draft_absent"
    )
    _relocate(monkeypatch, draft, tmp_path / "lonely")

    assert draft._authorization_module() is None

    record = draft._authorize_draft(tmp_path, "corca-ai/charness", [514], "direct-commit")

    assert record == {
        "authorized": True,
        "applies": False,
        "crosswalk_status": "authorization_module_unavailable",
    }


def test_the_readback_reports_an_unavailable_gate_rather_than_suppressing_itself(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The post-publication readback must survive a missing gate.

    `verify-closeout --expect-state CLOSED` is the channel that confirms an
    irreversible close actually landed. Raising here because the authorization helper
    could not be reached would destroy that confirmation over a check with nothing left
    to protect, so the record degrades and stays reported-only.
    """
    # No `skill_runtime_bootstrap.py` sits above `tmp_path/nohost/scripts`, which is
    # the real shape of a skill vendored into a host without the repo root beside it.
    verify = _load(ISSUE_SCRIPTS / "issue_verify_closeout.py", "coverage_verify_absent")
    _relocate(monkeypatch, verify, tmp_path / "nohost" / "scripts")

    assert verify._resolve_bootstrap() is None

    record = verify._authorization_record(tmp_path, "corca-ai/charness", [514], "pr-body")

    assert record == {
        "applies": False,
        "authorized": True,
        "crosswalk_status": "authorization_module_unavailable",
    }
