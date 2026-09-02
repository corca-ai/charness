#!/usr/bin/env python3
"""Edit-time advisory for the duplicate-ratchet trap (#474).

The length-headroom advisory already exists so the "append until the hard gate
fires" trap is a workflow affordance rather than agent memory. Its sibling trap
had no such affordance: `check_dup_ratchet.py` runs only in the closeout
aggregate, where a new duplicate family is a HARD BLOCK discovered after the
slice is finished and the commit message is written.

Four consecutive runs wrote "run the dup ratchet early" into a plan and hit it
at the aggregate anyway. A prose checklist fires exactly when nobody is reading
the prose, which is the whole point: this moves the signal to the moment the
duplication is being written.

Two deliberate scoping choices, both about NOT training token-theater:

* **Scope, not membership.** The gate baseline stores family fingerprints, not
  member paths, so "is this file already in a family" cannot be answered without
  re-running the scanner (measured ~2.8s). This advisory answers the cheap
  question the issue actually asked — is this file inside the ratchet's declared
  scope — and points at the real command.
* **Substantial additions only.** Every edit to every scanned file would fire on
  almost every edit in this repo. A new duplicate family needs a meaningful block
  of new code, so the trigger is added lines in this file versus HEAD, over a
  threshold. A one-line tweak to a scanned file says nothing and stays silent.

Advisory only, never a gate: the hard arm stays exactly where it is. This adds an
early signal, not a new floor.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

try:
    from scripts.git_checkout import head_oid_from_files
except ModuleNotFoundError:  # invoked as `python3 scripts/dup_ratchet_edit_advisory.py`
    from git_checkout import head_oid_from_files

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

#: Fallback when the adapter cannot be read. Kept identical to the shipped
#: `.agents/quality-adapter.yaml` `dup_ratchet.scope_paths` default.
DEFAULT_SCOPE_PATHS = ("scripts", "skills/public", "skills/support")

#: Added lines in ONE file, versus HEAD, before the advisory fires. A new
#: fixable duplicate family is a repeated block, not a line: below this the
#: signal would be noise, and a noisy advisory is worse than none.
DEFAULT_ADDED_LINE_THRESHOLD = 30

# The ratchet is not Python-only: this repo already carries two checked-in `.mjs`
# duplicate families, and `dup-ratchet.md` explicitly contemplates a non-Python
# family member. A `.py`-only advisory would be silent for exactly those.
_SCANNED_SUFFIXES = (".py", ".mjs", ".sh")


def _resolve_scope_prefixes(
    repo_root: Path, roots: tuple[str, ...]
) -> tuple[list[str] | None, list[str]]:
    """Load the canonical scope resolver from the source or exported layout.

    This root-level advisory runs from both layouts. The public skill's
    ``skills/public`` segment is flattened in an export, so a package import
    would work in only one of them. If the resolver is unavailable, the scope is
    unknown and the advisory stays conservative instead of reviving the raw
    prefix comparison.
    """

    bases = (repo_root, Path(__file__).resolve().parents[1])
    seen: set[Path] = set()
    for base in bases:
        for relative in (
            Path("skills/public/quality/scripts/dup_ratchet_scope.py"),
            Path("skills/quality/scripts/dup_ratchet_scope.py"),
        ):
            candidate = (base / relative).resolve()
            if candidate in seen or not candidate.is_file():
                continue
            seen.add(candidate)
            spec = importlib.util.spec_from_file_location(
                "_dup_ratchet_scope_for_edit_advisory", candidate
            )
            if spec is None or spec.loader is None:
                continue
            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                resolver = module.resolve_scope_prefixes
            except (AttributeError, ImportError, OSError, SyntaxError, TypeError, ValueError):
                continue
            return resolver(roots)
    return [], list(roots)


def scope_paths(repo_root: Path) -> tuple[str, ...]:
    """The ratchet's declared scope, read from the adapter with a pinned fallback."""

    adapter = repo_root / ".agents/quality-adapter.yaml"
    if not adapter.is_file():
        return DEFAULT_SCOPE_PATHS
    try:
        import yaml  # imported lazily: the advisory must never break an edit
    except ImportError:  # pragma: no cover - yaml is a repo dependency
        return DEFAULT_SCOPE_PATHS
    try:
        data = yaml.safe_load(adapter.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return DEFAULT_SCOPE_PATHS
    if not isinstance(data, dict):
        return DEFAULT_SCOPE_PATHS
    section = data.get("dup_ratchet")
    if not isinstance(section, dict) or not section.get("enabled", False):
        # A disabled ratchet cannot hard-block, so there is nothing to warn about
        # — and neither can an ABSENT one. Falling back to the default scope when
        # the section is missing would make this advisory fire in a consumer repo
        # that never opted into the ratchet, pointing at a command that may not
        # exist there. The fallback below is for an unreadable adapter only.
        return ()
    declared = section.get("scope_paths")
    if not isinstance(declared, list) or not declared:
        return DEFAULT_SCOPE_PATHS
    return tuple(str(entry) for entry in declared if isinstance(entry, str))


def in_ratchet_scope(
    relpath: str, roots: tuple[str, ...], *, repo_root: Path | None = None
) -> bool:
    """Whether the ratchet would scan this repo-relative path at all."""

    if not relpath.endswith(_SCANNED_SUFFIXES):
        return False
    # Generated mirrors carry the same code but are not independently authored,
    # and the ratchet does not scan them. Warning about them would send an author
    # to fix a file that is regenerated from the one they should be editing.
    if relpath.startswith("plugins/"):
        return False
    posix = Path(relpath).as_posix()
    prefixes, _unresolvable = _resolve_scope_prefixes(
        repo_root or Path(__file__).resolve().parents[1], roots
    )
    if prefixes is None:
        return True
    # A known literal prefix remains useful when a declaration also contains a
    # glob or another shape this prefix matcher cannot resolve. Unknown entries
    # never widen the advisory to every path.
    return any(posix == root or posix.startswith(f"{root}/") for root in prefixes)


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    """One git invocation, or None when git itself could not be run.

    Local and tiny on purpose: an advisory on an edit-time hook must never raise,
    so every git failure collapses to "no answer" and the advisory stays silent.
    """

    try:
        return run_process(["git", *args], cwd=repo_root, timeout_seconds=10)
    except OSError:
        return None


def added_lines_vs_head(repo_root: Path, relpath: str) -> int | None:
    """Added lines for one path versus HEAD, or None when git cannot answer.

    A brand-new untracked file counts as fully added: that is the case most
    likely to introduce a family, and `git diff HEAD` alone would report nothing
    for it.
    """

    proc = _git(repo_root, "diff", "--numstat", "HEAD", "--", relpath)
    if proc is None or proc.returncode != 0:
        return None
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].isdigit():
            return int(parts[0])
    target = repo_root / relpath
    if not target.is_file():
        return None
    from scripts.checkout_view import GitCheckout, path_is_tracked

    tracked = path_is_tracked(GitCheckout(repo_root), relpath)
    if tracked is None:
        return None
    if tracked:
        return 0  # tracked and unchanged versus HEAD
    try:
        return len(target.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return None


_SEEN_RELPATH = ".charness/dup-ratchet/advised.json"


def _already_advised(repo_root: Path, relpath: str, head: str | None) -> bool:
    """Whether this (file, HEAD) pair has already been advised about.

    Without this the advisory re-fires on EVERY later edit to the same file --
    a typo fix, a one-word rename -- because `added_lines_vs_head` measures
    cumulative additions versus HEAD rather than this edit's delta. Repeated
    identical advisories are the token-theater this module exists to avoid, and
    they would also make "warns at the FIRST substantial addition" false.

    Keyed by HEAD so the signal returns after a commit moves the baseline.
    """

    if head is None:
        return False
    path = repo_root / _SEEN_RELPATH
    try:
        seen = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        seen = {}
    if not isinstance(seen, dict) or seen.get("head") != head:
        seen = {"head": head, "paths": []}
    paths = seen.get("paths")
    if not isinstance(paths, list):
        paths = []
    if relpath in paths:
        return True
    paths.append(relpath)
    seen["paths"] = paths
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(seen), encoding="utf-8")
    except OSError:
        # Unwritable state means we re-advise rather than go silent: a repeated
        # advisory is noise, a missed one is the trap this exists to catch.
        return False
    return False


def advise_for_edited_file(
    repo_root: Path,
    relpath: str,
    *,
    threshold: int = DEFAULT_ADDED_LINE_THRESHOLD,
    added: int | None = None,
    head_sha: str | None = None,
) -> str | None:
    """The advisory text for a just-edited file, or None to stay silent."""

    roots = scope_paths(repo_root)
    if not roots or not in_ratchet_scope(relpath, roots, repo_root=repo_root):
        return None
    added_count = added_lines_vs_head(repo_root, relpath) if added is None else added
    if added_count is None or added_count < threshold:
        return None
    if head_sha is None:
        # `.git/HEAD` already states this; a `rev-parse` subprocess purely to key
        # a dedupe cache asked Git a question the checkout files already answer
        # (see `scripts.git_checkout.head_oid_from_files`).
        head_sha = head_oid_from_files(repo_root)
    if _already_advised(repo_root, relpath, head_sha):
        return None
    return advisory_message(relpath, added_count)


def advisory_message(relpath: str, added: int) -> str:
    """The advisory prose, with no dedupe state and no side effect.

    Split out of `advise_for_edited_file` so the CLI can carry the remediation
    text in its payload. The CLI emits unconditional YAML, and the remediation --
    which command to run, and how to classify a deliberate family -- is the only
    part of this module a reader cannot reconstruct from `advisory_state`. The
    hook path still goes through `advise_for_edited_file` so its once-per-HEAD
    dedupe (and the state write that implements it) stays where it was.
    """

    return (
        f"ADVISORY (dup ratchet): {relpath} is inside the duplicate-ratchet scope "
        f"and this slice has added {added} lines to it. A new fixable duplicate "
        "family is a HARD BLOCK at the closeout aggregate, discovered after the "
        "slice is finished and the commit message is written. Check it now:\n"
        "  python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary\n"
        "If the duplication is deliberate, classify the family `intentional` in "
        "charness-artifacts/quality/dup-review.json with the reason; prefer the "
        "scoped accepts over --write-baseline. Advisory only, never blocks."
    )


def advisory_state(
    repo_root: Path, relpath: str, *, threshold: int = DEFAULT_ADDED_LINE_THRESHOLD
) -> dict:
    """Structured form of the same decision, for tests and callers that want the why."""

    roots = scope_paths(repo_root)
    in_scope = bool(roots) and in_ratchet_scope(relpath, roots, repo_root=repo_root)
    added = added_lines_vs_head(repo_root, relpath) if in_scope else None
    return {
        "path": relpath,
        "scope_paths": list(roots),
        "in_scope": in_scope,
        "added_lines": added,
        "threshold": threshold,
        "fires": bool(in_scope and added is not None and added >= threshold),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    # Resolved HERE, not at module import. This module also rides an edit-time
    # PostToolUse hook, where it is imported as `scripts.dup_ratchet_edit_advisory`
    # with the REPO ROOT on `sys.path`, while `python3 scripts/...` puts `scripts/`
    # there instead. A single top-level spelling is wrong in one of the two
    # contexts, and the hook path must not pay for the CLI's renderer at all.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from scripts.yaml_output import emit_yaml

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--path", required=True, help="Repo-relative path just edited.")
    parser.add_argument("--threshold", type=int, default=DEFAULT_ADDED_LINE_THRESHOLD)
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    state = advisory_state(repo_root, args.path, threshold=args.threshold)
    # The remediation prose rides along in the payload rather than on a second
    # stream. The CLI reads the decision WITHOUT the once-per-HEAD dedupe write,
    # because a diagnostic read must not silence the hook's next real advisory.
    state["advisory"] = (
        advisory_message(args.path, int(state["added_lines"])) if state["fires"] else None
    )
    emit_yaml(state)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
