#!/usr/bin/env python3
"""Pre-commit gate (#257): the *staged* plugin mirror must match staged sources.

The trap this closes: editing an exported source file (repo ``scripts/``, a
skill's ``SKILL.md``/``references/``, ``profiles/``, ``presets/``,
``integrations/``, ``README.md``) regenerates the ``plugins/...`` mirror via
``sync_root_plugin_manifests.py`` — but it is easy to stage only the source and
forget the regenerated mirror. A partial stage passes pre-commit yet leaves the
committed mirror stale, so ``validate_packaging_committed`` fails only *after*
the commit (forcing a ``--amend``). This gate moves that detection to commit time.

Mechanism — reuse, not reinvention: ``git write-tree`` writes the current index
(the staged state) as a tree object; ``validate_packaging_committed`` already
archives a tree-ish and runs ``validate_packaging`` against it. Feeding the index
tree therefore validates exactly the staged snapshot — catching both "forgot to
sync" and "synced but forgot to stage the mirror" without mutating the working
tree. This is a hard gate (gateable, ungameable, binary), unlike the advisory
length-headroom signal (#256).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_vpc = import_repo_module(__file__, "scripts.validate_packaging_committed")


def staged_index_tree(repo_root: Path) -> str:
    """Return the tree SHA of the current index (staged state) via ``git write-tree``.

    The written tree reflects what *would be committed*, so validating it catches
    staged source whose mirror was not also staged — which a HEAD-based check
    (``validate_packaging_committed``) cannot see until after the commit.
    """
    result = subprocess.run(
        ["git", "write-tree"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise _vpc.ValidationError(
            f"`git write-tree` failed in `{repo_root}`:\nSTDERR:\n{result.stderr}"
        )
    return result.stdout.strip()


def check_staged_mirror_drift(repo_root: Path) -> subprocess.CompletedProcess[str]:
    """Validate the staged index's plugin mirror against its staged sources.

    Returns the ``validate_packaging`` CompletedProcess run against the archived
    index snapshot (returncode 0 = staged mirror is in sync).
    """
    tree = staged_index_tree(repo_root)
    with tempfile.TemporaryDirectory(prefix="charness-staged-mirror-drift-") as tmpdir:
        snapshot_root = Path(tmpdir) / "snapshot"
        _vpc.extract_snapshot(repo_root, tree, snapshot_root)
        return _vpc.validate_snapshot(snapshot_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    result = check_staged_mirror_drift(repo_root)
    if result.returncode != 0:
        print(
            "charness: the STAGED plugin mirror is out of sync with staged sources.\n"
            "Run `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and "
            "`git add` the regenerated `plugins/` (and `.claude-plugin/`, "
            "`.agents/plugins/`) before committing.",
            file=sys.stderr,
        )
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n", file=sys.stderr)
        if result.stderr:
            print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
        return 1
    print("charness: staged plugin mirror matches staged sources.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except _vpc.ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
