#!/usr/bin/env python3
"""Refuse an export that cannot run on a machine holding only the export (#634).

The verdict; the reasoning and both arms live in
`export_self_sufficiency_lib`. Read that module first -- in particular WHY the
packaging validator is green while this defect ships, which is the reason this
gate is a separate question rather than a stricter setting on an existing one.

THREE SEVERITIES, and the split is measured rather than staged:

- **An unguarded third-party import in a DOCUMENTED consumer entrypoint BLOCKS.**
  That is the reported failure exactly: a consumer followed a `SKILL.md`, ran the
  command, and got a bare `ModuleNotFoundError`. The arm asks AVAILABILITY, not
  declaration -- an earlier version asked "does the export declare this package
  anywhere", which this slice's own repair satisfied for the whole export by
  shipping one requirements file while ~36 bare imports kept crashing. A shipped
  requirements file installs nothing.
- **Unshipped path literals are ADVISORY.** Not because they matter less -- the
  reported instance was one -- but because the arm's classification was falsified
  in both directions by round-1 review, and a release-blocking gate built on a
  falsified classification is one whose escape hatch becomes routine. The
  reasoning is in `export_self_sufficiency_lib`'s module docstring, along with
  what the arm still owes before it can refuse.

- **An exported ``.py`` or ``.sh`` that names a repository-only ``tools/``
  module BLOCKS unless the line carries an ``export-guard:`` comment saying why
  it cannot run in a consumer (an authoring-checkout test, a ``repo: charness``
  guard). Prose and data references stay advisory: the ``<authoring-repo>/tools/``
  spelling is how shipped docs point at the authoring tree.

An advisory list is still a carrier: it is regenerable, it appears in the runner's
payload, and it is what a later slice works from. What it is NOT is proof that
the listed sites are defects, and this gate does not claim that.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "tools.export_self_sufficiency_lib")
_packaging = import_repo_module(__file__, "scripts.plugin_export.packaging_lib")
_yaml_output = import_repo_module(__file__, "scripts.yaml_output")

DEFAULT_PACKAGE_ID = "charness"
#: The runner's "ran, established nothing" byte. Registered in run-quality.sh's
#: UNESTABLISHED_CAPABLE_LABELS; without that registration this exit is read as
#: an ordinary failure.
UNESTABLISHED_EXIT = 3

#: Starts "ADVISORY:" on purpose. The runner surfaces a passing phase's output
#: only when it matches `(WARNING|WARN|WEAK|ADVISORY)(:|\s)`; an earlier wording
#: put a COMMA after the marker, so this list was written to a per-phase log that
#: is deleted on exit and read by nobody -- the advisory bargain buying nothing.
PATH_ADVISORY_NOTE = (
    "ADVISORY: not a verdict. each entry is an exported module reading a repo-root path "
    "the export does not ship, but this arm cannot yet tell a module reading its OWN tree "
    "from a maintainer tool scanning whatever tree the operator named -- so the list "
    "contains both real delivery bugs and correct code. Read it as an inventory to work "
    "from, never as a count of defects."
)
#: The consumer-doc instruction arm BLOCKS while the module-prose half stays
#: advisory, and the split is measured rather than staged: seven consumer-doc
#: sites were repaired to `<plugin-dir>/` in the same slice that added this arm (12
#: rewritten, 5 reverted once review showed they were EXECUTED values), so the bar is
#: set at the count it already holds. That is the difference from the
#: path arm, which stayed advisory because its classification was falsified in both
#: directions and never reached zero.
CONSUMER_DOC_INSTRUCTION_REMEDY = (
    "an exported consumer-facing .md tells a consumer to run `python3 scripts/X`, "
    "which on their machine is THEIR repo root and not the plugin. Rewrite it as "
    "`python3 <plugin-dir>/scripts/X` -- check_plugin_dir_references.py owns that placeholder "
    "and will verify the target ships."
)
MODULE_PROSE_INSTRUCTION_NOTE = (
    "ADVISORY: not a verdict. Each entry is a `python3 scripts/X` string in an exported .py "
    "file or under a `scripts/` directory. Many are maintainer tools describing their own "
    "in-repo invocation, where rewriting to `<plugin-dir>/` would make the correct instruction "
    "wrong; others are consumer guidance that happens to live in a docstring, and an EXECUTED "
    "command string is indistinguishable from either. This arm cannot tell them apart -- the "
    "split is by file location, a declaration and not a measurement. Read it as an inventory "
    "to work from, never as a count of defects."
)
UNGUARDED_ENTRYPOINT_REMEDY = (
    "A script an exported SKILL.md/reference/adapter tells a consumer to RUN imports a "
    "third-party package unguarded, so that consumer meets it as a bare "
    "ModuleNotFoundError. Guard the import and raise a message naming the package and "
    "how to install it -- see skills/public/gather/scripts/gather_public_url.py. A "
    "function-level import does not count as guarded: it defers the same crash to call "
    "time. Declaring the package in a shipped requirements file does not count either; "
    "a requirements file installs nothing."
)
DEPENDENCY_INVENTORY_NOTE = (
    "ADVISORY: inventory, not a verdict. every top-level third-party import in the export "
    "whose distribution no shipped requirements file names. Reported so the surface is "
    "visible; NOT a claim that the listed modules are safe once declared, and NOT a claim "
    "that the unlisted ones are."
)
EXPORTED_TOOLS_REFERENCE_NOTE = (
    "ADVISORY: inventory, not a verdict. the exported file names a repository-only "
    "tools/ module or module carrier. Keep authoring-only references out of exported "
    ".md/.json/.yaml/.py/.sh files; consumer commands must resolve entirely inside "
    "the installed plugin."
)


def run_check(repo_root: Path, *, package_id: str = DEFAULT_PACKAGE_ID) -> dict:
    # ABSENCE only, not "anything load_manifest raises". `load_manifest` also
    # VALIDATES, re-raising every failure as PackagingError, so a blanket catch
    # reported a real, unrelated packaging defect as "no manifest here" -- a false
    # cause, and a laundering path the moment `unestablished` stops exiting 1.
    if not (repo_root / "packaging" / f"{package_id}.json").is_file():
        return {
            "status": "unestablished",
            "reason": (
                f"no packaging manifest at {repo_root}/packaging/{package_id}.json. "
                "This gate judges a repo that BUILDS an export; an installed plugin is "
                "the artifact, not the builder, and has nothing here to check."
            ),
        }
    manifest = _packaging.load_manifest(repo_root, package_id)
    export_root = repo_root / _packaging.materialized_plugin_root(manifest)
    if not export_root.is_dir():
        # Zero files scanned is an unestablished scope, not a clean one: it reads
        # identically to a full pass while proving nothing about the artifact.
        return {
            "status": "unestablished",
            "reason": f"no materialized export tree at {export_root}; nothing was validated",
        }

    repo_root_entries = {entry.name for entry in repo_root.iterdir()}
    path_findings = _lib.unshipped_path_findings(
        export_root, repo_root_entries=repo_root_entries, relative_to=repo_root
    )
    entrypoint_findings = _lib.unguarded_entrypoint_import_findings(
        export_root, relative_to=repo_root
    )
    dependency_findings = _lib.undeclared_dependency_findings(export_root, relative_to=repo_root)
    exported_tools_references = _lib.exported_tools_reference_findings(export_root)
    exported_tools_code_references = [
        finding
        for finding in exported_tools_references
        if finding.get("code") and finding.get("executable") and not finding.get("guarded")
    ]

    instruction_findings = _lib.repo_root_instruction_findings(export_root)
    consumer_doc_instructions = [
        finding for finding in instruction_findings if finding["site_class"] == "consumer-doc"
    ]
    module_prose_instructions = [
        finding for finding in instruction_findings if finding["site_class"] == "module-prose"
    ]

    payload: dict[str, object] = {
        "status": (
            "fail"
            if entrypoint_findings or consumer_doc_instructions or exported_tools_code_references
            else "pass"
        ),
        "export_root": _packaging.materialized_plugin_root(manifest).as_posix(),
        "scanned_python_files": len(list(export_root.rglob("*.py"))),
        "documented_entrypoint_count": len(_lib.documented_entrypoint_names(export_root)),
        "unguarded_entrypoint_imports": entrypoint_findings,
        "declared_distributions": sorted(_lib.declared_distributions(export_root)),
        "advisory_unshipped_path_sites": path_findings,
        "advisory_path_note": PATH_ADVISORY_NOTE,
        "advisory_undeclared_dependencies": dependency_findings,
        "advisory_dependency_note": DEPENDENCY_INVENTORY_NOTE,
        "exported_tools_code_references": exported_tools_code_references,
        "advisory_exported_tools_references": exported_tools_references,
        "advisory_exported_tools_note": EXPORTED_TOOLS_REFERENCE_NOTE,
        "consumer_doc_repo_root_instructions": consumer_doc_instructions,
        "advisory_module_prose_repo_root_instructions": module_prose_instructions,
        "advisory_module_prose_note": MODULE_PROSE_INSTRUCTION_NOTE,
    }
    remedies: list[str] = []
    if entrypoint_findings:
        remedies.append(UNGUARDED_ENTRYPOINT_REMEDY)
    if consumer_doc_instructions:
        remedies.append(CONSUMER_DOC_INSTRUCTION_REMEDY)
    if remedies:
        payload["remedy"] = remedies
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--package-id", default=DEFAULT_PACKAGE_ID)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    payload = run_check(repo_root, package_id=args.package_id)
    _yaml_output.emit_yaml(payload)
    if payload["status"] == "pass":
        return 0
    if payload["status"] == "unestablished":
        # 3, not 1: the runner renders this as UNPROVEN rather than FAIL. Every
        # neighbour in this block degrades to no gate in a consumer/tmp repo; this
        # gate is EXPORTED, so exiting 1 there meant repairing a stranded-consumer
        # defect by handing every consumer a red lane.
        return UNESTABLISHED_EXIT
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
