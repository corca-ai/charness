#!/usr/bin/env python3

"""A command a GATE spawns is covered, not only one a document prescribes (SC17).

The recurrence that produced this gate had no document anywhere in it. A config
literal in `cosmic-ray.toml` is read by `mutation_sampling_lib.read_test_command`
and spawned by `check_changed_line_mutation_coverage.py` as a serial,
coverage-instrumented, whole-suite pytest run. It was killed at 25 minutes,
unfinished, inside the same session that wrote the retro about correct rules
with no carrier. A registry over DOCUMENTS is inert against every step of that
chain.

So this gate reads two seams, and neither is prose:

1. **Config literals a gate reads and then spawns**, declared in the registry as
   `config_literals` (path + key). This is the seam the recurrence proves the
   document seam missed.
2. **Standing-gate surfaces**, through the already-exported
   `standing_gate_discovery_lib` -- shell runners, `package.json` scripts,
   lefthook, make. Command inventory was the half that already shipped; what was
   missing is the policy layer, which is `command_dominance_lib`.

Document-shape seams are owned by their artifact validators; this gate only
checks command ownership and dominance.

WHAT THIS GATE DOES NOT DECIDE. The registry's blind class governs everything
here and is stated in `command_dominance_lib`'s docstring; two consequences are
worth repeating at the verdict surface. First, a green result means "no
registered dominated shape at the sites listed below", never "no dominated
command in this repo" -- the registry is a denylist and the site list is finite.
Second, an EXEMPT site is still a dominated command; the exemption records that a
human judged its site, and this gate prints that judgement rather than hiding the
site. A report with zero blocking findings and three exempt ones is not a clean
repo, and the payload says so in `did_not_judge`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import adapter_lib
import quality_label_universe

from runtime_bootstrap import load_path_module, repo_root_from_script, skill_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

REGISTRY_PATH = Path(".agents/command-dominance.yaml")


# The LIBRARY comes from this script's OWN tree; only the registry and the scanned
# sites come from the analysed repo. Resolving the library from `--repo-root` made
# the gate crash on any tree that is not a charness checkout -- which is every tree
# an operator would point it at. It is the same discrimination the export gate one
# slice earlier was falsified for missing: "reads its own tree" is not "scans
# whatever tree the caller passed", and conflating them is how a maintainer tool
# reads as broken while its own repo stays green.
_DOMINANCE_CACHE = {}


def _load_dominance_lib():
    """Cached, and that is correctness rather than speed.

    `load_path_module` execs a FRESH module object per call, so two calls produce
    two distinct `RegistryError` classes and `except dominance.RegistryError`
    silently stops catching the error `evaluate` actually raised. Measured: the
    acceptance test for the refusal path failed with the refusal it was asserting.
    An uncaught exception here would surface as a traceback rather than the named
    verdict this gate exists to render.
    """
    if "lib" not in _DOMINANCE_CACHE:
        _DOMINANCE_CACHE["lib"] = load_path_module(
            "command_dominance_lib", skill_script(REPO_ROOT, "quality", "command_dominance_lib.py")
        )
    return _DOMINANCE_CACHE["lib"]


def _load_discovery_lib():
    return load_path_module(
        "standing_gate_discovery_lib_for_dominance",
        skill_script(REPO_ROOT, "quality", "standing_gate_discovery_lib.py"),
    )


def read_config_literal(path: Path, key: str, dominance) -> list[tuple[int, str]]:
    """Delegates to the ONE owner in `command_dominance_lib`; this reads the file."""
    if not path.is_file():
        return []
    return dominance.read_config_literal(path.read_text(encoding="utf-8"), key)


def scan_config_literals(repo_root: Path, registry, dominance) -> list:
    findings = []
    for entry in registry.config_literals:
        rel = entry["path"]
        key = entry["key"]
        site = f"{rel}:{key}"
        for line, command in read_config_literal(repo_root / rel, key, dominance):
            finding = dominance.classify_site(
                command,
                registry,
                site=site,
                line=line,
                context={"seam": "config-literal"},
            )
            if finding is not None:
                findings.append(finding)
    return findings


def scan_standing_gates(repo_root: Path, registry, dominance, discovery) -> list:
    findings = []
    surfaces = discovery.discover_surfaces(repo_root)
    for snippet in discovery.iter_snippets(surfaces):
        command = snippet.get("snippet") or ""
        if not command.strip():
            continue
        site = snippet.get("path") or "<unknown>"
        context = {"seam": "standing-gate", "origin": snippet.get("origin", "")}
        # Consumer repos without the declaration retain the historical shell
        # fallback. The in-tree data branch below carries labels directly, so
        # this compatibility heuristic is never used for the checked-in gate list.
        label = dominance.wrapper_label(command, registry.wrappers)
        if label:
            context["queue_label"] = label
        finding = dominance.classify_site(
            command, registry, site=site, line=snippet.get("line"), context=context
        )
        if finding is not None:
            findings.append(finding)
    return findings


def scan_declared_gate_commands(repo_root: Path, registry, dominance) -> list:
    """Classify commands from the declarative rows, preserving their labels."""
    rows = quality_label_universe.quality_gate_rows(repo_root)
    if rows is None:
        return []
    findings = []
    for row in rows:
        command = " ".join(row["command"])
        context = {
            "seam": "standing-gate",
            "origin": "quality-gate-declaration",
            "queue_label": row["label"],
        }
        finding = dominance.classify_site(
            command,
            registry,
            site=f"{quality_label_universe.QUALITY_GATES_PATH}:{row['label']}",
            context=context,
        )
        if finding is not None:
            findings.append(finding)
    return findings


NOT_JUDGED = (
    "whether an UNREGISTERED expensive command exists -- the registry is a "
    "denylist, so its false negatives are real and are not bounded by this run",
    "whether a registered `replacement` is actually cheaper, or still exists -- "
    "nothing here runs either command",
    "an EXEMPT site is still a dominated command; the exemption records a human "
    "judgement about that site and does not remove it from this report",
    "any command assembled at runtime, reached one indirection deeper, or living "
    "at a site outside `scanned_sites` below",
    "whether a reported command ever RUNS -- the standing-gate reader is a line "
    "scanner with no heredoc or reachability awareness, so a command inside a usage "
    "heredoc is discovered and classified like any other",
    "for a standing-gate finding, an exemption is keyed to the FILE, not the line; "
    "`line` shows which command was judged, but the exemption covers the file",
)


def evaluate(repo_root: Path) -> dict[str, object]:
    registry_path = repo_root / REGISTRY_PATH
    dominance = _load_dominance_lib()
    if not registry_path.is_file():
        return {
            "armed": False,
            "reason": (
                f"{REGISTRY_PATH} is absent; this repo records no dominated commands, "
                "so there is nothing to reconcile spawned commands against"
            ),
            "findings": [],
            "blocking": [],
        }
    # `load_yaml_file_report`, not `load_yaml_file`, and the difference is a
    # verdict rather than a nicety. This repo's adapter reader is a hand-rolled
    # block-YAML parser that DROPS what it cannot interpret; the exported
    # inventory reads the same file with PyYAML, which accepts more. A flow
    # mapping (`- {path: x, key: y}`) is a live example: PyYAML reads a rule, this
    # parser drops it, and the gate goes green over a registry entry that exists.
    # Two readers with different acceptance over one proof surface is the
    # builder-disagreement class this release already reconciled once, so the
    # narrower reader REFUSES instead of quietly reading less.
    data, uninterpreted = adapter_lib.load_yaml_file_report(registry_path)
    if uninterpreted:
        raise dominance.RegistryError(
            f"{REGISTRY_PATH} has line(s) this reader dropped, so any verdict from it "
            "would be rendered over a registry it did not fully read:\n  "
            + "\n  ".join(adapter_lib.uninterpreted_warnings(uninterpreted))
        )
    registry = dominance.parse_registry(data)
    findings = scan_config_literals(repo_root, registry, dominance)
    if (repo_root / quality_label_universe.QUALITY_GATES_PATH).is_file():
        try:
            findings.extend(scan_declared_gate_commands(repo_root, registry, dominance))
        except quality_label_universe.UniverseError as error:
            raise dominance.RegistryError(str(error)) from error
    else:
        discovery = _load_discovery_lib()
        findings.extend(scan_standing_gates(repo_root, registry, dominance, discovery))
    blocking = [finding for finding in findings if not finding.exempt]
    return {
        "armed": True,
        "reason": None,
        "registry_rules": len(registry.rules),
        "scanned_sites": {
            "config_literals": [
                f"{item['path']}:{item['key']}" for item in registry.config_literals
            ],
            "standing_gate_surfaces": True,
        },
        "findings": [finding.as_payload() for finding in findings],
        "blocking": [dominance.finding_message(finding) for finding in blocking],
        "exempt_count": len(findings) - len(blocking),
    }


def report_payload(report: dict[str, object], dominance) -> dict[str, object]:
    payload = dict(report)
    if not report["armed"]:
        payload["advisory"] = f"WARN: command dominance: not armed -- {report['reason']}"
        return payload
    payload["did_not_judge"] = list(NOT_JUDGED)
    blocking = report["blocking"]
    exempt = report["exempt_count"]
    if blocking:
        payload["summary"] = (
            f"{len(blocking)} spawned or queued command(s) are dominated by a cheaper "
            "command this repo already has."
        )
        payload["remedy"] = (
            "Replace the command with the `replacement` named in each finding, or -- "
            "if the site genuinely needs the slower command -- add an entry to "
            f"`{REGISTRY_PATH}` `exemptions` naming the site, the rule, and the "
            "measured reason. An exemption keeps the site in this report."
        )
        return payload
    summary = (
        "command dominance: no spawned or queued command matches a registered dominated shape."
    )
    if exempt:
        # Riding the WARN marker deliberately: a run whose only findings are
        # exempt is NOT the same as a run with no findings, and `print_phase_output`
        # surfaces a passing phase log only when it carries an attention marker.
        # Without this the exempt sites would be written to a per-phase log nobody
        # opens -- the advisory-buys-nothing shape a round-2 reviewer measured one
        # slice ago.
        payload["advisory"] = (
            f"WARN: {exempt} dominated command site(s) pass only under a recorded "
            "exemption; each is listed in `findings` with its reason."
        )
    payload["summary"] = summary
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    dominance = _load_dominance_lib()
    try:
        report = evaluate(repo_root)
    except dominance.RegistryError as exc:
        emit_yaml(
            {
                "armed": False,
                "error": f"{REGISTRY_PATH} cannot be read as a dominance registry: {exc}",
            }
        )
        return 1
    emit_yaml(report_payload(report, dominance))
    return 1 if report["armed"] and report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main())
