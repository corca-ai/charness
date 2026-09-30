"""chmod allowlist: every production `.chmod` needs a reviewed owner (#881).

Changing a mode before unlink can mutate a hardlinked survivor's inode, so new
chmod sites must name their reason here. Mirrors the subprocess-form gate's
shape as a test: the two unlink-adjacent files pin the enclosing function,
owned-path installs pin the file.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tests.quality_gates.support import ROOT

SCAN_GLOBS = ("scripts/**/*.py", "tools/**/*.py", "skills/**/*.py")
SKIP_PARTS = {"__pycache__", "vendor", "generated"}

#: (relative path, enclosing function or None for whole-file) -> reason.
REVIEWED_CHMODS = {
    ("scripts/runtime_scratch.py", "_rmtree_writable"): (
        "dirs-only unlink guard (+ Windows-only file bits; POSIX files untouched)"
    ),
    ("scripts/gates_support/runtime_root_retention.py", "_remove_tree"): (
        "Windows-only single-file unlink; POSIX unlinks without chmod"
    ),
    ("scripts/cli/host_claude.py", None): "owned wrapper/target install (0755)",
    ("scripts/core/bootstrap_runtime.py", None): "owned launcher install (0755)",
    ("tools/check_coverage.py", None): "owned generated script (0755)",
    ("skills/public/release/scripts/publish_release_runtime.py", None): (
        "owned release record dir (0700)"
    ),
    ("skills/public/critique/scripts/run_review_promotion_storage.py", None): (
        "mode copy onto a managed promotion destination"
    ),
    ("skills/public/critique/scripts/semantic_review_input.py", None): (
        "owned review-carrier hardening (0444/0555)"
    ),
}


class _ChmodFinder(ast.NodeVisitor):
    def __init__(self) -> None:
        self.stack: list[str] = []
        self.hits: list[tuple[int, str | None]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "chmod":
            enclosing = self.stack[-1] if self.stack else None
            self.hits.append((node.lineno, enclosing))
        self.generic_visit(node)


def _findings(repo: Path) -> list[str]:
    unreviewed: list[str] = []
    for glob in SCAN_GLOBS:
        for path in sorted(repo.glob(glob)):
            if set(path.parts) & SKIP_PARTS or not path.is_file():
                continue
            relative = path.relative_to(repo).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            finder = _ChmodFinder()
            finder.visit(tree)
            for lineno, enclosing in finder.hits:
                if (relative, enclosing) in REVIEWED_CHMODS or (relative, None) in REVIEWED_CHMODS:
                    continue
                unreviewed.append(f"{relative}:{lineno}: unreviewed .chmod in {enclosing or '<module>'}")
    return unreviewed


def test_production_chmod_sites_are_all_reviewed() -> None:
    assert _findings(ROOT) == []


def test_seeded_chmod_is_flagged(tmp_path: Path) -> None:
    probe = tmp_path / "scripts"
    probe.mkdir(parents=True)
    (probe / "probe.py").write_text(
        "import os\n\n\ndef wipe(path):\n    os.chmod(path, 0o600)\n    path.unlink()\n",
        encoding="utf-8",
    )

    assert _findings(tmp_path) == ["scripts/probe.py:5: unreviewed .chmod in wipe"]
