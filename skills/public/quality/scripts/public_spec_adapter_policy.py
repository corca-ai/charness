from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT = r"Covered by pytest:\s+`tests/[^`]+`(?:,\s*`tests/[^`]+`)*"
DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS = [
    "Fixed Decisions",
    "HTTP API contract",
    "Server backend stack",
    "Deferred Decisions",
    "Non-Goals",
]
DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR = 0.02
DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_GUARD_MIN_LINES = 100
DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS = [
    "proof: pointer",
    "proof: pointer-spec",
    "executable_proof: pointer",
    "public_spec_proof: pointer",
]


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


def repo_script_module(module_name: str) -> Any | None:
    """A repo `scripts/` module by flat name, located by the layout resolver.

    None when this skill runs where no repo scripts ship (no tree root, no
    resolver, or the module is absent): the policy then keeps its exported
    defaults. The resolver is reached through the skill runtime bootstrap, the
    same seam every other quality script uses to import repo modules.
    """
    try:
        runtime = _load_skill_runtime_bootstrap()
        repo_root = runtime.repo_root_from_skill_script(__file__)
        layout = runtime.load_repo_module_from_skill_script(__file__, "scripts.core.repo_layout")
        candidate = layout.find_repo_script(repo_root, f"{module_name}.py")
    except (ImportError, RuntimeError):
        return None
    if candidate is None:
        return None
    spec = importlib.util.spec_from_file_location(module_name, candidate)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(module_name, module)
    spec.loader.exec_module(module)
    return module


_POLICY_DEFAULTS = repo_script_module("quality_policy_defaults")
if _POLICY_DEFAULTS is not None:
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT = _POLICY_DEFAULTS.DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT
    DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS = _POLICY_DEFAULTS.DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS
    DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR = (
        _POLICY_DEFAULTS.DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR
    )
    DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_GUARD_MIN_LINES = (
        _POLICY_DEFAULTS.DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_GUARD_MIN_LINES
    )
    DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS = (
        _POLICY_DEFAULTS.DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS
    )


def load_quality_adapter_data(repo_root: Path) -> dict[str, Any]:
    module = repo_script_module("quality_adapter_lib")
    if module is None:
        return {}
    payload = module.load_quality_adapter(repo_root)
    if isinstance(payload, dict) and not payload.get("valid", True):
        errors = payload.get("errors", [])
        rendered = "; ".join(str(error) for error in errors) if errors else "unknown error"
        raise ValueError(f"Invalid quality adapter: {rendered}")
    data = payload.get("data") if isinstance(payload, dict) else None
    return data if isinstance(data, dict) else {}


def option(data: dict[str, Any], field: str, default: Any) -> Any:
    return data.get(field, default)
