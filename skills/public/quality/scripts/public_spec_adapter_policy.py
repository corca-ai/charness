from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT = r"Covered by pytest:\s+`tests/[^`]+`(?:,\s*`tests/[^`]+`)*"
DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS = ["Fixed Decisions", "HTTP API contract", "Server backend stack", "Deferred Decisions", "Non-Goals"]
DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR = 0.02
DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS = ["proof: pointer", "proof: pointer-spec", "executable_proof: pointer", "public_spec_proof: pointer"]


def load_repo_script_module(module_name: str) -> Any | None:
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "scripts" / f"{module_name}.py"
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(module_name, candidate)
        if spec is None or spec.loader is None:
            continue
        if str(ancestor) not in sys.path:
            sys.path.insert(0, str(ancestor))
        module = importlib.util.module_from_spec(spec)
        sys.modules.setdefault(module_name, module)
        spec.loader.exec_module(module)
        return module
    return None


_POLICY_DEFAULTS = load_repo_script_module("quality_policy_defaults")
if _POLICY_DEFAULTS is not None:
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT = _POLICY_DEFAULTS.DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT
    DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS = _POLICY_DEFAULTS.DEFAULT_PUBLIC_SPEC_SECTION_EXEMPTIONS
    DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR = _POLICY_DEFAULTS.DEFAULT_PUBLIC_SPEC_IMPLEMENTATION_REF_DENSITY_FLOOR
    DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS = _POLICY_DEFAULTS.DEFAULT_PUBLIC_SPEC_POINTER_PROOF_MARKERS


def load_quality_adapter_data(repo_root: Path) -> dict[str, Any]:
    module = load_repo_script_module("quality_adapter_lib")
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
