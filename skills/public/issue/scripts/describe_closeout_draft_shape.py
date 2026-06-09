#!/usr/bin/env python3
"""Author-time required-shape source for the GitHub-issue closeout-draft surface.

``validate-closeout-draft`` (which reuses ``verify_closeout``) enforces a body
shape an author otherwise discovers by failing the validator several times (the
recurring authoring-preflight class). This module is the *shape source* the
artifact-surface preflight dispatcher reads for ``--type closeout-draft`` —
exactly like a scaffold script, it prints the required shape and a starter stub.

It never re-declares the contract: every classification, ledger field, carrier,
and manual-fallback reason is rendered from the LIVE enforced constants in the
sibling verifier modules, so the surfaced shape cannot drift from the gate.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_local(module_name: str) -> Any:
    """Load a sibling issue-script module by filesystem spec (clone-safe; no
    sys.modules registration), so this resolves in the working tree and the
    installed plugin export alike."""
    spec = importlib.util.spec_from_file_location(
        module_name, Path(__file__).resolve().parent / f"{module_name}.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside describe_closeout_draft_shape.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_VERIFY = _load_local("issue_verify_closeout")
_BODY = _load_local("issue_verify_closeout_body")
_CRITIQUE = _load_local("issue_resolution_critique")


def _field_label(field_id: str, aliases: tuple[str, ...]) -> str:
    """Render one ledger field as ``field_id`` plus its accepted ``Header:``
    keyword(s) when they differ — the failure message names the field_id, the
    body needs the header. Case-insensitive; written as ``Header: value``."""
    headers = " / ".join(f"{alias.title()}:" for alias in aliases)
    if aliases == (field_id,):
        return f"{field_id.title()}:"
    return f"{field_id} ({headers})"


def _ledger_block() -> list[str]:
    """The per-classification ledger fields, rendered from the live requirement
    map (``issue_verify_closeout_body._classification_requirements``)."""
    out: list[str] = ["Classification ledger fields (substantive value per field; `TODO`/`TBD`/`n/a` do not count):"]
    for classification in _VERIFY.CLASSIFICATIONS:
        labels = [_field_label(fid, aliases) for fid, aliases in _BODY._classification_requirements(classification)]
        out.append(f"  - {classification}: {', '.join(labels)}")
    out.append(
        "  - bug `Siblings:` must name BOTH a decision and proof "
        "(`siblings_decision_and_proof` fails otherwise)."
    )
    return out


def required_shape() -> str:
    crit = ", ".join(_CRITIQUE.CRITIQUE_REQUIRED_CLASSIFICATIONS)
    carriers = ", ".join(_VERIFY.CARRIERS)
    reasons = ", ".join(_VERIFY.MANUAL_FALLBACK_REASONS)
    lines = [
        "closeout-draft required shape (enforced by `issue_tool.py validate-closeout-draft`,",
        "which reuses `verify_closeout` — same checks before anything mutates GitHub):",
        "",
        f"Carrier (--carrier, one of: {carriers}) decides the carrier-body SOURCE:",
        "  - direct-commit: the body is the COMMIT MESSAGE — pass `--commit-message-file`",
        "    (the proposed commit subject/body), NOT `--body-file`. (Post-close",
        "    `verify-closeout` reads the same message back from the commit via `git show`.)",
        "    This is the trap that cost a round-trip.",
        "  - pr-body / manual-fallback: the body is `--body-file`.",
        "",
        "Close keyword (not required for manual-fallback): each --number needs a",
        "`Closes #N` / `Fixes #N` / `Resolves #N` line (optionally `owner/repo#N`).",
        "",
        f"resolution_critique (required for classifications: {crit}):",
        "  - a `Critique: <path>` line (single-issue) or `Critique #N: <path>` (bundled,",
        "    one per --number, or `Critique #1 #2: <path>`).",
        "  - <path> is a checked-in critique artifact that EXISTS, is non-empty, and",
        "    BINDS to the issue number (its basename or content contains `#N`/the number).",
        "  - the cited critique must itself pass `validate_critique_artifacts` (a blocked",
        "    fresh-eye satisfaction there needs `host signal:` / `tool signal:`);",
        "    `Critique: blocked <reason>` records a host-blocked-subagent fallback.",
        "",
    ]
    lines += _ledger_block()
    lines += [
        "",
        f"manual-fallback carrier also requires --manual-fallback-reason one of: {reasons}.",
        "",
        "Externally-sourced body (a substantive `Source origin:`): also needs at least one",
        "of `Source text:` / `Re-read obligation:` / `Source degraded reason:`.",
        "",
        "If the body declares a `## Proof Ledger`: each gap must be dispositioned",
        "(no proof entry / reached < required / gap lacks disposition all fail).",
    ]
    return "\n".join(lines).rstrip() + "\n"


def stub() -> str:
    """A starter closeout body (feature/deferred-work shape — the common case)."""
    return (
        "<!-- closeout-draft starter; pick the ledger fields for YOUR --classification "
        "(run --type closeout-draft for the full shape). Example: feature/deferred-work. -->\n"
        "Closes #N\n\n"
        "JTBD: <the job this issue was the obstacle to>\n"
        "Boundary: <what is in / out of scope for this resolution>\n"
        "Resolution brief: <the chosen approach in a sentence or two>\n"
        "Implementation: <what changed — files / commits>\n"
        "Prevention: <what stops this class from recurring>\n"
        "Critique #N: charness-artifacts/critique/<dated-resolution-critique>.md\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--stub", action="store_true", help="Emit a starter closeout body")
    args = parser.parse_args(argv)
    sys.stdout.write(stub() if args.stub else required_shape())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
