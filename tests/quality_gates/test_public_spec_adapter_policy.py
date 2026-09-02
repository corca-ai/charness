"""The exported quality skill reaches repo scripts through the layout resolver (#777)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"


def _load(name: str):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


policy = _load("public_spec_adapter_policy")
inventory_lib = _load("public_spec_inventory_lib")


def test_repo_script_module_loads_a_flat_repo_script_through_the_resolver() -> None:
    module = policy.repo_script_module("quality_policy_defaults")
    assert module is not None
    assert (
        module.DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT == policy.DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT
    )


def test_repo_script_module_returns_none_for_a_script_that_does_not_exist() -> None:
    assert policy.repo_script_module("definitely_not_a_repo_script_777") is None


def test_repo_script_module_returns_none_where_no_tree_root_resolves(monkeypatch) -> None:
    # A consumer install with no `scripts/adapter_lib.py` above the skill keeps the
    # exported defaults rather than crashing at import.
    class _Runtime:
        @staticmethod
        def repo_root_from_skill_script(_file):
            raise RuntimeError("no tree root")

    monkeypatch.setattr(policy, "_load_skill_runtime_bootstrap", lambda: _Runtime())
    assert policy.repo_script_module("quality_policy_defaults") is None


def test_vendored_prefixes_read_the_adapter_through_the_resolved_lib() -> None:
    assert inventory_lib._VENDORED_LIB is not None
    prefixes = inventory_lib._vendored_prefixes({"vendored_paths": ["third_party/"]})
    assert prefixes and all(isinstance(prefix, str) for prefix in prefixes)


def test_the_shim_refuses_when_no_ancestor_carries_the_skill_runtime_bootstrap(monkeypatch) -> None:
    class _NoParents:
        def resolve(self):
            return self

        parents = ()

    monkeypatch.setattr(policy, "Path", lambda _file: _NoParents())
    import pytest

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        policy._load_skill_runtime_bootstrap()


def test_repo_script_module_returns_none_when_no_loader_spec_can_be_built(monkeypatch) -> None:
    # The bootstrap itself runs through runpy, which builds a spec the same way, so
    # it is resolved first and the patch reaches only the repo script's loader.
    runtime = policy._load_skill_runtime_bootstrap()
    monkeypatch.setattr(policy, "_load_skill_runtime_bootstrap", lambda: runtime)
    monkeypatch.setattr(policy.importlib.util, "spec_from_file_location", lambda *_a, **_k: None)
    assert policy.repo_script_module("quality_policy_defaults") is None
