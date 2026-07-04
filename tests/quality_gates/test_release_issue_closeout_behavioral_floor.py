"""North-star finding: release-driven issue closes bypassed the rung-1
behavioral-verdict presence floor the issue skill's own closeout already
enforces, and relabeled a `state==CLOSED` re-read as `verified` -- a P4
same-proxy masquerade. This proves the release close-issue boundary now:

- refuses (fails BEFORE any GitHub call) when a closed issue carries no
  `Behavior #N:` line or typed non-`verified` disposition;
- reports exactly which issue numbers are missing when some, not all, are
  covered;
- threads a present behavioral-verdict line into both closeout carriers (the
  release commit body and the manual-fallback close comment); and
- records the close-mutation re-read as `state-verified`, never `verified`.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "public" / "release" / "scripts"


def _load(name: str):
    return _load_path(_SCRIPTS / f"{name}.py")


def _load_path(path: Path):
    spec = importlib.util.spec_from_file_location(f"{path.stem}_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CLOSEOUT = _load("release_issue_closeout")


def _fake_run(states: dict[str, str], calls: list[list[str]]):
    def run(command, *, cwd, check=True):
        calls.append(command)
        if command[:3] == ["gh", "issue", "view"]:
            number = command[3]
            payload = {"number": int(number), "state": states.get(number, "OPEN"), "url": f"https://x/{number}"}
            return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")
        if command[:3] == ["gh", "issue", "close"]:
            number = command[3]
            states[number] = "CLOSED"
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(f"unexpected command: {command}")

    return run


# --- rung-1 presence floor: evaluate_release_behavioral_verdict -----------


def test_evaluate_release_behavioral_verdict_refuses_silence() -> None:
    verdict = _CLOSEOUT.evaluate_release_behavioral_verdict([], [44])
    assert verdict["ok"] is False
    assert verdict["missing"] == [44]


def test_evaluate_release_behavioral_verdict_reports_missing_per_issue() -> None:
    verdict = _CLOSEOUT.evaluate_release_behavioral_verdict(["Behavior #44: confirmed via fresh checkout"], [44, 45])
    assert verdict["ok"] is False
    assert verdict["missing"] == [45]


def test_evaluate_release_behavioral_verdict_passes_confirmation_and_typed_disposition_equally() -> None:
    # F2a: a confirmation and a typed non-`verified` disposition pass EQUALLY --
    # this floor is presence-only and never judges which is more honest.
    confirmed = _CLOSEOUT.evaluate_release_behavioral_verdict(["Behavior #44: confirmed via fresh checkout"], [44])
    disposed = _CLOSEOUT.evaluate_release_behavioral_verdict(["Behavior #45: blocked-needs-capability"], [45])
    assert confirmed["ok"] is True
    assert disposed["ok"] is True


def test_evaluate_release_behavioral_verdict_not_applicable_when_no_issues() -> None:
    # A release that closes no issue never reaches the floor at all -- the
    # early return, on the REAL module (loaded once at collection time above,
    # not a tmp-path copy), must short-circuit before touching
    # `_ISSUE_CLOSEOUT_BODY` at all.
    verdict = _CLOSEOUT.evaluate_release_behavioral_verdict([], [])
    assert verdict == {"applies": False, "ok": True, "missing": []}


def test_evaluate_release_behavioral_verdict_refuses_with_typed_message_on_the_real_module(
    monkeypatch,
) -> None:
    # On a normal source-tree checkout `_ISSUE_CLOSEOUT_BODY` loads successfully
    # (the module-level absence-degrade tests below prove the None path only on
    # a tmp-path COPY). Forcing the module ATTRIBUTE to None here exercises the
    # same "helper missing" SystemExit on the REAL loaded module/file, with a
    # non-empty issue_numbers so the floor is actually reached (unlike the
    # empty-list early return above).
    monkeypatch.setattr(_CLOSEOUT, "_ISSUE_CLOSEOUT_BODY", None)
    monkeypatch.setattr(_CLOSEOUT, "_ISSUE_CLOSEOUT_BODY_ERROR", "issue_verify_closeout_body.py not found (forced)")
    with pytest.raises(SystemExit, match="issue_verify_closeout_body.py"):
        _CLOSEOUT.evaluate_release_behavioral_verdict(["Behavior #44: confirmed via fresh checkout"], [44])


# --- preflight_release_issues: fails BEFORE any GitHub mutation -----------


def test_preflight_refuses_before_any_github_call_when_behavior_missing() -> None:
    def run_never_called(*_args, **_kwargs):
        raise AssertionError("preflight must refuse before any GitHub call when behavior is missing")

    payload: dict = {}
    with pytest.raises(SystemExit, match="missing per-issue behavioral-verdict line"):
        _CLOSEOUT.preflight_release_issues(
            Path("."), repo="example/demo", issue_numbers=[44], payload=payload, run=run_never_called,
        )
    assert payload["issue_closeout_behavioral_verdict"]["ok"] is False
    assert "issue_closeout_preflight" not in payload  # never reached the GH-view loop


def test_preflight_proceeds_when_behavior_present() -> None:
    calls: list[list[str]] = []
    payload: dict = {}
    _CLOSEOUT.preflight_release_issues(
        Path("."), repo="example/demo", issue_numbers=[44], payload=payload,
        run=_fake_run({"44": "OPEN"}, calls),
        behavior_lines=["Behavior #44: confirmed via fresh checkout install"],
    )
    assert payload["issue_closeout_behavioral_verdict"]["ok"] is True
    assert payload["issue_closeout_preflight"]["status"] == "verified"
    assert calls == [["gh", "issue", "view", "44", "--repo", "example/demo", "--json", "number,state,url"]]


# --- carrier threading: the present line rides both closeout carriers -----


def test_release_commit_body_includes_behavior_lines() -> None:
    payload = {"tag_name": "v1.0.0", "quality_command": "make quality"}
    body = _CLOSEOUT.release_commit_body(payload, [44], ["Behavior #44: confirmed via fresh checkout install"])
    assert "Close #44." in body
    assert "Behavior #44: confirmed via fresh checkout install" in body


def test_manual_fallback_comment_includes_behavior_lines() -> None:
    calls: list[list[str]] = []
    payload = {"tag_name": "v1.0.0", "release_url": "https://x/v1.0.0", "commit_sha": "abc123"}
    _CLOSEOUT.ensure_release_issues_closed(
        Path("."), repo="example/demo", issue_numbers=[44], payload=payload,
        run=_fake_run({"44": "OPEN"}, calls),
        behavior_lines=["Behavior #44: confirmed via fresh checkout install"],
    )
    close_call = next(call for call in calls if call[:3] == ["gh", "issue", "close"])
    comment = close_call[close_call.index("--comment") + 1]
    assert "Behavior #44: confirmed via fresh checkout install" in comment


# --- state-verified rename: a CLOSED re-read is never `verified` ----------


def test_ensure_release_issues_closed_records_state_verified_not_verified() -> None:
    calls: list[list[str]] = []
    payload = {"tag_name": "v1.0.0", "release_url": "https://x/v1.0.0", "commit_sha": "abc123"}
    _CLOSEOUT.ensure_release_issues_closed(
        Path("."), repo="example/demo", issue_numbers=[44], payload=payload,
        run=_fake_run({"44": "OPEN"}, calls),
        behavior_lines=["Behavior #44: confirmed via fresh checkout install"],
    )
    assert payload["issue_closeout"]["status"] == "state-verified"
    assert payload["issue_closeout"]["status"] != "verified"


# --- portability: degrade to absence, never crash the whole release CLI ---
#
# The tests below copy release_issue_closeout.py into a fresh tmp_path tree and
# import THAT COPY, so coverage.py attributes the executed lines to the tmp
# path, never to this repo's real file (the #393 subprocess/copy-attribution
# class). `_package_root` and `_load_issue_closeout_body_lib` are plain
# functions on the already-loaded `_CLOSEOUT` module object (bound to the real
# repo file above), so calling them directly here -- with synthetic inputs or a
# monkeypatched loader seam -- exercises the real file's branches in-process.


def test_package_root_resolves_installed_layout() -> None:
    # The source-tree pattern ("skills","public","release","scripts") does not
    # match an installed-plugin path; the second loop's installed pattern
    # ("skills","release","scripts") must be checked and match instead.
    path = Path("/opt/plugin/skills/release/scripts/release_issue_closeout.py")
    package_root, installed_first = _CLOSEOUT._package_root(path)
    assert package_root == Path("/opt/plugin")
    assert installed_first is True


def test_package_root_raises_when_neither_layout_matches() -> None:
    with pytest.raises(ImportError, match="cannot resolve release package root"):
        _CLOSEOUT._package_root(Path("/nowhere/foo.py"))


def test_load_issue_closeout_body_lib_covers_missing_and_unloadable_candidates(
    tmp_path: Path, monkeypatch
) -> None:
    # First rel candidate missing (loop `continue`s past it), second rel
    # candidate present but `spec_from_file_location` forced to return None (the
    # `if spec is None or spec.loader is None: continue` branch), so the loop
    # exhausts to the final "not found" raise -- all three in one pass.
    package_root = tmp_path / "pkg"
    (package_root / "skills" / "issue" / "scripts").mkdir(parents=True)
    (package_root / "skills" / "issue" / "scripts" / "issue_verify_closeout_body.py").write_text(
        "OK = True\n", encoding="utf-8"
    )
    monkeypatch.setattr(_CLOSEOUT, "_package_root", lambda _here: (package_root, False))
    monkeypatch.setattr(_CLOSEOUT.importlib.util, "spec_from_file_location", lambda *_a, **_k: None)

    with pytest.raises(ImportError, match="issue_verify_closeout_body.py not found"):
        _CLOSEOUT._load_issue_closeout_body_lib()


def test_module_level_absence_degrade_records_error_on_the_real_file(tmp_path: Path) -> None:
    # Covers the module-level `try/except ImportError` (lines ~67-72) itself, in
    # the REAL repo file: `module_from_spec` sets `__file__` before `exec_module`
    # runs, so overriding it to an isolated path (no ancestor skills/... layout)
    # BEFORE `exec_module` makes `_load_issue_closeout_body_lib()` raise while the
    # bytecode still executes from -- and coverage still attributes to -- this
    # repo's `release_issue_closeout.py` (confirmed via the loader's `spec.origin`,
    # unlike `test_module_import_survives_missing_issue_skill` below which loads a
    # tmp_path COPY and so cannot attribute to the real file).
    isolated_file = tmp_path / "nowhere" / "release_issue_closeout.py"
    isolated_file.parent.mkdir(parents=True)
    spec = importlib.util.spec_from_file_location("release_issue_closeout_reexec", _SCRIPTS / "release_issue_closeout.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(isolated_file)
    spec.loader.exec_module(module)  # must not raise -- degrades to absence

    assert module._ISSUE_CLOSEOUT_BODY is None
    assert module._ISSUE_CLOSEOUT_BODY_ERROR is not None
    assert "cannot resolve release package root" in module._ISSUE_CLOSEOUT_BODY_ERROR


def test_module_import_survives_missing_issue_skill(tmp_path: Path) -> None:
    # Simulate a portable install where the issue skill is not vendored
    # alongside release: an isolated `skills/public/release/scripts/` tree with
    # no sibling `skills/public/issue` (or `skills/issue`) for the cross-skill
    # loader's candidate paths to resolve. Importing must NOT raise -- every
    # release command that never touches --close-issue has to keep working.
    fake_scripts = tmp_path / "skills" / "public" / "release" / "scripts"
    fake_scripts.mkdir(parents=True)
    shutil.copy2(_SCRIPTS / "release_issue_closeout.py", fake_scripts / "release_issue_closeout.py")

    module = _load_path(fake_scripts / "release_issue_closeout.py")  # must not raise

    assert module._ISSUE_CLOSEOUT_BODY is None
    assert module._ISSUE_CLOSEOUT_BODY_ERROR is not None


def test_no_close_issue_still_works_when_issue_skill_missing(tmp_path: Path) -> None:
    fake_scripts = tmp_path / "skills" / "public" / "release" / "scripts"
    fake_scripts.mkdir(parents=True)
    shutil.copy2(_SCRIPTS / "release_issue_closeout.py", fake_scripts / "release_issue_closeout.py")
    module = _load_path(fake_scripts / "release_issue_closeout.py")

    # (a) a release that does not close any issue is unaffected by the absence.
    verdict = module.evaluate_release_behavioral_verdict([], [])
    assert verdict == {"applies": False, "ok": True, "missing": []}
    payload: dict = {}
    module.preflight_release_issues(
        tmp_path, repo="example/demo", issue_numbers=[], payload=payload, run=None,
    )
    assert payload["issue_closeout_preflight"]["status"] == "not_requested"


def test_close_issue_refuses_with_typed_message_when_issue_skill_missing(tmp_path: Path) -> None:
    fake_scripts = tmp_path / "skills" / "public" / "release" / "scripts"
    fake_scripts.mkdir(parents=True)
    shutil.copy2(_SCRIPTS / "release_issue_closeout.py", fake_scripts / "release_issue_closeout.py")
    module = _load_path(fake_scripts / "release_issue_closeout.py")

    # (b) --close-issue with the lib missing refuses with a typed message
    # naming the missing capability, not a bare traceback (AttributeError on
    # `None.evaluate_behavioral_verdict`).
    with pytest.raises(SystemExit, match="issue_verify_closeout_body.py"):
        module.evaluate_release_behavioral_verdict(["Behavior #44: x"], [44])

    def run_never_called(*_args, **_kwargs):
        raise AssertionError("must refuse before any GitHub call")

    payload: dict = {}
    with pytest.raises(SystemExit, match="issue_verify_closeout_body.py"):
        module.preflight_release_issues(
            tmp_path, repo="example/demo", issue_numbers=[44], payload=payload, run=run_never_called,
        )
