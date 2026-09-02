"""Refuse to write repo state through a helper copy that has drifted from the target repo.

Four release publishes died to one shape: a charness helper was invoked from the
INSTALLED plugin tree with ``--repo-root`` pointing at the charness SOURCE tree.
The installed copy's libraries predated the source tree's schema, so the helper
wrote an old-schema artifact that the source repo's own gate then rejected. The
gate caught the damage but named a remediation ("run ``--write``") that cannot
work, because the next run through the same stale copy overwrites the fix again.

This module owns the provenance check those write helpers share: when the running
script belongs to one charness tree and ``--repo-root`` names a different charness
SOURCE tree, writing is refused unless the compared copies are provably identical.
When the target carries its own copy of the invoked helper, the refusal names it —
the only remediation that terminates. When it does not, the refusal says so and
tells the operator to stop and decide rather than resync-and-retry, because the
resync can be what removes the entry point.

"A different tree" includes a tree CONTAINED in the target: the materialized
``plugins/<pkg>`` export is a full second charness tree that this repo declares as
an install source, and it is stale during every ``mutate -> sync`` window.

A helper run against an ordinary consuming repo is untouched: that is the normal
installed-plugin case, and the consuming repo owns no competing copy.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable

# Dual-path, like every other consumer of this helper. A bare
# `from scripts.core.env_bypass import ...` turned a module whose imports were
# stdlib-only into one that requires `scripts` to be importable AS A PACKAGE.
# This module is mirrored into the exported plugin tree and is also imported
# FLAT by callers that put `scripts/` itself on `sys.path`
# (`tests/test_degradation_branch_coverage.py` does exactly that, and survived
# only because pytest independently puts the repo root on `sys.path` too).


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.core.env_bypass import env_bypass_enabled
except ModuleNotFoundError:
    _env_bypass_spec = importlib.util.spec_from_file_location(
        "env_bypass", Path(__file__).with_name("env_bypass.py")
    )
    if _env_bypass_spec is None or _env_bypass_spec.loader is None:
        raise
    _env_bypass = importlib.util.module_from_spec(_env_bypass_spec)
    sys.modules["env_bypass"] = _env_bypass
    _env_bypass_spec.loader.exec_module(_env_bypass)
    env_bypass_enabled = _env_bypass.env_bypass_enabled

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
    candidates: list[Path] = []
    if len(parts) > 1 and parts[0] == "skills" and parts[1] not in {"public", "support"}:
        tail = Path(*parts[1:])
        candidates = [Path("skills") / "public" / tail, Path("skills") / "support" / tail]
    elif len(parts) > 1 and parts[0] in {"support", "shared"}:
        # The exporter hoists `skills/support/<id>` and `skills/shared/**` to
        # top-level `support/<id>` and `shared/**`, so the remap has to run in this
        # direction too. Without the `shared` arm the export's shared helpers
        # resolved to no counterpart and were skipped by a scan that claims to
        # compare every module the tree could load.
        candidates = [Path("skills") / parts[0] / Path(*parts[1:])]
    # The identity candidate is always a fallback, never replaced: two trees in the
    # SAME layout (a second source checkout) share the path verbatim, and dropping
    # it silently skipped every `skills/shared/**` file.
    candidates.append(relative)
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
        # `support/` and `shared/` are where the EXPORTED layout puts the same script
        # packages `skills/` holds in the source layout; keying only on `skills` left
        # every exported support/shared entry point comparing one lone file.
        if anchor.relative_to(own_root).parts[0] in {"skills", "support", "shared"}:
            files.extend(sorted(p for p in anchor.parent.rglob("*.py") if p not in files))
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


_REFUSAL_DRIFT_LIMIT = 8
_OWN_ROOT_UNESTABLISHED = "own-root-unestablished"
_REFUSED_STATUSES = ("drifted", "scope-unestablished", _OWN_ROOT_UNESTABLISHED)
_EXPORT_PARENT = "plugins"
_RESYNC_CURE = "  python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root ."


def _is_materialized_export(verdict: dict) -> bool:
    """True only for the target repo's OWN materialized `plugins/<pkg>` export.

    Containment alone is the wrong test: a git worktree created inside the repo is
    also contained, and telling its operator to run the plugin resync would mutate
    the repo without touching the drift being reported.
    """
    own_root = verdict.get("own_root")
    if not own_root:
        return False
    try:
        relative = Path(own_root).relative_to(Path(verdict["target_root"]))
    except ValueError:
        return False
    return bool(relative.parts) and relative.parts[0] == _EXPORT_PARENT
_TREE_SCAN_SHIMS = ("runtime_bootstrap.py", "skill_runtime_bootstrap.py")
# `support/` and `shared/` are where the EXPORTED layout puts support skills and
# shared helpers; omitting them left 27 of the export's Python modules unscanned
# by a check that advertises "every module this tree could load".
_TREE_SCAN_ROOTS = ("scripts", "skills", "support", "shared")


def tree_python_files(own_root: Path) -> list[Path]:
    """Every Python module in this tree a run could load, imported yet or not.

    The anchor scan in ``_tracked_files`` can only see modules already in
    ``sys.modules`` (plus the anchors' skill siblings). A module the run imports
    *later* is therefore invisible to a check that runs *first* — which is
    exactly the gap an entrypoint guard exists to close. The drift that killed
    two publishes lived in ``scripts/recent_lessons_lib.py``, which the release
    path imports only when it writes the retro closeout, long after the
    entrypoint ran; an anchor scan at the entrypoint reports ``in-sync`` and
    waves the run through. Version comparison does not cover it either: the
    release helper bumps the target version *after* the entrypoint, so at
    entrypoint time the two trees still agree.
    """

    files: list[Path] = []
    for shim in _TREE_SCAN_SHIMS:
        candidate = own_root / shim
        if candidate.is_file():
            files.append(candidate)
    for sub in _TREE_SCAN_ROOTS:
        base = own_root / sub
        if not base.is_dir():
            continue
        files.extend(
            path for path in sorted(base.rglob("*.py")) if "__pycache__" not in path.parts
        )
    return files


def inspect_helper_provenance(
    script_file: str | Path,
    repo_root: str | Path,
    *,
    loaded_modules: Iterable[ModuleType] | None = None,
    scan: str = "anchors",
) -> dict:
    """Classify a helper invocation without acting on it.

    ``status`` is one of ``own-root-unestablished``, ``same-tree``,
    ``consuming-repo``, ``in-sync``, ``scope-unestablished``, or ``drifted``.
    ``drifted``, ``scope-unestablished`` and ``own-root-unestablished`` are refusals.

    ``scan`` selects which files are compared: ``anchors`` (the default, for
    write-site guards) walks the anchors plus already-imported modules;
    ``tree`` walks every Python module in the tree, which is what an entrypoint
    guard needs — see ``tree_python_files``.
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
        # A copy that sits in no locatable charness tree cannot be compared against
        # anything, so "own root unknown" is the absence of evidence, never a pass:
        # the stalest possible copy reaches this branch (a vendored or hand-copied
        # script package with no tree marker above it) and used to be waved straight
        # through into the source tree. Scope the refusal the way the located path is
        # scoped: only a charness SOURCE target owns a competing copy, so a run against
        # an ordinary consuming repo stays the untouched installed-plugin case.
        if not is_charness_source_tree(target_root):
            return {**verdict, "status": "consuming-repo"}
        return {
            **verdict,
            "target_version": charness_version(target_root),
            "status": _OWN_ROOT_UNESTABLISHED,
        }
    if own_root == target_root:
        return {**verdict, "status": "same-tree"}
    # A copy merely CONTAINED in the target root is not the same tree. The materialized
    # `plugins/<pkg>` mirror is a full second charness tree that this repo's own
    # packaging manifest declares as an install source, so exempting it made the one
    # copy that is stale during every `mutate -> sync` window structurally unchecked.
    # It falls through to the normal comparison: synced mirror -> `in-sync`, stale
    # mirror -> `drifted`.
    if not is_charness_source_tree(target_root):
        return {**verdict, "status": "consuming-repo"}

    own_version = charness_version(own_root)
    target_version = charness_version(target_root)
    invoked = entry_script(own_root) or script_path
    drifted: list[str] = []
    compared = (
        tree_python_files(own_root)
        if scan == "tree"
        else _tracked_files(own_root, [script_path, invoked], loaded_modules)
    )
    matched = 0
    unreadable: list[str] = []
    for tracked in compared:
        relative = tracked.relative_to(own_root)
        counterpart = counterpart_path(target_root, relative)
        if counterpart is None:
            continue
        matched += 1
        own_digest = _digest(tracked)
        # Two unreadable files both digest to `None` and would compare EQUAL — a
        # fail-open inside a fail-closed guard. An unreadable file is unproven, not
        # identical. Name it on its OWN side too: reporting only the target path
        # points the operator at a file that is fine.
        if own_digest is None:
            unreadable.append(str(relative))
        if own_digest is None or own_digest != _digest(counterpart):
            drifted.append(str(counterpart.relative_to(target_root)))
    entry_counterpart = counterpart_path(target_root, invoked.relative_to(own_root))
    verdict.update(
        {
            "own_version": own_version,
            "target_version": target_version,
            "version_mismatch": own_version != target_version,
            "drifted": sorted(drifted),
            "unreadable": sorted(unreadable),
            "scan": scan,
            "compared_count": len(compared),
            # Files SCANNED is not files COMPARED: a path with no counterpart in the
            # target is skipped above and still counted. Only this number establishes
            # the scope a clean verdict is reported over.
            "compared_pairs": matched,
            "invoked": str(invoked),
            "target_helper": (
                str(entry_counterpart.relative_to(target_root)) if entry_counterpart is not None else None
            ),
        }
    )
    if not matched:
        # When NOTHING resolved to a counterpart, "no drift found" is not a finding,
        # it is an empty scan — the same verdict-over-unestablished-scope this guard
        # exists to refuse. A rename of the whole script package in the target
        # reaches exactly this state. Unconditional by design: gating it on the
        # entry-counterpart test left a `tree`-scan path that still passed `in-sync`
        # over zero compared bytes.
        return {**verdict, "status": "scope-unestablished"}
    if entry_counterpart is None and not drifted and not verdict["version_mismatch"]:
        # The target source tree carries no copy of this helper, so there is no
        # repo-local alternative to demand. Two things this existence test must NOT
        # override, because both are evidence the run is foreign: a non-empty
        # `drifted` list the loop already computed, and a version mismatch.
        return {**verdict, "status": "consuming-repo"}
    if not verdict["version_mismatch"] and not drifted:
        return {**verdict, "status": "in-sync"}
    return {**verdict, "status": "drifted"}


def _is_repo_root_flag(token: str) -> bool:
    """argparse accepts any unambiguous prefix, so `--repo` reaches `--repo-root`."""

    return token.startswith("--") and len(token) > 2 and "--repo-root".startswith(token)


def _retargets_root(token: str, value: str, target_root: str) -> bool:
    """True when this token/value pair is the repo root the guard actually checked.

    A prefix match is NOT enough to rewrite a value. `issue_tool.py` declares
    `--repo` as its own required owner/repo option on the same subparsers that
    declare `--repo-root`, so treating every prefix as an abbreviation replaced
    `--repo corca-ai/charness` with `--repo .` and destroyed the target of an
    irreversible issue close. The exact spelling is always the root; an
    abbreviation is only the root when its value is the root the guard resolved.
    """
    if token == "--repo-root":
        return True
    if not _is_repo_root_flag(token):
        return False
    try:
        return Path(value).expanduser().resolve() == Path(target_root)
    except OSError:
        return False


def _remediation_argv(target_root: str) -> str:
    """The invocation rebuilt IN PLACE with the repo root retargeted to `.`.

    At a write site `--repo-root .` was the whole command. At an entrypoint it is
    not: `publish_release.py` requires one of `--publish-current/--part/--set-version`,
    so a remediation that drops them exits 2 again — the same
    remediation-that-cannot-terminate this module was written to kill.

    Position matters as much as presence. `issue_tool.py` declares `--repo-root` on
    each SUBparser, so hoisting the flag ahead of the remaining arguments printed
    `issue_tool.py --repo-root . close-with-comment ...`, which argparse rejects
    before it ever reads the subcommand. Rewriting the flag where the operator put
    it keeps both flat and subcommand CLIs runnable, and keeps an abbreviated
    spelling (`--repo`) bound to the target the guard actually checked.
    """
    import shlex

    argv = sys.argv[1:]
    kept: list[str] = []
    seen = False
    skip_next = False
    for index, token in enumerate(argv):
        if skip_next:
            skip_next = False
            continue
        flag, sep, value = token.partition("=")
        if sep and _retargets_root(flag, value, target_root):
            kept.extend([flag, "."])
            seen = True
            continue
        following = argv[index + 1] if index + 1 < len(argv) else ""
        if _retargets_root(token, following, target_root):
            kept.extend([token, "."])
            seen = True
            # A following token that is itself a flag was never this flag's value
            # (argparse would have rejected the invocation), so consuming it would
            # silently drop an argument from the printed remediation.
            skip_next = bool(following) and not following.startswith("--")
            continue
        kept.append(token)
    if not seen:
        kept.extend(["--repo-root", "."])
    return " " + " ".join(shlex.quote(part) for part in kept)


def format_refusal(verdict: dict) -> str:
    if verdict.get("status") == _OWN_ROOT_UNESTABLISHED:
        # Nothing was compared and nothing could be: there is no own tree to compare
        # FROM. Saying "the two copies have drifted" would claim a finding this branch
        # never reached, and naming a resync would cure a drift nobody established.
        return "\n".join(
            [
                "charness helper provenance refusal: this script sits in no locatable charness tree",
                f"(no {_OWN_ROOT_MARKER} above it), so its provenance against the target was not established.",
                f"  running: {verdict.get('invoked') or verdict['script']}",
                f"  target:  {verdict['target_root']} (charness {verdict.get('target_version') or 'unknown'})",
                "Writing through an unlocatable copy can emit an artifact schema the target repo's own",
                "gates reject, and nothing here proves this copy matches the target. Stop and decide:",
                "  - run the target repo's own copy of this helper from inside the target tree; or",
                "  - re-run from a complete charness tree, so this guard can compare the two copies.",
                f"Set {OVERRIDE_ENV}=1 only when the copies are known to be compatible.",
            ]
        )
    target_helper = verdict.get("target_helper")
    reason = (
        "and nothing in this copy could be compared against it."
        if verdict.get("status") == "scope-unestablished"
        else "and the two copies have drifted."
    )
    lines = [
        "charness helper provenance refusal: this script belongs to a different charness tree",
        f"than the --repo-root it was asked to write, {reason}",
        f"  running: {verdict.get('invoked') or verdict['script']} (charness {verdict.get('own_version') or 'unknown'})",
        f"  target:  {verdict['target_root']} (charness {verdict.get('target_version') or 'unknown'})",
    ]
    drifted = verdict.get("drifted") or []
    if drifted:
        # A tree scan can name hundreds of files; an unbounded join buries the
        # remediation line the operator actually needs under the evidence.
        shown = ", ".join(drifted[:_REFUSAL_DRIFT_LIMIT])
        if len(drifted) > _REFUSAL_DRIFT_LIMIT:
            shown += f", ... (+{len(drifted) - _REFUSAL_DRIFT_LIMIT} more)"
        lines.append(f"  drifted: {shown}")
    elif verdict.get("version_mismatch"):
        lines.append("  drifted: version manifests differ; loaded libraries were not compared")
    # The scope the verdict was reached over, printed rather than implied: files
    # scanned in this tree versus counterparts actually resolved and digested. A gap
    # is the part "compared everything" does not cover.
    if verdict.get("compared_count") is not None:
        lines.append(
            f"  compared: {verdict.get('compared_pairs')} of {verdict['compared_count']} scanned "
            f"module(s) had a counterpart in the target (scan={verdict.get('scan')})"
        )
    unreadable = verdict.get("unreadable") or []
    if unreadable:
        lines.append(
            f"  unreadable in this copy (counted as unproven, not identical): {', '.join(unreadable[:_REFUSAL_DRIFT_LIMIT])}"
        )
    lines.append(
        "Writing through this copy can emit an artifact schema the target repo's own gates reject,"
    )
    if _is_materialized_export(verdict):
        # The newly-compared population: this repo's own materialized export. Its drift
        # has a one-command cure, and it is the branch where the generic
        # "do not resync" advice below would be exactly backwards.
        lines.append("and re-running the same copy overwrites any fix. Resync the contained copy:")
        lines.append(_RESYNC_CURE)
        if target_helper is not None:
            lines.append("or run the target repo's own copy instead:")
            lines.append(
                f"  cd {verdict['target_root']} && python3 {target_helper}{_remediation_argv(verdict['target_root'])}"
            )
    elif target_helper is not None:
        lines.extend(
            [
                "and re-running the same copy overwrites any fix. Run the target repo's own copy instead:",
                f"  cd {verdict['target_root']} && python3 {target_helper}"
                f"{_remediation_argv(verdict['target_root'])}",
            ]
        )
    else:
        # The target carries no copy of the invoked entry point, so naming one would
        # hand the operator a command that does not exist. "Resync and re-run" is not
        # a remediation here either: the counterpart may be missing BECAUSE the target
        # dropped the helper, in which case the resync deletes the command being
        # re-run. The terminating instruction is to stop and decide, not to retry.
        lines.extend(
            [
                "and re-running the same copy overwrites any fix. The target repo carries no counterpart",
                "for the invoked entry point, so no repo-local command can be named. Stop here and decide:",
                f"  - the helper is newer than {verdict['target_root']}: run this work from a tree at the",
                "    target's revision, or update the target first;",
                "  - the target dropped the helper: this run should not proceed at all.",
                "Re-running after a resync is not a remediation; the resync can delete this entry point.",
            ]
        )
    lines.append(f"Set {OVERRIDE_ENV}=1 only when the copies are known to be compatible.")
    return "\n".join(lines)


def require_repo_local_helper(
    script_file: str | Path,
    repo_root: str | Path,
    *,
    loaded_modules: Iterable[ModuleType] | None = None,
    exit_on_drift: bool = True,
    stream=None,
    scan: str = "anchors",
) -> dict:
    """Refuse a drifted foreign-copy write; return the verdict when the write may proceed.

    ``exit_on_drift`` keeps CLI entry points operator-facing (message on stderr,
    exit status 2) while tests and callers that want to handle the condition
    themselves pass ``False`` and catch ``ForeignHelperError``.

    Pass ``scan="tree"`` at an entrypoint that will go on to perform an
    irreversible action, so drift in a not-yet-imported module is caught before
    the mutation starts rather than partway through it.
    """

    verdict = inspect_helper_provenance(
        script_file, repo_root, loaded_modules=loaded_modules, scan=scan
    )
    # `scope-unestablished` refuses for the same reason `drifted` does: neither has
    # evidence that this copy agrees with the target. "Found no drift" and "compared
    # nothing" are different facts, and only the first is a pass.
    if verdict["status"] not in _REFUSED_STATUSES:
        return verdict
    if env_bypass_enabled(OVERRIDE_ENV):
        print(
            f"warning: {OVERRIDE_ENV} is set; writing through an unverified helper copy "
            f"({verdict['status']}) "
            f"({verdict['script']} -> {verdict['target_root']})",
            file=stream or sys.stderr,
        )
        return {**verdict, "status": "override-allowed"}
    message = format_refusal(verdict)
    if not exit_on_drift:
        raise ForeignHelperError(message)
    print(message, file=stream or sys.stderr)
    raise SystemExit(2)
