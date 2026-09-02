#!/usr/bin/env python3
"""Refuse a lingering `.invalid` placeholder git identity (#432).

The trap this gate closes: a proof/test flow sets a synthetic repo-local
`git config user.email hotl-proof@example.invalid` (or an equivalent
`GIT_COMMITTER_EMAIL`/`GIT_AUTHOR_EMAIL` env override) for a bounded proof, then
never restores it. Every commit made afterward -- including unrelated real work
-- is durably misattributed to the synthetic identity until someone notices
(#432: 62 pushed commits on main were misattributed this way).

Resolution mirrors what git itself uses to stamp a commit: `git var
GIT_AUTHOR_IDENT` / `git var GIT_COMMITTER_IDENT` (config AND environment
overrides both apply through these, so the check cannot be fooled by clearing
one but not the other). `.invalid` is the RFC 2606 placeholder TLD reserved for
"this is not a real domain" -- exactly what a synthetic proof identity should
use, but only ever scoped to the one command that needs it, never left as the
durable effective identity.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

_INVALID_SUFFIX = ".invalid"
_EMAIL_RE = re.compile(r"<([^<>]*)>")
_IDENT_VARS: tuple[tuple[str, str], ...] = (
    ("author", "GIT_AUTHOR_IDENT"),
    ("committer", "GIT_COMMITTER_IDENT"),
)


def _git_var(repo_root: str, name: str) -> str | None:
    """Resolve one effective identity via `git var`, or None if git cannot."""
    proc = run_process(
        ["git", "-C", repo_root, "var", name],
        cwd=Path(repo_root),
        timeout_seconds=None,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return proc.stdout.strip()


def _ident_email(ident: str) -> str | None:
    match = _EMAIL_RE.search(ident)
    return match.group(1) if match else None


def resolve_idents(repo_root: str) -> dict[str, str | None]:
    """The effective author/committer idents git would stamp on a commit now."""
    return {kind: _git_var(repo_root, name) for kind, name in _IDENT_VARS}


def find_invalid_identity(idents: dict[str, str | None]) -> tuple[str, str] | None:
    """Return (kind, ident) for the first resolved identity whose email domain
    is the `.invalid` placeholder TLD, checking author before committer."""
    for kind, _name in _IDENT_VARS:
        ident = idents.get(kind)
        if ident is None:
            continue
        email = _ident_email(ident)
        if email is not None and email.strip().lower().endswith(_INVALID_SUFFIX):
            return kind, ident
    return None


def _refusal_message(kind: str, ident: str) -> str:
    return (
        f"check-git-identity: BLOCKED -- effective git {kind} identity resolves to a "
        f"`.invalid` placeholder domain: {ident}\n"
        "A `.invalid` identity is the RFC 2606 placeholder TLD; committing with it "
        "durably misattributes published history to a synthetic identity (#432 -- a "
        "lingering proof-flow identity misattributed 62 real commits before anyone "
        "noticed).\n"
        "Remediation: clear the lingering identity -- `git config --unset user.email` "
        "(and `user.name` if it is also synthetic), or unset the environment override "
        "(GIT_AUTHOR_EMAIL / GIT_COMMITTER_EMAIL / GIT_AUTHOR_NAME / GIT_COMMITTER_NAME). "
        "If a proof flow genuinely needs a synthetic identity, scope it per command "
        "instead of mutating durable config -- `git -c user.name=... -c "
        "user.email=...` or GIT_AUTHOR_*/GIT_COMMITTER_* env vars set for that one "
        "command only."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Refuse a lingering .invalid placeholder git identity at the "
            "commit/release boundary (#432)."
        )
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    args = parser.parse_args(argv)

    idents = resolve_idents(args.repo_root)
    finding = find_invalid_identity(idents)
    if finding is not None:
        kind, ident = finding
        # floor-addition-restraint: keep — recorded recurrence (62 misattributed
        # pushed commits, #432); environment check, adds no authoring-shape weight
        print(_refusal_message(kind, ident))
        return 1

    if all(value is None for value in idents.values()):
        # `git var` could not resolve either identity (e.g. a fresh environment
        # with no user.email set at all). That is git's own failure mode to
        # surface at commit time -- this gate must not add a new one.
        print(
            "check-git-identity: unresolvable (git could not resolve an identity; not blocked here)"
        )
        return 0

    print("check-git-identity: clean (no .invalid effective commit identity)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
