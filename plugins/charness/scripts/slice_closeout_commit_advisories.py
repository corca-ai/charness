#!/usr/bin/env python3
"""Pre-push commit-hygiene slice-closeout advisories (#363, #364).

Split out of ``slice_closeout_advisories`` to keep both modules under the
function/file length budget. Two non-blocking advisories that fire author-time,
before the blocking gates they forecast, so the fix happens before a
rejected-commit / premature-close round-trip:

- ``advise_close_keyword_leakage`` (#363): a GitHub close keyword in an unpushed
  commit whose changed paths are not a plausible fix for the issue.
- ``advise_decaying_habits`` (#364): a changed ``scripts/*.py`` with a stale
  plugin mirror, and a changed test that subprocesses an import-safe
  ``scripts/*.py``.

Both reuse the real signals (the shared ``is_artifact_only_commit`` classifier,
the packaging mirror map, the boundary-bypass inventory) so they cannot drift
from the gates they forecast.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

_advisories = import_repo_module(__file__, "scripts.slice_closeout_advisories")
is_artifact_only_commit = _advisories.is_artifact_only_commit


# --- close-keyword-leakage advisory (#363) --------------------------------------
# A GitHub close keyword (close/fix/resolve + #N) auto-closes issue #N when pushed
# to the default branch, even when the commit is NOT the fix. #362 was auto-closed
# a day before its fix existed by a draft-goal-shaping commit whose body said
# "resolve #362". This advisory flags a close keyword in a commit whose changed
# paths are not a plausible fix for #N (an artifact-only goal-shaping / handoff
# commit). Non-blocking, per Floor-Addition Restraint (one recorded recurrence).
# Keyword forms GitHub honors: close/closes/closed, fix/fixes/fixed,
# resolve/resolves/resolved, directly before `#N` (or owner/repo#N, or the full
# issues URL) with optional `:` and whitespace.
_CLOSE_KEYWORD_RE = re.compile(
    r"\b(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)[\s:]+"
    r"(?:https?://github\.com/[\w.-]+/[\w.-]+/issues/(?P<url>\d+)"
    r"|(?:[\w.-]+/[\w.-]+)?#(?P<num>\d+))",
    re.IGNORECASE,
)


def parse_close_keyword_refs(message: str) -> list[int]:
    """Issue numbers referenced by a GitHub close keyword in ``message`` (the live
    auto-close carrier). De-duplicated, in first-seen order. A bare ``#N`` mention
    with no close verb adjacent is intentionally NOT matched."""
    refs: list[int] = []
    for match in _CLOSE_KEYWORD_RE.finditer(message):
        number = match.group("url") or match.group("num")
        value = int(number)
        if value not in refs:
            refs.append(value)
    return refs


def _unpushed_commits(repo_root: Path, base: str) -> list[tuple[str, str, list[str]]]:
    """``(sha, message, changed_paths)`` for each commit in ``base``..HEAD (the
    not-yet-pushed range, where a close keyword has not yet auto-closed anything).
    Degrades to ``[]`` when ``base`` does not resolve (tmp repos / no upstream)."""
    probe = subprocess.run(["git", "rev-parse", "--verify", "--quiet", base], cwd=repo_root, capture_output=True)
    if probe.returncode != 0:
        return []
    rev_list = subprocess.run(
        ["git", "rev-list", f"{base}..HEAD"], cwd=repo_root, capture_output=True, text=True
    )
    if rev_list.returncode != 0:
        return []
    commits: list[tuple[str, str, list[str]]] = []
    for sha in rev_list.stdout.split():
        message = subprocess.run(
            ["git", "log", "-1", "--format=%B", sha], cwd=repo_root, capture_output=True, text=True
        )
        show = subprocess.run(
            ["git", "show", "--pretty=format:", "--name-only", sha], cwd=repo_root, capture_output=True, text=True
        )
        if message.returncode != 0 or show.returncode != 0:
            break
        paths = [line for line in show.stdout.splitlines() if line.strip()]
        commits.append((sha, message.stdout, paths))
    return commits


def advise_close_keyword_leakage(repo_root: Path, base: str = "origin/main") -> None:
    """Non-blocking advisory (#363): an unpushed commit carries a close keyword for
    #N but its changed paths are not a plausible fix for #N (an artifact-only
    goal-shaping / handoff commit). Pushing it to the default branch would
    auto-close #N before its fix lands. Reuses the shared ``is_artifact_only_commit``
    signal (no drift) and degrades silently off a git repo / unresolved ``base``."""
    findings: list[str] = []
    for sha, message, changed_paths in _unpushed_commits(repo_root, base):
        refs = parse_close_keyword_refs(message)
        if refs and is_artifact_only_commit(changed_paths):
            issues = ", ".join(f"#{ref}" for ref in refs)
            findings.append(f"{sha[:9]} ({issues})")
    if not findings:
        return
    print(
        "ADVISORY: close keyword in a commit whose changed paths are not a plausible "
        "fix (artifact-only) — pushing to the default branch auto-closes the issue "
        "before its fix lands (#363): " + "; ".join(findings) + ". If this commit is "
        "NOT the fix (a goal-shaping / handoff / draft commit), reword the body to "
        "cite the issue as a bare `#N` or URL with no close verb adjacent "
        "(close/fix/resolve), then `git commit --amend`/rebase before push. The close "
        "keyword belongs in the commit (or PR body) that actually fixes the issue.",
        file=sys.stderr,
    )


# --- decaying-habit advisories (#364) -------------------------------------------
# Two pre-commit-gate author habits whose persisted lessons keep decaying and
# re-violating, each paying a reject->fix->re-commit round-trip: (1) a repo-root
# scripts/*.py change must be mirrored into the plugin tree
# (sync_root_plugin_manifests.py) before the staged-mirror-drift gate; (2) a test
# that needs the verdict of an import-safe scripts/*.py should call its main()
# in-process, not subprocess it (the boundary-bypass ratchet). Non-blocking and
# author-time: they fire EARLIER than the blocking gates already in place, per
# Floor-Addition Restraint (recorded recurrence -> advisory, not a new floor).
# Both reuse the real signals (the packaging mirror map; the boundary-bypass
# inventory) so they cannot drift from the gates they forecast.


def _changed_scripts_mirror_drift(repo_root: Path, changed_paths: list[str]) -> list[str]:
    """Changed ``scripts/*.py`` whose checked-in plugin mirror does not match the
    working-tree source (the proactive-mirror-sync habit). Reuses the packaging
    manifest's plugin root (``checked_in_plugin_root``) so the mirror path is not
    hand-hardcoded; degrades to ``[]`` when the manifest cannot be loaded."""
    changed_scripts = [p for p in changed_paths if p.startswith("scripts/") and p.endswith(".py")]
    if not changed_scripts:
        return []
    try:
        packaging = import_repo_module(__file__, "scripts.packaging_lib")
        plugin_root = packaging.checked_in_plugin_root(packaging.load_manifest(repo_root, "charness"))
    except Exception:
        return []
    drifted: list[str] = []
    for path in changed_scripts:
        source = repo_root / path
        mirror = repo_root / plugin_root / path
        if not source.is_file():
            continue
        if not mirror.is_file() or mirror.read_bytes() != source.read_bytes():
            drifted.append(path)
    return drifted


def _changed_tests_boundary_bypass(repo_root: Path, changed_paths: list[str]) -> list[tuple[str, list[str]]]:
    """Changed ``tests/**/test_*.py`` that spawn an import-safe ``scripts/*.py``
    through a process boundary when an in-process ``main()`` exists (the
    in-process-test-default habit). Reuses the boundary-bypass inventory's real
    detection and honors its exemptions file (an intentional boundary is not
    nagged); degrades to ``[]`` when the probe cannot be loaded."""
    changed_tests = [
        p for p in changed_paths
        if p.startswith("tests/") and p.endswith(".py") and Path(p).name.startswith("test_")
    ]
    if not changed_tests:
        return []
    try:
        inventory = import_repo_module(__file__, "scripts.inventory_boundary_bypass_lib")
        ratchet = import_repo_module(__file__, "scripts.boundary_bypass_ratchet_lib")
        exemptions = ratchet.load_exemptions(repo_root / ratchet.DEFAULT_EXEMPTIONS_PATH)
    except Exception:
        return []
    findings: list[tuple[str, list[str]]] = []
    for path in changed_tests:
        if not (repo_root / path).is_file():
            continue
        try:
            row = inventory.analyze_test_file(repo_root, repo_root / path)
        except OSError:
            continue
        if row is None or row["likely_keep_boundary"]:
            continue
        convertible = [
            target for target in row["clean_inprocess_targets"]
            if ratchet.candidate_key(path, target) not in exemptions
        ]
        if convertible:
            findings.append((path, convertible))
    return findings


def advise_decaying_habits(repo_root: Path, changed_paths: list[str]) -> None:
    """Non-blocking author-time advisories (#364) for the two recurring
    pre-commit-gate habits, firing before the blocking gates (staged-mirror-drift,
    boundary-bypass ratchet) so the fix happens before the rejected-commit
    round-trip."""
    drifted = _changed_scripts_mirror_drift(repo_root, changed_paths)
    if drifted:
        print(
            "ADVISORY: changed repo-root scripts/*.py with a stale plugin mirror (#364): "
            + ", ".join(drifted) + ". scripts/*.py is part of the plugin install surface; "
            "run `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and `git add` "
            "the regenerated plugins/ BEFORE the commit gate, not after the staged-mirror-drift "
            "rejection.",
            file=sys.stderr,
        )
    bypass = _changed_tests_boundary_bypass(repo_root, changed_paths)
    if bypass:
        rendered = "; ".join(f"{test} -> {', '.join(targets)}" for test, targets in bypass)
        print(
            "ADVISORY: changed test(s) subprocess an import-safe scripts/*.py when an "
            "in-process path exists (#364): " + rendered + ". Prefer calling the script's "
            "main() in-process (patch argv) or a *_lib function over "
            "subprocess.run([\"python3\", \"scripts/...\"]) — the boundary-bypass ratchet "
            "blocks the subprocess form. If the boundary is intentional (exit-code/stderr "
            "contract), add it to scripts/boundary-bypass-exemptions.txt with a `# why:`.",
            file=sys.stderr,
        )
