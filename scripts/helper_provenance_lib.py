"""Refuse to write repo state through a helper copy that has drifted from the target repo.

Four release publishes died to one shape: a charness helper was invoked from the
INSTALLED plugin tree with ``--repo-root`` pointing at the charness SOURCE tree.
The installed copy's libraries predated the source tree's schema, so the helper
wrote an old-schema artifact that the source repo's own gate then rejected. The
gate caught the damage but named a remediation ("run ``--write``") that cannot
work, because the next run through the same stale copy overwrites the fix again.

This module owns the provenance check those write helpers share: when the running
script belongs to one charness tree and ``--repo-root`` names a different charness
SOURCE tree that carries its own copy of the same helper, writing is refused
unless the two copies are provably identical. The refusal names the target repo's
own copy, which is the only remediation that terminates.

A helper run against an ordinary consuming repo is untouched: that is the normal
installed-plugin case, and the consuming repo owns no competing copy.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable

OVERRIDE_ENV = "CHARNESS_ALLOW_FOREIGN_HELPER"
SOURCE_TREE_MARKER = Path("packaging") / "charness.json"
_OWN_ROOT_MARKER = Path("scripts") / "runtime_bootstrap.py"
_VERSION_SOURCES = (
    SOURCE_TREE_MARKER,
    Path(".claude-plugin") / "plugin.json",
    Path("plugins") / "charness" / ".claude-plugin" / "plugin.json",
)


class ForeignHelperError(RuntimeError):
    """A drifted helper copy tried to write into the charness source tree."""


def own_tree_root(script_file: str | Path) -> Path | None:
    """Return the charness tree the running script itself belongs to."""

    script_path = Path(script_file).resolve()
    for ancestor in script_path.parents:
        if (ancestor / _OWN_ROOT_MARKER).is_file():
            return ancestor
    return None


def is_charness_source_tree(root: Path) -> bool:
    """True when ``root`` is a charness SOURCE checkout, not a consuming repo."""

    manifest = root / SOURCE_TREE_MARKER
    if not manifest.is_file():
        return False
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and payload.get("package_id") == "charness"


def charness_version(root: Path) -> str | None:
    """Read the declared charness version of a source tree or exported plugin root."""

    for relative in _VERSION_SOURCES:
        candidate = root / relative
        if not candidate.is_file():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        version = payload.get("version") if isinstance(payload, dict) else None
        if isinstance(version, str) and version:
            return version
    return None


def counterpart_path(target_root: Path, relative: Path) -> Path | None:
    """Map a path relative to one charness tree onto the same file in another.

    Exported plugin trees flatten ``skills/public/<id>`` and ``skills/support/<id>``
    to ``skills/<id>``, so a relative path alone does not identify the source-tree
    file. Only paths that actually exist in ``target_root`` are returned.
    """

    parts = relative.parts
    candidates: list[Path] = [relative]
    if len(parts) > 1 and parts[0] == "skills" and parts[1] not in {"public", "support"}:
        tail = Path(*parts[1:])
        candidates = [Path("skills") / "public" / tail, Path("skills") / "support" / tail]
    for candidate in candidates:
        resolved = target_root / candidate
        if resolved.is_file():
            return resolved
    return None


def entry_script(own_root: Path) -> Path | None:
    """The script the operator actually invoked, when it belongs to the same tree.

    A guard called from a library knows only the library's own path, and naming
    `scripts/recent_lessons_lib.py --repo-root .` as the remediation would hand the
    operator a command that is not runnable. ``sys.argv[0]`` is the invoked
    entry point, so the refusal can name a command that works.
    """
    if not sys.argv or not sys.argv[0]:
        return None
    try:
        candidate = Path(sys.argv[0]).resolve()
    except OSError:
        return None
    if candidate.is_file() and candidate.is_relative_to(own_root):
        return candidate
    return None


def _digest(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _tracked_files(own_root: Path, anchors: Iterable[Path], loaded_modules: Iterable[ModuleType] | None) -> list[Path]:
    """The anchor files plus every already-imported module that came from the same tree.

    ``anchors`` are the guarding module and the invoked entry point -- both, because a
    guard called from a library sees only the library, and the drift may be in the
    entry script it was called from.

    Skill script packages also contribute their sibling modules: they are loaded
    through ``load_local_skill_module``, which bypasses ``sys.modules``, so a
    module-scan alone would miss exactly the libraries these helpers write through.
    """

    modules = list(sys.modules.values()) if loaded_modules is None else list(loaded_modules)
    files: list[Path] = []
    for anchor in anchors:
        if anchor in files:
            continue
        files.append(anchor)
        if anchor.relative_to(own_root).parts[0] == "skills":
            files.extend(sorted(p for p in anchor.parent.glob("*.py") if p not in files))
    for module in modules:
        module_file = getattr(module, "__file__", None)
        if not isinstance(module_file, str):
            continue
        try:
            resolved = Path(module_file).resolve()
        except OSError:
            continue
        if resolved.suffix != ".py" or resolved in files:
            continue
        if resolved.is_relative_to(own_root):
            files.append(resolved)
    return files


def inspect_helper_provenance(
    script_file: str | Path,
    repo_root: str | Path,
    *,
    loaded_modules: Iterable[ModuleType] | None = None,
) -> dict:
    """Classify a helper invocation without acting on it.

    ``status`` is one of ``own-root-unknown``, ``same-tree``, ``consuming-repo``,
    ``in-sync``, or ``drifted``. Only ``drifted`` is a refusal.
    """

    script_path = Path(script_file).resolve()
    target_root = Path(repo_root).resolve()
    own_root = own_tree_root(script_path)
    verdict: dict = {
        "script": str(script_path),
        "target_root": str(target_root),
        "own_root": str(own_root) if own_root is not None else None,
    }
    if own_root is None:
        return {**verdict, "status": "own-root-unknown"}
    if own_root == target_root or script_path.is_relative_to(target_root):
        return {**verdict, "status": "same-tree"}
    if not is_charness_source_tree(target_root):
        return {**verdict, "status": "consuming-repo"}

    own_version = charness_version(own_root)
    target_version = charness_version(target_root)
    invoked = entry_script(own_root) or script_path
    drifted: list[str] = []
    for tracked in _tracked_files(own_root, [script_path, invoked], loaded_modules):
        relative = tracked.relative_to(own_root)
        counterpart = counterpart_path(target_root, relative)
        if counterpart is None:
            continue
        if _digest(tracked) != _digest(counterpart):
            drifted.append(str(counterpart.relative_to(target_root)))
    entry_counterpart = counterpart_path(target_root, invoked.relative_to(own_root))
    verdict.update(
        {
            "own_version": own_version,
            "target_version": target_version,
            "version_mismatch": own_version != target_version,
            "drifted": sorted(drifted),
            "invoked": str(invoked),
            "target_helper": (
                str(entry_counterpart.relative_to(target_root)) if entry_counterpart is not None else None
            ),
        }
    )
    if entry_counterpart is None:
        # The target source tree carries no copy of this helper, so there is no
        # repo-local alternative to demand.
        return {**verdict, "status": "consuming-repo"}
    if not verdict["version_mismatch"] and not drifted:
        return {**verdict, "status": "in-sync"}
    return {**verdict, "status": "drifted"}


def format_refusal(verdict: dict) -> str:
    target_helper = verdict.get("target_helper")
    lines = [
        "charness helper provenance refusal: this script belongs to a different charness tree",
        "than the --repo-root it was asked to write, and the two copies have drifted.",
        f"  running: {verdict.get('invoked') or verdict['script']} (charness {verdict.get('own_version') or 'unknown'})",
        f"  target:  {verdict['target_root']} (charness {verdict.get('target_version') or 'unknown'})",
    ]
    drifted = verdict.get("drifted") or []
    if drifted:
        lines.append(f"  drifted: {', '.join(drifted)}")
    elif verdict.get("version_mismatch"):
        lines.append("  drifted: version manifests differ; loaded libraries were not compared")
    lines.extend(
        [
            "Writing through this copy can emit an artifact schema the target repo's own gates reject,",
            "and re-running the same copy overwrites any fix. Run the target repo's own copy instead:",
            f"  cd {verdict['target_root']} && python3 {target_helper} --repo-root .",
            f"Set {OVERRIDE_ENV}=1 only when the copies are known to be compatible.",
        ]
    )
    return "\n".join(lines)


def require_repo_local_helper(
    script_file: str | Path,
    repo_root: str | Path,
    *,
    loaded_modules: Iterable[ModuleType] | None = None,
    exit_on_drift: bool = True,
    stream=None,
) -> dict:
    """Refuse a drifted foreign-copy write; return the verdict when the write may proceed.

    ``exit_on_drift`` keeps CLI entry points operator-facing (message on stderr,
    exit status 2) while tests and callers that want to handle the condition
    themselves pass ``False`` and catch ``ForeignHelperError``.
    """

    verdict = inspect_helper_provenance(script_file, repo_root, loaded_modules=loaded_modules)
    if verdict["status"] != "drifted":
        return verdict
    if os.environ.get(OVERRIDE_ENV):
        print(
            f"warning: {OVERRIDE_ENV} is set; writing through a drifted helper copy "
            f"({verdict['script']} -> {verdict['target_root']})",
            file=stream or sys.stderr,
        )
        return {**verdict, "status": "override-allowed"}
    message = format_refusal(verdict)
    if not exit_on_drift:
        raise ForeignHelperError(message)
    print(message, file=stream or sys.stderr)
    raise SystemExit(2)
