#!/usr/bin/env python3

"""Is the command your gates prescribe dominated by a cheaper one you already have?

The consumer half of the cost direction (SC19), and it is the LARGER half. What
the quality skill exported before this was the budget apparatus —
`check_runtime_budget.py`, `runtime_budget_lib.py`, `runtime_profile_lib.py`,
`render_runtime_summary.py` — so a consuming repo inherited the ledger and none
of the speed, and nothing told it so. `check_runtime_budget_universe.py` is
deliberately NOT exported (its own docstring records why: it only understands
`run-quality.sh`), so the direction that does exist upstream did not reach
consumers either.

This closes that with a POLICY LAYER, not a new scanner. `standing_gate_discovery_lib`
already ships and already tokenizes commands out of shell runners, `package.json`
scripts, lefthook, and make; `command_dominance_lib` already owns the "is this
dominated" question. Both are exported. What was missing is the file that asks
one of the other.

Advisory by construction, and it exits 0 on every tree including a broken one. An
EXPORTED gate that returns nonzero hands a red lane to a consumer who installed a
plugin — the stranded-consumer defect the slice before this one was built to end.
"""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

BOOTSTRAP_ANCHOR = Path("packaging") / "bootstrap-requirements.txt"


def missing_yaml_message(module_name: str, here: Path) -> str:
    """The stranded-consumer message, as a testable function.

    A function rather than inline `except` body, so both branches are reachable
    in-process. The end-to-end proof runs a COPY of this script in a subprocess
    with PyYAML blocked, and coverage attributes that to the copy's path, not to
    this file — so the handler's own lines read as unproven no matter how strong
    the end-to-end test is. Splitting the message out is what makes the branch
    both provable here and still executed there.
    """
    found = next((parent for parent in here.parents if (parent / BOOTSTRAP_ANCHOR).is_file()), None)
    head = (
        "command-dominance inventory cannot start: PyYAML is missing from the "
        f"interpreter running this script (import of `{module_name}` failed)"
    )
    if found is None:
        # No counted-hop fallback. The first version fell back to `parents[3]`,
        # which is `<repo>/skills` in the dev tree, so a vendored install without
        # `packaging/` was told to install from a requirements file that does not
        # exist -- stranding the consumer this guard exists to un-strand.
        return (
            f"{head}, and no `{BOOTSTRAP_ANCHOR}` was found in any parent of "
            f"{here}, so this install is incomplete.\n"
            f"  Install PyYAML into THIS interpreter: {sys.executable} -m pip install PyYAML"
        )
    requirements = found / BOOTSTRAP_ANCHOR
    return (
        f"{head}.\n"
        f"  Install it into THIS interpreter: {sys.executable} -m pip install "
        f"-r {requirements}\n"
        f"  The pinned versions are declared in {requirements}."
    )


try:
    import yaml
except ModuleNotFoundError as exc:
    # NO `# pragma: no cover`. The first version carried
    # `# pragma: no cover - exercised by test_export_self_sufficiency`, and that
    # test never referenced this file -- a false pragma naming a test that does
    # not exercise it, verbatim the defect three reviewers caught in the sibling
    # guard one slice earlier.
    raise SystemExit(missing_yaml_message(exc.name, Path(__file__).resolve())) from exc


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_dominance = SKILL_RUNTIME.load_local_skill_module(__file__, "command_dominance_lib")
_discovery = SKILL_RUNTIME.load_local_skill_module(__file__, "standing_gate_discovery_lib")
_summary_output = SKILL_RUNTIME.load_local_skill_module(__file__, "summary_output_lib")
_runtime_profile = SKILL_RUNTIME.load_local_skill_module(__file__, "runtime_profile_lib")
dump_yaml = _summary_output.dump_yaml

DEFAULT_REGISTRY_PATH = Path(".agents/command-dominance.yaml")
DEFAULT_QUALITY_ADAPTER_PATH = Path(".agents/quality-adapter.yaml")

# Advisory interpretation contract (skills/shared/references/
# advisory-interpretation-contract.md). `blind_spots` is the load-bearing field
# and it is the same blind class `command_dominance_lib`'s docstring states: this
# is authored memory, not measurement.
INTERPRETATION = {
    "measures": (
        "commands discovered in this repo's standing-gate surfaces (shell runners, "
        "package.json scripts, lefthook, make) and in registry-declared config "
        "literals, matched against the dominated-command shapes THIS repo declared "
        "in its own registry; and for each such command, whether a budgeted label "
        "in this repo's quality adapter covers it"
    ),
    "proxy_for": (
        "operator and agent time spent re-proving something a cheaper command in "
        "this same repo already proves"
    ),
    "blind_spots": (
        "the registry is a DENYLIST authored by hand, so an expensive command nobody "
        "registered is invisible and a green result is not a cheap repo; nothing here "
        "runs either command, so a `replacement` that is actually slower or no longer "
        "exists is accepted silently; only command TEXT at scanned sites is read, so a "
        "command assembled at runtime or reached through one more indirection is "
        "missed; a dominated shape can be deliberate at a particular site, which "
        "is why exempt sites stay in this report instead of disappearing from it; the "
        "discovery reader is a line scanner with no heredoc or reachability awareness, "
        "so it can also report a command that never RUNS (a usage heredoc counts); and "
        "the budget answer is membership only -- a label with a bar that nothing ever "
        "exercises reads as budgeted here"
    ),
    "interpretation_question": (
        "for each command listed, is the cheaper replacement actually equivalent "
        "evidence for what THAT site needs — or does the site need the slower "
        "command's isolation, and the registry needs an exemption with a reason? "
        "And for each command reported as unbudgeted: should it carry a bar, or is "
        "it genuinely outside the measured lane on purpose?"
    ),
}

SUMMARY_FIELDS = (
    "repo_root",
    "registry_path",
    "registry_state",
    "discovered_surfaces",
    "discovered_commands",
    "dominated_findings",
    "exempt_findings",
    "unbudgeted_commands",
    "budget_state",
    "interpretation",
)


def load_registry(registry_path: Path):
    """Parse the registry, or say which of the three states this repo is in.

    Absent is NOT an error and is the state every fresh consumer starts in. It is
    reported by name, with the next action, rather than as an empty finding list —
    an empty list beside a green summary reads as "nothing is dominated here",
    which is a claim this run has no basis for.
    """
    if not registry_path.is_file():
        return None, {
            "state": "absent",
            "detail": (
                f"no {DEFAULT_REGISTRY_PATH} in this repo, so no command shapes are "
                "declared dominated and nothing below is a coverage claim"
            ),
            "next_action": (
                "declare the commands you have measured as dominated, each with its "
                "replacement and reason; see the `quality` skill's cost-dominance "
                "reference for the schema"
            ),
        }
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        registry = _dominance.parse_registry(data)
    except Exception as exc:  # noqa: BLE001 - a consumer's malformed file must not crash their gate
        return None, {"state": "unreadable", "detail": str(exc), "next_action": "repair the registry"}
    return registry, {"state": "loaded", "detail": f"{len(registry.rules)} rule(s)"}


def load_budgeted_labels(adapter_path: Path) -> tuple[dict[str, list[str]], dict[str, str]]:
    """The consumer's budgeted labels, or the named reason there are none.

    Added by owner ruling 2026-08-16 after a bounded reviewer measured that the
    exported critique angle promised this inventory answered "is the expensive
    command budgeted at all" while it read no budgets anywhere. The claim was
    shipped; the capability was not.

    Reads the quality adapter's budget blocks through the EXPORTED
    `runtime_profile_lib.budgeted_label_union`, the same owner
    `check_runtime_budget_universe` reads, so the two cannot drift about what
    counts as budgeted. Absent adapter is a named state, not an empty answer.
    """
    if not adapter_path.is_file():
        return {}, {
            "state": "absent",
            "detail": (
                f"no {DEFAULT_QUALITY_ADAPTER_PATH} in this repo, so no runtime budgets "
                "are declared and every command below is reported unbudgeted"
            ),
        }
    try:
        data = yaml.safe_load(adapter_path.read_text(encoding="utf-8")) or {}
        labels = _runtime_profile.budgeted_label_union(data if isinstance(data, dict) else {})
    except Exception as exc:  # noqa: BLE001 - a consumer's malformed adapter must not crash their lane
        return {}, {"state": "unreadable", "detail": str(exc)}
    return labels, {"state": "loaded", "detail": f"{len(labels)} budgeted label(s)"}


def inventory(
    repo_root: Path, registry_path: Path, adapter_path: Path | None = None
) -> dict[str, object]:
    registry, registry_state = load_registry(registry_path)
    budgeted, budget_state = load_budgeted_labels(
        adapter_path or (repo_root / DEFAULT_QUALITY_ADAPTER_PATH)
    )
    surfaces = _discovery.discover_surfaces(repo_root)
    snippets = _discovery.iter_snippets(surfaces)

    dominated: list[dict[str, object]] = []
    exempt: list[dict[str, object]] = []
    unbudgeted: list[dict[str, object]] = []
    if registry is not None:
        sites: list[tuple[str, int | None, str]] = [
            (snippet["path"], snippet.get("line"), snippet["snippet"]) for snippet in snippets
        ]
        for entry in registry.config_literals:
            literal_path = repo_root / entry["path"]
            if not literal_path.is_file():
                continue
            for number, value in _dominance.read_config_literal(
                literal_path.read_text(encoding="utf-8"), entry["key"]
            ):
                sites.append((f"{entry['path']}:{entry['key']}", number, value))
        for site, line, command in sites:
            label = _dominance.wrapper_label(command, registry.wrappers)
            finding = _dominance.classify_site(
                command,
                registry,
                site=site,
                line=line,
                context={"queue_label": label} if label else None,
            )
            if finding is None:
                continue
            (exempt if finding.exempt else dominated).append(finding.as_payload())
            if not label or label not in budgeted:
                unbudgeted.append(
                    {
                        "site": site,
                        "command": finding.command,
                        "queue_label": label,
                        # One sentence, one owner: the wording lives in
                        # `command_dominance_lib.unbudgeted_basis` so this and the
                        # repo gate cannot drift about what the finding MEANS.
                        "basis": _dominance.unbudgeted_basis(label),
                    }
                )

    return {
        "repo_root": str(repo_root),
        "registry_path": str(registry_path),
        "registry_state": registry_state,
        "budget_state": budget_state,
        "discovered_surfaces": [surface["path"] for surface in surfaces],
        "discovered_commands": len(snippets),
        "dominated_findings": dominated,
        "exempt_findings": exempt,
        "unbudgeted_commands": unbudgeted,
        "interpretation": dict(INTERPRETATION),
    }


SUMMARY_NOTE = (
    "summary is triage output; use --detail for every discovered surface and the "
    "full finding payload"
)


def summarize_payload(payload: dict[str, object]) -> dict[str, object]:
    """The compact view: the counts and the findings, not every surface path."""
    compact = {field: payload[field] for field in SUMMARY_FIELDS}
    compact["summary_note"] = SUMMARY_NOTE
    compact["discovered_surfaces"] = len(payload["discovered_surfaces"])
    return compact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--registry-path", type=Path, default=None)
    parser.add_argument("--quality-adapter-path", type=Path, default=None)
    _summary_output.add_output_args(
        parser,
        summary_help="Emit compact YAML for agent review instead of every discovered surface",
        detail_help="Emit the full inventory payload as YAML",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    registry_path = args.registry_path or (repo_root / DEFAULT_REGISTRY_PATH)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path
    adapter_path = args.quality_adapter_path or (repo_root / DEFAULT_QUALITY_ADAPTER_PATH)
    if not adapter_path.is_absolute():
        adapter_path = repo_root / adapter_path
    payload = inventory(repo_root, registry_path, adapter_path)
    if not _summary_output.emit_selected(payload, args, summarize=summarize_payload):
        sys.stdout.write(dump_yaml({field: payload[field] for field in SUMMARY_FIELDS}))
    # Always 0. See the module docstring: an exported advisory that can fail a
    # consumer's lane is a defect, not a stricter gate.
    return 0


if __name__ == "__main__":
    sys.exit(main())
