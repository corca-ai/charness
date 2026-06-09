"""Sibling/shared-module loaders for the achieve closeout-evidence gate.

The closeout-evidence wrapper (``goal_artifact_closeout_evidence.py``) delegates
to a fan of sibling floors (disposition, early-close-report, coordination,
phase-routing, closeout-delegation, metric-window, adapter-policy) plus the
repo-owned shared closeout helper. Resolving each of those is near-identical
filesystem-spec boilerplate; collecting it here keeps the wrapper focused on the
gate logic and both files comfortably under the single-file line gate.

Each loader stays VERBATIM from the wrapper so behavior is preserved exactly:

- ``_load_shared_helper`` parent-walks to ``scripts/`` for the portable shared
  closeout helper (resolves in the working tree and the installed export alike);
- every ``_load_sibling_*`` loads a leaf module from the SAME directory via
  ``spec_from_file_location`` (no ``from scripts.`` import, no ``sys.modules``
  registration), so the dependency stays one-directional (this leaf never imports
  back into the wrapper).

The wrapper re-binds these as its own module attributes so the established
``ce._load_shared_helper`` / ``ce._load_sibling_*`` surface — including the
monkeypatch and fail-closed ImportError tests — is unchanged.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_shared_helper():
    """Load the repo-owned shared closeout-evidence helper.

    Resolution walks parent directories until ``scripts/`` is found, so the
    helper stays portable across the working tree and any installed export.
    """
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "check_prescribed_skill_executed_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "check_prescribed_skill_executed_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/check_prescribed_skill_executed_lib.py not found")


def _load_sibling_disposition():
    """Load the sibling improvement-disposition gate module.

    Kept in its own file (a separable concept, like this module was split from
    ``goal_artifact_lib.py``) so neither file approaches the single-file line
    gate. This module depends on it; the dependency is one-directional (the
    disposition module is a leaf), so there is no circular import.
    """
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_disposition",
        Path(__file__).resolve().parent / "goal_artifact_disposition.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_disposition.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_sibling_early_close_report():
    """Load the sibling early-close report floor module."""
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_early_close_report",
        Path(__file__).resolve().parent / "goal_artifact_early_close_report.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_early_close_report.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_sibling_metric_window():
    """Load the sibling goal-metric-window module for the non-blocking
    closeout attention signal. A leaf module (no sibling imports), so the
    dependency stays one-directional.
    """
    spec = importlib.util.spec_from_file_location(
        "goal_metric_window_lib",
        Path(__file__).resolve().parent / "goal_metric_window_lib.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_metric_window_lib.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_sibling_coordination_floors():
    """Load the sibling gather/release coordination-floor module.

    A leaf like the disposition module (no sibling imports), kept separate so
    this wrapper stays under the single-file line gate. One-directional: this
    module depends on it, never the reverse.
    """
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_coordination_floors",
        Path(__file__).resolve().parent / "goal_artifact_coordination_floors.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_coordination_floors.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_sibling_phase_routing():
    """Load the sibling phase-routing floor module."""
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_phase_routing",
        Path(__file__).resolve().parent / "goal_artifact_phase_routing.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_phase_routing.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_sibling_closeout_delegation():
    """Load the sibling orchestrator/sub-goal closeout-delegation gate.

    A leaf like the disposition/coordination modules (no sibling imports), kept
    separate so this wrapper stays under the single-file line gate. One-directional:
    this module depends on it, never the reverse.
    """
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_closeout_delegation",
        Path(__file__).resolve().parent / "goal_artifact_closeout_delegation.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_closeout_delegation.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_sibling_adapter_policy():
    """Load the optional achieve adapter policy leaf module."""
    spec = importlib.util.spec_from_file_location(
        "achieve_adapter_policy",
        Path(__file__).resolve().parent / "achieve_adapter_policy.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("achieve_adapter_policy.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
