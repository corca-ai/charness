"""Exported text that names a repository-only ``tools/`` module.

Split from ``export_self_sufficiency_lib`` (#769): the arm that scans the
exported tree for moved basenames, ``-m tools.`` carriers, dotted module
spellings, and ``tools/<name>.py`` paths, and marks which sites run the
module (blocking unless ``export-guard:``-annotated) versus merely name it.
"""

from __future__ import annotations

import re
from pathlib import Path

MOVED_TOOL_BASENAMES = tuple(
    """
    check_bootstrap_shim_consistency.py check_closeout_classification_parity.py
    check_consumer_validator_catalog_decisions.py check_coverage.py check_coverage_extra_lib.py
    check_current_pointer_writes.py check_export_self_sufficiency.py check_inventory_declaration_coverage.py
    check_last_verified.py check_plugin_asset_command_carriers.py check_plugin_doc_links.py
    check_plugin_import_smoke.py check_public_doc_coupling.py check_quality_tool_fixtures.py
    check_references_link_inventory.py check_runtime_budget_universe.py check_skill_bootstrap_vars.py
    check_skill_contracts.py check_timing_layer_completeness.py check_unreferenced_scripts.py
    eval_issue_scenarios.py eval_registry.py eval_setup.py export_self_sufficiency_lib.py
    inventory_skill_script_references.py public_skill_dogfood_validation_lib.py quality_gates_extract.py
    run_evals.py skill_portability_lib.py suggest_public_skill_validation.py
    validate_attention_state_visibility.py validate_current_pointer_freshness.py
    validate_inference_interpretation.py validate_integrations.py
    validate_inventory_consumption_declaration.py validate_packaging_committed.py validate_presets.py
    validate_profiles.py validate_public_skill_dogfood.py validate_public_skill_validation.py
    validate_quality_closeout_contract.py validate_quality_reference_catalog.py validate_skills.py
    validate_surfaces.py
    """.split()
)


_MOVED_TOOL_BASENAME_RE = re.compile(
    "|".join(re.escape(name) for name in sorted(MOVED_TOOL_BASENAMES, key=len, reverse=True))
)


_EXPORTED_TOOL_REFERENCE_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".sh"}


# `import_repo_module(__file__, "tools.x")`, `repo_module("tools.x")`, and an argv
# list spelled `"-m", "tools.x"` all reach a tools/ module without the literal
# `-m tools.` or a `<basename>.py`; the round-1 arm missed every one of them.
_DOTTED_TOOL_MODULE_RE = re.compile(r"\btools\.[a-z_][a-z0-9_]*\b")


_TOOLS_LIST_ITEM_RE = re.compile(r"""["']tools["']\s*,""")


_TOOLS_PATH_RE = re.compile(r"(?<![\w<>/.-])tools/[a-z_][a-z0-9_]*\.py\b")


_CODE_TOOL_REFERENCE_SUFFIXES = {".py", ".sh"}


def exported_tools_reference_findings(export_root: Path) -> list[dict[str, object]]:
    """Find exported text that names a command from the non-exported ``tools/`` tree.

    This is a shipping-boundary check, not a filename inventory: it reads file
    contents only. A stale path or ``python3 -m tools.<name>`` carrier leaves an
    installed consumer with instructions for a file that is intentionally absent.
    """
    findings: list[dict[str, object]] = []
    for path in sorted(export_root.rglob("*")):
        if not path.is_file() or path.suffix not in _EXPORTED_TOOL_REFERENCE_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        in_docstring = False
        for lineno, line in enumerate(lines, start=1):
            if line.count('"""') % 2 == 1:
                in_docstring = not in_docstring
                continue
            if in_docstring:
                # Prose inside a docstring describes a spelling; it does not run it.
                continue
            names = set(_MOVED_TOOL_BASENAME_RE.findall(line))
            executable: set[str] = set()
            if "-m tools." in line:
                executable.add("-m tools.")
            executable.update(_DOTTED_TOOL_MODULE_RE.findall(line))
            executable.update(_TOOLS_PATH_RE.findall(line))
            if _TOOLS_LIST_ITEM_RE.search(line):
                names.add('"tools" argv item')
            names.update(executable)
            if not names:
                continue
            findings.append(
                {
                    "path": path.relative_to(export_root).as_posix(),
                    "line": lineno,
                    "references": sorted(names),
                    "code": path.suffix in _CODE_TOOL_REFERENCE_SUFFIXES,
                    # Only a spelling that RUNS or IMPORTS the module blocks; a
                    # basename in a comment or a docstring is advisory.
                    "executable": bool(executable),
                    # A site that names a tools/ module on purpose carries an
                    # `export-guard:` comment saying why the reference cannot run
                    # in a consumer (an authoring-checkout test, a repo guard).
                    # ruff moves a trailing comment to the closing bracket line,
                    # so the marker may sit up to two lines below the spelling.
                    "guarded": any(
                        "export-guard:" in lines[index]
                        for index in range(lineno - 1, min(lineno + 2, len(lines)))
                    ),
                }
            )
    return findings
