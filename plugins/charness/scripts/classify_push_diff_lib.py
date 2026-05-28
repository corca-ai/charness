"""Classify a pending git push as docs/artifact-only vs full-gate-required.

The pre-push hook (`.githooks/pre-push`) reads this classification to decide
whether to skip the ~100-120s broad quality gate on a bookkeeping-only push.
Closes [#230](https://github.com/corca-ai/charness/issues/230) Waste 3 — but
only with hard correctness guarantees:

- Any path under ``plugins/``, ``.claude-plugin/``, or ``.agents/plugins/``
  (any generated plugin export surface) unconditionally forces a full gate
  regardless of any other classification (goal stop condition).
- Any path matching the source-code or test patterns forces a full gate.
- Only when every changed path is on the docs/artifact allowlist AND no
  unconditional-trigger path appears does the classification flip to
  ``docs-artifact-only``.
- The operator can always force a full gate via the
  ``CHARNESS_FORCE_FULL_GATE=1`` env var at the hook layer; the classifier
  surfaces ``force_full_gate_env`` in its report for legibility.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

# Generated plugin export surfaces. Any change here unconditionally forces a
# full gate. This is the slice-7 stop condition.
UNCONDITIONAL_FULL_GATE_PREFIXES = (
    "plugins/",
    ".claude-plugin/",
    ".agents/plugins/",
)

# Repo paths that are safe to push without re-running the broad gate when
# they are the *only* changes. The allowlist is conservative: any new
# top-level directory that could affect runtime, validators, or imports must
# be added explicitly here.
DOCS_ARTIFACT_PREFIXES = (
    "docs/",
    "charness-artifacts/",
)
DOCS_ARTIFACT_FILES = frozenset(
    {
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
    }
)

# Path patterns that always force a full gate, even if every other change
# is on the docs/artifact allowlist. Listed for legibility in the report.
FULL_GATE_PATTERN_HINTS = (
    re.compile(r"^scripts/.*\.(py|sh)$"),
    re.compile(r"^skills/"),
    re.compile(r"^tests/"),
    re.compile(r"^integrations/"),
    re.compile(r"^profiles/"),
    re.compile(r"^presets/"),
    re.compile(r"^packaging/"),
    re.compile(r"^evals/"),
    re.compile(r"^charness$"),
    re.compile(r"^pyproject\.toml$"),
    re.compile(r"^Makefile$"),
    # Catch-all for top-level dotfiles/dirs (`.gitignore`, `.gitattributes`,
    # `.editorconfig`, `.vscode/`, `.pre-commit-config.yaml`, `.githooks/`,
    # `.github/`, `.envrc`, etc.). Runtime-shaping config that should never
    # be silently classified as bookkeeping. Slice-7 critique F3.
    re.compile(r"^\.[^/]+"),
)


def _is_unconditional(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in UNCONDITIONAL_FULL_GATE_PREFIXES)


def _is_docs_artifact(path: str) -> bool:
    if path in DOCS_ARTIFACT_FILES:
        return True
    return any(path.startswith(prefix) for prefix in DOCS_ARTIFACT_PREFIXES)


def _matches_full_gate_hint(path: str) -> bool:
    return any(pattern.match(path) for pattern in FULL_GATE_PATTERN_HINTS)


def classify(changed_paths: list[str]) -> dict[str, Any]:
    """Return the classification report for a list of changed paths.

    The function is pure (does not call git); a CLI wrapper resolves the
    diff range and passes the path list in.
    """
    # Deduplicate while preserving order so the report is stable.
    seen: dict[str, None] = {}
    for path in changed_paths:
        if path and path not in seen:
            seen[path] = None
    paths = list(seen.keys())

    unconditional_hits = [path for path in paths if _is_unconditional(path)]
    full_gate_hints = [path for path in paths if _matches_full_gate_hint(path)]
    non_allowlist = [
        path
        for path in paths
        if not _is_docs_artifact(path) and not _is_unconditional(path)
    ]

    if not paths:
        # An empty diff (e.g., a tag-only push) is safe to skip.
        return {
            "classification": "docs-artifact-only",
            "files": [],
            "unconditional_full_gate_hits": [],
            "full_gate_pattern_hits": [],
            "non_allowlist_paths": [],
            "reason": "no changed paths in the push diff",
        }

    if unconditional_hits:
        return {
            "classification": "full-gate-required",
            "files": paths,
            "unconditional_full_gate_hits": unconditional_hits,
            "full_gate_pattern_hits": full_gate_hints,
            "non_allowlist_paths": non_allowlist,
            "reason": (
                "unconditional full-gate path touched: "
                + ", ".join(unconditional_hits[:5])
                + (f" (+{len(unconditional_hits) - 5} more)" if len(unconditional_hits) > 5 else "")
            ),
        }
    if full_gate_hints:
        return {
            "classification": "full-gate-required",
            "files": paths,
            "unconditional_full_gate_hits": [],
            "full_gate_pattern_hits": full_gate_hints,
            "non_allowlist_paths": non_allowlist,
            "reason": (
                "source/test/config path touched: "
                + ", ".join(full_gate_hints[:5])
                + (f" (+{len(full_gate_hints) - 5} more)" if len(full_gate_hints) > 5 else "")
            ),
        }
    if non_allowlist:
        return {
            "classification": "full-gate-required",
            "files": paths,
            "unconditional_full_gate_hits": [],
            "full_gate_pattern_hits": [],
            "non_allowlist_paths": non_allowlist,
            "reason": (
                "non-allowlist path touched: "
                + ", ".join(non_allowlist[:5])
                + (f" (+{len(non_allowlist) - 5} more)" if len(non_allowlist) > 5 else "")
            ),
        }
    return {
        "classification": "docs-artifact-only",
        "files": paths,
        "unconditional_full_gate_hits": [],
        "full_gate_pattern_hits": [],
        "non_allowlist_paths": [],
        "reason": "every changed path is on the docs/artifact allowlist",
    }


def resolve_diff_range(repo_root: Path, remote: str = "origin") -> str | None:
    """Best-effort: return the two-dot diff range ``<remote>/<branch>..HEAD``.

    Returns ``None`` when the remote tracking branch is unknown (e.g., a
    brand-new branch with no upstream). The caller should fall back to
    forcing a full gate when the range is unknown. For accurate per-ref
    classification during a push that updates multiple refs, the pre-push
    hook should pass an explicit ``--diff-range`` derived from the
    ``<remote-sha>..<local-sha>`` pair git supplies on stdin.
    """
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    if not branch or branch == "HEAD":
        return None
    upstream = f"{remote}/{branch}"
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", upstream],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    return f"{upstream}..HEAD"


def changed_paths_from_git(repo_root: Path, diff_range: str) -> list[str]:
    """Return the list of paths changed in ``diff_range`` via ``git diff --name-only``."""
    result = subprocess.run(
        ["git", "diff", "--name-only", diff_range],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
