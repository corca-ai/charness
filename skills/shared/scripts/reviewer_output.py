#!/usr/bin/env python3
"""Shared structured-output boundary for reviewer worker CLIs."""

from __future__ import annotations

import importlib.util
import os


def _load_yaml_output():
    """Load Charness' canonical YAML renderer from the owning tree."""
    directory = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        directory = os.path.dirname(directory)
        candidate = os.path.join(directory, "scripts", "yaml_output.py")
        if os.path.isfile(candidate):
            spec = importlib.util.spec_from_file_location("charness_yaml_output", candidate)
            if spec is None or spec.loader is None:
                break
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/yaml_output.py not found within 5 ancestors of this script")


emit_yaml = _load_yaml_output().emit_yaml
