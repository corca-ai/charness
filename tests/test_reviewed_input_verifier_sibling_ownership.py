"""Which `reviewed_input_identity` the shipped verifier resolves.

This module ships to consumer repos and is loaded BY FILE PATH by the reviewer
carrier, precisely because there is no trustworthy package context there. So
"which sibling owns the identity" has to be answered from the file's own
directory, not from whatever happens to be importable.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

from tests.module_eviction import evict_module

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts" / "review" / "reviewed_input_verification.py"


def _load_by_path():
    spec = importlib.util.spec_from_file_location("verifier_under_test", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_consumer_module_of_the_same_name_cannot_substitute_the_owner(monkeypatch) -> None:
    """A preloaded `scripts.review.reviewed_input_identity` used to win outright.

    The verifier tried the package import BEFORE its file-relative fallback, so a
    consumer repo carrying its own module of that name supplied the constants and
    the reconstruction the packet verdict rests on. A fresh-eye review proved the
    substitution by preloading a synthetic module.
    """
    fake = types.ModuleType("scripts.review.reviewed_input_identity")
    fake.ALGORITHM = "consumer-owned"
    fake.__file__ = "/tmp/definitely-not-charness/scripts/review/reviewed_input_identity.py"
    monkeypatch.setitem(sys.modules, "scripts.review.reviewed_input_identity", fake)

    module = _load_by_path()

    assert module.ALGORITHM != "consumer-owned"
    assert module.ALGORITHM == "sha256-v2"


def test_an_already_imported_owner_is_reused_when_it_is_the_same_file() -> None:
    """Reuse is required, not an optimisation.

    Re-executing the sibling would build a SECOND module object, and the owner
    would stop being authoritative under monkeypatch — the same import-time
    aliasing defect this split already had to undo once.
    """
    from scripts.review import reviewed_input_identity as owner

    module = _load_by_path()

    assert module._identity is owner


def test_the_verifier_resolves_its_own_adjacent_sibling(monkeypatch) -> None:
    """With nothing preloaded, the answer still comes from the file's directory."""
    evict_module(monkeypatch, "scripts.review.reviewed_input_identity")

    module = _load_by_path()

    assert Path(module._identity.__file__).resolve() == (
        VERIFIER.with_name("reviewed_input_identity.py")
    )


def test_the_owner_is_the_same_object_whichever_module_loads_first(monkeypatch) -> None:
    """Which object you get must not depend on who imported first.

    The first cut of the substitution fix reused an already-imported owner but
    fell back to a by-path load when the canonical name was unbound — so loading
    the verifier BEFORE `scripts.review.reviewed_input_identity` produced a second module
    object, and patching either left the other stale. That traded one
    ambient-state dependency for another; a full-suite run caught it.
    """
    evict_module(monkeypatch, "scripts.review.reviewed_input_identity")

    verifier_first = _load_by_path()
    from scripts.review import reviewed_input_identity as owner

    assert verifier_first._identity is owner


IDENTITY = ROOT / "scripts" / "review" / "reviewed_input_identity.py"


def _load_identity_by_path():
    spec = importlib.util.spec_from_file_location("identity_under_test", IDENTITY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_consumer_module_cannot_substitute_the_nonblob_binder(monkeypatch) -> None:
    """The non-blob split re-opened the same surface, so it gets the same guard.

    Two defects came out of this pattern already — a consumer module winning the
    name, and an import-order-dependent second object — so the third application
    is written against both from the start rather than after a review finds them.
    """
    fake = types.ModuleType("scripts.review.reviewed_input_nonblob")
    fake.CURRENT_POINTER_FILENAME = "consumer-owned.md"
    fake._current_pointer_payload = lambda *_a, **_k: None
    fake._gitlink_sha256 = lambda *_a, **_k: None
    fake.__file__ = "/tmp/definitely-not-charness/scripts/review/reviewed_input_nonblob.py"
    monkeypatch.setitem(sys.modules, "scripts.review.reviewed_input_nonblob", fake)

    module = _load_identity_by_path()

    assert module._nonblob.CURRENT_POINTER_FILENAME == "latest.md"


def test_the_nonblob_owner_is_the_same_object_whichever_loads_first(monkeypatch) -> None:
    evict_module(monkeypatch, "scripts.review.reviewed_input_nonblob")

    identity_first = _load_identity_by_path()
    from scripts.review import reviewed_input_nonblob as owner

    assert identity_first._nonblob is owner


def test_identity_resolves_the_repository_changed_path_owner(monkeypatch) -> None:
    """A consumer's same-named module cannot replace the changed-path owner."""
    fake = types.ModuleType("scripts.adapters.surfaces_lib")
    fake.__file__ = "/tmp/consumer/scripts/adapters/surfaces_lib.py"
    monkeypatch.setitem(sys.modules, "scripts.adapters.surfaces_lib", fake)

    module = _load_identity_by_path()

    assert (
        Path(module._changed_path_owner.__file__).resolve()
        == (ROOT / "scripts" / "adapters" / "surfaces_lib.py").resolve()
    )


def test_a_consumer_module_cannot_substitute_the_path_selection_owner(monkeypatch) -> None:
    fake = types.ModuleType("scripts.review.reviewed_input_path_selection")
    fake.changed_path_owner = types.SimpleNamespace(__file__="/tmp/consumer/surfaces_lib.py")
    fake.auto_paths = lambda *_args: ["consumer-owned"]
    fake.lexical_path = Path
    fake.checked_path = lambda root, path: root / path
    fake.__file__ = "/tmp/consumer/scripts/review/reviewed_input_path_selection.py"
    monkeypatch.setitem(sys.modules, "scripts.review.reviewed_input_path_selection", fake)

    module = _load_identity_by_path()

    assert Path(module._path_selection.__file__).resolve() == (
        IDENTITY.with_name("reviewed_input_path_selection.py").resolve()
    )


def test_a_consumer_module_cannot_substitute_the_range_owner(monkeypatch) -> None:
    fake = types.ModuleType("scripts.review.reviewed_input_range")
    fake.__file__ = "/tmp/consumer/scripts/review/reviewed_input_range.py"
    fake.range_endpoints = lambda *_args: (None, "consumer-owned")
    monkeypatch.setitem(sys.modules, "scripts.review.reviewed_input_range", fake)

    module = _load_identity_by_path()

    assert Path(module._range.__file__).resolve() == (
        IDENTITY.with_name("reviewed_input_range.py").resolve()
    )


def test_a_consumer_module_cannot_substitute_the_worktree_owner(monkeypatch) -> None:
    fake = types.ModuleType("scripts.review.reviewed_input_worktree")
    fake.__file__ = "/tmp/consumer/scripts/review/reviewed_input_worktree.py"
    fake.capture = lambda *_args: None
    monkeypatch.setitem(sys.modules, "scripts.review.reviewed_input_worktree", fake)

    module = _load_identity_by_path()

    assert Path(module._worktree.__file__).resolve() == (
        IDENTITY.with_name("reviewed_input_worktree.py").resolve()
    )
