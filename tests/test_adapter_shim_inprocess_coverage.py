"""In-process coverage for the canonical bootstrap shim in adapter scripts (#393 class).

The #390 bootstrap-finder convergence (a741e613) stamped the governed canonical
shim — ``_load_skill_runtime_bootstrap()`` plus its ``raise ImportError`` guard —
into every per-skill ``init_adapter.py`` / ``resolve_adapter.py`` /
``review_adapter.py`` / ``preflight_sources.py``. Those scripts run ONLY via
subprocess, so coverage.py never attributes the shim block; the ``raise
ImportError`` guard in particular stays uncovered, and over a batch range that
touched the shim every such changed line reads as a blocking changed line — the
same #219 -> #251 -> #260 -> #306 -> #335 -> #393 recurrence class.

This test DISCOVERS every adapter script carrying the canonical shim marker (so
the next converged adapter is covered automatically rather than re-filing the
auto-issue) and, in-process, (1) imports it so the module-level shim happy-path
lines are attributed, and (2) forces the bootstrap-not-found branch so the
``raise ImportError`` guard line is covered. Test-only; no production change.
Mirrors ``tests/test_scaffold_inprocess_coverage.py`` /
``tests/test_nose_inprocess_coverage.py``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SKILLS = REPO_ROOT / "skills" / "public"
SHIM_MARKER = 'raise ImportError("skill_runtime_bootstrap.py not found")'
ADAPTER_SCRIPT_NAMES = ("init_adapter.py", "resolve_adapter.py", "review_adapter.py", "preflight_sources.py")


def _discover_shim_adapters() -> list[str]:
    found: list[str] = []
    if not PUBLIC_SKILLS.is_dir():
        return found
    for skill_dir in sorted(PUBLIC_SKILLS.iterdir()):
        scripts = skill_dir / "scripts"
        if not scripts.is_dir():
            continue
        for name in ADAPTER_SCRIPT_NAMES:
            path = scripts / name
            if path.is_file() and SHIM_MARKER in path.read_text(encoding="utf-8"):
                found.append(path.relative_to(REPO_ROOT).as_posix())
    return found


ADAPTERS = _discover_shim_adapters()


def test_shim_adapters_discovered() -> None:
    # Guard against a silent empty/short parametrization (e.g. a marker reword)
    # that would make the per-file coverage tests vacuously pass.
    assert len(ADAPTERS) >= 20, ADAPTERS


def _load(rel: str):
    path = REPO_ROOT / rel
    spec = importlib.util.spec_from_file_location(f"{rel.replace('/', '_')}_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("rel", ADAPTERS)
def test_adapter_shim_in_process_coverage(rel: str, tmp_path: Path, monkeypatch) -> None:
    module = _load(rel)  # exec_module attributes the module-level shim happy path
    assert hasattr(module, "_load_skill_runtime_bootstrap")

    # Force the bootstrap-not-found branch so the `raise ImportError` guard line
    # is covered: point __file__ at an isolated dir whose ancestors lack the
    # bootstrap, mirroring the scaffold validator-fallback technique.
    isolated = tmp_path / "deep" / "nest" / "x.py"
    isolated.parent.mkdir(parents=True)
    monkeypatch.setattr(module, "__file__", str(isolated))
    with pytest.raises(ImportError):
        module._load_skill_runtime_bootstrap()
