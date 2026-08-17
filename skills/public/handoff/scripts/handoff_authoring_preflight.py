#!/usr/bin/env python3
"""Pre-edit handoff checks as one cohesive authoring boundary."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

HANDOFF_AUTHORING_ACTIONS = frozenset({"refresh_handoff", "repair_or_prune_handoff"})
PREFLIGHT = "scripts/check_doc_authoring_preflight.py"
#: The entrypoints the probe starts its walk from. NOT the dependency list -- see
#: `preflight_dependencies`, which derives that from the sources.
PREFLIGHT_ROOTS = (PREFLIGHT, "scripts/doc_authoring_rules.py")

#: Imported by name (not through the shim) by every repo script, so no source scan finds
#: them. Absent, the emitted command dies on its first import line.
_BOOTSTRAP_MODULES = ("scripts/runtime_bootstrap.py", "scripts/yaml_output.py")

#: The two spellings a repo script uses to reach a sibling: the `import_repo_module`
#: shim, and a plain `from scripts.<name> import ...`. Both were needed -- the shim
#: alone missed `scripts/repo_layout.py`, which `repo_file_listing` imports the plain
#: way, and the execution assertion in this probe's guard test is what surfaced it.
_SIBLING_IMPORT_RE = re.compile(
    r'import_repo_module\([^,]+,\s*"scripts\.([A-Za-z0-9_]+)"'
    r"|(?:^|\W)from\s+scripts\.([A-Za-z0-9_]+)\s+import"
)


def preflight_dependencies(repo_root: Path) -> tuple[str, ...]:
    """Every repo file the emitted command imports, derived from the sources themselves.

    This was a hand-written two-entry tuple, and hand-written is why it was wrong. It
    listed the entrypoint and `doc_authoring_rules.py`; the command's actual closure in
    this repo is fourteen files plus two bootstrap modules, so a repo carrying exactly
    the listed pair got a command advertised as available that dies on
    `ModuleNotFoundError` -- the failure the list exists to prevent, present since before
    the list was written and made one file worse by splitting `markdownlint_probe.py` out.
    Its guard test could not see any of it: the test seeded whatever the tuple named and
    asserted the tuple's own entries were each required, which is self-consistency, not
    completeness.

    Deriving closes the class rather than the instance. A new sibling import is picked up
    with no edit here and no edit in the test.

    Blind class: this reads the TARGET repo's sources with a regex, so it sees only the
    `import_repo_module(..., "scripts.X")` spelling. A dependency reached by a computed
    module name, an `exec`, or a plain `sys.path` import of a repo file is invisible, and
    such a command would still be advertised and still crash. The bootstrap modules are
    listed explicitly for exactly that reason -- they are imported by bare name.
    """
    seen: set[str] = set()
    stack = list(PREFLIGHT_ROOTS)
    while stack:
        rel = stack.pop()
        if rel in seen:
            continue
        seen.add(rel)
        source = repo_root / rel
        if not source.is_file():
            # A missing file is what the caller is probing for; stop walking THROUGH it
            # rather than guessing at imports it would have made.
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            continue
        stack.extend(
            f"scripts/{shim or plain}.py" for shim, plain in _SIBLING_IMPORT_RE.findall(text)
        )
    return tuple(sorted(seen | set(_BOOTSTRAP_MODULES)))


def _item(why: str, command: str) -> dict[str, Any]:
    return {
        "path": PREFLIGHT,
        "why": why,
        "kind": "preflight",
        "base": "repo",
        "command": command,
    }


def required_reads(repo_root: Path, artifact_path: str) -> list[dict[str, Any]]:
    """Return rules-first, target-second checks when the repo can run them.

    Rules mode forecasts the contract. Target mode reports deterministic
    findings already present in the current artifact. Semantic proof-receipt
    ownership remains agent judgment in the handoff skill's phase barrier.
    """
    if any(not (repo_root / required).is_file() for required in preflight_dependencies(repo_root)):
        return []
    surface = "handoff" if artifact_path.endswith("handoff.md") else None
    rules_command = f"python3 {PREFLIGHT} --repo-root ."
    if surface:
        rules_command += f" --as-surface {surface}"
    reads = [
        _item("deterministic rules for this surface BEFORE writing into it", rules_command)
    ]
    if (repo_root / artifact_path).is_file():
        reads.append(
            _item(
                "deterministic findings already present in the current handoff BEFORE rewriting it",
                f"python3 {PREFLIGHT} --repo-root . --path {artifact_path}",
            )
        )
    return reads
