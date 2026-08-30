# Issue #749 Retained-Python Boundary Audit

Date: 2026-08-30

Current provider source has no repository mypy, pyright, or basedpyright configuration and none of those checker executables resolves on the local development path. This is an absence observation, not a type-safety result.

`scripts/packaging_lib.py` still calls `replace_tree_if_present(scripts_root, exported_scripts_root)` and then removes only the explicit `SOURCE_ONLY_PLUGIN_SCRIPTS` set. Packaging therefore remains a broad scripts-tree export rather than an approved selective-export boundary.

No retained-Python role inventory, selected checker contract, selective-export proof, or measured consumer-rework JTBD exists for a new campaign. These absences are not implementation success.

This audit does not claim the top-level CLI should stay Python, that fewer lines are undesirable, or that the current Python boundary is typed or complete.
