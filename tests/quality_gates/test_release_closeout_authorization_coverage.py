"""What a release closeout is authorized to do when its authorization surface is
only PARTIALLY installed.

`release_closeout_authorization.py` is the single place the release lane asks whether
an issue may be closed at all, and it sits in front of an irreversible boundary: a
temp carrier write, a version bump, a publish, a `gh issue close`. Its loader has
four distinct absence paths (no sibling loader spec, no issue skill on disk, an
unloadable candidate, an exhausted candidate list) and each one answers the same
question differently only in HOW it degrades — the answer itself is always
"permissive", so each path must be shown to reach that answer deliberately rather
than by crashing, and the permissive answer must be shown to be the one a
fully-installed repo does NOT give for a protected target.

The escape each test guards:

- a partial vendoring must not turn a typed refusal into an `ImportError` traceback
  (an operator who cannot read the refusal reaches for `--no-verify` next), and
- the permissive degrade must stay scoped to installs with nothing to protect — the
  paired protected-world test proves a complete install still refuses #514, so the
  degrade cannot be mistaken for "release closes are unguarded everywhere".

No GitHub contact and no publication happens anywhere in this file: every test either
refuses before the first side effect or runs a loader that never reaches a backend.
"""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

from tests.closeout_authorization_world import build_protected_world

REPO_ROOT = Path(__file__).resolve().parents[2]
RELEASE_SCRIPTS = REPO_ROOT / "skills" / "public" / "release" / "scripts"
# The production files this suite measures, written as repo-relative literals.
#
# This is not decoration. The release-final changed-line lane maps tests to files
# TEXTUALLY (`suggest_mutation_coverage_command`), and every path below is otherwise
# assembled as `RELEASE_SCRIPTS / "..."` — a variable the mapper cannot follow. With no
# match it instruments no test for these files and blocks them as uncovered, which is a
# FALSE STOP: the coverage exists and the broad producer measures it at 100%/86%/85%.
# That is the same mapper blind spot the producer's own docstring already records for
# `seed_dup_review.py`, hit from the other side.
#
# Keeping the list here rather than widening the mapper's regex is deliberate: a literal
# says which production files this suite claims to cover, which a reader can check.
COVERS = (
    "skills/public/release/scripts/release_closeout_authorization.py",
    "skills/public/release/scripts/release_issue_closeout.py",
    "skills/public/release/scripts/release_closeout_floors.py",
    "skills/public/release/scripts/release_issue_closeout_message.py",
)

AUTHZ_PATH = RELEASE_SCRIPTS / "release_closeout_authorization.py"
CLOSEOUT_PATH = RELEASE_SCRIPTS / "release_issue_closeout.py"
FLOORS_PATH = RELEASE_SCRIPTS / "release_closeout_floors.py"


def _load(path: Path, name: str, *, as_file: Path | None = None):
    """Execute the REAL repo file, optionally pretending it lives at `as_file`.

    `module_from_spec` sets `__file__` before `exec_module` runs, so overriding it
    first makes every `Path(__file__)`-relative lookup resolve inside a synthetic
    install tree while the executed bytecode — and therefore coverage attribution —
    stays on this repo's real script. Copying the script into the tree instead would
    measure the copy and leave the shipped file unproven.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    if as_file is not None:
        module.__file__ = str(as_file)
    spec.loader.exec_module(module)
    return module


def _release_scripts_tree(tmp_path: Path, *, sibling: bool = True) -> Path:
    """A synthetic `skills/public/release/scripts/` install with no issue skill."""
    scripts = tmp_path / "pkg" / "skills" / "public" / "release" / "scripts"
    scripts.mkdir(parents=True)
    if sibling:
        shutil.copy2(CLOSEOUT_PATH, scripts / "release_issue_closeout.py")
        # The loader now borrows `_package_root` from the floors module, which owns the
        # cross-skill resolution; a vendored tree without it cannot answer at all.
        shutil.copy2(FLOORS_PATH, scripts / "release_closeout_floors.py")
    return scripts


def _seed_issue_authorization(tmp_path: Path) -> None:
    issue_scripts = tmp_path / "pkg" / "skills" / "public" / "issue" / "scripts"
    issue_scripts.mkdir(parents=True)
    (issue_scripts / "issue_closeout_authorization.py").write_text(
        "def authorize(**_kwargs):\n    return {'authorized': True}\n",
        encoding="utf-8",
    )


def _spec_none_for(module_name: str):
    """Real `spec_from_file_location`, except it refuses to produce a spec for one
    module name — the in-process stand-in for a candidate file that exists but cannot
    be loaded (unreadable, truncated, or wrong-architecture bytecode)."""
    real = importlib.util.spec_from_file_location

    def fake(name, location, *args, **kwargs):
        if name == module_name:
            return None
        return real(name, location, *args, **kwargs)

    return fake


# --- release_closeout_authorization: the four absence paths ----------------


def test_authorization_loader_returns_none_when_its_own_sibling_loader_is_unusable(
    monkeypatch,
) -> None:
    """The loader borrows `release_closeout_floors._package_root` to find the issue
    skill. If that sibling cannot even be turned into a module spec, the release lane
    has no way to locate the authorization logic — it must answer "not installed"
    (None) rather than raise, because this code runs at the top of every release
    close, including the ones that close nothing protected.
    """
    authz = _load(AUTHZ_PATH, "release_closeout_authorization_sibling_unusable")
    monkeypatch.setattr(
        authz.importlib.util,
        "spec_from_file_location",
        _spec_none_for("release_closeout_package_root"),
    )

    assert authz.load_closeout_authorization() is None

    # And the refusal entrypoint above it degrades to permissive rather than raising:
    # an install this broken has no crosswalk artifact and therefore nothing to guard.
    result = authz.refuse_unauthorized_release_close(
        Path("."), repo="corca-ai/charness", issue_numbers=[514], carrier_source="release"
    )
    assert result == {"authorized": True, "applies": False, "carrier_source": "release"}


def test_authorization_loader_returns_none_when_no_issue_skill_is_vendored(tmp_path: Path) -> None:
    """`release` vendored without `issue`: neither the source-tree nor the installed
    candidate path exists, so both are skipped and the loader reports absence.

    This is the legitimate install the module's docstring names. Refusing every
    release close here would break release for consumers who never had the protected
    surface — the teeth live in the consuming repo's crosswalk artifact.
    """
    scripts = _release_scripts_tree(tmp_path)
    authz = _load(
        AUTHZ_PATH,
        "release_closeout_authorization_no_issue_skill",
        as_file=scripts / "release_closeout_authorization.py",
    )

    assert authz.load_closeout_authorization() is None
    assert authz.refuse_unauthorized_release_close(
        tmp_path, repo="corca-ai/charness", issue_numbers=[514, 515], carrier_source="publish-resume"
    ) == {"authorized": True, "applies": False, "carrier_source": "publish-resume"}


def test_authorization_loader_skips_a_present_but_unloadable_issue_helper(
    tmp_path: Path, monkeypatch
) -> None:
    """The issue skill's authorization file is PRESENT but cannot be loaded.

    The loop must not treat "found a file" as "found the logic": it skips the
    unloadable candidate, tries the other layout, and ends at absence. Returning a
    half-initialized module here would hand the release lane an object whose
    `authorize` call fails deep inside an irreversible sequence instead of before it.
    """
    scripts = _release_scripts_tree(tmp_path)
    _seed_issue_authorization(tmp_path)
    authz = _load(
        AUTHZ_PATH,
        "release_closeout_authorization_unloadable_candidate",
        as_file=scripts / "release_closeout_authorization.py",
    )
    monkeypatch.setattr(
        authz.importlib.util,
        "spec_from_file_location",
        _spec_none_for("release_issue_closeout_authorization"),
    )

    assert authz.load_closeout_authorization() is None


def test_authorization_loader_finds_a_vendored_issue_helper_in_the_source_layout(
    tmp_path: Path,
) -> None:
    """Counterpart to the three absence tests: when the issue skill IS vendored, the
    same loop loads it, so the absence answers above are a real fork in behavior and
    not the only thing this loader can do.
    """
    scripts = _release_scripts_tree(tmp_path)
    _seed_issue_authorization(tmp_path)
    authz = _load(
        AUTHZ_PATH,
        "release_closeout_authorization_present_candidate",
        as_file=scripts / "release_closeout_authorization.py",
    )

    module = authz.load_closeout_authorization()
    assert module is not None
    assert module.authorize()["authorized"] is True


def test_release_close_of_no_issues_is_authorized_without_consulting_the_crosswalk() -> None:
    """A release that closes nothing is not a closeout at all.

    The empty-target early answer must be `applies: False` — reporting "authorized"
    for a close that was never requested would let a later reader treat this record
    as evidence that some target passed the gate.
    """
    authz = _load(AUTHZ_PATH, "release_closeout_authorization_empty_targets")

    result = authz.refuse_unauthorized_release_close(
        REPO_ROOT, repo="corca-ai/charness", issue_numbers=[], carrier_source="release"
    )

    assert result == {"authorized": True, "applies": False, "carrier_source": "release"}


def test_a_complete_install_still_refuses_a_protected_target(tmp_path: Path) -> None:
    """The bound on every permissive answer above.

    With the issue skill present and a real crosswalk in the repo, the same
    entrypoint refuses #514 by raising before any bump, publish, or `gh` call. This
    is what the degraded installs give up, and it is why the degrade must never be
    read as "release closes are unguarded".
    """
    build_protected_world(tmp_path)
    authz = _load(AUTHZ_PATH, "release_closeout_authorization_protected_world")

    with pytest.raises(SystemExit, match="REFUSED"):
        authz.refuse_unauthorized_release_close(
            tmp_path, repo="corca-ai/charness", issue_numbers=[514], carrier_source="release"
        )


def test_a_complete_install_still_authorizes_an_unrelated_target(tmp_path: Path) -> None:
    """Blast radius of the guard itself: on the same complete install, a release
    closing an issue the crosswalk does not protect is authorized and returns the
    real authorization record. A gate that quietly refused every release close would
    be removed within a week, taking the protection with it.
    """
    build_protected_world(tmp_path)
    authz = _load(AUTHZ_PATH, "release_closeout_authorization_unrelated_target")

    result = authz.refuse_unauthorized_release_close(
        tmp_path, repo="corca-ai/charness", issue_numbers=[9001], carrier_source="release"
    )

    assert result["authorized"] is True


# --- release_issue_closeout: the re-export degrades the same way -----------


def test_release_issue_closeout_reexport_degrades_when_authorization_script_is_absent(
    tmp_path: Path,
) -> None:
    """A partial vendoring that copies some release scripts but not
    `release_closeout_authorization.py`.

    `release_issue_closeout` re-exports the refusal so every release caller keeps one
    import site; when the backing script is missing it must answer with a TYPED
    record naming `authorization_module_unavailable`, not an `ImportError` traceback.
    The traceback is the escape: it hides which capability is missing, and it fires on
    release commands that never asked to close an issue.

    Exercised in-process against the real repo file (via an overridden `__file__`)
    rather than a `shutil.copy` into tmp_path, because a copied script's executed
    lines are attributed to the copy and leave the shipped file's degrade unmeasured.
    """
    scripts = tmp_path / "pkg" / "skills" / "public" / "release" / "scripts"
    scripts.mkdir(parents=True)
    closeout = _load(
        CLOSEOUT_PATH,
        "release_issue_closeout_partial_vendoring",
        as_file=scripts / "release_issue_closeout.py",
    )

    assert closeout._load_authorization_module() is None

    result = closeout.refuse_unauthorized_release_close(
        tmp_path, repo="corca-ai/charness", issue_numbers=[514], carrier_source="release"
    )

    assert result == {
        "authorized": True,
        "applies": False,
        "carrier_source": "release",
        "crosswalk_status": "authorization_module_unavailable",
    }


def test_release_issue_closeout_reexport_delegates_when_the_script_is_present() -> None:
    """On a complete install the re-export is a pass-through, not a second copy of
    the authorization logic — the record it returns carries no
    `crosswalk_status: authorization_module_unavailable` marker, so a reader can tell
    a real authorization from a degraded one.
    """
    closeout = _load(CLOSEOUT_PATH, "release_issue_closeout_complete_install")

    assert closeout._load_authorization_module() is not None

    result = closeout.refuse_unauthorized_release_close(
        REPO_ROOT, repo="corca-ai/charness", issue_numbers=[], carrier_source="release"
    )

    assert result["applies"] is False
    assert result.get("crosswalk_status") != "authorization_module_unavailable"


# --- release_issue_closeout_message: the temp-carrier re-authorization -----


def test_message_reauthorization_is_a_no_op_when_no_issue_is_being_closed() -> None:
    """The message helper re-authorizes before writing its temp commit-message file,
    because it is separately importable and reachable without the release preflight
    having run in this process.

    With no issue numbers there is no close to authorize, so it must return quietly
    rather than consult the crosswalk. Raising or refusing here would break every
    release commit-message render that closes nothing — the common case — and an
    operator whose ordinary release stops working routes around the whole helper,
    which is how the temp-carrier check gets lost.
    """
    message = _load(
        RELEASE_SCRIPTS / "release_issue_closeout_message.py", "release_message_no_targets"
    )
    assert message._ISSUE_AUTHZ is not None  # the guard is genuinely installed here

    assert message._refuse_unauthorized_message(REPO_ROOT, "corca-ai/charness", []) is None


def test_message_reauthorization_degrades_when_the_issue_skill_is_not_vendored(
    tmp_path: Path,
) -> None:
    """Same early return, reached the other way: `release` vendored without `issue`.

    The authorization module is absent, so the temp carrier is written without a
    crosswalk check — deliberately, because such an install has no crosswalk artifact
    to check against. What must NOT happen is an `AttributeError` on `None.authorize`
    at the moment a release is mid-flight.
    """
    scripts = _release_scripts_tree(tmp_path, sibling=False)
    message = _load(
        RELEASE_SCRIPTS / "release_issue_closeout_message.py",
        "release_message_partial_vendoring",
        as_file=scripts / "release_issue_closeout_message.py",
    )
    assert message._ISSUE_AUTHZ is None

    assert message._refuse_unauthorized_message(tmp_path, "corca-ai/charness", [514]) is None
